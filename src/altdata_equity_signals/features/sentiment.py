"""Small finance-oriented sentiment lexicon for reproducible baselines."""

from __future__ import annotations

import re

POSITIVE_WORDS = {
    "beat",
    "beats",
    "breakout",
    "bull",
    "bullish",
    "buy",
    "calls",
    "cheap",
    "gain",
    "gains",
    "growth",
    "long",
    "moon",
    "outperform",
    "rally",
    "rip",
    "squeeze",
    "strong",
    "undervalued",
    "upside",
}

NEGATIVE_WORDS = {
    "bagholder",
    "bankrupt",
    "bear",
    "bearish",
    "crash",
    "debt",
    "dilution",
    "downside",
    "dump",
    "fraud",
    "miss",
    "overvalued",
    "puts",
    "risk",
    "sell",
    "short",
    "weak",
}

TOKEN_RE = re.compile(r"[A-Za-z']+")


def lexicon_sentiment(text: str | None) -> float:
    """Return a normalized bullish-minus-bearish sentiment score."""
    if not text:
        return 0.0
    tokens = [token.lower() for token in TOKEN_RE.findall(str(text))]
    if not tokens:
        return 0.0

    pos = sum(token in POSITIVE_WORDS for token in tokens)
    neg = sum(token in NEGATIVE_WORDS for token in tokens)
    return (pos - neg) / max(1, pos + neg)
