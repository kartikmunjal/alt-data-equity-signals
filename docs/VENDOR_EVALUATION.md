# Data Quality And Vendor Evaluation Framework

Alternative data is useful only if it survives vendor diligence before portfolio research. This checklist is intended to be run before treating a new dataset as investable.

## Dataset Identity

| Question | What To Check |
|---|---|
| What economic activity is measured? | WSB attention measures retail discussion; web traffic measures consumer/product demand proxies. |
| Who creates the data? | Users, panels, browser extensions, direct measurement, scraped public pages, or modeled estimates. |
| What is the update cadence? | Daily for social data; monthly for many web-traffic exports. |
| What is the vendor timestamp? | Separate event date from vendor publication date. |

## Coverage Diagnostics

Minimum tables to produce:

- ticker coverage by date
- date coverage by ticker
- missingness heatmap
- new/deleted ticker history
- sector/industry concentration
- overlap with the tradable universe

Coverage questions:

- Does coverage disappear exactly when the stock becomes interesting?
- Are small caps or delisted names missing?
- Does the sample start after the signal was already popular?
- Are there ticker/domain mapping ambiguities, such as parent companies with multiple brands?

## Point-In-Time Discipline

For every record, distinguish:

```text
event_date       = when the consumer/social activity happened
vendor_date      = when the vendor could have known it
research_date    = when the signal is allowed to enter the model
```

Rules used in this repo:

- WSB posts are available on the post timestamp.
- Monthly web traffic is available only after a configurable publication lag, default 7 days.
- Signals are evaluated using forward returns aligned at the signal date.
- Exported factor panels should never be backfilled before the assumed availability date.

## Survivorship Bias

Failure modes:

- using today's ticker list for historical tests
- dropping delisted or bankrupt names
- retaining only companies that still have clean domain mappings
- selecting tickers after seeing which names were discussed online

Mitigations:

- use a historical universe when possible
- keep missing values instead of silently filling old coverage
- report coverage separately from performance
- run sensitivity tests on stable ticker subsets and full available coverage

## Signal Cleaning

Social data checks:

- bot/repost filtering
- ticker false positives such as `ON`, `IT`, `A`, `FOR`
- cashtag vs plain uppercase token hit rate
- outlier post/comment bursts
- duplicate post IDs

Web-traffic checks:

- domain-to-ticker mapping quality
- parent/subsidiary ambiguity
- app traffic vs web traffic mismatch
- panel methodology changes
- month-end revision history
- holiday/seasonality adjustment

## Investability Tests

| Test | Pass Criteria |
|---|---|
| Mean IC | directionally stable and economically interpretable |
| ICIR | positive across adjacent horizons, not one isolated spike |
| Fama-MacBeth | Newey-West t-stat supports nonzero slope |
| Quintile spread | monotonic or at least concentrated in top/bottom buckets |
| Turnover | realistic after data cadence and publication lag |
| Capacity | works in liquid names, not only tiny names |
| Robustness | survives date splits and ticker subsets |
| Incremental value | adds explanatory power beyond standard factors |

## Current Dataset Assessment

| Dataset | Strength | Main Limitation | Current Use |
|---|---|---|---|
| WSB Reddit | high-frequency retail attention and tone | noisy ticker extraction, meme-stock concentration | retail attention and squeeze-risk signal |
| Web traffic | operational demand proxy for e-commerce/tech names | limited coverage and monthly cadence | revenue-surprise and demand-growth proxy |

## Research Questions

WSB:

> Do abnormal retail-attention shocks predict short-horizon stock returns or squeeze-like dislocations?

Web traffic:

> Does abnormal monthly web traffic growth predict future returns, revenue surprises, or analyst estimate revisions for consumer internet and e-commerce stocks?

Securities lending interaction:

> Are high-borrow-stress stocks with abnormal retail attention more likely to generate positive forward-return dislocations?

## Recommendation Framework

| Rating | Meaning |
|---|---|
| Reject | coverage, leakage, or mapping quality is too weak |
| Research-only | signal is interesting but not yet robust/investable |
| Candidate production signal | clean point-in-time data, stable IC, explainable economics, feasible turnover/capacity |

The default classification for new datasets should be `Research-only` until the dataset passes coverage, leakage, robustness, and incremental-value checks.
