"""Deterministic synthetic data for demos and CI tests."""

from __future__ import annotations

import numpy as np
import pandas as pd


def make_synthetic_altdata(
    *,
    n_days: int = 90,
    tickers: list[str] | None = None,
    seed: int = 7,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Create WSB-like posts and close prices with a weak embedded attention signal."""
    rng = np.random.default_rng(seed)
    tickers = tickers or [
        "AAPL",
        "AMD",
        "AMZN",
        "GME",
        "META",
        "MSFT",
        "NVDA",
        "PLTR",
        "TSLA",
        "SPY",
        "QQQ",
        "NFLX",
        "SHOP",
        "COIN",
        "RIVN",
    ]
    dates = pd.bdate_range("2021-01-04", periods=n_days)

    attention = pd.DataFrame(
        rng.normal(0, 1, size=(len(dates), len(tickers))),
        index=dates,
        columns=tickers,
    )
    returns = pd.DataFrame(
        rng.normal(0.0003, 0.025, size=(len(dates), len(tickers))),
        index=dates,
        columns=tickers,
    )
    returns += 0.006 * attention.shift(1).fillna(0.0)
    close = 100.0 * (1.0 + returns).cumprod()

    rows = []
    for date in dates:
        daily_attention = attention.loc[date]
        mention_prob = 1 / (1 + np.exp(-daily_attention))
        for ticker, prob in mention_prob.items():
            n_mentions = rng.poisson(0.8 + 3.5 * prob)
            for _ in range(n_mentions):
                bullish = daily_attention[ticker] + rng.normal(0, 1) > 0
                word = rng.choice(["bullish", "breakout", "calls", "upside"] if bullish else ["puts", "sell", "weak", "risk"])
                rows.append(
                    {
                        "created_utc": int(pd.Timestamp(date).timestamp()) + int(rng.integers(0, 86400)),
                        "title": f"${ticker} {word} setup",
                        "selftext": f"I am {'long' if bullish else 'bearish'} {ticker} after this move.",
                    }
                )

    traffic_rows = []
    month_ends = pd.date_range(dates.min(), dates.max(), freq="ME")
    for month_end in month_ends:
        month_ix = dates.get_indexer([dates[dates <= month_end][-1]])[0]
        for ticker in tickers:
            base_visits = 1_000_000 + 150_000 * tickers.index(ticker)
            attention_boost = max(0.0, attention.loc[dates[month_ix], ticker]) * 75_000
            noise = rng.normal(0, 50_000)
            traffic_rows.append(
                {
                    "date": month_end,
                    "ticker": ticker,
                    "visits": max(10_000, base_visits + attention_boost + noise),
                    "source": "synthetic_similarweb",
                }
            )

    posts = pd.DataFrame(rows).sort_values("created_utc").reset_index(drop=True)
    web_traffic = pd.DataFrame(traffic_rows)
    return posts, close, web_traffic
