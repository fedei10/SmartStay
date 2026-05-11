from dataclasses import dataclass

from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import settings
from app.services.liteapi_service import LiteAPIService


@dataclass
class BookingDeps:
    llm: ChatGoogleGenerativeAI | None
    liteapi: LiteAPIService


def build_booking_deps() -> BookingDeps:
    llm = None
    if settings.GOOGLE_API_KEY:
        llm = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            api_key=settings.GOOGLE_API_KEY,
            temperature=0.2,
            max_retries=2,
        )

    return BookingDeps(
        llm=llm,
        liteapi=LiteAPIService(),
    )
