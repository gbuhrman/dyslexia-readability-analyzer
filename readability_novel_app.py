
import streamlit as st
import pandas as pd
import docx2txt
import re
from io import BytesIO
from readability_utils import analyze_text

st.set_page_config(page_title="📘 Chapter Batch Analyzer", layout="wide")
st.title("📘 Dyslexia-Friendly Chapter Batch Analyzer")
st.markdown("Upload a full `.docx` novel and get chapter-by-chapter readability metrics based on the trusted scoring model.")

# === Helper functions ===
def split_into_chapters(text):
    pattern = re.compile(r"(?i)(^chapter\s+\d+|^chap\.\s*\d+|^CHAPTER\s+\w+)", re.MULTILINE)
    matches = list(pattern.finditer(text))
    chapters = []

    for i in range(len(matches)):
        start = matches[i].start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        chapter_text = text[start:end].strip()
        chapter_title = matches[i].group().strip()
        chapters.append((chapter_title, chapter_text))

    return chapters

# === File uploader ===
uploaded_file = st.file_uploader("Upload your novel (.docx)", type=["docx"])

if uploaded_file:
    with st.spinner("Analyzing chapters..."):
        text = docx2txt.process(uploaded_file)
        chapters = split_into_chapters(text)
        results = []

        for idx, (title, chap_text) in enumerate(chapters):
            metrics = analyze_text(chap_text)
            metrics["Chapter"] = f"Chapter {idx + 1}"
            results.append(metrics)

        df = pd.DataFrame(results)
        df = df[["Chapter"] + [col for col in df.columns if col != "Chapter"]]

        st.success(f"✅ {len(df)} chapters processed.")
        st.dataframe(df, use_container_width=True)

        # Download button
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download Chapter Metrics (.csv)", csv, "chapter_readability_analysis.csv", "text/csv")

        # Excel download
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Chapter Analysis")
            st.download_button(
                label="Download Chapter Metrics (.xlsx)",
                data=buffer.getvalue(),
                file_name="chapter_readability_analysis.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
