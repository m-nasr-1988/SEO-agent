import streamlit as st
import pandas as pd
from modules import seo_analyzer, seo_suggester

st.set_page_config(page_title="SEO Agent - Phase 4", page_icon="🔎", layout="wide")

st.title("🔎 SEO Agent — Phase 4")
st.write("Analyze a page and generate AI-powered SEO suggestions.")

url = st.text_input("Enter a URL", value="https://ibagsie.com")
analyze_btn = st.button("Analyze & Suggest")

if analyze_btn:
    import requests
    try:
        resp = requests.get(url, timeout=15)
        html = resp.text
    except Exception as e:
        st.error(f"Failed to fetch: {e}")
        st.stop()

    elements = seo_analyzer.extract_seo_elements(html)
    st.subheader("Current SEO Elements")
    st.json(elements)

    with st.spinner("Generating AI suggestions..."):
        suggestions = seo_suggester.suggest_improvements(
            elements["title"], elements["meta_description"], elements["h1"]
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
