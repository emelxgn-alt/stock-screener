"""
Global Stock Screener v3
- Embeds all data as JSON into HTML template
- Line charts (3M price trend) + Bubble charts (return vs volume)
- US Sector ETF heatmap + chart + table
- Auto-sorted + user-sortable columns
"""

import yfinance as yf
import pandas as pd
import json
from datetime import datetime, timedelta

# ─────────────────────────────────────────────
# US SECTOR ETFs
# ─────────────────────────────────────────────

SECTOR_ETFS = {
    "XLK":  "Technology",
    "XLV":  "Healthcare",
    "XLF":  "Financials",
    "XLE":  "Energy",
    "XLI":  "Industrials",
    "XLY":  "Consumer Discret.",
    "XLP":  "Consumer Staples",
    "XLB":  "Materials",
    "XLRE": "Real Estate",
    "XLU":  "Utilities",
    "XLC":  "Communication",
}

# ─────────────────────────────────────────────
# MARKETS
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
            "RIOT","COIN","MU","KEY","RF","PARA","PLUG","FCEL","SPCE","SNDL"
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
            "2880.TW","1303.TW","1326.TW","2883.TW","5880.TW","2887.TW"
        ],
        "tickers_vol": [
            "2330.TW","2317.TW","2303.TW","2308.TW","2002.TW","2882.TW",
            "2881.TW","2891.TW","3481.TW","2886.TW","2884.TW","2883.TW",
            "2885.TW","2880.TW","2892.TW","1301.TW","1303.TW","2207.TW",
            "6770.TW","2382.TW","2454.TW","2379.TW","3711.TW","2357.TW",
            "2395.TW","2344.TW","4938.TW","3008.TW","2327.TW","2360.TW"
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
            "601989.SS","600309.SS","601186.SS","600028.SS","601390.SS",
            "600048.SS","600918.SS","601138.SS","600050.SS","601766.SS"
        ],
        "tickers_vol": [
            "600519.SS","600036.SS","601398.SS","600030.SS","601939.SS",
            "601288.SS","600016.SS","601166.SS","600031.SS","601601.SS",
            "601688.SS","600309.SS","601318.SS","600887.SS","603288.SS",
            "600028.SS","601088.SS","601186.SS","600048.SS","601668.SS",
            "601989.SS","600104.SS","601336.SS","601766.SS","600690.SS",
            "600406.SS","600050.SS","601818.SS","601328.SS","601998.SS"
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
            "1038.HK","0006.HK","0017.HK","0083.HK","0019.HK","0004.HK"
        ],
        "tickers_vol": [
            "0700.HK","0941.HK","3690.HK","1398.HK","0939.HK","0388.HK",
            "0005.HK","2318.HK","0883.HK","1299.HK","0016.HK","0011.HK",
            "0012.HK","2628.HK","0762.HK","0002.HK","0003.HK","0006.HK",
            "1177.HK","0823.HK","1093.HK","0688.HK","0066.HK","1038.HK",
            "0027.HK","0017.HK","0083.HK","0019.HK","3988.HK","2388.HK"
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
            "Q5T.SI","5E2.SI","S63.SI","Y92.SI"
        ],
        "tickers_vol": [
            "D05.SI","O39.SI","U11.SI","Z74.SI","S68.SI","C52.SI","V03.SI",
            "BN4.SI","BS6.SI","C09.SI","F34.SI","G13.SI","H78.SI","J36.SI",
            "U96.SI","A17U.SI","C38U.SI","ME8U.SI","N2IU.SI","BUOU.SI",
            "T82U.SI","K71U.SI","M44U.SI","SK6U.SI","AW9U.SI","AJBU.SI",
            "Q5T.SI","5E2.SI","S63.SI","Y92.SI"
        ]
    }
}

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def fetch(ticker, period="1y"):
    try:
        df = yf.download(ticker, period=period, auto_adjust=True, progress=False)
        return None if df.empty else df
    except:
        return None

def pct_return(close, days):
    if len(close) < days + 1:
        return None
    return round((float(close.iloc[-1]) / float(close.iloc[-days]) - 1) * 100, 2)

def ytd_return(df):
    try:
        year_start = datetime(datetime.now().year, 1, 1)
        df.index = pd.to_datetime(df.index)
        past = df[df.index >= year_start]
        if past.empty:
            return None
        first = float(past["Close"].squeeze().iloc[0])
        last  = float(past["Close"].squeeze().iloc[-1])
        return round((last / first - 1) * 100, 2)
    except:
        return None

def get_benchmark(ticker):
    df = fetch(ticker, "1y")
    if df is None:
        return {"1m": None, "3m": None, "ytd": None}
    c = df["Close"].squeeze()
    return {
        "1m":  pct_return(c, 21),
        "3m":  pct_return(c, 63),
        "ytd": ytd_return(df)
    }

def get_price_trend(df, days=63):
    """Return last N days of closing prices as list of {date, price}"""
    try:
        c = df["Close"].squeeze().tail(days)
        base = float(c.iloc[0])
        return [
            {"d": str(idx.date()), "p": round((float(v) / base - 1) * 100, 2)}
            for idx, v in c.items()
        ]
    except:
        return []

def analyse_stock(ticker, bench_ret):
    df = fetch(ticker, "2y")
    if df is None or len(df) < 60:
        return None

    close  = df["Close"].squeeze()
    volume = df["Volume"].squeeze()
    cur    = float(close.iloc[-1])

    h52  = float(close[-252:].max()) if len(close) >= 252 else float(close.max())
    ath  = float(close.max())
    p52  = round((cur - h52) / h52 * 100, 2)
    path = round((cur - ath) / ath * 100, 2)

    r1m = pct_return(close, 21)
    r3m = pct_return(close, 63)
    rytd = ytd_return(df)

    op1 = round(r1m - bench_ret["1m"], 2) if r1m and bench_ret.get("1m") else None
    op3 = round(r3m - bench_ret["3m"], 2) if r3m and bench_ret.get("3m") else None

    vol_today   = float(volume.iloc[-1])
    vol_20d_avg = float(volume.iloc[-21:-1].mean()) if len(volume) >= 21 else None
    vol_surge   = round((vol_today / vol_20d_avg - 1) * 100, 1) if vol_20d_avg and vol_20d_avg > 0 else None
    is_surge    = vol_surge is not None and vol_surge >= 10

    score = 0
    if p52  >= -5:  score += 3
    elif p52 >= -10: score += 1
    if path >= -5:  score += 2
    if op1 and op1 > 0: score += 2
    if op3 and op3 > 0: score += 2
    if is_surge:    score += 1

    trend = get_price_trend(df, 63)

    try:
        name = yf.Ticker(ticker).info.get("shortName", ticker)
    except:
        name = ticker

    return {
        "ticker": ticker, "name": name, "price": round(cur, 2),
        "p52w": p52, "path": path,
        "r1m": r1m, "r3m": r3m, "rytd": rytd,
        "op1": op1, "op3": op3,
        "vol": int(vol_today),
        "vol_avg": int(vol_20d_avg) if vol_20d_avg else 0,
        "vol_surge": vol_surge,
        "is_surge": is_surge,
        "score": score,
        "trend": trend
    }

# ─────────────────────────────────────────────
# SECTOR ETF SCREENER
# ─────────────────────────────────────────────

def screen_sectors():
    spx = get_benchmark("^GSPC")
    results = []
    for ticker, name in SECTOR_ETFS.items():
        print(f"   → {ticker}", end=" ", flush=True)
        df = fetch(ticker, "2y")
        if df is None:
            print("✗"); continue
        c = df["Close"].squeeze()
        cur = float(c.iloc[-1])
        r1m  = pct_return(c, 21)
        r3m  = pct_return(c, 63)
        rytd = ytd_return(df)
        vs1  = round(r1m  - spx["1m"],  2) if r1m  and spx.get("1m")  else None
        vs3  = round(r3m  - spx["3m"],  2) if r3m  and spx.get("3m")  else None
        vsytd= round(rytd - spx["ytd"], 2) if rytd and spx.get("ytd") else None
        trend = get_price_trend(df, 63)
        results.append({
            "ticker": ticker, "name": name, "price": round(cur, 2),
            "r1m": r1m, "r3m": r3m, "rytd": rytd,
            "vs1": vs1, "vs3": vs3, "vsytd": vsytd,
            "trend": trend
        })
        print("✓")
    results.sort(key=lambda x: x["r1m"] or -999, reverse=True)
    return {"sectors": results, "spx": spx}

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def run_screener():
    all_results = {}
    for mkey, config in MARKETS.items():
        print(f"\n📊 {config['label']}...")
        bench = get_benchmark(config["benchmark"])
        seen  = set()
        tickers = []
        for t in config["tickers_mcap"]:
            if t not in seen: tickers.append((t, True, False)); seen.add(t)
        for t in config["tickers_vol"]:
            if t not in seen: tickers.append((t, False, True)); seen.add(t)
            else:
                tickers = [(x[0], x[1], True) if x[0] == t else x for x in tickers]

        stocks = []
        for ticker, in_mc, in_v in tickers:
            print(f"   → {ticker}", end=" ", flush=True)
            row = analyse_stock(ticker, bench)
            if row:
                row["in_mcap"] = in_mc
                row["in_vol"]  = in_v
                stocks.append(row)
                print(f"✓{'🔥' if row['is_surge'] else ''}")
            else:
                print("✗")

        stocks.sort(key=lambda x: x["score"], reverse=True)
        all_results[mkey] = {
            "label": config["label"],
            "bench_name": config["benchmark_name"],
            "bench": bench,
            "stocks": stocks
        }

    print("\n📊 US Sector ETFs...")
    sector_data = screen_sectors()
    return all_results, sector_data

# ─────────────────────────────────────────────
# READ TEMPLATE & INJECT DATA
# ─────────────────────────────────────────────

def build_html(markets, sector_data):
    with open("template.html", "r", encoding="utf-8") as f:
        tmpl = f.read()
    now = datetime.utcnow().strftime("%d %b %Y %H:%M UTC")
    payload = json.dumps({"markets": markets, "sectors": sector_data, "updated": now},
                         ensure_ascii=False)
    return tmpl.replace("__DATA_PLACEHOLDER__", payload)

if __name__ == "__main__":
    markets, sectors = run_screener()
    html = build_html(markets, sectors)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("\n✅ index.html generated!")
