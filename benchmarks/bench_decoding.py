"""Benchmark uncached vs cached (and HF generate as a reference) greedy decoding.

    python benchmarks/bench_decoding.py --dtype float16
    python benchmarks/bench_decoding.py --dtype float32 --out benchmarks/logs/kv_bench_fp32.json

For every (input length, output length) it checks that the generated tokens are identical,
and reports prefill time, decode time, decode tokens/s and peak GPU memory (median of
--repeats timed runs after one warm-up run; timings are synchronised with cuda.synchronize).
Exactly N new tokens are forced (no EOS) so lengths are comparable.
"""
import argparse
import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import torch  # noqa: E402

from core.kv_cache import generate_cached, generate_uncached, kv_bytes_per_token  # noqa: E402
from core.model_loader import ADAPTER_REPO, ADAPTER_SUBFOLDER, load_model, load_tokenizer  # noqa: E402
from core.schema import split_note  # noqa: E402
from data.build_prompts import build_messages, load_split  # noqa: E402


def make_prompt_ids(tok, rows, length, device):
    """Real clinical prompts concatenated, then cut to exactly `length` tokens."""
    ids = []
    for r in rows:
        text = tok.apply_chat_template(
            build_messages(split_note(r["note"]), r["criterion_type"], r["criterion_text"]),
            add_generation_prompt=True, tokenize=False)
        ids += tok(text, add_special_tokens=False)["input_ids"]
        if len(ids) >= length:
            break
    return torch.tensor([ids[:length]], device=device)


def hf_generate(model, ids, n_new):
    import time
    torch.cuda.synchronize(); t = time.perf_counter()
    out = model.generate(ids, max_new_tokens=n_new, min_new_tokens=n_new, do_sample=False,
                         temperature=None, top_p=None, top_k=None, use_cache=True,
                         repetition_penalty=1.0)
    torch.cuda.synchronize()
    return out[:, ids.shape[1]:], {"total_s": time.perf_counter() - t}


def timed(fn, model, ids, n_new, repeats):
    fn(model, ids, n_new)                                    # warm-up
    runs, tokens = [], None
    for _ in range(repeats):
        torch.cuda.reset_peak_memory_stats()
        tokens, st = fn(model, ids, n_new)
        st = dict(st)
        st["peak_mem_gib"] = torch.cuda.max_memory_allocated() / 2**30
        runs.append(st)
    med = {k: statistics.median(r[k] for r in runs) for k in runs[0]}
    return tokens, med


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dtype", default="float16", choices=["float16", "float32"])
    ap.add_argument("--input-lens", type=int, nargs="+", default=[128, 256, 512])
    ap.add_argument("--output-lens", type=int, nargs="+", default=[16, 64, 128])
    ap.add_argument("--repeats", type=int, default=3)
    ap.add_argument("--adapter", default=ADAPTER_REPO)
    ap.add_argument("--subfolder", default=ADAPTER_SUBFOLDER)
    ap.add_argument("--no-adapter", action="store_true")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    assert torch.cuda.is_available(), "benchmark needs a GPU"

    tok = load_tokenizer()
    adapter = None if args.no_adapter else args.adapter
    model = load_model(adapter=adapter, subfolder=args.subfolder, dtype=args.dtype)
    rows = load_split("val")                      # benchmark prompts come from validation notes
    dev = "cuda"
    base_mem = torch.cuda.memory_allocated() / 2**30
    bpt = kv_bytes_per_token(model.config, 2 if args.dtype == "float16" else 4)
    print(f"model memory {base_mem:.2f} GiB; KV cache {bpt} bytes/token ({args.dtype})")

    results = []
    print(f"{'in':>5} {'out':>4} {'mode':>9} {'prefill s':>10} {'decode s':>9} {'dec tok/s':>10} "
          f"{'peak GiB':>9} {'match':>6}")
    for L in args.input_lens:
        ids = make_prompt_ids(tok, rows, L, dev)
        for N in args.output_lens:
            ref, s_ref = timed(generate_uncached, model, ids, N, args.repeats)
            got, s_c = timed(generate_cached, model, ids, N, args.repeats)
            hf, s_hf = timed(hf_generate, model, ids, N, args.repeats)
            match_c = torch.equal(ref, got)
            match_hf = torch.equal(ref, hf)
            first_bad = None if match_c else int((ref != got).nonzero()[0, 1])
            for mode, s, m in (("uncached", s_ref, True), ("cached", s_c, match_c)):
                tps = (N - 1) / s["decode_s"]
                print(f"{L:>5} {N:>4} {mode:>9} {s['prefill_s']:>10.3f} {s['decode_s']:>9.3f} "
                      f"{tps:>10.1f} {s['peak_mem_gib']:>9.2f} {str(m):>6}")
            print(f"{L:>5} {N:>4} {'hf_gen':>9} {'-':>10} {s_hf['total_s']:>9.3f} {'-':>10} "
                  f"{s_hf['peak_mem_gib']:>9.2f} {str(match_hf):>6}")
            results.append({"input_len": L, "output_len": N, "uncached": s_ref, "cached": s_c,
                            "hf_generate": s_hf, "cached_equals_uncached": match_c,
                            "hf_equals_uncached": match_hf, "first_mismatch_index": first_bad})

    out = Path(args.out or ROOT / "benchmarks" / "logs" / f"kv_bench_{args.dtype}.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"dtype": args.dtype, "adapter": adapter, "model_mem_gib": base_mem,
                               "kv_bytes_per_token": bpt, "repeats": args.repeats,
                               "results": results}, indent=2))
    print("wrote", out)


if __name__ == "__main__":
    main()
