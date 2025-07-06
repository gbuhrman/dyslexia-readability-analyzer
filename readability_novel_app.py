
import streamlit as st
import pandas as pd
import re
from readability_utils import analyze_text
from validation_report_generator import generate_validation_report
import os
import unicodedata

st.set_page_config(page_title="Novel Readability Analyzer", layout="wide")
st.title("📚 Novel Readability Analyzer")

uploaded_file = st.file_uploader("Upload a .txt file with ### METADATA, ### START, and ### END tags", type=["txt"])

if uploaded_file:
    raw_text = uploaded_file.read().decode("utf-8", errors="ignore")
    lines = raw_text.splitlines()

    # --- METADATA PARSING ---
    title = "Untitled"
    author = "Unknown"
    try:
        meta_start = lines.index("### METADATA START") + 1
        meta_end = lines.index("### METADATA END")
        metadata_lines = lines[meta_start:meta_end]
        for line in metadata_lines:
            if line.startswith("### Title:"):
                title = line.split(":", 1)[1].strip()
            elif line.startswith("### Author:"):
                author = line.split(":", 1)[1].strip()
    except ValueError:
        st.warning("No metadata block found. Using defaults.")

    # Normalize to ASCII-safe
    def safe_ascii(text):
        return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()

    title = safe_ascii(title)
    author = safe_ascii(author)

    # --- TEXT EXTRACTION ---
    try:
        start = lines.index("### START") + 1
        end = lines.index("### END")
        text_lines = lines[start:end]
    except ValueError:
        st.error("Missing ### START or ### END tag.")
        st.stop()

    # --- CHAPTER SPLITTING ---
    chapters = []
    current_chapter = []
    for line in text_lines:
        if line.strip().startswith("### CHAPTER"):
            if current_chapter:
                chapters.append("\n".join(current_chapter))
                current_chapter = []
        current_chapter.append(line)
    if current_chapter:
        chapters.append("\n".join(current_chapter))

    # --- ANALYSIS ---
    st.info(f"Analyzing {len(chapters)} chapters from **{title}** by {author}...")
    all_data = []
    for i, chap in enumerate(chapters):
        metrics = analyze_text(chap)
        metrics["Chapter"] = i + 1
        all_data.append(metrics)

    df = pd.DataFrame(all_data)
    df = df[["Chapter"] + [col for col in df.columns if col != "Chapter"]]  # reorder

    st.success("Analysis complete!")
    st.dataframe(df)

    csv_path = "chapter_readability_analysis.csv"
    df.to_csv(csv_path, index=False)

    st.download_button("📥 Download Chapter Analysis CSV", data=df.to_csv(index=False), file_name=csv_path)

    # --- VALIDATION REPORT ---
    st.subheader("📄 Generate Full Validation Report")
    if st.button("Generate PDF Report"):
        report_path = "validation_report.pdf"
        try:
            generate_validation_report(csv_path, title=title, output_path=report_path)
            with open(report_path, "rb") as f:
                st.download_button("📄 Download Validation Report", f, file_name="Validation_Report.pdf", mime="application/pdf")
        except Exception as e:
            st.error(f"Report generation failed: {e}")
