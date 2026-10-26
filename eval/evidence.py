"""Evidence-sentence metrics with explicit handling of empty sets.

Conventions (documented in the report):
  * Micro P/R/F1 pools all sentences over all rows. Rows with empty gold evidence
    contribute false positives only if the model cites something. A zero denominator
    gives 0.0.
  * macro_f1_nonempty: mean per-row F1 over rows whose GOLD evidence is non-empty.
    Predicting nothing for such a row scores 0.
  * macro_f1_all_rows: mean per-row F1 over all rows, where gold empty & pred empty
    scores 1 and gold empty & pred non-empty scores 0.
  * empty_gold_agreement: among rows with empty gold evidence, fraction where the
    model also cited nothing.
"""
from typing import Dict, Sequence


def _prf(tp, fp, fn):
    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / (tp + fn) if tp + fn else 0.0
    f = 2 * p * r / (p + r) if p + r else 0.0
    return p, r, f


def evidence_metrics(gold_list: Sequence[Sequence[int]], pred_list: Sequence[Sequence[int]]) -> Dict:
    tp = fp = fn = 0
    f1_nonempty, f1_all = [], []
    p_nonempty, r_nonempty = [], []
    n_gold_empty = both_empty = 0
    for g, p in zip(gold_list, pred_list):
        g, p = set(g), set(p)
        tp += len(g & p)
        fp += len(p - g)
        fn += len(g - p)
        if not g:
            n_gold_empty += 1
            agree = not p
            both_empty += agree
            f1_all.append(1.0 if agree else 0.0)
        else:
            rp, rr, rf = _prf(len(g & p), len(p - g), len(g - p))
            p_nonempty.append(rp)
            r_nonempty.append(rr)
            f1_nonempty.append(rf)
            f1_all.append(rf)
    mp, mr, mf = _prf(tp, fp, fn)
    mean = lambda xs: sum(xs) / len(xs) if xs else 0.0  # noqa: E731
    return {
        "n_rows": len(gold_list),
        "n_gold_empty": n_gold_empty,
        "micro": {"precision": mp, "recall": mr, "f1": mf},
        "macro_nonempty": {"precision": mean(p_nonempty), "recall": mean(r_nonempty), "f1": mean(f1_nonempty)},
        "macro_f1_all_rows": mean(f1_all),
        "empty_gold_agreement": both_empty / n_gold_empty if n_gold_empty else None,
    }
