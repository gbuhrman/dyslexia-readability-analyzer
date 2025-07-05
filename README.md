
# Dyslexia-Friendly Chapter Analyzer

This Streamlit app processes a full novel in `.docx` format, detects chapters automatically, and performs a chapter-by-chapter readability analysis. The output includes sentence complexity, passive voice, sensory language, and a custom Dyslexia-Friendly Score.

## 🚀 Features
- Upload a full `.docx` manuscript
- Automatically splits the text into chapters using common patterns like "Chapter 1", "CHAPTER ONE", etc.
- Calculates:
  - Sentence Count
  - Word Count
  - Average Sentence Length
  - Average Word Length
  - Average Syllables per Word
  - Passive Voice Count
  - Rare/Abstract Word Count
  - Sensory Word Count
  - Dyslexia-Friendly Score (0–100)
- Downloadable chapter metrics as a `.csv` file

## 📂 File Upload
Upload a `.docx` file. The app will extract and analyze each chapter.

## 📥 Output
A downloadable `.csv` file is provided with one row per chapter and all relevant readability metrics.

## 📦 Requirements
Install dependencies using:

```
pip install -r requirements.txt
```

## 🖥 Deployment
Deploy via [Streamlit Cloud](https://streamlit.io/cloud) by connecting your GitHub repository. Ensure `readability_novel_app.py` is set as the main entry point.

---

Created by [Howard Forge Press](https://www.howardforgepress.com)
