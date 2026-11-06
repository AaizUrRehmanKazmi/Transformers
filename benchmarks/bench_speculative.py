"""Plain cached greedy decoding vs greedy speculative decoding on real validation prompts.

    python benchmarks/bench_speculative.py --dtype float16
    python benchmarks/bench_speculative.py --draft-adapter <hub_or_dir> --draft-subfolder <sub>

Target = Qwen2.5-1.5B-Instruct + your adapter; draft = Qwen2.5-0.5B-Instruct (optionally with
its own adapter). For each draft length k: token equality with plain greedy on every prompt,
acceptance rate, tokens per target pass, mean latency per prompt, tokens/s, speedup, peak memory
(both models resident). Prompts are real clinical screening prompts; generation stops at EOS.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import torch  # noqa: E402

from core.kv_cache import generate_cached  # noqa: E402
from core.model_loader import (ADAPTER_REPO, ADAPTER_SUBFOLDER, DRAFT_ID, TARGET_ID,  # noqa: E402
                               load_model, load_tokenizer)
from core.schema import split_note  # noqa: E402
from core.speculative import generate_speculative, tokenizers_compatible  # noqa: E402
from data.build_prompts import build_messages, load_split  # noqa: E402


def build_prompts(tok, n, device):
    rows = load_split("val")
    rows = rows[::max(1, len(rows) // n)][:n]
    out = []
    for r in rows:
        text = tok.apply_chat_template(
            build_messages(split_note(r["note"]), r["criterion_type"], r["criterion_text"]),
            add_generation_prompt=True, tokenize=False)
        out.append(torch.tensor([tok(text, add_special_tokens=False)["input_ids"]], device=device))
    return out


def run(fn, prompts):
    fn(prompts[0])                                           # warm-up
    torch.cuda.reset_peak_memory_stats()
    outs, stats = [], []
    for ids in prompts:
        o, s = fn(ids)
        outs.append(o); stats.append(s)
    peak = torch.cuda.max_memory_allocated() / 2**30
    total_s = sum(s["prefill_s"] + s["decode_s"] for s in stats)
    n_tok = sum(s["new_tokens"] for s in stats)
    return outs, stats, {"latency_s": total_s / len(prompts), "tok_s": n_tok / total_s,
                         "peak_gib": peak, "new_tokens": n_tok}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dtype", default="float16", choices=["float16", "float32"])
    ap.add_argument("--n-prompts", type=int, default=20)
    ap.add_argument("--max-new-tokens", type=int, default=64)
    ap.add_argument("--ks", type=int, nargs="+", default=[1, 2, 3, 4, 6, 8])
    ap.add_argument("--adapter", default=ADAPTER_REPO)
    ap.add_argument("--subfolder", default=ADAPTER_SUBFOLDER)
    ap.add_argument("--draft-adapter", default=None)
    ap.add_argument("--draft-subfolder", default=None)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    assert torch.cuda.is_available(), "benchmark needs a GPU"

    tok, dtok = load_tokenizer(TARGET_ID), load_tokenizer(DRAFT_ID)
    compat = tokenizers_compatible(tok, dtok)
    print("tokenizers identical (vocab + EOS):", compat)
    assert compat, "draft and target must share a tokenizer"
    target = load_model(TARGET_ID, args.adapter, args.subfolder, args.dtype)
    draft = load_model(DRAFT_ID, args.draft_adapter, args.draft_subfolder, args.dtype)
    print(f"target {sum(p.numel() for p in target.parameters()) / 1e6:.0f}M params, "
          f"draft {sum(p.numel() for p in draft.parameters()) / 1e6:.0f}M params, "
          f"resident memory {torch.cuda.memory_allocated() / 2**30:.2f} GiB")

    eos = tuple(sorted({tok.convert_tokens_to_ids("<|im_end|>"), tok.eos_token_id}))
    prompts = build_prompts(tok, args.n_prompts, "cuda")
    N = args.max_new_tokens

    ref_outs, _, base = run(lambda ids: generate_cached(target, ids, N, eos), prompts)
    print(f"\nplain cached greedy: {base['latency_s']:.3f} s/prompt, {base['tok_s']:.1f} tok/s, "
          f"peak {base['peak_gib']:.2f} GiB, {base['new_tokens']} tokens over {len(prompts)} prompts")
    print(f"\n{'k':>3} {'accept':>7} {'tok/round':>10} {'s/prompt':>9} {'tok/s':>7} "
          f"{'speedup':>8} {'peak GiB':>9} {'all equal':>10}")
    rows = []
    for k in args.ks:
        outs, stats, agg = run(lambda ids: generate_speculative(target, draft, ids, N, k, eos), prompts)
        equal = [torch.equal(a, b) for a, b in zip(ref_outs, outs)]
        prop = sum(s["proposed"] for s in stats); acc = sum(s["accepted"] for s in stats)
        rnd = sum(s["rounds"] for s in stats)
        row = {"k": k, "acceptance_rate": acc / prop if prop else None,
               "tokens_per_round": (agg["new_tokens"] - len(prompts)) / rnd if rnd else None,
               "latency_s": agg["latency_s"], "tok_s": agg["tok_s"], "peak_gib": agg["peak_gib"],
               "speedup": base["latency_s"] / agg["latency_s"], "n_equal": sum(equal),
               "n_prompts": len(prompts), "mismatch_prompts": [i for i, e in enumerate(equal) if not e],
               "draft_s": sum(s["draft_s"] for s in stats), "verify_s": sum(s["verify_s"] for s in stats)}
        rows.append(row)
        print(f"{k:>3} {row['acceptance_rate']:>7.3f} {row['tokens_per_round']:>10.2f} "
              f"{row['latency_s']:>9.3f} {row['tok_s']:>7.1f} {row['speedup']:>7.2f}x "
              f"{row['peak_gib']:>9.2f} {sum(equal):>6}/{len(prompts)}")

    out = Path(args.out or ROOT / "benchmarks" / "logs" / f"spec_bench_{args.dtype}.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"dtype": args.dtype, "max_new_tokens": N, "draft_adapter": args.draft_adapter,
                               "plain": base, "speculative": rows}, indent=2))
    print("wrote", out)


if __name__ == "__main__":
    main()
