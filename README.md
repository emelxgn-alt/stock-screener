# 🌏 Global Stock Screener

Automatically screens stocks across US, Taiwan, China, Hong Kong and Singapore for:
- Stocks near their 52-week high and all-time high
- Stocks outperforming their country benchmark over 1M and 3M

📊 **[View Live Dashboard](https://emelxgn-alt.github.io/stock-screener/)**

## Folder Structure

```
stock-screener/
├── .github/
│   └── workflows/
│       └── run_screener.yml   ← Robot schedule
├── screener.py                ← The brain
├── requirements.txt           ← Python dependencies
└── index.html                 ← Auto-generated dashboard
```

## How it works
1. GitHub Actions runs the screener every day at 1am UTC (9am Singapore time)
2. `screener.py` fetches live data from Yahoo Finance
3. Saves results as `index.html`
4. GitHub Pages serves the HTML as a live website

> Data from Yahoo Finance. Not financial advice.
