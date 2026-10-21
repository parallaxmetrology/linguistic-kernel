"""Load the ORIGINAL kernel_v19.py by path (for golden generation and checks)."""
import importlib.util
import sys


def load(path):
    spec = importlib.util.spec_from_file_location("kernel_v19_original", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["kernel_v19_original"] = mod
    spec.loader.exec_module(mod)
    return mod
