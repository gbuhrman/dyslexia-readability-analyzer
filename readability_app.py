
import streamlit as st
import pandas as pd
import docx2txt
import re
from io import StringIO

# === Helper Functions ===
def count_sentences(text):
    return len(re.findall(r'[.!?]', text))

def count_words(text):
    return len(re.findall(r'\b\w+\b', text))

def count_syllables(word):
    return len(re.findall(r'[aeiouy]+', word.lower()))

def average_sentence_length(text):
    return count_words(text) / max(1, count_sentences(text))

def average_word_length(text):
    words = re.findall(r'\b\w+\b', text)
    return sum(len(word) for word in words) / max(1, len(words))

def average_syllables_per_word(text):
    words = re.findall(r'\b\w+\b', text)
    return sum(count_syllables(word) for word in words) / max(1, len(words))

def detect_passive_sentences(text):
    return len(re.findall(r'\b(is|was|were|been|being|are|am|be)\b\s+\w+ed\b', text))

def lexical_analysis(text):
    words = re.findall(r'\b\w+\b', text.lower())
    unique_words = len(set(words))
    rare_words = sum(1 for w in words if len(w) > 10 or w.endswith(('ion', 'ity', 'ment')))
    return unique_words, rare_words

def count_sensory_words(text):
    senses = {
        'sight': ['look', 'see', 'glance', 'watch', 'glow', 'color', 'shine'],
        'sound': ['hear', 'sound', 'ring', 'roar', 'echo', 'clang'],
        'touch': ['feel', 'touch', 'warm', 'cold', 'rough', 'smooth'],
        'smell': ['smell', 'scent', 'odor', 'fragrance'],
        'taste': ['taste', 'flavor', 'bitter', 'sweet']
    }
    sense_counts = {sense: sum(text.lower().count(word) for word in words) for sense, words in senses.items()}
    return sense_counts

def compute_readability_score(avg_sentence_len, avg_word_len, avg_syllables, passive_ratio, sensory_ratio, rare_word_ratio):
    score = (
        30 * (1 - min(avg_sentence_len / 20, 1)) +
        15 * (1 - min(avg_word_len / 8, 1)) +
        15 * (1 - min(avg_syllables / 3, 1)) +
        10 * (1 - passive_ratio) +
        10 * sensory_ratio +
        20 * (1 - rare_word_ratio)
    )
    return round(score, 2)

# === Streamlit UI ===
st.set_page_config(page_title="Dyslexia-Friendly Readability Analyzer")
st.title("Dyslexia-Friendly Readability Analyzer")
st.markdown("Created by **Howard Forge Press**  |  [Visit Website](https://www.howardforgepress.com)")

st.markdown("""
Upload a `.docx` or `.txt` file, and this tool will evaluate:
- Sentence and word count
- Sentence and word complexity
- Passive voice usage
- Lexical variety and abstract vocabulary
- Sensory language (sight, sound, touch, smell, taste)
- **Overall Dyslexia-Friendly Score** (0–100)
""")

uploaded_file = st.file_uploader("Choose a .docx or .txt file", type=["docx", "txt"])

if uploaded_file:
    if uploaded_file.name.endswith(".docx"):
        text = docx2txt.process(uploaded_file)
    else:
        text = StringIO(uploaded_file.getvalue().decode("utf-8")).read()

    sentence_count = count_sentences(text)
    word_count = count_words(text)
    avg_sentence_len = average_sentence_length(text)
    avg_word_len = average_word_length(text)
    avg_syllables = average_syllables_per_word(text)
    passive_count = detect_passive_sentences(text)
    passive_ratio = passive_count / max(1, sentence_count)
    unique_words, rare_words = lexical_analysis(text)
    rare_word_ratio = rare_words / max(1, word_count)
    sensory_counts = count_sensory_words(text)
    sensory_total = sum(sensory_counts.values())
    sensory_ratio = sensory_total / max(1, word_count)

    readability_score = compute_readability_score(
        avg_sentence_len, avg_word_len, avg_syllables,
        passive_ratio, sensory_ratio, rare_word_ratio
    )

    full_analysis = {
        "Sentence Count": sentence_count,
        "Word Count": word_count,
        "Avg Sentence Length (words)": avg_sentence_len,
        "Avg Word Length (characters)": avg_word_len,
        "Avg Syllables per Word": avg_syllables,
        "Passive Voice Sentences": passive_count,
        "Unique Word Count": unique_words,
        "Rare/Abstract Words": rare_words,
        "Sight Words": sensory_counts["sight"],
        "Sound Words": sensory_counts["sound"],
        "Touch Words": sensory_counts["touch"],
        "Smell Words": sensory_counts["smell"],
        "Taste Words": sensory_counts["taste"],
        "Dyslexia-Friendly Score (0–100)": readability_score
    }

    analysis_df = pd.DataFrame.from_dict(full_analysis, orient='index', columns=["Value"])
    st.subheader("Readability and Engagement Analysis")
    st.dataframe(analysis_df)

    csv_data = analysis_df.to_csv().encode("utf-8")
    st.download_button(
        label="Download Analysis as CSV",
        data=csv_data,
        file_name="readability_analysis.csv",
        mime="text/csv"
    )

    st.subheader("📋 Feature Importance Table")
    st.write("This table shows how each feature influenced readability classification in early model testing.")
    st.write("**Positive values** lean toward harder texts. **Negative values** lean toward easier texts.")

    importance_df = pd.read_csv("embedded_feature_importance.csv")
    if 'Unnamed: 0' in importance_df.columns:
        importance_df.rename(columns={"Unnamed: 0": "Feature"}, inplace=True)
    importance_df = importance_df.sort_values(by="Importance", ascending=False)
    importance_df.columns = ["Feature", "Coefficient"]
    st.dataframe(importance_df)
