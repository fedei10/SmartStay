from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from app.agents.booking.nodes import (
    flight_agent_node,
    generate_flight_response,
    generate_response,
    general_agent_node,
    hotel_agent_node,
    insurance_agent_node,
    orchestrate_travel,
    package_agent_node,
    search_flights,
    search_hotels,
)
from app.agents.booking.routing import (
    route_after_flight_agent,
    route_after_flight_search,
    route_after_orchestrator,
    route_after_search,
    route_after_validation,
)
from app.agents.booking.state import BookingState


def build_booking_graph(checkpointer=None):
    builder = StateGraph(BookingState)

    # ── Nodes ─────────────────────────────────────────────────────────────────
    builder.add_node("travel_orchestrator", orchestrate_travel)
    builder.add_node("hotel_agent", hotel_agent_node)
    builder.add_node("flight_agent", flight_agent_node)
    builder.add_node("insurance_agent", insurance_agent_node)
    builder.add_node("package_agent", package_agent_node)
    builder.add_node("general_agent", general_agent_node)

    # Hotel sub-graph
    builder.add_node("search_hotels", search_hotels)
    builder.add_node("generate_response", generate_response)

    # Flight sub-graph
    builder.add_node("search_flights", search_flights)
    builder.add_node("generate_flight_response", generate_flight_response)

    # ── Edges ─────────────────────────────────────────────────────────────────
    builder.add_edge(START, "travel_orchestrator")

    builder.add_conditional_edges(
        "travel_orchestrator",
        route_after_orchestrator,
        {
            "hotel_agent": "hotel_agent",
            "flight_agent": "flight_agent",
            "insurance_agent": "insurance_agent",
            "package_agent": "package_agent",
            "general_agent": "general_agent",
            "end": END,
        },
    )

    # Hotel flow: validate → search → respond
    builder.add_conditional_edges(
        "hotel_agent",
        route_after_validation,
        {"search": "search_hotels", "end": END},
    )
    builder.add_conditional_edges(
        "search_hotels",
        route_after_search,
        {"respond": "generate_response", "end": END},
    )
    builder.add_edge("generate_response", END)

    # Flight flow: validate → search → respond
    builder.add_conditional_edges(
        "flight_agent",
        route_after_flight_agent,
        {"search": "search_flights", "end": END},
    )
    builder.add_conditional_edges(
        "search_flights",
        route_after_flight_search,
        {"respond": "generate_flight_response", "end": END},
    )
    builder.add_edge("generate_flight_response", END)

    # Other agents go directly to END
    builder.add_edge("insurance_agent", END)
    builder.add_edge("package_agent", END)
    builder.add_edge("general_agent", END)

    return builder.compile(checkpointer=checkpointer or MemorySaver())
