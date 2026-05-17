from dataclasses import dataclass

from langchain_core.language_models.chat_models import BaseChatModel

try:
    from langchain_openai import ChatOpenAI
except ImportError:
    ChatOpenAI = None

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    ChatGoogleGenerativeAI = None

try:
    from langchain_groq import ChatGroq
except ImportError:
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


def _build_llm() -> tuple[BaseChatModel | None, str | None]:
    """Return (llm, provider_name) following the priority chain:
    SwiftRouter → Groq → Gemini → None.
    """
    # ── 1. SwiftRouter (OpenAI-compatible) ──────────────────────────────────
    swift_key = (settings.SWIFTROUTER_API_KEY or "").strip()
    if swift_key:
        if ChatOpenAI is None:
            raise RuntimeError("langchain-openai is required when SWIFTROUTER_API_KEY is set")
        llm = ChatOpenAI(
            model=settings.SWIFTROUTER_MODEL,
            api_key=swift_key,
            base_url=settings.SWIFTROUTER_BASE_URL,
            temperature=0.2,
            max_retries=1,
        )
        return llm, "swiftrouter"

    # ── 2. Groq ──────────────────────────────────────────────────────────────
    groq_key = (settings.GROQ_API_KEY or "").strip()
    if groq_key:
        if ChatGroq is None:
            raise RuntimeError("langchain-groq is required when GROQ_API_KEY is set")
        llm = ChatGroq(
            model=settings.GROQ_MODEL,
            api_key=groq_key,
            temperature=0.2,
            max_retries=1,
        )
        return llm, "groq"

    # ── 3. Gemini ────────────────────────────────────────────────────────────
    google_key = (settings.GOOGLE_API_KEY or "").strip()
    if google_key:
        if ChatGoogleGenerativeAI is None:
            raise RuntimeError("langchain-google-genai is required when GOOGLE_API_KEY is set")
        llm = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            api_key=google_key,
            temperature=0.2,
            max_retries=2,
        )
        return llm, "gemini"

    return None, None


def build_booking_deps() -> BookingDeps:
    llm, llm_provider = _build_llm()

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
