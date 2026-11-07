# Reproducing the submission

## Environment

The original repository describes GPU experiments on a Kaggle T4 (16 GB), Python 3.13. A complete original package lock was not retained. Saved GPU logs are historical results, not measurements from the current CPU machine.

The current CPU environment passed 113 tests on November 7, 2026: Python 3.14.8, torch 2.15.0+cpu, transformers 5.22.1, peft 0.21.2, gradio 6.31.0, datasets 5.1.0, accelerate 1.15.0, numpy 2.5.4, scikit-learn 1.9.1, pandas 3.1.1, matplotlib 3.11.2, huggingface_hub 2.4.0, pytest 9.2.0. See `requirements-tested-cpu.txt` for direct dependency constraints. This is a tested-version record, not a claim of a clean installation or original GPU equivalence.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m pytest -q tests
```

For the recorded CPU package versions, use `pip install -r requirements-tested-cpu.txt`; availability depends on platform and package index. Use the appropriate PyTorch CUDA build for GPU work. The existing implementation does not require bitsandbytes quantization.

## Start the application

```bash
source .venv/bin/activate
python app/app.py --no-draft
```

Open http://localhost:7860. For all three decoding modes, omit `--no-draft`. The operator starts the service; the evaluator interacts through the browser. CPU FP32 uses more model memory and is slower than GPU FP16. The draft adds memory and computation. Do not claim a speculative speedup unless measured.

If remote subfolder loading fails with a newer PEFT version, download the adapter once and pass its local directory:

```bash
hf download AK302/trialgpt-qwen1.5b-lora --include 'lora_r16_bal/epoch3/*' --local-dir artifacts/adapter
python app/app.py --adapter artifacts/adapter/lora_r16_bal/epoch3 --subfolder ''
```

The adapter revision used in the saved greedy results is `bb77ea10574eb0f04c6d720692cebfa5040efebe`. Use `--revision` with that value when downloading to reproduce it. Base-model snapshot currently cached locally: `989aa7980e4cf806f80c7fef2b1adb7bc71aa306`. Network access is needed for uncached assets; authenticate with `hf auth login` if the repository requires access. Once cached, `HF_HUB_OFFLINE=1` permits offline loading. Public unauthenticated adapter availability has not been reverified.

## Experiments and provenance

Use README commands for splitting, fine-tuning, evaluation, and GPU benchmarks. Keep the manifest fixed. Training loads train and validation only. Do not tune on test examples. The current report uses `baseline_{val,test}_greedy` and `final_{val,test}_greedy` as its primary series (repetition penalty 1.0). Older result directories remain for provenance; some lack complete decoding settings. Their existence means a single untouched final test evaluation cannot be asserted.

The app's later review rules are separate from raw model evaluation. They do not modify the saved metrics. Numerical/cache compatibility fixes were tested locally; historical GPU timing logs have not been regenerated. The standalone tiled attention implementation is benchmarked independently and is not installed inside Qwen.

## Build the IEEE paper

Requires a LaTeX installation with pdfLaTeX, TikZ, AMS math, graphics, and booktabs. `report/IEEEtran.cls` is the unmodified IEEEtran 1.8b class downloaded from CTAN; its license is embedded in the file.

```bash
cd report
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

Output: `report/main.pdf`. Upload the whole `report/` directory as a source project if using Overleaf. Author details must be confirmed before final submission. Figures and tables are already included; `report/make_report_assets.py` can regenerate them from saved logs using the project environment.
