# 👻 Meme Coin Radar

AI-powered meme coin safety scanner. Check any meme coin for scams, rugs, and profit potential.

## Features

| Tab | What it does |
|-----|-------------|
| Scanner | Search any coin, get trust score + full audit |
| Hype Radar | Trending, boosted, and new tokens |
| Deep Dive | Contract address full security audit |
| Website Checker | Phishing + scam website detection |
| Profit Estimator | Entry/exit/TSL/TP calculator with tax |
| Watchlist | Track coins with live price refresh |
| Alerts | Price and security alert setup |

## Data Sources (all free, no API keys needed)

- **DexScreener API** — live price, volume, liquidity, buy/sell ratio, market cap
- **GoPlus Security API** — honeypot, mint, hidden owner, tax, holder count, rug pull flags
- **TokenSniffer** — automated audit score (web link)

## Trust Score System (0-100)

| Score | Grade | Meaning |
|-------|-------|---------|
| 80+ | A | Safe |
| 65-79 | B | Likely safe |
| 50-64 | C | Risky |
| 35-49 | D | High risk |
| 0-34 | F | Danger |

## Setup

```bash
cd meme-coin-tool
pip install -r requirements.txt
streamlit run app.py
```

App opens at `http://localhost:8501`

## How to Use

1. **Scanner tab** — type coin name (e.g. PEPE), get ranked list by trust score
2. **Deep Dive tab** — paste contract address + select chain for full audit
3. **Hype Radar tab** — find trending and boosted coins
4. **Website Checker tab** — paste coin website URL to check for phishing
5. **Profit Estimator tab** — set entry price, TP, SL, tax to calculate P&L
6. **Watchlist tab** — add coins from scanner, refresh prices anytime
7. **Alerts tab** — set price/volume/liquidity alerts

## Disclaimer

This tool provides data only. Not financial advice. Always DYOR.
