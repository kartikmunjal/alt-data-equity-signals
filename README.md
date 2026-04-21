# Alt-Data Equity Signals

**Core question:** Do public alternative datasets, including retail-investor attention and operational web-traffic data, contain stock-level information that predicts future equity returns after standard cross-sectional validation?

This repo extends the methodology from
[`Cross-Sectional-Factor-Research`](https://github.com/kartikmunjal/Cross-Sectional-Factor-Research)
to alternative data:

- Build stock-level signal panels from noisy text data.
- Evaluate predictive power with rank IC, ICIR, IC decay, and BH-adjusted p-values.
- Run Fama-MacBeth cross-sectional regressions with Newey-West t-statistics.
- Validate portfolio monotonicity with equal-weight quintile sorts.

The first implemented dataset is Reddit WallStreetBets posts/comments from public Pushshift/Kaggle-style exports. The second implemented dataset is monthly web traffic for operational demand proxies, compatible with SimilarWeb-style exports. The code also includes a deterministic synthetic data mode so the full pipeline and tests run without proprietary data or API keys.

## Why This Project Exists

Traditional factor work asks whether price, volatility, value, or quality characteristics predict returns. This project asks the same question for alternative data:

```text
raw WSB posts/comments
    -> ticker mentions and sentiment
    -> daily date x ticker signal panels
monthly web traffic
    -> demand growth and abnormal traffic panels
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
| `web_traffic_level_z` | cross-sectional z-score of log monthly visits | operational scale / consumer demand |
| `web_traffic_growth_z` | cross-sectional z-score of monthly traffic growth | demand acceleration |
| `web_traffic_shock_z` | traffic minus trailing baseline, then z-scored | abnormal demand shock |

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

The repo has been run on the free MIT-licensed Figshare dataset
[Wallstreetbets Reddit Data (10/2020 - 04/2022)](https://figshare.com/articles/dataset/Wallstreetbets_Reddit_Data_10_2020_-_04_2022_/22010699)
plus free Yahoo/yfinance prices.

```bash
python scripts/prepare_figshare_wsb.py \
  --root data/raw/free_sources/extracted \
  --out data/processed/figshare_wsb_posts.parquet \
  --start 2020-10-01 \
  --end 2022-04-30

python scripts/run_pipeline.py \
  --posts data/processed/figshare_wsb_posts.parquet \
  --tickers GME AMC AAPL MSFT NOK TSLA \
  --start 2020-10-01 \
  --end 2022-05-31 \
  --min-stocks 3 \
  --out results/real_figshare_wsb
```

That run used **229,638** real WSB rows from **2020-10-01 to 2022-04-29** across
`AAPL`, `AMC`, `GME`, `MSFT`, `NOK`, and `TSLA`.

### Actual Real-Data Results

Output directory: `results/real_figshare_wsb/`

| Signal | Horizon | Mean IC | ICIR | t-stat | BH p-value | Periods | Interpretation |
|---|---:|---:|---:|---:|---:|---:|---|
| `mention_z` | 10d | -0.0876 | -0.1737 | -3.40 | 0.0088 | 384 | higher WSB mention intensity predicted underperformance |
| `mention_z` | 21d | -0.0709 | -0.1290 | -2.52 | 0.0720 | 383 | negative after FDR, weaker than 10d |
| `attention_shock_z` | 5d | 0.0340 | 0.0693 | 1.35 | 0.3531 | 382 | not significant |
| `sentiment_z` | 1d | 0.0514 | 0.0897 | 1.55 | 0.2955 | 297 | not significant |

Fama-MacBeth on the standalone alt-data repo did **not** find a Newey-West significant
WSB coefficient:

| Signal | Mean Lambda | NW t-stat | p-value | Periods |
|---|---:|---:|---:|---:|
| `sentiment_z` | -0.0174 | -1.43 | 0.1537 | 298 |
| `mention_z` | 0.0138 | 1.31 | 0.1919 | 384 |
| `attention_shock_z` | 0.0132 | 1.28 | 0.2024 | 382 |

The full-universe quintile sort selected the best ICIR signal and produced a positive
5-day `Q5-Q1` spread of **0.0501**, but this is dominated by the meme-stock sample
and should not be read as a production portfolio result.

### GME/AMC Sensitivity

I also reran the same pipeline excluding the two most event-driven meme names:

```bash
python scripts/run_pipeline.py \
  --posts data/processed/figshare_wsb_posts.parquet \
  --prices data/processed/close_figshare_universe.parquet \
  --tickers AAPL MSFT NOK TSLA \
  --min-stocks 3 \
  --out results/real_figshare_wsb_ex_gme_amc
```

Result: the WSB effect weakens materially. `mention_z` at 21 days remains negative
but only marginal (`mean_ic=-0.0695`, `ICIR=-0.1045`, `p=0.0502`, BH p-value
`0.6019`). `attention_shock_z` flips positive at 21 days (`mean_ic=0.0255`) and is
not significant. This confirms the six-name WSB run is narrow and heavily influenced
by the GME/AMC episode.

### Investment Thesis From The Result

The strongest real-data finding is contrarian: abnormal retail attention and high WSB
mention intensity are associated with later underperformance, especially around the
10- to 21-day horizon. A plausible thesis is that retail attention temporarily inflates
prices, after which crowded attention mean-reverts. This is consistent with the investor
attention literature, including Da, Engelberg, and Gao (2011), but this repo treats it
as a research hypothesis rather than a tradable strategy because the current public
sample is small and event-biased.

### Point-In-Time Status

WSB signals are timestamped from Reddit `created_utc` values and aggregated by calendar
date. The current reported runs align signal date `T` with forward close-to-close returns
from `T` to `T+h`, so they are **research diagnostics, not production execution results**.
The intended production convention is: compute the signal after market close on date `T`,
first trade at the next session, and evaluate returns from `T+1` onward. A next-session
execution lag should be enforced before treating these ICs as tradable.

### Generic WSB CSV Example

For another public WSB dataset, use columns such as `created_utc`, `title`, `selftext`,
or `body`.

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
  --web-traffic data/raw/monthly_web_traffic.csv \
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
    ├── WSB_ATTENTION_SHOCK_Z.parquet
    ├── WSB_WEB_TRAFFIC_LEVEL_Z.parquet
    ├── WSB_WEB_TRAFFIC_GROWTH_Z.parquet
    └── WSB_WEB_TRAFFIC_SHOCK_Z.parquet
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
├── CONNECTION_WRITEUP.md
├── DATASETS.md
└── VENDOR_EVALUATION.md
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

The web-traffic feature code and schema are implemented, but I did **not** run a real
Similarweb/web-traffic result because no free bulk historical monthly traffic file was
available locally and the public free tiers generally require account/API access or
provide rank-style endpoints rather than ticker-level history.

See [docs/DATASETS.md](docs/DATASETS.md) for public dataset options and schema expectations, and [docs/VENDOR_EVALUATION.md](docs/VENDOR_EVALUATION.md) for the data-quality and vendor diligence framework.

Additional research write-ups:

- [Retail attention investment memo](docs/INVESTMENT_MEMO_RETAIL_ATTENTION.md):
  non-technical question/data/finding/implication/caveats write-up for the real
  WSB result.
- [Web traffic and revenue surprise study design](docs/WEB_TRAFFIC_REVENUE_SURPRISE_STUDY.md):
  the operational alt-data extension needed to test whether traffic predicts
  revenue surprises.
- [Tech and consumer sector notes](docs/TECH_CONSUMER_SECTOR_NOTES.md):
  segment-specific framing for e-commerce, marketplaces, social, streaming, and SaaS.
