"""
Friendly wrapper around the frozen v19 kernel (`_v19.py`).

`_v19.py` is the Linguistic Kernel v19 source, unchanged except that ChatGPT
citation markers were removed from its docstring and an unrelated add-on
section at the end was left out (see docs/lineage.md). Its numbers are pinned
by tests/test_golden.py against the original file.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from . import _v19

KERNEL_VERSION = "lang-kernel-rebuild-v19"

# unicode keys used by v19 -> plain names used in CSVs and the corpus tools
NAMES = {"Δx": "delta_x", "rᵥ": "r_v", "ρᵣ": "rho_r", "μ": "mu",
         "Δy": "delta_y", "xₚ": "x_p", "θ": "theta", "dₛ": "d_s"}
CORE_KEYS = ("delta_x", "r_v", "rho_r", "mu")
AUX_KEYS = ("delta_y", "x_p", "theta", "d_s")
KERNEL_KEYS = CORE_KEYS + AUX_KEYS

EVIDENCE_KEYS = ("token_count", "sentence_count", "paragraph_count", "bullet_line_count",
                 "segmentation_reliable", "rhetorical_state", "collapse_subtype",
                 "tail_incomplete_flag", "math_expression_tail_flag", "tiktoken_token_count")

_KERNEL: Optional[_v19.LinguisticKernel] = None


def _kernel() -> _v19.LinguisticKernel:
    global _KERNEL
    if _KERNEL is None:
        _KERNEL = _v19.LinguisticKernel()
    return _KERNEL


def measure_full(text: str, prompt: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """The complete v19 output: kernel, aux, basin, flags, evidence, meta, detail."""
    return _kernel().compute(text, prompt=prompt, **kwargs)


def flatten(full: Dict[str, Any]) -> Dict[str, Any]:
    """One flat row: eight coordinates, basin, state and the key evidence counts."""
    row: Dict[str, Any] = {}
    for block in ("kernel", "aux"):
        for k, v in (full.get(block) or {}).items():
            row[NAMES.get(k, k)] = v
    row["basin"] = full.get("basin")
    ev = full.get("evidence") or {}
    for k in EVIDENCE_KEYS:
        if k in ev:
            row[k] = ev[k]
    row["kernel_version"] = (full.get("meta") or {}).get("kernel_version", KERNEL_VERSION)
    return row


def measure(text: str, prompt: Optional[str] = None) -> Dict[str, Any]:
    """Measure one text. Returns a flat dict (see `flatten`).

        >>> import lingkernel
        >>> r = lingkernel.measure("The cache stores results. Reads reuse them.")
        >>> r["delta_x"], r["rhetorical_state"]
    """
    return flatten(measure_full(text, prompt=prompt, include_detail=False))
