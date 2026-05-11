from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from app.agents.booking.nodes import (
    generate_response,
    parse_intent,
    search_hotels,
    validate_slots,
)
from app.agents.booking.routing import route_after_search, route_after_validation
from app.agents.booking.state import BookingState


def build_booking_graph(checkpointer=None):
    builder = StateGraph(BookingState)

    builder.add_node("parse_intent", parse_intent)
    builder.add_node("validate_slots", validate_slots)
    builder.add_node("search_hotels", search_hotels)
    builder.add_node("generate_response", generate_response)

    builder.add_edge(START, "parse_intent")
    builder.add_edge("parse_intent", "validate_slots")
    builder.add_conditional_edges(
        "validate_slots",
        route_after_validation,
        {
            "search": "search_hotels",
            "end": END,
        },
    )
    builder.add_conditional_edges(
        "search_hotels",
        route_after_search,
        {
            "respond": "generate_response",
            "end": END,
        },
    )
    builder.add_edge("generate_response", END)

    return builder.compile(checkpointer=checkpointer or MemorySaver())
