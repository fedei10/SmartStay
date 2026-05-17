"""Unit tests for routing functions — no LLM or external services needed."""
import pytest

from app.agents.booking.routing import (
    route_after_hotel_selection,
    route_after_orchestrator,
    route_after_search,
    route_after_validation,
)


class TestRouteAfterOrchestrator:
    def test_hotel_agent_routes_to_hotel(self):
        state = {"agent": "hotel_booking_agent", "next_action": None}
        assert route_after_orchestrator(state) == "hotel_agent"

    def test_insurance_agent_routes_to_insurance(self):
        state = {"agent": "insurance_management_agent", "next_action": None}
        assert route_after_orchestrator(state) == "insurance_agent"

    def test_general_assistant_routes_to_general(self):
        state = {"agent": "general_travel_assistant", "next_action": None}
        assert route_after_orchestrator(state) == "general_agent"

    def test_unknown_agent_routes_to_package(self):
        state = {"agent": "travel_booking_agent", "next_action": None}
        assert route_after_orchestrator(state) == "package_agent"

    def test_clarification_needed_routes_to_end(self):
        # When orchestrator itself asks a clarification, short-circuit to END.
        state = {"agent": "hotel_booking_agent", "next_action": "ask_clarification"}
        assert route_after_orchestrator(state) == "end"


class TestHotelRouting:
    def test_search_hotels_action_goes_to_search(self):
        assert route_after_validation({"next_action": "search_hotels"}) == "search"

    def test_search_hotel_rates_action_goes_to_rate_search(self):
        assert route_after_validation({"next_action": "search_hotel_rates"}) == "search_hotel_rates"

    def test_ask_clarification_goes_to_end(self):
        assert route_after_validation({"next_action": "ask_clarification"}) == "end"

    def test_error_goes_to_end(self):
        assert route_after_validation({"next_action": "error"}) == "end"

    def test_show_hotels_goes_to_respond(self):
        assert route_after_search({"next_action": "show_hotels"}) == "respond"

    def test_hotel_error_goes_to_end(self):
        assert route_after_search({"next_action": "error"}) == "end"

    def test_hotel_selection_can_show_existing_rates(self):
        assert route_after_hotel_selection({"next_action": "show_hotel_rates"}) == "generate_hotel_rates"
