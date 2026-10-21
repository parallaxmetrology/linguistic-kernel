"""
Corpus-level readings: how a model (or prompt set, or writer) occupies structural
space, and whether new outputs leave it.

fingerprint / compare / rigidity follow the Visual Thinking Lens corpus tools.
The envelope functions follow v19's own Phase-2 helpers (z-space centroid, r95,
band at 0.75 and 1.0 r95; hysteresis = distance between stress and recovery
centroids).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, List, Optional, Sequence, Union

import numpy as np
import pandas as pd

from .kernel import KERNEL_KEYS, NAMES

SIGNED = {"delta_x", "delta_y"}
SIGNED_LABEL = "signed: see window"
CV_WIDE, CV_MODERATE = 0.30, 0.15
WALL_HARD, WALL_SOFT = 0.15, 0.30
RIGID, FLEXIBLE = 1.5, 2.5
ENVELOPE_KEYS = ("delta_x", "r_v", "rho_r", "mu", "theta", "d_s", "x_p")  # v19 default (no delta_y)


def _plain(df: pd.DataFrame) -> pd.DataFrame:
    """Accept v19's unicode column names (Δx, rᵥ...) as well as plain ones."""
    return df.rename(columns={k: v for k, v in NAMES.items() if k in df.columns})


def _usable(df: pd.DataFrame) -> pd.DataFrame:
    """Rows with an error (unreadable input) are dropped. Unreliable segmentation is
    kept and should be reported, not silently filtered."""
    df = _plain(df)
    if "error" in df.columns:
        df = df[df["error"].isna()]
    return df


def _metrics(df: pd.DataFrame, metrics: Optional[Sequence[str]]) -> list:
    return list(metrics) if metrics is not None else [m for m in KERNEL_KEYS if m in df.columns]


def fingerprint(df: pd.DataFrame, metrics: Optional[Sequence[str]] = None) -> pd.DataFrame:
    """One row per metric: median, window (p10–p90), spread, walls, bimodality.

    Signed metrics (delta_x, delta_y) get no CV-based spread label; compare their
    window_width instead.
    """
    df = _usable(df)
    rows = []
    for m in _metrics(df, metrics):
        v = pd.to_numeric(df[m], errors="coerce").dropna().to_numpy(dtype=float)
        if len(v) < 2:
            continue
        mean, std = v.mean(), v.std()
        signed = m in SIGNED
        cv = float("nan") if signed else (std / abs(mean) if abs(mean) > 1e-8 else 0.0)
        rng = v.max() - v.min() if v.max() > v.min() else 1.0
        hard = std / rng
        z = (v - mean) / std if std > 0 else np.zeros_like(v)
        skew = float(np.mean(z ** 3)) if std > 0 else 0.0
        kurt = float(np.mean(z ** 4)) if std > 0 else 0.0
        p10, p50, p90 = np.percentile(v, [10, 50, 90])
        rows.append({
            "metric": m, "n": len(v), "mean": mean, "std": std, "cv": cv,
            "spread": (SIGNED_LABEL if signed else
                       "wide" if cv > CV_WIDE else "moderate" if cv > CV_MODERATE else "tight"),
            "p10": p10, "p50": p50, "p90": p90, "window_width": p90 - p10,
            "wall_hardness": hard,
            "walls": "hard" if hard < WALL_HARD else "soft" if hard > WALL_SOFT else "moderate",
            "skew": skew, "kurtosis": kurt,
            "bimodal": bool(len(v) >= 3 and kurt < 2.0 and abs(skew) < 0.8),
        })
    return pd.DataFrame(rows).set_index("metric") if rows else pd.DataFrame()


def compare(a: pd.DataFrame, b: pd.DataFrame, metrics: Optional[Sequence[str]] = None,
            labels: Iterable[str] = ("a", "b")) -> pd.DataFrame:
    """Two sets side by side: medians, windows, Cohen's d, window overlap.

    Report length too (`token_count`): many structural differences between
    models travel with how much they write.
    """
    la, lb = labels
    fa, fb = fingerprint(a, metrics), fingerprint(b, metrics)
    rows = []
    for m in fa.index.intersection(fb.index):
        pooled = np.sqrt((fa.at[m, "std"] ** 2 + fb.at[m, "std"] ** 2) / 2.0)
        lo, hi = max(fa.at[m, "p10"], fb.at[m, "p10"]), min(fa.at[m, "p90"], fb.at[m, "p90"])
        wb = fb.at[m, "window_width"]
        rows.append({"metric": m,
                     f"median_{la}": fa.at[m, "p50"], f"median_{lb}": fb.at[m, "p50"],
                     f"window_{la}": fa.at[m, "window_width"], f"window_{lb}": wb,
                     "cohens_d": (fa.at[m, "mean"] - fb.at[m, "mean"]) / pooled if pooled > 0 else 0.0,
                     "window_overlap": max(0.0, hi - lo) / wb if wb > 0 else float(lo <= hi)})
    return pd.DataFrame(rows).set_index("metric")


def rigidity(df: pd.DataFrame, group: Union[str, Callable[[dict], str]],
             metrics: Optional[Sequence[str]] = None):
    """Total std across grouped outputs / mean within-group std, per metric.

    Group by prompt to ask whether different prompts move structure more than
    re-runs of one prompt do. ~1: prompts barely matter; > 2.5: prompts drive it.
    Returns (per-metric table, overall median ratio).
    """
    df = _usable(df)
    keys = df.apply(group, axis=1) if callable(group) else df[group]
    groups = [g for _, g in df.groupby(keys.values) if len(g) >= 2]
    rows = []
    for m in _metrics(df, metrics):
        within = [np.var(g[m].astype(float)) for g in groups]
        allv = np.concatenate([g[m].astype(float).to_numpy() for g in groups]) if groups else np.array([])
        w = float(np.sqrt(np.mean(within))) if within else 0.0
        t = float(np.sqrt(np.var(allv))) if len(allv) else 0.0
        r = t / w if w > 1e-8 else 0.0
        rows.append({"metric": m, "within_std": w, "total_std": t, "rigidity_ratio": r,
                     "reading": "flexible" if r > FLEXIBLE else "moderate" if r > RIGID else "rigid"})
    out = pd.DataFrame(rows).set_index("metric")
    valid = out["rigidity_ratio"][out["rigidity_ratio"] > 0]
    return out, float(np.median(valid)) if len(valid) else 0.0


# ── Envelope (v19 Phase-2 helpers) ───────────────────────────────────────────
@dataclass
class Envelope:
    feature_cols: List[str]
    mean: np.ndarray
    std: np.ndarray
    centroid: np.ndarray
    r95: float
    n: int

    def to_dict(self):
        return {"feature_cols": self.feature_cols, "mean": self.mean.tolist(), "std": self.std.tolist(),
                "centroid": self.centroid.tolist(), "r95": self.r95, "n": self.n}

    @classmethod
    def from_dict(cls, d):
        return cls(d["feature_cols"], np.array(d["mean"]), np.array(d["std"]), np.array(d["centroid"]),
                   float(d["r95"]), int(d.get("n", 0)))


def _matrix(df: pd.DataFrame, cols: Sequence[str]) -> np.ndarray:
    return _plain(df)[list(cols)].apply(pd.to_numeric, errors="coerce").fillna(0.0).to_numpy(dtype=float)


def fit_envelope(baseline: pd.DataFrame, feature_cols: Sequence[str] = ENVELOPE_KEYS) -> Envelope:
    """Fit a z-space envelope (centroid + 95th-percentile radius) on your own normal outputs."""
    cols = [c for c in feature_cols if c in _plain(baseline).columns]
    X = _matrix(baseline, cols)
    mean, std = X.mean(axis=0), X.std(axis=0)
    std = np.where(std < 1e-8, 1.0, std)
    Z = (X - mean) / std
    centroid = Z.mean(axis=0)
    d = np.linalg.norm(Z - centroid, axis=1)
    return Envelope(cols, mean, std, centroid, float(np.quantile(d, 0.95)) if len(d) else 0.0, len(X))


def envelope_distance(df: pd.DataFrame, env: Envelope) -> np.ndarray:
    Z = (_matrix(df, env.feature_cols) - env.mean) / env.std
    return np.linalg.norm(Z - env.centroid, axis=1)


def envelope_band(distance: float, r95: float) -> str:
    """v19 bands: within 0.75·r95 stable, up to 1.0·r95 elevated, beyond: excursion."""
    if r95 <= 0:
        return "NA"
    nd = distance / r95
    return "stable" if nd <= 0.75 else "elevated" if nd <= 1.0 else "excursion"


def check(df: pd.DataFrame, env: Envelope) -> pd.DataFrame:
    """Add envelope distance and band to each row."""
    out = df.copy()
    d = envelope_distance(df, env)
    out["envelope_distance"] = d
    out["envelope_band"] = [envelope_band(float(x), env.r95) for x in d]
    return out


def hysteresis(stress: pd.DataFrame, recovery: pd.DataFrame, env: Envelope) -> float:
    """Distance between the stress and recovery centroids in the envelope's z-space."""
    if len(stress) == 0 or len(recovery) == 0:
        return float("nan")
    s = ((_matrix(stress, env.feature_cols) - env.mean) / env.std).mean(axis=0)
    r = ((_matrix(recovery, env.feature_cols) - env.mean) / env.std).mean(axis=0)
    return float(np.linalg.norm(s - r))
