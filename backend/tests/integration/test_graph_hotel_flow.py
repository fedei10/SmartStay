"""Integration tests: end-to-end hotel booking flow through the compiled graph.

Uses MemorySaver + mocked LLM/services so no real network calls are made.
Tests follow the pattern from docs/test.md.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from langgraph.checkpoint.memory import MemorySaver

from app.agents.booking.graph import build_booking_graph
from app.agents.booking.schemas import TravelOrchestratorDecision
from tests.conftest import make_config, make_structured_llm_mock


_HOTELS = [
    {
        "hotel_id": "H1",
        "name": "The Ritz London",
        "city": "London",
        "country": "GB",
        "stars": 5,
        "rating": 9.5,
        "image_url": None,
        "image_urls": [],
        "rates": [],
    }
]

_RATES_RESPONSE = {
    "hotels": [
        {
            "id": "H1",
            "name": "The Ritz London",
            "city": "London",
            "country": "GB",
            "stars": 5,
            "rating": 9.5,
        }
    ],
    "data": [
        {
            "hotelId": "H1",
            "roomTypes": [
                {
                    "offerId": "offer-1",
                    "rates": [
                        {
                            "name": "Classic Room",
                            "boardName": "Room Only",
                            "retailRate": {"total": [{"amount": 500, "currency": "USD"}]},
                            "cancellationPolicies": {"refundableTag": "NON_REFUNDABLE"},
                        }
                    ],
                }
            ],
        }
    ],
}


def _hotel_orchestrator_decision(**overrides):
    defaults = dict(
        intent="hotel_search",
        agent="hotel_booking_agent",
        city_name="London",
        country_code="GB",
        checkin_date="2026-07-14",
        checkout_date="2026-07-17",
        guests=None,
        response_language="en",
        requested_services=["hotels"],
    )
    defaults.update(overrides)
    return TravelOrchestratorDecision(**defaults)


@pytest.fixture
def hotel_graph(booking_deps):
    """Graph whose LLM returns a hotel_booking_agent decision."""
    booking_deps.llm = make_structured_llm_mock(_hotel_orchestrator_decision())
    booking_deps.hotels.search_rates = AsyncMock(return_value=_RATES_RESPONSE)
    booking_deps.liteapi_tools.ainvoke = AsyncMock(return_value={"hotels": _HOTELS})
    checkpointer = MemorySaver()
    return build_booking_graph(checkpointer=checkpointer), booking_deps


@pytest.mark.asyncio
async def test_hotel_search_complete_flow(hotel_graph):
    """Full path: orchestrate → hotel_agent → search_hotels → generate_response."""
    graph, deps = hotel_graph
    config = make_config("hotel-e2e-1", deps)

    result = await graph.ainvoke(
        {"user_message": "Book me a hotel in London", "messages": []},
        config=config,
    )

    assert result["next_action"] == "show_hotels"
    assert result["agent"] == "hotel_booking_agent"
    assert len(result["hotels"]) == 1
    assert result["hotels"][0]["name"] == "The Ritz London"
    assert "The Ritz London" in result["response"]


@pytest.mark.asyncio
async def test_hotel_search_missing_city_asks_clarification(booking_deps):
    """When orchestrator extracts no city, hotel_agent should ask for it."""
    booking_deps.llm = make_structured_llm_mock(
        _hotel_orchestrator_decision(city_name=None, country_code=None)
    )
    graph = build_booking_graph(checkpointer=MemorySaver())
    config = make_config("hotel-e2e-2", booking_deps)

    result = await graph.ainvoke(
        {"user_message": "I need a hotel", "messages": []},
        config=config,
    )

    assert result["next_action"] == "ask_clarification"
    assert result["agent"] == "hotel_booking_agent"
    assert result.get("response")


@pytest.mark.asyncio
async def test_hotel_search_api_error_returns_error_state(booking_deps):
    """When LiteAPI raises, result should contain an error response."""
    booking_deps.llm = make_structured_llm_mock(_hotel_orchestrator_decision())
    booking_deps.hotels.search_rates = AsyncMock(side_effect=RuntimeError("API down"))
    booking_deps.liteapi_tools.ainvoke = AsyncMock(side_effect=RuntimeError("API down"))
    graph = build_booking_graph(checkpointer=MemorySaver())
    config = make_config("hotel-e2e-3", booking_deps)

    result = await graph.ainvoke(
        {"user_message": "Hotel in London", "messages": []},
        config=config,
    )

    assert result["next_action"] == "error"
    assert result.get("response")


@pytest.mark.asyncio
async def test_hotel_individual_search_node(booking_deps):
    """Test search_hotels node in isolation via graph.nodes API (from test.md)."""
    booking_deps.hotels.search_rates = AsyncMock(return_value=_RATES_RESPONSE)
    graph = build_booking_graph(checkpointer=MemorySaver())
    config = make_config("hotel-node-1", booking_deps)

    # All our nodes are async — use ainvoke, not invoke.
    result = await graph.nodes["search_hotels"].ainvoke(
        {
            "city_name": "London",
            "country_code": "GB",
            "checkin_date": "2026-07-14",
            "checkout_date": "2026-07-17",
            "mcp_tools": [],
            "response_language": "en",
        },
        config=config,
    )

    assert result["next_action"] == "show_hotels"
    assert result["hotels"][0]["name"] == "The Ritz London"


@pytest.mark.asyncio
async def test_hotel_partial_execution_from_hotel_agent(booking_deps):
    """Use update_state to inject hotel_agent output, then run search+respond only.

    Demonstrates the partial execution pattern from test.md:
    Skip orchestrator, start from search_hotels, stop after generate_response.
    """
    booking_deps.hotels.search_rates = AsyncMock(return_value=_RATES_RESPONSE)
    booking_deps.liteapi_tools.ainvoke = AsyncMock(return_value={"hotels": _HOTELS})
    checkpointer = MemorySaver()
    graph = build_booking_graph(checkpointer=checkpointer)
    config = make_config("hotel-partial-1", booking_deps)

    # Simulate hotel_agent having already validated and set next_action=search_hotels
    graph.update_state(
        config=config,
        values={
            "city_name": "London",
            "country_code": "GB",
            "checkin_date": "2026-07-14",
            "checkout_date": "2026-07-17",
            "mcp_tools": [],
            "next_action": "search_hotels",
            "agent": "hotel_booking_agent",
            "response_language": "en",
            "messages": [],
        },
        as_node="hotel_agent",
    )

    result = await graph.ainvoke(None, config=config)

    assert result["next_action"] == "show_hotels"
    assert "The Ritz London" in result["response"]
