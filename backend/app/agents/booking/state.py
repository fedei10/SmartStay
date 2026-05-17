import operator
from typing import Annotated, Literal, TypedDict

from app.agents.booking.schemas import TravelIntent


class Message(TypedDict):
    role: str
    content: str


class HotelOption(TypedDict, total=False):
    hotel_id: str
    name: str
    address: str
    city: str
    country: str
    stars: int
    rating: float
    image_url: str
    image_urls: list[str]
    rates: list[dict]


class BookingState(TypedDict, total=False):
    # Conversation
    messages: Annotated[list[Message], operator.add]
    user_message: str

    # Routing
    intent: TravelIntent
    agent: str
    response_language: str
    next_action: str | None

    # Context
    memory_context: list[dict]
    retrieval_context: list[dict]
    mcp_tools: list[str]
    requested_services: list[str]
    service_selection_required: bool | None

    # Location / hotel dates
    city_name: str | None
    country_code: str | None

    # Stay details
    checkin_date: str | None
    checkout_date: str | None
    guests: int | None
    rooms: int | None

    # Selection state — which item the user picked from a displayed list (1-based)
    selected_item_index: int | None

    # Hotel search results (list display)
    hotels: list[HotelOption]

    # Hotel rates for a specific hotel (room options)
    hotel_rates: list[dict]

    # Slot-filling helpers
    missing_fields: list[str]
    asked_fields: list[str]

    # Selection identifiers
    selected_hotel_id: str | None       # hotel chosen from hotels list
    selected_hotel_offer_id: str | None # room/rate offer chosen from hotel_rates

    # Payment / booking state
    prebook_id: str | None
    transaction_id: str | None
    secret_key: str | None
    payment_status: str | None     # "payment_required" | "completed"
    booking_status: str | None     # "payment_required" | "guest_details_required" | "confirmed"
    booking_type: str | None       # "hotel"
    payment_url: str | None
    payment_sdk_secret_key: str | None
    payment_sdk_public_key: str | None
    payment_transaction_id: str | None
    payment_prebook_id: str | None

    # Guest details for hotel booking (collected after payment)
    guest_first_name: str | None
    guest_last_name: str | None
    guest_email: str | None

    # Budget
    budget_level: str | None       # "budget" | "mid_range" | "luxury"
    budget_amount: float | None
    currency: str | None

    # Response
    response: str
    error_message: str | None
    state: dict | None

    # Legacy next_action literal (kept for routing compatibility)
    next_action: Literal[
        "ask_clarification",
        "search_hotels",
        "show_hotels",
        "search_hotel_rates",
        "show_hotel_rates",
        "prebook_hotel",
        "payment_required",
        "route_to_insurance",
        "route_to_package",
        "answer_general",
        "guest_details_required",
        "booking_confirmed",
        "error",
    ] | str | None
