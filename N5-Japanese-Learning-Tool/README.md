# N5 Japanese Learning Tool

A Streamlit application for translating between English and Japanese and studying the Japanese text with word meanings, kanji, hiragana readings, romaji, and N5 vocabulary. The interface uses a black and violet theme with side-by-side source and translation panes.

This project was developed with the assistance of AI tools.

## Workflow

1. Select English-to-Japanese or Japanese-to-English.
2. Enter a sentence and request a translation.
3. Analyze the Japanese text with the tokenizer and local vocabulary files.
4. Display kanji, hiragana, romaji, English meanings, and N5 matches.

Translation uses `deep-translator` with MyMemory as the primary provider and Google Translate as a fallback. Both services require internet access and may be subject to service limits. Local word meanings and N5 matches depend on the entries in the CSV files.

## Project structure

```text
N5-Japanese-Learning-Tool/
|-- app.py                     # Streamlit application entry point
|-- requirements.txt           # Python dependencies
|-- README.md                  # Project documentation
|-- data/
|   |-- n5_vocabulary.csv      # Curated JLPT N5 vocabulary starter list
|   |-- japanese_particles.csv # Particle roles and example translations
|   |-- hiragana_words.csv     # Hiragana-only words and English meanings
|   `-- japanese_punctuation.csv # Japanese punctuation explanations
`-- src/
	|-- tokenizer.py           # Japanese sentence tokenization
	|-- dictionary.py          # Vocabulary and dictionary lookup
	|-- romaji.py              # Romaji generation
	`-- translator.py          # Translation service integration
```

## Project status

The Streamlit interface and processing modules are implemented. The vocabulary CSV contains a curated N5 starter list; JLPT does not publish one definitive vocabulary list, so this data is not exhaustive. Add more entries as needed. Translation requires an internet connection.

The N5 vocabulary CSV contains only kanji entries and uses the columns `word`, `reading`, and `meaning`. Every row in this file is treated as an N5 entry; kana-only words are kept separately in `hiragana_words.csv`.

The particle reference uses `particle`, `role`, `reading`, `romaji`, `meaning`, `example`, `example_reading`, and `example_translation`. The N5 hiragana dictionary uses only `hiragana` and `meaning`; every row is treated as N5 and contains a complete kana word, not an individual character. The punctuation reference uses `punctuation` and `meaning`; punctuation is shown for learning but is not counted as N5 vocabulary. Sentence breakdown meanings can come from all four CSV files.

## Planned setup

Create and activate a Python virtual environment, install the dependencies, and launch the Streamlit app:

```bash
python -m venv .venv
python -m pip install -r requirements.txt
streamlit run app.py
```

On Windows PowerShell, activate the environment with:

```powershell
.venv\Scripts\Activate.ps1
```

