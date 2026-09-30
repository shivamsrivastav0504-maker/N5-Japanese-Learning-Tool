from functools import lru_cache

import fugashi


@lru_cache(maxsize=1)
def _get_tagger() -> fugashi.Tagger:
	return fugashi.Tagger()


def tokenize(sentence: str) -> list[dict[str, str]]:
	"""Split a Japanese sentence into surface forms, lemmas, and readings."""
	if not sentence.strip():
		return []

	tokens: list[dict[str, str]] = []
	for item in _get_tagger()(sentence):
		features = item.feature
		surface = item.surface
		tokens.append(
			{
				"surface": surface,
				"lemma": getattr(features, "lemma", "") or surface,
				"reading": getattr(features, "kana", "")
				or getattr(features, "pron", "")
				or surface,
				"part_of_speech": getattr(features, "pos1", ""),
			}
		)
	return tokens
