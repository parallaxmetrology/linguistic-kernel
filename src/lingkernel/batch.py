"""Measure many texts into one table."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Iterable, List, Optional, Union

import pandas as pd

from .kernel import measure

TEXT_COLUMNS = ("text", "response", "output", "completion", "answer")
TEXT_EXTS = {".txt", ".md"}


def _records(path: Path) -> List[dict]:
    suf = path.suffix.lower()
    if suf == ".jsonl":
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if suf == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else [data]
    if suf == ".csv":
        return pd.read_csv(path).to_dict("records")
    if suf in TEXT_EXTS:
        return [{"id": path.name, "text": path.read_text(encoding="utf-8")}]
    return []


def _expand(paths: Iterable[Union[str, os.PathLike]]) -> List[Path]:
    out: List[Path] = []
    for p in map(Path, paths):
        if p.is_dir():
            out += sorted(q for q in p.rglob("*") if q.suffix.lower() in TEXT_EXTS | {".jsonl", ".json", ".csv"}
                          and not any(part.startswith(".") for part in q.relative_to(p).parts))
        else:
            out.append(p)
    return out


def measure_many(source: Union[str, os.PathLike, pd.DataFrame, Iterable], text_col: Optional[str] = None,
                 prompt_col: Optional[str] = "prompt", progress: bool = False) -> pd.DataFrame:
    """One row per text.

    `source` may be a DataFrame, a list of texts (plain strings) or dicts, or paths
    (a single path string, or Path objects): `.txt`/`.md`
    files (one text each), `.jsonl`/`.json`/`.csv` (one text per record), or folders
    of those. The text column is found automatically (text, response, output,
    completion, answer) unless `text_col` is given. Other columns (ids, engine,
    prompt type...) are carried through.
    """
    if isinstance(source, pd.DataFrame):
        records = source.to_dict("records")
    elif isinstance(source, (str, os.PathLike)):
        records = [r for p in _expand([source]) for r in _records(p)]
    else:
        items = list(source)
        if items and all(isinstance(i, str) for i in items):
            records = [{"text": t} for t in items]
        elif items and all(isinstance(i, dict) for i in items):
            records = items
        else:
            records = [r for p in _expand(items) for r in _records(p)]

    rows = []
    for i, rec in enumerate(records, 1):
        col = text_col or next((c for c in TEXT_COLUMNS if c in rec), None)
        if col is None:
            raise ValueError(f"No text column found in record {i}; pass text_col=. Keys: {sorted(rec)[:10]}")
        text = rec.get(col)
        text = "" if text is None or (isinstance(text, float) and pd.isna(text)) else str(text)
        prompt = rec.get(prompt_col) if prompt_col else None
        prompt = None if prompt is None or (isinstance(prompt, float) and pd.isna(prompt)) else str(prompt)
        if progress and (i % 100 == 0 or i == len(records)):
            print(f"[{i}/{len(records)}]", flush=True)
        meta = {k: v for k, v in rec.items() if k not in (col, prompt_col)}
        rows.append({**meta, **measure(text, prompt=prompt)})
    return pd.DataFrame(rows)
