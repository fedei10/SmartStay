from app.agents.booking.state import BookingState


def route_after_validation(state: BookingState) -> str:
    if state.get("next_action") == "search_hotels":
        return "search"
    return "end"


def route_after_search(state: BookingState) -> str:
    if state.get("next_action") == "show_hotels":
        return "respond"
    return "end"
