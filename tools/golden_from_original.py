"""
Regenerate tests/golden/v19.json by running the ORIGINAL kernel_v19.py on
examples/texts.jsonl. The package's copy (src/lingkernel/_v19.py) must reproduce
these outputs exactly; tests/test_golden.py checks it.

    python tools/golden_from_original.py /path/to/kernel_v19.py
"""
import json
import sys
from pathlib import Path

from _orig import load

ROOT = Path(__file__).resolve().parents[1]


def main():
    mod = load(sys.argv[1])
    lk = mod.LinguisticKernel()
    out = {}
    for line in (ROOT / "examples" / "texts.jsonl").read_text().splitlines():
        r = json.loads(line)
        out[r["id"]] = lk.compute(r["response"], prompt=r["prompt"] or None)
    (ROOT / "tests" / "golden").mkdir(parents=True, exist_ok=True)
    (ROOT / "tests" / "golden" / "v19.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, sort_keys=True))
    print(f"wrote {len(out)} readings")


if __name__ == "__main__":
    main()
