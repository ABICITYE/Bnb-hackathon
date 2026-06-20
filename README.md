# Hype-Divergence Risk Flag

**BNB Hack: AI Trading Agent Edition — Track 2, Strategy Skills**
Powered by CoinMarketCap (CMC for Agent)

> **Note on data sourcing:** the deployed Skill (`skill.py`) runs
> entirely on CoinMarketCap's free API — no other data source. CoinGecko
> appears only in the historical backtest validation, due to a
> documented CMC free-tier limitation (see `spec.md` for details).

## What this is

A CMC Skill that flags tokens where 24h trading volume has surged
unusually relative to peers, without corresponding 7-day price trend
to support it — a pattern that historically predicted weaker forward
returns in backtesting (see `spec.md` for full methodology and results).

## Files

- `skill.py` — the live, deployable Skill. Pulls a single CMC
  `quotes/latest` call across a token universe and computes a
  cross-sectional hype-vs-trend divergence score. No paid API tier
  required.
- `backtest.py` — historical validation of the underlying hypothesis
  using a time-series OBV-divergence formulation (CoinGecko data,
  documented limitation: CMC's free tier blocks historical OHLCV —
  see spec.md).
- `backtest_results.csv` — full signal log from the validated backtest.
- `spec.md` — strategy spec: hypothesis, methodology, results, honest
  limitations, real-world relevance.

## Usage
No external dependencies — pure Python standard library.

## Quick result

Backtested across 10 BEP-20-eligible tokens over a 1-year window:
"hype without accumulation" signals showed a consistent, monotonically
worsening forward-return pattern as signal conviction increased — the
hallmark of a genuine, if modest, predictive effect. Full numbers in
`spec.md`.
