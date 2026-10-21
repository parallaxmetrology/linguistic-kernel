"""
The package must reproduce the ORIGINAL kernel_v19.py exactly.

tests/golden/v19.json was produced by running the original file on
examples/texts.jsonl (tools/golden_from_original.py). The kernel is pure
Python (regex, counting, arithmetic), so outputs must match to the last digit
on any platform. Only the tiktoken version string is allowed to differ.
"""
import json
import math
from pathlib import Path

import pytest

import lingkernel

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = json.loads((ROOT / "tests" / "golden" / "v19.json").read_text())
_LINES = (ROOT / "examples" / "texts.jsonl").read_text().splitlines()
TEXTS = {json.loads(line)["id"]: json.loads(line) for line in _LINES}
SKIP = {("meta", "tiktoken_version")}


def _same(a, b, path=()):
    if path[-2:] in SKIP or (len(path) >= 2 and tuple(path[-2:]) in SKIP):
        return
    if isinstance(b, dict):
        assert isinstance(a, dict) and set(a) == set(b), f"{path}: keys differ"
        for k in b:
            _same(a[k], b[k], path + (k,))
    elif isinstance(b, list):
        assert isinstance(a, list) and len(a) == len(b), f"{path}: list differs"
        for i, (x, y) in enumerate(zip(a, b)):
            _same(x, y, path + (i,))
    elif isinstance(b, float):
        assert isinstance(a, (int, float)) and (math.isclose(a, b, rel_tol=0, abs_tol=1e-12)
                                                 or (math.isnan(a) and math.isnan(b))), f"{path}: {a} != {b}"
    else:
        assert a == b, f"{path}: {a!r} != {b!r}"


@pytest.mark.parametrize("tid", sorted(GOLDEN))
def test_matches_original_v19(tid):
    t = TEXTS[tid]
    got = json.loads(json.dumps(lingkernel.measure_full(t["response"], prompt=t["prompt"] or None), ensure_ascii=False))
    _same(got, GOLDEN[tid])
