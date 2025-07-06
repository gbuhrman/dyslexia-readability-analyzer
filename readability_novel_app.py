
import streamlit as st
import pandas as pd
from readability_utils import analyze_text
from validation_report_generator import generate_validation_report
import os

st.set_page_config(page_title="Novel Readability Analyzer", layout="wide")
st.title("📚 Novel Readability Analyzer")

uploaded_file = st.file_uploader("Upload a .txt file with ### START and ### END metadata", type=["txt"])

if uploaded_file:
    raw_text = uploaded_file.read().decode("utf-8")

    # Extract metadata
    lines = raw_text.splitlines()
    title = "Untitled"
    author = "Unknown"
    for line in lines:
        if line.startswith("### Title:"):
            title = line.split(":", 1)[1].strip()
        elif line.startswith("### Author:"):
            author = line.split(":", 1)[1].strip()

    # Extract text between ### START and ### END
    try:
        start = lines.index("### START") + 1
        end = lines.index("### END")
        text_lines = lines[start:end]
    except ValueError:
        st.error("Missing ### START or ### END tag.")
        st.stop()

    # Chapter splitting
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

    # Run analysis
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

    # Generate validation report
    st.subheader("📄 Generate Full Validation Report")
    if st.button("Generate PDF Report"):
        report_path = "validation_report.pdf"
        generate_validation_report(csv_path, title=title, output_path=report_path)
        with open(report_path, "rb") as f:
            st.download_button("📄 Download Validation Report", f, file_name="Validation_Report.pdf", mime="application/pdf")
