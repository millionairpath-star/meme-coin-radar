"""
Meme Coin Radar — Cron job for daily alerts
Runs via Kiro Crew Schedule. Checks watchlist + sends alerts.
"""
import json
import os
import requests
from datetime import datetime

WATCHLIST_FILE = os.path.join(os.path.dirname(__file__), "watchlist.json")
ALERTS_FILE = os.path.join(os.path.dirname(__file__), "alerts.json")
DEXSCREENER_BASE = "https://api.dexscreener.com"


def load_json(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return []


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def get_token_price(chain, address):
    """Get current price from DexScreener."""
    try:
        r = requests.get(f"{DEXSCREENER_BASE}/token-pairs/v1/{chain}/{address}", timeout=10)
        r.raise_for_status()
        pairs = r.json()
        if not pairs:
            return None
        best = max(pairs, key=lambda p: (p.get("liquidity", {}) or {}).get("usd", 0) if isinstance(p.get("liquidity"), dict) else 0)
        return {
            "price": float(best.get("priceUsd", 0) or 0),
            "change_24h": (best.get("priceChange", {}) or {}).get("h24", 0) if best.get("priceChange") else 0,
            "liquidity": (best.get("liquidity", {}) or {}).get("usd", 0) if best.get("liquidity") else 0,
            "volume_24h": (best.get("volume", {}) or {}).get("h24", 0) if best.get("volume") else 0,
        }
    except Exception:
        return None


def check_alerts(watchlist, alerts):
    """Check all alerts against current prices. Returns list of triggered alerts."""
    triggered = []
    for a in alerts:
        if a.get("triggered"):
            continue
        # Find matching coin in watchlist
        coin = next((w for w in watchlist if w.get("symbol") == a["symbol"]), None)
        if not coin:
            continue
        data = get_token_price(coin["chain"], coin["address"])
        if not data:
            continue
        price = data["price"]
        change = data["change_24h"]
        liq = data["liquidity"]
        vol = data["volume_24h"]
        old_price = coin.get("current_price", coin.get("price", 0))

        condition_met = False
        atype = a["type"]
        val = a["value"]

        if atype == "Price above" and price >= val:
            condition_met = True
        elif atype == "Price below" and price <= val:
            condition_met = True
        elif atype == "24h change above %" and change >= val:
            condition_met = True
        elif atype == "24h change below %" and change <= val:
            condition_met = True
        elif atype == "Liquidity drop > 20%":
            old_liq = coin.get("liquidity_usd", 0)
            if old_liq > 0 and (old_liq - liq) / old_liq * 100 > 20:
                condition_met = True
        elif atype == "Volume spike > 2x":
            old_vol = coin.get("vol_24h", 0)
            if old_vol > 0 and vol > old_vol * 2:
                condition_met = True

        if condition_met:
            a["triggered"] = True
            a["triggered_at"] = datetime.now().isoformat()
            a["current_price"] = price
            triggered.append({
                "symbol": a["symbol"],
                "type": a["type"],
                "value": val,
                "current_price": price,
                "change_24h": change,
            })

    return triggered


def run_cron(ctx):
    """Entry point for Kiro Crew cron job."""
    watchlist = load_json(WATCHLIST_FILE)
    alerts = load_json(ALERTS_FILE)

    if not watchlist:
        ctx.notify("Meme Coin Radar: Watchlist empty. Add coins first.")
        return

    if not alerts:
        # Still send a daily price update
        msg_lines = ["📊 **Daily Meme Coin Watchlist Update**\n"]
        for w in watchlist[:10]:
            data = get_token_price(w["chain"], w["address"])
            if data:
                old = w.get("current_price", w.get("price", 0))
                change_pct = ((data["price"] - old) / old * 100) if old > 0 else 0
                icon = "🟢" if change_pct >= 0 else "🔴"
                msg_lines.append(
                    f"{icon} **{w['symbol']}** — ${data['price']:.8f} ({change_pct:+.1f}%) | Liq: ${data['liquidity']:,.0f}"
                )
                w["current_price"] = data["price"]
                w["price_change_24h"] = data["change_24h"]
                w["liquidity_usd"] = data["liquidity"]
                w["vol_24h"] = data["volume_24h"]

        save_json(WATCHLIST_FILE, watchlist)
        ctx.notify("\n".join(msg_lines))
        return

    # Check alerts
    triggered = check_alerts(watchlist, alerts)
    save_json(ALERTS_FILE, alerts)
    save_json(WATCHLIST_FILE, watchlist)

    if triggered:
        msg_lines = ["🚨 **ALERT TRIGGERED!**\n"]
        for t in triggered:
            msg_lines.append(f"**{t['symbol']}** — {t['type']} {t['value']} | Price: ${t['current_price']:.8f} | 24h: {t['change_24h']}%")
        ctx.notify("\n".join(msg_lines))
    else:
        # Send daily update
        msg_lines = ["📊 **Daily Update — No alerts triggered**\n"]
        for w in watchlist[:5]:
            data = get_token_price(w["chain"], w["address"])
            if data:
                old = w.get("current_price", w.get("price", 0))
                change_pct = ((data["price"] - old) / old * 100) if old > 0 else 0
                icon = "🟢" if change_pct >= 0 else "🔴"
                msg_lines.append(f"{icon} {w['symbol']}: ${data['price']:.8f} ({change_pct:+.1f}%)")
        ctx.notify("\n".join(msg_lines))
