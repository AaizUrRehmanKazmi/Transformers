"""Build every figure and LaTeX table of the report from the result files in this repository.

    python report/make_report_assets.py

Reads  eval/results/*/metrics.json, benchmarks/logs/*.json, train/runs/*/log.jsonl
Writes report/figures/*.png and report/tables/*.tex (include with \\input{tables/<name>}).
Nothing is typed by hand: re-run after any new experiment and the report numbers follow.
"""
import json
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
FIG, TAB = ROOT / "report" / "figures", ROOT / "report" / "tables"
FIG.mkdir(parents=True, exist_ok=True)
TAB.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({"font.size": 7, "axes.titlesize": 8, "savefig.dpi": 300, "savefig.bbox": "tight"})

SHORT = {"included": "incl.", "not included": "not incl.", "excluded": "excl.", "not excluded": "not excl.",
         "not enough information": "NEI", "not applicable": "N/A", "invalid": "invalid"}
ORDER = ["included", "not included", "excluded", "not excluded", "not enough information", "not applicable"]


def load(rel):
    return json.loads((ROOT / rel).read_text())


def fmt(x, d=3):
    return "---" if x is None else f"{x:.{d}f}"


def write_table(name, header, rows, colspec, caption_note=""):
    lines = [f"\\begin{{tabular}}{{{colspec}}}", "\\hline", " & ".join(header) + " \\\\", "\\hline"]
    lines += [" & ".join(str(c) for c in r) + " \\\\" for r in rows]
    lines += ["\\hline", "\\end{tabular}"]
    (TAB / f"{name}.tex").write_text("\n".join(lines) + "\n")


# ------------------------------------------------------------------ classification tables / figures
test = load("eval/results/final_test_greedy/metrics.json")
test_base = load("eval/results/baseline_test_greedy/metrics.json")
val = load("eval/results/final_val_greedy/metrics.json")
val_base = load("eval/results/baseline_val_greedy/metrics.json")


def main_rows():
    def col(m):
        o, e = m["overall"], m["evidence"]["overall"]["micro"]
        return [fmt(o["accuracy"]), fmt(o["macro_f1_present"]), fmt(o["macro_f1_all"]),
                fmt(e["precision"]), fmt(e["recall"]), fmt(e["f1"]), fmt(o["invalid_rate"])]
    maj_t, maj_v = test["majority_baseline"], val["majority_baseline"]
    maj = lambda m: [fmt(m["accuracy"]), fmt(m["macro_f1_present"]), fmt(m["macro_f1_all"]), "---", "---", "---", "---"]  # noqa: E731
    names = ["Accuracy", "Macro-F1 (present)", "Macro-F1 (all)", "Evidence P", "Evidence R", "Evidence F1", "Invalid rate"]
    cols = [maj(val["majority_baseline"]), col(val_base), col(val), maj(test["majority_baseline"]), col(test_base), col(test)]
    return [[n] + [c[i] for c in cols] for i, n in enumerate(names)]


write_table("main_results", ["Metric", "Maj.", "Base", "Tuned", "Maj.", "Base", "Tuned"], main_rows(), "lcccccc")

rows = []
for lab in ORDER:
    pc = test["overall"]["per_class"][lab]
    bc = test_base["overall"]["per_class"][lab]
    rows.append([lab, fmt(pc["precision"], 2), fmt(pc["recall"], 2), fmt(pc["f1"], 2), fmt(bc["f1"], 2), pc["support"]])
write_table("per_class_test", ["Class", "P", "R", "F1", "Base F1", "n"], rows, "lccccr")

for scope, title in (("inclusion", "Inclusion"), ("exclusion", "Exclusion")):
    m, mb = test[scope], test_base[scope]
    write_table(f"scope_{scope}", ["Split", "Acc.", "Macro-F1 (pres.)", "Macro-F1 (all)", "n"],
                [[f"{title}, tuned", fmt(m["accuracy"]), fmt(m["macro_f1_present"]), fmt(m["macro_f1_all"]), m["n"]],
                 [f"{title}, base", fmt(mb["accuracy"]), fmt(mb["macro_f1_present"]), fmt(mb["macro_f1_all"]), mb["n"]]], "lccc r")


def confusion(m, scope, fname, title):
    cm = m[scope]["confusion_matrix"]
    labels, M = cm["labels"], np.array(cm["rows_gold_cols_pred"])
    keep = [i for i in range(len(labels)) if M[i].sum() > 0 or M[:, i].sum() > 0]
    M2, names = M[np.ix_(keep, keep)], [SHORT.get(labels[i], labels[i]) for i in keep]
    fig, ax = plt.subplots(figsize=(3.4, 3.0))
    ax.imshow(M2, cmap="Blues")
    for i in range(len(keep)):
        for j in range(len(keep)):
            ax.text(j, i, M2[i, j], ha="center", va="center", color="white" if M2[i, j] > M2.max() / 2 else "black")
    ax.set_xticks(range(len(keep)), names, rotation=45, ha="right")
    ax.set_yticks(range(len(keep)), names)
    ax.set_xlabel("predicted"); ax.set_ylabel("gold"); ax.set_title(title)
    fig.tight_layout(); fig.savefig(FIG / fname); plt.close(fig)


confusion(test, "overall", "cm_test_overall.png", "Test: all criteria")
confusion(test, "inclusion", "cm_test_inclusion.png", "Test: inclusion criteria")
confusion(test, "exclusion", "cm_test_exclusion.png", "Test: exclusion criteria")

fig, ax = plt.subplots(figsize=(3.4, 2.4))
labs = [l for l in ORDER if test["overall"]["per_class"][l]["support"] > 0]
x = np.arange(len(labs))
ax.bar(x - 0.2, [test_base["overall"]["per_class"][l]["f1"] for l in labs], 0.4, label="base (zero-shot)")
ax.bar(x + 0.2, [test["overall"]["per_class"][l]["f1"] for l in labs], 0.4, label="fine-tuned")
ax.set_xticks(x, [f"{SHORT[l]}\n(n={test['overall']['per_class'][l]['support']})" for l in labs])
ax.set_ylabel("F1 (test)"); ax.legend(); fig.tight_layout(); fig.savefig(FIG / "per_class_f1.png"); plt.close(fig)

# ------------------------------------------------------------------ training curves
fig, ax = plt.subplots(figsize=(3.4, 2.4))
for run, lab in (("lora_r16", "plain"), ("lora_r16_bal", "oversampled (final)")):
    p = ROOT / "train" / "runs" / run / "log.jsonl"
    if not p.exists():
        continue
    recs = [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
    tr = [(r["step"], r["train_loss"]) for r in recs if "train_loss" in r]
    va = [(r["step"], r["val_loss"]) for r in recs if "val_loss" in r]
    line, = ax.plot(*zip(*tr), alpha=0.5, lw=0.8, label=f"{lab}: train")
    ax.plot(*zip(*va), "o-", color=line.get_color(), label=f"{lab}: validation")
ax.set_xlabel("optimizer step"); ax.set_ylabel("answer-token loss"); ax.set_yscale("log"); ax.legend(fontsize=5.5)
fig.tight_layout(); fig.savefig(FIG / "training_curves.png"); plt.close(fig)

# ------------------------------------------------------------------ KV-cache benchmark
kv = load("benchmarks/logs/kv_bench_float16.json")["results"]
tps = lambda s: (s["new_tokens"] - 1) / s["decode_s"]  # noqa: E731
rows = []
for r in kv:
    u, c = r["uncached"], r["cached"]
    rows.append([r["input_len"], r["output_len"], f"{tps(u):.1f}", f"{tps(c):.1f}", f"{u['decode_s'] / c['decode_s']:.2f}",
                 f"{u['prefill_s'] * 1000:.0f}", f"{u['peak_mem_gib']:.2f}", f"{c['peak_mem_gib']:.2f}",
                 "yes" if r["cached_equals_uncached"] else "NO"])
write_table("kv_cache", ["In", "Out", "Unc. tok/s", "Cached tok/s", "Decode speedup", "Prefill ms", "Unc. GiB", "Cached GiB", "Identical"],
            rows, "rrcccccc c")
fig, ax = plt.subplots(figsize=(3.4, 2.4))
sel = [r for r in kv if r["output_len"] == max(x["output_len"] for x in kv)]
ax.plot([r["input_len"] for r in sel], [tps(r["uncached"]) for r in sel], "o-", label="uncached")
ax.plot([r["input_len"] for r in sel], [tps(r["cached"]) for r in sel], "s-", label="KV-cached")
ax.set_xlabel("prompt length (tokens)"); ax.set_ylabel("decode tokens/s"); ax.legend()
fig.tight_layout(); fig.savefig(FIG / "kv_throughput.png"); plt.close(fig)

# ------------------------------------------------------------------ attention benchmark
att = load("benchmarks/logs/attn_bench.json")["rows"]
Ts = sorted({r["T"] for r in att})
by = {(r["T"], r["method"]): r for r in att}
rows = []
for T in Ts:
    rows.append([T] + [f"{by[(T, m)]['ms']:.2f}" for m in ("reference", "tiled", "sdpa")]
                + [f"{by[(T, m)]['extra_mib']:.1f}" for m in ("reference", "tiled", "sdpa")]
                + [f"{by[(T, 'tiled')]['max_err_fp32_inputs']:.1e}", f"{by[(T, 'tiled')]['max_err_fp16_inputs']:.1e}"])
write_table("attention", ["T", "Ref ms", "Tiled ms", "SDPA ms", "Ref MiB", "Tiled MiB", "SDPA MiB", "Err fp32", "Err fp16"],
            rows, "rcccccccc")
fig, axs = plt.subplots(1, 2, figsize=(6.8, 2.4))
for m, lab in (("reference", "reference"), ("tiled", "tiled online-softmax"), ("sdpa", "PyTorch SDPA")):
    axs[0].plot(Ts, [by[(T, m)]["ms"] for T in Ts], "o-", label=lab)
    axs[1].plot(Ts, [by[(T, m)]["extra_mib"] for T in Ts], "o-", label=lab)
for a, yl in zip(axs, ("time (ms)", "extra GPU memory (MiB)")):
    a.set_xscale("log", base=2); a.set_yscale("log"); a.set_xlabel("sequence length T"); a.set_ylabel(yl)
axs[0].legend(); fig.tight_layout(); fig.savefig(FIG / "attention_bench.png"); plt.close(fig)

# ------------------------------------------------------------------ speculative decoding
sp = load("benchmarks/logs/spec_bench_float16.json")
rows = [["plain", "---", "---", fmt(sp["plain"]["latency_s"]), fmt(sp["plain"]["tok_s"], 1), "1.00", f"{sp['plain']['peak_gib']:.2f}", "---"]]
for r in sp["speculative"]:
    rows.append([r["k"], fmt(r["acceptance_rate"], 2), fmt(r["tokens_per_round"], 2), fmt(r["latency_s"]), fmt(r["tok_s"], 1),
                 f"{r['speedup']:.2f}", f"{r['peak_gib']:.2f}", f"{r['n_equal']}/{r['n_prompts']}"])
write_table("speculative", ["k", "Accept.", "Tok/round", "s/prompt", "Tok/s", "Speedup", "Peak GiB", "Identical"], rows, "rccccccc")
fig, ax = plt.subplots(figsize=(3.4, 2.4))
ks = [r["k"] for r in sp["speculative"]]
ax.plot(ks, [r["speedup"] for r in sp["speculative"]], "o-", label="speedup vs plain")
ax.axhline(1.0, color="gray", ls="--", lw=0.8)
ax.set_xlabel("draft length k"); ax.set_ylabel("speedup (x)")
ax2 = ax.twinx(); ax2.plot(ks, [r["acceptance_rate"] for r in sp["speculative"]], "s--", color="tab:orange", label="acceptance")
ax2.set_ylabel("draft acceptance rate")
fig.legend(loc="upper right", bbox_to_anchor=(0.88, 0.88), fontsize=6)
fig.tight_layout(); fig.savefig(FIG / "speculative.png"); plt.close(fig)

print("figures:", sorted(p.name for p in FIG.glob("*.png")))
print("tables: ", sorted(p.name for p in TAB.glob("*.tex")))
