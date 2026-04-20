# Alt-Data Equity Signals

**Core question:** Do public alternative datasets, especially retail-investor attention from Reddit WallStreetBets, contain stock-level information that predicts future equity returns after standard cross-sectional validation?

This repo extends the methodology from
[`Cross-Sectional-Factor-Research`](https://github.com/kartikmunjal/Cross-Sectional-Factor-Research)
to alternative data:

- Build stock-level signal panels from noisy text data.
- Evaluate predictive power with rank IC, ICIR, IC decay, and BH-adjusted p-values.
- Run Fama-MacBeth cross-sectional regressions with Newey-West t-statistics.
- Validate portfolio monotonicity with equal-weight quintile sorts.

The first implemented dataset is Reddit WallStreetBets posts/comments from public Pushshift/Kaggle-style exports. The code also includes a deterministic synthetic data mode so the full pipeline and tests run without proprietary data or API keys.

## Why This Project Exists

Traditional factor work asks whether price, volatility, value, or quality characteristics predict returns. This project asks the same question for alternative data:

```text
raw WSB posts/comments
    -> ticker mentions and sentiment
    -> daily date x ticker signal panels
    -> forward return panels
    -> IC / ICIR / Fama-MacBeth / quintile spreads
```

That mirrors a systematic research workflow: convert messy data into point-in-time stock signals, test whether the signal survives cross-sectional validation, then decide whether it deserves further modeling or portfolio work.

## Implemented Signals

| Signal | Definition | Intuition |
|---|---|---|
| `mention_z` | cross-sectional z-score of log daily ticker mentions | retail attention level |
| `sentiment_z` | cross-sectional z-score of bullish-minus-bearish lexicon score | retail tone |
| `attention_shock_z` | log mentions minus trailing 20-day mean, then z-scored | abnormal attention shock |

All signals are shaped as `date x ticker` DataFrames, matching the factor-panel convention used in the factor research repo.

## Quickstart

```bash
git clone git@github.com:kartikmunjal/alt-data-equity-signals.git
cd alt-data-equity-signals
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# End-to-end smoke test with deterministic synthetic data
python scripts/run_pipeline.py --synthetic --out results/synthetic

# Run tests
pytest -q
```

## Real Data Example

Download a public WSB dataset, for example a Kaggle/Pushshift export with columns such as `created_utc`, `title`, `selftext`, or `body`.

```bash
python scripts/run_pipeline.py \
  --posts data/raw/wsb_posts.csv \
  --tickers GME AMC TSLA NVDA AMD AAPL MSFT PLTR COIN RIVN SPY QQQ \
  --start 2020-12-01 \
  --out results/wsb_retail_attention
```

If you already have a close-price panel:

```bash
python scripts/run_pipeline.py \
  --posts data/raw/wsb_posts.csv \
  --prices data/raw/close_panel.parquet \
  --out results/wsb_retail_attention
```

Expected outputs:

```text
results/
├── ic_summary.csv
├── fama_macbeth.csv
├── quintile_returns.csv
├── signal_mention_z.parquet
├── signal_sentiment_z.parquet
├── signal_attention_shock_z.parquet
└── factor_panels/
    ├── WSB_MENTION_Z.parquet
    ├── WSB_SENTIMENT_Z.parquet
    └── WSB_ATTENTION_SHOCK_Z.parquet
```

## Methodology

**Information Coefficient**

For each date, compute the Spearman rank correlation across stocks:

```text
IC_t = SpearmanCorr_i(signal_i,t, forward_return_i,t->t+h)
```

The summary table reports mean IC, ICIR, t-stat, hit rate, and Benjamini-Hochberg adjusted p-values across tested signal/horizon pairs.

**Fama-MacBeth**

For each date, run a cross-sectional regression:

```text
r_i,t->t+h = alpha_t + beta_t * signal_i,t + epsilon_i,t
```

Then test whether the average beta is different from zero using Newey-West standard errors on the time series of betas.

**Quintile Sorts**

Sort stocks into five equal groups by signal each date. The reported `Q5-Q1` spread tests whether high-signal stocks outperform low-signal stocks monotonically.

## Project Structure

```text
src/altdata_equity_signals/
├── analytics/       # IC, Fama-MacBeth, forward returns, quintile sorts
├── data/            # deterministic synthetic fixture
├── features/        # ticker extraction, sentiment, signal panels
├── ingestion/       # WSB and price loaders
├── integration.py   # factor-panel export/load adapters
└── pipeline.py      # end-to-end research workflow
scripts/
└── run_pipeline.py
docs/
├── CONNECTIONS.md
└── DATASETS.md
tests/
```

## Connections

- `Cross-Sectional-Factor-Research`: same panel interface and same IC/Fama-MacBeth evaluation logic.
- `securities-lending`: natural next merge point for retail attention, short interest, borrow stress, and squeeze-risk research.
- `HFT-trades-local`: downstream intraday execution extension, where daily retail-attention signals can gate bar-level entries.
- `options-vol-research`: follow-up use case, testing whether attention shocks predict realized volatility or implied-vol repricing.

See [docs/CONNECTIONS.md](docs/CONNECTIONS.md) for the integration plan.

## Data Notes

The repository does not commit raw Reddit or price data. Put local data under `data/raw/`; outputs go under `results/`.

See [docs/DATASETS.md](docs/DATASETS.md) for public dataset options and schema expectations.
