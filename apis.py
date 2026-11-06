"""
Meme Coin Hunter API Layer
Free APIs: DexScreener (no key) + GoPlus Security (no key)
"""
import requests
import time
from functools import lru_cache

# ─── DexScreener ──────────────────────────────────────────────
DEXSCREENER_BASE = "https://api.dexscreener.com"


def dexscreener_search(query: str) -> list:
    """Search pairs by name/symbol. Returns list of pair dicts."""
    try:
        r = requests.get(f"{DEXSCREENER_BASE}/latest/dex/search",
                         params={"q": query}, timeout=10)
        r.raise_for_status()
        data = r.json()
        return data.get("pairs", []) or []
    except Exception as e:
        return [{"error": str(e)}]


def dexscreener_token_pairs(chain_id: str, token_address: str) -> list:
    """Get all pools for a token on a chain."""
    try:
        r = requests.get(f"{DEXSCREENER_BASE}/token-pairs/v1/{chain_id}/{token_address}",
                         timeout=10)
        r.raise_for_status()
        return r.json() if r.json() else []
    except Exception as e:
        return [{"error": str(e)}]


def dexscreener_trending_boosted() -> list:
    """Get tokens with most active boosts (hyped tokens)."""
    try:
        r = requests.get(f"{DEXSCREENER_BASE}/token-boosts/top/v1", timeout=10)
        r.raise_for_status()
        return r.json() or []
    except Exception as e:
        return [{"error": str(e)}]


def dexscreener_latest_boosted() -> list:
    """Get latest boosted tokens (new hype)."""
    try:
        r = requests.get(f"{DEXSCREENER_BASE}/token-boosts/latest/v1", timeout=10)
        r.raise_for_status()
        return r.json() or []
    except Exception as e:
        return [{"error": str(e)}]


def dexscreener_latest_profiles() -> list:
    """Get latest token profiles (newly listed with info)."""
    try:
        r = requests.get(f"{DEXSCREENER_BASE}/token-profiles/latest/v1", timeout=10)
        r.raise_for_status()
        return r.json() or []
    except Exception as e:
        return [{"error": str(e)}]


def dexscreener_trending_metas() -> list:
    """Get trending narratives/metas."""
    try:
        r = requests.get(f"{DEXSCREENER_BASE}/metas/trending/v1", timeout=10)
        r.raise_for_status()
        return r.json() or []
    except Exception as e:
        return [{"error": str(e)}]


# ─── GoPlus Security ──────────────────────────────────────────
GOPLUS_BASE = "https://api.gopluslabs.io/api/v1"

# Chain ID mapping (common ones for meme coins)
CHAIN_MAP = {
    "ethereum": 1,
    "bsc": 56,
    "solana": "solana",  # separate endpoint
    "polygon": 137,
    "arbitrum": 42161,
    "base": 8453,
    "optimism": 10,
    "avalanche": 43114,
    "fantom": 250,
    "linea": 59144,
    "blast": 81457,
    "scroll": 534352,
    "mantle": 5000,
    "cronos": 25,
    "moonbeam": 1284,
}


def goplus_token_security(chain_id, contract_address: str) -> dict:
    """Get full security data from GoPlus for EVM chains."""
    try:
        r = requests.get(f"{GOPLUS_BASE}/token_security/{chain_id}",
                         params={"contract_addresses": contract_address},
                         timeout=15)
        r.raise_for_status()
        data = r.json()
        result = data.get("result", {})
        # result is keyed by contract address (lowercase)
        if result:
            key = list(result.keys())[0]
            return result[key] or {}
        return {}
    except Exception as e:
        return {"error": str(e)}


def goplus_solana_security(token_address: str) -> dict:
    """Get security data for Solana tokens (beta endpoint)."""
    try:
        r = requests.get(f"{GOPLUS_BASE}/solana_token_security",
                         params={"contract_addresses": token_address},
                         timeout=15)
        r.raise_for_status()
        data = r.json()
        result = data.get("result", {})
        if result:
            key = list(result.keys())[0]
            return result[key] or {}
        return {}
    except Exception as e:
        return {"error": str(e)}


def goplus_phishing_check(url: str) -> dict:
    """Check if a website URL is a known phishing site."""
    try:
        r = requests.get(f"{GOPLUS_BASE}/phishing_site",
                         params={"url": url},
                         timeout=10)
        r.raise_for_status()
        return r.json().get("result", {})
    except Exception as e:
        return {"error": str(e)}


def get_security_data(chain_id_str: str, contract_address: str) -> dict:
    """Wrapper: route to EVM or Solana endpoint based on chain."""
    if chain_id_str.lower() == "solana":
        return goplus_solana_security(contract_address)
    # Map chain name to numeric ID
    cid = CHAIN_MAP.get(chain_id_str.lower(), chain_id_str)
    return goplus_token_security(cid, contract_address)


# ─── TokenSniffer (link only, API is paid) ────────────────────
def tokensniffer_url(chain: str, contract: str) -> str:
    """Generate TokenSniffer web link for manual audit check."""
    chain_map = {
        "ethereum": "ethereum",
        "bsc": "binancesmartchain",
        "polygon": "polygon",
        "arbitrum": "arbitrum",
        "base": "base",
        "optimism": "optimism",
        "avalanche": "avalanche",
        "solana": "solana",
    }
    c = chain_map.get(chain.lower(), chain.lower())
    return f"https://tokensniffer.com/token/{c}/{contract}"


# ─── Combined Analysis ───────────────────────────────────────
def analyze_pair(pair: dict) -> dict:
    """Extract key metrics from a DexScreener pair."""
    if "error" in pair:
        return pair

    base = pair.get("baseToken", {})
    quote = pair.get("quoteToken", {})
    txns = pair.get("txns", {})
    vol = pair.get("volume", {})
    change = pair.get("priceChange", {})
    liq = pair.get("liquidity", {})
    info = pair.get("info", {})

    # 24h buy/sell ratio
    t24 = txns.get("h24", {})
    buys_24h = t24.get("buys", 0)
    sells_24h = t24.get("sells", 0)
    total_24h = buys_24h + sells_24h
    buy_pct = (buys_24h / total_24h * 100) if total_24h > 0 else 50

    # 5m and 1h buy ratio for momentum
    t5 = txns.get("m5", {})
    t1 = txns.get("h1", {})
    buy_pct_5m = (t5.get("buys", 0) / (t5.get("buys", 0) + t5.get("sells", 0)) * 100) if (t5.get("buys", 0) + t5.get("sells", 0)) > 0 else 50
    buy_pct_1h = (t1.get("buys", 0) / (t1.get("buys", 0) + t1.get("sells", 0)) * 100) if (t1.get("buys", 0) + t1.get("sells", 0)) > 0 else 50

    # Price changes
    price_change_5m = change.get("m5", 0) if change else 0
    price_change_1h = change.get("h1", 0) if change else 0
    price_change_6h = change.get("h6", 0) if change else 0
    price_change_24h = change.get("h24", 0) if change else 0

    # Liquidity
    liq_usd = liq.get("usd", 0) if liq else 0

    # Volume
    vol_24h = vol.get("h24", 0) if vol else 0
    vol_6h = vol.get("h6", 0) if vol else 0
    vol_1h = vol.get("h1", 0) if vol else 0
    vol_5m = vol.get("m5", 0) if vol else 0

    # Market cap & FDV
    mcap = pair.get("marketCap", 0) or 0
    fdv = pair.get("fdv", 0) or 0

    # Pair age
    created = pair.get("pairCreatedAt", 0)
    age_hours = ((time.time() * 1000 - created) / 3_600_000) if created else 0

    # Website & socials
    websites = info.get("websites", []) if info else []
    socials = info.get("socials", []) if info else []
    website_url = websites[0]["url"] if websites else ""

    return {
        "chain": pair.get("chainId", ""),
        "dex": pair.get("dexId", ""),
        "pair_url": pair.get("url", ""),
        "pair_address": pair.get("pairAddress", ""),
        "token_name": base.get("name", ""),
        "token_symbol": base.get("symbol", ""),
        "token_address": base.get("address", ""),
        "quote_symbol": quote.get("symbol", ""),
        "price_usd": float(pair.get("priceUsd", 0) or 0),
        "price_native": pair.get("priceNative", ""),
        "liquidity_usd": liq_usd,
        "market_cap": mcap,
        "fdv": fdv,
        "vol_5m": vol_5m,
        "vol_1h": vol_1h,
        "vol_6h": vol_6h,
        "vol_24h": vol_24h,
        "buys_24h": buys_24h,
        "sells_24h": sells_24h,
        "buy_pct_24h": round(buy_pct, 1),
        "buy_pct_5m": round(buy_pct_5m, 1),
        "buy_pct_1h": round(buy_pct_1h, 1),
        "price_change_5m": price_change_5m,
        "price_change_1h": price_change_1h,
        "price_change_6h": price_change_6h,
        "price_change_24h": price_change_24h,
        "age_hours": round(age_hours, 1),
        "website": website_url,
        "socials": socials,
        "boosts": pair.get("boosts", {}).get("active", 0) if pair.get("boosts") else 0,
        "labels": pair.get("labels", []) or [],
    }


def full_analysis(chain: str, token_address: str) -> dict:
    """
    Combined DexScreener + GoPlus analysis for a token.
    Returns market data + security data + trust score.
    """
    # Get market data from DexScreener
    pairs = dexscreener_token_pairs(chain, token_address)
    if pairs and "error" not in pairs[0]:
        best_pair = max(pairs, key=lambda p: (p.get("liquidity", {}) or {}).get("usd", 0) if isinstance(p.get("liquidity"), dict) else 0)
        market = analyze_pair(best_pair)
    else:
        market = {"error": "No pairs found on DexScreener"}

    # Get security data from GoPlus
    security = get_security_data(chain, token_address)

    # Calculate trust score
    trust = calculate_trust_score(market, security)

    # TokenSniffer link
    ts_link = tokensniffer_url(chain, token_address)

    return {
        "market": market,
        "security": security,
        "trust_score": trust,
        "tokensniffer_url": ts_link,
    }


def calculate_trust_score(market: dict, security: dict) -> dict:
    """
    Calculate a trust score 0-100 based on security + market signals.
    Higher = safer. Returns score + breakdown.
    """
    score = 0
    max_score = 100
    breakdown = []

    # ─── Security checks (60 points max) ───────────────────
    if "error" in security:
        breakdown.append(("Security data unavailable", 0, 60))
    else:
        # Open source (10 pts)
        if security.get("is_open_source") == "1":
            score += 10
            breakdown.append(("Contract open source", 10, 10))
        else:
            breakdown.append(("Contract NOT open source", 0, 10))

        # Not honeypot (15 pts)
        if security.get("is_honeypot") == "0":
            score += 15
            breakdown.append(("Not honeypot", 15, 15))
        elif security.get("is_honeypot") == "1":
            breakdown.append(("HONEYPOT DETECTED", 0, 15))
        else:
            breakdown.append(("Honeypot status unknown", 0, 15))

        # Not mintable (10 pts)
        if security.get("is_mintable") == "0":
            score += 10
            breakdown.append(("Not mintable", 10, 10))
        else:
            breakdown.append(("Mintable - owner can print tokens", 0, 10))

        # No hidden owner (10 pts)
        if security.get("hidden_owner") == "0":
            score += 10
            breakdown.append(("No hidden owner", 10, 10))
        else:
            breakdown.append(("Hidden owner detected", 0, 10))

        # Ownership renounced (5 pts bonus)
        if security.get("is_owner_multisig") == "1":
            score += 5
            breakdown.append(("Owner is multisig", 5, 5))
        elif security.get("is_in_white_list") == "1":
            score += 3
            breakdown.append(("Whitelisted by GoPlus", 3, 5))
        else:
            breakdown.append(("Owner status unclear", 0, 5))

        # Buy tax reasonable (5 pts)
        buy_tax = float(security.get("buy_tax") or 0)
        if buy_tax <= 5:
            score += 5
            breakdown.append((f"Buy tax {buy_tax}%", 5, 5))
        elif buy_tax <= 10:
            score += 3
            breakdown.append((f"Buy tax {buy_tax}% (high)", 3, 5))
        else:
            breakdown.append((f"Buy tax {buy_tax}% (very high!)", 0, 5))

        # Sell tax reasonable (5 pts)
        sell_tax = float(security.get("sell_tax") or 0)
        if sell_tax <= 5:
            score += 5
            breakdown.append((f"Sell tax {sell_tax}%", 5, 5))
        elif sell_tax <= 10:
            score += 3
            breakdown.append((f"Sell tax {sell_tax}% (high)", 3, 5))
        else:
            breakdown.append((f"Sell tax {sell_tax}% (very high!)", 0, 5))

        # Not proxy (5 pts)
        if security.get("is_proxy") == "0":
            score += 5
            breakdown.append(("Not proxy contract", 5, 5))
        else:
            breakdown.append(("Proxy contract (risky)", 0, 5))

        # Not anti-whale / anti-sell (5 pts)
        if security.get("is_anti_whale") == "0":
            score += 5
            breakdown.append(("No anti-whale limits", 5, 5))
        else:
            breakdown.append(("Anti-whale limits exist", 0, 5))

        # No blacklisted function (5 pts)
        if security.get("is_blacklisted") == "0":
            score += 5
            breakdown.append(("No blacklist function", 5, 5))
        else:
            breakdown.append(("Blacklist function detected", 0, 5))

        # Can take back ownership (5 pts)
        if security.get("can_take_back_ownership") == "0":
            score += 5
            breakdown.append(("Cannot reclaim ownership", 5, 5))
        else:
            breakdown.append(("Can reclaim ownership (risky)", 0, 5))

        # Not transfer pausable (5 pts)
        if security.get("is_transfer_pausable") == "0":
            score += 5
            breakdown.append(("Transfers not pausable", 5, 5))
        else:
            breakdown.append(("Transfers can be paused", 0, 5))

        # Not personal interest (5 pts)
        if security.get("is_personal_interest") == "0":
            score += 5
            breakdown.append(("No suspicious interest patterns", 5, 5))
        else:
            breakdown.append(("Suspicious interest pattern", 0, 5))

    # ─── Market checks (40 points max) ──────────────────────
    if "error" not in market:
        # Liquidity > $50k (10 pts)
        liq = market.get("liquidity_usd", 0)
        if liq >= 100000:
            score += 10
            breakdown.append((f"Liquidity ${liq:,.0f} (excellent)", 10, 10))
        elif liq >= 50000:
            score += 7
            breakdown.append((f"Liquidity ${liq:,.0f} (good)", 7, 10))
        elif liq >= 10000:
            score += 4
            breakdown.append((f"Liquidity ${liq:,.0f} (low)", 4, 10))
        else:
            breakdown.append((f"Liquidity ${liq:,.0f} (very low!)", 0, 10))

        # Volume 24h > liquidity (10 pts)
        vol_24 = market.get("vol_24h", 0)
        if vol_24 > liq:
            score += 10
            breakdown.append(("24h volume > liquidity (high activity)", 10, 10))
        elif vol_24 > liq * 0.5:
            score += 7
            breakdown.append(("24h volume good", 7, 10))
        elif vol_24 > 0:
            score += 3
            breakdown.append(("Some volume", 3, 10))
        else:
            breakdown.append(("No volume", 0, 10))

        # Buy pressure > 55% (10 pts)
        buy_pct = market.get("buy_pct_24h", 50)
        if buy_pct >= 60:
            score += 10
            breakdown.append((f"Buy pressure {buy_pct}% (strong)", 10, 10))
        elif buy_pct >= 55:
            score += 7
            breakdown.append((f"Buy pressure {buy_pct}%", 7, 10))
        elif buy_pct >= 45:
            score += 5
            breakdown.append((f"Buy pressure {buy_pct}% (balanced)", 5, 10))
        else:
            breakdown.append((f"Buy pressure {buy_pct}% (sells > buys!)", 0, 10))

        # Age > 24h (5 pts) — very new tokens are riskier
        age = market.get("age_hours", 0)
        if age >= 168:  # 7 days
            score += 5
            breakdown.append((f"Age {age:.0f}h (7+ days)", 5, 5))
        elif age >= 24:
            score += 3
            breakdown.append((f"Age {age:.0f}h (1+ day)", 3, 5))
        else:
            breakdown.append((f"Age {age:.0f}h (VERY NEW - high risk!)", 0, 5))

        # Has website (3 pts)
        if market.get("website"):
            score += 3
            breakdown.append(("Has website", 3, 3))
        else:
            breakdown.append(("No website", 0, 3))

        # Has socials (2 pts)
        if market.get("socials"):
            score += 2
            breakdown.append(("Has social media", 2, 2))
        else:
            breakdown.append(("No social media", 0, 2))

    return {
        "score": min(score, max_score),
        "grade": score_to_grade(score),
        "breakdown": breakdown,
    }


def score_to_grade(score: int) -> str:
    if score >= 80:
        return "A - SAFE"
    elif score >= 65:
        return "B - LIKELY SAFE"
    elif score >= 50:
        return "C - RISKY"
    elif score >= 35:
        return "D - HIGH RISK"
    else:
        return "F - DANGER"


# ─── Batch token analysis ─────────────────────────────────────
def batch_analyze(query: str, limit: int = 10) -> list:
    """
    Search DexScreener, analyze each result, return sorted by trust score.
    """
    pairs = dexscreener_search(query)
    if not pairs or "error" in pairs[0]:
        return []

    # Deduplicate by token address
    seen = set()
    unique_pairs = []
    for p in pairs:
        addr = p.get("baseToken", {}).get("address", "")
        chain = p.get("chainId", "")
        key = f"{chain}_{addr}"
        if key not in seen and addr:
            seen.add(key)
            unique_pairs.append(p)

    results = []
    for pair in unique_pairs[:limit]:
        market = analyze_pair(pair)
        chain = pair.get("chainId", "")
        token_addr = pair.get("baseToken", {}).get("address", "")

        # Get security if we have a valid address
        if token_addr and chain:
            security = get_security_data(chain, token_addr)
            trust = calculate_trust_score(market, security)
        else:
            security = {}
            trust = {"score": 0, "grade": "N/A", "breakdown": []}

        results.append({
            "market": market,
            "security": security,
            "trust": trust,
            "tokensniffer_url": tokensniffer_url(chain, token_addr) if token_addr else "",
        })

    # Sort by trust score descending
    results.sort(key=lambda x: x["trust"].get("score", 0), reverse=True)
    return results
