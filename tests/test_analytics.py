import numpy as np
import pandas as pd

from altdata_equity_signals.analytics.fama_macbeth import FamaMacBeth
from altdata_equity_signals.analytics.ic_analysis import compute_ic_series, summarize_ic


def test_ic_series_detects_rank_relation():
    dates = pd.bdate_range("2024-01-01", periods=8)
    tickers = [f"T{i}" for i in range(12)]
    signal = pd.DataFrame(np.tile(np.arange(12), (8, 1)), index=dates, columns=tickers)
    returns = signal / 100.0

    ic = compute_ic_series(signal, returns, min_stocks=10)
    result = summarize_ic(ic, "test", 1)

    assert result.mean_ic > 0.99
    assert result.n_periods == 8


def test_fama_macbeth_positive_slope():
    dates = pd.bdate_range("2024-01-01", periods=12)
    tickers = [f"T{i}" for i in range(15)]
    base = pd.DataFrame(np.tile(np.linspace(-1, 1, 15), (12, 1)), index=dates, columns=tickers)
    returns = 0.01 * base

    model = FamaMacBeth(min_stocks=10).fit(base, returns)
    summary = model.summary()

    assert summary.loc["signal", "mean_lambda"] > 0
    assert summary.loc["signal", "n_periods"] == 12
