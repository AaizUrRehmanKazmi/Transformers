"""Patient-grouped 37/8/8 split of ncbi/TrialGPT-Criterion-Annotations (seed 42).

Usage:
    python data/prepare_split.py            # downloads dataset, writes manifest
    python data/prepare_split.py --inspect  # just print columns/label values

The dataset schema is detected, not assumed: run --inspect first and, if the
auto-detected column names are wrong, override them in COLUMN_OVERRIDES below.
"""
import argparse
import json
from pathlib import Path

import numpy as np
from datasets import load_dataset

DATASET = "ncbi/TrialGPT-Criterion-Annotations"
OUT = Path(__file__).parent / "split_manifest.json"

# Fill these in after --inspect if auto-detection guesses wrong.
COLUMN_OVERRIDES = {"patient_id": None}

# Columns that hold previous GPT-4 outputs. They must NEVER reach a prompt.
LEAKY_HINTS = ("gpt", "gpt4", "gpt-4", "pred", "explanation")


def load_all():
    ds = load_dataset(DATASET)
    # Merge whatever splits the hub provides into one table; we re-split ourselves.
    return [row for split in ds.values() for row in split]


def detect_patient_col(rows):
    if COLUMN_OVERRIDES["patient_id"]:
        return COLUMN_OVERRIDES["patient_id"]
    for c in rows[0].keys():
        if "patient" in c.lower() and "id" in c.lower():
            return c
    raise SystemExit(f"Could not detect patient id column in {list(rows[0].keys())}. "
                     "Set COLUMN_OVERRIDES['patient_id'].")


def make_split(patient_ids):
    ids = sorted(set(map(str, patient_ids)))
    assert len(ids) == 53, f"expected 53 unique patients, got {len(ids)}"
    rng = np.random.default_rng(42)
    ids = list(rng.permutation(ids))  # shuffle of the sorted list
    return {"train": ids[:37], "val": ids[37:45], "test": ids[45:]}


def check_no_leakage(split):
    sets = {k: set(v) for k, v in split.items()}
    assert not (sets["train"] & sets["val"])
    assert not (sets["train"] & sets["test"])
    assert not (sets["val"] & sets["test"])
    assert [len(split[k]) for k in ("train", "val", "test")] == [37, 8, 8]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inspect", action="store_true")
    args = ap.parse_args()

    rows = load_all()
    print(f"rows: {len(rows)}")
    print("columns:", list(rows[0].keys()))
    leaky = [c for c in rows[0] if any(h in c.lower() for h in LEAKY_HINTS)]
    print("columns that look like GPT-4 outputs (excluded from prompts):", leaky)
    pcol = detect_patient_col(rows)
    for c in rows[0]:
        vals = {str(r[c]) for r in rows}
        if len(vals) <= 12:
            print(f"  low-cardinality column {c!r}: {sorted(vals)}")
    if args.inspect:
        return

    split = make_split([r[pcol] for r in rows])
    check_no_leakage(split)
    where = {pid: s for s, ids in split.items() for pid in ids}
    counts = {s: 0 for s in split}
    for r in rows:
        counts[where[str(r[pcol])]] += 1

    manifest = {
        "dataset": DATASET, "seed": 42, "patient_column": pcol,
        "excluded_columns": leaky,
        "patients": split,
        "num_patients": {k: len(v) for k, v in split.items()},
        "num_annotation_rows": counts,
    }
    OUT.write_text(json.dumps(manifest, indent=2))
    print("wrote", OUT, manifest["num_patients"], counts)


if __name__ == "__main__":
    main()
