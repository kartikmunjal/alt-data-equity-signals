# Investment Memo: Retail Attention As A Contrarian Signal

## Question

Does abnormal WallStreetBets attention contain investable information about future
stock returns?

## Data

The real-data run uses the free MIT-licensed Figshare WallStreetBets dataset from
2020-10-01 to 2022-04-29. The usable ticker universe is narrow: `AAPL`, `AMC`,
`GME`, `MSFT`, `NOK`, and `TSLA`. Signals are built from Reddit `created_utc`
timestamps, ticker mentions, and lexicon sentiment.

The dataset is public and useful for demonstrating methodology, but it is biased
toward the meme-stock episode and should not be treated as a production universe.

## Finding

The cleanest WSB finding is contrarian. In the connected factor-research run,
`WSB_ATTENTION_SHOCK_Z` had a Fama-MacBeth Newey-West t-stat of `-2.70`
with p-value `0.0146` at the 21-day horizon. Separately, raw mention intensity
had negative rank IC:

| Signal | Horizon | Mean IC | ICIR | t-stat | p-value |
|---|---:|---:|---:|---:|---:|
| `WSB_MENTION_Z` | 21d | -0.0717 | -0.1306 | -2.56 | 0.0109 |
| `WSB_ATTENTION_SHOCK_Z` | FM 21d | -0.0433 lambda | n/a | -2.70 NW | 0.0146 |

The effect weakens when `GME` and `AMC` are excluded. In the ex-GME/AMC run,
`mention_z` remained negative at 21 days (`mean_ic=-0.0695`) but the BH-adjusted
p-value rose to `0.6019`, so the robust conclusion is not "WSB always predicts
underperformance." The more defensible conclusion is that the public WSB sample
contains a strong event-driven contrarian pattern that requires broader coverage
before production use.

## Investment Implication

For a fundamental or discretionary investor, the result is a warning flag rather
than an automatic trade. A sharp increase in retail attention may indicate that
a name has moved from fundamentals-driven ownership into attention-driven price
formation. That can justify a short or underweight review when combined with:

- stretched valuation,
- elevated short interest or days-to-cover,
- high borrow stress,
- deteriorating earnings revisions,
- a lack of confirming operational data such as web traffic or app usage.

The practical PM question is:

> Is the stock going up because fundamentals improved, or because retail attention
> temporarily overwhelmed fundamentals?

## Caveats

- The public universe has only six tickers.
- `GME` and `AMC` dominate the economic story.
- The current pipeline reports research-aligned forward returns, not a next-open
  execution-lagged production backtest.
- Reddit attention is noisy and subject to bot/repost/ticker false-positive issues.
- A real production test should add a larger universe, short-interest publication
  lags, sector controls, and operational datasets.

## Next Test

Pair `WSB_ATTENTION_SHOCK_Z` with securities-lending features:

```text
high retail attention shock
  x high days-to-cover
  x high borrow stress
  -> squeeze risk / later reversal test
```

The thesis is strongest where crowded short positioning and abnormal retail
attention coexist. The current securities-lending integration is wired, but the
available local lending panel is still a demo panel rather than real vendor data.
