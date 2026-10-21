# Lineage

`src/lingkernel/_v19.py` is **Linguistic Kernel v19** (`lang-kernel-rebuild-v19`), the frozen version behind the published studies. Two changes were made to the file, and neither touches any computation:

1. ChatGPT citation markers (`:contentReference[oaicite:N]{index=N}`, 14 of them) were removed from the module docstring.
2. The trailing "v4 additions" section was left out. It held the envelope helpers, which are reimplemented in `lingkernel/corpus.py` with v19's formulas, and two text proxies (a "logical integrity score" and a "hallucination gradient" proxy). The proxies count reversal words, numbers and capitalized words, and their names promise more than those counts can carry. They may return later under plainer names.

Checks: `tests/test_golden.py` compares the package with the original file on 28 texts (all fields, to 1e-12), and the package reproduces all 1,200 published EMS readings (`fingerprints/ems_3engines_1200.csv`) exactly. `tools/golden_from_original.py` regenerates the goldens from any copy of the original.

The original also shipped a copy of the `cl100k_base` tokenizer vocabulary (the file named `9b5ad71b2c…`, tiktoken's cache name for it). The package depends on `tiktoken` instead (optional; only `tiktoken_token_count` uses it).

## Version history (from the v19 changelog)

- **v16–v17:** `x_p` redesigned as a domain-agnostic rarity measure; `d_s` weights semicolons and colons 1.5×.
- **v18:** `formatting_collapse` state for very short truncations; token counts via tiktoken.
- **v19:** collapse split into three tiers (severe, partial, math), with `tail_incomplete_flag` and `collapse_subtype` in evidence.

Earlier readings (v13 and before) used a different `x_p` and aren't comparable.

## Not in this repository

- **Parallax Telemetry**, the scoring, comparison and monitoring service built on this kernel.
- **RTP / adaptive controller**, the reasoning-topology probe and intervention layer.
- **Conversational Integrity Monitor**, an agent skill for drift across long conversations (planned, once tested).
