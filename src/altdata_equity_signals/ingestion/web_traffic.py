"""Load operational web-traffic datasets such as SimilarWeb exports."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_web_traffic(path: str | Path) -> pd.DataFrame:
    """Load monthly ticker-level web traffic from CSV or Parquet.

    Expected columns:
        date, ticker, visits

    Optional columns:
        source, domain
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)

    if path.suffix.lower() in {".parquet", ".pq"}:
        frame = pd.read_parquet(path)
    else:
        frame = pd.read_csv(path)

    required = {"date", "ticker", "visits"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"web traffic file missing required columns: {sorted(missing)}")

    frame = frame.copy()
    frame["date"] = pd.to_datetime(frame["date"]).dt.to_period("M").dt.to_timestamp("M")
    frame["ticker"] = frame["ticker"].astype(str).str.upper()
    frame["visits"] = pd.to_numeric(frame["visits"], errors="coerce")
    frame = frame.dropna(subset=["date", "ticker", "visits"])
    return frame.sort_values(["date", "ticker"]).reset_index(drop=True)
