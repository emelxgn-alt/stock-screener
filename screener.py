"""
Stock Screener - screens global markets for stocks near 52-week / all-time highs
and outperforming their country benchmark over 1M and 3M.
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import json
import os

# ─────────────────────────────────────────────
# 1. DEFINE YOUR UNIVERSES
#    These are the stocks + benchmarks per market.
#    You can add/remove tickers freely.
# ─────────────────────────────────────────────

MARKETS = {
    "🇺🇸 United States": {
        "benchmark": "^GSPC",          # S&P 500
        "benchmark_name": "S&P 500",
        "tickers": [
            "AAPL","MSFT","NVDA","GOOGL","AMZN",
            "META","TSLA","BRK-B","JPM","V",
            "UNH","XOM","MA","HD","PG",
            "AVGO","MRK","CVX","LLY","ABBV"
        ]
    },
    "🇹🇼 Taiwan": {
        "benchmark": "^TWII",          # TAIEX
        "benchmark_name": "TAIEX",
        "tickers": [
            "2330.TW","2317.TW","2454.TW","2382.TW",
            "2308.TW","2303.TW","2412.TW","2881.TW",
            "2882.TW","1301.TW","2002.TW","2886.TW",
            "2891.TW","2884.TW","3711.TW"
        ]
    },
    "🇨🇳 China": {
        "benchmark": "000001.SS",      # Shanghai Composite
        "benchmark_name": "Shanghai Composite",
        "tickers": [
            "600519.SS","601398.SS","600036.SS","601288.SS",
            "601939.SS","600276.SS","601166.SS","600900.SS",
            "601628.SS","600887.SS","603288.SS","601318.SS",
            "600030.SS","601088.SS","600585.SS"
        ]
    },
    "🇭🇰 Hong Kong": {
        "benchmark": "^HSI",           # Hang Seng Index
        "benchmark_name": "Hang Seng Index",
        "tickers": [
            "0700.HK","0941.HK","0388.HK","1299.HK",
            "0005.HK","2318.HK","0883.HK","1398.HK",
            "3690.HK","0939.HK","0002.HK","0003.HK",
            "0012.HK","0016.HK","0027.HK"
        ]
    },
    "🇸🇬 Singapore": {
        "benchmark": "^STI",           # Straits Times Index
        "benchmark_name": "Straits Times Index",
        "tickers": [
            "D05.SI","O39.SI","U11.SI","Z74.SI",
            "C52.SI","V03.SI","BN4.SI","BS6.SI",
            "C09.SI","F34.SI","G13.SI","H78.SI",
            "J36.SI","S68.SI","U96.SI"
        ]
    }
}

# ─────────────────────────────────────────────
# 2. HELPER: fetch price history for a ticker
# ─────────────────────────────────────────────

def fetch_data(ticker, period="1y"):
    try:
        df = yf.download(ticker, period=period, auto_adjust=True, progress=False)
        if df.empty:
            return None
        return df
    except Exception:
        return None


# ─────────────────────────────────────────────
# 3. ANALYSE ONE STOCK
# ─────────────────────────────────────────────

def analyse_stock(ticker, benchmark_returns):
    df = fetch_data(ticker, period="2y")   # 2 years to get ATH context
    if df is None or len(df) < 60:
        return None

    close = df["Close"].squeeze()
    current = float(close.iloc[-1])

    # 52-week high
    high_52w = float(close[-252:].max()) if len(close) >= 252 else float(close.max())
    pct_from_52w = (current - high_52w) / high_52w * 100

    # All-time high (within data window)
    ath = float(close.max())
    pct_from_ath = (current - ath) / ath * 100

    # 1-month return
    ret_1m = None
    if len(close) >= 21:
        ret_1m = (current / float(close.iloc[-21]) - 1) * 100

    # 3-month return
    ret_3m = None
    if len(close) >= 63:
        ret_3m = (current / float(close.iloc[-63]) - 1) * 100

    # Outperformance vs benchmark
    outperf_1m = (ret_1m - benchmark_returns["1m"]) if (ret_1m is not None and benchmark_returns.get("1m") is not None) else None
    outperf_3m = (ret_3m - benchmark_returns["3m"]) if (ret_3m is not None and benchmark_returns.get("3m") is not None) else None

    # Scoring: near 52w high AND outperforming
    score = 0
    if pct_from_52w >= -5:   score += 3   # within 5% of 52w high
    elif pct_from_52w >= -10: score += 1
    if pct_from_ath >= -5:    score += 2   # within 5% of ATH
    if outperf_1m is not None and outperf_1m > 0: score += 2
    if outperf_3m is not None and outperf_3m > 0: score += 2

    # Get company name
    try:
        info = yf.Ticker(ticker).fast_info
        name = getattr(info, "currency", ticker)   # fallback
        name2 = yf.Ticker(ticker).info.get("shortName", ticker)
    except Exception:
        name2 = ticker

    return {
        "ticker": ticker,
        "name": name2,
        "current": round(current, 2),
        "52w_high": round(high_52w, 2),
        "pct_from_52w": round(pct_from_52w, 2),
        "ath": round(ath, 2),
        "pct_from_ath": round(pct_from_ath, 2),
        "ret_1m": round(ret_1m, 2) if ret_1m is not None else None,
        "ret_3m": round(ret_3m, 2) if ret_3m is not None else None,
        "outperf_1m": round(outperf_1m, 2) if outperf_1m is not None else None,
        "outperf_3m": round(outperf_3m, 2) if outperf_3m is not None else None,
        "score": score
    }


# ─────────────────────────────────────────────
# 4. GET BENCHMARK RETURNS
# ─────────────────────────────────────────────

def get_benchmark_returns(ticker):
    df = fetch_data(ticker, period="1y")
    if df is None or df.empty:
        return {"1m": None, "3m": None}
    close = df["Close"].squeeze()
    ret_1m = (float(close.iloc[-1]) / float(close.iloc[-21]) - 1) * 100 if len(close) >= 21 else None
    ret_3m = (float(close.iloc[-1]) / float(close.iloc[-63]) - 1) * 100 if len(close) >= 63 else None
    return {"1m": round(ret_1m, 2) if ret_1m else None,
            "3m": round(ret_3m, 2) if ret_3m else None}


# ─────────────────────────────────────────────
# 5. RUN ALL MARKETS
# ─────────────────────────────────────────────

def run_screener():
    all_results = {}
    for market_name, config in MARKETS.items():
        print(f"\n📊 Screening {market_name}...")
        bench_returns = get_benchmark_returns(config["benchmark"])
        results = []
        for ticker in config["tickers"]:
            print(f"   → {ticker}", end=" ")
            row = analyse_stock(ticker, bench_returns)
            if row:
                results.append(row)
                print("✓")
            else:
                print("✗ (no data)")
        results.sort(key=lambda x: x["score"], reverse=True)
        all_results[market_name] = {
            "benchmark_name": config["benchmark_name"],
            "benchmark_returns": bench_returns,
            "stocks": results
        }
    return all_results


# ─────────────────────────────────────────────
# 6. GENERATE HTML
# ─────────────────────────────────────────────

def fmt(val, suffix="%", plus=True):
    if val is None:
        return "<span class='na'>N/A</span>"
    sign = "+" if val > 0 and plus else ""
    cls = "pos" if val > 0 else "neg" if val < 0 else "neu"
    return f"<span class='{cls}'>{sign}{val}{suffix}</span>"

def stars(score):
    full = score // 2
    return "★" * full + "☆" * (5 - full)

def build_html(data):
    now = datetime.utcnow().strftime("%d %b %Y %H:%M UTC")
    
    market_sections = ""
    for market_name, mdata in data.items():
        bench = mdata["benchmark_name"]
        br = mdata["benchmark_returns"]
        stocks = mdata["stocks"]
        
        b1 = fmt(br.get("1m"))
        b3 = fmt(br.get("3m"))

        rows = ""
        for s in stocks:
            near_52w = "🟢" if s["pct_from_52w"] >= -5 else ("🟡" if s["pct_from_52w"] >= -15 else "🔴")
            near_ath = "🟢" if s["pct_from_ath"] >= -5 else ("🟡" if s["pct_from_ath"] >= -15 else "🔴")
            rows += f"""
            <tr>
              <td><strong>{s['ticker']}</strong><br><small>{s['name']}</small></td>
              <td>{s['current']}</td>
              <td>{near_52w} {fmt(s['pct_from_52w'])}</td>
              <td>{near_ath} {fmt(s['pct_from_ath'])}</td>
              <td>{fmt(s['ret_1m'])}</td>
              <td>{fmt(s['outperf_1m'])}</td>
              <td>{fmt(s['ret_3m'])}</td>
              <td>{fmt(s['outperf_3m'])}</td>
              <td class='stars' title='Score: {s["score"]}/9'>{stars(s["score"])}</td>
            </tr>"""

        market_sections += f"""
        <section class="market">
          <div class="market-header">
            <h2>{market_name}</h2>
            <div class="bench-pill">
              Benchmark: {bench} &nbsp;|&nbsp;
              1M: {b1} &nbsp;|&nbsp; 3M: {b3}
            </div>
          </div>
          <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Stock</th>
                <th>Price</th>
                <th>vs 52W High</th>
                <th>vs ATH</th>
                <th>1M Return</th>
                <th>1M vs Benchmark</th>
                <th>3M Return</th>
                <th>3M vs Benchmark</th>
                <th>Rating</th>
              </tr>
            </thead>
            <tbody>{rows}</tbody>
          </table>
          </div>
        </section>"""

    legend = """
    <section class="legend">
      <h3>📖 How to read this</h3>
      <ul>
        <li><strong>vs 52W High</strong> — How far the stock is from its highest price in the past year. 0% means it's AT the high right now!</li>
        <li><strong>vs ATH</strong> — How far from its all-time highest price ever recorded.</li>
        <li><strong>1M / 3M Return</strong> — How much the stock went up (green) or down (red) in the last 1 or 3 months.</li>
        <li><strong>vs Benchmark</strong> — Is this stock beating its country's index? Green = YES, beating the market 🎉</li>
        <li><strong>Rating ★</strong> — Overall score. More stars = near highs AND beating the market.</li>
        <li>🟢 = within 5% of high &nbsp; 🟡 = within 15% &nbsp; 🔴 = more than 15% below high</li>
      </ul>
    </section>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Global Stock Screener</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
  :root {{
    --bg: #0d1117;
    --surface: #161b22;
    --surface2: #21262d;
    --border: #30363d;
    --text: #e6edf3;
    --muted: #8b949e;
    --accent: #58a6ff;
    --green: #3fb950;
    --red: #f85149;
    --yellow: #d29922;
    --gold: #f0c040;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background: var(--bg);
    color: var(--text);
    font-family: 'DM Sans', sans-serif;
    font-size: 14px;
    line-height: 1.6;
  }}
  header {{
    background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
    border-bottom: 1px solid var(--border);
    padding: 2rem 2rem 1.5rem;
    display: flex;
    align-items: flex-end;
    gap: 1.5rem;
    flex-wrap: wrap;
  }}
  header h1 {{
    font-family: 'DM Serif Display', serif;
    font-size: 2rem;
    color: var(--accent);
    letter-spacing: -0.5px;
  }}
  header p {{ color: var(--muted); font-size: 0.85rem; }}
  .timestamp {{ margin-left: auto; color: var(--muted); font-size: 0.8rem; }}
  main {{ max-width: 1400px; margin: 0 auto; padding: 2rem; }}
  .market {{ margin-bottom: 3rem; }}
  .market-header {{
    display: flex; align-items: center; gap: 1rem; flex-wrap: wrap;
    margin-bottom: 1rem;
  }}
  .market-header h2 {{ font-family: 'DM Serif Display', serif; font-size: 1.4rem; }}
  .bench-pill {{
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 0.3rem 1rem;
    font-size: 0.8rem;
    color: var(--muted);
  }}
  .table-wrap {{ overflow-x: auto; border-radius: 10px; border: 1px solid var(--border); }}
  table {{ width: 100%; border-collapse: collapse; background: var(--surface); }}
  thead th {{
    background: var(--surface2);
    padding: 0.75rem 1rem;
    text-align: left;
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--muted);
    white-space: nowrap;
    border-bottom: 1px solid var(--border);
  }}
  tbody tr {{ border-bottom: 1px solid var(--border); transition: background 0.15s; }}
  tbody tr:last-child {{ border-bottom: none; }}
  tbody tr:hover {{ background: var(--surface2); }}
  td {{ padding: 0.7rem 1rem; vertical-align: middle; }}
  td small {{ color: var(--muted); display: block; font-size: 0.75rem; }}
  .pos {{ color: var(--green); font-weight: 500; }}
  .neg {{ color: var(--red); font-weight: 500; }}
  .neu {{ color: var(--muted); }}
  .na {{ color: var(--muted); opacity: 0.5; }}
  .stars {{ color: var(--gold); letter-spacing: 1px; font-size: 1rem; }}
  .legend {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1.5rem 2rem;
    margin-top: 2rem;
  }}
  .legend h3 {{ margin-bottom: 0.75rem; font-family: 'DM Serif Display', serif; }}
  .legend ul {{ list-style: none; display: grid; gap: 0.4rem; }}
  .legend li {{ color: var(--muted); font-size: 0.85rem; }}
  .legend li strong {{ color: var(--text); }}
  footer {{
    text-align: center;
    padding: 2rem;
    color: var(--muted);
    font-size: 0.8rem;
    border-top: 1px solid var(--border);
    margin-top: 3rem;
  }}
  @media (max-width: 600px) {{
    header h1 {{ font-size: 1.5rem; }}
    td, th {{ padding: 0.5rem 0.6rem; font-size: 0.75rem; }}
  }}
</style>
</head>
<body>
<header>
  <div>
    <h1>🌏 Global Stock Screener</h1>
    <p>Stocks near 52-Week &amp; All-Time Highs · Outperforming their Benchmark</p>
  </div>
  <div class="timestamp">Updated: {now}</div>
</header>
<main>
{market_sections}
{legend}
</main>
<footer>
  Data sourced from Yahoo Finance via yfinance · For informational purposes only · Not financial advice<br>
  Auto-refreshed daily by GitHub Actions
</footer>
</body>
</html>"""
    return html


# ─────────────────────────────────────────────
# 7. MAIN
# ─────────────────────────────────────────────

if __name__ == "__main__":
    results = run_screener()
    html = build_html(results)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("\n✅ index.html generated successfully!")
