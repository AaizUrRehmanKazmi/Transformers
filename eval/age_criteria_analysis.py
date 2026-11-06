"""How does the fine-tuned model do on age criteria in the held-out data? Uses saved predictions only.

    python eval/age_criteria_analysis.py

Needs eval/results/final_{val,test}_greedy/predictions.jsonl and internet access once for the dataset
(to read the criterion text). Age criteria are found with a simple regex, so the selection is approximate.
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from data.build_prompts import load_split  # noqa: E402

AGE = re.compile(r"\bage[ds]?\b|years? old|years? of age|\byo\b", re.I)

for name, split in (("final_val_greedy", "val"), ("final_test_greedy", "test")):
    rows = {str(r["annotation_id"]): r for r in load_split(split)}
    preds = [json.loads(l) for l in (ROOT / "eval" / "results" / name / "predictions.jsonl").read_text().splitlines() if l.strip()]
    sel = [p for p in preds if AGE.search(rows[str(p["annotation_id"])]["criterion_text"])]
    right = sum(p["gold_label"] == p["pred_label"] for p in sel)
    print(f"\n== {split}: {len(sel)} age-related criteria of {len(preds)}; correct {right} ({right / max(len(sel), 1):.2f})")
    print("   gold labels:", dict(Counter(p["gold_label"] for p in sel)))
    print("   wrong (gold -> predicted):", dict(Counter((p["gold_label"], p["pred_label"]) for p in sel if p["gold_label"] != p["pred_label"])))
    for p in [q for q in sel if q["gold_label"] != q["pred_label"]][:12]:
        print(f"   - gold={p['gold_label']!r} pred={p['pred_label']!r}: {rows[str(p['annotation_id'])]['criterion_text'][:110]}")
