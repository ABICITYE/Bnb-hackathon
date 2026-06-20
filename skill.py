"""
Hype-Divergence Risk Flag Skill
Powered by CoinMarketCap (CMC for Agent)

Flags tokens where 24h trading volume has surged unusually relative to
peers, without corresponding 7-day price trend support — a pattern
historically associated with weaker forward returns (see backtest.py
and spec.md for the time-series validation this hypothesis is based on).

This live version is a cross-sectional reformulation: instead of
comparing a token's volume against its own history (blocked on CMC's
free tier), it compares all tokens in the universe against each other
at the same point in time, using a single free quotes/latest call.

Usage:
    export CMC_API_KEY="your-key-here"
    python3 skill.py
"""

import os
import json
import statistics
import urllib.request

DEFAULT_SYMBOLS = ["ETH", "ADA", "LINK", "DOT", "UNI", "AAVE", "AVAX", "ATOM", "LTC", "FIL"]
RISK_THRESHOLD = 1.0


def fetch_quotes(symbols, api_key):
    url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?symbol={','.join(symbols)}"
    req = urllib.request.Request(url)
    req.add_header("X-CMC_PRO_API_KEY", api_key)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())["data"]


def zscore(value, series):
    mu = statistics.mean(series)
    sd = statistics.pstdev(series) or 1e-9
    return (value - mu) / sd


def compute_divergence_signals(api_key, symbols=None, threshold=RISK_THRESHOLD):
    symbols = symbols or DEFAULT_SYMBOLS
    data = fetch_quotes(symbols, api_key)

    rows = []
    for sym, info in data.items():
        q = info["quote"]["USD"]
        rows.append({
            "symbol": sym,
            "volume_change_24h": q["volume_change_24h"],
            "percent_change_7d": q["percent_change_7d"],
        })

    vol_series = [r["volume_change_24h"] for r in rows]
    trend_series = [r["percent_change_7d"] for r in rows]

    for r in rows:
        hype_z = zscore(r["volume_change_24h"], vol_series)
        trend_z = zscore(r["percent_change_7d"], trend_series)
        r["risk_score"] = round(hype_z - trend_z, 3)
        r["flag"] = "AVOID" if r["risk_score"] > threshold else None

    rows.sort(key=lambda r: -r["risk_score"])
    return rows


if __name__ == "__main__":
    api_key = os.environ.get("CMC_API_KEY")
    if not api_key:
        print("Set CMC_API_KEY environment variable first.")
        exit(1)

    results = compute_divergence_signals(api_key)

    print(f"{'Symbol':<8}{'VolChg24h%':<13}{'PctChg7d%':<12}{'RiskScore':<11}{'Flag'}")
    for r in results:
        flag = r["flag"] or ""
        print(f"{r['symbol']:<8}{r['volume_change_24h']:<13.2f}{r['percent_change_7d']:<12.2f}{r['risk_score']:<11}{flag}")
