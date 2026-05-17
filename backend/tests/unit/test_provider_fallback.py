from app.agents.booking import dependencies
from app.agents.booking.language import provider_runtime_error


def test_provider_runtime_error_handles_quota_message():
    message = provider_runtime_error(
        "en",
        "gemini",
        "429 RESOURCE_EXHAUSTED: quota exceeded for requests",
    )

    assert "quota or rate limit" in message
    assert "invalid" not in message.lower()


def test_build_llm_prefers_swiftrouter_over_gemini(monkeypatch):
    calls: list[tuple[str, dict]] = []

    def fake_init_chat_model(model: str, **kwargs):
        calls.append((model, kwargs))
        return object()

    monkeypatch.setattr(dependencies, "init_chat_model", fake_init_chat_model)
    monkeypatch.setattr(dependencies.settings, "SWIFTROUTER_API_KEY", "swift-key")
    monkeypatch.setattr(dependencies.settings, "GOOGLE_API_KEY", "google-key")
    monkeypatch.setattr(dependencies.settings, "SWIFTROUTER_MODEL", "kimi-k2.5")
    monkeypatch.setattr(dependencies.settings, "SWIFTROUTER_BASE_URL", "https://api.swiftrouter.com/v1")

    llm, provider = dependencies._build_llm()

    assert llm is not None
    assert provider == "swiftrouter"
    assert calls[0][0] == "openai:kimi-k2.5"
