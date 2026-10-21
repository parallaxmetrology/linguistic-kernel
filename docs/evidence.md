# What the data supports so far, and what's open

The kernel has been run on three corpora: **EMS** (Claude, GPT and Gemini on the same 400 everyday, science and math prompts under a batch constraint; 1,200 responses, in [`fingerprints/`](../fingerprints/)), a **Gemini operating-window** set (1,600 responses across baseline, temperature, context, template and stress conditions), and a **structural residue** set (60 responses with token log-probabilities). This page separates findings the data supports from questions that are still open. Open doesn't mean wrong: it means not yet established, untested at scale, or likely to need adjusting.

## Supported so far

- **The kernel reproduces.** Same text, same numbers, on any machine (pure Python counting). The package reproduces all 1,200 published EMS readings to within 1e-16, with identical states and collapse labels.
- **Engines write differently, starting with length.** Under the same prompts, Claude's median answer is about 86 tokens, GPT's 39 and Gemini's 41. Many structural differences travel with length, so compare at similar lengths or report length alongside.
- **Truncation is engine-specific.** Human-confirmed truncations: Gemini 20, GPT 15, Claude 1 of 400 each. The same ten prompts truncate in both Gemini and GPT.
- **The collapse detector finds them on its home corpus.** On EMS, `formatting_collapse` flags 38 responses: all 36 confirmed truncations plus 2 complete Gemini answers. A length-only rule does far worse (best case: 12 of 36 with no false alarms). The detector's thresholds were calibrated on these same corpora, so this is in-sample performance.
- **Clause stacking tracks generation-level uncertainty.** In the residue set, `d_s` correlates with a log-probability instability score (r = 0.46; r = 0.36, p = 0.005 after controlling for length and prompt family, n = 60). `d_s` is mostly comma density (r = 0.76), which is a plain, checkable story.
- **`x_p` separates prompt types** in the operating-window set (η² = 0.18 by prompt type).
- **`mu` responds to conditions** in the operating-window set (η² = 0.14), and shows no engine difference in EMS (η² ≈ 0).

## Open: not yet established, may need adjusting

- **Out-of-sample collapse detection.** The detector hasn't been tested on a corpus it wasn't calibrated on. Fresh labeled truncations from other models are the most useful contribution anyone could make.
- **Kernel distance as a general anomaly score.** In one test, an unweighted distance from a prompt's own norm didn't beat word count at spotting truncations (AUC 0.75 vs 0.89) or prompt echoes (0.42). The kernel does carry directional signatures (echoed prompts push μ up). A weighted or learned combination may do better; untested.
- **Which axis carries the movement.** Earlier work read Δy as carrying most of the variation across conditions. That share depends heavily on how axes are scaled (raw vs standardized vs robust), so it's open which axis dominates.
- **Δy and steerability.** "High-Δy prompts are more steerable" is driven by two constraint-stacked prompts in the data. Untested beyond them.
- **`mu` as a stability control.** μ's narrow range comes partly from its sigmoid. In practice it follows reference-pronoun rate, because the transition list rarely fires. Its role as a cohesion measure may need adjusting.
- **`r_v` and instability.** An association seen in raw data isn't yet established once length and prompt family are controlled.
- **Envelope bands.** The 0.75 / 1.0 × r95 bands are working heuristics. A stylistically mixed baseline gives a wide r95, so nothing breaches. Read the raw distance, and fit envelopes on coherent sets.

## Known sharp edges

- **Short complete answers can read as collapse.** "Yes." and some one- or two-sentence answers trip the severe tier. Check `token_count` and the text before calling a flag a failure.
- **Length confounds.** Most axes shift with length. Report `token_count` and compare like with like.
- **Prompt echo.** 219 of 1,600 operating-window answers restate the prompt, which moves μ and others. Strip echoed prompts if you're comparing answers.
- **English word lists.** Stopwords, common words, transitions and subordinators are English. Other languages will read strangely.
- **Older readings.** `x_p` from versions before v17 isn't comparable with v19 (it changed definition, and an earlier version stored values that don't match v19's). Compare within one `kernel_version`.
- **Token counts need tiktoken.** `tiktoken_token_count` is −1 unless `tiktoken` is installed. The first use downloads the `cl100k_base` vocabulary.
