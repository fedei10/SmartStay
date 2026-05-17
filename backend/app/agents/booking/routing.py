from app.agents.booking.state import BookingState
from app.agents.booking.travel_orchestrator import node_for_agent


def route_after_orchestrator(state: BookingState) -> str:
    if state.get("next_action") == "ask_clarification":
        return "end"
    intent = state.get("intent")
    if intent == "hotel_selection":
        return "hotel_selection"
    if intent == "hotel_rate_selection":
        return "hotel_rate_selection"
    return node_for_agent(state.get("agent", "travel_booking_agent"))


# ── Hotel routing ─────────────────────────────────────────────────────────────

def route_after_validation(state: BookingState) -> str:
    if state.get("next_action") == "search_hotel_rates":
        return "search_hotel_rates"
    if state.get("next_action") == "search_hotels":
        return "search"
    return "end"


def route_after_search(state: BookingState) -> str:
    if state.get("next_action") == "show_hotels":
        return "respond"
    return "end"


def route_after_hotel_selection(state: BookingState) -> str:
    if state.get("next_action") == "show_hotel_rates":
        return "generate_hotel_rates"
    return "search_hotel_rates" if state.get("next_action") == "search_hotel_rates" else "end"


def route_after_hotel_rates(state: BookingState) -> str:
    return "generate_hotel_rates" if state.get("next_action") == "show_hotel_rates" else "end"


def route_after_hotel_rate_selection(state: BookingState) -> str:
    return "prebook_hotel" if state.get("next_action") == "prebook_hotel" else "end"
