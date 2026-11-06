"""Browser application: clinical-trial criterion screening with the fine-tuned Transformer.

    pip install -r requirements.txt
    python app/app.py                 # then open http://localhost:7860
    python app/app.py --share         # temporary public gradio.live link (e.g. from Kaggle)
    python app/app.py --no-draft      # skip the draft model (disables speculative mode)

The target model and LoRA adapter are downloaded from the Hugging Face Hub on first start.
Uses a GPU (fp16) if available, otherwise the CPU (fp32, much slower).
"""
import argparse
import statistics
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import gradio as gr  # noqa: E402
import matplotlib  # noqa: E402
import torch  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from app.screening import (DISCLAIMER, RULES, SAMPLES, InputError, aggregate, render_cards_html,  # noqa: E402
                           save_report, validate_inputs, age_check)
from core.kv_cache import generate_cached, generate_uncached  # noqa: E402
from core.model_loader import (ADAPTER_REPO, ADAPTER_SUBFOLDER, DRAFT_ID, TARGET_ID,  # noqa: E402
                               default_device, load_model, load_tokenizer)
from core.schema import parse_output, render_explanation  # noqa: E402
from core.speculative import generate_speculative, tokenizers_compatible  # noqa: E402
from core.tiled_attention import reference_attention, sdpa_attention, tiled_attention  # noqa: E402
from data.build_prompts import build_messages  # noqa: E402

MAX_CONTEXT, MAX_NEW, SPEC_K = 2048, 64, 4
MODES = {"KV-cached greedy (default)": "cached",
         "Speculative greedy (0.5B draft)": "speculative",
         "Plain greedy, no cache (slow reference)": "uncached"}
REPORT_DIR = Path(tempfile.gettempdir()) / "trial_screening_reports"


class Engine:
    def __init__(self, adapter, subfolder, dtype, load_draft):
        self.device = default_device()
        self.dtype = dtype or ("float16" if self.device == "cuda" else "float32")
        if self.device == "cpu":
            print("WARNING: no GPU found; running on CPU (fp32). Expect several seconds per criterion.")
        print("Loading tokenizer and target model + adapter ...")
        self.tok = load_tokenizer(TARGET_ID)
        self.target = load_model(TARGET_ID, adapter, subfolder or None, self.dtype, self.device)
        self.draft = None
        if load_draft:
            print("Loading draft model ...")
            self.draft = load_model(DRAFT_ID, None, None, self.dtype, self.device)
            assert tokenizers_compatible(self.tok, load_tokenizer(DRAFT_ID)), "draft tokenizer mismatch"
        self.eos = tuple(sorted({self.tok.convert_tokens_to_ids("<|im_end|>"), self.tok.eos_token_id}))
        self.adapter = f"{adapter}/{subfolder}" if subfolder else str(adapter)

    def encode(self, sentences, ctype, ctext, reserve):
        kept = list(sentences)
        while True:
            text = self.tok.apply_chat_template(build_messages(kept, ctype, ctext),
                                                add_generation_prompt=True, tokenize=False)
            ids = self.tok(text, add_special_tokens=False)["input_ids"]
            if len(ids) + reserve <= MAX_CONTEXT or len(kept) <= 1:
                break
            kept.pop()                      # drop trailing sentences until the prompt fits
        return torch.tensor([ids], device=self.device), kept, len(kept) < len(sentences)

    def generate(self, ids, mode, max_new, k=SPEC_K, force=False):
        eos = () if force else self.eos
        if mode == "uncached":
            return generate_uncached(self.target, ids, max_new, eos)
        if mode == "cached":
            return generate_cached(self.target, ids, max_new, eos)
        return generate_speculative(self.target, self.draft, ids, max_new, k, eos)


ENGINE = None


def screen(note, incl, excl, mode_label, progress=gr.Progress()):
    try:
        sentences, criteria = validate_inputs(note, incl, excl)
    except InputError as e:
        raise gr.Error(str(e))
    mode = MODES[mode_label]
    if mode == "speculative" and ENGINE.draft is None:
        raise gr.Error("The draft model is not loaded (app was started with --no-draft).")
    by_id = dict(sentences)
    results = []
    for n, (ctype, ctext) in enumerate(criteria):
        progress(n / len(criteria), desc=f"Criterion {n + 1}/{len(criteria)}")
        ids, kept, truncated = ENGINE.encode(sentences, ctype, ctext, MAX_NEW)
        t0 = time.perf_counter()
        toks, _ = ENGINE.generate(ids, mode, MAX_NEW)
        raw = ENGINE.tok.decode(toks[0], skip_special_tokens=True)
        parsed = parse_output(raw, ctype, kept[-1][0] + 1)
        ev = [(i, by_id[i]) for i in parsed.evidence if i in by_id] if parsed.valid else []
        results.append({
            "ctype": ctype, "criterion": ctext, "valid": parsed.valid, "error": parsed.error, "raw": raw,
            "label": parsed.label if parsed.valid else None, "evidence": ev, "truncated": truncated,
            "seconds": time.perf_counter() - t0,
            "age_flag": age_check(sentences, ctype, ctext, parsed.label if parsed.valid else None),
            "explanation": (render_explanation(parsed.label, parsed.evidence, sentences) if parsed.valid
                            else "The model output could not be parsed; treated as missing information."),
        })
    overall = aggregate(results)
    meta = {"timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()), "model": TARGET_ID,
            "adapter": ENGINE.adapter, "decoding_mode": mode_label, "max_new_tokens": MAX_NEW,
            "device": f"{ENGINE.device} / {ENGINE.dtype}"}
    md_path, html_path = save_report(REPORT_DIR, results, sentences, overall, meta)
    summary = f"### {overall['status']}\n{overall['reason']}"
    if overall["missing"]:
        summary += "\n\n**Missing information for:**\n" + "\n".join(f"- {c}" for c in overall["missing"])
    if overall.get("unsupported"):
        summary += ("\n\n**Decisions without cited evidence (verify manually):**\n"
                    + "\n".join(f"- {c}" for c in overall["unsupported"]))
    if overall.get("contradictions"):
        summary += ("\n\n**Labels contradicting the rule-based age check (verify manually):**\n"
                    + "\n".join(f"- {c}" for c in overall["contradictions"]))
    if any(r["truncated"] for r in results):
        summary += "\n\n*Warning: the note was truncated for at least one criterion (context limit).*"
    table = [[r["ctype"], r["criterion"], r["label"] or "unparsed",
              ", ".join(str(i) for i, _ in r["evidence"]) or "-", f"{r['seconds']:.2f}"] for r in results]
    return summary, table, render_cards_html(results, sentences, overall), md_path, html_path


def benchmark(note, incl, excl, n_new, k, progress=gr.Progress()):
    try:
        sentences, criteria = validate_inputs(note, incl, excl)
    except InputError as e:
        raise gr.Error(str(e))
    ctype, ctext = criteria[0]
    ids, _, _ = ENGINE.encode(sentences, ctype, ctext, int(n_new))
    modes = ["uncached", "cached"] + (["speculative"] if ENGINE.draft is not None else [])
    cuda = ENGINE.device == "cuda"
    rows, outs, base_total = [], {}, None
    for n, mode in enumerate(modes):
        progress(n / len(modes), desc=f"Running {mode}")
        ENGINE.generate(ids, mode, 4, int(k), force=True)               # warm-up
        if cuda:
            torch.cuda.reset_peak_memory_stats()
        toks, st = ENGINE.generate(ids, mode, int(n_new), int(k), force=True)
        peak = f"{torch.cuda.max_memory_allocated() / 2**30:.2f}" if cuda else "n/a (CPU)"
        total = st["prefill_s"] + st["decode_s"]
        base_total = base_total or total
        outs[mode] = toks
        rows.append([mode, f"{st['prefill_s']:.3f}", f"{st['decode_s']:.3f}", f"{total:.3f}",
                     f"{(toks.shape[1] - 1) / st['decode_s']:.1f}", peak, f"{base_total / total:.2f}x",
                     "reference" if mode == "uncached" else str(bool(torch.equal(outs['uncached'], toks))),
                     f"{st['acceptance_rate']:.2f}" if st.get("acceptance_rate") is not None else "-"])
    fig, ax = plt.subplots(figsize=(5.5, 3))
    ax.bar([r[0] for r in rows], [float(r[3]) for r in rows])
    ax.set_ylabel("total seconds"); ax.set_title(f"{int(n_new)} new tokens, {ids.shape[1]} prompt tokens")
    fig.tight_layout()
    note_txt = (f"Benchmark criterion: *{ctext}* ({ctype}). Exactly {int(n_new)} tokens are generated "
                "(end-of-answer stop disabled) so all modes do identical work. Greedy decoding: all "
                "modes should produce identical tokens; a False in the equality column signals a numerical "
                "difference or a bug.")
    return rows, fig, note_txt


def attention_check(T, causal):
    T = int(T)
    dev = ENGINE.device
    dt = torch.float16 if dev == "cuda" else torch.float32
    g = torch.Generator(device=dev).manual_seed(0)
    q, k, v = (torch.randn(1, 12, T, 128, device=dev, generator=g, dtype=dt) for _ in range(3))
    ref = reference_attention(q.float(), k.float(), v.float(), causal)
    fns = {"reference (softmax(QK^T)V)": lambda: reference_attention(q, k, v, causal),
           "tiled online-softmax (ours)": lambda: tiled_attention(q, k, v, causal, 128, 128),
           "PyTorch SDPA (fused backend)": lambda: sdpa_attention(q, k, v, causal)}
    rows = []
    for name, fn in fns.items():
        fn()
        times, mem = [], "n/a (CPU)"
        for _ in range(3):
            if dev == "cuda":
                torch.cuda.synchronize(); base = torch.cuda.memory_allocated(); torch.cuda.reset_peak_memory_stats()
            t0 = time.perf_counter(); out = fn()
            if dev == "cuda":
                torch.cuda.synchronize(); mem = f"{(torch.cuda.max_memory_allocated() - base) / 2**20:.1f}"
            times.append((time.perf_counter() - t0) * 1000)
        rows.append([name, f"{statistics.median(times):.2f}", mem, f"{(out.float() - ref).abs().max().item():.2e}"])
    return rows


def build_ui():
    with gr.Blocks(title="Clinical trial eligibility screening (prototype)") as demo:
        gr.Markdown(f"# Clinical trial eligibility screening\n**{DISCLAIMER}**")
        with gr.Tab("Screening"):
            sample = gr.Dropdown(["(none)"] + list(SAMPLES), value="(none)", label="Load a synthetic example")
            note = gr.Textbox(lines=9, label="Patient note (plain text, or numbered '0. ...' lines)")
            with gr.Row():
                incl = gr.Textbox(lines=5, label="Inclusion criteria (one per line)")
                excl = gr.Textbox(lines=5, label="Exclusion criteria (one per line)")
            mode = gr.Radio(list(MODES), value=list(MODES)[0], label="Inference mode (all are exact greedy decoding)")
            run = gr.Button("Run screening", variant="primary")
            summary = gr.Markdown()
            table = gr.Dataframe(headers=["Type", "Criterion", "Predicted label", "Cited sentence ids", "Seconds"],
                                 interactive=False, wrap=True)
            cards = gr.HTML()
            with gr.Row():
                md_file = gr.File(label="Download report (Markdown)")
                html_file = gr.File(label="Download report (HTML, printable to PDF)")
            run.click(screen, [note, incl, excl, mode], [summary, table, cards, md_file, html_file])
            sample.change(lambda s: (SAMPLES[s]["note"], SAMPLES[s]["inclusion"], SAMPLES[s]["exclusion"])
                          if s in SAMPLES else (gr.update(), gr.update(), gr.update()), sample, [note, incl, excl])
        with gr.Tab("Inference benchmark"):
            gr.Markdown("Runs the **first criterion** from the Screening tab with each decoding mechanism, live. "
                        "On CPU keep the token count small.")
            with gr.Row():
                n_new = gr.Slider(8, 128, value=48, step=8, label="New tokens to generate")
                k = gr.Slider(1, 8, value=SPEC_K, step=1, label="Speculative draft length k")
            bench_btn = gr.Button("Run decoding benchmark")
            bench_tbl = gr.Dataframe(headers=["Mode", "Prefill s", "Decode s", "Total s", "Decode tok/s", "Peak GiB",
                                              "Speedup vs uncached", "Tokens identical", "Draft acceptance"], interactive=False)
            bench_plot, bench_txt = gr.Plot(), gr.Markdown()
            bench_btn.click(benchmark, [note, incl, excl, n_new, k], [bench_tbl, bench_plot, bench_txt])
            gr.Markdown("### Attention implementations")
            with gr.Row():
                T = gr.Slider(128, 2048, value=512, step=128, label="Sequence length T (12 heads, head dim 128)")
                causal = gr.Checkbox(value=True, label="Causal mask")
            att_btn = gr.Button("Compare attention implementations")
            att_tbl = gr.Dataframe(headers=["Method", "Median ms", "Extra GPU MiB", "Max abs error vs fp32 reference"],
                                   interactive=False)
            att_btn.click(attention_check, [T, causal], att_tbl)
        with gr.Tab("About"):
            gr.Markdown(
                f"**Model:** {TARGET_ID} fine-tuned with LoRA (r=16) on the TrialGPT criterion annotations "
                "(patient-grouped split, seed 42). Labels: included / not included (inclusion), excluded / "
                "not excluded (exclusion), not enough information, not applicable. Greedy decoding, "
                "repetition penalty 1.0.\n\n**Overall outcome rules:**\n```\n" + RULES + "\n```\n"
                "**Limitations:** small training set (37 patients); weak on 'not enough information' for exclusion "
                "criteria and on rare labels; evidence recall is limited. Not for clinical use.")
    return demo


def main():
    global ENGINE
    ap = argparse.ArgumentParser()
    ap.add_argument("--adapter", default=ADAPTER_REPO, help="Hub repo id or local adapter directory")
    ap.add_argument("--subfolder", default=ADAPTER_SUBFOLDER, help="adapter subfolder ('' for a local dir)")
    ap.add_argument("--dtype", default=None, choices=[None, "float16", "float32"])
    ap.add_argument("--no-draft", action="store_true")
    ap.add_argument("--port", type=int, default=7860)
    ap.add_argument("--share", action="store_true")
    args = ap.parse_args()
    ENGINE = Engine(args.adapter, args.subfolder, args.dtype, not args.no_draft)
    print("Models ready. Starting the web interface ...")
    build_ui().queue().launch(server_name="0.0.0.0", server_port=args.port, share=args.share)


if __name__ == "__main__":
    main()
