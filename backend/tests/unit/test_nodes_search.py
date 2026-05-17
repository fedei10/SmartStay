"""Unit tests for search_hotels and generate_response nodes."""
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.agents.booking.nodes import search_hotels, generate_response, _compact_hotels_from_provider
from tests.conftest import make_config

_SAMPLE_HOTELS = [
    {
        "hotel_id": "H1",
        "name": "The Grand",
        "address": "1 Main St",
        "city": "London",
        "country": "GB",
        "stars": 5,
        "rating": 9.2,
        "image_url": "https://example.com/img.jpg",
        "image_urls": [],
        "rates": [],
    }
]

_SAMPLE_RATES_RESPONSE = {
    "hotels": [
        {
            "id": "H1",
            "name": "The Grand",
            "address": "1 Main St",
            "city": "London",
            "country": "GB",
            "stars": 5,
            "rating": 9.2,
            "main_photo": "https://example.com/img.jpg",
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
                            "name": "Superior Room",
                            "boardName": "Room Only",
                            "mappedRoomId": "room-1",
                            "retailRate": {
                                "total": [{"amount": 593, "currency": "USD"}],
                                "taxesAndFees": [{"included": True}],
                            },
                            "cancellationPolicies": {
                                "refundableTag": "NON_REFUNDABLE",
                                "cancelPolicyInfos": [],
                            },
                        }
                    ],
                }
            ],
        }
    ],
}


@pytest.mark.asyncio
async def test_search_hotels_uses_availability_rates(booking_deps):
    """Hotel search should use rates so displayed hotels are available for dates."""
    booking_deps.hotels.search_rates = AsyncMock(return_value=_SAMPLE_RATES_RESPONSE)
    state = {
        "city_name": "London",
        "country_code": "GB",
        "checkin_date": "2026-07-14",
        "checkout_date": "2026-07-17",
        "guests": 2,
        "mcp_tools": ["get_data_hotels"],
        "response_language": "en",
    }
    result = await search_hotels(state, make_config("s1", booking_deps))

    assert result["next_action"] == "show_hotels"
    assert len(result["hotels"]) == 1
    assert result["hotels"][0]["name"] == "The Grand"
    assert result["hotels"][0]["rates"][0]["price"] == 593
    booking_deps.hotels.search_rates.assert_awaited_once_with({
        "aiSearch": "Hotels in London, GB",
        "occupancies": [{"adults": 2}],
        "currency": "USD",
        "guestNationality": "US",
        "checkin": "2026-07-14",
        "checkout": "2026-07-17",
        "roomMapping": True,
        "maxRatesPerHotel": 1,
        "includeHotelData": True,
    })


@pytest.mark.asyncio
async def test_search_hotels_requires_dates(booking_deps):
    booking_deps.hotels.search_rates = AsyncMock()
    state = {
        "city_name": "London",
        "country_code": "GB",
        "mcp_tools": [],
        "response_language": "en",
    }
    result = await search_hotels(state, make_config("s2", booking_deps))

    assert result["next_action"] == "ask_clarification"
    assert result["missing_fields"] == ["check-in date", "check-out date"]
    booking_deps.hotels.search_rates.assert_not_awaited()


@pytest.mark.asyncio
async def test_search_hotels_no_results(booking_deps):
    booking_deps.hotels.search_rates = AsyncMock(return_value={"data": []})
    state = {
        "city_name": "Nowhere",
        "country_code": "XX",
        "checkin_date": "2026-07-14",
        "checkout_date": "2026-07-17",
        "mcp_tools": [],
        "response_language": "en",
    }
    result = await search_hotels(state, make_config("s3", booking_deps))

    assert result["next_action"] == "error"
    assert result.get("response")


@pytest.mark.asyncio
async def test_search_hotels_api_exception(booking_deps):
    booking_deps.hotels.search_rates = AsyncMock(side_effect=RuntimeError("Timeout"))
    state = {
        "city_name": "London",
        "country_code": "GB",
        "checkin_date": "2026-07-14",
        "checkout_date": "2026-07-17",
        "mcp_tools": [],
        "response_language": "en",
    }
    result = await search_hotels(state, make_config("s4", booking_deps))

    assert result["next_action"] == "error"
    assert "Timeout" in result.get("error_message", "")


@pytest.mark.asyncio
async def test_generate_response_formats_list():
    state = {
        "hotels": _SAMPLE_HOTELS,
        "city_name": "London",
        "response_language": "en",
    }
    result = await generate_response(state)

    assert result["next_action"] == "show_hotels"
    assert "The Grand" in result["response"]
    assert "5 stars" in result["response"]
    assert "9.2" in result["response"]
    assert "1." in result["response"]


@pytest.mark.asyncio
async def test_generate_response_empty_hotels():
    state = {"hotels": [], "city_name": "London", "response_language": "en"}
    result = await generate_response(state)
    assert result["next_action"] == "show_hotels"
    assert result["response"]


class TestCompactHotelsFromProvider:
    def test_parses_hotels_key(self):
        data = {"hotels": [{"hotelId": "H1", "name": "Ritz", "stars": 5}]}
        hotels = _compact_hotels_from_provider(data)
        assert hotels[0]["hotel_id"] == "H1"
        assert hotels[0]["stars"] == 5

    def test_parses_data_key(self):
        data = {"data": [{"hotelId": "H2", "name": "Hilton"}]}
        hotels = _compact_hotels_from_provider(data)
        assert hotels[0]["hotel_id"] == "H2"

    def test_parses_json_string(self):
        import json
        data = json.dumps({"hotels": [{"hotelId": "H3", "name": "Ibis"}]})
        hotels = _compact_hotels_from_provider(data)
        assert hotels[0]["name"] == "Ibis"

    def test_mcp_text_envelope(self):
        """MCP returns [{type: text, text: json_string}] list."""
        import json
        payload = [{"type": "text", "text": json.dumps({"hotels": [{"hotelId": "H4", "name": "Novotel"}]})}]
        hotels = _compact_hotels_from_provider(payload)
        assert hotels[0]["name"] == "Novotel"

    def test_invalid_input_returns_empty(self):
        assert _compact_hotels_from_provider("not json {{{") == []

    def test_empty_hotels_list(self):
        assert _compact_hotels_from_provider({"hotels": []}) == []
