import streamlit as st
import pandas as pd

from modules import competitor

# ---------------------------
# App config
# ---------------------------
st.set_page_config(
    page_title="SEO Agent - Phase 3",
    page_icon="🔎",
    layout="wide"
)

# ---------------------------
# Sidebar
# ---------------------------
st.sidebar.title("SEO Agent")
st.sidebar.caption("Phase 3: Competitor Analysis")

st.sidebar.subheader("Settings")
timeout_sec = st.sidebar.slider("Timeout (seconds)", min_value=5, max_value=30, value=15)
user_agent = st.sidebar.text_input(
    "User-Agent",
    value="ibagsie-seo-agent/0.3 (+https://ibagsie.com)"
)

# ---------------------------
# Main layout
# ---------------------------
st.title("🔎 SEO Agent — Phase 3")
st.write("Compare your site against competitors by analyzing SEO basics.")

# Input fields
st.subheader("Enter URLs to analyze")
st.caption("Enter one URL per line (include your site and competitors).")

urls_input = st.text_area("URLs", value="https://ibagsie.com\nhttps://example.com")
analyze_btn = st.button("Run Analysis")

if analyze_btn:
    urls = [u.strip() for u in urls_input.splitlines() if u.strip()]
    if not urls:
        st.error("Please enter at least one URL.")
    else:
        with st.spinner("Fetching and analyzing competitor sites..."):
            results = competitor.analyze_urls(urls, timeout=timeout_sec, ua=user_agent)

        df = pd.DataFrame(results)

        st.subheader("Competitor Analysis Results")
        st.dataframe(df, use_container_width=True)

        st.success("Analysis complete.")
else:
    st.caption("Click 'Run Analysis' to start competitor analysis.")
