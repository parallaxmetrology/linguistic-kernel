# Contributing

The project grows when people measure things and argue about what they find.

## Ways in

- **Labeled outputs.** Answers from any model with a note of which ones are truncated, broken, echoed or otherwise off. That's how the collapse detector gets tested outside the corpus it was calibrated on.
- **Fingerprints.** Measure a set (`lk measure outputs.jsonl -o out.csv`) and open a Discussion or a *Fingerprint* issue: model and version, prompts, how outputs were collected, what surprised you.
- **Wrong readings.** A text whose numbers clearly don't fit what it's doing. Include the text and `lk measure --full` output.
- **Other languages and a browser port.** See the roadmap.

## Development

```bash
git clone https://github.com/parallaxmetrology/linguistic-kernel
cd linguistic-kernel
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## The one firm rule: v19 doesn't move

`src/lingkernel/_v19.py` is the frozen kernel behind the published studies. Don't edit it. Improvements go in new modules, or into a future `v20` file with its own version string, golden files, and a changelog entry explaining every difference. `tests/test_golden.py` must keep passing unchanged.

Be kind and specific: disagree with numbers, not people. See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
