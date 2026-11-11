# Changelog

## 0.2.0 — 2026-11-11

- `lingkernel.read` / `read_row` / `frame_text`: the reading frame (r1.1) for chat-style text. Measures every text raw and with markdown neutralised (code blocks, tables, header and bold-only title lines, link URLs), adds English/length eligibility, restates v19's collapse tiers for chat corpora, and catches texts v19 cannot read. No kernel number changes; plain text reads identically. See docs/reading-frame.md.
- docs/evidence.md: four more known sharp edges (markdown, θ = 0, the tail check on complete sentences, literal special tokens).
- Evidence from "Structure Beyond Length", which used this frame on four public preference corpora.

## 0.1.0 — 2026-10-21

First release as a package, wrapping the frozen kernel v19 (`lang-kernel-rebuild-v19`).

- `lingkernel.measure` / `measure_full`: eight coordinates, basin, rhetorical state, collapse tiers, evidence
- `measure_many`: .jsonl / .json / .csv / .txt inputs and folders
- `fingerprint`, `compare`, `rigidity`; `fit_envelope`, `check`, `hysteresis` (v19's envelope formulas)
- `lk` command line
- Golden tests against the original file; all 1,200 published EMS readings reproduce exactly
- Data: EMS prompts and answers (3 engines × 400) with confirmed-truncation labels; Gemini operating-window readings
- Guess the Engine browser game

Differences from the original file: citation markers removed from the docstring; the trailing add-on section (envelope helpers, now in `corpus.py`, and two text proxies) left out; the tokenizer vocabulary isn't bundled (tiktoken is an optional dependency).
