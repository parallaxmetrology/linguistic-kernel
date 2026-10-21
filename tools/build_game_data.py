"""
Build docs/game-data.json for "Guess the Engine".

For every EMS prompt, the three engines' answers and their kernel readings.
For every pair of engines on a prompt, "the lens's guess": which answer sits
closer to which engine's profile, using engine centroids computed WITHOUT that
prompt (leave-one-prompt-out) over the eight axes plus log token count.

    python tools/build_game_data.py
"""
import itertools
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AXES = ["delta_x", "r_v", "rho_r", "mu", "delta_y", "x_p", "theta", "d_s"]
FEATS = AXES + ["log_tokens"]
ENGINES = ["Claude", "GPT", "Gemini"]


def main():
    read = pd.read_csv(ROOT / "fingerprints" / "ems_3engines_1200.csv")
    text = pd.read_json(ROOT / "data" / "ems_1200.jsonl", lines=True)
    d = read.merge(text[["engine", "prompt_id", "prompt", "response"]], on=["engine", "prompt_id"])
    d["log_tokens"] = np.log1p(d["token_count"])

    rounds, correct, total = [], 0, 0
    pair_stats = {}
    for pid, g in d.groupby("prompt_id"):
        if set(g["engine"]) != set(ENGINES):
            continue
        tr = d[d["prompt_id"] != pid]
        mu, sd = tr[FEATS].mean(), tr[FEATS].std().replace(0, 1)
        cent = {e: ((tr[tr["engine"] == e][FEATS] - mu) / sd).mean() for e in ENGINES}
        z = {r["engine"]: (r[FEATS] - mu) / sd for _, r in g.iterrows()}
        lens = {}
        for a, b in itertools.combinations(ENGINES, 2):
            keep = np.linalg.norm(z[a] - cent[a]) + np.linalg.norm(z[b] - cent[b])
            swap = np.linalg.norm(z[a] - cent[b]) + np.linalg.norm(z[b] - cent[a])
            ok = bool(keep < swap)
            lens[f"{a}|{b}"] = ok
            correct += ok
            total += 1
            key = f"{a} vs {b}"
            s = pair_stats.setdefault(key, [0, 0])
            s[0] += ok
            s[1] += 1
        answers = {}
        for _, r in g.iterrows():
            answers[r["engine"]] = {
                "text": r["response"],
                "tokens": int(r["token_count"]),
                "state": r["rhetorical_state"],
                "collapse": r["collapse_subtype"],
                "truncated": bool(r["confirmed_truncation"]),
                **{k: round(float(r[k]), 4) for k in AXES},
            }
        rounds.append({"id": int(pid), "type": g["prompt_type"].iloc[0], "prompt": g["prompt"].iloc[0],
                       "answers": answers, "lens": lens})

    ranges = {k: [round(float(d[k].quantile(0.05)), 4), round(float(d[k].quantile(0.95)), 4)] for k in AXES}
    ranges["tokens"] = [int(d["token_count"].quantile(0.05)), int(d["token_count"].quantile(0.95))]
    out = {
        "source": "EMS study: Claude, GPT and Gemini on the same 400 prompts (kernel v19)",
        "lens_accuracy": round(correct / total, 3),
        "lens_pairs": {k: round(v[0] / v[1], 3) for k, v in pair_stats.items()},
        "ranges": ranges,
        "rounds": rounds,
    }
    (ROOT / "docs").mkdir(exist_ok=True)
    (ROOT / "docs" / "game-data.json").write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")))
    print(f"{len(rounds)} prompts; lens accuracy {out['lens_accuracy']}; by pair {out['lens_pairs']}")


if __name__ == "__main__":
    main()
