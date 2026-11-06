"""Compare reference, tiled (online softmax, plain PyTorch) and PyTorch SDPA attention.

    python benchmarks/bench_attention.py

Shapes follow Qwen2.5-1.5B: 12 query heads, head_dim 128, batch 1, causal, fp16 inputs.
For each sequence length: numerical error vs an fp32 reference (tiled run on fp32 inputs shows
the pure algorithmic error; on fp16 inputs it also includes fp16 output rounding), median
runtime of --repeats synchronised runs after a warm-up, and peak extra GPU memory.
"""
import argparse
import json
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import torch  # noqa: E402

from core.tiled_attention import reference_attention, sdpa_attention, tiled_attention  # noqa: E402


def bench(fn, repeats):
    fn(); torch.cuda.synchronize()                       # warm-up
    times, mems = [], []
    for _ in range(repeats):
        torch.cuda.synchronize()
        base = torch.cuda.memory_allocated()
        torch.cuda.reset_peak_memory_stats()
        t = time.perf_counter()
        out = fn()
        torch.cuda.synchronize()
        times.append(time.perf_counter() - t)
        mems.append(torch.cuda.max_memory_allocated() - base)
        del out
    return statistics.median(times) * 1000, statistics.median(mems) / 2**20


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lens", type=int, nargs="+", default=[256, 512, 1024, 2048, 4096])
    ap.add_argument("--heads", type=int, default=12)
    ap.add_argument("--head-dim", type=int, default=128)
    ap.add_argument("--block", type=int, default=128)
    ap.add_argument("--repeats", type=int, default=5)
    ap.add_argument("--out", default=str(ROOT / "benchmarks" / "logs" / "attn_bench.json"))
    args = ap.parse_args()
    assert torch.cuda.is_available(), "benchmark needs a GPU"

    rows = []
    print(f"{'T':>5} {'method':>10} {'ms':>9} {'extra MiB':>10} {'max err':>10} {'mean err':>10}")
    for T in args.lens:
        g = torch.Generator(device="cuda").manual_seed(0)
        mk = lambda: torch.randn(1, args.heads, T, args.head_dim, device="cuda",  # noqa: E731
                                 generator=g, dtype=torch.float16)
        q, k, v = mk(), mk(), mk()
        ref = reference_attention(q.float(), k.float(), v.float(), True)    # fp32 ground truth
        q32, k32, v32 = q.float(), k.float(), v.float()
        methods = {
            "reference": lambda: reference_attention(q, k, v, True),
            "tiled": lambda: tiled_attention(q, k, v, True, args.block, args.block),
            "sdpa": lambda: sdpa_attention(q, k, v, True),
        }
        for name, fn in methods.items():
            out = fn().float()
            err = (out - ref).abs()
            ms, mib = bench(fn, args.repeats)
            row = {"T": T, "method": name, "ms": ms, "extra_mib": mib,
                   "max_err_fp16_inputs": err.max().item(), "mean_err_fp16_inputs": err.mean().item()}
            if name == "tiled":
                e32 = (tiled_attention(q32, k32, v32, True, args.block, args.block) - ref).abs()
                row["max_err_fp32_inputs"] = e32.max().item()
            rows.append(row)
            print(f"{T:>5} {name:>10} {ms:>9.2f} {mib:>10.1f} {row['max_err_fp16_inputs']:>10.2e} "
                  f"{row['mean_err_fp16_inputs']:>10.2e}")
            del out, err
        print(f"      tiled error with fp32 inputs (algorithmic only): {rows[-2]['max_err_fp32_inputs']:.2e}")

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps({"heads": args.heads, "head_dim": args.head_dim,
                                          "block": args.block, "rows": rows}, indent=2))
    print("wrote", args.out)


if __name__ == "__main__":
    main()
