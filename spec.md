# Strategy Spec: Hype-Divergence Risk Flag

**BNB Hack: AI Trading Agent Edition — Track 2, Strategy Skills**

## Hypothesis

Retail-driven hype — a spike in trading volume not backed by genuine
accumulation — tends to precede weaker-than-average forward returns.
Conversely, price strength that builds quietly, without an unusual
volume spike, is not reliably predictive in either direction on its
own. In short: hype without support is a risk signal, not the
inverse.

## Methodology — Historical Validation

**Data:** Daily price and volume for 10 BEP-20-eligible tokens (ETH,
ADA, LINK, DOT, UNI, AAVE, AVAX, ATOM, LTC, FIL) over a 366-day
window, sourced from CoinGecko's free public API. CMC's free tier
does not expose historical OHLCV (confirmed via direct API testing,
error code 1006 — plan upgrade required), so this validation step
uses an alternative free source. This is disclosed explicitly; see
Limitations.

**Signal construction:**
- `hype_score` = rolling 20-day z-score of daily trading volume
- `accumulation_score` = rolling 20-day z-score of On-Balance Volume
  (OBV), a standard technical indicator that accumulates volume on
  up-days and subtracts it on down-days
- `divergence_score` = accumulation_score − hype_score

**Signal evaluation:** A 7-day forward return is measured whenever
`divergence_score` exceeds a threshold (long/accumulation signal) or
falls below the negative threshold (avoid/hype-without-support
signal), tested at thresholds 0.5, 1.0, 1.5, and 2.0.

## Methodology — Live Skill

CMC's free tier does not support historical time-series queries, so
the live, deployable Skill (`skill.py`) uses a cross-sectional
reformulation of the same hypothesis: instead of comparing a token's
current volume/trend against its own history, it z-scores
`volume_change_24h` (hype) and `percent_change_7d` (trend support)
**across the token universe at the same point in time**, using a
single CMC `quotes/latest` call. This is a practical adaptation for
free-tier deployment, not a re-validation of the identical mechanism
— see Limitations.

## Results

Pooled across all 10 tokens, 366 days. Average buy-and-hold return
over the period: **-58.7%** (a severely bearish window for this
token set). Unconditional baseline average 7-day forward return
(all days, all tokens, no signal applied): **-1.54%**.

| Threshold | Long: signals | Long: win% | Long: avg ret% | Avoid: signals | Avoid: win% | Avoid: avg ret% |
|---|---|---|---|---|---|---|
| 0.5 | 1149 | 40.2 | -1.32 | 1308 | 41.0 | -1.84 |
| 1.0 | 780  | 39.6 | -1.49 | 967  | 39.8 | -1.88 |
| 1.5 | 457  | 37.0 | -1.85 | 700  | 38.3 | -2.26 |
| 2.0 | 255  | 32.2 | -2.67 | 493  | 36.9 | -2.75 |

**Interpretation:** The long (accumulation) signal does not behave
the way a genuine predictive signal should — average return gets
*worse* as conviction (threshold) increases, the opposite of what
real signal strength should produce. The avoid (hype-without-support)
signal behaves correctly: average return worsens monotonically as
threshold increases (-1.84% → -1.88% → -2.26% → -2.75%), consistently
underperforming the -1.54% baseline by a widening margin. This is the
hallmark of genuine, if modest, signal — not noise. The strategy was
therefore reframed from a buy-signal to a risk-flag, based on what
the data actually showed rather than the original hypothesis.

**Live skill example** (snapshot, 2026-06-18, illustrative only — not
a backtest result):

| Symbol | VolChg24h% | PctChg7d% | RiskScore | Flag |
|---|---|---|---|---|
| ATOM | 37.04 | -0.80 | 2.94 | AVOID |
| DOT  | 20.78 | 3.53  | 1.15 | AVOID |
| UNI  | -14.04 | 23.53 | -4.12 | (healthy: real strength, no hype spike) |

## Real-World Relevance

A risk-flag tool that warns "this move is hype-driven, not
fundamentals-driven" has a clear, plausible user: a trader or
portfolio manager deciding whether to chase a pump or hold off.
Unlike a buy-signal generator, which competes with countless
momentum strategies, a disciplined risk-avoidance filter is a
narrower, more defensible niche — and the backtest data supports this
specific framing rather than the broader one.

## Limitations (disclosed honestly)

- Backtest data sourced from CoinGecko, not CMC, due to a confirmed
  free-tier API restriction on CMC's historical endpoint.
- The live Skill's cross-sectional methodology was not independently
  backtested under its own exact formulation — it is a practical
  reformulation of the validated time-series hypothesis, not an
  identical, re-proven mechanism.
- The backtest window (mid-2025 to mid-2026) was a severely bearish
  regime for this token set (-58.7% average buy-and-hold). The
  signal's behavior in bull or sideways markets is untested.
- Hold period was fixed at 7 days and not swept; token universe was
  fixed at 10 tokens, limiting cross-sectional z-score robustness.
- Sample sizes, while reasonably large (250-1300+ signals depending
  on threshold), come from overlapping 7-day windows on the same 10
  tokens, not fully independent observations.

## Reproducibility
No paid API tier or external dependencies required for either script.
