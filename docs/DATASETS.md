# Public Dataset Options

## Implemented: Reddit WallStreetBets

Good public starting points:

- Kaggle WSB posts/comments exports based on Pushshift.
- Any CSV/JSONL/Parquet export with `created_utc` and one or more text columns.

Expected columns:

| Column | Required | Notes |
|---|---:|---|
| `created_utc` | yes | Unix seconds or parseable datetime |
| `title` | no | Used when present |
| `selftext` | no | Used when present |
| `body` | no | Used when present, common for comments |

At least one of `title`, `selftext`, or `body` must exist.

## Implemented: SimilarWeb-Style Web Traffic

Implemented as a generic monthly web-traffic loader.

Expected columns:

| Column | Required | Notes |
|---|---:|---|
| `date` | yes | month or month-end date |
| `ticker` | yes | mapped public company ticker |
| `visits` | yes | monthly visits or comparable traffic metric |
| `source` | no | vendor/source label |
| `domain` | no | original mapped domain |

Signals:

- traffic level
- month-over-month traffic growth
- abnormal traffic shock versus trailing baseline

Research framing:

> Does web traffic predict future returns, revenue surprises, or analyst
> estimate revisions for consumer internet and e-commerce stocks?

## Price Data

Two supported paths:

1. Provide a local close-price panel:

   ```text
   index=date, columns=tickers, values=close price
   ```

2. Let the script download adjusted closes from yfinance using `--tickers`.

## Candidate Next Datasets

### Robinhood Popularity / Robintrack

Signal ideas:

- user-holder count change
- popularity acceleration
- abnormal popularity shock
- popularity change adjusted for realized volatility

Best use: retail crowding and attention, especially around 2020-2021.

### Foursquare / SafeGraph-Style POI And Foot Traffic

The open Foursquare dataset is mostly POI/place data, not visit counts. A robust stock signal requires a separate mapping from public companies to store locations and a true traffic/visits time series. This is more complex and better as a second project after the WSB pipeline.

### SEC Form 4 / Insider Transactions

Public, point-in-time, and stock-level. Useful as a non-text alt-data extension with cleaner entity mapping.

### Google Trends

Public-ish and easy to explain, but rate limits and normalization issues make it harder to treat as a clean panel without careful batching.
