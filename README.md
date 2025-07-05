
# Dyslexia-Friendly Readability Analyzer

This tool evaluates how accessible a piece of writing is for dyslexic readers using a combination of textual analysis, readability metrics, and sensory engagement measures.

## 🧰 Features

- Upload `.docx` or `.txt` files for analysis
- Calculates:
  - Sentence and word counts
  - Average sentence and word length
  - Average syllables per word
  - Passive voice usage
  - Lexical variety and rare/abstract word count
  - Sensory language counts (sight, sound, touch, smell, taste)
- Computes a **Dyslexia-Friendly Score** (0–100) based on these metrics
- Provides a downloadable `.csv` report
- Includes a **Feature Importance Chart** based on logistic regression analysis
- Designed to support both writers and educators

## 📈 New Feature: Composite Readability Score

We’ve developed a custom scoring function that weights key features known to affect readability for dyslexic readers. The formula prioritizes:
- Concise sentences
- Concrete and sensory-rich vocabulary
- Low passive voice usage
- Reduced rare or abstract words

The final score is on a **0–100 scale**, with higher scores indicating more dyslexia-friendly content.

## 🔬 Validation Summary

To validate our scoring system:
1. We analyzed 6 known text samples:
   - 3 considered **difficult** for dyslexic readers (e.g., Moby Dick)
   - 3 known to be **accessible** (e.g., Barrington Stoke-style writing)
2. We computed metrics for each and labeled them “Easy” or “Hard”
3. We trained a **logistic regression model** to classify difficulty based on those features
4. Results:
   - 100% classification accuracy on labeled set
   - Key features aligned with intuition (sentence length, sensory language, rare word usage)
5. The **feature importance chart** is included in the app to show which metrics most influence readability

As we collect more feedback and test data, the model will continue to evolve.

## 🔗 Deployment

This app runs on [Streamlit Cloud](https://streamlit.io/cloud) and can be embedded or linked from author websites, educator platforms, or reading support tools.

Created by **Howard Forge Press**  
🔗 [www.howardforgepress.com](https://www.howardforgepress.com)

