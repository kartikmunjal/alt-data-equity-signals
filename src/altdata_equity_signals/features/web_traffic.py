"""Operational web-traffic signal construction."""

from __future__ import annotations

import numpy as np
import pandas as pd

from altdata_equity_signals.features.panels import cross_sectional_zscore


def build_web_traffic_signal_panels(
    traffic: pd.DataFrame,
    universe: list[str],
    *,
    daily_index: pd.DatetimeIndex | None = None,
    publication_lag_days: int = 7,
) -> dict[str, pd.DataFrame]:
    """Build operational factor panels from monthly web visits.

    The publication lag is a point-in-time guardrail: month-end traffic for
    January is treated as available only after a configurable delay.
    """
    if traffic.empty:
        empty = pd.DataFrame(columns=universe, dtype=float)
        return {
            "web_traffic_level_z": empty,
            "web_traffic_growth_z": empty,
            "web_traffic_shock_z": empty,
        }

    frame = traffic.copy()
    frame["date"] = pd.to_datetime(frame["date"]).dt.to_period("M").dt.to_timestamp("M")
    frame["ticker"] = frame["ticker"].astype(str).str.upper()

    visits = (
        frame.groupby(["date", "ticker"])["visits"]
        .sum()
        .unstack("ticker")
        .reindex(columns=[ticker.upper() for ticker in universe])
        .sort_index()
    )

    log_visits = np.log1p(visits)
    level = cross_sectional_zscore(log_visits)
    growth = cross_sectional_zscore(log_visits.diff(1))
    trailing = log_visits.rolling(6, min_periods=3).mean().shift(1)
    shock = cross_sectional_zscore(log_visits - trailing)

    signals = {
        "web_traffic_level_z": level,
        "web_traffic_growth_z": growth,
        "web_traffic_shock_z": shock,
    }

    available_dates = pd.DatetimeIndex(signals["web_traffic_level_z"].index) + pd.Timedelta(
        days=publication_lag_days
    )
    signals = {
        name: panel.set_index(available_dates)
        for name, panel in signals.items()
    }

    if daily_index is not None:
        signals = {
            name: panel.reindex(pd.DatetimeIndex(daily_index).sort_values(), method="ffill")
            for name, panel in signals.items()
        }

    return signals
