import pytest

from app.agents.booking.nodes import hotel_agent_node, orchestrate_travel
from app.agents.booking.schemas import TravelOrchestratorDecision


@pytest.mark.asyncio
async def test_hotel_agent_stays_on_hotel_flow_for_generic_trip_request():
    result = await hotel_agent_node(
        {
            "user_message": "I want to travel to Munich",
            "city_name": "Munich",
            "country_code": "DE",
            "checkin_date": "2026-07-14",
            "checkout_date": "2026-07-17",
            "response_language": "en",
        },
        {},
    )

    assert result["agent"] == "hotel_booking_agent"
    assert result["next_action"] == "search_hotels"


@pytest.mark.asyncio
async def test_hotel_agent_allows_hotel_first_when_user_explicitly_requests_it():
    result = await hotel_agent_node(
        {
            "user_message": "just hotel in Munich",
            "city_name": "Munich",
            "country_code": "DE",
            "checkin_date": "2026-07-14",
            "checkout_date": "2026-07-17",
            "response_language": "en",
        },
        {},
    )

    assert result["agent"] == "hotel_booking_agent"
    assert result["next_action"] == "search_hotels"


@pytest.mark.asyncio
async def test_orchestrator_requires_service_choice_for_generic_trip_request():
    result = await orchestrate_travel(
        {
            "user_message": "I want to travel to Munich",
            "memory_context": [],
            "requested_services": [],
        },
        {
            "configurable": {
                "conversation_id": "conv-1",
                "deps": _DummyDeps(),
            }
        },
    )

    assert result["intent"] == "clarification_needed"
    assert result["service_selection_required"] is True
    assert "hotel" in result["response"].lower()


@pytest.mark.asyncio
async def test_orchestrator_routes_after_hotel_service_choice_reply():
    result = await orchestrate_travel(
        {
            "user_message": "hotel",
            "service_selection_required": True,
            "memory_context": [],
            "requested_services": [],
        },
        {
            "configurable": {
                "conversation_id": "conv-1",
                "deps": _DummyDeps(),
            }
        },
    )

    assert result["intent"] == "hotel_search"
    assert result["agent"] == "hotel_booking_agent"
    assert result["requested_services"] == ["hotels"]
    assert result["service_selection_required"] is False


class _DummyMemory:
    async def get_recent(self, conversation_id):
        return []

    async def get_booking_state(self, conversation_id):
        return {}

    async def get_user_profile(self, user_id):
        return {}


class _DummyRetriever:
    async def search(self, message, limit):
        if "munich" in message.lower():
            return [{"city_name": "Munich"}]
        return []


class _DummyLiteAPITools:
    async def get_tool_names(self):
        return []


class _DummyDeps:
    def __init__(self):
        self.conversation_memory = _DummyMemory()
        self.retriever = _DummyRetriever()
        self.liteapi_tools = _DummyLiteAPITools()
        self.llm = _DummyLLM()
        self.llm_provider = None


class _DummyLLM:
    def with_structured_output(self, schema):
        return self

    async def ainvoke(self, messages):
        latest = messages[-1].content.lower()
        if "munich" in latest:
            return TravelOrchestratorDecision(
                intent="hotel_booking",
                agent="hotel_booking_agent",
                city_name="Munich",
                country_code="DE",
                requested_services=[],
                response_language="en",
            )
        return TravelOrchestratorDecision(
            intent="general_travel_question",
            agent="general_travel_assistant",
            requested_services=[],
            response_language="en",
        )
