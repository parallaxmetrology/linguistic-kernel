# Fingerprints

Measured readings, kernel `lang-kernel-rebuild-v19`.

| file | n | what |
|---|---|---|
| `ems_3engines_1200.csv` | 1,200 | Claude, GPT and Gemini on the same 400 everyday, science and math prompts under a batch constraint (EMS study). All eight axes, basin, rhetorical state, collapse subtype, word and BPE token counts, `batch_position`, and **`confirmed_truncation`**: a human label for answers that were actually cut off. Texts: `../data/ems_1200.jsonl`. |
| `gemini_operating_window_1600.csv` | 1,600 | Gemini across conditions: baseline, temperature, context, template, spike, and stress families (contradiction loops, recursion, instruction conflict, topic jumps…). Readings as published; the texts aren't included. |

## Quick looks

```python
import pandas as pd, lingkernel as L
d = pd.read_csv("fingerprints/ems_3engines_1200.csv")
for e, g in d.groupby("engine"):
    print(e, g.token_count.median(), g.confirmed_truncation.sum())
L.compare(d[d.engine == "GPT"], d[d.engine == "Gemini"], labels=("GPT", "Gemini"))
```

| engine | median words | confirmed truncations | flagged by the kernel |
|---|---|---|---|
| Claude | 86 | 1 | 1 |
| GPT | 39 | 15 | 15 |
| Gemini | 41 | 20 | 22 (2 complete answers) |

The detector's thresholds were calibrated on these corpora, so treat the agreement as in-sample. New labeled data from other models is the best test.

**Add yours:** a CSV from `lk measure … -o out.csv`, plus a few lines on the model, version, prompts and how outputs were collected.
