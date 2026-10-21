"""
Command line:

    lk measure "some text"                      JSON for one text
    lk measure --file answer.txt                JSON for one file
    lk measure outputs.jsonl -o readings.csv    many texts (.jsonl/.json/.csv/.txt or folders)
    lk fingerprint readings.csv [--by engine]   how a set occupies structural space
    lk compare a.csv b.csv [--labels A B]       two sets side by side
    lk envelope fit normal.csv -o env.json      fit an envelope on your own normal outputs
    lk envelope check env.json new.csv          distance and band for new outputs
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd


def _cmd_measure(a):
    from .batch import measure_many
    from .kernel import measure, measure_full
    if a.file or (len(a.inputs) == 1 and not Path(a.inputs[0]).exists()):
        text = Path(a.file).read_text(encoding="utf-8") if a.file else a.inputs[0]
        out = measure_full(text, prompt=a.prompt, include_detail=False) if a.full else measure(text, prompt=a.prompt)
        print(json.dumps(out, indent=2, ensure_ascii=False, default=str))
        return
    df = measure_many([Path(x) for x in a.inputs], text_col=a.text_col, progress=a.out is not None)
    if a.out:
        df.to_csv(a.out, index=False)
        print(f"Wrote {len(df)} rows -> {a.out}")
    else:
        df.to_csv(sys.stdout, index=False)


def _cmd_fingerprint(a):
    from .corpus import fingerprint
    df = pd.read_csv(a.csv)
    pd.set_option("display.width", 170)
    groups = df.groupby(a.by) if a.by else [("all", df)]
    for name, g in groups:
        print(f"\n== {name}: {len(g)} texts")
        print(fingerprint(g).round(4)[["n", "p10", "p50", "p90", "window_width", "spread", "walls"]].to_string())
        if "token_count" in g.columns:
            print(f"   median length: {g['token_count'].median():.0f} tokens")


def _cmd_compare(a):
    from .corpus import compare
    pd.set_option("display.width", 170)
    print(compare(pd.read_csv(a.a), pd.read_csv(a.b), labels=a.labels).round(4).to_string())


def _cmd_envelope(a):
    from .corpus import Envelope, check, fit_envelope
    if a.action == "fit":
        env = fit_envelope(pd.read_csv(a.data))
        Path(a.out).write_text(json.dumps(env.to_dict(), indent=2))
        print(f"Envelope from {env.n} texts, r95 = {env.r95:.3f} -> {a.out}")
    else:
        env = Envelope.from_dict(json.loads(Path(a.env).read_text()))
        out = check(pd.read_csv(a.data), env)
        cols = [c for c in ("id", "engine", "prompt_id") if c in out.columns]
        print(out[cols + ["envelope_distance", "envelope_band"]].round(3).to_string(index=False))
        print("\n" + out["envelope_band"].value_counts().to_string())


def main(argv=None):
    p = argparse.ArgumentParser(prog="lk", description="Linguistic Kernel — measure the shape of text.")
    sub = p.add_subparsers(dest="cmd", required=True)

    m = sub.add_parser("measure", help="measure one text, a file, or many")
    m.add_argument("inputs", nargs="*", help="text, or .jsonl/.json/.csv/.txt files or folders")
    m.add_argument("--file", help="read one text from this file")
    m.add_argument("--prompt", help="the prompt (recorded in meta)")
    m.add_argument("--full", action="store_true", help="full v19 output with evidence and meta")
    m.add_argument("--text-col", dest="text_col", help="column holding the text (auto-detected by default)")
    m.add_argument("-o", "--out", help="write CSV here")
    m.set_defaults(func=_cmd_measure)

    f = sub.add_parser("fingerprint", help="how a set occupies structural space")
    f.add_argument("csv")
    f.add_argument("--by", help="column to group by, e.g. engine")
    f.set_defaults(func=_cmd_fingerprint)

    c = sub.add_parser("compare", help="compare two measured sets")
    c.add_argument("a")
    c.add_argument("b")
    c.add_argument("--labels", nargs=2, default=("a", "b"))
    c.set_defaults(func=_cmd_compare)

    e = sub.add_parser("envelope", help="fit an envelope on normal outputs, or check new ones")
    es = e.add_subparsers(dest="action", required=True)
    ef = es.add_parser("fit")
    ef.add_argument("data")
    ef.add_argument("-o", "--out", required=True)
    ec = es.add_parser("check")
    ec.add_argument("env")
    ec.add_argument("data")
    e.set_defaults(func=_cmd_envelope)

    a = p.parse_args(argv)
    if a.cmd == "measure" and not a.inputs and not a.file:
        p.error("measure needs text, --file, or input paths")
    a.func(a)


if __name__ == "__main__":
    main()
