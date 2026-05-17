from app.agents.booking.state import BookingState
from app.agents.booking.travel_orchestrator import node_for_agent


def route_after_orchestrator(state: BookingState) -> str:
    if state.get("next_action") == "ask_clarification":
        return "end"
    return node_for_agent(state.get("agent", "travel_booking_agent"))


def route_after_validation(state: BookingState) -> str:
    if state.get("next_action") == "search_hotels":
        return "search"
    return "end"


def route_after_search(state: BookingState) -> str:
    if state.get("next_action") == "show_hotels":
        return "respond"
    return "end"
