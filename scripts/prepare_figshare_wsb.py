#!/usr/bin/env python3
"""Convert Figshare ticker-level WSB JSON exports into one pipeline input file."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


KEEP_COLUMNS = (
    "created_utc",
    "title",
    "selftext",
    "body",
    "score",
    "ups",
    "num_comments",
    "link_flair_text",
    "url",
    "permalink",
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare Figshare WSB JSON files")
    parser.add_argument("--root", required=True, help="Extracted Figshare directory")
    parser.add_argument("--tickers", nargs="+", default=["GME", "AMC", "AAPL", "MSFT", "NOK", "TSLA"])
    parser.add_argument("--out", required=True, help="Output CSV/Parquet path")
    parser.add_argument("--start", default="2020-10-01")
    parser.add_argument("--end", default="2022-04-30")
    args = parser.parse_args()

    root = Path(args.root)
    frames: list[pd.DataFrame] = []
    for ticker in args.tickers:
        ticker_root = root / ticker.upper()
        if not ticker_root.exists():
            raise FileNotFoundError(ticker_root)
        for path in sorted(ticker_root.glob("*.json")):
            if path.stat().st_size <= 2:
                continue
            try:
                frame = pd.read_json(path)
            except ValueError:
                continue
            if frame.empty or "created_utc" not in frame.columns:
                continue
            keep = [col for col in KEEP_COLUMNS if col in frame.columns]
            frame = frame[keep].copy()
            frame["source_ticker"] = ticker.upper()
            frame["source_file"] = path.name
            frames.append(frame)

    if not frames:
        raise RuntimeError(f"no usable Figshare WSB files found under {root}")

    posts = pd.concat(frames, ignore_index=True)
    posts = posts.drop_duplicates(subset=[col for col in ("created_utc", "title", "body", "url") if col in posts.columns])
    dates = pd.to_datetime(posts["created_utc"], unit="s", utc=True)
    mask = (dates >= pd.Timestamp(args.start, tz="UTC")) & (dates <= pd.Timestamp(args.end, tz="UTC"))
    posts = posts.loc[mask].sort_values("created_utc").reset_index(drop=True)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.suffix.lower() in {".parquet", ".pq"}:
        posts.to_parquet(out, index=False)
    else:
        posts.to_csv(out, index=False)

    print(f"wrote {len(posts):,} rows to {out}")
    print(f"date range: {pd.to_datetime(posts['created_utc'], unit='s').min().date()} to {pd.to_datetime(posts['created_utc'], unit='s').max().date()}")
    print(f"source tickers: {', '.join(sorted(posts['source_ticker'].unique()))}")


if __name__ == "__main__":
    main()
