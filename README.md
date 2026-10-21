# Linguistic Kernel

**Text has shape. Measure it.**

A deterministic instrument for the *structure* of text, especially model output: where a response puts its weight, how much it breathes, how packed and how cohesive it is, how its sentences run. Every number is a count over the text itself. No model in the loop, no judge, no embeddings: same text, same numbers, on any machine.

It doesn't judge whether an answer is right, safe or good. Two equally correct answers can sit far apart, and that's the point: it measures *how* something was said, so prompts, models and conversations can be compared on evidence instead of vibes.

**[Play: Guess the Engine →](https://parallaxmetrology.github.io/linguistic-kernel/)** Same prompt, two answers: which one is Claude? Then see what a ruler that only counts would have guessed. (It's right 82% of the time.)

---

## Install

```bash
pip install "linguistic-kernel[tokens] @ git+https://github.com/parallaxmetrology/linguistic-kernel"
```

(`[tokens]` adds tiktoken for a BPE token count. Everything else needs only numpy and pandas.)

## Use

```python
import lingkernel

r = lingkernel.measure("The cache stores results. Later reads reuse them.\n\nStaleness is the cost.")
r["delta_x"], r["r_v"], r["mu"], r["rhetorical_state"]

df = lingkernel.measure_many("outputs.jsonl")      # .jsonl/.json/.csv/.txt, or folders
lingkernel.fingerprint(df)                          # how a set occupies structural space
```

```bash
lk measure "some text"                              # JSON for one text
lk measure outputs.jsonl -o readings.csv            # many texts
lk fingerprint readings.csv --by engine             # windows per model
lk compare model_a.csv model_b.csv --labels A B     # two sets side by side
lk envelope fit normal.csv -o env.json              # your normal, as an envelope
lk envelope check env.json today.csv                # stable / elevated / excursion
```

## What it measures

| | name | reads |
|---|---|---|
| `Δx` | weight shift | front-loaded (−) or back-loaded (+) content |
| `rᵥ` | void ratio | breathing room: paragraphs, bullets, short sentences |
| `ρᵣ` | packing density | content words vs connective words |
| `μ` | cohesion | discourse scaffolding (in practice, mostly reference pronouns) |
| `Δy` | segmentation strain | long run-on sentences (+) vs short fragments (−) |
| `xₚ` | peripheral pull | rare vocabulary and figurative language |
| `θ` | flow instability | jumps between sentences vs smooth continuation |
| `dₛ` | structural thickness | clause stacking (commas, colons, subordinators) |

Plus a basin label, a **rhetorical state** (including `formatting_collapse` for truncated or broken answers), and an evidence bundle with every count behind every number. Definitions: [docs/metrics.md](docs/metrics.md).

## What the data supports so far

From three corpora (Claude, GPT and Gemini on the same 400 prompts; 1,600 Gemini answers across stress conditions; 60 answers with token log-probabilities):

- **Engines write differently, starting with length.** Claude's median answer is about twice as long as GPT's or Gemini's under the same prompts, and many structural differences travel with length.
- **Shape and length together tell engines apart** better than either alone: 82% of pairings, against 67% for shape and 65% for length (leave-one-prompt-out). Claude is easy to spot; GPT vs Gemini is close to a coin flip with a lean (62%).
- **The collapse detector catches truncations** on its home corpus: all 36 human-confirmed truncations, with 2 false alarms. A length-only rule catches 12. Out-of-sample, it's untested.
- **Clause thickness (`dₛ`) tracks generation-level uncertainty** (r = 0.36 after controlling for length and prompt family).

Several earlier readings are still **open**: not yet established, and some may need adjusting. They include which axis carries most of the movement, whether μ works as a stability control, and whether kernel distance beats word count as a general anomaly score. The details, and the known sharp edges, are in [docs/evidence.md](docs/evidence.md).

## Faithful to the published kernel

The package wraps **v19**, the frozen kernel behind the studies. `tests/test_golden.py` checks it against the original file on 28 texts, field by field, and the package reproduces all 1,200 published EMS readings exactly. See [docs/lineage.md](docs/lineage.md).

## Data

[`fingerprints/`](fingerprints/) has the measured readings: three engines × 400 prompts, with human-confirmed truncation labels, and the Gemini operating-window set. [`data/ems_1200.jsonl`](data/ems_1200.jsonl) has the prompts and the 1,200 answers themselves. Beat the detector, or show where it's wrong.

## Contribute

Most useful, in order:
- **Labeled outputs from other models**, especially truncated or broken ones, to test the collapse detector out of sample.
- **Disagreements:** a text whose reading is obviously off.
- **Other languages:** the word lists are English.
- **A browser port** so anyone can paste text into the demo.

See [CONTRIBUTING.md](CONTRIBUTING.md). Questions go in [Discussions](https://github.com/parallaxmetrology/linguistic-kernel/discussions).

## Part of Parallax Metrology

One principle across domains: structure has geometry, and geometry is measurable without knowing what it means. The visual sibling is the [Visual Thinking Lens](https://github.com/parallaxmetrology/visual-thinking-lens). More at [parallaxmetrology.com](https://www.parallaxmetrology.com).

## License

Code: [MIT](LICENSE). Docs and data: [CC BY 4.0](LICENSE-CONTENT). Model answers in `data/` were produced by Claude, GPT and Gemini for the EMS study and are shared for research and reproducibility.
