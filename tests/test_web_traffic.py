import pandas as pd

from altdata_equity_signals.features.web_traffic import build_web_traffic_signal_panels
from altdata_equity_signals.ingestion.web_traffic import load_web_traffic


def test_load_web_traffic_normalizes_schema(tmp_path):
    path = tmp_path / "traffic.csv"
    pd.DataFrame(
        {
            "date": ["2024-01-15", "2024-01-31"],
            "ticker": ["amzn", "SHOP"],
            "visits": ["1000", "2000"],
        }
    ).to_csv(path, index=False)

    frame = load_web_traffic(path)

    assert list(frame.columns) == ["date", "ticker", "visits"]
    assert frame["ticker"].tolist() == ["AMZN", "SHOP"]
    assert frame["date"].dt.is_month_end.all()


def test_build_web_traffic_signal_panels_daily_aligns_with_lag():
    traffic = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-31", "2024-01-31", "2024-02-29", "2024-02-29"]),
            "ticker": ["AMZN", "SHOP", "AMZN", "SHOP"],
            "visits": [1000, 2000, 1300, 1800],
        }
    )
    daily_index = pd.bdate_range("2024-02-01", "2024-03-15")

    panels = build_web_traffic_signal_panels(
        traffic,
        universe=["AMZN", "SHOP"],
        daily_index=daily_index,
        publication_lag_days=7,
    )

    assert set(panels) == {"web_traffic_level_z", "web_traffic_growth_z", "web_traffic_shock_z"}
    assert panels["web_traffic_level_z"].index.equals(daily_index)
    assert panels["web_traffic_level_z"].loc["2024-02-01":"2024-02-06"].isna().all().all()
    assert panels["web_traffic_level_z"].loc["2024-02-07"].notna().any()
