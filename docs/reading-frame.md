# Reading chat-style text: the reading frame

v19 was built for plain prose. Chat and benchmark answers bring markdown, very short replies, other languages and the occasional literal special token, and v19 misreads each of these in a specific way. `lingkernel.read` puts a thin preparation layer in front of the kernel. It never changes a kernel number: it changes what text the kernel is given, and it measures every text both ways.

```python
import lingkernel
r = lingkernel.read(answer)
r["eligible"], r["reasons"]          # English, ≥40 words, readable by v19
r["raw"]["delta_y"], r["framed"]["delta_y"], r["delta"]["delta_y"]
r["edits"]                            # code blocks, table lines, headers, bold lines, links removed
r["collapse_reading"]                 # short_complete / short_cut / cut_partial / cut_code_or_math / none
row = lingkernel.read_row(answer)     # the same as one flat row: raw_*, framed_*, edit_*
```

Plain text with no markdown comes back byte-identical, so `raw == framed` and every delta is 0.

## What it changes

| Pattern | What v19 does with it | What the frame does |
|---|---|---|
| Fenced code block | reads code as one long run-on sentence (Δy, dₛ inflate) | removes it (unclosed fences are recorded) |
| Table rows | reads a table as one huge sentence, collapses rᵥ | removes them |
| `# Header` / `**Bold title:**` line | glues the title onto the next sentence | removes the line, leaving a paragraph break |
| `[text](url)` | counts URL fragments as rare words | keeps the text, drops the URL |

On 3,000 Chatbot Arena answers, framing moved sentence-length strain (Δy) for code answers from 1.11 to 0.40 (plain answers: 0.47) and for tables from 4.76 to 0.63, and clause stacking (dₛ) for code answers from 0.83 to 0.52 (plain: 0.56). An earlier version turned headers into their own one-sentence paragraph; that added paragraphs that were not there (rᵥ 0.39 → 0.60 against 0.27 for plain answers), so titles are dropped instead (0.42 → 0.30).

## Eligibility

A text is eligible when at least 95% of its letters are a-z, at least 12% of its words are English function words (checked from 20 words up), it has at least 40 words after framing, and v19 can read it. `reasons` lists what failed: `no_letters`, `non_latin_script`, `low_english_function_words`, `short_prose`, `kernel_error`.

## Collapse, restated for chat

On chat corpora v19's `severe` collapse tier fires mostly on short complete answers and refusals. `collapse_reading` keeps v19's label but splits `severe` by whether the text actually ends open: `short_cut` only when v19's tail signal fires *and* the text does not end in closing punctuation. On 3,000 Arena answers, 206 of 209 `severe` labels read as `short_complete`. Truncation is always taken from the raw reading, because removing code would hide a cut-off code answer.

## Version

`FRAME_VERSION = "reading-frame-r1.1"`, the version used in [Structure Beyond Length](https://github.com/parallaxmetrology/structure-beyond-length). r1.1 added the `kernel_error` path for texts v19 cannot read.
