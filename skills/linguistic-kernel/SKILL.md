---
name: linguistic-kernel
description: Measure the structure of text (especially LLM outputs) with the deterministic Linguistic Kernel: weight shift, void, packing, cohesion, sentence length, rare-word pull, flow, clause thickness, plus collapse and truncation flags. Use when someone wants to compare how two models or prompts write, check outputs for truncation or structural breakage, track drift against a baseline, or get countable evidence about an answer's form without an LLM judge.
---

# Linguistic Kernel

Counts over the text itself: no model, no judge, same text and same numbers. It measures *how* something is written, never whether it's correct, safe or good.

## Setup

```bash
pip install "linguistic-kernel[tokens] @ git+https://github.com/parallaxmetrology/linguistic-kernel"
```

## Measure

| task | command |
|---|---|
| one text | `lk measure "text"` or `lk measure --file answer.txt` (add `--full` for evidence) |
| many | `lk measure outputs.jsonl -o readings.csv` (.jsonl/.json/.csv/.txt, folders) |
| per-model windows | `lk fingerprint readings.csv --by engine` |
| two sets | `lk compare a.csv b.csv --labels A B` |
| drift | `lk envelope fit normal.csv -o env.json`, then `lk envelope check env.json new.csv` |

## Read

1. **State first.** `rhetorical_state = formatting_collapse` with `collapse_subtype` severe/partial/math suggests truncation or breakage. Check the text: short, complete answers ("Yes.") also trip it. `segmentation_reliable = False` means the sentence-based axes are low confidence.
2. **Length always.** Report `token_count`. Many axes move with length, so compare like with like.
3. **Axes as descriptions:** Δx front/back-loaded · rᵥ breathing room · ρᵣ content-heavy vs connective · μ scaffolding (mostly pronouns) · Δy long vs short sentences · xₚ rare words and metaphor · θ jumps between sentences · dₛ clause stacking (mostly commas).
4. **Sets, not single texts,** for any claim about a model's habits: use fingerprint windows and compare, with group sizes.

## Boundaries

- Never infer correctness, truthfulness, safety, quality or intent from these numbers.
- Collapse detection was calibrated on the EMS corpora; on new models, treat flags as candidates to check.
- Open questions (see docs/evidence.md in the repo): which axis carries the most movement, μ as a control, kernel distance vs word count as an anomaly score. Don't present these as settled.
- Word lists are English.
