"""Integration tests: multi-turn conversations and state persistence.

Key scenarios:
- State fields survive across graph invocations (same thread_id)
- _keep() prevents overwriting confirmed city/date when LLM returns None
- Each new turn correctly merges new data onto prior state
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, call
from langgraph.checkpoint.memory import MemorySaver

from app.agents.booking.graph import build_booking_graph
from app.agents.booking.schemas import TravelOrchestratorDecision
from tests.conftest import make_config, make_structured_llm_mock


def _decision(**overrides):
    defaults = dict(
        intent="hotel_search",
        agent="hotel_booking_agent",
        city_name=None,
        country_code=None,
        checkin_date=None,
        checkout_date=None,
        guests=None,
        response_language="en",
        requested_services=["hotels"],
    )
    defaults.update(overrides)
    return TravelOrchestratorDecision(**defaults)


@pytest.mark.asyncio
async def test_city_persists_across_turns(booking_deps):
    """Turn 1 provides city; Turn 2 should NOT overwrite it with None.

    This is the core regression test for the _keep() bug — the LLM on Turn 2
    returning city_name=None must NOT wipe the confirmed city from Turn 1.
    """
    checkpointer = MemorySaver()
    graph = build_booking_graph(checkpointer=checkpointer)
    config = make_config("multi-1", booking_deps)

    # Turn 1: LLM extracts city London from "I want a hotel in London"
    booking_deps.llm = make_structured_llm_mock(
        _decision(city_name="London", country_code="GB")
    )
    booking_deps.liteapi.search_hotels_by_city = AsyncMock(
        return_value={"hotels": [{"hotel_id": "H1", "name": "Hilton", "city": "London",
                                  "country": "GB", "stars": 4, "rating": 8.0,
                                  "image_url": None, "image_urls": [], "rates": []}]}
    )
    booking_deps.liteapi_tools.ainvoke = AsyncMock(return_value={"hotels": []})

    result1 = await graph.ainvoke(
        {"user_message": "I want a hotel in London", "messages": []},
        config=config,
    )
    assert result1["city_name"] == "London"
    assert result1["country_code"] == "GB"

    # Turn 2: LLM returns city_name=None (simulating short follow-up "next weekend")
    booking_deps.llm = make_structured_llm_mock(
        _decision(city_name=None, country_code=None, checkin_date="2025-06-21")
    )

    result2 = await graph.ainvoke(
        {"user_message": "next weekend", "messages": []},
        config=config,
    )

    # City must NOT have been wiped by the second LLM call returning None.
    assert result2["city_name"] == "London", (
        "city_name was overwritten with None — _keep() merge is broken"
    )
    assert result2["country_code"] == "GB"


@pytest.mark.asyncio
async def test_checkin_date_extracted_on_followup(booking_deps):
    """User provides dates in a follow-up; they should be stored and used."""
    checkpointer = MemorySaver()
    graph = build_booking_graph(checkpointer=checkpointer)
    config = make_config("multi-2", booking_deps)

    # Turn 1 — city only
    booking_deps.llm = make_structured_llm_mock(
        _decision(city_name="Paris", country_code="FR")
    )
    booking_deps.liteapi.search_hotels_by_city = AsyncMock(return_value={"hotels": []})
    await graph.ainvoke({"user_message": "hotel in Paris", "messages": []}, config=config)

    # Turn 2 — dates added
    booking_deps.llm = make_structured_llm_mock(
        _decision(
            city_name="Paris",
            country_code="FR",
            checkin_date="2025-07-14",
            checkout_date="2025-07-17",
        )
    )
    result2 = await graph.ainvoke(
        {"user_message": "14 to 17 July", "messages": []},
        config=config,
    )

    assert result2["checkin_date"] == "2025-07-14"
    assert result2["checkout_date"] == "2025-07-17"
    assert result2["city_name"] == "Paris"


@pytest.mark.asyncio
async def test_different_threads_are_isolated(booking_deps):
    """Two different conversation IDs should not share state."""
    checkpointer = MemorySaver()
    graph = build_booking_graph(checkpointer=checkpointer)

    booking_deps.llm = make_structured_llm_mock(
        _decision(city_name="London", country_code="GB")
    )
    booking_deps.liteapi.search_hotels_by_city = AsyncMock(return_value={"hotels": []})

    config_a = make_config("thread-A", booking_deps)
    config_b = make_config("thread-B", booking_deps)

    # Thread A: city = London
    await graph.ainvoke({"user_message": "hotel in London", "messages": []}, config=config_a)

    # Thread B: city = Paris
    booking_deps.llm = make_structured_llm_mock(
        _decision(city_name="Paris", country_code="FR")
    )
    result_b = await graph.ainvoke(
        {"user_message": "hotel in Paris", "messages": []}, config=config_b
    )

    # Thread B should NOT see London (Thread A's state)
    assert result_b["city_name"] == "Paris"

    # Now go back to Thread A — it should still have London
    booking_deps.llm = make_structured_llm_mock(
        _decision(city_name=None, country_code=None)
    )
    result_a2 = await graph.ainvoke(
        {"user_message": "what were the options?", "messages": []}, config=config_a
    )
    assert result_a2["city_name"] == "London", "Thread A state leaked to Thread B or was lost"


@pytest.mark.asyncio
async def test_guests_extracted_midconversation(booking_deps):
    """Guests provided in Turn 2 should merge into existing state."""
    checkpointer = MemorySaver()
    graph = build_booking_graph(checkpointer=checkpointer)
    config = make_config("multi-3", booking_deps)

    booking_deps.liteapi.search_hotels_by_city = AsyncMock(return_value={"hotels": []})

    # Turn 1: city only
    booking_deps.llm = make_structured_llm_mock(
        _decision(city_name="Rome", country_code="IT")
    )
    await graph.ainvoke({"user_message": "hotel in Rome", "messages": []}, config=config)

    # Turn 2: add guests
    booking_deps.llm = make_structured_llm_mock(
        _decision(city_name="Rome", country_code="IT", guests=2)
    )
    result = await graph.ainvoke(
        {"user_message": "for 2 people", "messages": []},
        config=config,
    )

    assert result["guests"] == 2
    assert result["city_name"] == "Rome"
