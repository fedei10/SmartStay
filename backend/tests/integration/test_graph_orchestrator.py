"""Integration tests: orchestrator routing decisions.

Each test verifies that the right sub-agent is activated for a given user intent.
"""
import pytest
from unittest.mock import AsyncMock
from langgraph.checkpoint.memory import MemorySaver

from app.agents.booking.graph import build_booking_graph
from app.agents.booking.schemas import TravelOrchestratorDecision
from tests.conftest import make_config, make_structured_llm_mock


def _decision(**overrides):
    defaults = dict(
        intent="general_travel_question",
        agent="general_travel_assistant",
        city_name=None, country_code=None,
        checkin_date=None, checkout_date=None,
        guests=None,
        response_language="en",
        requested_services=[],
    )
    defaults.update(overrides)
    return TravelOrchestratorDecision(**defaults)


@pytest.mark.asyncio
async def test_general_message_routes_to_general_agent(booking_deps):
    booking_deps.llm = make_structured_llm_mock(_decision())
    graph = build_booking_graph(checkpointer=MemorySaver())

    result = await graph.ainvoke(
        {"user_message": "hello!", "messages": []},
        config=make_config("orch-1", booking_deps),
    )

    assert result["agent"] == "general_travel_assistant"
    assert result["next_action"] == "answer_general"
    assert result.get("response")


@pytest.mark.asyncio
async def test_hotel_intent_routes_to_hotel_agent(booking_deps):
    booking_deps.llm = make_structured_llm_mock(
        _decision(intent="hotel_search", agent="hotel_booking_agent",
                  city_name="Madrid", country_code="ES", requested_services=["hotels"])
    )
    booking_deps.liteapi.search_hotels_by_city = AsyncMock(return_value={"hotels": []})
    graph = build_booking_graph(checkpointer=MemorySaver())

    result = await graph.ainvoke(
        {"user_message": "Hotels in Madrid", "messages": []},
        config=make_config("orch-2", booking_deps),
    )

    assert result["agent"] == "hotel_booking_agent"


@pytest.mark.asyncio
async def test_no_llm_returns_error_response(booking_deps):
    """When no LLM is configured the graph should return an error, not crash."""
    booking_deps.llm = None
    graph = build_booking_graph(checkpointer=MemorySaver())

    result = await graph.ainvoke(
        {"user_message": "hello", "messages": []},
        config=make_config("orch-no-llm", booking_deps),
    )

    assert result.get("next_action") == "error"
    assert result.get("response")


@pytest.mark.asyncio
async def test_llm_exception_returns_error_response(booking_deps):
    """When structured LLM raises, graph returns error without crashing."""
    router_mock = booking_deps.llm.with_structured_output.return_value
    router_mock.ainvoke = AsyncMock(side_effect=RuntimeError("Rate limit"))
    graph = build_booking_graph(checkpointer=MemorySaver())

    result = await graph.ainvoke(
        {"user_message": "book hotel London", "messages": []},
        config=make_config("orch-exc", booking_deps),
    )

    assert result.get("next_action") == "error"
    assert result.get("response")


@pytest.mark.asyncio
async def test_insurance_intent_routes_to_insurance_agent(booking_deps):
    booking_deps.llm = make_structured_llm_mock(
        _decision(intent="insurance", agent="insurance_management_agent",
                  requested_services=["insurance"])
    )
    graph = build_booking_graph(checkpointer=MemorySaver())

    result = await graph.ainvoke(
        {"user_message": "I need travel insurance", "messages": []},
        config=make_config("orch-ins", booking_deps),
    )

    assert result["agent"] == "insurance_management_agent"


@pytest.mark.asyncio
async def test_combined_trip_routes_to_package_agent(booking_deps):
    booking_deps.llm = make_structured_llm_mock(
        _decision(
            intent="combined_trip", agent="travel_booking_agent",
            city_name="Barcelona", country_code="ES",
            requested_services=["hotels"],
        )
    )
    graph = build_booking_graph(checkpointer=MemorySaver())

    result = await graph.ainvoke(
        {"user_message": "hotel stay in Barcelona", "messages": []},
        config=make_config("orch-pkg", booking_deps),
    )

    assert result["agent"] == "travel_booking_agent"


@pytest.mark.asyncio
async def test_response_language_detected_from_message(booking_deps):
    """Orchestrator should pass through response_language from the LLM decision."""
    booking_deps.llm = make_structured_llm_mock(
        _decision(response_language="fr")
    )
    graph = build_booking_graph(checkpointer=MemorySaver())

    result = await graph.ainvoke(
        {"user_message": "Bonjour", "messages": []},
        config=make_config("orch-lang", booking_deps),
    )

    assert result.get("response_language") == "fr"
