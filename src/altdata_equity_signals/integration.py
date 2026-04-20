"""Adapters for connecting alt-data panels to the existing research repos."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def export_factor_panels(
    signals: dict[str, pd.DataFrame],
    output_dir: str | Path,
    *,
    prefix: str = "WSB",
) -> dict[str, Path]:
    """Export alt-data signals as named parquet panels for factor-research reuse.

    The output format is intentionally the same as the factor research repo expects:
    index=date, columns=ticker, values=signal score.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    paths: dict[str, Path] = {}
    for name, panel in signals.items():
        factor_name = f"{prefix}_{name}".upper()
        path = output_dir / f"{factor_name}.parquet"
        clean = panel.copy()
        clean.index = pd.to_datetime(clean.index)
        clean.columns = [str(col).upper() for col in clean.columns]
        clean.sort_index().to_parquet(path)
        paths[factor_name] = path
    return paths


def load_factor_panels(input_dir: str | Path, pattern: str = "*.parquet") -> dict[str, pd.DataFrame]:
    """Load exported parquet panels into a factor-name -> DataFrame mapping."""
    input_dir = Path(input_dir)
    panels = {}
    for path in sorted(input_dir.glob(pattern)):
        panel = pd.read_parquet(path)
        panel.index = pd.to_datetime(panel.index)
        panels[path.stem.upper()] = panel.sort_index()
    return panels


def merge_with_factor_library(
    base_factors: dict[str, pd.DataFrame],
    alt_factors: dict[str, pd.DataFrame],
) -> dict[str, pd.DataFrame]:
    """Return a combined factor dictionary without mutating either input."""
    overlap = set(base_factors).intersection(alt_factors)
    if overlap:
        raise ValueError(f"factor name collision: {sorted(overlap)}")
    return {**base_factors, **alt_factors}
