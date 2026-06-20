import subprocess, json, time, statistics, csv

TOKENS = {
    "ETH": "ethereum", "ADA": "cardano", "LINK": "chainlink",
    "DOT": "polkadot", "UNI": "uniswap", "AAVE": "aave",
    "AVAX": "avalanche-2", "ATOM": "cosmos", "LTC": "litecoin",
    "FIL": "filecoin"
}
DAYS = 365
HOLD_DAYS = 7
THRESHOLDS = [0.5, 1.0, 1.5, 2.0]

def fetch(coin_id, retries=2):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days={DAYS}&interval=daily"
    for attempt in range(retries + 1):
        result = subprocess.run(["curl", "-4", "-s", "-m", "20", url], capture_output=True, text=True)
        try:
            data = json.loads(result.stdout)
            if "prices" in data:
                return [p[1] for p in data["prices"]], [v[1] for v in data["total_volumes"]]
            else:
                msg = data.get("status", {}).get("error_message", "unknown")
                print(f"  retry {attempt+1}: {msg}")
        except json.JSONDecodeError:
            print(f"  retry {attempt+1}: bad response")
        time.sleep(15)
    raise RuntimeError("failed after retries")

def zscore(series, window=20):
    out = [0.0] * len(series)
    for i in range(window, len(series)):
        w = series[i-window:i]
        mu = statistics.mean(w)
        sd = statistics.pstdev(w) or 1e-9
        out[i] = (series[i] - mu) / sd
    return out

def obv(prices, volumes):
    o = [0.0] * len(prices)
    for i in range(1, len(prices)):
        if prices[i] > prices[i-1]:
            o[i] = o[i-1] + volumes[i]
        elif prices[i] < prices[i-1]:
            o[i] = o[i-1] - volumes[i]
        else:
            o[i] = o[i-1]
    return o

token_data = {}
for sym, cid in TOKENS.items():
    try:
        prices, volumes = fetch(cid)
        obv_series = obv(prices, volumes)
        hype = zscore(volumes)
        accum = zscore(obv_series)
        bh_ret = (prices[-1] - prices[20]) / prices[20] * 100
        token_data[sym] = (prices, accum, hype, bh_ret)
        print(f"{sym}: fetched {len(prices)} days, buy-hold {bh_ret:.1f}%")
    except Exception as e:
        print(f"{sym}: SKIPPED ({e})")
    time.sleep(8)

# Unconditional baseline: average forward return across ALL days, all tokens
baseline_returns = []
for sym, (prices, accum, hype, bh_ret) in token_data.items():
    for i in range(20, len(prices) - HOLD_DAYS):
        baseline_returns.append((prices[i + HOLD_DAYS] - prices[i]) / prices[i])
baseline_avg = statistics.mean(baseline_returns) * 100
print(f"\nUnconditional baseline avg {HOLD_DAYS}-day return (all days, all tokens): {baseline_avg:.2f}%\n")

all_rows = []
print(f"{'Thresh':<8}{'LongSig':<9}{'LongWin%':<10}{'LongRet%':<10}{'AvoidSig':<10}{'AvoidWin%':<11}{'AvoidRet%':<10}")
for thresh in THRESHOLDS:
    long_returns, long_wins = [], 0
    avoid_returns, avoid_wins = [], 0
    for sym, (prices, accum, hype, bh_ret) in token_data.items():
        for i in range(20, len(prices) - HOLD_DAYS):
            divergence = accum[i] - hype[i]
            fwd_ret = (prices[i + HOLD_DAYS] - prices[i]) / prices[i]
            if divergence > thresh:
                long_returns.append(fwd_ret)
                if fwd_ret > 0: long_wins += 1
                all_rows.append([sym, thresh, "long", i, divergence, fwd_ret])
            elif divergence < -thresh:
                avoid_returns.append(fwd_ret)
                if fwd_ret > 0: avoid_wins += 1
                all_rows.append([sym, thresh, "avoid", i, divergence, fwd_ret])
    ln, an = len(long_returns), len(avoid_returns)
    lw = (long_wins/ln*100) if ln else 0
    lr = (statistics.mean(long_returns)*100) if ln else 0
    aw = (avoid_wins/an*100) if an else 0
    ar = (statistics.mean(avoid_returns)*100) if an else 0
    print(f"{thresh:<8}{ln:<9}{lw:<10.1f}{lr:<10.2f}{an:<10}{aw:<11.1f}{ar:<10.2f}")

with open("backtest_results.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["symbol", "threshold", "signal_type", "day_index", "divergence_score", "forward_return"])
    w.writerows(all_rows)

print("\nSaved full signal log to backtest_results.csv")
