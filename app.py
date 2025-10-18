import time
from urllib.parse import urlparse

import streamlit as st
import requests
import pandas as pd

from modules import seo_analyzer

# ---------------------------
# App config
# ---------------------------
st.set_page_config(
    page_title="SEO Agent - Phase 2",
    page_icon="🔎",
    layout="wide"
)

# ---------------------------
# Sidebar
# ---------------------------
st.sidebar.title("SEO Agent")
st.sidebar.caption("Phase 2: SEO Analyzer")

default_url = "https://ibagsie.com"
url = st.sidebar.text_input("Website URL", value=default_url, help="Include https://")
fetch_btn = st.sidebar.button("Analyze page")

timeout_sec = st.sidebar.slider("Timeout (seconds)", min_value=5, max_value=30, value=15)
user_agent = st.sidebar.text_input(
    "User-Agent",
    value="ibagsie-seo-agent/0.2 (+https://ibagsie.com)"
)

# ---------------------------
# Helper functions
# ---------------------------
def normalize_url(u: str) -> str:
    u = u.strip()
    if not u:
        return u
    parsed = urlparse(u)
    if not parsed.scheme:
        u = "https://" + u
    return u

def fetch_page(u: str, timeout: int = 15, ua: str = "ibagsie-seo-agent/0.2"):
    headers = {"User-Agent": ua}
    start = time.perf_counter()
    resp = requests.get(u, headers=headers, timeout=timeout, allow_redirects=True)
    elapsed = time.perf_counter() - start
    return {
        "status_code": resp.status_code,
        "elapsed_ms": int(elapsed * 1000),
        "final_url": resp.url,
        "text": resp.text,
        "ok": resp.ok
    }

# ---------------------------
# Main layout
# ---------------------------
st.title("🔎 SEO Agent — Phase 2")
st.write("Analyze a page for SEO basics: title, meta description, and H1.")

norm_url = normalize_url(url)
st.info(f"Target URL: {norm_url}")

if fetch_btn:
    if not norm_url:
        st.error("Please provide a valid URL.")
    else:
        with st.spinner("Fetching and analyzing..."):
            try:
                result = fetch_page(norm_url, timeout=timeout_sec, ua=user_agent)
            except requests.exceptions.RequestException as e:
                st.error(f"Request failed: {e}")
                st.stop()

        if not result["ok"]:
            st.error(f"Request failed with status {result['status_code']}")
            st.stop()

        # Extract SEO elements
        elements = seo_analyzer.extract_seo_elements(result["text"])
        evaluation = seo_analyzer.evaluate_seo_elements(elements)

        # Combine into one record
        record = {
            "URL": result["final_url"],
            "Title": elements["title"],
            "Title Length": evaluation["title_length"],
            "Title OK": "✅" if evaluation["title_ok"] else "⚠️",
            "Meta Description": elements["meta_description"],
            "Meta Length": evaluation["meta_length"],
            "Meta OK": "✅" if evaluation["meta_ok"] else "⚠️",
            "H1": elements["h1"],
            "Has H1": "✅" if evaluation["has_h1"] else "⚠️"
        }

        df = pd.DataFrame([record])

        st.subheader("SEO Analysis Results")
        st.dataframe(df, use_container_width=True)

        st.success("Analysis complete.")
else:
    st.caption("Click 'Analyze page' in the sidebar to run the SEO analyzer.")
