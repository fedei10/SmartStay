from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

TravelIntent = Literal[
    "hotel_search",
    "hotel_booking",
    "flight_search",
    "flight_booking",
    "insurance",
    "combined_trip",
    "general_travel_question",
    "clarification_needed",
]

AgentName = Literal[
    "travel_booking_agent",
    "hotel_booking_agent",
    "flight_booking_agent",
    "insurance_management_agent",
    "general_travel_assistant",
]

RequestedService = Literal["hotels", "flights", "insurance", "planning"]


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
    origin: str | None = Field(
        default=None, description="Flight origin IATA airport code (e.g. TUN, CDG) when available."
    )
    destination: str | None = Field(
        default=None,
        description="Flight destination IATA airport code (e.g. CDG, JFK) when available.",
    )
    departure_date: str | None = Field(
        default=None, description="Resolved ISO date YYYY-MM-DD for flight departure."
    )
    return_date: str | None = Field(
        default=None, description="Resolved ISO date YYYY-MM-DD for return flight when round trip."
    )
    trip_type: str | None = Field(
        default=None,
        description="'one_way' or 'round_trip'. Infer from context — default to one_way when unclear.",
    )
    travelers: int | None = Field(
        default=None,
        description="Total number of travelers (adults). Extract from phrases like '2 people', 'for 3'.",
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
            "and recent memory. Include hotels, flights, insurance, or planning."
        ),
    )

    model_config = ConfigDict(extra="forbid")
