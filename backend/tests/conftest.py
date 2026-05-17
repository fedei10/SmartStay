"""Shared fixtures for all test suites."""
import pytest
from dataclasses import dataclass
from unittest.mock import AsyncMock, MagicMock

from langgraph.checkpoint.memory import MemorySaver

from app.agents.booking.dependencies import BookingDeps
from app.agents.booking.graph import build_booking_graph


# ── LLM mock helpers ─────────────────────────────────────────────────────────

def make_llm_mock(reply: str = "How can I help you?"):
    """Return an async LLM mock that returns a fixed text reply."""
    msg = MagicMock()
    msg.content = reply
    llm = MagicMock()
    llm.ainvoke = AsyncMock(return_value=msg)
    llm.with_structured_output = MagicMock(return_value=llm)
    return llm


def make_structured_llm_mock(structured_output):
    """Return an LLM mock whose .ainvoke() returns a Pydantic model instance."""
    llm = MagicMock()
    router = MagicMock()
    router.ainvoke = AsyncMock(return_value=structured_output)
    llm.with_structured_output = MagicMock(return_value=router)
    llm.ainvoke = AsyncMock(return_value=MagicMock(content="ok"))
    return llm


# ── Dependency fixtures ───────────────────────────────────────────────────────

@pytest.fixture
def memory_mock():
    m = MagicMock()
    m.get_recent = AsyncMock(return_value=[])
    m.get_booking_state = AsyncMock(return_value={})
    m.set_booking_state = AsyncMock()
    m.append_interaction = AsyncMock()
    return m


@pytest.fixture
def hotels_mock():
    m = MagicMock()
    m.search = AsyncMock(return_value={"hotels": []})
    m.book = AsyncMock(return_value={"data": {"bookingId": "BK001", "hotelConfirmationCode": "CONF001"}})
    return m


@pytest.fixture
def liteapi_tools_mock():
    m = MagicMock()
    m.get_tool_names = AsyncMock(return_value=["get_data_hotels"])
    m.ainvoke = AsyncMock(return_value={"hotels": []})
    return m


@pytest.fixture
def retriever_mock():
    m = MagicMock()
    m.search = AsyncMock(return_value=[])
    return m


@pytest.fixture
def booking_deps(memory_mock, hotels_mock, liteapi_tools_mock, retriever_mock):
    """Minimal BookingDeps with all external services mocked out."""
    return BookingDeps(
        llm=make_llm_mock(),
        llm_provider="mock",
        liteapi_tools=liteapi_tools_mock,
        liteapi=MagicMock(),
        hotels=hotels_mock,
        conversation_memory=memory_mock,
        retriever=retriever_mock,
    )


@pytest.fixture
def compiled_graph(booking_deps):
    """Compiled booking graph with an in-memory checkpointer, ready for testing."""
    checkpointer = MemorySaver()
    graph = build_booking_graph(checkpointer=checkpointer)
    return graph


def make_config(conversation_id: str = "test-conv-1", deps=None):
    """Build the LangGraph config dict the way chat.py does."""
    return {
        "configurable": {
            "thread_id": f"conversation:{conversation_id}",
            "conversation_id": conversation_id,
            "deps": deps,
        }
    }
