"""Price ingestion helpers."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_close_panel(path: str | Path) -> pd.DataFrame:
    """Load a date x ticker close-price panel from CSV or Parquet."""
    path = Path(path)
    if path.suffix.lower() in {".parquet", ".pq"}:
        panel = pd.read_parquet(path)
    else:
        panel = pd.read_csv(path, index_col=0)
    panel.index = pd.to_datetime(panel.index)
    panel.columns = [str(col).upper() for col in panel.columns]
    return panel.sort_index()


def download_close_panel(tickers: list[str], start: str, end: str | None = None) -> pd.DataFrame:
    """Download adjusted close prices with yfinance."""
    import yfinance as yf

    data = yf.download(tickers, start=start, end=end, auto_adjust=True, progress=False)
    if isinstance(data.columns, pd.MultiIndex):
        close = data["Close"]
    else:
        close = data[["Close"]].rename(columns={"Close": tickers[0]})
    close.columns = [str(col).upper() for col in close.columns]
    close.index = pd.to_datetime(close.index).tz_localize(None).normalize()
    return close.sort_index()
