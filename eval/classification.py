"""Label-level metrics: accuracy, macro-F1, per-class P/R/F1, confusion matrix.

Predictions that the strict parser rejected are given the pseudo-label "invalid":
they count as wrong, and appear as an extra column in the confusion matrix.

Two macro-F1 variants are reported:
  macro_f1_present : mean F1 over labels with support > 0 in the gold set (primary)
  macro_f1_all     : mean F1 over every valid label (labels with no support score 0)
"""
from typing import Dict, List, Sequence

from sklearn.metrics import confusion_matrix, precision_recall_fscore_support

INVALID = "invalid"


def classification_report(gold: Sequence[str], pred: Sequence[str], labels: List[str]) -> Dict:
    gold, pred = list(gold), list(pred)
    n = len(gold)
    if n == 0:
        return {"n": 0}
    p, r, f, s = precision_recall_fscore_support(gold, pred, labels=labels, zero_division=0)
    present = [i for i, sup in enumerate(s) if sup > 0]
    cm_labels = labels + [INVALID]
    cm = confusion_matrix(gold, pred, labels=cm_labels)
    return {
        "n": n,
        "accuracy": sum(g == q for g, q in zip(gold, pred)) / n,
        "macro_f1_present": float(sum(f[i] for i in present) / len(present)) if present else 0.0,
        "macro_f1_all": float(f.mean()),
        "invalid_rate": sum(q == INVALID for q in pred) / n,
        "per_class": {
            l: {"precision": float(p[i]), "recall": float(r[i]), "f1": float(f[i]), "support": int(s[i])}
            for i, l in enumerate(labels)
        },
        "confusion_matrix": {"labels": cm_labels, "rows_gold_cols_pred": cm.tolist()},
    }
