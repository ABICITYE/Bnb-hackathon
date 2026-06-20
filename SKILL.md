# Skill: Hype-Divergence Risk Flag

**Purpose**
Flags crypto assets where short-term trading volume has spiked well
beyond what peers are seeing, without a matching 7-day price trend —
a signature of hype-driven moves that historically underperform.

**Data source**
CoinMarketCap `quotes/latest` endpoint (free tier compatible).

**Inputs**
- `api_key` (str): CMC API key, read from `CMC_API_KEY` env var
- `symbols` (list[str]): token universe to evaluate (default: 10
  liquid BEP-20-eligible tokens)
- `threshold` (float): risk score cutoff for flagging, default 1.0

**Output**
Ranked list of dicts per token: `volume_change_24h`, `percent_change_7d`,
`risk_score`, `flag` ("AVOID" if risk_score exceeds threshold).

**Method**
Cross-sectional z-score of 24h volume change minus z-score of 7-day
price change, computed across the token universe at call time. One
API call, no historical data dependency.

**Validation**
A time-series formulation of the same hypothesis was backtested over
a 1-year window (see `spec.md`). The live cross-sectional version is
a practical reformulation for free-tier deployment and was not
independently re-backtested under this exact methodology — disclosed
as a limitation in the spec.
