import operator
from typing import Annotated, Literal, TypedDict


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
    city_name: str | None
    country_code: str | None
    hotels: list[HotelOption]
    next_action: Literal[
        "ask_clarification",
        "search_hotels",
        "show_hotels",
        "error",
    ]
    response: str
    error_message: str | None
