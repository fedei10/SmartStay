from langgraph.graph import END, START, StateGraph

from app.agents.booking.nodes import (
    generate_hotel_rates_response,
    generate_response,
    general_agent_node,
    hotel_agent_node,
    hotel_rate_selection_node,
    hotel_selection_node,
    insurance_agent_node,
    orchestrate_travel,
    package_agent_node,
    prebook_hotel_node,
    search_hotel_rates_node,
    search_hotels,
)
from app.agents.booking.routing import (
    route_after_hotel_rate_selection,
    route_after_hotel_rates,
    route_after_hotel_selection,
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
    builder.add_node("insurance_agent", insurance_agent_node)
    builder.add_node("package_agent", package_agent_node)
    builder.add_node("general_agent", general_agent_node)

    # Hotel sub-graph
    builder.add_node("search_hotels", search_hotels)
    builder.add_node("generate_response", generate_response)
    builder.add_node("hotel_selection", hotel_selection_node)
    builder.add_node("search_hotel_rates", search_hotel_rates_node)
    builder.add_node("generate_hotel_rates", generate_hotel_rates_response)
    builder.add_node("hotel_rate_selection", hotel_rate_selection_node)
    builder.add_node("prebook_hotel", prebook_hotel_node)

    # ── Edges ─────────────────────────────────────────────────────────────────
    builder.add_edge(START, "travel_orchestrator")

    builder.add_conditional_edges(
        "travel_orchestrator",
        route_after_orchestrator,
        {
            "hotel_agent": "hotel_agent",
            "insurance_agent": "insurance_agent",
            "package_agent": "package_agent",
            "general_agent": "general_agent",
            "hotel_selection": "hotel_selection",
            "hotel_rate_selection": "hotel_rate_selection",
            "end": END,
        },
    )

    # Hotel flow: validate → search → respond
    builder.add_conditional_edges(
        "hotel_agent",
        route_after_validation,
        {
            "search": "search_hotels",
            "search_hotel_rates": "search_hotel_rates",
            "end": END,
        },
    )
    builder.add_conditional_edges(
        "search_hotels",
        route_after_search,
        {"respond": "generate_response", "end": END},
    )
    builder.add_edge("generate_response", END)

    # Hotel selection → rates → rate selection → prebook
    builder.add_conditional_edges(
        "hotel_selection",
        route_after_hotel_selection,
        {
            "search_hotel_rates": "search_hotel_rates",
            "generate_hotel_rates": "generate_hotel_rates",
            "end": END,
        },
    )
    builder.add_conditional_edges(
        "search_hotel_rates",
        route_after_hotel_rates,
        {"generate_hotel_rates": "generate_hotel_rates", "end": END},
    )
    builder.add_edge("generate_hotel_rates", END)
    builder.add_conditional_edges(
        "hotel_rate_selection",
        route_after_hotel_rate_selection,
        {"prebook_hotel": "prebook_hotel", "end": END},
    )
    builder.add_edge("prebook_hotel", END)

    # Other agents go directly to END
    builder.add_edge("insurance_agent", END)
    builder.add_edge("package_agent", END)
    builder.add_edge("general_agent", END)

    return builder.compile(checkpointer=checkpointer)
