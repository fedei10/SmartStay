from app.agents.booking.state import BookingState
from app.agents.booking.travel_orchestrator import node_for_agent


def route_after_orchestrator(state: BookingState) -> str:
    if state.get("next_action") == "ask_clarification":
        return "end"
    return node_for_agent(state.get("agent", "travel_booking_agent"))


# ── Hotel routing ─────────────────────────────────────────────────────────────

def route_after_validation(state: BookingState) -> str:
    if state.get("next_action") == "search_hotels":
        return "search"
    return "end"


def route_after_search(state: BookingState) -> str:
    if state.get("next_action") == "show_hotels":
        return "respond"
    return "end"


# ── Flight routing ────────────────────────────────────────────────────────────

def route_after_flight_agent(state: BookingState) -> str:
    if state.get("next_action") == "route_to_flights":
        return "search"
    return "end"


def route_after_flight_search(state: BookingState) -> str:
    if state.get("next_action") == "show_flights":
        return "respond"
    return "end"
