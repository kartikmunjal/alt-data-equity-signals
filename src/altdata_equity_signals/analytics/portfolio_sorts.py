"""Quintile portfolio diagnostics for stock-level signals."""

from __future__ import annotations

import pandas as pd

from altdata_equity_signals.analytics.returns import align_panel


def quintile_returns(
    signal: pd.DataFrame,
    returns: pd.DataFrame,
    *,
    min_stocks: int = 10,
) -> pd.DataFrame:
    """Equal-weight forward returns by signal quintile plus Q5-Q1 spread."""
    signal, returns = align_panel(signal, returns)
    rows = []
    for date in signal.index:
        frame = pd.concat(
            [signal.loc[date].rename("signal"), returns.loc[date].rename("return")],
            axis=1,
        ).dropna()
        if len(frame) < min_stocks:
            continue
        labels = pd.qcut(frame["signal"].rank(method="first"), 5, labels=False) + 1
        by_q = frame.groupby(labels)["return"].mean()
        row = {f"Q{q}": float(by_q.get(q, float("nan"))) for q in range(1, 6)}
        row["Q5-Q1"] = row["Q5"] - row["Q1"]
        row["date"] = pd.Timestamp(date)
        rows.append(row)

    if not rows:
        return pd.DataFrame(columns=["Q1", "Q2", "Q3", "Q4", "Q5", "Q5-Q1"])
    return pd.DataFrame(rows).set_index("date").sort_index()
