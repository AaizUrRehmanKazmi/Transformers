"""Prompt/answer construction, answer-only loss masking and truncation statistics.

Only `note`, `criterion_type`, `criterion_text` go into the prompt. Targets come from
`expert_eligibility` and `expert_sentences`. GPT-4 columns are never touched.

    python data/build_prompts.py --model Qwen/Qwen2.5-1.5B-Instruct --max-len 2048
"""
import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core.schema import LABELS_BY_TYPE, format_answer, parse_gold, split_note  # noqa: E402

MANIFEST = ROOT / "data" / "split_manifest.json"
DATASET = "ncbi/TrialGPT-Criterion-Annotations"

SYSTEM = (
    "You are a clinical trial screening assistant (educational prototype). Given a numbered "
    "patient note and ONE trial criterion, output JSON with 'label' and 'evidence' (list of "
    "supporting sentence ids). Use only the note; if it does not say enough, answer "
    "'not enough information'."
)


def build_user_prompt(sentences, criterion_type, criterion_text):
    note = "\n".join(f"[{i}] {t}" for i, t in sentences)
    labels = " | ".join(LABELS_BY_TYPE[criterion_type])
    return (f"Patient note:\n{note}\n\nCriterion type: {criterion_type}\n"
            f"Criterion: {criterion_text}\n\nAllowed labels: {labels}\n"
            'Answer as JSON: {"label": ..., "evidence": [ids]}')


def build_messages(sentences, criterion_type, criterion_text):
    return [{"role": "system", "content": SYSTEM},
            {"role": "user", "content": build_user_prompt(sentences, criterion_type, criterion_text)}]


def load_split(name):
    from datasets import load_dataset
    manifest = json.loads(MANIFEST.read_text())
    pcol = manifest["patient_column"]
    keep = set(manifest["patients"][name])
    ds = load_dataset(DATASET)["train"]
    return [dict(r) for r in ds if str(r[pcol]) in keep]


def _prompt_ids(tok, sents, row):
    msgs = build_messages(sents, row["criterion_type"], row["criterion_text"])
    # Render to text, then tokenize: works across transformers versions
    # (newer ones return a BatchEncoding from apply_chat_template(tokenize=True)).
    text = tok.apply_chat_template(msgs, add_generation_prompt=True, tokenize=False)
    return tok(text, add_special_tokens=False)["input_ids"]


def encode_example(tok, row, max_len=2048):
    """Returns input_ids/labels (loss only on the answer) plus truncation metadata.
    Truncation drops trailing sentences; kept sentences retain their original ids."""
    sents_all = split_note(row["note"])
    gold = parse_gold(row["expert_sentences"])
    answer = format_answer(row["expert_eligibility"], gold)
    ans_ids = tok(answer + "<|im_end|>", add_special_tokens=False)["input_ids"]
    budget = max_len - len(ans_ids)

    full_len = len(_prompt_ids(tok, sents_all, row))
    sents = list(sents_all)
    prompt = _prompt_ids(tok, sents, row)
    while len(prompt) > budget and len(sents) > 1:
        sents.pop()
        prompt = _prompt_ids(tok, sents, row)

    kept_ids = {i for i, _ in sents}
    return {
        "input_ids": prompt + ans_ids,
        "labels": [-100] * len(prompt) + ans_ids,
        "attention_mask": [1] * (len(prompt) + len(ans_ids)),
        "meta": {
            "n_sentences": len(sents_all), "n_kept": len(sents),
            "full_prompt_tokens": full_len,
            "truncated": len(sents) < len(sents_all),
            "lost_gold": bool(set(gold) - kept_ids),
        },
    }


def _pct(xs, q):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(q * len(xs)))]


def main():
    from transformers import AutoTokenizer
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen2.5-1.5B-Instruct")
    ap.add_argument("--max-len", type=int, default=2048)
    args = ap.parse_args()
    tok = AutoTokenizer.from_pretrained(args.model)

    for split in ("train", "val", "test"):
        rows = load_split(split)
        encs = [encode_example(tok, r, args.max_len) for r in rows]
        lens = [e["meta"]["full_prompt_tokens"] for e in encs]
        n_trunc = sum(e["meta"]["truncated"] for e in encs)
        n_lost = sum(e["meta"]["lost_gold"] for e in encs)
        empty = sum(1 for r in rows if not parse_gold(r["expert_sentences"]))
        labels = Counter((r["criterion_type"], r["expert_eligibility"]) for r in rows)
        print(f"\n== {split}: {len(rows)} rows, {len({r['patient_id'] for r in rows})} patients")
        print(f"prompt tokens: median={_pct(lens, .5)} p95={_pct(lens, .95)} max={max(lens)}")
        print(f"truncated at max_len={args.max_len}: {n_trunc}; gold evidence lost: {n_lost}")
        print(f"rows with empty gold evidence: {empty}")
        for k, v in sorted(labels.items()):
            print(f"  {k[0]:9s} {k[1]:24s} {v}")


if __name__ == "__main__":
    main()
