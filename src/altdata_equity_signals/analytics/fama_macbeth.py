"""Fama-MacBeth cross-sectional regressions with Newey-West t-statistics."""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

from altdata_equity_signals.analytics.returns import align_panel


class FamaMacBeth:
    """Run per-date cross-sectional OLS and test the average signal slope."""

    def __init__(self, nw_lags: int = 4, min_stocks: int = 10):
        self.nw_lags = nw_lags
        self.min_stocks = min_stocks
        self.lambdas_: pd.DataFrame | None = None
        self.r2_: pd.Series | None = None

    def fit(
        self,
        signal: pd.DataFrame,
        returns: pd.DataFrame,
        controls: dict[str, pd.DataFrame] | None = None,
    ) -> "FamaMacBeth":
        signal, returns = align_panel(signal, returns)
        controls = controls or {}

        rows: list[np.ndarray] = []
        dates: list[pd.Timestamp] = []
        r2s: list[float] = []
        columns = ["alpha", "signal"] + list(controls)

        for date in signal.index:
            frame = pd.concat(
                [returns.loc[date].rename("ret"), signal.loc[date].rename("signal")],
                axis=1,
            )
            for name, panel in controls.items():
                if date in panel.index:
                    frame[name] = panel.loc[date].reindex(frame.index)
            frame = frame.dropna()
            if len(frame) < self.min_stocks:
                continue

            x_cols = ["signal"] + list(controls)
            x = frame[x_cols].apply(_zscore, axis=0).fillna(0.0).to_numpy()
            x = np.column_stack([np.ones(len(frame)), x])
            y = frame["ret"].to_numpy()

            try:
                beta, *_ = np.linalg.lstsq(x, y, rcond=None)
            except np.linalg.LinAlgError:
                continue

            y_hat = x @ beta
            ss_res = float(np.sum((y - y_hat) ** 2))
            ss_tot = float(np.sum((y - y.mean()) ** 2))
            r2s.append(1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0)
            rows.append(beta)
            dates.append(pd.Timestamp(date))

        if not rows:
            raise ValueError("No valid Fama-MacBeth cross-sections found.")

        self.lambdas_ = pd.DataFrame(rows, index=dates, columns=columns)
        self.r2_ = pd.Series(r2s, index=dates, name="r2")
        return self

    def summary(self) -> pd.DataFrame:
        if self.lambdas_ is None:
            raise RuntimeError("call fit() before summary()")

        rows = []
        for coefficient in self.lambdas_.columns:
            series = self.lambdas_[coefficient].dropna()
            n = len(series)
            mean = float(series.mean())
            std = float(series.std(ddof=1)) if n > 1 else np.nan
            se_fm = std / np.sqrt(n) if n > 1 else np.nan
            t_fm = mean / se_fm if se_fm and se_fm > 0 else np.nan
            se_nw = _newey_west_se(series.to_numpy(), self.nw_lags)
            t_nw = mean / se_nw if se_nw > 0 else np.nan
            p_nw = 2 * stats.t.sf(abs(t_nw), df=n - 1) if n > 1 and pd.notna(t_nw) else np.nan
            rows.append(
                {
                    "coefficient": coefficient,
                    "mean_lambda": mean,
                    "std_lambda": std,
                    "t_stat_fm": t_fm,
                    "t_stat_nw": t_nw,
                    "p_value_nw": p_nw,
                    "significant": bool(abs(t_nw) > 2.0) if pd.notna(t_nw) else False,
                    "mean_r2": float(self.r2_.mean()) if self.r2_ is not None else np.nan,
                    "n_periods": n,
                }
            )
        return pd.DataFrame(rows).set_index("coefficient")


def run_fama_macbeth_table(
    signals: dict[str, pd.DataFrame],
    returns: pd.DataFrame,
    controls: dict[str, pd.DataFrame] | None = None,
    *,
    nw_lags: int = 4,
    min_stocks: int = 10,
) -> pd.DataFrame:
    """Run Fama-MacBeth for every signal and return one row per signal slope."""
    rows = []
    for name, panel in signals.items():
        try:
            model = FamaMacBeth(nw_lags=nw_lags, min_stocks=min_stocks).fit(panel, returns, controls)
        except ValueError:
            continue
        row = model.summary().loc["signal"].to_dict()
        row["signal"] = name
        rows.append(row)
    if not rows:
        return pd.DataFrame(
            columns=[
                "mean_lambda",
                "std_lambda",
                "t_stat_fm",
                "t_stat_nw",
                "p_value_nw",
                "significant",
                "mean_r2",
                "n_periods",
            ]
        )
    return pd.DataFrame(rows).set_index("signal").sort_values("t_stat_nw", key=abs, ascending=False)


def _zscore(series: pd.Series) -> pd.Series:
    std = series.std(ddof=0)
    if std == 0 or pd.isna(std):
        return series * 0.0
    return (series - series.mean()) / std


def _newey_west_se(values: np.ndarray, lags: int) -> float:
    values = np.asarray(values, dtype=float)
    values = values[~np.isnan(values)]
    n = len(values)
    if n <= 1:
        return np.nan

    demeaned = values - values.mean()
    gamma0 = float(np.sum(demeaned * demeaned) / n)
    var = gamma0
    for lag in range(1, min(lags, n - 1) + 1):
        weight = 1.0 - lag / (lags + 1.0)
        gamma = float(np.sum(demeaned[lag:] * demeaned[:-lag]) / n)
        var += 2.0 * weight * gamma
    return float(np.sqrt(max(var, 0.0) / n))
