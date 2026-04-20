"""End-to-end alternative-data signal evaluation pipeline."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from altdata_equity_signals.analytics.fama_macbeth import run_fama_macbeth_table
from altdata_equity_signals.analytics.ic_analysis import compute_ic_table
from altdata_equity_signals.analytics.portfolio_sorts import quintile_returns
from altdata_equity_signals.analytics.returns import compute_forward_returns
from altdata_equity_signals.data.synthetic import make_synthetic_altdata
from altdata_equity_signals.features.panels import build_wsb_signal_panels
from altdata_equity_signals.features.web_traffic import build_web_traffic_signal_panels
from altdata_equity_signals.ingestion.prices import download_close_panel, load_close_panel
from altdata_equity_signals.ingestion.wsb import load_wsb_posts
from altdata_equity_signals.ingestion.web_traffic import load_web_traffic
from altdata_equity_signals.integration import export_factor_panels


def run_pipeline(
    *,
    posts_path: str | Path | None = None,
    prices_path: str | Path | None = None,
    web_traffic_path: str | Path | None = None,
    tickers: list[str] | None = None,
    start: str = "2021-01-01",
    end: str | None = None,
    horizons: list[int] | None = None,
    output_dir: str | Path = "results",
    use_synthetic: bool = False,
    min_stocks: int = 10,
) -> dict[str, pd.DataFrame]:
    """Run data -> signals -> IC/FM/quintile analysis."""
    horizons = horizons or [1, 5, 10, 21]
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if use_synthetic:
        posts, close, synthetic_web_traffic = make_synthetic_altdata()
        universe = list(close.columns)
    else:
        if posts_path is None:
            raise ValueError("posts_path is required unless use_synthetic=True")
        posts = load_wsb_posts(posts_path)
        if prices_path is not None:
            close = load_close_panel(prices_path)
        else:
            if not tickers:
                raise ValueError("tickers are required when prices_path is not supplied")
            close = download_close_panel(tickers, start=start, end=end)
        universe = tickers or list(close.columns)
        synthetic_web_traffic = None

    signals = build_wsb_signal_panels(posts, universe=universe)
    if web_traffic_path is not None or synthetic_web_traffic is not None:
        web_traffic = synthetic_web_traffic if synthetic_web_traffic is not None else load_web_traffic(web_traffic_path)
        signals.update(
            build_web_traffic_signal_panels(
                web_traffic,
                universe=universe,
                daily_index=close.index,
            )
        )
    forward_returns = compute_forward_returns(close, horizons)

    ic_table = compute_ic_table(signals, forward_returns, min_stocks=min_stocks)
    primary_horizon = 5 if 5 in forward_returns else horizons[0]
    fm_table = run_fama_macbeth_table(
        signals,
        forward_returns[primary_horizon],
        min_stocks=min_stocks,
    )

    best_signal = _select_best_signal(ic_table)
    quintiles = quintile_returns(
        signals[best_signal],
        forward_returns[primary_horizon],
        min_stocks=min_stocks,
    )

    ic_table.to_csv(output_dir / "ic_summary.csv", index=False)
    fm_table.to_csv(output_dir / "fama_macbeth.csv")
    quintiles.to_csv(output_dir / "quintile_returns.csv")
    for name, panel in signals.items():
        panel.to_parquet(output_dir / f"signal_{name}.parquet")
    export_factor_panels(signals, output_dir / "factor_panels")

    return {
        "ic": ic_table,
        "fama_macbeth": fm_table,
        "quintiles": quintiles,
    }


def _select_best_signal(ic_table: pd.DataFrame) -> str:
    if ic_table.empty or ic_table["icir"].isna().all():
        return "mention_z"
    ranked = ic_table.assign(abs_icir=ic_table["icir"].abs()).sort_values("abs_icir", ascending=False)
    return str(ranked.iloc[0]["signal"])
