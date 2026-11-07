# Six-minute application demonstration

Record your own narration and browser interaction. The following is a script, not a completed video. Start the app and load both models before recording; verify speculative generation works with the current source. Use synthetic records only. On CPU, shorten benchmark output and transparently label any edited waiting time.

| Time | Action and explanation |
|---|---|
| 0:00–0:35 | Introduce the educational task, Qwen target, LoRA adapter, and explicit non-clinical disclaimer. Explain one criterion plus sentence evidence. |
| 0:35–1:35 | Enter the positive case below. Run cached screening, inspect the exact cited sentences, and explain the aggregate rules. |
| 1:35–2:30 | Change age 55 to 20. Show the age correction, original model label, and likely-ineligible outcome. Remove surgery history and show unknown information. Report actual output honestly if the model errs. |
| 2:30–3:05 | Submit an empty note to demonstrate validation, restore input, and export/open the HTML or Markdown report with provenance. |
| 3:05–4:15 | Open the live decoding benchmark, choose a small output budget, and compare uncached/cached/speculative outputs and timing. Explain draft acceptance and why slowdown is allowed. |
| 4:15–4:50 | Run the attention comparison with a small sequence. Explain tiling, running maximum/normalizer, and memory versus speed. |
| 4:50–5:35 | Show paper results: 70.4% raw-model test accuracy, 60.3% present-class macro-F1, 50.0% evidence micro-F1, eight test patients. Distinguish application rules from measured model metrics. |
| 5:35–6:00 | Show repository, weights and report links. Explain limitations and AI assistance. Finish with the clinical disclaimer. |

## Copyable synthetic case

Patient:
```
A 55-year-old man attends a routine appointment. He has never undergone coronary artery bypass surgery.
```
Inclusion:
```
Adults aged 40 years or older
```
Exclusion:
```
Prior coronary artery bypass surgery
```
Expected: included [0], not excluded [1], preliminarily eligible. At age 20, expected age label is not included. If surgery information is deleted, expected surgery label is not enough information; the model can still fail when it attaches irrelevant evidence.

## Defense preparation

- Explain why patient grouping prevents patient leakage but does not remove all domain similarity.
- Explain answer-only loss and why LoRA reduces trainable state without eliminating base weights.
- Derive 28,672 FP16 KV bytes/token for the target and explain the final token not entering the cache.
- Explain bottom-right causal alignment when query length differs from key length.
- Derive online-softmax rescaling after the running maximum changes.
- Walk through a speculative round with two accepted proposals and one rejection; explain both caches.
- Explain why empty evidence is not proof and why no test excluded examples limits interpretation.
- Explain the current library compatibility fix and the float64 numerical oracle.
- Acknowledge earlier test runs and that postprocessing was added later.
