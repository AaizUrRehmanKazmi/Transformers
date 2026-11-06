import pytest

from app.screening import (InputError, aggregate, build_report_html, build_report_markdown, number_note,
                           parse_criteria, validate_inputs)

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


def test_report_contains_disclaimer_and_escapes_html():
    results = [res("inclusion", "included", criterion="<script>alert(1)</script>")]
    sents = [(0, "x")]
    meta = {"timestamp": "t", "model": "m", "adapter": "a", "decoding_mode": "d", "max_new_tokens": 64, "device": "cpu"}
    ov = aggregate(results)
    assert "EDUCATIONAL SCREENING PROTOTYPE" in build_report_markdown(results, sents, ov, meta)
    h = build_report_html(results, sents, ov, meta)
    assert "<script>alert(1)</script>" not in h and "&lt;script&gt;" in h
