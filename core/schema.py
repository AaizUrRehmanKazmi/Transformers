"""Label sets, note/evidence parsing, answer format and strict output parser.

Single source of truth used by training, evaluation and the app.
"""
import ast
import json
import re
from dataclasses import dataclass, field
from typing import List, Optional, Sequence, Tuple

INCLUSION_LABELS = ("included", "not included", "not enough information", "not applicable")
EXCLUSION_LABELS = ("excluded", "not excluded", "not enough information", "not applicable")
LABELS_BY_TYPE = {"inclusion": INCLUSION_LABELS, "exclusion": EXCLUSION_LABELS}
ALL_LABELS = tuple(dict.fromkeys(INCLUSION_LABELS + EXCLUSION_LABELS))

_NOTE_LINE = re.compile(r"^\s*(\d+)\.\s?(.*)$")


def split_note(note: str) -> List[Tuple[int, str]]:
    """Parse a dataset note ('0. text' per line) into [(sentence_id, text)]."""
    sents: List[List] = []
    for line in note.splitlines():
        m = _NOTE_LINE.match(line)
        if m and int(m.group(1)) == len(sents):
            sents.append([len(sents), m.group(2).strip()])
        elif sents and line.strip():  # continuation of previous sentence
            sents[-1][1] += " " + line.strip()
    return [(i, t) for i, t in sents]


def number_plain_text(text: str) -> List[Tuple[int, str]]:
    """For the app: split an un-numbered clinical note into numbered sentences."""
    parts = [p.strip() for p in re.split(r"(?<=[.!?])\s+|\n+", text) if p.strip()]
    return list(enumerate(parts))


def parse_gold(value) -> List[int]:
    """expert_sentences is stored as a string such as '[0, 1, 2]' (or '[]')."""
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return sorted({int(v) for v in value})
    s = str(value).strip()
    if not s:
        return []
    try:
        out = json.loads(s)
    except json.JSONDecodeError:
        out = ast.literal_eval(s)
    return sorted({int(v) for v in out})


def format_answer(label: str, evidence: Sequence[int]) -> str:
    """Training target / expected model output (compact JSON)."""
    return json.dumps({"label": label, "evidence": [int(e) for e in evidence]})


@dataclass
class ParsedOutput:
    valid: bool
    label: Optional[str] = None
    evidence: List[int] = field(default_factory=list)
    error: Optional[str] = None


def parse_output(text: str, criterion_type: str, n_sentences: Optional[int] = None) -> ParsedOutput:
    """Strict parser. Malformed JSON, a label not valid for the criterion type, or
    out-of-range sentence ids are all reported as invalid (counted as errors)."""
    start = text.find("{")
    if start < 0:
        return ParsedOutput(False, error="no_json")
    try:
        obj, _ = json.JSONDecoder().raw_decode(text[start:])
    except json.JSONDecodeError:
        return ParsedOutput(False, error="malformed_json")
    if not isinstance(obj, dict) or "label" not in obj:
        return ParsedOutput(False, error="missing_label")
    label = str(obj["label"]).strip().lower()
    if label not in LABELS_BY_TYPE[criterion_type]:
        return ParsedOutput(False, label=label, error="label_not_valid_for_type")
    ev = obj.get("evidence", [])
    if not isinstance(ev, list) or not all(isinstance(e, int) and not isinstance(e, bool) for e in ev):
        return ParsedOutput(False, label=label, error="bad_evidence")
    if n_sentences is not None and any(e < 0 or e >= n_sentences for e in ev):
        return ParsedOutput(False, label=label, error="evidence_out_of_range")
    return ParsedOutput(True, label=label, evidence=sorted(set(ev)))


def render_explanation(label: str, evidence: Sequence[int], sentences: Sequence[Tuple[int, str]]) -> str:
    """Deterministic, grounded explanation built only from the cited sentences."""
    by_id = dict(sentences)
    cited = [(i, by_id[i]) for i in evidence if i in by_id]
    if not cited:
        return (f"Label '{label}': the model cited no supporting sentence. Absence of evidence "
                "is not treated as proof of eligibility or ineligibility.")
    quoted = " ".join(f"[{i}] {t}" for i, t in cited)
    return f"Label '{label}', based on patient sentences: {quoted}"
