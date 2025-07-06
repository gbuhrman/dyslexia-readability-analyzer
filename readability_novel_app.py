
import streamlit as st
import pandas as pd
import re
from io import BytesIO
from readability_utils import analyze_text
from docx import Document
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
from validation_report_generator_wrapped import generate_enhanced_report

def parse_metadata_and_chapters(text):
    metadata = {
        "Title": "Untitled",
        "Author": "Unknown",
        "Chapters": None,
        "Edition": ""
    }
    meta_block = re.search(r"### METADATA START(.*?)### METADATA END", text, re.DOTALL)
    if meta_block:
        lines = meta_block.group(1).strip().splitlines()
        for line in lines:
            if ':' in line:
                key, val = line.split(':', 1)
                metadata[key.strip()] = val.strip()

    chapter_splits = re.split(r"### CHAPTER (\d+)", text)
    chapters = []
    for i in range(1, len(chapter_splits), 2):
        chapter_number = chapter_splits[i]
        chapter_text = chapter_splits[i+1].strip()
        chapters.append((f"Chapter {chapter_number}", chapter_text))

    return metadata, chapters

def sanitize(text):
    return text.replace("–", "-").replace("’", "'").replace("“", '"').replace("”", '"')

def generate_enhanced_report(df, metadata):
    buffer = BytesIO()
    with PdfPages(buffer) as pdf:
        title = sanitize(metadata.get("Title", "Untitled"))
        author = sanitize(metadata.get("Author", "Unknown"))
        edition = sanitize(metadata.get("Edition", ""))
        mean_score = df["Dyslexia-Friendly Score"].mean()
        std_score = df["Dyslexia-Friendly Score"].std()

        fig, ax = plt.subplots(figsize=(8.5, 11))
        ax.axis('off')
        plt.text(0.1, 0.78, "Readability Validation Report", fontsize=22, weight='bold', transform=fig.transFigure)
        plt.text(0.1, 0.74, title, fontsize=18, transform=fig.transFigure)
        plt.text(0.1, 0.7, f"Author: {author}", fontsize=12, transform=fig.transFigure)
        if edition:
            plt.text(0.1, 0.67, f"Edition: {edition}", fontsize=12, transform=fig.transFigure)
        plt.text(0.1, 0.62, f"Total Chapters: {len(df)}", fontsize=11, transform=fig.transFigure)
        plt.text(0.1, 0.59, f"Mean Score: {mean_score:.2f}", fontsize=11, transform=fig.transFigure)
        plt.text(0.1, 0.56, f"Standard Deviation: {std_score:.2f}", fontsize=11, transform=fig.transFigure)
        plt.text(0.1, 0.52, "Z-score threshold for concern: +/-2", fontsize=11, transform=fig.transFigure)
        pdf.savefig()
        plt.close()

        fig, ax = plt.subplots(figsize=(10, 6))
        sns.lineplot(data=df, x=range(1, len(df)+1), y="Dyslexia-Friendly Score", marker="o", ax=ax)
        ax.axhline(mean_score, color='green', linestyle='--', label='Mean')
        ax.axhline(mean_score + 2*std_score, color='red', linestyle='--', label='+2 SD')
        ax.axhline(mean_score - 2*std_score, color='red', linestyle='--', label='-2 SD')
        ax.set_title("Dyslexia-Friendly Score by Chapter")
        ax.set_xlabel("Chapter")
        ax.set_ylabel("Score")
        ax.legend()
        pdf.savefig()
        plt.close()

        z_df = df.select_dtypes(include='number').drop(columns=["Dyslexia-Friendly Score"])
        z_scores = (z_df - z_df.mean()) / z_df.std()
        fig, ax = plt.subplots(figsize=(12, 8))
        sns.heatmap(z_scores.T, cmap="vlag", center=0, cbar_kws={"label": "Z-score"}, ax=ax)
        ax.set_xticks(np.arange(len(df)))
        ax.set_xticklabels([str(i+1) for i in range(len(df))], rotation=0)
        ax.set_title("Z-score Heatmap by Feature and Chapter")
        ax.set_xlabel("Chapter")
        ax.set_ylabel("Feature (Z)")
        pdf.savefig()
        plt.close()

        outliers = z_scores[(z_scores > 2) | (z_scores < -2)].dropna(how="all")
        fig, ax = plt.subplots(figsize=(8.5, 11))
        ax.axis('off')
        ax.set_title("Outlier Chapters (Z > 2 or Z < -2)", fontsize=16, weight='bold', pad=20)
        if not outliers.empty:
            table_data = outliers.round(2).reset_index().values.tolist()
            col_labels = ["Feature"] + [f"Chapter {i+1}" for i in range(len(df))]
            table = ax.table(cellText=table_data, colLabels=col_labels, loc='center', cellLoc='center')
            table.auto_set_font_size(False)
            table.set_fontsize(8)
            table.scale(1.2, 1.2)
        else:
            ax.text(0.2, 0.5, "No chapters with extreme Z-scores found.", fontsize=12)
        pdf.savefig()
        plt.close()

        fig, ax = plt.subplots(figsize=(8.5, 11))
        ax.axis('off')
        ax.set_title("Appendix: Feature Descriptions", fontsize=16, weight='bold', pad=20)
        appendix_text = sanitize("""Sentence Count: Number of sentences. Higher count helps segmentation.
Word Count: Total word count. Neutral by itself.
Avg Sentence Length: Lower is easier. (Lower Z = better)
Avg Word Length: Fewer characters per word helps. (Lower Z = better)
Avg Syllables per Word: Less complex is better. (Lower Z = better)
Passive Sentences: Avoid too many. (Lower Z = better)
Rare/Abstract Words: Lower is more accessible. (Lower Z = better)
Sensory Words: More engagement. (Higher Z = better)
Score: Higher is better.
""")
        ax.text(0.05, 0.95, appendix_text, va='top', wrap=True, fontsize=10)
        pdf.savefig()
        plt.close()

    buffer.seek(0)
    return buffer

st.set_page_config(page_title="Readability Novel Analyzer", layout="centered")
st.title("📘 Novel-Level Readability Analyzer")
st.markdown("Upload a `.txt` or `.docx` file with metadata and chapter headers.")

uploaded_file = st.file_uploader("Upload your novel file", type=["txt", "docx"])

if uploaded_file:
    ext = uploaded_file.name.split('.')[-1]
    if ext == "txt":
        text = uploaded_file.getvalue().decode("utf-8")
    elif ext == "docx":
        doc = Document(uploaded_file)
        text = "\n".join([p.text for p in doc.paragraphs])
    else:
        st.error("Unsupported file type.")
        st.stop()

    metadata, chapters = parse_metadata_and_chapters(text)

    st.subheader("Extracted Metadata")
    for k, v in metadata.items():
        st.text(f"{k}: {v}")
    st.text(f"Total Chapters Detected: {len(chapters)}")

    if st.button("Run Readability Analysis and Generate Report"):
        results = []
        for chap_title, chap_text in chapters:
            metrics = analyze_text(chap_text)
            metrics["Chapter"] = chap_title
            results.append(metrics)
        df = pd.DataFrame(results)
        df = df[["Chapter"] + [col for col in df.columns if col != "Chapter"]]

        st.success("Analysis Complete!")
        st.dataframe(df)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download Chapter Analysis (.csv)", csv, "chapter_readability_analysis.csv", "text/csv")

        pdf_buffer = generate_validation_report(df, metadata)
        st.download_button("📘 Download Validation Report (.pdf)", data=pdf_buffer,
                           file_name=f"{metadata['Title'].replace(' ', '_')}_Validation_Report.pdf",
                           mime="application/pdf")
