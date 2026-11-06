"""Hand-written probe cases run through the SAME Engine as the web app (no browser needed).

    python eval/probe_cases.py            # fine-tuned model + adapter, exactly as in the app
    python eval/probe_cases.py --base     # base model without the adapter, for comparison

Prints raw model output, parsed label and cited evidence per case and writes
eval/results/probe_finetuned.json (or probe_base.json). If --base and the default run give identical
outputs for every case, the adapter is not taking effect, which would be an app/loading bug.
"""
import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.app import Engine  # noqa: E402
from app.screening import number_note  # noqa: E402
from core.model_loader import ADAPTER_REPO, ADAPTER_SUBFOLDER  # noqa: E402
from core.schema import parse_output  # noqa: E402

CASES = [  # (note, criterion type, criterion, expected label)
    ("A 15 years old male with no pain", "inclusion", "At least 40 years old", "not included"),
    ("A 15 years old male with no pain", "inclusion", "18 to 60 years", "not included"),
    ("A 52-year-old man with type 2 diabetes.", "inclusion", "Age between 40 and 65 years", "included"),
    ("A 70-year-old woman presents with knee pain.", "inclusion", "Adults aged 18 to 60 years", "not included"),
    ("A 34-year-old woman is seen for follow-up of mild asthma.", "inclusion", "Age 18 years or older", "included"),
    ("A 15-year-old boy presents with a sore throat for two days. He has no known medical conditions.",
     "inclusion", "Patients must be at least 18 years old.", "not included"),
    ("A 15 years old male with no pain", "exclusion", "Prior history of cardiovascular disease",
     "not enough information"),
    ("A 60-year-old man has a history of myocardial infarction.", "exclusion",
     "Prior history of cardiovascular disease", "excluded"),
    ("A 45-year-old male with hypertension.", "exclusion", "Currently pregnant", "not applicable"),
    ("A 45-year-old man with hypertension, no medication.", "inclusion", "Diagnosis of hypertension", "included"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", action="store_true", help="no adapter (zero-shot base model)")
    args = ap.parse_args()
    eng = Engine(None if args.base else ADAPTER_REPO, None if args.base else ADAPTER_SUBFOLDER, None, False)
    print(f"\nmodel: {'BASE (no adapter)' if args.base else 'fine-tuned'}  device: {eng.device}/{eng.dtype}\n")

    out, right = [], 0
    for note, ctype, crit, expected in CASES:
        sents = number_note(note)
        ids, kept, _ = eng.encode(sents, ctype, crit, 64)
        t0 = time.perf_counter()
        toks, _ = eng.generate(ids, "cached", 64)
        raw = eng.tok.decode(toks[0], skip_special_tokens=True)
        p = parse_output(raw, ctype, kept[-1][0] + 1)
        label = p.label if p.valid else "INVALID"
        ok = label == expected
        right += ok
        print(f"[{'OK ' if ok else 'BAD'}] {ctype}: {crit}\n      note: {note}\n"
              f"      expected: {expected} | predicted: {label} | evidence: {p.evidence} | {time.perf_counter() - t0:.1f}s\n"
              f"      raw: {raw.strip()}\n")
        out.append({"note": note, "type": ctype, "criterion": crit, "expected": expected,
                    "predicted": label, "evidence": p.evidence, "raw": raw.strip()})
    print(f"correct: {right}/{len(CASES)}")
    dest = ROOT / "eval" / "results" / f"probe_{'base' if args.base else 'finetuned'}.json"
    dest.write_text(json.dumps(out, indent=2))
    print("wrote", dest)


if __name__ == "__main__":
    main()
