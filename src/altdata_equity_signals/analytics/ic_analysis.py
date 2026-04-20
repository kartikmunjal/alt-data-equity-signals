"""Information Coefficient analysis for alternative-data equity signals."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import stats

from altdata_equity_signals.analytics.returns import align_panel


@dataclass(frozen=True)
class ICResult:
    signal: str
    horizon: int
    mean_ic: float
    std_ic: float
    icir: float
    t_stat: float
    p_value: float
    pct_positive: float
    n_periods: int


def compute_ic_series(
    signal: pd.DataFrame,
    returns: pd.DataFrame,
    *,
    min_stocks: int = 10,
) -> pd.Series:
    """Compute period-by-period Spearman rank IC."""
    signal, returns = align_panel(signal, returns)
    values: dict[pd.Timestamp, float] = {}

    for date in signal.index:
        joined = pd.concat(
            [signal.loc[date].rename("signal"), returns.loc[date].rename("return")],
            axis=1,
        ).dropna()
        if len(joined) < min_stocks:
            continue
        ic = joined["signal"].corr(joined["return"], method="spearman")
        if pd.notna(ic):
            values[pd.Timestamp(date)] = float(ic)

    return pd.Series(values, name="ic").sort_index()


def summarize_ic(ic: pd.Series, signal_name: str, horizon: int) -> ICResult:
    """Summarize an IC time series into mean IC, ICIR, t-stat, and hit rate."""
    ic = ic.dropna()
    n = len(ic)
    if n == 0:
        return ICResult(signal_name, horizon, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, 0)

    mean_ic = float(ic.mean())
    std_ic = float(ic.std(ddof=1)) if n > 1 else 0.0
    icir = mean_ic / std_ic if std_ic > 0 else np.nan
    t_stat = icir * np.sqrt(n) if pd.notna(icir) else np.nan
    p_value = 2 * stats.t.sf(abs(t_stat), df=n - 1) if n > 1 and pd.notna(t_stat) else np.nan

    return ICResult(
        signal=signal_name,
        horizon=horizon,
        mean_ic=mean_ic,
        std_ic=std_ic,
        icir=float(icir),
        t_stat=float(t_stat),
        p_value=float(p_value),
        pct_positive=float((ic > 0).mean()),
        n_periods=n,
    )


def compute_ic_table(
    signals: dict[str, pd.DataFrame],
    forward_returns: dict[int, pd.DataFrame],
    *,
    min_stocks: int = 10,
) -> pd.DataFrame:
    """Evaluate each signal/horizon pair and apply Benjamini-Hochberg p-values."""
    rows = []
    for signal_name, panel in signals.items():
        for horizon, returns in forward_returns.items():
            ic = compute_ic_series(panel, returns, min_stocks=min_stocks)
            rows.append(summarize_ic(ic, signal_name, horizon).__dict__)

    table = pd.DataFrame(rows)
    if table.empty:
        return table

    table = table.sort_values("p_value", na_position="last").reset_index(drop=True)
    valid = table["p_value"].notna()
    m = int(valid.sum())
    table["p_value_bh"] = np.nan
    if m:
        ranks = np.arange(1, m + 1)
        table.loc[valid, "p_value_bh"] = (table.loc[valid, "p_value"].to_numpy() * m / ranks).clip(
            max=1.0
        )
    return table.sort_values(["signal", "horizon"]).reset_index(drop=True)
