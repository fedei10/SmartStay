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


class BookingState(TypedDict, total=False):
    messages: Annotated[list[Message], operator.add]
    user_message: str
    intent: TravelIntent
    agent: str
    city_name: str | None
    country_code: str | None
    origin: str | None
    destination: str | None
    departure_date: str | None
    return_date: str | None
    requested_services: list[str]
    response_language: str
    memory_context: list[dict]
    retrieval_context: list[dict]
    mcp_tools: list[str]
    hotels: list[HotelOption]
    next_action: Literal[
        "ask_clarification",
        "search_hotels",
        "show_hotels",
        "route_to_flights",
        "route_to_insurance",
        "route_to_package",
        "answer_general",
        "error",
    ]
    response: str
    error_message: str | None
