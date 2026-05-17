from dataclasses import dataclass

from langchain_core.language_models.chat_models import BaseChatModel

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:  # pragma: no cover - dependency is declared in requirements.
    ChatGoogleGenerativeAI = None

try:
    from langchain_groq import ChatGroq
except ImportError:  # pragma: no cover - dependency is declared in requirements.
    ChatGroq = None

from app.core.config import settings
from app.coreAgents.tools.liteapi import LiteAPIMCPToolProvider
from app.services.elasticsearch.retrieval import OrchestrationRetriever
from app.services.liteapi_flights_service import LiteAPIFlightsService
from app.services.liteapi_hotels_service import LiteAPIHotelsService
from app.services.liteapi_service import LiteAPIService
from app.services.redis.memory import ConversationMemory


@dataclass
class BookingDeps:
    llm: BaseChatModel | None
    llm_provider: str | None
    liteapi_tools: LiteAPIMCPToolProvider
    liteapi: LiteAPIService
    hotels: LiteAPIHotelsService
    flights: LiteAPIFlightsService
    conversation_memory: ConversationMemory
    retriever: OrchestrationRetriever


def build_booking_deps() -> BookingDeps:
    llm = None
    llm_provider = None
    google_api_key = (settings.GOOGLE_API_KEY or "").strip()
    groq_api_key = (settings.GROQ_API_KEY or "").strip()

    if groq_api_key:
        if ChatGroq is None:
            raise RuntimeError("langchain-groq is required when GROQ_API_KEY is configured")
        llm = ChatGroq(
            model=settings.GROQ_MODEL,
            api_key=groq_api_key,
            temperature=0.2,
            max_retries=2,
        )
        llm_provider = "groq"
    elif google_api_key:
        if ChatGoogleGenerativeAI is None:
            raise RuntimeError("langchain-google-genai is required when GOOGLE_API_KEY is configured")
        llm = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            api_key=google_api_key,
            temperature=0.2,
            max_retries=2,
        )
        llm_provider = "gemini"

    liteapi = LiteAPIService()
    return BookingDeps(
        llm=llm,
        llm_provider=llm_provider,
        liteapi_tools=LiteAPIMCPToolProvider(),
        liteapi=liteapi,
        hotels=LiteAPIHotelsService(liteapi),
        flights=LiteAPIFlightsService(liteapi),
        conversation_memory=ConversationMemory(),
        retriever=OrchestrationRetriever(),
    )
