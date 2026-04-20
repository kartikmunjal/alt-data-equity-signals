"""Ticker extraction for noisy retail-investor text."""

from __future__ import annotations

import re
from collections.abc import Iterable

CASHTAG_RE = re.compile(r"(?<![A-Z0-9])\$([A-Z]{1,5})(?![A-Z0-9])")
UPPER_RE = re.compile(r"(?<![A-Z0-9])([A-Z]{2,5})(?![A-Z0-9])")

# Common words that collide with listed tickers. Keep this conservative; the goal is
# to avoid obvious false positives without removing real cashtags like "$ON".
DEFAULT_STOPWORDS = {
    "A",
    "ALL",
    "AM",
    "ARE",
    "ATH",
    "BE",
    "BIG",
    "CEO",
    "DD",
    "ETF",
    "EV",
    "FOR",
    "GDP",
    "GO",
    "HOLD",
    "IMO",
    "IPO",
    "IT",
    "LOL",
    "MOON",
    "NEXT",
    "ON",
    "ONE",
    "OR",
    "PM",
    "RH",
    "SEC",
    "THE",
    "USA",
    "YOLO",
}


def extract_tickers(
    text: str | None,
    universe: Iterable[str],
    *,
    stopwords: set[str] | None = None,
    include_plain_uppercase: bool = True,
) -> list[str]:
    """Extract ticker mentions from a post/comment.

    Cashtags are trusted when they are in the supplied universe. Plain uppercase
    tokens are accepted only if they are in the universe and not in the stoplist.
    """
    if not text:
        return []

    universe_set = {ticker.upper() for ticker in universe}
    stop = DEFAULT_STOPWORDS if stopwords is None else stopwords
    text = str(text).upper()

    tickers: set[str] = set()
    for match in CASHTAG_RE.finditer(text):
        ticker = match.group(1)
        if ticker in universe_set:
            tickers.add(ticker)

    if include_plain_uppercase:
        for match in UPPER_RE.finditer(text):
            ticker = match.group(1)
            if ticker in universe_set and ticker not in stop:
                tickers.add(ticker)

    return sorted(tickers)
