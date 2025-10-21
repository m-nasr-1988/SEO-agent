import streamlit as st
import requests
import re
from collections import Counter
import pandas as pd
import plotly.express as px
from fpdf import FPDF
from modules import seo_analyzer, seo_suggester

st.set_page_config(page_title="SEO Agent - Phase 5e", page_icon="🔎", layout="wide")

st.title("🔎 SEO Agent — Phase 5e")
st.write("Analyze SEO elements, extract keywords, compare with a competitor, visualize scores, generate SEO from description, and export reports.")

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
url = st.text_input("Enter your URL", value="")
competitor_url = st.text_input("Enter competitor URL (optional)")
description = st.text_area("Or describe your website (optional)", 
    placeholder="e.g. Booking website that enables customers to navigate airlines...")

# --- Keyword extraction helper ---
def extract_keywords(text, top_n=10):
    words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
    counts = Counter(words)
    return counts.most_common(top_n)

# --- Scoring helper ---
def score_page(elements, keywords, competitor_keywords):
    scores = {}
    title_len = len(elements.get("title", "") or "")
    if 30 <= title_len <= 60:
        scores["Title Length"] = 100
    else:
        scores["Title Length"] = max(0, 100 - abs(title_len - 45))

    meta_len = len(elements.get("meta_description", "") or "")
    if 80 <= meta_len <= 160:
        scores["Meta Length"] = 100
    else:
        scores["Meta Length"] = max(0, 100 - abs(meta_len - 120))

    scores["H1 Presence"] = 100 if elements.get("h1") else 0

    your_kw_set = {k for k, _ in keywords}
    comp_kw_set = {k for k, _ in competitor_keywords}
    if comp_kw_set:
        coverage = len(your_kw_set & comp_kw_set) / len(comp_kw_set)
        scores["Keyword Coverage"] = int(coverage * 100)
    else:
        scores["Keyword Coverage"] = 0

    return scores

# --- PDF generator ---
def generate_pdf(report_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in report_text.splitlines():
        pdf.multi_cell(0, 10, line)
    return pdf.output(dest="S").encode("latin-1")

if st.button("Analyze & Compare"):
    report_sections = []

    # --- Description-based SEO generation ---
    if description:
        st.subheader("Generated SEO Elements from Description")
        with st.spinner(f"Generating SEO from description using {method}..."):
            generated = seo_suggester.suggest_improvements(
                title="", meta=description, h1="", method=method
            )
        st.json(generated)
        report_sections.append(f"## SEO from Description\n{description}\n\nGenerated:\n{generated}\n")

    # --- URL-based analysis ---
    elements, your_keywords, competitor_keywords, comp_elements = {}, [], [], {}
    if url:
        try:
            resp = requests.get(url, timeout=15)
            html = resp.text
        except Exception as e:
            st.error(f"Failed to fetch your URL: {e}")
            st.stop()

        elements = seo_analyzer.extract_seo_elements(html)
        st.subheader("Your Current SEO Elements")
        st.json(elements)

        your_keywords = extract_keywords(html, top_n=10)
        st.subheader("Your Top Keywords")
        df_your = pd.DataFrame(your_keywords, columns=["Keyword", "Count"])
        st.bar_chart(df_your.set_index("Keyword"))

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

        report_sections.append(f"## Your Page\nURL: {url}\n\nElements: {elements}\n\nSuggestions: {suggestions}\n\nTop Keywords: {your_keywords}\n")

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

            competitor_keywords = extract_keywords(comp_html, top_n=10)
            st.subheader("Competitor Top Keywords")
            df_comp = pd.DataFrame(competitor_keywords, columns=["Keyword", "Count"])
            st.bar_chart(df_comp.set_index("Keyword"))

            your_kw_set = {k for k, _ in your_keywords}
            comp_kw_set = {k for k, _ in competitor_keywords}

            st.subheader("Keyword Comparison")
            st.write("**Shared keywords:**", your_kw_set & comp_kw_set)
            st.write("**Unique to you:**", your_kw_set - comp_kw_set)
            st.write("**Unique to competitor:**", comp_kw_set - your_kw_set)

            st.subheader("SEO Score Comparison")
            your_scores = score_page(elements, your_keywords, competitor_keywords)
            comp_scores = score_page(comp_elements, competitor_keywords, your_keywords)

            df_scores = pd.DataFrame([your_scores, comp_scores], index=["You", "Competitor"])
            st.dataframe(df_scores)

            df_long = df_scores.reset_index().melt(
                id_vars="index",
                var_name="Metric",
                value_name="Score"
            )

            fig = px.line_polar(
                df_long,
                r="Score",
                theta="Metric",
                color="index",
                line_close=True,
                range_r=[0,100]
            )
            st.plotly_chart(fig, use_container_width=True)

            report_sections.append(f"## Competitor Page\nURL: {competitor_url}\n\nElements: {comp_elements}\n\nTop Keywords: {competitor_keywords}\n\nKeyword Comparison:\nShared: {your_kw_set & comp_kw_set}\nUnique to you: {your_kw_set - comp_kw_set}\nUnique to competitor: {comp_kw_set - your_kw_set}\n\nScores:\n{df_scores.to_markdown()}\n")

    # --- Export Report ---
    if report_sections:
        report = "# SEO Report\n\n" + "\n\n".join(report_sections)

        st.subheader("📄 Export SEO Report")
        st.download_button(
            label="Download Report (Markdown)",
            data=report,
            file_name="seo_report.md",
            mime="text/markdown"
        )

        pdf_bytes = generate_pdf(report)
        st.download_button(
            label="Download Report (PDF)",
            data=pdf_bytes,
            file_name="seo_report.pdf",
            mime="application/pdf"
        )
