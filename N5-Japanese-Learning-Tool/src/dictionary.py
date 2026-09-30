import csv
from pathlib import Path

from src.romaji import to_hiragana


VOCABULARY_PATH = Path(__file__).resolve().parents[1] / "data" / "n5_vocabulary.csv"
PARTICLES_PATH = Path(__file__).resolve().parents[1] / "data" / "japanese_particles.csv"
HIRAGANA_WORDS_PATH = Path(__file__).resolve().parents[1] / "data" / "hiragana_words.csv"
PUNCTUATION_PATH = Path(__file__).resolve().parents[1] / "data" / "japanese_punctuation.csv"


def _normalize(value: str) -> str:
	return value.strip().casefold()


def _is_n5(level: str) -> bool:
	return _normalize(level).replace(" ", "").replace("-", "") in {
		"n5",
		"jlptn5",
	}


def _read_rows(path: Path) -> list[dict[str, str]]:
	if not path.exists():
		return []
	with path.open("r", encoding="utf-8-sig", newline="") as csv_file:
		return list(csv.DictReader(csv_file))


def lookup_tokens(
	tokens: list[dict[str, str]],
	vocabulary_path: Path = VOCABULARY_PATH,
) -> list[dict[str, str | bool]]:
	"""Combine meanings from the current N5, hiragana, and particle CSV files."""
	vocabulary: dict[str, dict[str, str]] = {}
	for entry in _read_rows(vocabulary_path):
		word = entry.get("word", "").strip()
		if word:
			vocabulary.setdefault(_normalize(word), entry)

	hiragana_words: dict[str, dict[str, str]] = {}
	for entry in _read_rows(HIRAGANA_WORDS_PATH):
		word = entry.get("hiragana", "").strip()
		if word:
			hiragana_words.setdefault(_normalize(word), entry)

	particles: dict[str, dict[str, str]] = {}
	for particle in _read_rows(PARTICLES_PATH):
		word = particle.get("particle", "").strip()
		if word:
			particles.setdefault(_normalize(word), particle)

	punctuation: dict[str, dict[str, str]] = {}
	for mark in _read_rows(PUNCTUATION_PATH):
		word = mark.get("punctuation", "").strip()
		if word:
			punctuation.setdefault(_normalize(word), mark)

	results: list[dict[str, str | bool]] = []
	for token in tokens:
		entry = vocabulary.get(_normalize(token.get("lemma", "")))
		if entry is None:
			entry = vocabulary.get(_normalize(token.get("surface", "")), {})
		hiragana_entry = hiragana_words.get(
			_normalize(to_hiragana(token.get("reading", ""))), {}
		)
		particle_entry = {}
		if token.get("part_of_speech") == "助詞":
			particle_entry = particles.get(_normalize(token.get("surface", "")), {})
		punctuation_entry = {}
		if token.get("part_of_speech") == "補助記号":
			punctuation_entry = punctuation.get(
				_normalize(token.get("surface", "")), {}
			)

		if punctuation_entry:
			level = "Punctuation"
		elif entry:
			level = entry.get("level", "").strip() or "N5"
		elif hiragana_entry:
			level = hiragana_entry.get("level", "").strip() or "N5"
		else:
			level = ""
		results.append(
			{
				**token,
				"hiragana": entry.get("reading", "").strip()
				or hiragana_entry.get("hiragana", "").strip()
				or particle_entry.get("reading", "").strip()
				or token.get("reading", ""),
				"meaning": entry.get("meaning", "").strip()
				or hiragana_entry.get("meaning", "").strip()
				or particle_entry.get("meaning", "").strip()
				or punctuation_entry.get("meaning", "").strip(),
				"level": level
				or ("Particle" if particle_entry else "Not listed"),
				"is_n5": False if punctuation_entry else _is_n5(level),
				"particle_role": particle_entry.get("role", ""),
				"particle_romaji": particle_entry.get("romaji", ""),
				"particle_example": particle_entry.get("example", ""),
				"particle_example_translation": particle_entry.get(
					"example_translation", ""
				),
			}
		)
	return results
