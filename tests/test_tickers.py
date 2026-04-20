from altdata_equity_signals.features.tickers import extract_tickers


def test_extract_tickers_prefers_cashtags_and_filters_common_words():
    universe = ["AAPL", "TSLA", "ON", "GME"]

    assert extract_tickers("$TSLA calls and AAPL breakout ON watch", universe) == ["AAPL", "TSLA"]
    assert extract_tickers("$ON is valid as a cashtag", universe) == ["ON"]
    assert extract_tickers("GME squeeze setup", universe) == ["GME"]
