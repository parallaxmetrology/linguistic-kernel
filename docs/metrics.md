# Metrics (kernel `lang-kernel-rebuild-v19`)

Every number is a count or ratio over the text itself: words, sentences, paragraphs, bullets, punctuation, and fixed word lists. No model, no embedding, no randomness. The `evidence` block in `measure_full` exposes the counts behind each coordinate.

Tokenization: lowercase words (`\w+`); sentences split where terminal punctuation is followed by a space and a capital or digit, with common abbreviations protected, and each bullet line kept as its own unit; paragraphs on blank lines. Word lists (stopwords, common words, transitions, reference pronouns, subordinators, metaphor patterns) are English.

## Core kernel K = [Δx, rᵥ, ρᵣ, μ]

| key | name | how it's computed | reading |
|---|---|---|---|
| `delta_x` | weight shift | each sentence weighted by its share of content words (non-stopwords, ≥ 4 letters); centroid of those weights along sentence order, minus 0.5 | − front-loaded, + back-loaded, 0 balanced (or one sentence) |
| `r_v` | void ratio | 0.30·paragraph rate + 0.25·bullet rate + 0.25·share of short sentences (≤ 10 words) + 0.20·inverse average sentence length, each normalized and capped | breathing room from formatting and rhythm; high = airy, low = dense |
| `rho_r` | packing density | content words ÷ all words | high = content-heavy; low = connective-heavy |
| `mu` | cohesion | sigmoid of (8 × transition-word rate + 4 × reference-pronoun rate) | discourse scaffolding; in practice it mostly follows pronoun rate (see [evidence](evidence.md)) |

## Auxiliary

| key | name | how it's computed | reading |
|---|---|---|---|
| `delta_y` | segmentation strain | (average sentence length − 15) ÷ 15 | + long, run-on sentences; − short, fragmented ones. The Δy name is historical: nothing vertical |
| `x_p` | peripheral pull | sigmoid of (3.5 × rare-word ratio + 0.15 × metaphor rate) | reaching for rare vocabulary and figurative language |
| `theta` | flow instability | 1 − mean cosine similarity of adjacent sentences' word counts | jumps between sentences vs smooth continuation |
| `d_s` | structural thickness | (commas + 1.5 × semicolons/colons + subordinators) per token, normalized and capped | clause stacking; mostly comma density in practice |

## Labels

- `basin`: a coarse location from Δx and rᵥ: `B0_centered_compact`, `B1_right_bias_compact`, `B2_left_bias_compact`, `B3_high_void_or_high_displacement` (z-space versions `ZB0`–`ZB3` when a family baseline is used). A place, not a grade.
- `rhetorical_state`: one of `revising`, `formatting_collapse` (severe / partial / math tiers), `complying_under_constraint`, `dialectic` or `assertive`, routed over the evidence in roughly that order. See [evidence](evidence.md) for how the collapse tiers were calibrated.
- `collapse_subtype`: `severe` (≤ 15 tokens, short and airy), `partial` (16–40 tokens with an incomplete tail), `math` (math or code with an unclosed tail), or `none`.
- `tail_incomplete_flag`: ends mid-structure (open bracket, dangling operator or conjunction…).
- `segmentation_reliable`: False when sentence splitting is degenerate (one giant run-on, repetition loops). Treat sentence-derived axes as low confidence.

## Baselines and envelopes

- `LinguisticKernel` can z-score against a **prompt-family baseline** (`fit` in the original CLI; registries of family means and standard deviations).
- `lingkernel.fit_envelope` fits a z-space centroid and 95th-percentile radius (`r95`) on *your own* normal outputs. `check` gives each new output a distance and a band: **stable** (≤ 0.75·r95), **elevated** (≤ 1.0·r95), **excursion** (beyond). These bands are v19's; they are working heuristics, not validated cutoffs.
- `hysteresis(stress, recovery, env)`: distance between the stress and recovery centroids. Did the model return to where it started?

## Not measured

Correctness, factuality, safety, helpfulness, persuasiveness, intent, or model internals. Two equally correct answers can sit far apart, deliberately.
