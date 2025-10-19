import streamlit as st
import requests
import re
from collections import Counter
import pandas as pd
from modules import seo_analyzer, seo_suggester

st.set_page_config(page_title="SEO Agent - Phase 5", page_icon="🔎", layout="wide")

st.title("🔎 SEO Agent — Phase 5")
st.write("Analyze SEO elements, extract keywords, and compare with a competitor.")

# --- Toggle for Mock vs OpenAI ---
if "use_openai" not in st.session_state:
    st.session_state["use_openai"] = False

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

method = "OpenAI" if st.session_state["use_openai"] else "Mock"

# --- Status banner ---
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

# --- Inputs ---
url = st.text_input("Enter your URL", value="https://ibagsie.com")
competitor_url = st.text_input("Enter competitor URL (optional)")

# --- Keyword extraction helper ---
def extract_keywords(text, top_n=10):
    words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
    counts = Counter(words)
    return counts.most_common(top_n)

if st.button("Analyze & Compare"):
    try:
        resp = requests.get(url, timeout=15)
        html = resp.text
    except Exception as e:
        st.error(f"Failed to fetch your URL: {e}")
        st.stop()

    elements = seo_analyzer.extract_seo_elements(html)
    st.subheader("Your Current SEO Elements")
    st.json(elements)

    # --- Keyword analysis for your page ---
    your_keywords = extract_keywords(html, top_n=10)
    st.subheader("Your Top Keywords")
    df_your = pd.DataFrame(your_keywords, columns=["Keyword", "Count"])
    st.bar_chart(df_your.set_index("Keyword"))

    # --- Suggestions (Mock or OpenAI) ---
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

    # --- Competitor analysis ---
    if competitor_url:
        try:
            comp_resp = requests.get(competitor_url, timeout=15)
            comp_html = comp_resp.text
        except Exception as e:
            st.error(f"Failed to fetch competitor URL: {e}")
            st.stop()

        comp_elements = seo_analyzer.extract_seo_elements(comp_html)
        st.subheader("Competitor SEO Elements")
        st.json(comp_elements)

        comp_keywords = extract_keywords(comp_html, top_n=10)
        st.subheader("Competitor Top Keywords")
        df_comp = pd.DataFrame(comp_keywords, columns=["Keyword", "Count"])
        st.bar_chart(df_comp.set_index("Keyword"))

        # --- Keyword overlap ---
        your_kw_set = {k for k, _ in your_keywords}
        comp_kw_set = {k for k, _ in comp_keywords}

        st.subheader("Keyword Comparison")
        st.write("**Shared keywords:**", your_kw_set & comp_kw_set)
        st.write("**Unique to you:**", your_kw_set - comp_kw_set)
        st.write("**Unique to competitor:**", comp_kw_set - your_kw_set)
