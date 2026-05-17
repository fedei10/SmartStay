from dataclasses import dataclass

from langchain.chat_models import init_chat_model
from langchain_core.language_models.chat_models import BaseChatModel

from app.core.config import settings
from app.coreAgents.tools.liteapi import LiteAPIMCPToolProvider
from app.services.elasticsearch.retrieval import OrchestrationRetriever
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
    conversation_memory: ConversationMemory
    retriever: OrchestrationRetriever


def _build_llm() -> tuple[BaseChatModel | None, str | None]:
    """Return (llm, provider_name).

    Priority: SwiftRouter (OpenAI-compatible) → Gemini (Google AI).
    Uses init_chat_model so the model string is the single source of truth.
    """
    # ── 1. SwiftRouter (OpenAI-compatible) ───────────────────────────────────
    swift_key = (settings.SWIFTROUTER_API_KEY or "").strip()
    if swift_key:
        llm = init_chat_model(
            f"openai:{settings.SWIFTROUTER_MODEL}",
            openai_api_key=swift_key,
            openai_api_base=settings.SWIFTROUTER_BASE_URL,
            temperature=0.2,
            max_retries=1,
        )
        return llm, "swiftrouter"

    # ── 2. Gemini ─────────────────────────────────────────────────────────────
    google_key = (settings.GOOGLE_API_KEY or "").strip()
    if google_key:
        llm = init_chat_model(
            f"google_genai:{settings.GEMINI_MODEL}",
            google_api_key=google_key,
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
        conversation_memory=ConversationMemory(),
        retriever=OrchestrationRetriever(),
    )
