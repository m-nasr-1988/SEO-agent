import time
from urllib.parse import urlparse

import streamlit as st
import requests
from bs4 import BeautifulSoup

# ---------------------------
# App config
# ---------------------------
st.set_page_config(
    page_title="SEO Agent - Phase 1",
    page_icon="🔎",
    layout="wide"
)

# ---------------------------
# Sidebar: URL input & actions
# ---------------------------
st.sidebar.title("SEO Agent")
st.sidebar.caption("Phase 1: Setup & Basic Fetch")

default_url = "https://ibagsie.com"
url = st.sidebar.text_input("Website URL", value=default_url, help="Include https://")
fetch_btn = st.sidebar.button("Fetch page")

# Optional: request settings
st.sidebar.subheader("Request settings")
timeout_sec = st.sidebar.slider("Timeout (seconds)", min_value=5, max_value=30, value=15)
user_agent = st.sidebar.text_input(
    "User-Agent",
    value="ibagsie-seo-agent/0.1 (+https://ibagsie.com)"
)

# ---------------------------
# Helper functions
# ---------------------------
def normalize_url(u: str) -> str:
    """Ensure the URL has scheme and looks valid."""
    u = u.strip()
    if not u:
        return u
    parsed = urlparse(u)
    if not parsed.scheme:
        u = "https://" + u  # default to https
    return u

def fetch_page(u: str, timeout: int = 15, ua: str = "ibagsie-seo-agent/0.1"):
    """Fetch a URL with basic headers and return structured info."""
    headers = {
        "User-Agent": ua,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en"
    }
    start = time.perf_counter()
    resp = requests.get(u, headers=headers, timeout=timeout, allow_redirects=True)
    elapsed = time.perf_counter() - start
    return {
        "status_code": resp.status_code,
        "elapsed_ms": int(elapsed * 1000),
        "final_url": resp.url,
        "headers": dict(resp.headers),
        "text": resp.text,
        "ok": resp.ok
    }

def html_to_text(html: str, max_chars: int = 4000) -> str:
    """Convert HTML to readable text for preview."""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = soup.get_text(separator="\n")
    text = "\n".join(line.strip() for line in text.splitlines() if line.strip())
    if len(text) > max_chars:
        text = text[:max_chars] + "\n... [truncated]"
    return text

# ---------------------------
# Main layout
# ---------------------------
st.title("🔎 SEO Agent — Phase 1")
st.write("Enter a URL and fetch the page to verify connectivity and see the raw HTML with a text preview.")

norm_url = normalize_url(url)
st.info(f"Target URL: {norm_url}")

if fetch_btn:
    if not norm_url:
        st.error("Please provide a valid URL.")
    else:
        with st.spinner("Fetching page..."):
            try:
                result = fetch_page(norm_url, timeout=timeout_sec, ua=user_agent)
            except requests.exceptions.RequestException as e:
                st.error(f"Request failed: {e}")
                st.stop()

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Status code", result["status_code"])
        with col2:
            st.metric("Response time", f'{result["elapsed_ms"]} ms')
        with col3:
            st.metric("OK", "Yes" if result["ok"] else "No")

        st.write(f"Final URL (after redirects): {result['final_url']}")
        with st.expander("Response headers"):
            st.json(result["headers"])

        st.subheader("Raw HTML")
        st.code(result["text"][:10000] + ("\n... [truncated]" if len(result["text"]) > 10000 else ""), language="html")

        st.subheader("Text preview")
        preview_text = html_to_text(result["text"])
        st.text(preview_text)

        st.success("Fetched successfully. Phase 1 complete.")
else:
    st.caption("Click 'Fetch page' in the sidebar to run the request.")
