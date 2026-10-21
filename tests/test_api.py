import json
from pathlib import Path

import pandas as pd

import lingkernel as L
from lingkernel.cli import main

ROOT = Path(__file__).resolve().parents[1]
TEXTS = ROOT / "examples" / "texts.jsonl"


def test_measure_flat_keys_and_determinism():
    t = "First we fill the cache. Then reads reuse it.\n\nStaleness is the cost."
    a, b = L.measure(t), L.measure(t)
    assert a == b
    assert set(L.KERNEL_KEYS) <= set(a)
    assert a["kernel_version"] == L.KERNEL_VERSION


def test_measure_many_from_jsonl_strings_and_frame():
    df = L.measure_many(TEXTS)
    assert len(df) == len(TEXTS.read_text().splitlines())
    assert {"engine", "id", "delta_x", "rhetorical_state"} <= set(df.columns)
    assert len(L.measure_many(["one text.", "two texts here."])) == 2
    assert len(L.measure_many(pd.DataFrame({"output": ["a b c.", "d e f."]}))) == 2


def test_fingerprint_signed_and_unicode_columns():
    df = L.measure_many(TEXTS)
    fp = L.fingerprint(df)
    assert fp.loc["delta_x", "spread"] == "signed: see window"
    uni = df.rename(columns={"delta_x": "Δx", "r_v": "rᵥ"})
    assert "delta_x" in L.fingerprint(uni).index


def test_envelope_roundtrip_and_bands():
    df = L.measure_many(TEXTS)
    env = L.fit_envelope(df)
    env2 = L.Envelope.from_dict(json.loads(json.dumps(env.to_dict())))
    out = L.check(df, env2)
    assert set(out["envelope_band"]) <= {"stable", "elevated", "excursion"}
    assert (out["envelope_band"] == "stable").mean() > 0.5
    assert L.envelope_band(0.5, 1.0) == "stable" and L.envelope_band(0.9, 1.0) == "elevated"
    assert L.envelope_band(1.2, 1.0) == "excursion"
    assert L.hysteresis(df.iloc[:5], df.iloc[:5], env) == 0.0


def test_rigidity_runs():
    df = L.measure_many(TEXTS)
    table, overall = L.rigidity(df, "engine")
    assert "rigidity_ratio" in table.columns and overall >= 0


def test_cli(tmp_path, capsys):
    main(["measure", "A short answer. It ends."])
    assert '"delta_x"' in capsys.readouterr().out
    out = tmp_path / "r.csv"
    main(["measure", str(TEXTS), "-o", str(out)])
    main(["fingerprint", str(out), "--by", "engine"])
    assert "Claude" in capsys.readouterr().out
    main(["envelope", "fit", str(out), "-o", str(tmp_path / "env.json")])
    main(["envelope", "check", str(tmp_path / "env.json"), str(out)])
    assert "stable" in capsys.readouterr().out
