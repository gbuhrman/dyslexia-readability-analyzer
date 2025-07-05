
import re

def count_syllables(word):
    return len(re.findall(r'[aeiouy]+', word.lower()))

def analyze_text(text):
    sentences = re.split(r'(?<=[.!?]) +', text.strip())
    words = re.findall(r'\b\w+\b', text)
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
