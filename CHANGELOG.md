# Changelog

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
