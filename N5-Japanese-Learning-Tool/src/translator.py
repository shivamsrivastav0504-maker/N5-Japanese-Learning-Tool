from deep_translator import GoogleTranslator, MyMemoryTranslator


def translate_text(
	sentence: str,
	source_language: str = "ja",
	target_language: str = "en",
) -> str:
	"""Translate between English and Japanese using the configured providers."""
	if not sentence.strip():
		raise ValueError("Enter text to translate.")

	language_codes = {
		"en": {"mymemory": "en-US", "google": "en"},
		"ja": {"mymemory": "ja-JP", "google": "ja"},
	}
	if source_language not in language_codes or target_language not in language_codes:
		raise ValueError("Only English and Japanese translation is supported.")
	if source_language == target_language:
		raise ValueError("Choose different source and target languages.")

	try:
		translation = MyMemoryTranslator(
			source=language_codes[source_language]["mymemory"],
			target=language_codes[target_language]["mymemory"],
		).translate(sentence)
	except Exception as primary_error:
		try:
			translation = GoogleTranslator(
				source=language_codes[source_language]["google"],
				target=language_codes[target_language]["google"],
			).translate(sentence)
		except Exception as fallback_error:
			raise RuntimeError(
				"Translation failed with both providers. "
				f"MyMemory: {primary_error}. Google Translate: {fallback_error}"
			) from fallback_error

	if not translation:
		raise RuntimeError("The translation service returned no result.")
	return translation
