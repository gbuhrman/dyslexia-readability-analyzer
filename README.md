# Dyslexia-Friendly Validation Report Generator

This tool creates enhanced Dyslexia-Friendly Validation Reports from chapter-level readability data. Reports are formatted as multi-page PDFs including:

- Title page with average readability score
- Z-score heatmap of key features by chapter
- Paginated Outlier Tables with styled formatting
- Chapter-specific narrative insights
- Full Feature Explanation Appendix

## 🔧 How It Works

This module assumes you have a `.csv` file exported from the Dyslexia Readability Analyzer containing chapter-level metrics.

---

### 📉 Limitations & Intended Use

> **Disclaimer:** This tool uses a lightweight, simplified implementation of sentence and word counting to support rapid and scalable analysis. While effective for relative comparisons and visualizations, it is **not intended to match the precision** of more mature tools like **Microsoft Word's Readability Checker** or professional linguistic platforms.

> As a result, all output values — including **Flesch-Kincaid Grade Level** and **Dyslexia-Friendly Score** — should be treated as **approximate**. These values are not suitable for publication-quality analysis and should **not be used for clinical or educational diagnosis** without further validation.

> The core utility of this tool lies in **highlighting trends**, **detecting outliers**, and **supporting exploratory research** on narrative-level readability in long-form fiction.

---

### Required Columns
- Chapter
- Sentence Count
- Word Count
- Avg Sentence Length
- Avg Word Length
- Avg Syllables per Word
- Passive Sentences
- Rare/Abstract Words
- Sensory Words
- Dyslexia-Friendly Score

### How to Use

1. Place your input CSV file into the project directory.
2. Run the `validation_report_generator.py` script.
3. Your PDF will be saved in the output directory.

### Run from Streamlit
This script is compatible with Streamlit apps. You can import it into your `readability_novel_app.py` and call it after analysis.

```python
from validation_report_generator import generate_validation_report
generate_validation_report("chapter_readability_analysis.csv", "Your_Title_Here")


- matplotlib
- seaborn
- numpy
- nltk
- fpdf
- streamlit

## 🏷️ License
This project is open source under the MIT License. Created by Howard Forge Press.
