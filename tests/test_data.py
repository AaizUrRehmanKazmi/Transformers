import json
from pathlib import Path

import pytest

from core.schema import parse_gold, parse_output, split_note, render_explanation
from data.build_prompts import build_messages

NOTE = ("0. A 58-year-old woman presents with chest pain.\n"
        "1. She has hypertension.\n"
        "2. She takes no medications.")


def test_split_note():
    s = split_note(NOTE)
    assert [i for i, _ in s] == [0, 1, 2]
    assert s[1][1] == "She has hypertension."


def test_parse_gold():
    assert parse_gold("[0, 1, 2]") == [0, 1, 2]
    assert parse_gold("[]") == []
    assert parse_gold("[3, 3, 1]") == [1, 3]


def test_parse_output_valid_and_invalid():
    ok = parse_output('{"label": "included", "evidence": [0, 2]}', "inclusion", 3)
    assert ok.valid and ok.evidence == [0, 2]
    assert not parse_output("garbage", "inclusion").valid
    # 'included' is not a valid exclusion label
    assert parse_output('{"label": "included", "evidence": []}', "exclusion").error == "label_not_valid_for_type"
    assert parse_output('{"label": "excluded", "evidence": [9]}', "exclusion", 3).error == "evidence_out_of_range"


def test_explanation_only_uses_cited_sentences():
    ex = render_explanation("included", [1], split_note(NOTE))
    assert "hypertension" in ex and "chest pain" not in ex


def test_prompt_has_no_gpt4_content():
    row = {"note": NOTE, "criterion_type": "inclusion", "criterion_text": "Has hypertension.",
           "gpt4_explanation": "SENTINEL_GPT4", "gpt4_sentences": "SENTINEL_GPT4",
           "gpt4_eligibility": "SENTINEL_GPT4", "explanation_correctness": "SENTINEL_GPT4"}
    msgs = build_messages(split_note(row["note"]), row["criterion_type"], row["criterion_text"])
    assert "SENTINEL_GPT4" not in json.dumps(msgs)


MANIFEST = Path(__file__).resolve().parent.parent / "data" / "split_manifest.json"


@pytest.mark.skipif(not MANIFEST.exists(), reason="manifest not generated yet")
def test_manifest_no_leakage():
    m = json.loads(MANIFEST.read_text())
    p = {k: set(v) for k, v in m["patients"].items()}
    assert [len(p[k]) for k in ("train", "val", "test")] == [37, 8, 8]
    assert not (p["train"] & p["val"]) and not (p["train"] & p["test"]) and not (p["val"] & p["test"])
    assert not set(m["excluded_columns"]) - {"gpt4_explanation", "explanation_correctness",
                                              "gpt4_sentences", "gpt4_eligibility"}
