"""Unit tests for language detection and localised error strings."""
import pytest

from app.agents.booking.language import (
    detect_language,
    agent_configuration_error,
    hotel_search_error,
    no_hotels_found,
    hotels_intro,
)


class TestDetectLanguage:
    def test_english_default(self):
        assert detect_language("I want to book a hotel in Paris") == "en"

    def test_arabic_script(self):
        assert detect_language("أريد حجز فندق في باريس") == "ar"

    def test_french_keyword(self):
        assert detect_language("Je veux réserver un hôtel") == "fr"

    def test_explicit_in_arabic(self):
        assert detect_language("Tell me in arabic please") == "ar"

    def test_explicit_in_french(self):
        assert detect_language("Répondez en français") == "fr"

    def test_explicit_in_english(self):
        # Even if message has Arabic chars, explicit request overrides
        assert detect_language("reply in english please") == "en"

    def test_empty_string_defaults_english(self):
        assert detect_language("") == "en"

    def test_none_defaults_english(self):
        assert detect_language(None) == "en"

    def test_french_bonjour(self):
        assert detect_language("Bonjour, je cherche un hôtel") == "fr"

    def test_salut_french(self):
        assert detect_language("salut je veux un voyage") == "fr"


class TestLocalisedStrings:
    def test_config_error_en(self):
        msg = agent_configuration_error("en", "Groq")
        assert "Groq" in msg
        assert "API key" in msg.lower() or "key" in msg.lower()

    def test_config_error_ar(self):
        msg = agent_configuration_error("ar", "Groq")
        assert "Groq" in msg
        assert any(c > "؀" for c in msg)  # contains Arabic

    def test_config_error_fr(self):
        msg = agent_configuration_error("fr", "Groq")
        assert "Groq" in msg
        assert "clé" in msg.lower() or "connexion" in msg.lower()

    def test_no_hotels_en(self):
        assert "hotel" in no_hotels_found("en").lower()

    def test_no_hotels_ar(self):
        msg = no_hotels_found("ar")
        assert any(c > "؀" for c in msg)

    def test_no_hotels_fr(self):
        assert "hôtel" in no_hotels_found("fr").lower()

    def test_hotels_intro_en(self):
        assert "London" in hotels_intro("London", "en")

    def test_hotels_intro_unknown_city(self):
        msg = hotels_intro(None, "en")
        assert "destination" in msg.lower()
