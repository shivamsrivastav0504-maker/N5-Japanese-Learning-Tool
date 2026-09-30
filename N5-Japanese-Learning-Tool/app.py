from html import escape

import streamlit as st

from src.dictionary import lookup_tokens
from src.romaji import add_readings
from src.tokenizer import tokenize
from src.translator import translate_text


LANGUAGE_PAIRS = {
	"English → Japanese": ("en", "ja"),
	"Japanese → English": ("ja", "en"),
}
EXAMPLE_TEXT = "Next spring, I want to see the cherry blossoms in Kyoto."

st.set_page_config(
	page_title="Kotoba | Japanese Translator",
	page_icon="語",
	layout="wide",
)

st.markdown(
	"""
	<style>
	@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Space+Grotesk:wght@400;500;600;700&display=swap');
	:root {
		--ink: #f4f0fa;
		--muted: #aaa2b8;
		--violet: #b89aff;
		--violet-dark: #211832;
		--lime: #c9f27a;
		--line: rgba(206, 185, 255, 0.16);
		--panel: rgba(22, 17, 31, 0.92);
	}
	[data-testid="stAppViewContainer"] {
		background-color: #0b0910;
		background-image:
			linear-gradient(rgba(179, 147, 240, 0.035) 1px, transparent 1px),
			linear-gradient(90deg, rgba(179, 147, 240, 0.035) 1px, transparent 1px),
			linear-gradient(140deg, #100b17 0%, #0b0910 56%, #100c17 100%);
		background-size: 34px 34px, 34px 34px, 100% 100%;
		color: var(--ink);
	}
	[data-testid="stHeader"] { background: transparent; }
	.block-container { max-width: 1220px; padding-top: 2rem; padding-bottom: 3rem; }
	h1, h2, h3, label, p, button, input, textarea {
		font-family: 'Space Grotesk', 'Yu Gothic UI', sans-serif;
		color: var(--ink);
	}
	.brand-row { display: flex; align-items: center; gap: 12px; margin-bottom: 25px; }
	.brand-mark {
		width: 42px; height: 42px; display: grid; place-items: center;
		border: 1px solid rgba(200, 173, 255, 0.4); border-radius: 8px;
		background: #211832; color: var(--violet); font-size: 22px; font-weight: 700;
	}
	.brand-name { color: var(--ink); font-size: 15px; font-weight: 700; }
	.brand-meta { color: var(--muted); font-family: 'DM Mono', monospace; font-size: 10px; letter-spacing: 1px; }
	.eyebrow { color: var(--violet); font-family: 'DM Mono', monospace; font-size: 11px; letter-spacing: 1px; text-transform: uppercase; }
	.pane-title { color: var(--ink); font-size: 14px; font-weight: 600; margin: 0 0 10px 0; }
	.output-copy {
		box-sizing: border-box; min-height: 228px; white-space: pre-wrap; overflow-wrap: anywhere;
		padding: 16px; border: 1px solid var(--line); border-radius: 8px;
		background: rgba(12, 10, 17, 0.88); color: var(--ink); line-height: 1.8;
	}
	.output-empty { color: #81798f; }
	.direction-arrow { color: var(--violet); font-size: 22px; text-align: center; padding-top: 95px; }
	div[data-testid="stVerticalBlockBorderWrapper"] {
		background: var(--panel); border-color: var(--line); border-radius: 8px;
	}
	.stTextArea textarea {
		background: rgba(12, 10, 17, 0.88); color: var(--ink);
		border: 1px solid var(--line); border-radius: 8px; line-height: 1.7;
	}
	.stTextArea textarea:focus { border-color: var(--violet); box-shadow: 0 0 0 1px var(--violet); }
	.stRadio > div { gap: 8px; }
	.stRadio label {
		padding: 7px 12px; border: 1px solid var(--line); border-radius: 8px;
		background: rgba(24, 19, 33, 0.8);
	}
	.stButton > button {
		min-height: 44px; border: 1px solid #b89aff; border-radius: 8px;
		background: #b89aff; color: #110c19; font-weight: 700;
	}
	.stButton > button:hover { border-color: var(--lime); background: var(--lime); color: #10110b; }
	[data-testid="stMetric"] {
		padding: 12px 14px; border: 1px solid var(--line); border-radius: 8px;
		background: rgba(22, 17, 31, 0.9);
	}
	[data-testid="stMetricLabel"] { color: var(--muted); }
	[data-testid="stDataFrame"] { border: 1px solid var(--line); border-radius: 8px; overflow: hidden; }
	.kanji-run { color: var(--violet); font-size: 23px; line-height: 1.8; }
	@media (max-width: 700px) {
		.block-container { padding-left: 1rem; padding-right: 1rem; }
		.direction-arrow { display: none; }
	}
	</style>
	""",
	unsafe_allow_html=True,
)

if "source_text" not in st.session_state:
	st.session_state.source_text = EXAMPLE_TEXT
if "translation_result" not in st.session_state:
	st.session_state.translation_result = ""
if "translation_error" not in st.session_state:
	st.session_state.translation_error = ""
if "analysis_results" not in st.session_state:
	st.session_state.analysis_results = []
if "japanese_text" not in st.session_state:
	st.session_state.japanese_text = ""

st.markdown(
	'<div class="brand-row"><div class="brand-mark">語</div>'
	'<div><div class="brand-name">KOTOBA</div>'
	'<div class="brand-meta">JAPANESE SENTENCE LAB</div></div></div>',
	unsafe_allow_html=True,
)
st.title("Sentence translator")

direction = st.radio(
	"Translation direction",
	options=list(LANGUAGE_PAIRS),
	horizontal=True,
	label_visibility="collapsed",
	key="translation_direction",
)
source_language, target_language = LANGUAGE_PAIRS[direction]
source_name = "English" if source_language == "en" else "Japanese"
target_name = "English" if target_language == "en" else "Japanese"

source_panel, arrow_panel, output_panel = st.columns([1, 0.08, 1], gap="small")
with source_panel:
	with st.container(border=True):
		st.markdown(f'<div class="eyebrow">{source_name} text</div>', unsafe_allow_html=True)
		source_text = st.text_area(
			f"{source_name} text",
			key="source_text",
			label_visibility="collapsed",
			placeholder="Type or paste a sentence...",
			max_chars=1000,
			height=190,
		)
		st.caption(f"{len(source_text)} / 1,000")
		submitted = st.button("Translate", type="primary", use_container_width=True)

if submitted:
	st.session_state.translation_error = ""
	st.session_state.translation_result = ""
	st.session_state.analysis_results = []
	st.session_state.japanese_text = ""
	if not source_text.strip():
		st.session_state.translation_error = "Enter text to translate."
	else:
		try:
			with st.spinner("Translating..."):
				translation = translate_text(source_text, source_language, target_language)
			st.session_state.translation_result = translation
			japanese_text = source_text if source_language == "ja" else translation
			st.session_state.japanese_text = japanese_text
			with st.spinner("Reading the Japanese sentence..."):
				tokens = tokenize(japanese_text)
				st.session_state.analysis_results = add_readings(lookup_tokens(tokens))
		except Exception as error:
			st.session_state.translation_error = str(error)

with arrow_panel:
	st.markdown('<div class="direction-arrow">→</div>', unsafe_allow_html=True)

with output_panel:
	with st.container(border=True):
		st.markdown(f'<div class="eyebrow">{target_name} translation</div>', unsafe_allow_html=True)
		if st.session_state.translation_error:
			st.error(st.session_state.translation_error)
		elif st.session_state.translation_result:
			st.markdown(
				f'<div class="output-copy">{escape(st.session_state.translation_result)}</div>',
				unsafe_allow_html=True,
			)
		else:
			st.markdown(
				'<div class="output-copy output-empty">Translation appears here.</div>',
				unsafe_allow_html=True,
			)

analysis_results = st.session_state.analysis_results
japanese_text = st.session_state.japanese_text
if analysis_results:
	st.divider()
	word_count = len(analysis_results)
	n5_results = [result for result in analysis_results if result["is_n5"]]
	kanji = list(dict.fromkeys(char for char in japanese_text if "\u4e00" <= char <= "\u9fff"))

	metric_words, metric_n5 = st.columns(2)
	metric_words.metric("Words analyzed", word_count)
	metric_n5.metric("N5 kanji", len(n5_results))

	if kanji:
		st.markdown('<div class="eyebrow">KANJI IN THIS SENTENCE</div>', unsafe_allow_html=True)
		st.markdown(
			f'<div class="kanji-run">{"　".join(escape(char) for char in kanji)}</div>',
			unsafe_allow_html=True,
		)

	all_words_tab, n5_tab = st.tabs(["Word breakdown", "N5 words"])
	with all_words_tab:
		st.dataframe(
			[
				{
					"Word": result["surface"],
					"Hiragana": result["hiragana"],
					"Romaji": result["romaji"],
					"English meaning": result["meaning"] or "No local meaning found",
					"JLPT level": result["level"],
				}
				for result in analysis_results
			],
			hide_index=True,
			width="stretch",
		)
	with n5_tab:
		if n5_results:
			st.dataframe(
				[
					{
						"Word": result["surface"],
						"Hiragana": result["hiragana"],
						"Romaji": result["romaji"],
						"English meaning": result["meaning"],
					}
					for result in n5_results
				],
				hide_index=True,
				width="stretch",
			)
		else:
			st.info("No N5 matches found for this sentence.")
