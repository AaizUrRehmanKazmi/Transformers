"""Per-class tables, error taxonomy and a markdown file of representative failures.

    python eval/error_analysis.py --name lora_best_val --split val
    python eval/error_analysis.py --name lora_best_test --split test --final

Reads eval/results/<name>/{metrics,predictions}.json(l); writes error_analysis.md.
No model is run here. (For test, analysis is for REPORTING only, never for tuning.)
"""
import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core.schema import render_explanation, split_note  # noqa: E402
from data.build_prompts import load_split  # noqa: E402

NEI = "not enough information"


def tag(r):
    g, p = r["gold_label"], r["pred_label"]
    if not r["valid"]:
        return "format_failure"
    if g == p:
        ge, pe = set(r["gold_evidence"]), set(r["pred_evidence"])
        if ge == pe:
            return None
        if not ge:
            return "label_ok_unsupported_evidence"   # cited sentences where gold cites none
        if not pe:
            return "label_ok_evidence_missed"        # cited nothing where gold cites some
        return "label_ok_evidence_mismatch"
    if p == NEI:
        return "missed_decision_pred_NEI"            # gold decided, model says not enough info
    if g == NEI:
        return "unsupported_decision_gold_NEI"       # model decides although info is missing
    if "not applicable" in (g, p):
        return "not_applicable_confusion"
    return "polarity_flip"                           # included<->not included, excluded<->not excluded


def print_per_class(metrics):
    for scope in ("overall", "inclusion", "exclusion"):
        m = metrics[scope]
        print(f"\n[{scope}] n={m['n']} acc={m['accuracy']:.3f} macroF1(present)={m['macro_f1_present']:.3f} "
              f"macroF1(all)={m['macro_f1_all']:.3f}")
        for lab, v in m["per_class"].items():
            if v["support"] or scope == "overall":
                print(f"  {lab:24s} P={v['precision']:.2f} R={v['recall']:.2f} F1={v['f1']:.2f} n={v['support']}")
        cm = m["confusion_matrix"]
        print("  confusion (rows=gold, cols=pred):", cm["labels"])
        for lab, row in zip(cm["labels"], cm["rows_gold_cols_pred"]):
            if sum(row):
                print(f"   {lab:24s} {row}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True)
    ap.add_argument("--split", choices=["val", "test"], default="val")
    ap.add_argument("--final", action="store_true")
    ap.add_argument("--per-category", type=int, default=3)
    args = ap.parse_args()
    if args.split == "test" and not args.final:
        raise SystemExit("Pass --final to analyse the test split (reporting only).")

    d = ROOT / "eval" / "results" / args.name
    metrics = json.loads((d / "metrics.json").read_text())
    records = [json.loads(l) for l in (d / "predictions.jsonl").read_text().splitlines() if l.strip()]
    rows = {str(r["annotation_id"]): r for r in load_split(args.split)}

    print_per_class(metrics)
    ev = metrics["evidence"]["overall"]
    print(f"\nEvidence: micro={ev['micro']}  macro_nonempty={ev['macro_nonempty']}  "
          f"empty_gold_agreement={ev['empty_gold_agreement']}")

    groups = defaultdict(list)
    for r in records:
        t = tag(r)
        if t:
            groups[t].append(r)
    n_err = sum(len(v) for v in groups.values())
    print(f"\nRows with any error: {n_err}/{len(records)}")
    print("Error taxonomy:")
    for t, v in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        print(f"  {t:34s} {len(v)}")
    print("Wrong-label pairs (gold -> pred):")
    for (g, p), c in Counter((r["gold_label"], r["pred_label"]) for r in records
                             if r["gold_label"] != r["pred_label"]).most_common(10):
        print(f"  {g} -> {p}: {c}")

    lines = [f"# Error analysis: {args.name} ({args.split})\n",
             f"{n_err} of {len(records)} rows have a label or evidence error.\n",
             "| Category | Count |\n|---|---|"]
    lines += [f"| {t} | {len(v)} |" for t, v in sorted(groups.items(), key=lambda kv: -len(kv[1]))]
    for t, v in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        lines.append(f"\n## {t} ({len(v)} rows)\n")
        for r in v[:args.per_category]:
            row = rows[str(r["annotation_id"])]
            sents = split_note(row["note"])
            lines.append(f"**annotation {r['annotation_id']}** (patient {r['patient_id']}, {r['criterion_type']})\n")
            lines.append(f"- Criterion: {row['criterion_text']}")
            lines.append(f"- Gold: `{r['gold_label']}`, evidence {r['gold_evidence']}")
            lines.append(f"- Predicted: `{r['pred_label']}`, evidence {r['pred_evidence']}"
                         + (f"  (parse error: {r['error']})" if r["error"] else ""))
            lines.append(f"- Raw output: `{r['raw_output'].strip()[:200]}`")
            lines.append(f"- Grounded explanation: {render_explanation(r['pred_label'], r['pred_evidence'], sents)}")
            lines.append("- Patient note:\n")
            lines += [f"  > [{i}] {t_}" for i, t_ in sents]
            lines.append("")
    (d / "error_analysis.md").write_text("\n".join(lines))
    print("\nwrote", d / "error_analysis.md")


if __name__ == "__main__":
    main()
