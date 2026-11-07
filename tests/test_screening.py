import pytest

from app.screening import (InputError, aggregate, build_report_html, build_report_markdown, number_note,
                           parse_criteria, validate_inputs, age_bounds, age_check, patient_age, review_result)


@pytest.mark.parametrize('age,expected', [(20, 'not included'), (39, 'not included'), (40, 'included'), (62, 'included')])
def test_review_age_threshold(age, expected):
    sents = [(0, f'A {age}-year-old man presents with chest pain.')]
    r = review_result(res('inclusion', 'not enough information', criterion='Adults aged 40 years or older'), sents)
    assert r['label'] == expected
    assert r['model_label'] == 'not enough information'
    assert r['evidence'] == sents


def test_report_regression_age_and_missing_surgery():
    sents = [(0, 'A 20-year-old man presents with chest pain.')]
    age = review_result(res('inclusion', 'not enough information', criterion='Adults aged 40 years or older'), sents)
    surgery = res('exclusion', 'not excluded', criterion='Prior coronary artery bypass surgery')
    surgery['evidence'] = []
    surgery = review_result(surgery, sents)
    assert surgery['label'] == 'not enough information'
    assert surgery['model_label'] == 'not excluded'
    overall = aggregate([age, surgery])
    assert overall['status'] == 'LIKELY INELIGIBLE'
    assert overall['missing'] == ['Prior coronary artery bypass surgery']
    meta = dict(timestamp='t', model='m', adapter='a', decoding_mode='d', max_new_tokens=64, device='cpu')
    for render in (build_report_html, build_report_markdown):
        report = render([age, surgery], sents, overall, meta)
        assert 'Original model label' in report and 'Age check' in report


@pytest.mark.parametrize('note,criterion', [
    ('His father is a 20-year-old man.', 'Adults aged 40 years or older'),
    ('A 20-year-old man. His wife is 45 years old.', 'Adults aged 40 years or older'),
    ('A 20-year-old man.', 'Adults aged 40 years or older with diabetes'),
])
def test_review_does_not_override_ambiguous_age(note, criterion):
    r = review_result(res('inclusion', 'not enough information', criterion=criterion), number_note(note))
    assert r['label'] == 'not enough information'

NOTE = "A 62-year-old man presents with chest pain. He has diabetes. He takes aspirin daily."


def res(ctype, label, valid=True, criterion="c"):
    return {"ctype": ctype, "criterion": criterion, "label": label, "valid": valid, "error": None if valid else "bad",
            "raw": "", "evidence": [(1, "He has diabetes.")] if label else [], "explanation": "e", "truncated": False}


def test_validation_errors():
    with pytest.raises(InputError):
        validate_inputs("", "Age over 40", "")
    with pytest.raises(InputError):
        validate_inputs(NOTE, "", "")
    with pytest.raises(InputError):
        validate_inputs(NOTE, "x", "")                       # criterion too short
    with pytest.raises(InputError):
        validate_inputs(NOTE, "\n".join(f"criterion number {i}" for i in range(30)), "")


def test_validation_ok_and_numbering():
    sents, crit = validate_inputs(NOTE, "1. Age 40 or older\n- Chest pain", "Prior surgery")
    assert [i for i, _ in sents] == [0, 1, 2]
    assert crit[0] == ("inclusion", "Age 40 or older") and crit[-1] == ("exclusion", "Prior surgery")
    assert number_note("0. First one.\n1. Second one.") == [(0, "First one."), (1, "Second one.")]
    assert parse_criteria("  \n- a criterion here\n") == ["a criterion here"]


def test_aggregation_rules():
    assert aggregate([res("exclusion", "excluded"), res("inclusion", "included")])["status"] == "LIKELY INELIGIBLE"
    assert aggregate([res("inclusion", "not included")])["status"] == "LIKELY INELIGIBLE"
    r = aggregate([res("inclusion", "included"), res("exclusion", "not enough information", criterion="liver")])
    assert r["status"] == "UNDETERMINED" and r["missing"] == ["liver"]
    assert aggregate([res("inclusion", None, valid=False)])["status"] == "UNDETERMINED"
    assert aggregate([res("inclusion", "included"), res("exclusion", "not applicable")])["status"] == "PRELIMINARILY ELIGIBLE"


def test_decision_without_evidence_is_flagged():
    r = res("exclusion", "not excluded", criterion="prior disease")
    r["evidence"] = []
    ov = aggregate([res("inclusion", "included"), r])
    assert ov["unsupported"] == ["prior disease"]
    assert ov["status"] == "PRELIMINARILY ELIGIBLE (needs review)"


def test_patient_age():
    assert patient_age(number_note("A 15 years old male with no pain")) == 15
    assert patient_age([(0, "A 52-year-old man with diabetes.")]) == 52
    assert patient_age([(0, "She is aged 70.")]) == 70
    assert patient_age([(0, "A 58-year-old woman with a 60 years old husband.")]) is None
    assert patient_age([(0, "A 6-month-old infant.")]) is None


def test_age_bounds():
    assert age_bounds("At least 40 years old") == ((40, True), None)
    assert age_bounds("18 to 60 years") == ((18, True), (60, True))
    assert age_bounds("Younger than 18 years of age") == (None, (18, False))
    assert age_bounds("Age 18 years or older") == ((18, True), None)
    assert age_bounds("Adults aged over 65 years") == ((65, False), None)
    assert age_bounds("Diabetes for more than 5 years") is None
    assert age_bounds("Prior history of cardiovascular disease") is None


def test_age_check_flags_contradictions():
    s = [(0, "A 15 years old male with no pain")]
    assert "not included" in age_check(s, "inclusion", "At least 40 years old", "included")
    assert age_check(s, "inclusion", "At least 40 years old", "not included") is None
    assert "excluded" in age_check(s, "exclusion", "Younger than 18 years of age", "not excluded")
    assert "not included" in age_check(s, "inclusion", "18 to 60 years", "included")
    assert age_check(s, "inclusion", "Healthy volunteers with diabetes aged 18 to 60 years", "included") is None
    assert age_check([(0, "No age stated here.")], "inclusion", "At least 40 years old", "included") is None


def test_age_flag_needs_review():
    r = res("inclusion", "included", criterion="18 to 60 years")
    r["age_flag"] = "contradiction"
    ov = aggregate([r])
    assert ov["contradictions"] == ["18 to 60 years"]
    assert ov["status"] == "PRELIMINARILY ELIGIBLE (needs review)"


def test_report_contains_disclaimer_and_escapes_html():
    results = [res("inclusion", "included", criterion="<script>alert(1)</script>")]
    sents = [(0, "x")]
    meta = {"timestamp": "t", "model": "m", "adapter": "a", "decoding_mode": "d", "max_new_tokens": 64, "device": "cpu"}
    ov = aggregate(results)
    assert "EDUCATIONAL SCREENING PROTOTYPE" in build_report_markdown(results, sents, ov, meta)
    h = build_report_html(results, sents, ov, meta)
    assert "<script>alert(1)</script>" not in h and "&lt;script&gt;" in h
