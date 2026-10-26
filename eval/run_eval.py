"""Evaluate a model (optionally with a LoRA adapter) on the val or test split.

Zero-shot baseline (validation):
    python eval/run_eval.py --name baseline_val --split val
Fine-tuned:
    python eval/run_eval.py --name lora_val --split val --adapter <path_or_hub_id>
Final test (only once, after all choices are frozen):
    python eval/run_eval.py --name lora_test --split test --final --adapter ...

Greedy decoding, same prompt and settings for every model so results are comparable.
"""
import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import torch  # noqa: E402
from transformers import AutoModelForCausalLM, AutoTokenizer  # noqa: E402

from core.schema import ALL_LABELS, LABELS_BY_TYPE, parse_gold, parse_output, split_note  # noqa: E402
from data.build_prompts import build_messages, load_split  # noqa: E402
from eval.classification import INVALID, classification_report  # noqa: E402
from eval.evidence import evidence_metrics  # noqa: E402


def generate_batch(model, tok, texts, max_new_tokens, eos_ids, rep_penalty=1.0):
    enc = tok(texts, return_tensors="pt", padding=True, add_special_tokens=False).to(model.device)
    with torch.no_grad():
        out = model.generate(**enc, max_new_tokens=max_new_tokens, do_sample=False,
                             temperature=None, top_p=None, top_k=None,
                             eos_token_id=eos_ids, pad_token_id=tok.pad_token_id,
                             repetition_penalty=rep_penalty)
    return tok.batch_decode(out[:, enc["input_ids"].shape[1]:], skip_special_tokens=True)


def summarize(records, train_rows):
    metrics = {"overall": classification_report(
        [r["gold_label"] for r in records], [r["pred_label"] for r in records], list(ALL_LABELS))}
    for t in ("inclusion", "exclusion"):
        sub = [r for r in records if r["criterion_type"] == t]
        metrics[t] = classification_report(
            [r["gold_label"] for r in sub], [r["pred_label"] for r in sub], list(LABELS_BY_TYPE[t]))
    metrics["evidence"] = {
        "overall": evidence_metrics([r["gold_evidence"] for r in records],
                                    [r["pred_evidence"] for r in records])}
    for t in ("inclusion", "exclusion"):
        sub = [r for r in records if r["criterion_type"] == t]
        metrics["evidence"][t] = evidence_metrics([r["gold_evidence"] for r in sub],
                                                  [r["pred_evidence"] for r in sub])
    # Majority-class baseline per criterion type, taken from the TRAIN split
    maj = {t: Counter(r["expert_eligibility"] for r in train_rows if r["criterion_type"] == t).most_common(1)[0][0]
           for t in ("inclusion", "exclusion")}
    metrics["majority_baseline"] = {
        "labels": maj,
        **classification_report([r["gold_label"] for r in records],
                                [maj[r["criterion_type"]] for r in records], list(ALL_LABELS)),
    }
    metrics["output_errors"] = dict(Counter(r["error"] for r in records if r["error"]))
    return metrics


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True)
    ap.add_argument("--model", default="Qwen/Qwen2.5-1.5B-Instruct")
    ap.add_argument("--adapter", default=None)
    ap.add_argument("--split", choices=["val", "test"], default="val")
    ap.add_argument("--final", action="store_true", help="required to touch the test split")
    ap.add_argument("--batch-size", type=int, default=8)
    ap.add_argument("--max-new-tokens", type=int, default=64)
    ap.add_argument("--rep-penalty", type=float, default=1.0,
                    help="1.0 = pure greedy. (The model's default config may set >1.0.)")
    ap.add_argument("--limit", type=int, default=None, help="debug: first N rows only")
    args = ap.parse_args()
    if args.split == "test" and not args.final:
        raise SystemExit("Refusing to evaluate on test without --final (test set must stay untouched).")

    tok = AutoTokenizer.from_pretrained(args.model)
    tok.padding_side = "left"
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(args.model, torch_dtype=torch.float16).to("cuda").eval()
    if args.adapter:
        from peft import PeftModel
        model = PeftModel.from_pretrained(model, args.adapter).eval()
    eos_ids = sorted({tok.convert_tokens_to_ids("<|im_end|>"), tok.eos_token_id})

    rows = load_split(args.split)
    if args.limit:
        rows = rows[:args.limit]
    sents = [split_note(r["note"]) for r in rows]
    texts = [tok.apply_chat_template(build_messages(s, r["criterion_type"], r["criterion_text"]),
                                     add_generation_prompt=True, tokenize=False)
             for s, r in zip(sents, rows)]

    records = []
    for i in range(0, len(rows), args.batch_size):
        outs = generate_batch(model, tok, texts[i:i + args.batch_size], args.max_new_tokens, eos_ids,
                              args.rep_penalty)
        for r, s, raw in zip(rows[i:i + args.batch_size], sents[i:i + args.batch_size], outs):
            parsed = parse_output(raw, r["criterion_type"], len(s))
            records.append({
                "annotation_id": r["annotation_id"], "patient_id": str(r["patient_id"]),
                "criterion_type": r["criterion_type"],
                "gold_label": r["expert_eligibility"], "gold_evidence": parse_gold(r["expert_sentences"]),
                "raw_output": raw, "valid": parsed.valid, "error": parsed.error,
                "pred_label": parsed.label if parsed.valid else INVALID,
                "pred_evidence": parsed.evidence if parsed.valid else [],
            })
        print(f"{min(i + args.batch_size, len(rows))}/{len(rows)}", flush=True)

    metrics = summarize(records, load_split("train"))
    metrics["settings"] = {"model": args.model, "adapter": args.adapter, "split": args.split,
                           "decoding": "greedy", "repetition_penalty": args.rep_penalty,
                           "max_new_tokens": args.max_new_tokens,
                           "batch_size": args.batch_size, "dtype": "float16", "n_rows": len(rows)}
    out = ROOT / "eval" / "results" / args.name
    out.mkdir(parents=True, exist_ok=True)
    (out / "metrics.json").write_text(json.dumps(metrics, indent=2))
    (out / "predictions.jsonl").write_text("\n".join(json.dumps(r) for r in records))

    o = metrics["overall"]
    print(f"\n{args.name}: acc={o['accuracy']:.3f} macroF1(present)={o['macro_f1_present']:.3f} "
          f"invalid={o['invalid_rate']:.3f}")
    print(f"majority baseline: acc={metrics['majority_baseline']['accuracy']:.3f} "
          f"macroF1(present)={metrics['majority_baseline']['macro_f1_present']:.3f}")
    print("evidence micro:", {k: round(v, 3) for k, v in metrics["evidence"]["overall"]["micro"].items()})
    print("output errors:", metrics["output_errors"])
    print("wrote", out)


if __name__ == "__main__":
    main()
