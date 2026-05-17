from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

TravelIntent = Literal[
    "hotel_search",
    "hotel_booking",
    "hotel_selection",       # user picked a hotel from the displayed list
    "hotel_rate_selection",  # user picked a room/rate from displayed rates
    "insurance",
    "combined_trip",
    "general_travel_question",
    "clarification_needed",
]

AgentName = Literal[
    "travel_booking_agent",
    "hotel_booking_agent",
    "insurance_management_agent",
    "general_travel_assistant",
]

RequestedService = Literal["hotels", "insurance", "planning"]


class TravelOrchestratorDecision(BaseModel):
    intent: TravelIntent = Field(
        description="The booking intent that determines which ttrip sub-agent handles the request."
    )
    agent: AgentName = Field(
        description="The ttrip sub-agent selected by the orchestrator."
    )
    city_name: str | None = Field(
        default=None, description="Hotel destination city name in English when available."
    )
    country_code: str | None = Field(
        default=None, description="ISO 3166-1 alpha-2 country code when available."
    )
    checkin_date: str | None = Field(
        default=None,
        description=(
            "Resolved ISO date YYYY-MM-DD for hotel check-in. "
            "Resolve relative phrases like 'next week' → next Monday, 'this weekend' → nearest Saturday."
        ),
    )
    checkout_date: str | None = Field(
        default=None,
        description=(
            "Resolved ISO date YYYY-MM-DD for hotel check-out. "
            "Default stay: 3 nights when the user gives a week/period without an explicit duration."
        ),
    )
    guests: int | None = Field(
        default=None,
        description="Number of hotel guests (adults). Extract from '2 people', 'family of 4', etc.",
    )
    selected_item_index: int | None = Field(
        default=None,
        description=(
            "1-based index when the user selects an item from a displayed list. "
            "Extract from '1', '2', 'the first one', 'option 2', 'hotel 3', etc."
        ),
    )
    guest_first_name: str | None = Field(
        default=None,
        description="Main guest first name for hotel booking. Extract from user message.",
    )
    guest_last_name: str | None = Field(
        default=None,
        description="Main guest last name for hotel booking.",
    )
    guest_email: str | None = Field(
        default=None,
        description="Main guest email address for hotel booking.",
    )
    response_language: str = Field(
        default="en",
        description=(
            "BCP-47-style language code for the assistant reply. Detect it from the latest "
            "user message unless the user explicitly requests another response language."
        ),
    )
    requested_services: list[RequestedService] = Field(
        default_factory=list,
        description=(
            "Travel services the user is asking for, inferred from the latest message "
            "and recent memory. Include hotels, insurance, or planning."
        ),
    )

    model_config = ConfigDict(extra="forbid")
