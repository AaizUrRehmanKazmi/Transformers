# Clinical-trial criterion screening with a fine-tuned Transformer

Educational research prototype for the Generative AI course (Assignment 2). Given a patient note and one
inclusion/exclusion criterion of a clinical trial, a LoRA-fine-tuned Qwen2.5-1.5B-Instruct returns an eligibility
label and the supporting patient-sentence IDs. The repository also contains our own implementations of
KV-cached decoding, tiled online-softmax attention and greedy speculative decoding, and a browser app.

> **Not a clinical decision tool.** Predictions can be wrong and must never be used for patient enrollment.

Author: `<your name>`, roll no. 23I-0589, section D, FAST-NUCES.

## Links

| Item | Location |
|---|---|
| Trained adapter (LoRA, final checkpoint) | https://huggingface.co/AK302/trialgpt-qwen1.5b-lora (subfolder `lora_r16_bal/epoch3`) |
| Split manifest | `data/split_manifest.json` |
| Benchmark and evaluation logs | `benchmarks/logs/`, `eval/results/` |
| Report (PDF) | `<link or path>` |
| Demo video (5-7 min) | `<link>` |

## Setup

```bash
git clone https://github.com/AaizUrRehmanKazmi/Transformers.git
cd Transformers
python -m venv .venv && source .venv/bin/activate        # optional
pip install -r requirements.txt
python -m pytest -q tests                                 # 100 tests, no GPU or download needed
```

Tested with Python 3.13 on Kaggle (T4 16 GB): torch, transformers, peft and gradio versions are in
`requirements.txt` (record exact versions with `pip freeze` if you need to reproduce bit-for-bit).
The base model (about 3 GB) and the adapter (about 74 MB) download automatically on first use. If the adapter
repo is private, run `huggingface-cli login` or set `HF_TOKEN` first.

## Run the application

```bash
python app/app.py                # open http://localhost:7860
python app/app.py --no-draft     # skip the 0.5B draft model (disables speculative mode)
python app/app.py --share        # temporary public link (e.g. when started from Kaggle)
```

A GPU (fp16) is used if available. Without a GPU the app runs on the CPU in fp32; expect several seconds per
criterion. The app lets you paste a patient note, enter inclusion/exclusion criteria (or load a synthetic example),
choose the decoding mode, inspect every criterion with its cited evidence sentences, and download a report
(Markdown or HTML). The *Inference benchmark* tab runs plain, KV-cached and speculative decoding and the
attention implementations live.

## Data and split

Only `ncbi/TrialGPT-Criterion-Annotations` is used (1015 criterion-level rows, 53 patients). The patient-grouped
split sorts unique patient IDs, shuffles with `numpy.random.default_rng(42)` and assigns 37 / 8 / 8 patients to
train / validation / test (603 / 206 / 206 rows). The GPT-4 columns (`gpt4_*`, `explanation_correctness`) are never
used as input. Tests check that there is no patient overlap and no GPT-4 text in prompts.

```bash
python data/prepare_split.py            # writes data/split_manifest.json
python data/build_prompts.py            # token-length / truncation / label statistics
```

## Reproduce the experiments

```bash
# Fine-tuning (about 13 minutes on a Kaggle T4); final run:
python train/finetune.py --name lora_r16_bal --epochs 3 --batch-size 2 --grad-accum 8 --grad-ckpt \
       --oversample-min 80 --max-repeat 4 --hub-id <your-hf-user>/trialgpt-qwen1.5b-lora

# Evaluation (pure greedy decoding, repetition_penalty=1.0), validation then the single final test run
python eval/run_eval.py --name baseline_val_greedy --split val
python eval/run_eval.py --name final_val_greedy --split val --adapter <adapter_dir>
python eval/run_eval.py --name baseline_test_greedy --split test --final
python eval/run_eval.py --name final_test_greedy --split test --final --adapter <adapter_dir>
python eval/error_analysis.py --name final_test_greedy --split test --final

# Inference benchmarks
python benchmarks/bench_decoding.py --dtype float16        # uncached vs KV-cached vs HF generate
python benchmarks/bench_attention.py                       # reference vs tiled vs SDPA
python benchmarks/bench_speculative.py --dtype float16     # plain vs speculative greedy
```

`<adapter_dir>` is a local adapter directory (for example a `snapshot_download` of the Hub repo's
`lora_r16_bal/epoch3` folder). `--test` evaluation requires the explicit `--final` flag.

Training configuration: LoRA r=16, alpha=32, dropout 0.05 on all attention and MLP projections, lr 2e-4 with
cosine decay and 5% warmup, 3 epochs, effective batch 16, max length 1024 tokens (longest prompt: 567 tokens, so
nothing is truncated), seed 42, answer-only loss, rare (criterion type, label) groups oversampled up to 80 rows
with at most 4 copies. The checkpoint was chosen on validation task metrics and then frozen.

## Results (held-out test split, 8 patients, greedy decoding)

| | Base model (zero-shot) | Majority class | Fine-tuned |
|---|---|---|---|
| Accuracy | 0.155 | 0.626 | **0.704** |
| Macro-F1 (classes present in test gold) | 0.165 | 0.272 | **0.603** |
| Macro-F1 (all valid labels) | - | - | 0.503 |
| Evidence micro precision / recall / F1 | 0.082 / 0.734 / 0.147 | - | 0.437 / 0.585 / 0.500 |

Validation (fine-tuned): accuracy 0.738, macro-F1 0.572, evidence F1 0.561. The weakest point is "not enough
information" for exclusion criteria (recall 4/28 on test): the model often predicts "not excluded" when
information is missing. Details: `eval/results/*/metrics.json` and `error_analysis.md`.

| Inference mechanism | Result |
|---|---|
| KV cache (own implementation) | Token-identical to the uncached reference in all 9 input/output length combinations; about 27 tok/s cached vs 5-23 tok/s uncached (5x faster at 512 input tokens) |
| Tiled online-softmax attention | Error vs fp32 reference about 5e-7 (fp32 inputs); extra memory 17 MiB vs 2304 MiB at T=4096; about 4x slower than the plain reference and 68x slower than PyTorch SDPA (Python loop vs fused kernel) |
| Speculative decoding (0.5B draft) | Token-identical to plain greedy on 20/20 prompts for k = 1..8; acceptance 0.81 (k=1) to 0.48 (k=8); 0.50x-0.74x speed (slower: decoding here is launch-overhead bound, so draft steps cost almost as much as target steps) |

## Repository layout

```
core/        schema, model loader, kv_cache.py, tiled_attention.py, speculative.py
data/        split script, prompt builder, split_manifest.json
train/       finetune.py, runs/*/ (config, log.jsonl, curves.png; adapter weights are on the Hub)
eval/        classification, evidence metrics, run_eval.py, error_analysis.py, results/
benchmarks/  decoding, attention and speculative benchmarks, logs/
app/         Gradio application (app.py) and screening logic (screening.py)
tests/       100 tests (split leakage, prompts, metrics, cache equality, attention, speculation, app logic)
report/      IEEE LaTeX report
```

## Limitations

Small training set (37 patients) and a small, noisy test set (8 patients; one label never occurs in test gold);
rare labels ("not included", "not applicable") are weak; evidence recall is limited; the overall patient-level
outcome in the app is a rule-based aggregation of criterion-level predictions, not a ground-truth label.

## AI assistance

An AI assistant (Claude, Anthropic) was used for code scaffolding, debugging and drafting explanations. All code was
run and tested by the author. `<edit this paragraph to describe exactly what you used it for>`
