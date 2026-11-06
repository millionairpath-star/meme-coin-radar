# 👻 Meme Coin Radar

AI-powered meme coin safety scanner. Check any meme coin for scams, rugs, and profit potential.

## Live Demo

Deploy free on Streamlit Cloud:
1. Fork this repo to your GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Select this repo, set main file path to `app.py`
4. Get a public URL — works on phone, PC, tablet

## Install as App (PWA)

- **Android:** Open URL in Chrome → Menu → "Install app"
- **iPhone:** Open URL in Safari → Share → "Add to Home Screen"
- **PC:** Open URL in Chrome → Click install icon in address bar

No Play Store needed. No APK build needed. Works offline too.

## Features

| Tab | Free | Premium |
|-----|------|---------|
| Scanner | ✅ 8 coins/search | 🔒 Unlimited |
| Hype Radar | ✅ | ✅ |
| Deep Dive Audit | ✅ EVM chains | 🔒 + Solana |
| Website Checker | ✅ | ✅ |
| Profit Estimator | ✅ | ✅ |
| Watchlist | ✅ 10 coins | 🔒 Unlimited |
| Alerts | ✅ Local | 🔒 Telegram |
| AI Pump Signals | 🔒 | ✅ |
| Whale Tracker | 🔒 | ✅ |
| Rug-Pull Predictor | 🔒 | ✅ |
| Auto-Trade Bot | 🔒 | ✅ |

## Trust Score System (0-100)

| Score | Grade | Meaning |
|-------|-------|---------|
| 80+ | A | Safe |
| 65-79 | B | Likely safe |
| 50-64 | C | Risky |
| 35-49 | D | High risk |
| 0-34 | F | Danger |

## Data Sources (all free, no API keys needed)

- **DexScreener API** — live price, volume, liquidity, buy/sell ratio, market cap
- **GoPlus Security API** — honeypot, mint, hidden owner, tax, holder count, rug pull flags
- **TokenSniffer** — automated audit score (web link)

## Setup (Local)

```bash
cd meme-coin-tool
pip install -r requirements.txt
streamlit run app.py
```

App opens at `http://localhost:8501`

## Setup (Streamlit Cloud — Free Hosting)

1. Create GitHub account: [github.com/signup](https://github.com/signup)
2. Upload this folder to a new repo
3. Go to [share.streamlit.io](https://share.streamlit.io)
4. Sign in with GitHub
5. Select your repo, set path to `app.py`
6. Click Deploy — done!

## File Structure

```
meme-coin-tool/
├── app.py              # Main Streamlit app (7 tabs)
├── apis.py             # DexScreener + GoPlus API layer
├── premium.py          # Premium features wall
├── pwa_setup.py        # PWA install banner
├── cron_meme_radar.py  # Daily cron job for alerts
├── requirements.txt    # Python dependencies
├── .streamlit/
│   └── config.toml     # Dark theme config
├── static/
│   ├── manifest.json   # PWA manifest
│   └── sw.js           # Service worker (offline)
└── README.md
```

## Disclaimer

This tool provides data only. Not financial advice. Always DYOR.
