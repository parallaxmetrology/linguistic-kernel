"""
Linguistic Kernel — deterministic structural measurement of text.

    import lingkernel
    r = lingkernel.measure("Some model output…")      # eight coordinates + state
    df = lingkernel.measure_many("outputs.jsonl")        # one row per text
    lingkernel.fingerprint(df)                           # how a set occupies structural space

Part of Parallax Metrology: https://www.parallaxmetrology.com
"""
from .batch import measure_many
from .corpus import (Envelope, check, compare, envelope_band, fingerprint, fit_envelope, hysteresis,
                     rigidity)
from .kernel import AUX_KEYS, CORE_KEYS, KERNEL_KEYS, KERNEL_VERSION, measure, measure_full

__version__ = "0.1.0"

__all__ = [
    "measure", "measure_full", "measure_many",
    "fingerprint", "compare", "rigidity",
    "Envelope", "fit_envelope", "check", "envelope_band", "hysteresis",
    "CORE_KEYS", "AUX_KEYS", "KERNEL_KEYS", "KERNEL_VERSION", "__version__",
]
