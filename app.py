import streamlit as st
from modules import seo_analyzer, seo_suggester
import requests

st.set_page_config(page_title="SEO Agent - Phase 4", page_icon="🔎", layout="wide")

st.title("🔎 SEO Agent — Phase 4")
st.write("Analyze a page and generate SEO suggestions (toggle between Mock and OpenAI).")

# --- Persist toggle state across runs ---
if "use_openai" not in st.session_state:
    st.session_state["use_openai"] = False  # default to Mock

# Layout: toggle + info icon side by side
col1, col2 = st.columns([4,1])
with col1:
    st.session_state["use_openai"] = st.toggle(
        "Use OpenAI (turn off for Mock Mode)",
        value=st.session_state["use_openai"]
    )
with col2:
    st.markdown(
        "<span title='Mock Mode: No API calls, safe for testing. "
        "OpenAI Mode: Uses your real API key and generates live suggestions.'>ℹ️</span>",
        unsafe_allow_html=True
    )

# Derive method from toggle
method = "OpenAI" if st.session_state["use_openai"] else "Mock"

# --- Status banner shown immediately ---
if method == "Mock":
    st.markdown(
        "<div style='background-color:#FF9800; color:white; padding:8px; border-radius:6px; font-weight:bold;'>🟠 Mock Mode Active — using local mock suggester (no API calls)</div>",
        unsafe_allow_html=True
    )
else:
    st.markdown(
        "<div style='background-color:#4CAF50; color:white; padding:8px; border-radius:6px; font-weight:bold;'>🟢 OpenAI Mode Active — using real OpenAI API</div>",
        unsafe_allow_html=True
    )

url = st.text_input("Enter a URL", value="https://ibagsie.com")

if st.button("Analyze & Suggest"):
    try:
        resp = requests.get(url, timeout=15)
        html = resp.text
    except Exception as e:
        st.error(f"Failed to fetch: {e}")
        st.stop()

    elements = seo_analyzer.extract_seo_elements(html)
    st.subheader("Current SEO Elements")
    st.json(elements)

    with st.spinner(f"Generating {method} suggestions..."):
        suggestions = seo_suggester.suggest_improvements(
            elements["title"], elements["meta_description"], elements["h1"], method=method
        )

    st.subheader("Suggested Improvements")
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Current Title:**", elements["title"])
        st.write("**Current Meta:**", elements["meta_description"])
        st.write("**Current H1:**", elements["h1"])
    with col2:
        st.write("**Suggested Title:**", suggestions["title"])
        st.write("**Suggested Meta:**", suggestions["meta"])
        st.write("**Suggested H1:**", suggestions["h1"])
