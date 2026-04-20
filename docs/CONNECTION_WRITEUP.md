# Cross-Repo Connection Write-Up

## Executive Summary

`alt-data-equity-signals` is the upstream research repo for public alternative
datasets. It owns raw WSB/retail-attention data ingestion, ticker extraction,
sentiment scoring, signal construction, and standalone IC/Fama-MacBeth validation.

The connected repos consume the finished factor panels:

```text
alt-data-equity-signals/results/<run>/factor_panels/
├── WSB_MENTION_Z.parquet
├── WSB_SENTIMENT_Z.parquet
└── WSB_ATTENTION_SHOCK_Z.parquet
```

Each file is `date x ticker`, which is the shared contract across all connected
research code.

The alt-data repo now covers two source types:

- social attention: WSB ticker mentions, sentiment, and abnormal attention
- operational data: monthly web traffic level, growth, and abnormal traffic

## Connection 1: Cross-Sectional-Factor-Research

**Purpose:** compare alt-data factors directly against traditional equity
factors.

Implemented connection:

- Added `src/factors/altdata.py`.
- Added `scripts/run_full_pipeline.py --alt-factor-dir`.
- Added alt-data factor metadata for:
  - `WSB_MENTION_Z`
  - `WSB_SENTIMENT_Z`
  - `WSB_ATTENTION_SHOCK_Z`
  - `WSB_WEB_TRAFFIC_LEVEL_Z`
  - `WSB_WEB_TRAFFIC_GROWTH_Z`
  - `WSB_WEB_TRAFFIC_SHOCK_Z`
- Added `docs/ALT_DATA_CONNECTION.md`.

Workflow:

```bash
cd alt-data-equity-signals
python scripts/run_pipeline.py \
  --posts data/raw/wsb_posts.csv \
  --prices data/raw/close_panel.parquet \
  --out results/wsb_retail_attention

cd ../Cross-Sectional-Factor-Research
python scripts/run_full_pipeline.py \
  --alt-factor-dir ../alt-data-equity-signals/results/wsb_retail_attention/factor_panels \
  --save
```

Research question:

> Do retail attention and operational web traffic add predictive power versus
> momentum, volatility, value, quality, and liquidity factors?

## Connection 2: securities-lending

**Purpose:** combine retail crowding with short crowding.

Implemented connection:

- Added `src/securities_lending/features/retail_attention.py`.
- Added `scripts/run_analysis.py --alt-factor-dir`.
- Added retail signals and interaction terms to IC, portfolio-sort, and
  Fama-MacBeth analysis:
  - `wsb_mention_z`
  - `wsb_sentiment_z`
  - `wsb_attention_shock_z`
  - `borrow_stress_x_wsb_attention`
  - `dtc_x_wsb_attention`
  - `short_pressure_x_wsb_sentiment`
- Extended the squeeze detector to use WSB features when present.
- Added a dedicated interaction backtest that reports annualized spread,
  Sharpe, hit rate, and top-bucket event hit rate.
- Added `docs/ALT_DATA_CONNECTION.md`.

Workflow:

```bash
cd securities-lending
python scripts/run_analysis.py \
  --features data/processed/features.parquet \
  --alt-factor-dir ../alt-data-equity-signals/results/wsb_retail_attention/factor_panels \
  --output-dir data/results/with_retail_attention
```

Dedicated interaction backtest:

```bash
python scripts/run_retail_squeeze_backtest.py \
  --features data/processed/features.parquet \
  --alt-factor-dir ../alt-data-equity-signals/results/wsb_retail_attention/factor_panels \
  --signal borrow_stress_x_wsb_attention
```

Research question:

> Are crowded shorts with abnormal WSB attention more likely to produce positive
> forward-return dislocations or squeeze events?

## Optional Connection: HFT-trades-local

No code connection was added yet. This repo should remain downstream execution
research, not signal discovery.

Best future link:

- Generate daily WSB signal panels after market close.
- Carry signals into the next trading day.
- Use them as filters/features for intraday bar-ML entries.
- Compare turnover, hit rate, and cost-adjusted returns with and without the
  retail-attention gate.

## Optional Connection: options-vol-research

No code connection was added yet. The correct extension is volatility-focused:

- Test whether `WSB_ATTENTION_SHOCK_Z` predicts realized volatility.
- Test whether it predicts implied-vol richening.
- Use it for single-stock straddle selection or VRP regime filters.

## Not Connected: future-options

The futures carry repo is intentionally left separate. Equity social/retail
attention does not naturally map to CME futures carry unless a new macro alt-data
dataset is introduced.

## Ownership Boundary

The clean dependency direction is:

```text
alt-data-equity-signals
    -> Cross-Sectional-Factor-Research
    -> securities-lending
    -> optional HFT/options-vol downstream experiments
```

Downstream repos should not reimplement raw Reddit ingestion or ticker parsing.
They should consume the exported `WSB_*.parquet` factor panels.
