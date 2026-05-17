import pytest
from unittest.mock import AsyncMock, MagicMock

from app.api.V1.chat import _persist_conversation_booking_memory
from app.schemas.chat import ChatRequest
from app.services.redis.memory import ConversationMemory


def test_chat_request_accepts_user_profile_payload():
    payload = ChatRequest(
        conversation_id="conv-1",
        message="hello",
        user_id="user_123",
        user_profile={
            "first_name": "Fedi",
            "last_name": "Bellakhel",
            "email": "fedi@example.com",
        },
    )

    assert payload.user_id == "user_123"
    assert payload.user_profile is not None
    assert payload.user_profile["first_name"] == "Fedi"


def test_sanitize_user_profile_removes_empty_and_unknown_fields():
    profile = ConversationMemory.sanitize_user_profile(
        {
            "user_id": "user_123",
            "first_name": "Fedi",
            "last_name": "",
            "email": "fedi@example.com",
            "birthday": None,
            "ignored": "x",
        }
    )

    assert profile == {
        "user_id": "user_123",
        "first_name": "Fedi",
        "email": "fedi@example.com",
    }


@pytest.mark.asyncio
async def test_booking_memory_persists_confirmed_slots_each_turn():
    deps = MagicMock()
    deps.conversation_memory.get_booking_state = AsyncMock(
        return_value={"city_name": "Paris"}
    )
    deps.conversation_memory.set_booking_state = AsyncMock()

    state = await _persist_conversation_booking_memory(
        "conv-1",
        deps,
        {
            "city_name": "Paris",
            "country_code": "FR",
            "checkin_date": "2026-07-14",
            "checkout_date": "2026-07-17",
            "guests": 2,
            "selected_hotel_id": "hotel-1",
            "hotel_rates": [],
        },
    )

    assert state["city_name"] == "Paris"
    assert state["country_code"] == "FR"
    assert state["checkin_date"] == "2026-07-14"
    assert state["checkout_date"] == "2026-07-17"
    assert state["guests"] == 2
    assert state["selected_hotel_id"] == "hotel-1"
    deps.conversation_memory.set_booking_state.assert_awaited_once_with("conv-1", state)
