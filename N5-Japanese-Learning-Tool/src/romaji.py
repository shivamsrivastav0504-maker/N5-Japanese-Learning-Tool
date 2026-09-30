import pykakasi


_CONVERTER = pykakasi.kakasi()


def to_hiragana(text: str) -> str:
	if not text:
		return ""
	return "".join(part["hira"] for part in _CONVERTER.convert(text))


def to_romaji(text: str) -> str:
	if not text:
		return ""
	return "".join(part["hepburn"] for part in _CONVERTER.convert(text))


def add_readings(tokens: list[dict[str, str | bool]]) -> list[dict[str, str | bool]]:
	"""Add hiragana and romaji display fields to dictionary results."""
	results: list[dict[str, str | bool]] = []
	for token in tokens:
		reading = str(token.get("hiragana") or token.get("reading") or token["surface"])
		results.append(
			{
				**token,
				"hiragana": to_hiragana(reading),
				"romaji": str(token.get("particle_romaji") or to_romaji(reading)),
			}
		)
	return results
