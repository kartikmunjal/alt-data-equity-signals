"""Load Reddit WallStreetBets exports from Pushshift/Kaggle-style files."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_wsb_posts(path: str | Path) -> pd.DataFrame:
    """Load WSB posts/comments from CSV, JSONL, or Parquet."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)

    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path)
    if suffix in {".jsonl", ".ndjson"}:
        return pd.read_json(path, lines=True)
    if suffix == ".json":
        return pd.read_json(path)
    if suffix in {".parquet", ".pq"}:
        return pd.read_parquet(path)
    raise ValueError(f"unsupported WSB file type: {path.suffix}")
