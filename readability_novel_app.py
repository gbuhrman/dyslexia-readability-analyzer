
import streamlit as st
import pandas as pd
import re
import docx2txt
from io import StringIO
import base64

# === Helper Functions ===
def simple_sent_tokenize(text):
    return re.split(r'(?<=[.!?]) +', text.strip())

def simple_word_tokenize(text):
    return re.findall(r'\b\w+\b', text)

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

def count_syllables(word):
    return len(re.findall(r'[aeiouy]+', word.lower()))

def analyze_text_basic(text):
    sentences = simple_sent_tokenize(text)
    words = simple_word_tokenize(text)
    word_count = len(words)
    sentence_count = len(sentences)
    avg_sentence_len = word_count / max(1, sentence_count)
    avg_word_len = sum(len(w) for w in words) / max(1, word_count)
    avg_syllables = sum(count_syllables(w) for w in words) / max(1, word_count)
    passive_count = len(re.findall(r'\b(is|was|were|been|being|are|am|be)\b\s+\w+ed\b', text))
    rare_words = sum(1 for w in words if len(w) > 10 or w.endswith(('ion', 'ity', 'ment')))
    sensory_words = sum(1 for w in words if w.lower() in [
        'look', 'see', 'glance', 'watch', 'glow', 'color', 'shine',
        'hear', 'sound', 'ring', 'roar', 'echo', 'clang',
        'feel', 'touch', 'warm', 'cold', 'rough', 'smooth',
        'smell', 'scent', 'odor', 'fragrance',
        'taste', 'flavor', 'bitter', 'sweet'
    ])
    sensory_ratio = sensory_words / max(1, word_count)
    passive_ratio = passive_count / max(1, sentence_count)
    rare_ratio = rare_words / max(1, word_count)

    score = (
        30 * (1 - min(avg_sentence_len / 20, 1)) +
        15 * (1 - min(avg_word_len / 8, 1)) +
        15 * (1 - min(avg_syllables / 3, 1)) +
        10 * (1 - passive_ratio) +
        10 * sensory_ratio +
        20 * (1 - rare_ratio)
    )

    return {
        "Sentence Count": sentence_count,
        "Word Count": word_count,
        "Avg Sentence Length": avg_sentence_len,
        "Avg Word Length": avg_word_len,
        "Avg Syllables per Word": avg_syllables,
        "Passive Sentences": passive_count,
        "Rare/Abstract Words": rare_words,
        "Sensory Words": sensory_words,
        "Dyslexia-Friendly Score": round(score, 2)
    }

# === Streamlit UI ===
st.set_page_config(page_title="Novel Chapter Analyzer")
st.title("📘 Dyslexia-Friendly Chapter Analyzer")
st.markdown("Upload a full novel `.docx` file. The app will split by chapters and generate a readability score for each.")

uploaded_file = st.file_uploader("Upload your novel (.docx)", type=["docx"])

if uploaded_file:
    with st.spinner("Processing... please wait."):
        text = docx2txt.process(uploaded_file)
        chapters = split_into_chapters(text)
        results = []

        for idx, (title, chap_text) in enumerate(chapters):
            metrics = analyze_text_basic(chap_text)
            metrics["Chapter"] = f"Chapter {idx + 1}"
            results.append(metrics)

        df = pd.DataFrame(results)
        df = df[["Chapter"] + [col for col in df.columns if col != "Chapter"]]

        st.success(f"Analyzed {len(df)} chapters.")
        st.dataframe(df)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download Chapter Analysis (.csv)", csv, "chapter_readability_analysis.csv", "text/csv")
