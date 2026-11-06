import streamlit as st
from datetime import datetime

def show_premium_wall():
    """Show premium features behind a wall."""
    st.markdown("---")
    st.markdown("## 💎 Premium Features")
    st.markdown("*(Unlock with premium subscription)*")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 🔒 AI Signals")
        st.markdown("AI detects pump patterns and sends alerts before they happen.")
        if st.button("🔒 Unlock", key="prem_ai", disabled=True):
            pass
    with col2:
        st.markdown("### 🔒 Solana Full Audit")
        st.markdown("Deep Solana token security with holder analysis.")
        if st.button("🔒 Unlock", key="prem_sol", disabled=True):
            pass
    with col3:
        st.markdown("### 🔒 Telegram Alerts")
        st.markdown("Get instant alerts on Telegram when conditions hit.")
        if st.button("🔒 Unlock", key="prem_tg", disabled=True):
            pass

    col4, col5, col6 = st.columns(3)
    with col4:
        st.markdown("### 🔒 Auto-Trade Bot")
        st.markdown("Auto buy/sell based on your preset rules.")
        if st.button("🔒 Unlock", key="prem_trade", disabled=True):
            pass
    with col5:
        st.markdown("### 🔒 Whale Tracker")
        st.markdown("Track whale wallets and follow their moves.")
        if st.button("🔒 Unlock", key="prem_whale", disabled=True):
            pass
    with col6:
        st.markdown("### 🔒 Rug-Pull Predictor")
        st.markdown("ML model predicts rug-pull probability before it happens.")
        if st.button("🔒 Unlock", key="prem_rug", disabled=True):
            pass


def show_premium_sidebar():
    """Premium badge in sidebar."""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💎 Premium")
    st.sidebar.markdown("""
    **Free Tier:**
    - ✅ Scanner (8 coins/search)
    - ✅ Deep Dive audit
    - ✅ Hype Radar
    - ✅ Profit Estimator
    - ✅ Watchlist (10 coins)

    **Premium ($9/mo):**
    - 🔒 Unlimited scans
    - 🔒 Solana deep audit
    - 🔒 AI pump signals
    - 🔒 Telegram alerts
    - 🔒 Whale tracker
    - 🔒 Rug-pull predictor
    - 🔒 Auto-trade bot
    - 🔒 Watchlist (unlimited)
    """)
