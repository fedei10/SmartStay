"""Unit tests for hotel_agent_node — invoked directly, bypassing checkpointer."""
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.agents.booking.nodes import (
    hotel_agent_node,
    hotel_selection_node,
    search_hotel_rates_node,
)
from tests.conftest import make_config, make_llm_mock


def _make_config(deps):
    return make_config("test-hotel-1", deps)


@pytest.mark.asyncio
async def test_hotel_agent_asks_for_city_when_missing(booking_deps):
    """When city_name is missing, node should ask for it."""
    state = {"user_message": "I want to book a hotel", "response_language": "en"}
    result = await hotel_agent_node(state, _make_config(booking_deps))

    assert result["next_action"] == "ask_clarification"
    assert result["agent"] == "hotel_booking_agent"
    assert result.get("response")  # some text was generated


@pytest.mark.asyncio
async def test_hotel_agent_asks_for_country_when_city_known(booking_deps):
    """When city is known but country missing, still asks for missing field."""
    state = {
        "user_message": "London",
        "city_name": "London",
        "country_code": None,
        "response_language": "en",
    }
    result = await hotel_agent_node(state, _make_config(booking_deps))

    assert result["next_action"] == "ask_clarification"
    assert result["agent"] == "hotel_booking_agent"


@pytest.mark.asyncio
async def test_hotel_agent_routes_to_search_when_complete(booking_deps):
    """When destination and dates are present, node should return search_hotels."""
    state = {
        "user_message": "book me a hotel",
        "city_name": "London",
        "country_code": "GB",
        "checkin_date": "2026-07-14",
        "checkout_date": "2026-07-17",
        "response_language": "en",
    }
    result = await hotel_agent_node(state, _make_config(booking_deps))

    assert result["next_action"] == "search_hotels"
    assert result["agent"] == "hotel_booking_agent"
    assert "response" not in result or result.get("response") is None


@pytest.mark.asyncio
async def test_hotel_agent_asks_for_dates_before_search(booking_deps):
    state = {
        "user_message": "book me a hotel in London",
        "city_name": "London",
        "country_code": "GB",
        "response_language": "en",
    }
    result = await hotel_agent_node(state, _make_config(booking_deps))

    assert result["next_action"] == "ask_clarification"
    assert result["agent"] == "hotel_booking_agent"
    assert result.get("response")


@pytest.mark.asyncio
async def test_hotel_agent_routes_selected_hotel_to_rate_search_when_dates_known(booking_deps):
    state = {
        "user_message": "14 to 17 July",
        "city_name": "Paris",
        "country_code": "FR",
        "selected_hotel_id": "hotel-1",
        "checkin_date": "2026-07-14",
        "checkout_date": "2026-07-17",
        "response_language": "en",
    }
    result = await hotel_agent_node(state, _make_config(booking_deps))

    assert result["next_action"] == "search_hotel_rates"
    assert result["agent"] == "hotel_booking_agent"


@pytest.mark.asyncio
async def test_hotel_selection_asks_for_dates_before_room_rates(booking_deps):
    state = {
        "user_message": "1",
        "hotels": [{"hotel_id": "hotel-1", "name": "Mercure Toulouse"}],
        "selected_item_index": 1,
        "response_language": "en",
    }
    result = await hotel_selection_node(state, _make_config(booking_deps))

    assert result["next_action"] == "ask_clarification"
    assert result["selected_hotel_id"] == "hotel-1"
    assert result["missing_fields"] == ["check-in date", "check-out date"]
    assert result.get("response")


@pytest.mark.asyncio
async def test_hotel_selection_fetches_full_rates_after_hotel_pick(booking_deps):
    rates = [{"offer_id": "offer-1", "name": "Superior Room", "price": 593}]
    state = {
        "user_message": "1",
        "hotels": [{"hotel_id": "hotel-1", "name": "Mercure Toulouse", "rates": rates}],
        "selected_item_index": 1,
        "checkin_date": "2026-05-19",
        "checkout_date": "2026-05-21",
        "response_language": "en",
    }
    result = await hotel_selection_node(state, _make_config(booking_deps))

    assert result["next_action"] == "search_hotel_rates"
    assert result["selected_hotel_id"] == "hotel-1"
    assert result["hotel_rates"] == rates


@pytest.mark.asyncio
async def test_search_hotel_rates_requires_dates_without_defaulting(booking_deps):
    booking_deps.hotels.search_rates = AsyncMock()
    state = {
        "user_message": "show rooms",
        "selected_hotel_id": "hotel-1",
        "response_language": "en",
    }
    result = await search_hotel_rates_node(state, _make_config(booking_deps))

    assert result["next_action"] == "ask_clarification"
    assert result["missing_fields"] == ["check-in date", "check-out date"]
    booking_deps.hotels.search_rates.assert_not_awaited()


@pytest.mark.asyncio
async def test_search_hotel_rates_falls_back_to_existing_hotel_rates(booking_deps):
    booking_deps.hotels.search_rates = AsyncMock(return_value={"data": [{"hotelId": "hotel-1", "roomTypes": []}]})
    rates = [{"offer_id": "offer-1", "name": "Superior Room", "price": 593}]
    state = {
        "user_message": "show rooms",
        "selected_hotel_id": "hotel-1",
        "hotels": [{"hotel_id": "hotel-1", "name": "Mercure Toulouse", "rates": rates}],
        "checkin_date": "2026-05-19",
        "checkout_date": "2026-05-21",
        "response_language": "en",
    }
    result = await search_hotel_rates_node(state, _make_config(booking_deps))

    assert result["next_action"] == "show_hotel_rates"
    assert result["hotel_rates"] == rates


@pytest.mark.asyncio
async def test_hotel_agent_no_llm_returns_error(booking_deps):
    """When no LLM is configured, error state is returned."""
    booking_deps.llm = None
    state = {
        "user_message": "book hotel",
        "city_name": None,
        "country_code": None,
        "response_language": "en",
    }
    result = await hotel_agent_node(state, _make_config(booking_deps))

    assert result["next_action"] == "error"
    assert result.get("response")


@pytest.mark.asyncio
async def test_hotel_agent_llm_exception_returns_error(booking_deps):
    """When LLM raises, node should gracefully return error state."""
    booking_deps.llm.ainvoke = AsyncMock(side_effect=RuntimeError("LLM down"))
    state = {
        "user_message": "hotel please",
        "city_name": None,
        "response_language": "en",
    }
    result = await hotel_agent_node(state, _make_config(booking_deps))

    assert result["next_action"] == "error"
