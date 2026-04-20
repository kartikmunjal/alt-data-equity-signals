# Connections To Existing Research Repos

## Primary Connection: Cross-Sectional-Factor-Research

This repo intentionally uses the same core object shape:

```python
signal_panel: pd.DataFrame      # index=date, columns=ticker
return_panel: pd.DataFrame      # index=date, columns=ticker
```

That makes WSB social signals and web-traffic operational signals drop-in peers to traditional factors such as momentum, idiosyncratic volatility, value, and quality.

Recommended integration path:

1. Export signal panels from this repo:

   ```bash
   python scripts/run_pipeline.py \
     --posts data/raw/wsb_posts.csv \
     --web-traffic data/raw/monthly_web_traffic.csv \
     --prices data/raw/close.parquet
   ```

2. Copy or symlink `results/signal_*.parquet` into the factor research repo under `data/alt/`.

3. Add an `altdata.py` factor module in `Cross-Sectional-Factor-Research/src/factors/`.

4. Register:

   - `WSB_MENTION_Z`
   - `WSB_SENTIMENT_Z`
   - `WSB_ATTENTION_SHOCK_Z`
   - `WSB_WEB_TRAFFIC_LEVEL_Z`
   - `WSB_WEB_TRAFFIC_GROWTH_Z`
   - `WSB_WEB_TRAFFIC_SHOCK_Z`

5. Run the existing factor pipeline with the alt-data factors included in the same IC, Fama-MacBeth, and quintile workflow.

## Secondary Connection: securities-lending

The strongest combined research story is retail attention plus shorting/crowding:

```text
short interest / borrow stress / days-to-cover
    + WSB attention shock
    + WSB bullish sentiment
    -> squeeze-risk and forward-return diagnostics
```

Recommended additions to `securities-lending`:

- Use `attention_shock_z` as a control in borrow-rate Fama-MacBeth regressions.
- Add interaction terms:
  - `borrow_stress * attention_shock_z`
  - `days_to_cover * mention_z`
  - `short_interest_pct_float * sentiment_z`
- Feed WSB attention features into the existing squeeze detector.

This turns the securities-lending repo into a broader crowding and dislocation research platform.

Implemented connection:

- `securities-lending/src/securities_lending/features/retail_attention.py`
  loads `WSB_*.parquet` panels and converts them to the repo's long feature
  frame: `date, symbol, wsb_*`.
- `securities-lending/scripts/run_analysis.py --alt-factor-dir ...` merges
  retail-attention features into the existing short-interest feature panel.
- The analysis includes standalone WSB signals and interaction features:
  - `borrow_stress_x_wsb_attention`
  - `dtc_x_wsb_attention`
  - `short_pressure_x_wsb_sentiment`
- `securities-lending/src/securities_lending/models/squeeze_detector.py`
  treats those WSB columns as optional model features when present.
- `securities-lending/scripts/run_retail_squeeze_backtest.py` reports a compact
  long-short spread, Sharpe, hit rate, and top-bucket hit rate for the
  crowded-short x retail-attention interaction thesis.

Run:

```bash
cd ../securities-lending
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

## Downstream Connection: HFT-trades-local

The HFT/bar-ML repo is not the right home for the research, but it is a useful downstream test:

- Build daily attention signals after market close.
- Carry the signal into the next trading day.
- Use it as a gate or feature for intraday bar-level entries.
- Compare turnover, hit rate, and cost-adjusted returns with and without the gate.

This keeps signal discovery separate from execution research.

## Follow-Up Connection: options-vol-research

Retail attention is plausibly more predictive of volatility than direction.

Useful follow-up tests:

- Does `attention_shock_z` predict next 5-day or 21-day realized volatility?
- Does it predict implied-vol richening for single-stock options?
- Does it improve delta-hedged straddle selection?

That would connect this repo to the volatility-surface and delta-hedging framework after the equity-return signal is validated.
