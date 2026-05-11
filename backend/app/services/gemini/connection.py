from app.core.config import settings


def test_gemini_connection():
    if not settings.GOOGLE_API_KEY:
        return {
            "status": "error",
            "message": "GOOGLE_API_KEY or GEMINI_API_KEY is not configured",
        }

    return {
        "status": "ok",
        "message": "Gemini API key is configured",
        "model": settings.GEMINI_MODEL,
    }
