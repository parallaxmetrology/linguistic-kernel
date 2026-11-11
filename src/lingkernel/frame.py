"""
Reading frame: a preparation layer for reading chat-style text with the frozen v19 kernel.

v19 was built for plain prose. On chat and benchmark answers it misreads a few things:
markdown (code blocks, tables, header and bold-only title lines are read as long run-on
sentences), short complete answers (read as "severe collapse"), and literal special
tokens such as <|endoftext|> (v19's token count raises an error). The frame handles these
without changing a single kernel number:

    import lingkernel
    r = lingkernel.read("## Plan\\nThe survey ran for two years. Results were mixed.")
    r["eligible"], r["framed"]["delta_y"], r["raw"]["delta_y"], r["collapse_reading"]

Every text is measured twice: `raw` (exactly as given) and `framed` (markdown neutralised).
Plain text with no markdown comes back byte-identical, so its two readings are identical.

What the frame changes, and nothing else:
  1. Fenced code blocks (``` or ~~~) are removed.
  2. Table rows and separator lines are removed.
  3. Header lines (# Title) and bold-only lines (**Title:**) are removed, leaving a
     paragraph break where markdown renders one.
  4. Markdown links keep their text and drop the URL.

Fields it adds:
  eligible          English (by script and function-word share) and at least
                    MIN_PROSE_TOKENS word tokens after framing, and v19 could read it
  reasons           why not eligible: no_letters, non_latin_script,
                    low_english_function_words, short_prose, kernel_error
  collapse_reading  v19's collapse_subtype restated for chat corpora:
                      severe + tail signal + open ending -> short_cut
                      severe otherwise                   -> short_complete
                      partial -> cut_partial;  math -> cut_code_or_math;  none -> none
                    (always from the raw reading: removing code would hide a cut-off answer)

This is reading frame r1.1, the version used in "Structure Beyond Length"
(https://github.com/parallaxmetrology/structure-beyond-length).
"""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

from .kernel import KERNEL_KEYS, flatten, measure_full

FRAME_VERSION = "reading-frame-r1.1"
MIN_PROSE_TOKENS = 40
MIN_ASCII_LETTER_SHARE = 0.95
MIN_FUNCTION_WORD_SHARE = 0.12
FUNCTION_WORD_CHECK_MIN_TOKENS = 20

_WORD_RE = re.compile(r"[A-Za-z0-9]+(?:'[A-Za-z0-9]+)?")  # same word pattern as v19
_FENCE_RE = re.compile(r"^\s{0,3}(```|~~~)")
_HEADER_RE = re.compile(r"^\s{0,3}#{1,6}\s+(.*?)\s*#*\s*$")
_BOLD_LINE_RE = re.compile(r"^\s*(\*\*|__)([^*_].*?)\1\s*:?\s*$")
_TABLE_ROW_RE = re.compile(r"^\s*\|.*\|\s*$")
_TABLE_SEP_RE = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$")
_LINK_RE = re.compile(r"\[([^\]\n]+)\]\(([^)\s]+)\)")
_CLOSED_END_RE = re.compile(r"[.!?。！？…][\"'”’)\]*_]*\s*$")

_FUNCTION_WORDS = frozenset("""
a an the and or but if then so of to in on at by for with from as is are was were be been being
it its this that these those there here i you he she we they me him her us them my your our their
not no do does did have has had will would can could should may might must which who what when
where how why than also just only about into over after before because while all any each some
""".split())


@dataclass
class FrameEdits:
    code_blocks: int = 0
    code_lines: int = 0
    unclosed_fence: bool = False
    table_lines: int = 0
    headers: int = 0
    bold_lines: int = 0
    links: int = 0

    @property
    def any(self) -> bool:
        return bool(self.code_blocks or self.table_lines or self.headers or self.bold_lines or self.links)


@dataclass
class Framed:
    text: str
    edits: FrameEdits
    identical: bool
    prose_tokens: int
    ascii_letter_share: float
    function_word_share: float
    english: bool
    eligible: bool
    reasons: List[str] = field(default_factory=list)


def frame_text(text: str) -> Framed:
    """Neutralise the markdown patterns v19 misreads and check eligibility. No kernel call."""
    edits = FrameEdits()
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    out: List[str] = []
    in_fence, fence_mark = False, ""
    for ln in lines:
        m = _FENCE_RE.match(ln)
        if in_fence:
            edits.code_lines += 1
            if m and m.group(1) == fence_mark:
                in_fence = False
                out.append("")
            continue
        if m:
            in_fence, fence_mark = True, m.group(1)
            edits.code_blocks += 1
            edits.code_lines += 1
            out.append("")
            continue
        if _TABLE_SEP_RE.match(ln) or _TABLE_ROW_RE.match(ln):
            edits.table_lines += 1
            out.append("")
            continue
        if _HEADER_RE.match(ln):
            edits.headers += 1
            out.append("")
            continue
        if _BOLD_LINE_RE.match(ln):
            edits.bold_lines += 1
            out.append("")
            continue
        new_ln, n_links = _LINK_RE.subn(r"\1", ln)
        edits.links += n_links
        out.append(new_ln)
    edits.unclosed_fence = in_fence

    if edits.any:
        framed = re.sub(r"\n[ \t]*(\n[ \t]*)+\n", "\n\n", "\n".join(out)).strip()
    else:
        framed = text

    tokens = _WORD_RE.findall(framed.lower())
    letters = [c for c in framed if c.isalpha()]
    ascii_share = (sum(1 for c in letters if c.isascii()) / len(letters)) if letters else 0.0
    fw_share = (sum(1 for t in tokens if t in _FUNCTION_WORDS) / len(tokens)) if tokens else 0.0
    reasons: List[str] = []
    if not letters:
        reasons.append("no_letters")
    elif ascii_share < MIN_ASCII_LETTER_SHARE:
        reasons.append("non_latin_script")
    elif len(tokens) >= FUNCTION_WORD_CHECK_MIN_TOKENS and fw_share < MIN_FUNCTION_WORD_SHARE:
        reasons.append("low_english_function_words")
    english = not reasons
    if len(tokens) < MIN_PROSE_TOKENS:
        reasons.append("short_prose")
    return Framed(text=framed, edits=edits, identical=(framed == text), prose_tokens=len(tokens),
                  ascii_letter_share=round(ascii_share, 4), function_word_share=round(fw_share, 4),
                  english=english, eligible=not reasons, reasons=reasons)


def ends_closed(text: str) -> bool:
    """True when the text ends in sentence-closing punctuation (optionally followed by quotes or brackets)."""
    return bool(_CLOSED_END_RE.search(text or ""))


def collapse_reading(row: Dict[str, Any], text: str = "") -> str:
    """v19's collapse_subtype restated for chat corpora. v19's tail signal also fires on a final
    scaffold word ("...help with that."), so a short text ending in closing punctuation reads as complete."""
    sub = row.get("collapse_subtype", "none")
    if sub == "severe":
        return "short_cut" if (row.get("tail_incomplete_flag") and not ends_closed(text)) else "short_complete"
    return {"partial": "cut_partial", "math": "cut_code_or_math"}.get(sub, "none")


def _measure(text: str) -> tuple:
    if not text or not text.strip():
        return None, None
    try:
        return flatten(measure_full(text, include_detail=False)), None
    except Exception as ex:  # v19 raises on some inputs, e.g. a literal "<|endoftext|>"
        return None, f"{type(ex).__name__}: {str(ex)[:120]}"


def read(text: str) -> Dict[str, Any]:
    """Read one text raw and framed. Returns eligibility, edits, collapse_reading, both readings and their delta."""
    text = text if isinstance(text, str) else ""
    f = frame_text(text)
    raw, err = _measure(text)
    framed, err2 = (raw, err) if f.identical else _measure(f.text)
    kernel_error = err or err2
    reasons = list(f.reasons) + (["kernel_error"] if kernel_error else [])
    delta: Optional[Dict[str, float]] = None
    if raw and framed:
        delta = {k: framed[k] - raw[k] for k in KERNEL_KEYS if raw.get(k) is not None and framed.get(k) is not None}
    return {"frame_version": FRAME_VERSION, "eligible": f.eligible and not kernel_error, "reasons": reasons,
            "english": f.english, "prose_tokens": f.prose_tokens, "framed_identical": f.identical,
            "edits": asdict(f.edits), "collapse_reading": collapse_reading(raw, text) if raw else "empty",
            "ends_closed": ends_closed(text), "kernel_error": kernel_error,
            "raw": raw, "framed": framed, "delta": delta}


def read_row(text: str) -> Dict[str, Any]:
    """`read` as one flat row (raw_*, framed_*, edit_* columns), for a DataFrame or CSV."""
    r = read(text)
    row = {k: r[k] for k in ("frame_version", "eligible", "english", "prose_tokens", "framed_identical",
                             "collapse_reading", "ends_closed", "kernel_error")}
    row["reasons"] = ";".join(r["reasons"])
    row.update({f"edit_{k}": v for k, v in r["edits"].items()})
    for side in ("raw", "framed"):
        for k, v in (r[side] or {}).items():
            row[f"{side}_{k}"] = v
    return row
