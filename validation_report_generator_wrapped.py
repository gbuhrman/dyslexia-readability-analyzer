
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF
import os
from io import BytesIO

def sanitize_text(text):
    if not isinstance(text, str):
        return str(text)
    return (
        text.replace("’", "'")
            .replace("‘", "'")
            .replace("“", '"')
            .replace("”", '"')
            .replace("–", "-")
            .replace("—", "-")
            .replace("…", "...")
    )

def generate_enhanced_report(df, metadata=None, logo_path=None):
    feature_cols = df.columns.drop("Chapter")

    # Compute z-scores
    z_scores = df[feature_cols].apply(lambda x: (x - x.mean()) / x.std())
    z_scores["Chapter"] = df["Chapter"]

    # Detect outliers
    outliers = z_scores[feature_cols].abs() > 2
    outlier_rows = z_scores[outliers.any(axis=1)]
    outlier_data = df.loc[outlier_rows.index]

    # Summary info
    lowest = df.loc[df["Dyslexia-Friendly Score"].idxmin()]
    highest = df.loc[df["Dyslexia-Friendly Score"].idxmax()]
    avg_score = df["Dyslexia-Friendly Score"].mean()

    title = metadata.get("Title", "Readability Validation Report") if metadata else "Readability Validation Report"

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 20)
    pdf.cell(0, 10, sanitize_text(title), ln=True, align="L")
    pdf.set_font("Arial", 'I', 14)
    pdf.cell(0, 10, sanitize_text("Powered by Howard Forge Press"), ln=True)
    if logo_path and os.path.exists(logo_path):
        pdf.image(logo_path, x=170, y=10, w=30)

    pdf.set_font("Arial", '', 12)
    pdf.ln(10)
    score_guide = [
        "< 40 : Highly Challenging",
        "40-50 : Challenging",
        "50-55 : Dyslexia-Friendly",
        "55-60 : Highly Dyslexia-Friendly",
        "> 60 : Extremely Dyslexia-Friendly"
    ]
    pdf.cell(0, 8, sanitize_text("Dyslexia-Friendly Scoring Guide:"), ln=True)
    for line in score_guide:
        pdf.cell(0, 8, sanitize_text(line), ln=True)

    pdf.set_font("Arial", 'B', 14)
    pdf.ln(5)
    pdf.cell(0, 10, sanitize_text(f"Overall Dyslexia-Friendly Score: {avg_score:.2f}"), ln=True)

    pdf.set_font("Arial", '', 12)
    pdf.ln(5)
    lowest_text = (
        f"Lowest scoring chapter: {lowest['Chapter']} with a DF Score of {lowest['Dyslexia-Friendly Score']:.2f}. "
        f"This chapter had high {df.drop(columns=['Chapter']).iloc[lowest.name].idxmin()} which contributed to difficulty.")
    pdf.multi_cell(0, 8, sanitize_text(lowest_text))
    pdf.ln(2)
    highest_text = (
        f"Highest scoring chapter: {highest['Chapter']} with a DF Score of {highest['Dyslexia-Friendly Score']:.2f}. "
        f"Strong performance in {df.drop(columns=['Chapter']).iloc[highest.name].idxmax()} helped readability.")
    pdf.multi_cell(0, 8, sanitize_text(highest_text))

    plt.figure(figsize=(10, 4))
    sns.heatmap(z_scores.set_index("Chapter").transpose(), cmap="coolwarm", center=0, cbar_kws={'label': 'Z-score'})
    plt.title("Z-Score Heatmap")
    heatmap_path = "heatmap_temp.png"
    plt.tight_layout()
    plt.savefig(heatmap_path)
    plt.close()

    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, sanitize_text("Z-Score Heatmap"), ln=True)
    pdf.image(heatmap_path, x=10, y=25, w=180)

    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, sanitize_text("Chapter Outlier Explanations"), ln=True)
    pdf.set_font("Arial", '', 12)
    for _, row in outlier_rows.iterrows():
        chap = row["Chapter"]
        explanation = []
        for col in feature_cols:
            if abs(row[col]) > 2:
                direction = "high" if row[col] > 0 else "low"
                explanation.append(f"{direction} {col}")
        if explanation:
            feat_list = ", ".join(explanation)
            impact = "improve" if df.loc[row.name, "Dyslexia-Friendly Score"] > 55 else "reduce"
            msg = f"Chapter {chap} has outliers in: {feat_list}. These may {impact} the DF Score."
            pdf.multi_cell(0, 8, sanitize_text(msg))
            pdf.ln(1)

    appendix_text = '''Appendix: Explanation of Features

- Sentence Count - Total number of sentences in the chapter.
- Word Count - Total number of words.
- Avg Sentence Length - Longer sentences often reduce readability.
- Average Word Length - Longer words are harder to decode.
- Syllables per Word - Higher syllable counts increase complexity.
- Passive Sentences - Indirect grammar is harder to follow.
- Rare/Abstract Words - Difficult to visualize or decode.
- Sensory Words - Support mental imagery and comprehension.
- Dyslexia-Friendly Score - Overall accessibility estimate (0–100).'''
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, sanitize_text("Appendix: Feature Definitions"), ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 8, sanitize_text(appendix_text))

    pdf_output = pdf.output(dest='S').encode('latin1')
    pdf_buffer = BytesIO()
    pdf_buffer.write(pdf_output)
    pdf_buffer.seek(0)

    if os.path.exists(heatmap_path):
        os.remove(heatmap_path)

    return pdf_buffer
