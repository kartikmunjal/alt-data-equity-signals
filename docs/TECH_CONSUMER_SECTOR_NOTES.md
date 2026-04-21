# Tech And Consumer Sector Notes

## Why Segment The Alt-Data Signal?

Alternative data should map to a real business mechanism. A pooled "tech" or
"consumer" result can hide very different data-generating processes:

- e-commerce traffic can map directly to gross merchandise volume,
- streaming traffic can map to engagement or subscriber intent,
- ad-supported social traffic can map to impressions and ad inventory,
- SaaS web traffic may map only weakly to revenue because contracts are sold
  through enterprise sales cycles.

## Segment Hypotheses

| Segment | Better Signal | Expected Horizon | Main Caveat |
|---|---|---|---|
| E-commerce | traffic growth / traffic shock | current quarter | conversion rate and average order value missing |
| Marketplaces | traffic shock | current or next quarter | supply constraints and take rate matter |
| Social / ads | traffic level and engagement proxy | current quarter | visits are a weak substitute for time spent |
| Streaming | app/web engagement | current or next quarter | subscriber churn and pricing not observed |
| SaaS | job postings / product docs / web leads | one to four quarters | revenue recognition lags demand |

## How This Changes Interpretation

A positive web-traffic shock for `ETSY` or `SHOP` is plausibly a revenue signal.
The same shock for `CRM` is more likely a brand/search-interest signal unless it
can be tied to lead generation, product usage, or contract pipeline.

For WSB/social attention, the segment implication is different. Attention is less
about revenue and more about investor demand, crowding, and risk. In the current
real WSB run, the evidence is contrarian: abnormal attention is more consistent
with temporary price pressure than with a durable fundamental improvement.

## Interview-Ready Framing

The project now separates two kinds of alt data:

1. **Investor-attention data** such as WSB posts. This is useful for crowding,
   squeeze-risk, and mean-reversion questions.
2. **Operational data** such as web traffic. This is useful for fundamental
   diligence questions like revenue surprises and demand acceleration.

The current real result is in bucket 1. Bucket 2 is implemented as a pipeline and
schema, but it still needs a real historical traffic and revenue-surprise dataset
before it should be presented as a completed empirical result.
