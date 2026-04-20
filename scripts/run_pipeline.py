#!/usr/bin/env python3
"""Run the alt-data equity signal research pipeline."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from altdata_equity_signals.pipeline import run_pipeline


def main() -> None:
    parser = argparse.ArgumentParser(description="Alternative-data equity signal research")
    parser.add_argument("--posts", help="CSV/JSONL/Parquet WSB posts or comments export")
    parser.add_argument("--prices", help="CSV/Parquet date x ticker close-price panel")
    parser.add_argument("--web-traffic", help="CSV/Parquet monthly web traffic: date,ticker,visits")
    parser.add_argument("--tickers", nargs="+", help="Universe for yfinance download and extraction")
    parser.add_argument("--start", default="2021-01-01")
    parser.add_argument("--end", default=None)
    parser.add_argument("--horizons", nargs="+", type=int, default=[1, 5, 10, 21])
    parser.add_argument("--out", default="results")
    parser.add_argument("--synthetic", action="store_true", help="Run deterministic synthetic demo")
    args = parser.parse_args()

    outputs = run_pipeline(
        posts_path=args.posts,
        prices_path=args.prices,
        web_traffic_path=args.web_traffic,
        tickers=args.tickers,
        start=args.start,
        end=args.end,
        horizons=args.horizons,
        output_dir=args.out,
        use_synthetic=args.synthetic,
    )

    print("\nIC SUMMARY")
    print(outputs["ic"].round(4).to_string(index=False))
    print("\nFAMA-MACBETH")
    print(outputs["fama_macbeth"].round(4).to_string())
    print("\nQUINTILE MEANS")
    print(outputs["quintiles"].mean().round(4).to_string())


if __name__ == "__main__":
    main()
