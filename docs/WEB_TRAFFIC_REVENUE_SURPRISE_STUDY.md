# Study Design: Web Traffic And Revenue Surprises

## Question

Does abnormal web-traffic growth predict revenue surprises for technology and
consumer internet companies?

This is the operational alt-data question that the current repo is designed to
support but has not yet run on a real vendor file.

## Current Status

Implemented:

- monthly web-traffic loader,
- ticker/date/visits schema,
- traffic level, growth, and shock signals,
- IC/ICIR, Fama-MacBeth, quintile-sort framework,
- factor-panel export into the cross-sectional factor repo.

Not yet available locally:

- a real historical monthly web-traffic panel,
- point-in-time analyst revenue estimates,
- actual revenue surprise labels.

The README therefore does not report real web-traffic results. Reporting synthetic
or schema-only output as a real Similarweb/web-traffic result would be misleading.

## Required Data

### Web Traffic

```text
date,ticker,domain,visits,source,vendor_publication_date
2021-01-31,ETSY,etsy.com,123456789,similarweb,2021-02-07
```

Minimum fields:

- `date`: month-end traffic month,
- `ticker`: mapped public company ticker,
- `visits`: monthly web visits or comparable traffic measure,
- `vendor_publication_date`: when the metric was actually available.

### Revenue Surprise

```text
fiscal_quarter_end,earnings_date,ticker,actual_revenue,consensus_revenue
2021-03-31,2021-04-29,AMZN,108518000000,104470000000
```

Derived label:

```text
revenue_surprise = (actual_revenue - consensus_revenue) / consensus_revenue
```

## Universe

Start with a focused tech/consumer basket where web activity plausibly maps to
revenue:

| Segment | Example Tickers | Why Traffic Might Matter |
|---|---|---|
| E-commerce | `AMZN`, `ETSY`, `SHOP`, `EBAY`, `W`, `CHWY` | web visits map to transaction funnel |
| Travel / local marketplaces | `ABNB`, `BKNG`, `EXPE`, `UBER`, `DASH` | demand intent shows up online before reported revenue |
| Streaming / subscription | `NFLX`, `SPOT`, `ROKU` | engagement and subscriber funnel proxy |
| Social / ads | `META`, `PINS`, `SNAP`, `RDDT` | traffic can proxy ad inventory and engagement |
| SaaS / developer tools | `CRM`, `ADBE`, `NOW`, `DDOG`, `MDB` | weaker direct mapping; traffic may proxy pipeline, not revenue |

This sector split matters. Web traffic should have a more direct revenue link for
e-commerce and marketplaces than for enterprise SaaS, where sales cycles and
contract revenue recognition create longer lags.

## Methodology

1. Lag web traffic by vendor publication date.
2. Compute monthly `web_traffic_growth_z` and `web_traffic_shock_z`.
3. For each earnings event, use only traffic observations known before the earnings
   date.
4. Aggregate the last one to three known traffic months before earnings.
5. Regress or bucket revenue surprise on lagged traffic signals.
6. Run sector-specific results rather than one pooled conclusion.

Example event-study panel:

```text
revenue_surprise_i,q =
    alpha
  + beta * web_traffic_shock_z_i,pre_earnings
  + gamma * size_i
  + delta * sector_i
  + epsilon_i,q
```

## Decision Rule

A traffic dataset becomes interesting if:

- coverage is stable across the target universe,
- traffic observations are point-in-time and not revised after earnings,
- signal direction is intuitive by sector,
- revenue-surprise relationship survives excluding mega-cap names,
- the signal adds value beyond price momentum and analyst revision proxies.

## Expected Output

The first real run should produce:

- coverage table by ticker and month,
- sector-level traffic signal IC versus forward returns,
- revenue-surprise event-study coefficient table,
- one-page investment memo with the best and weakest segment findings.

Until the real traffic and revenue-surprise files exist locally, this remains a
study design and implementation target, not a completed result.
