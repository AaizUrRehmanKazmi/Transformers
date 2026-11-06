"""Model-free logic of the screening app: input validation, sentence numbering, overall
aggregation rules, HTML result cards and exportable reports (Markdown + HTML)."""
import datetime
import html
import re
from pathlib import Path

from core.schema import number_plain_text, split_note

DISCLAIMER = ("EDUCATIONAL SCREENING PROTOTYPE. This is not a clinical decision tool and not a "
              "clinical-trial enrollment decision. Predictions can be wrong; a qualified clinician "
              "must review every result.")

MIN_NOTE_CHARS, MAX_NOTE_CHARS = 20, 20000
MAX_CRITERIA, MIN_CRIT_CHARS, MAX_CRIT_CHARS = 20, 5, 1000

RULES = (
    "1. Any exclusion criterion labelled 'excluded' -> LIKELY INELIGIBLE.\n"
    "2. Otherwise, any inclusion criterion labelled 'not included' -> LIKELY INELIGIBLE.\n"
    "3. Otherwise, if any criterion is 'not enough information' or its model output could not be "
    "parsed -> UNDETERMINED (information missing, manual review needed).\n"
    "4. Otherwise -> PRELIMINARILY ELIGIBLE (inclusion criteria included or not applicable, no "
    "exclusion criterion met).\n"
    "These rules aggregate criterion-level predictions. They are not a ground-truth label, and "
    "missing evidence is never treated as proof of eligibility or ineligibility."
)

SAMPLES = {
    "Synthetic: chest pain, angina trial": {
        "note": ("A 62-year-old man presents with exertional chest pressure for three months. He has "
                 "type 2 diabetes treated with metformin and a 30 pack-year smoking history. He has no "
                 "history of heart failure. A resting ECG shows no acute changes. His blood pressure is "
                 "148/92 mmHg. He takes aspirin and atorvastatin daily. He is willing to give informed "
                 "consent."),
        "inclusion": "Adults aged 40 years or older\nChronic stable angina\nAble to provide informed consent",
        "exclusion": "History of heart failure\nCurrently pregnant\nPrior coronary artery bypass surgery",
    },
    "Synthetic: sparse note (missing information)": {
        "note": ("A 45-year-old woman is seen for follow-up of her migraine headaches. She reports "
                 "three episodes per month. She takes no regular medication."),
        "inclusion": "Diagnosis of chronic migraine with at least 15 headache days per month\nAge 18 to 65 years",
        "exclusion": "History of liver disease\nUse of opioid analgesics",
    },
}


class InputError(ValueError):
    """Raised with a user-readable message for invalid inputs."""


def number_note(text):
    """Sentence-number a note. A dataset-style note ('0. ...' per line) is kept as is."""
    sents = split_note(text)
    return sents if len(sents) >= 2 else number_plain_text(text)


def parse_criteria(text):
    out = []
    for line in text.splitlines():
        line = re.sub(r"^\s*(?:[-*\u2022]|\d+[.)])\s+", "", line).strip()
        if line:
            out.append(line)
    return out


def validate_inputs(note, incl_text, excl_text):
    note = (note or "").strip()
    if len(note) < MIN_NOTE_CHARS:
        raise InputError(f"Patient note is empty or too short (need at least {MIN_NOTE_CHARS} characters).")
    if len(note) > MAX_NOTE_CHARS:
        raise InputError(f"Patient note is too long ({len(note)} characters; maximum {MAX_NOTE_CHARS}).")
    sentences = number_note(note)
    if not sentences:
        raise InputError("Could not split the patient note into sentences.")
    criteria = ([("inclusion", c) for c in parse_criteria(incl_text or "")]
                + [("exclusion", c) for c in parse_criteria(excl_text or "")])
    if not criteria:
        raise InputError("Enter at least one inclusion or exclusion criterion (one per line).")
    if len(criteria) > MAX_CRITERIA:
        raise InputError(f"Too many criteria ({len(criteria)}; maximum {MAX_CRITERIA}).")
    for ctype, c in criteria:
        if not (MIN_CRIT_CHARS <= len(c) <= MAX_CRIT_CHARS):
            raise InputError(f"Criterion length must be {MIN_CRIT_CHARS}-{MAX_CRIT_CHARS} characters: '{c[:60]}'")
    return sentences, criteria


def aggregate(results):
    """Explicit rule-based overall outcome (see RULES)."""
    excluded = [r for r in results if r["ctype"] == "exclusion" and r["label"] == "excluded"]
    not_incl = [r for r in results if r["ctype"] == "inclusion" and r["label"] == "not included"]
    missing = [r for r in results if not r["valid"] or r["label"] == "not enough information"]
    if excluded:
        return {"status": "LIKELY INELIGIBLE", "reason": f"{len(excluded)} exclusion criterion/criteria predicted as met.",
                "missing": [r["criterion"] for r in missing]}
    if not_incl:
        return {"status": "LIKELY INELIGIBLE", "reason": f"{len(not_incl)} inclusion criterion/criteria predicted as not met.",
                "missing": [r["criterion"] for r in missing]}
    if missing:
        return {"status": "UNDETERMINED", "reason": f"Information is missing or unparsed for {len(missing)} criterion/criteria; manual review needed.",
                "missing": [r["criterion"] for r in missing]}
    return {"status": "PRELIMINARILY ELIGIBLE", "reason": "No exclusion criterion met and every inclusion criterion included or not applicable.",
            "missing": []}


_COLORS = {"included": "#2e7d32", "not excluded": "#2e7d32", "excluded": "#c62828", "not included": "#c62828",
           "not enough information": "#b26a00", "not applicable": "#546e7a"}


def _esc(x):
    return html.escape(str(x), quote=True)


def _badge(label):
    text = label if label else "unparsed output"
    return (f"<span style='background:{_COLORS.get(label, '#6d4c41')};color:#fff;padding:2px 10px;"
            f"border-radius:12px;font-weight:600'>{_esc(text)}</span>")


def render_cards_html(results, sentences, overall):
    cited = {i for r in results for i, _ in r["evidence"]}
    note = "<br>".join(f"<mark>[{i}] {_esc(t)}</mark>" if i in cited else f"[{i}] {_esc(t)}" for i, t in sentences)
    cards = []
    for n, r in enumerate(results, 1):
        ev = "".join(f"<li><b>[{i}]</b> {_esc(t)}</li>" for i, t in r["evidence"]) or "<li><i>No supporting sentence cited.</i></li>"
        extra = "" if r["valid"] else f"<p><b>Parse problem:</b> {_esc(r['error'])}. Raw output: <code>{_esc(r['raw'][:300])}</code></p>"
        trunc = "<p><i>Note was truncated to fit the context window for this criterion.</i></p>" if r.get("truncated") else ""
        cards.append(
            f"<div style='border:1px solid #8886;border-radius:8px;padding:10px 14px;margin:10px 0'>"
            f"<div><b>{n}. {_esc(r['ctype'].capitalize())} criterion:</b> {_esc(r['criterion'])}</div>"
            f"<div style='margin:6px 0'>{_badge(r['label'])}</div>"
            f"<div><b>Supporting evidence</b></div><ul>{ev}</ul>"
            f"<div><b>Explanation:</b> {_esc(r['explanation'])}</div>{extra}{trunc}</div>")
    return (f"<div><h3>Overall (rule-based): {_esc(overall['status'])}</h3><p>{_esc(overall['reason'])}</p>"
            f"{''.join(cards)}<h4>Patient note (cited sentences highlighted)</h4><div>{note}</div></div>")


def _meta_rows(meta):
    return [("Generated (UTC)", meta["timestamp"]), ("Model", meta["model"]), ("Adapter", meta["adapter"]),
            ("Decoding mode", meta["decoding_mode"]), ("Decoding", "greedy, repetition_penalty=1.0"),
            ("Max new tokens", meta["max_new_tokens"]), ("Device / dtype", meta["device"])]


def build_report_markdown(results, sentences, overall, meta):
    cell = lambda s: str(s).replace("|", "\\|").replace("\n", " ")  # noqa: E731
    lines = [f"# Eligibility screening report", "", f"> **{DISCLAIMER}**", "", "## Provenance", "",
             "| Item | Value |", "|---|---|"]
    lines += [f"| {k} | {cell(v)} |" for k, v in _meta_rows(meta)]
    lines += ["", f"## Overall (rule-based): {overall['status']}", "", overall["reason"], ""]
    if overall["missing"]:
        lines += ["Criteria with missing information:"] + [f"- {c}" for c in overall["missing"]] + [""]
    lines += ["Aggregation rules:", "", "```", RULES, "```", "", "## Criterion-level results", "",
              "| # | Type | Criterion | Predicted label | Cited sentence ids | Evidence text | Explanation |",
              "|---|---|---|---|---|---|---|"]
    for n, r in enumerate(results, 1):
        ids = ", ".join(str(i) for i, _ in r["evidence"]) or "-"
        txt = " / ".join(f"[{i}] {t}" for i, t in r["evidence"]) or "-"
        lines.append(f"| {n} | {r['ctype']} | {cell(r['criterion'])} | {r['label'] or 'unparsed'} | {ids} | {cell(txt)} | {cell(r['explanation'])} |")
    lines += ["", "## Patient note (sentence ids as used by the model)", ""] + [f"[{i}] {t}" for i, t in sentences]
    return "\n".join(lines) + "\n"


def build_report_html(results, sentences, overall, meta):
    rows = "".join(f"<tr><td>{_esc(k)}</td><td>{_esc(v)}</td></tr>" for k, v in _meta_rows(meta))
    return ("<!doctype html><html><head><meta charset='utf-8'><title>Eligibility screening report</title>"
            "<style>body{font-family:sans-serif;max-width:900px;margin:2em auto;padding:0 1em}"
            "td{padding:2px 12px 2px 0;vertical-align:top}.warn{border:2px solid #c62828;padding:8px 12px}</style></head><body>"
            f"<h1>Eligibility screening report</h1><p class='warn'><b>{_esc(DISCLAIMER)}</b></p>"
            f"<h2>Provenance</h2><table>{rows}</table>"
            f"{render_cards_html(results, sentences, overall)}"
            f"<h2>Aggregation rules</h2><pre>{_esc(RULES)}</pre></body></html>")


def save_report(outdir, results, sentences, overall, meta):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    md, ht = outdir / f"screening_report_{stamp}.md", outdir / f"screening_report_{stamp}.html"
    md.write_text(build_report_markdown(results, sentences, overall, meta), encoding="utf-8")
    ht.write_text(build_report_html(results, sentences, overall, meta), encoding="utf-8")
    return str(md), str(ht)
