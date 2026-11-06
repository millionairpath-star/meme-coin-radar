"""
Meme Coin Radar — AI-powered meme coin safety scanner
Streamlit app with 7 tabs:
1. Scanner — search any coin, get full safety report
2. Hype Radar — trending + boosted tokens
3. Deep Dive — contract address, full security audit
4. Website Checker — phishing + legitimacy check
5. Profit Estimator — entry/exit/TSL/TP calculator
6. Watchlist — saved coins with live price refresh
7. Alerts — price + security alerts setup
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import json
import time
import os
from datetime import datetime

from apis import (
    dexscreener_search, dexscreener_token_pairs,
    dexscreener_trending_boosted, dexscreener_latest_boosted,
    dexscreener_latest_profiles, dexscreener_trending_metas,
    goplus_phishing_check, get_security_data,
    analyze_pair, full_analysis, batch_analyze,
    calculate_trust_score, tokensniffer_url,
)
from pwa_setup import show_install_banner
from premium import show_premium_sidebar, show_premium_wall

# ─── Page config ─────────────────────────────────────────────
st.set_page_config(
    page_title="Meme Coin Radar",
    page_icon="👻",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "# Meme Coin Radar 👻\nAI-powered meme coin safety scanner.\nFree + Premium tiers.",
    },
)

# ─── Session state ────────────────────────────────────────────
if "watchlist" not in st.session_state:
    st.session_state.watchlist = []
if "alerts" not in st.session_state:
    st.session_state.alerts = []

WATCHLIST_FILE = os.path.join(os.path.dirname(__file__), "watchlist.json")
ALERTS_FILE = os.path.join(os.path.dirname(__file__), "alerts.json")


def load_watchlist():
    if os.path.exists(WATCHLIST_FILE):
        with open(WATCHLIST_FILE, "r") as f:
            st.session_state.watchlist = json.load(f)


def save_watchlist():
    with open(WATCHLIST_FILE, "w") as f:
        json.dump(st.session_state.watchlist, f, indent=2)


def load_alerts():
    if os.path.exists(ALERTS_FILE):
        with open(ALERTS_FILE, "r") as f:
            st.session_state.alerts = json.load(f)


def save_alerts():
    with open(ALERTS_FILE, "w") as f:
        json.dump(st.session_state.alerts, f, indent=2)


load_watchlist()
load_alerts()

# ─── PWA + Premium ────────────────────────────────────────────
show_install_banner()
show_premium_sidebar()

# ─── Sidebar ─────────────────────────────────────────────────
st.sidebar.title("👻 Meme Coin Radar")
st.sidebar.caption("AI Safety Scanner for Meme Coins")

tabs = st.sidebar.radio("Navigate", [
    "🔍 Scanner",
    "🔥 Hype Radar",
    "🔬 Deep Dive",
    "🌐 Website Checker",
    "💰 Profit Estimator",
    "👁️ Watchlist",
    "🔔 Alerts",
])

st.sidebar.divider()
st.sidebar.markdown("### Data Sources")
st.sidebar.markdown("""
- **DexScreener** — live price, volume, liquidity
- **GoPlus Security** — honeypot, tax, mint, owner
- **TokenSniffer** — audit score link
""")

st.sidebar.markdown("### ⚠️ Disclaimer")
st.sidebar.caption("This tool provides data only. Not financial advice. Always DYOR.")


# ═══════════════════════════════════════════════════════════════
# TAB 1: SCANNER
# ═══════════════════════════════════════════════════════════════
if tabs == "🔍 Scanner":
    st.title("🔍 Meme Coin Scanner")
    st.markdown("Search any meme coin. Get market data + security audit + trust score.")

    col1, col2 = st.columns([3, 1])
    with col1:
        query = st.text_input("Enter coin name or symbol (e.g. PEPE, DOGE, BONK)", placeholder="Search...")
    with col2:
        limit = st.number_input("Max results", min_value=3, max_value=20, value=8)

    if st.button("Scan", type="primary") and query:
        with st.spinner(f"Scanning '{query}' across DexScreener + GoPlus..."):
            results = batch_analyze(query, limit=limit)

        if not results:
            st.error("No results found. Try a different name or symbol.")
        else:
            st.success(f"Found {len(results)} tokens. Sorted by trust score.")

            # Summary table
            summary_data = []
            for r in results:
                m = r["market"]
                t = r["trust"]
                s = r["security"] if "security" in r else {}
                summary_data.append({
                    "Token": f"{m.get('token_symbol', '?')}",
                    "Name": m.get("token_name", "?")[:25],
                    "Chain": m.get("chain", "?"),
                    "Price": f"${m.get('price_usd', 0):.8f}",
                    "Liq $": f"${m.get('liquidity_usd', 0):,.0f}",
                    "Vol 24h": f"${m.get('vol_24h', 0):,.0f}",
                    "Buy %": f"{m.get('buy_pct_24h', 0)}%",
                    "Age": f"{m.get('age_hours', 0)}h",
                    "Score": t.get("score", 0),
                    "Grade": t.get("grade", "N/A"),
                    "Honeypot": s.get("is_honeypot", "?"),
                    "Mintable": s.get("is_mintable", "?"),
                    "Hidden Owner": s.get("hidden_owner", "?"),
                })

            df = pd.DataFrame(summary_data)
            st.dataframe(df, use_container_width=True, hide_index=True)

            # Color-coded trust scores
            st.markdown("### Trust Score Breakdown")
            for i, r in enumerate(results):
                m = r["market"]
                t = r["trust"]
                s = r.get("security", {})

                score = t.get("score", 0)
                grade = t.get("grade", "N/A")

                if score >= 65:
                    color = "🟢"
                elif score >= 50:
                    color = "🟡"
                elif score >= 35:
                    color = "🟠"
                else:
                    color = "🔴"

                with st.expander(f"{color} {m.get('token_symbol', '?')} — {m.get('token_name', '?')} | Score: {score}/100 | {grade}", expanded=(i < 3)):
                    mc1, mc2, mc3, mc4 = st.columns(4)
                    with mc1:
                        st.metric("Price", f"${m.get('price_usd', 0):.8f}")
                        st.metric("Liquidity", f"${m.get('liquidity_usd', 0):,.0f}")
                    with mc2:
                        st.metric("24h Volume", f"${m.get('vol_24h', 0):,.0f}")
                        st.metric("Market Cap", f"${m.get('market_cap', 0):,.0f}")
                    with mc3:
                        st.metric("Buy/Sell 24h", f"{m.get('buys_24h', 0)}/{m.get('sells_24h', 0)}")
                        st.metric("Buy Pressure", f"{m.get('buy_pct_24h', 0)}%")
                    with mc4:
                        st.metric("Age", f"{m.get('age_hours', 0)}h")
                        st.metric("Boosts", m.get("boosts", 0))

                    # Price changes
                    pc1, pc2, pc3, pc4 = st.columns(4)
                    with pc1:
                        st.metric("5m", f"{m.get('price_change_5m', 0)}%")
                    with pc2:
                        st.metric("1h", f"{m.get('price_change_1h', 0)}%")
                    with pc3:
                        st.metric("6h", f"{m.get('price_change_6h', 0)}%")
                    with pc4:
                        st.metric("24h", f"{m.get('price_change_24h', 0)}%")

                    # Security flags
                    if s and "error" not in s:
                        st.markdown("**Security Audit (GoPlus):**")
                        sec_cols = st.columns(4)
                        flags = [
                            ("Open Source", s.get("is_open_source"), "1=good"),
                            ("Honeypot", s.get("is_honeypot"), "0=good"),
                            ("Mintable", s.get("is_mintable"), "0=good"),
                            ("Proxy", s.get("is_proxy"), "0=good"),
                            ("Hidden Owner", s.get("hidden_owner"), "0=good"),
                            ("Transfer Pausable", s.get("is_transfer_pausable"), "0=good"),
                            ("Anti-Whale", s.get("is_anti_whale"), "0=good"),
                            ("Blacklist", s.get("is_blacklisted"), "0=good"),
                        ]
                        for idx, (label, val, hint) in enumerate(flags):
                            with sec_cols[idx % 4]:
                                if val == "0" or (label == "Open Source" and val == "1"):
                                    st.markdown(f"✅ {label}: {val}")
                                elif val == "1" or val == "True":
                                    st.markdown(f"❌ {label}: {val}")
                                else:
                                    st.markdown(f"⬜ {label}: {val}")

                        # Taxes
                        buy_tax = float(s.get("buy_tax") or 0)
                        sell_tax = float(s.get("sell_tax") or 0)
                        st.markdown(f"**Buy Tax:** {buy_tax}% | **Sell Tax:** {sell_tax}%")

                        # Holder count
                        holders = s.get("holder_count", "?")
                        st.markdown(f"**Holders:** {holders}")
                    elif s and "error" in s:
                        st.warning(f"Security data unavailable: {s['error']}")

                    # Trust breakdown
                    if t.get("breakdown"):
                        st.markdown("**Trust Score Breakdown:**")
                        for item, pts, max_pts in t["breakdown"]:
                            icon = "✅" if pts == max_pts else ("⚠️" if pts > 0 else "❌")
                            st.markdown(f"{icon} {item}: {pts}/{max_pts}")

                    # Links
                    link_cols = st.columns(3)
                    with link_cols[0]:
                        if m.get("pair_url"):
                            st.markdown(f"[📊 DexScreener Chart]({m['pair_url']})")
                    with link_cols[1]:
                        if r.get("tokensniffer_url"):
                            st.markdown(f"[🔍 TokenSniffer Audit]({r['tokensniffer_url']})")
                    with link_cols[2]:
                        if m.get("website"):
                            st.markdown(f"[🌐 Website]({m['website']})")

                    # Add to watchlist
                    token_addr = m.get("token_address", "")
                    chain = m.get("chain", "")
                    if token_addr and chain:
                        already = any(w.get("address") == token_addr and w.get("chain") == chain for w in st.session_state.watchlist)
                        if already:
                            st.info("Already in watchlist.")
                        elif st.button(f"Add {m.get('token_symbol', '?')} to Watchlist", key=f"wl_{i}"):
                            st.session_state.watchlist.append({
                                "symbol": m.get("token_symbol", ""),
                                "name": m.get("token_name", ""),
                                "chain": chain,
                                "address": token_addr,
                                "price": m.get("price_usd", 0),
                                "added_at": datetime.now().isoformat(),
                            })
                            save_watchlist()
                            st.success(f"Added {m.get('token_symbol', '?')} to watchlist!")


# ═══════════════════════════════════════════════════════════════
# TAB 2: HYPE RADAR
# ═══════════════════════════════════════════════════════════════
elif tabs == "🔥 Hype Radar":
    st.title("🔥 Hype Radar")
    st.markdown("Trending tokens, boosted tokens, and hot narratives.")

    hype_tab1, hype_tab2, hype_tab3, hype_tab4 = st.tabs([
        "🚀 Top Boosted", "⚡ New Boosts", "📋 New Profiles", "📊 Trending Metas"
    ])

    with hype_tab1:
        st.markdown("### Most Actively Boosted Tokens")
        st.caption("More boosts = more money spent on visibility = higher hype.")
        if st.button("Load Top Boosted"):
            with st.spinner("Fetching..."):
                boosted = dexscreener_trending_boosted()
            if boosted and "error" not in boosted[0]:
                data = []
                for b in boosted[:20]:
                    data.append({
                        "Symbol": b.get("tokenAddress", "")[:8] + "...",
                        "Chain": b.get("chainId", ""),
                        "Total Boosts": b.get("totalAmount", 0),
                        "Active Boosts": b.get("amount", 0),
                        "Description": (b.get("description") or "")[:50],
                    })
                st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)

                # Show links
                for b in boosted[:5]:
                    url = b.get("url", "")
                    if url:
                        st.markdown(f"- [{b.get('chainId', '')} — {url}]({url})")
            else:
                st.error("Failed to load.")

    with hype_tab2:
        st.markdown("### Latest Boosted Tokens (Fresh Hype)")
        if st.button("Load Latest Boosts"):
            with st.spinner("Fetching..."):
                latest = dexscreener_latest_boosted()
            if latest and "error" not in latest[0]:
                data = []
                for b in latest[:20]:
                    data.append({
                        "Chain": b.get("chainId", ""),
                        "Token": b.get("tokenAddress", "")[:10] + "...",
                        "Boost Amount": b.get("amount", 0),
                        "URL": b.get("url", ""),
                    })
                st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
            else:
                st.error("Failed to load.")

    with hype_tab3:
        st.markdown("### Newest Token Profiles")
        st.caption("Recently listed tokens with website/socials set up.")
        if st.button("Load New Profiles"):
            with st.spinner("Fetching..."):
                profiles = dexscreener_latest_profiles()
            if profiles and "error" not in profiles[0]:
                data = []
                for p in profiles[:20]:
                    links = p.get("links", []) or []
                    link_str = ", ".join([l.get("type", "") for l in links])
                    data.append({
                        "Chain": p.get("chainId", ""),
                        "Token": p.get("tokenAddress", "")[:10] + "...",
                        "Description": (p.get("description") or "")[:60],
                        "Links": link_str,
                    })
                st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
            else:
                st.error("Failed to load.")

    with hype_tab4:
        st.markdown("### Trending Narratives (Metas)")
        if st.button("Load Trending Metas"):
            with st.spinner("Fetching..."):
                metas = dexscreener_trending_metas()
            if metas and "error" not in metas[0]:
                data = []
                for m in metas[:15]:
                    data.append({
                        "Name": m.get("name", ""),
                        "Slug": m.get("slug", ""),
                        "Mkt Cap": m.get("marketCap", 0),
                        "Liquidity": m.get("liquidity", 0),
                        "Volume": m.get("volume", 0),
                        "Tokens": m.get("tokenCount", 0),
                    })
                df = pd.DataFrame(data)
                st.dataframe(df, use_container_width=True, hide_index=True)

                # Bar chart
                if data:
                    fig = px.bar(df, x="Name", y="Volume", title="Trending Metas by Volume")
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.error("Failed to load.")


# ═══════════════════════════════════════════════════════════════
# TAB 3: DEEP DIVE
# ═══════════════════════════════════════════════════════════════
elif tabs == "🔬 Deep Dive":
    st.title("🔬 Deep Dive Audit")
    st.markdown("Enter a contract address + chain for the most detailed security report.")

    dd_col1, dd_col2 = st.columns([2, 1])
    with dd_col1:
        contract = st.text_input("Contract Address", placeholder="0x... or Solana address")
    with dd_col2:
        chain = st.selectbox("Chain", [
            "ethereum", "bsc", "solana", "base", "arbitrum",
            "polygon", "optimism", "avalanche", "fantom",
            "linea", "blast", "scroll", "mantle", "cronos"
        ])

    if st.button("Run Full Audit", type="primary") and contract:
        with st.spinner("Running DexScreener + GoPlus + TokenSniffer analysis..."):
            result = full_analysis(chain, contract)

        market = result.get("market", {})
        security = result.get("security", {})
        trust = result.get("trust_score", {})
        ts_url = result.get("tokensniffer_url", "")

        # Trust score big display
        score = trust.get("score", 0)
        grade = trust.get("grade", "N/A")

        score_color = "#28a745" if score >= 65 else ("#ffc107" if score >= 50 else "#dc3545")

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(f"""
            <div style="text-align:center; padding:20px; border-radius:15px;
                        background:#1a1a2e; border: 2px solid {score_color};">
                <h1 style="color:{score_color}; font-size:3em;">{score}/100</h1>
                <h2 style="color:{score_color};">{grade}</h2>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # Market data
        if "error" not in market:
            st.markdown("### 📊 Market Data")
            mc1, mc2, mc3, mc4, mc5 = st.columns(5)
            with mc1:
                st.metric("Price", f"${market.get('price_usd', 0):.8f}")
            with mc2:
                st.metric("Liquidity", f"${market.get('liquidity_usd', 0):,.0f}")
            with mc3:
                st.metric("24h Volume", f"${market.get('vol_24h', 0):,.0f}")
            with mc4:
                st.metric("Market Cap", f"${market.get('market_cap', 0):,.0f}")
            with mc5:
                st.metric("FDV", f"${market.get('fdv', 0):,.0f}")

            pc1, pc2, pc3, pc4 = st.columns(4)
            with pc1:
                st.metric("5m Change", f"{market.get('price_change_5m', 0)}%")
            with pc2:
                st.metric("1h Change", f"{market.get('price_change_1h', 0)}%")
            with pc3:
                st.metric("6h Change", f"{market.get('price_change_6h', 0)}%")
            with pc4:
                st.metric("24h Change", f"{market.get('price_change_24h', 0)}%")

            # Buy/sell visualization
            buys = market.get("buys_24h", 0)
            sells = market.get("sells_24h", 0)
            if buys + sells > 0:
                fig = go.Figure(data=[go.Bar(
                    x=["Buys", "Sells"],
                    y=[buys, sells],
                    marker_color=["#28a745", "#dc3545"],
                )])
                fig.update_layout(title="24h Buy vs Sell", height=300)
                st.plotly_chart(fig, use_container_width=True)

            # Website & socials
            if market.get("website"):
                st.markdown(f"**Website:** {market['website']}")
            if market.get("socials"):
                social_str = ", ".join([f"{s.get('platform', '')}: {s.get('handle', '')}" for s in market["socials"]])
                st.markdown(f"**Socials:** {social_str}")

            if market.get("pair_url"):
                st.markdown(f"[📊 View on DexScreener]({market['pair_url']})")

        # Security details
        if security and "error" not in security:
            st.markdown("### 🔒 Security Audit (GoPlus)")
            sec_data = []
            security_fields = [
                ("Open Source", "is_open_source", "0=bad, 1=good"),
                ("Honeypot", "is_honeypot", "0=good, 1=BAD"),
                ("Mintable", "is_mintable", "0=good, 1=BAD"),
                ("Proxy", "is_proxy", "0=good, 1=risky"),
                ("Hidden Owner", "hidden_owner", "0=good, 1=BAD"),
                ("Transfer Pausable", "is_transfer_pausable", "0=good, 1=BAD"),
                ("Anti-Whale", "is_anti_whale", "0=good, 1=risky"),
                ("Blacklist", "is_blacklisted", "0=good, 1=BAD"),
                ("Can Reclaim Ownership", "can_take_back_ownership", "0=good, 1=BAD"),
                ("Owner Multisig", "is_owner_multisig", "1=good"),
                ("Personal Interest", "is_personal_interest", "0=good, 1=BAD"),
                ("Is In Whitelist", "is_in_white_list", "1=good"),
            ]
            for label, key, hint in security_fields:
                val = security.get(key, "N/A")
                sec_data.append({"Check": label, "Value": val, "Hint": hint})

            st.dataframe(pd.DataFrame(sec_data), use_container_width=True, hide_index=True)

            # Taxes
            st.markdown("### 💰 Tax Information")
            tc1, tc2 = st.columns(2)
            with tc1:
                buy_tax = float(security.get("buy_tax") or 0)
                st.metric("Buy Tax", f"{buy_tax}%")
            with tc2:
                sell_tax = float(security.get("sell_tax") or 0)
                st.metric("Sell Tax", f"{sell_tax}%")

            # Holder distribution
            holders = security.get("holder_count", "N/A")
            st.metric("Holder Count", holders)

            # Top holders
            top_holders = []
            for i in range(1, 11):
                h = security.get(f"holder_{i}_address", "")
                pct = security.get(f"holder_{i}_percentage", "")
                if h:
                    top_holders.append({"Rank": i, "Address": h[:12] + "...", "Percentage": pct})
            if top_holders:
                st.markdown("### 👥 Top Holders")
                st.dataframe(pd.DataFrame(top_holders), use_container_width=True, hide_index=True)

        elif security and "error" in security:
            st.warning(f"GoPlus security data unavailable: {security['error']}")

        # Trust breakdown
        if trust.get("breakdown"):
            st.markdown("### 📋 Trust Score Breakdown")
            for item, pts, max_pts in trust["breakdown"]:
                pct = (pts / max_pts * 100) if max_pts > 0 else 0
                icon = "✅" if pts == max_pts else ("⚠️" if pts > 0 else "❌")
                st.markdown(f"{icon} {item} ({pts}/{max_pts})")

        # TokenSniffer link
        if ts_url:
            st.markdown(f"### 🔗 External Audit")
            st.markdown(f"[🔍 Open TokenSniffer Full Audit]({ts_url})")


# ═══════════════════════════════════════════════════════════════
# TAB 4: WEBSITE CHECKER
# ═════════════════════════════████═════════════════════════════
elif tabs == "🌐 Website Checker":
    st.title("🌐 Website & Phishing Checker")
    st.markdown("Check if a coin's website is legit or a phishing/scam site.")

    url_input = st.text_input("Enter website URL", placeholder="https://example.com")

    if st.button("Check Website", type="primary") and url_input:
        with st.spinner("Checking GoPlus phishing database..."):
            result = goplus_phishing_check(url_input)

        if result and "error" not in result:
            is_phishing = result.get("phishing", 0)
            if is_phishing == 1:
                st.error("🚨 PHISHING SITE DETECTED! Do NOT visit or connect wallet!")
            else:
                st.success("✅ Not flagged as phishing by GoPlus.")

            st.json(result)
        else:
            st.warning("Could not check this URL. Check manually:")
            st.markdown(f"- [Google Safe Browsing](https://transparencyreport.google.com/safe-browsing/search?url={url_input})")
            st.markdown(f"- [URLVoid](https://www.urlvoid.com/scan/{url_input.replace('https://', '').replace('http://', '')}/)")
            st.markdown(f"- [VirusTotal](https://www.virustotal.com/gui/search/{url_input})")

    st.markdown("---")
    st.markdown("### Quick Manual Checks")
    st.markdown("""
    Before buying any meme coin, check:
    1. **Website** — Is it professional? Does it have real content?
    2. **Twitter/X** — Real followers? Regular posts? Engagement?
    3. **Telegram** — Active community or just bots?
    4. **TokenSniffer** — Automated audit score
    5. **GoPlus** — Contract security (honeypot, mint, etc.)
    6. **Holder distribution** — Is one wallet holding 50%+? Red flag.
    7. **Liquidity** — Is liquidity locked? How much?
    8. **Contract** — Is it verified/open source on block explorer?
    """)


# ═══════════════════════════════════════════════════════════════
# TAB 5: PROFIT ESTIMATOR
# ═══════════════════════════════════════════════════════════════
elif tabs == "💰 Profit Estimator":
    st.title("💰 Profit Estimator")
    st.markdown("Calculate potential profit with entry, exit, and risk management.")

    pe_col1, pe_col2, pe_col3 = st.columns(3)

    with pe_col1:
        entry_price = st.number_input("Entry Price ($)", min_value=0.0, value=0.0001, format="%.8f")
        investment = st.number_input("Investment ($)", min_value=1.0, value=100.0)
    with pe_col2:
        take_profit_pct = st.slider("Take Profit (%)", 10, 500, 50, step=10)
        stop_loss_pct = st.slider("Stop Loss (%)", 5, 50, 15, step=5)
    with pe_col3:
        buy_tax = st.number_input("Buy Tax (%)", min_value=0.0, max_value=25.0, value=0.0, step=0.5)
        sell_tax = st.number_input("Sell Tax (%)", min_value=0.0, max_value=25.0, value=0.0, step=0.5)

    if entry_price > 0 and investment > 0:
        # Tokens bought (after buy tax)
        tokens_bought = investment / (entry_price * (1 + buy_tax / 100))

        # TP and SL prices
        tp_price = entry_price * (1 + take_profit_pct / 100)
        sl_price = entry_price * (1 - stop_loss_pct / 100)

        # Profit at TP (after sell tax)
        gross_tp_value = tokens_bought * tp_price
        net_tp_value = gross_tp_value * (1 - sell_tax / 100)
        profit_tp = net_tp_value - investment
        roi_tp = (profit_tp / investment) * 100

        # Loss at SL (after sell tax)
        gross_sl_value = tokens_bought * sl_price
        net_sl_value = gross_sl_value * (1 - sell_tax / 100)
        loss_sl = net_sl_value - investment
        roi_sl = (loss_sl / investment) * 100

        # Risk-reward
        rr = abs(profit_tp / loss_sl) if loss_sl != 0 else float("inf")

        # Display
        st.markdown("### Results")

        r1, r2, r3, r4 = st.columns(4)
        with r1:
            st.metric("Tokens Received", f"{tokens_bought:,.2f}")
        with r2:
            st.metric("Take Profit Price", f"${tp_price:.8f}")
        with r3:
            st.metric("Stop Loss Price", f"${sl_price:.8f}")
        with r4:
            st.metric("Risk:Reward", f"1:{rr:.1f}")

        st.markdown("---")

        pc1, pc2 = st.columns(2)

        with pc1:
            st.markdown("#### ✅ If Take Profit Hits")
            st.metric("Gross Value", f"${gross_tp_value:,.2f}")
            st.metric("Net Value (after tax)", f"${net_tp_value:,.2f}")
            st.metric("Profit", f"${profit_tp:,.2f}")
            st.metric("ROI", f"{roi_tp:.1f}%")

        with pc2:
            st.markdown("#### ❌ If Stop Loss Hits")
            st.metric("Gross Value", f"${gross_sl_value:,.2f}")
            st.metric("Net Value (after tax)", f"${net_sl_value:,.2f}")
            st.metric("Loss", f"${loss_sl:,.2f}")
            st.metric("ROI", f"{roi_sl:.1f}%")

        # Visualization
        st.markdown("### Profit/Loss Scenarios")
        scenarios = []
        for pct in range(-stop_loss_pct, take_profit_pct + 1, max(1, (take_profit_pct + stop_loss_pct) // 20)):
            price = entry_price * (1 + pct / 100)
            gross = tokens_bought * price
            net = gross * (1 - sell_tax / 100)
            pnl = net - investment
            scenarios.append({"Price Change %": pct, "P&L ($)": pnl})

        df = pd.DataFrame(scenarios)
        fig = px.bar(df, x="Price Change %", y="P&L ($)",
                     color="P&L ($)",
                     color_continuous_scale=["#dc3545", "#ffc107", "#28a745"],
                     title="P&L at Different Price Levels")
        fig.add_hline(y=0, line_dash="dash", line_color="white")
        st.plotly_chart(fig, use_container_width=True)

        # Advice
        st.markdown("### 📌 Key Tips")
        if rr < 2:
            st.warning(f"Risk:Reward is 1:{rr:.1f} — aim for at least 1:2.")
        else:
            st.success(f"Risk:Reward is 1:{rr:.1f} — good setup.")
        if buy_tax > 5 or sell_tax > 5:
            st.error("High tax! Reconsider or adjust targets.")
        if take_profit_pct < 30:
            st.info("Low TP for meme coins — consider higher targets.")


# ═══════════════════════════════════════════════════════════════
# TAB 6: WATCHLIST
# ═══════════════════════════════════════════════════════════════
elif tabs == "👁️ Watchlist":
    st.title("👁️ Watchlist")

    if not st.session_state.watchlist:
        st.info("No coins in watchlist yet. Add from the Scanner tab.")
    else:
        st.markdown(f"### {len(st.session_state.watchlist)} coins tracked")

        if st.button("🔄 Refresh Prices"):
            with st.spinner("Fetching live prices..."):
                for w in st.session_state.watchlist:
                    pairs = dexscreener_token_pairs(w["chain"], w["address"])
                    if pairs and "error" not in pairs[0]:
                        best = max(pairs, key=lambda p: (p.get("liquidity", {}) or {}).get("usd", 0) if isinstance(p.get("liquidity"), dict) else 0)
                        market = analyze_pair(best)
                        w["current_price"] = market.get("price_usd", 0)
                        w["price_change_24h"] = market.get("price_change_24h", 0)
                        w["liquidity_usd"] = market.get("liquidity_usd", 0)
                        w["vol_24h"] = market.get("vol_24h", 0)
                save_watchlist()
            st.success("Prices updated!")

        wl_data = []
        for w in st.session_state.watchlist:
            old_price = w.get("price", 0)
            new_price = w.get("current_price", old_price)
            change = ((new_price - old_price) / old_price * 100) if old_price > 0 else 0
            wl_data.append({
                "Symbol": w.get("symbol", ""),
                "Name": w.get("name", ""),
                "Chain": w.get("chain", ""),
                "Entry Price": f"${old_price:.8f}",
                "Current Price": f"${new_price:.8f}",
                "Change %": f"{change:+.1f}%",
                "Liquidity": f"${w.get('liquidity_usd', 0):,.0f}",
                "24h Vol": f"${w.get('vol_24h', 0):,.0f}",
            })

        st.dataframe(pd.DataFrame(wl_data), use_container_width=True, hide_index=True)

        # Remove buttons
        st.markdown("### Remove from Watchlist")
        for i, w in enumerate(st.session_state.watchlist):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.text(f"{w.get('symbol', '')} — {w.get('name', '')}")
            with col2:
                if st.button("Remove", key=f"rm_{i}"):
                    st.session_state.watchlist.pop(i)
                    save_watchlist()
                    st.rerun()


# ═══════════════════════════ PEPE══════════════════════════════
# TAB 7: ALERTS
# ═══════════════════════════════════════════════════════════════
elif tabs == "🔔 Alerts":
    st.title("🔔 Price & Security Alerts")
    st.markdown("Set up alerts for watchlist coins.")

    if not st.session_state.watchlist:
        st.info("Add coins to your watchlist first.")
    else:
        with st.form("alert_form"):
            st.markdown("### Create Alert")
            al_col1, al_col2, al_col3 = st.columns(3)
            with al_col1:
                alert_symbol = st.selectbox("Coin", [w["symbol"] for w in st.session_state.watchlist])
            with al_col2:
                alert_type = st.selectbox("Alert Type", [
                    "Price above", "Price below",
                    "24h change above %", "24h change below %",
                    "Liquidity drop > 20%", "Volume spike > 2x"
                ])
            with al_col3:
                alert_value = st.number_input("Threshold", value=0.0, format="%.8f")

            submitted = st.form_submit_button("Add Alert")
            if submitted:
                st.session_state.alerts.append({
                    "symbol": alert_symbol,
                    "type": alert_type,
                    "value": alert_value,
                    "created_at": datetime.now().isoformat(),
                    "triggered": False,
                })
                save_alerts()
                st.success(f"Alert added for {alert_symbol}!")

        # List alerts
        if st.session_state.alerts:
            st.markdown("### Active Alerts")
            for i, a in enumerate(st.session_state.alerts):
                status = "🔔 Active" if not a.get("triggered") else "✅ Triggered"
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"{status} — **{a['symbol']}** {a['type']} {a['value']}")
                with col2:
                    if st.button("Delete", key=f"del_alert_{i}"):
                        st.session_state.alerts.pop(i)
                        save_alerts()
                        st.rerun()
        else:
            st.info("No alerts set up yet.")

    st.markdown("---")
    st.markdown("### 📱 About Alerts")
    st.markdown("""
    Alerts are stored locally. For live monitoring:
    1. Set up a Kiro Crew cron job to check prices every hour.
    2. The cron job reads this file and checks conditions.
    3. If triggered, it sends you a notification.
    """)

# ─── Premium Wall (always at bottom) ─────────────────────────
show_premium_wall()
