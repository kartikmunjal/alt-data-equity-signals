"""Build stock-level alternative-data signal panels."""

from __future__ import annotations

import numpy as np
import pandas as pd

from altdata_equity_signals.features.sentiment import lexicon_sentiment
from altdata_equity_signals.features.tickers import extract_tickers


def cross_sectional_zscore(panel: pd.DataFrame, winsor_quantile: float = 0.01) -> pd.DataFrame:
    """Winsorize and z-score each date's cross-section."""
    def _z(row: pd.Series) -> pd.Series:
        values = row.astype(float)
        valid = values.dropna()
        if len(valid) < 2:
            return values * np.nan
        lo = valid.quantile(winsor_quantile)
        hi = valid.quantile(1 - winsor_quantile)
        clipped = values.clip(lo, hi)
        std = clipped.std(ddof=0)
        if std == 0 or np.isnan(std):
            return clipped * 0.0
        return (clipped - clipped.mean()) / std

    return panel.apply(_z, axis=1)


def build_wsb_signal_panels(
    posts: pd.DataFrame,
    universe: list[str],
    *,
    text_columns: tuple[str, ...] = ("title", "selftext", "body"),
    timestamp_col: str = "created_utc",
    min_mentions_for_sentiment: int = 1,
) -> dict[str, pd.DataFrame]:
    """Convert WSB-style posts/comments into daily date x ticker signal panels.

    Expected raw columns are intentionally flexible. Kaggle/Pushshift exports commonly
    include `created_utc`, `title`, `selftext`, or `body`; missing text columns are ignored.
    """
    if timestamp_col not in posts.columns:
        raise ValueError(f"missing timestamp column: {timestamp_col}")

    if posts.empty:
        empty = pd.DataFrame(columns=universe, dtype=float)
        return {"mention_z": empty, "sentiment_z": empty, "attention_shock_z": empty}

    frame = posts.copy()
    frame["date"] = _parse_timestamp(frame[timestamp_col])
    frame["text"] = _combine_text_columns(frame, text_columns)
    frame["sentiment"] = frame["text"].map(lexicon_sentiment)
    frame["tickers"] = frame["text"].map(lambda text: extract_tickers(text, universe))

    exploded = frame.explode("tickers").dropna(subset=["tickers"])
    if exploded.empty:
        dates = pd.DatetimeIndex(sorted(frame["date"].dropna().unique()))
        empty = pd.DataFrame(0.0, index=dates, columns=universe)
        return {
            "mention_z": cross_sectional_zscore(empty),
            "sentiment_z": cross_sectional_zscore(empty),
            "attention_shock_z": cross_sectional_zscore(empty),
        }

    mention_counts = (
        exploded.groupby(["date", "tickers"]).size().unstack("tickers").reindex(columns=universe)
    )
    mention_counts = mention_counts.sort_index().fillna(0.0)

    sentiment = (
        exploded.groupby(["date", "tickers"])["sentiment"]
        .mean()
        .unstack("tickers")
        .reindex(index=mention_counts.index, columns=universe)
    )
    sentiment = sentiment.where(mention_counts >= min_mentions_for_sentiment)

    log_mentions = np.log1p(mention_counts)
    trailing = log_mentions.rolling(20, min_periods=3).mean().shift(1)
    attention_shock = log_mentions - trailing

    return {
        "mention_z": cross_sectional_zscore(log_mentions),
        "sentiment_z": cross_sectional_zscore(sentiment),
        "attention_shock_z": cross_sectional_zscore(attention_shock),
    }


def _parse_timestamp(series: pd.Series) -> pd.Series:
    if pd.api.types.is_numeric_dtype(series):
        return pd.to_datetime(series, unit="s", utc=True).dt.tz_convert(None).dt.normalize()
    return pd.to_datetime(series, utc=True).dt.tz_convert(None).dt.normalize()


def _combine_text_columns(frame: pd.DataFrame, columns: tuple[str, ...]) -> pd.Series:
    present = [col for col in columns if col in frame.columns]
    if not present:
        raise ValueError(f"none of the configured text columns exist: {columns}")
    text = frame[present].fillna("").astype(str).agg(" ".join, axis=1)
    return text.str.replace(r"\s+", " ", regex=True).str.strip()
