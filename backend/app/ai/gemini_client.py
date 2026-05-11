from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import settings


def get_llm() -> ChatGoogleGenerativeAI:
    if not settings.GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY or GEMINI_API_KEY is not configured")

    return ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL,
        api_key=settings.GOOGLE_API_KEY,
        temperature=0.2,
        max_retries=2,
    )
