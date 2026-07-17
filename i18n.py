# core/i18n.py
#
# Just the language list used by Wayfinder / AccessAI. Picked these based on
# the languages most likely to show up across the US/Mexico/Canada host
# nations for 2026 — not exhaustive, easy to extend if needed.

SUPPORTED_LANGUAGES = {
    "English": "en",
    "Spanish": "es",
    "French": "fr",
    "Portuguese": "pt",
    "Hindi": "hi",
    "Arabic": "ar",
    "Mandarin Chinese": "zh",
    "German": "de",
    "Japanese": "ja",
    "Korean": "ko",
}


def language_instruction(language_name: str) -> str:
    """Small helper to build a clear instruction for the LLM system prompt."""
    if language_name == "English":
        return "Respond in clear, natural English."
    return (
        f"Respond entirely in {language_name}, using natural, fluent, "
        f"conversational phrasing a native speaker would actually use — "
        f"not a literal word-for-word translation."
    )
