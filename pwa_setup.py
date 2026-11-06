import streamlit as st

# ─── PWA Install Prompt ─────────────────────────────────────
# This meta + JS makes the app installable as PWA on phone & PC

PWA_META = """
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Meme Radar">
<meta name="theme-color" content="#0e1117">
<link rel="manifest" href="/manifest.json">
<link rel="apple-touch-icon" href="/icon.png">
<script>
if ('serviceWorker' in navigator) {
  window.addEventListener('load', function() {
    navigator.serviceWorker.register('/sw.js').then(function(reg) {
      console.log('PWA registered');
    }).catch(function(e) {
      console.log('PWA failed:', e);
    });
  });
}
</script>
"""

st.markdown(PWA_META, unsafe_allow_html=True)


def show_install_banner():
    """Show install button in sidebar."""
    st.sidebar.markdown("### 📱 Install App")
    st.sidebar.markdown("""
    **Android:** Chrome menu → "Install app"  
    **iPhone:** Safari → Share → "Add to Home Screen"  
    **PC:** Chrome address bar ke right pe install icon
    """)
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💎 Upgrade to Premium")
    st.sidebar.markdown("Unlock: Solana support, AI signals, Telegram alerts, auto-trade bot")
    if st.sidebar.button("⬆️ Go Premium"):
        st.sidebar.info("Premium features coming soon!")
