
import re
import pandas as pd
import numpy as np
import pickle
from nltk.tokenize import word_tokenize
import string

# Load the Punkt sentence tokenizer from bundled file
with open("tokenizers/punkt/english.pickle", "rb") as f:
    sentence_tokenizer = pickle.load(f)

def analyze_text(text):
    sentences = sentence_tokenizer.tokenize(text.strip())
    words = word_tokenize(text)
    num_sentences = len(sentences)
    num_words = len(words)
    avg_sentence_len = np.mean([len(word_tokenize(s)) for s in sentences]) if sentences else 0
    avg_word_len = np.mean([len(w) for w in words]) if words else 0
    syllables_per_word = np.mean([count_syllables(w) for w in words]) if words else 0
    passive_sentences = sum([1 for s in sentences if is_passive(s)])
    percent_passive = passive_sentences / num_sentences * 100 if num_sentences else 0
    rare_word_ratio = count_rare_words(words)
    sensory_score = count_sensory_words(text)
    df_score = compute_df_score(avg_sentence_len, avg_word_len, syllables_per_word,
                                percent_passive, rare_word_ratio, sensory_score)

    return {
        "Sentence Count": num_sentences,
        "Word Count": num_words,
        "Avg Sentence Length": avg_sentence_len,
        "Average Word Length": avg_word_len,
        "Syllables per Word": syllables_per_word,
        "Passive Sentences": percent_passive,
        "Rare/Abstract Words": rare_word_ratio,
        "Sensory Words": sensory_score,
        "Dyslexia-Friendly Score": df_score
    }

def count_syllables(word):
    word = word.lower()
    return len(re.findall(r"[aeiouy]+", word))

def is_passive(sentence):
    return bool(re.search(r"\b(is|was|were|are|been|being|be)\b\s+\w+ed\b", sentence))

def count_rare_words(words):
    abstract_words = set(["freedom", "justice", "truth", "power", "emotion", "idea", "knowledge"])
    return sum(1 for w in words if w.lower() in abstract_words) / len(words) if words else 0

def count_sensory_words(text):
    sensory_vocab = ["see", "hear", "smell", "touch", "taste", "bright", "dark", "loud", "soft", "cold", "hot"]
    text_lower = text.lower()
    return sum(1 for word in sensory_vocab if word in text_lower)

def compute_df_score(avg_sent_len, avg_word_len, syllables, passive_pct, rare_ratio, sensory):
    base = 100
    deductions = (
        0.75 * max(0, avg_sent_len - 18) +
        0.5 * max(0, avg_word_len - 5) +
        1.0 * max(0, syllables - 1.5) +
        0.3 * passive_pct +
        30 * rare_ratio -
        0.5 * sensory
    )
    score = base - deductions
    return max(0, min(100, score))
