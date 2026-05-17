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

    # Location / travel dates
    city_name: str | None
    country_code: str | None
    origin: str | None
    destination: str | None
    departure_date: str | None
    return_date: str | None

    # Trip details
    trip_type: str | None          # "one_way" | "round_trip"
    travelers: int | None
    checkin_date: str | None
    checkout_date: str | None
    guests: int | None
    rooms: int | None

    # Hotel search results
    hotels: list[HotelOption]

    # Slot-filling helpers
    missing_fields: list[str]
    asked_fields: list[str]

    # Selection state
    selected_hotel_id: str | None
    selected_hotel_offer_id: str | None
    selected_flight_offer_id: str | None

    # Payment / booking state
    prebook_id: str | None
    transaction_id: str | None
    secret_key: str | None
    payment_status: str | None     # "payment_required" | "completed"
    booking_status: str | None     # "payment_required" | "guest_details_required" | "confirmed"
    payment_url: str | None
    payment_sdk_secret_key: str | None
    payment_sdk_public_key: str | None
    payment_transaction_id: str | None
    payment_prebook_id: str | None

    # Guest details (collected after payment)
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

    # Flights
    flights: list[dict]

    # Legacy next_action literal (kept for routing compatibility)
    next_action: Literal[
        "ask_clarification",
        "search_hotels",
        "show_hotels",
        "route_to_flights",
        "route_to_insurance",
        "route_to_package",
        "answer_general",
        "guest_details_required",
        "booking_confirmed",
        "error",
    ] | str | None
