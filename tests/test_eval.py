import pytest

from eval.classification import classification_report
from eval.evidence import evidence_metrics

LABELS = ["included", "not included", "not enough information", "not applicable"]


def test_perfect_classification():
    g = ["included", "not included", "not enough information"]
    r = classification_report(g, g, LABELS)
    assert r["accuracy"] == 1.0 and r["macro_f1_present"] == 1.0
    assert r["macro_f1_all"] < 1.0  # 'not applicable' has no support


def test_invalid_counts_as_wrong():
    r = classification_report(["included", "included"], ["included", "invalid"], LABELS)
    assert r["accuracy"] == 0.5 and r["invalid_rate"] == 0.5
    assert r["confusion_matrix"]["labels"][-1] == "invalid"


def test_evidence_basic():
    m = evidence_metrics([[1, 2], [3]], [[1], [3, 4]])
    # tp=2 fp=1 fn=1 -> P=R=2/3
    assert m["micro"]["precision"] == pytest.approx(2 / 3)
    assert m["micro"]["recall"] == pytest.approx(2 / 3)


def test_evidence_empty_handling():
    m = evidence_metrics([[], [], [5]], [[], [1], []])
    assert m["n_gold_empty"] == 2
    assert m["empty_gold_agreement"] == 0.5
    assert m["macro_nonempty"]["f1"] == 0.0      # missed the only non-empty row
    assert m["macro_f1_all_rows"] == pytest.approx(1 / 3)
