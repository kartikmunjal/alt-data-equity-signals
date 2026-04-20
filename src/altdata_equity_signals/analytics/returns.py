"""Return-panel utilities shared by IC and Fama-MacBeth research."""

from __future__ import annotations

import pandas as pd


def compute_forward_returns(close: pd.DataFrame, horizons: list[int]) -> dict[int, pd.DataFrame]:
    """Return dict of horizon -> forward simple returns aligned at signal date t."""
    close = close.sort_index()
    return {h: close.shift(-h) / close - 1.0 for h in horizons}


def align_panel(signal: pd.DataFrame, returns: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Align signal and return panels on common dates and tickers."""
    common_dates = signal.index.intersection(returns.index)
    common_tickers = signal.columns.intersection(returns.columns)
    return signal.loc[common_dates, common_tickers], returns.loc[common_dates, common_tickers]
