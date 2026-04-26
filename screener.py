"""
Global Stock Screener
- Top 50 by market cap + Top 50 by volume per market
- Near 52-week / all-time high
- Outperforming benchmark over 1M and 3M
- Volume surge: 10%+ above 20-day average volume
"""

import yfinance as yf
import pandas as pd
from datetime import datetime

# ─────────────────────────────────────────────
# STOCK UNIVERSE — Top 50 Market Cap + Top 50 Volume per market
# These are pre-researched. Update once a year if needed.
# ─────────────────────────────────────────────

MARKETS = {
    "us": {
        "label": "🇺🇸 United States",
        "benchmark": "^GSPC",
        "benchmark_name": "S&P 500",
        "tickers_mcap": [
            "AAPL","MSFT","NVDA","GOOGL","AMZN","META","TSLA","BRK-B","LLY","AVGO",
            "JPM","UNH","XOM","V","MA","PG","COST","HD","MRK","ABBV",
            "CVX","CRM","ACN","BAC","NFLX","KO","AMD","PEP","TMO","ADBE",
            "MCD","CSCO","WMT","ABT","TXN","PM","LIN","GE","DHR","CAT",
            "INTU","ISRG","BKNG","MS","AMGN","RTX","SPGI","HON","PFE","UBER"
        ],
        "tickers_vol": [
            "SQQQ","TQQQ","SPY","QQQ","SOFI","PLTR","F","BAC","AAL","CCL",
            "AMC","RIVN","NIO","LCID","SNAP","HOOD","VALE","ITUB","PBR","SLB",
            "WFC","C","INTC","T","VZ","CMCSA","GM","FCX","GRAB","MARA",
            "RIOT","COIN","SWN","MU","KEY","RF","PARA","DNA","PLUG","FCEL",
            "WISH","CLOV","BBBY","SDC","WKHS","GOEV","NKLA","SPCE","SNDL","ACB"
        ]
    },
    "tw": {
        "label": "🇹🇼 Taiwan",
        "benchmark": "^TWII",
        "benchmark_name": "TAIEX",
        "tickers_mcap": [
            "2330.TW","2317.TW","2454.TW","2382.TW","2308.TW","2303.TW",
            "2412.TW","2881.TW","2882.TW","1301.TW","2002.TW","2886.TW",
            "2891.TW","2884.TW","3711.TW","2357.TW","2379.TW","2395.TW",
            "3008.TW","2327.TW","2344.TW","2360.TW","4904.TW","2885.TW",
            "2880.TW","1303.TW","1326.TW","2883.TW","5880.TW","2887.TW",
            "2892.TW","2912.TW","1216.TW","2207.TW","2301.TW","6505.TW",
            "2474.TW","3045.TW","2352.TW","2376.TW","2408.TW","3006.TW",
            "2347.TW","2385.TW","2399.TW","3034.TW","2337.TW","2388.TW",
            "2356.TW","2376.TW"
        ],
        "tickers_vol": [
            "2330.TW","2317.TW","2303.TW","2308.TW","2002.TW","2882.TW",
            "2881.TW","2891.TW","3481.TW","2886.TW","2884.TW","2883.TW",
            "2885.TW","2880.TW","2892.TW","1301.TW","1303.TW","2207.TW",
            "6770.TW","2382.TW","2454.TW","2379.TW","3711.TW","2357.TW",
            "2395.TW","2344.TW","4938.TW","3008.TW","2327.TW","2360.TW",
            "6415.TW","3231.TW","2376.TW","2408.TW","5347.TW","2337.TW",
            "2352.TW","2301.TW","2474.TW","3034.TW","2347.TW","2399.TW",
            "2388.TW","2356.TW","3045.TW","4904.TW","2912.TW","1216.TW",
            "2887.TW","6505.TW"
        ]
    },
    "cn": {
        "label": "🇨🇳 China",
        "benchmark": "000001.SS",
        "benchmark_name": "Shanghai Composite",
        "tickers_mcap": [
            "600519.SS","601398.SS","600036.SS","601288.SS","601939.SS",
            "600276.SS","601166.SS","600900.SS","601628.SS","600887.SS",
            "603288.SS","601318.SS","600030.SS","601088.SS","600585.SS",
            "601668.SS","600016.SS","601601.SS","601688.SS","600031.SS",
            "601989.SS","600309.SS","601186.SS","600028.SS","601088.SS",
            "600048.SS","601390.SS","600918.SS","601138.SS","600050.SS",
            "601766.SS","600104.SS","601336.SS","600690.SS","601818.SS",
            "600406.SS","601328.SS","601998.SS","600009.SS","601169.SS",
            "600438.SS","601117.SS","600837.SS","601211.SS","600196.SS",
            "603501.SS","600745.SS","688111.SS","600703.SS","601012.SS"
        ],
        "tickers_vol": [
            "600519.SS","600036.SS","601398.SS","600030.SS","601939.SS",
            "601288.SS","600016.SS","601166.SS","600031.SS","601601.SS",
            "601688.SS","600309.SS","601318.SS","600887.SS","603288.SS",
            "600028.SS","601088.SS","601186.SS","600048.SS","601668.SS",
            "601989.SS","600104.SS","601336.SS","601766.SS","600690.SS",
            "600406.SS","600050.SS","601818.SS","601328.SS","601998.SS",
            "600009.SS","600438.SS","601117.SS","600837.SS","601211.SS",
            "600196.SS","603501.SS","600745.SS","688111.SS","600703.SS",
            "601012.SS","600900.SS","601628.SS","600585.SS","600276.SS",
            "601390.SS","600918.SS","601138.SS","601169.SS","601816.SS"
        ]
    },
    "hk": {
        "label": "🇭🇰 Hong Kong",
        "benchmark": "^HSI",
        "benchmark_name": "Hang Seng Index",
        "tickers_mcap": [
            "0700.HK","0941.HK","0388.HK","1299.HK","0005.HK","2318.HK",
            "0883.HK","1398.HK","3690.HK","0939.HK","0002.HK","0003.HK",
            "0012.HK","0016.HK","0027.HK","1093.HK","0823.HK","0688.HK",
            "2628.HK","0762.HK","1177.HK","0011.HK","0101.HK","0066.HK",
            "1038.HK","0006.HK","0017.HK","0083.HK","0019.HK","0004.HK",
            "2388.HK","1113.HK","0960.HK","1109.HK","2020.HK","3988.HK",
            "1928.HK","0669.HK","1044.HK","0291.HK","0241.HK","1088.HK",
            "0386.HK","0857.HK","0728.HK","2313.HK","0151.HK","0267.HK",
            "0175.HK","0992.HK"
        ],
        "tickers_vol": [
            "0700.HK","0941.HK","3690.HK","1398.HK","0939.HK","0388.HK",
            "0005.HK","2318.HK","0883.HK","1299.HK","0016.HK","0011.HK",
            "0012.HK","2628.HK","0762.HK","0002.HK","0003.HK","0006.HK",
            "1177.HK","0823.HK","1093.HK","0688.HK","0066.HK","1038.HK",
            "0027.HK","0017.HK","0083.HK","0019.HK","3988.HK","2388.HK",
            "1113.HK","0960.HK","1109.HK","2020.HK","1928.HK","0669.HK",
            "1044.HK","0291.HK","0241.HK","1088.HK","0386.HK","0857.HK",
            "0728.HK","2313.HK","0151.HK","0267.HK","0175.HK","0992.HK",
            "0101.HK","0004.HK"
        ]
    },
    "sg": {
        "label": "🇸🇬 Singapore",
        "benchmark": "^STI",
        "benchmark_name": "Straits Times Index",
        "tickers_mcap": [
            "D05.SI","O39.SI","U11.SI","Z74.SI","C52.SI","V03.SI","BN4.SI",
            "BS6.SI","C09.SI","F34.SI","G13.SI","H78.SI","J36.SI","S68.SI",
            "U96.SI","A17U.SI","C38U.SI","ME8U.SI","N2IU.SI","BUOU.SI",
            "T82U.SI","K71U.SI","M44U.SI","SK6U.SI","AW9U.SI","AJBU.SI",
            "CWCU.SI","RW0U.SI","J91U.SI","ND8U.SI","Q5T.SI","5E2.SI",
            "S63.SI","Y92.SI","C6L.SI","D01.SI","F99.SI","G07.SI","H02.SI",
            "M01.SI","S85.SI","U14.SI","V25.SI","W05.SI","X05.SI","9CI.SI",
            "CC3.SI","DBS.SI","OCBC.SI","UOB.SI"
        ],
        "tickers_vol": [
            "D05.SI","O39.SI","U11.SI","Z74.SI","S68.SI","C52.SI","V03.SI",
            "BN4.SI","BS6.SI","C09.SI","F34.SI","G13.SI","H78.SI","J36.SI",
            "U96.SI","A17U.SI","C38U.SI","ME8U.SI","N2IU.SI","BUOU.SI",
            "T82U.SI","K71U.SI","M44U.SI","SK6U.SI","AW9U.SI","AJBU.SI",
            "Q5T.SI","5E2.SI","S63.SI","Y92.SI","C6L.SI","D01.SI","F99.SI",
            "G07.SI","H02.SI","M01.SI","S85.SI","U14.SI","V25.SI","W05.SI",
            "X05.SI","9CI.SI","CC3.SI","CWCU.SI","RW0U.SI","J91U.SI",
            "ND8U.SI","Q5T.SI","G3B.SI","CLR.SI"
        ]
    }
}

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def fetch_data(ticker, period="1y"):
    try:
        df = yf.download(ticker, period=period, auto_adjust=True, progress=False)
        if df.empty:
            return None
        return df
    except Exception:
        return None

def get_benchmark_returns(ticker):
    df = fetch_data(ticker, period="1y")
    if df is None or df.empty:
        return {"1m": None, "3m": None}
    close = df["Close"].squeeze()
    r1 = (float(close.iloc[-1]) / float(close.iloc[-21]) - 1) * 100 if len(close) >= 21 else None
    r3 = (float(close.iloc[-1]) / float(close.iloc[-63]) - 1) * 100 if len(close) >= 63 else None
    return {"1m": round(r1, 2) if r1 else None, "3m": round(r3, 2) if r3 else None}

def analyse_stock(ticker, bench_returns):
    df = fetch_data(ticker, period="2y")
    if df is None or len(df) < 60:
        return None

    close = df["Close"].squeeze()
    volume = df["Volume"].squeeze()
    current = float(close.iloc[-1])

    # 52-week & ATH
    high_52w = float(close[-252:].max()) if len(close) >= 252 else float(close.max())
    pct_from_52w = (current - high_52w) / high_52w * 100
    ath = float(close.max())
    pct_from_ath = (current - ath) / ath * 100

    # Returns
    ret_1m = (current / float(close.iloc[-21]) - 1) * 100 if len(close) >= 21 else None
    ret_3m = (current / float(close.iloc[-63]) - 1) * 100 if len(close) >= 63 else None

    # Outperformance
    op1 = (ret_1m - bench_returns["1m"]) if ret_1m and bench_returns.get("1m") else None
    op3 = (ret_3m - bench_returns["3m"]) if ret_3m and bench_returns.get("3m") else None

    # ── VOLUME SURGE ──
    # Compare today's volume vs 20-day average
    vol_today = float(volume.iloc[-1])
    vol_20d_avg = float(volume.iloc[-21:-1].mean()) if len(volume) >= 21 else None
    vol_surge_pct = ((vol_today - vol_20d_avg) / vol_20d_avg * 100) if vol_20d_avg and vol_20d_avg > 0 else None
    is_vol_surge = vol_surge_pct is not None and vol_surge_pct >= 10

    # Score
    score = 0
    if pct_from_52w >= -5:    score += 3
    elif pct_from_52w >= -10: score += 1
    if pct_from_ath >= -5:    score += 2
    if op1 and op1 > 0:       score += 2
    if op3 and op3 > 0:       score += 2
    if is_vol_surge:          score += 1  # bonus point for volume surge

    # Name
    try:
        name = yf.Ticker(ticker).info.get("shortName", ticker)
    except Exception:
        name = ticker

    return {
        "ticker": ticker,
        "name": name,
        "current": round(current, 2),
        "52w_high": round(high_52w, 2),
        "pct_from_52w": round(pct_from_52w, 2),
        "ath": round(ath, 2),
        "pct_from_ath": round(pct_from_ath, 2),
        "ret_1m": round(ret_1m, 2) if ret_1m else None,
        "ret_3m": round(ret_3m, 2) if ret_3m else None,
        "outperf_1m": round(op1, 2) if op1 else None,
        "outperf_3m": round(op3, 2) if op3 else None,
        "vol_today": int(vol_today),
        "vol_20d_avg": int(vol_20d_avg) if vol_20d_avg else None,
        "vol_surge_pct": round(vol_surge_pct, 1) if vol_surge_pct else None,
        "is_vol_surge": is_vol_surge,
        "score": score
    }

# ─────────────────────────────────────────────
# MAIN SCREENER
# ─────────────────────────────────────────────

def run_screener():
    all_results = {}
    for mkey, config in MARKETS.items():
        print(f"\n📊 Screening {config['label']}...")
        bench_returns = get_benchmark_returns(config["benchmark"])

        # Deduplicate: combine mcap + vol lists, tag each stock's source
        mcap_set = set(config["tickers_mcap"])
        vol_set  = set(config["tickers_vol"])
        all_tickers = list(mcap_set | vol_set)

        results = []
        for ticker in all_tickers:
            print(f"   → {ticker}", end=" ", flush=True)
            row = analyse_stock(ticker, bench_returns)
            if row:
                row["in_mcap"] = ticker in mcap_set
                row["in_vol"]  = ticker in vol_set
                results.append(row)
                surge = "🔥" if row["is_vol_surge"] else ""
                print(f"✓ {surge}")
            else:
                print("✗")

        results.sort(key=lambda x: x["score"], reverse=True)
        all_results[mkey] = {
            "label": config["label"],
            "benchmark_name": config["benchmark_name"],
            "benchmark_returns": bench_returns,
            "stocks": results
        }
    return all_results

# ─────────────────────────────────────────────
# HTML BUILDER
# ─────────────────────────────────────────────

def fmt(val, suffix="%", plus=True):
    if val is None:
        return "<span class='na'>—</span>"
    sign = "+" if val > 0 and plus else ""
    cls = "pos" if val > 0 else "neg" if val < 0 else "neu"
    return f"<span class='{cls}'>{sign}{val}{suffix}</span>"

def stars(score):
    capped = min(score, 10)
    full = capped // 2
    return "★" * full + "☆" * (5 - full)

def dot(pct):
    if pct >= -5:  return "<span class='dot-g'></span>"
    if pct >= -15: return "<span class='dot-y'></span>"
    return "<span class='dot-r'></span>"

def vol_fmt(v):
    if v is None: return "—"
    if v >= 1_000_000: return f"{v/1_000_000:.1f}M"
    if v >= 1_000: return f"{v/1_000:.0f}K"
    return str(v)

def build_table_rows(stocks, surge_only=False):
    rows = ""
    for s in stocks:
        if surge_only and not s["is_vol_surge"]:
            continue
        surge_badge = "<span class='surge-badge'>🔥 VOL SURGE</span>" if s["is_vol_surge"] else ""
        source_tags = ""
        if s.get("in_mcap"): source_tags += "<span class='tag-mcap'>MktCap</span>"
        if s.get("in_vol"):  source_tags += "<span class='tag-vol'>Vol</span>"
        rows += f"""
        <tr class="{'surge-row' if s['is_vol_surge'] else ''}">
          <td>
            <strong>{s['ticker']}</strong>
            <small>{s['name']}</small>
            <div style="margin-top:3px">{source_tags}</div>
          </td>
          <td>{s['current']}</td>
          <td>{dot(s['pct_from_52w'])} {fmt(s['pct_from_52w'])}</td>
          <td>{dot(s['pct_from_ath'])} {fmt(s['pct_from_ath'])}</td>
          <td>{fmt(s['ret_1m'])}</td>
          <td>{fmt(s['outperf_1m'])}</td>
          <td>{fmt(s['ret_3m'])}</td>
          <td>{fmt(s['outperf_3m'])}</td>
          <td>
            {vol_fmt(s['vol_today'])}<br>
            <small>avg {vol_fmt(s['vol_20d_avg'])}</small>
            {surge_badge}
          </td>
          <td class='stars'>{stars(s['score'])}</td>
        </tr>"""
    if not rows:
        rows = "<tr><td colspan='10' style='text-align:center;padding:2rem;color:var(--muted)'>No stocks meeting volume surge criteria today.</td></tr>"
    return rows

def build_html(data):
    now = datetime.utcnow().strftime("%d %b %Y %H:%M UTC")

    market_tabs = ""
    market_panels = ""

    for i, (mkey, mdata) in enumerate(data.items()):
        active = "active" if i == 0 else ""
        label = mdata["label"]
        bench = mdata["benchmark_name"]
        br = mdata["benchmark_returns"]
        stocks = mdata["stocks"]
        vol_surge_count = sum(1 for s in stocks if s["is_vol_surge"])

        market_tabs += f'<div class="tab {active}" onclick="showMarket(\'{mkey}\')">{label}</div>'

        b1 = fmt(br.get("1m"))
        b3 = fmt(br.get("3m"))

        all_rows    = build_table_rows(stocks, surge_only=False)
        surge_rows  = build_table_rows(stocks, surge_only=True)

        thead = """<thead><tr>
          <th>Stock</th><th>Price</th>
          <th>vs 52W High</th><th>vs ATH</th>
          <th>1M Return</th><th>1M vs Benchmark</th>
          <th>3M Return</th><th>3M vs Benchmark</th>
          <th>Volume</th><th>Rating</th>
        </tr></thead>"""

        market_panels += f"""
        <div id="panel-{mkey}" class="market-panel {active}">
          <div class="bench-bar">
            <span class="bench-label">Benchmark</span>
            <span class="bench-name">{bench}</span>
            <span class="sep">|</span>
            <span class="bench-label">1M:</span> {b1}
            <span class="sep">|</span>
            <span class="bench-label">3M:</span> {b3}
            <span class="sep">|</span>
            <span class="bench-label">Stocks screened:</span>
            <span class="bench-name">{len(stocks)}</span>
            <span class="sep">|</span>
            <span class="bench-label">Volume surges:</span>
            <span class="surge-count">🔥 {vol_surge_count}</span>
          </div>

          <div class="subtabs">
            <div class="subtab active" onclick="showSubtab(this, '{mkey}', 'all')">
              All Stocks <span class="count-pill">{len(stocks)}</span>
            </div>
            <div class="subtab" onclick="showSubtab(this, '{mkey}', 'surge')">
              🔥 Volume Surge <span class="count-pill">{vol_surge_count}</span>
            </div>
          </div>

          <div id="{mkey}-all" class="subtab-panel active">
            <div class="table-wrap">
              <table>{thead}<tbody>{all_rows}</tbody></table>
            </div>
          </div>

          <div id="{mkey}-surge" class="subtab-panel">
            <div class="surge-explain">
              Showing stocks where today's volume is at least <strong>10% above</strong>
              the 20-day average volume — a signal of unusual market interest.
            </div>
            <div class="table-wrap">
              <table>{thead}<tbody>{surge_rows}</tbody></table>
            </div>
          </div>
        </div>"""

    legend = """
    <section class="legend">
      <h3>📖 How to read this</h3>
      <div class="legend-grid">
        <div><span class="dot-g"></span> <strong>Green dot</strong> = within 5% of high</div>
        <div><span class="dot-y"></span> <strong>Yellow dot</strong> = within 15% of high</div>
        <div><span class="dot-r"></span> <strong>Red dot</strong> = more than 15% below high</div>
        <div><strong>vs Benchmark</strong> = beating the country's market index?</div>
        <div><strong>Volume</strong> = today vs 20-day average. 🔥 = 10%+ above average</div>
        <div><strong>MktCap</strong> tag = top 50 by market cap &nbsp; <strong>Vol</strong> tag = top 50 by volume</div>
        <div><strong>Rating ★</strong> = near highs + beating market + volume surge bonus</div>
        <div><strong>Volume Surge tab</strong> = unusual buying/selling activity today</div>
      </div>
    </section>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Global Stock Screener</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
:root {{
  --bg:#0d1117;--surface:#161b22;--surface2:#21262d;--border:#30363d;
  --text:#e6edf3;--muted:#8b949e;--accent:#58a6ff;
  --green:#3fb950;--red:#f85149;--gold:#f0c040;
  --surge:#ff6b35;
}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:var(--bg);color:var(--text);font-family:'DM Sans',sans-serif;font-size:13px;line-height:1.6}}
header{{background:linear-gradient(135deg,#0d1117,#161b22);border-bottom:1px solid var(--border);padding:1.5rem 2rem}}
header h1{{font-family:'DM Serif Display',serif;font-size:1.8rem;color:var(--accent)}}
header p{{color:var(--muted);font-size:0.82rem;margin-top:3px}}
.timestamp{{float:right;font-size:0.78rem;color:var(--muted);background:var(--surface2);padding:3px 10px;border-radius:20px;border:1px solid var(--border)}}
.tabs{{display:flex;border-bottom:1px solid var(--border);padding:0 2rem;overflow-x:auto;background:var(--surface)}}
.tab{{padding:.6rem 1.1rem;font-size:12px;color:var(--muted);cursor:pointer;border-bottom:2px solid transparent;white-space:nowrap;transition:color .15s}}
.tab.active{{color:var(--accent);border-bottom-color:var(--accent);font-weight:500}}
.tab:hover:not(.active){{color:var(--text)}}
.market-panel{{display:none;padding:1.2rem 2rem}}
.market-panel.active{{display:block}}
.bench-bar{{display:flex;align-items:center;gap:.8rem;flex-wrap:wrap;margin-bottom:1rem;padding:.6rem 1rem;background:var(--surface2);border-radius:8px;border:1px solid var(--border)}}
.bench-label{{font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:.04em}}
.bench-name{{font-weight:500;font-size:12px}}
.sep{{color:var(--border)}}
.surge-count{{color:var(--surge);font-weight:600;font-size:12px}}
.subtabs{{display:flex;gap:.5rem;margin-bottom:1rem}}
.subtab{{padding:.4rem 1rem;font-size:12px;border-radius:20px;border:1px solid var(--border);cursor:pointer;color:var(--muted);background:var(--surface2)}}
.subtab.active{{background:var(--accent);color:#0d1117;border-color:var(--accent);font-weight:500}}
.subtab:hover:not(.active){{color:var(--text)}}
.subtab-panel{{display:none}}
.subtab-panel.active{{display:block}}
.count-pill{{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:0 6px;font-size:10px;margin-left:4px}}
.surge-explain{{background:#ff6b3515;border:1px solid #ff6b3540;border-radius:8px;padding:.7rem 1rem;margin-bottom:1rem;font-size:12px;color:#ffb347}}
.table-wrap{{overflow-x:auto;border-radius:8px;border:1px solid var(--border)}}
table{{width:100%;border-collapse:collapse;background:var(--surface)}}
thead th{{background:var(--surface2);padding:.55rem .9rem;text-align:left;font-size:10px;font-weight:500;text-transform:uppercase;letter-spacing:.05em;color:var(--muted);white-space:nowrap;border-bottom:1px solid var(--border)}}
tbody tr{{border-bottom:1px solid var(--border);transition:background .1s}}
tbody tr:last-child{{border-bottom:none}}
tbody tr:hover{{background:var(--surface2)}}
tbody tr.surge-row{{background:#ff6b350a}}
tbody tr.surge-row:hover{{background:#ff6b3515}}
td{{padding:.55rem .9rem;vertical-align:middle}}
td small{{color:var(--muted);display:block;font-size:10px}}
.pos{{color:#3fb950;font-weight:500}}
.neg{{color:#f85149;font-weight:500}}
.neu{{color:var(--muted)}}
.na{{color:var(--muted);opacity:.5}}
.stars{{color:var(--gold);letter-spacing:1px}}
.dot-g{{display:inline-block;width:7px;height:7px;border-radius:50%;background:#3fb950;margin-right:3px}}
.dot-y{{display:inline-block;width:7px;height:7px;border-radius:50%;background:#e3b341;margin-right:3px}}
.dot-r{{display:inline-block;width:7px;height:7px;border-radius:50%;background:#f85149;margin-right:3px}}
.surge-badge{{display:inline-block;font-size:10px;background:#ff6b3525;color:#ff8c55;border:1px solid #ff6b3550;border-radius:4px;padding:1px 5px;margin-top:3px}}
.tag-mcap{{font-size:9px;background:#58a6ff20;color:#58a6ff;border:1px solid #58a6ff40;border-radius:3px;padding:1px 4px;margin-right:3px}}
.tag-vol{{font-size:9px;background:#3fb95020;color:#3fb950;border:1px solid #3fb95040;border-radius:3px;padding:1px 4px}}
.legend{{margin:1.5rem 2rem;background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:1.2rem 1.5rem}}
.legend h3{{font-family:'DM Serif Display',serif;margin-bottom:.7rem}}
.legend-grid{{display:grid;grid-template-columns:1fr 1fr;gap:.35rem .5rem;font-size:11px;color:var(--muted)}}
.legend-grid strong{{color:var(--text)}}
footer{{text-align:center;padding:1.5rem;color:var(--muted);font-size:11px;border-top:1px solid var(--border);margin-top:1rem}}
</style>
</head>
<body>
<header>
  <span class="timestamp">Updated: {now}</span>
  <h1>🌏 Global Stock Screener</h1>
  <p>Top 50 by Market Cap + Top 50 by Volume · Near 52W &amp; All-Time Highs · Beating Benchmark · 🔥 Volume Surges</p>
</header>
<div class="tabs">{market_tabs}</div>
<div id="panels">{market_panels}</div>
{legend}
<footer>Data from Yahoo Finance · Not financial advice · Auto-refreshed daily by GitHub Actions</footer>
<script>
function showMarket(m){{
  document.querySelectorAll('.market-panel').forEach(p=>p.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
  document.getElementById('panel-'+m).classList.add('active');
  event.target.classList.add('active');
}}
function showSubtab(el,market,sub){{
  const panel=document.getElementById('panel-'+market);
  panel.querySelectorAll('.subtab').forEach(t=>t.classList.remove('active'));
  panel.querySelectorAll('.subtab-panel').forEach(p=>p.classList.remove('active'));
  el.classList.add('active');
  document.getElementById(market+'-'+sub).classList.add('active');
}}
</script>
</body>
</html>"""

if __name__ == "__main__":
    results = run_screener()
    html = build_html(results)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("\n✅ index.html generated!")
