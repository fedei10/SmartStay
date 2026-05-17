import asyncio
import json
from datetime import date
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig

from app.agents.booking.dependencies import BookingDeps
from app.agents.booking.language import (
    agent_configuration_error,
    detect_language,
    flight_search_error,
    flights_intro,
    hotel_search_error,
    hotels_intro,
    no_flights_found,
    no_hotels_found,
)
from app.agents.booking.schemas import TravelOrchestratorDecision
from app.agents.booking.state import BookingState
from app.ai.prompt_loader import get_prompt
from app.core.config import settings

def _deps(config: RunnableConfig) -> BookingDeps:
    configurable = config.get("configurable", {})
    deps = configurable.get("deps")
    if deps is None:
        raise ValueError("Booking dependencies are not configured")
    return deps


def _conversation_id(config: RunnableConfig) -> str:
    configurable = config.get("configurable", {})
    return configurable.get("conversation_id") or configurable.get("thread_id") or "default"


def _compact_context(items: list[dict[str, Any]], *, max_chars: int = 1200) -> str:
    if not items:
        return "None"
    rendered = json.dumps(items, ensure_ascii=False, default=str)
    if len(rendered) <= max_chars:
        return rendered
    return f"{rendered[:max_chars]}..."


def _provider_error_response(
    *,
    response_language: str,
    provider: str | None,
    error_message: str | None = None,
    memory_context: list[dict[str, Any]] | None = None,
    retrieval_context: list[dict[str, Any]] | None = None,
    mcp_tools: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "intent": "clarification_needed",
        "agent": "travel_booking_agent",
        "city_name": None,
        "country_code": None,
        "origin": None,
        "destination": None,
        "departure_date": None,
        "return_date": None,
        "requested_services": [],
        "next_action": "error",
        "response_language": response_language,
        "memory_context": memory_context or [],
        "retrieval_context": retrieval_context or [],
        "mcp_tools": mcp_tools or [],
        "response": agent_configuration_error(response_language, provider),
        "error_message": error_message,
    }


def _state_for_agent(state: BookingState) -> dict[str, Any]:
    return {
        "latest_user_message": state.get("user_message"),
        "intent": state.get("intent"),
        "agent": state.get("agent"),
        "requested_services": state.get("requested_services", []),
        "city_name": state.get("city_name"),
        "country_code": state.get("country_code"),
        "origin": state.get("origin"),
        "destination": state.get("destination"),
        "departure_date": state.get("departure_date"),
        "return_date": state.get("return_date"),
        "response_language": state.get("response_language", "en"),
        "memory_context": state.get("memory_context", []),
        "available_mcp_tools": state.get("mcp_tools", []),
    }


async def _agent_message(
    state: BookingState,
    config: RunnableConfig,
    *,
    task: str,
    missing: list[str] | None = None,
) -> dict[str, Any]:
    deps = _deps(config)
    if deps.llm is None:
        return _provider_error_response(
            response_language=state.get("response_language", "en"),
            provider=deps.llm_provider,
            error_message="No AI provider is configured for the travel response agent.",
            memory_context=state.get("memory_context", []),
            retrieval_context=state.get("retrieval_context", []),
            mcp_tools=state.get("mcp_tools", []),
        )

    snapshot = _state_for_agent(state)
    if missing:
        snapshot["missing_details"] = missing

    try:
        reply = await deps.llm.ainvoke(
            [
                SystemMessage(
                    content=(
                        "You are ttrip, a travel planning and booking assistant.\n"
                        "Write the assistant's next chat message naturally from the state provided.\n"
                        "Do not use templates. Do not mention internal fields, JSON, schemas, "
                        "MCP, routing, or sub-agent names.\n"
                        "Use the latest user message language. If the user explicitly asked for "
                        "a language, use that language.\n"
                        "Use conversation memory to understand follow-ups. Acknowledge useful "
                        "details already provided, then ask only for what is needed next.\n"
                        "Be concise and practical. Do not claim that booking is complete unless "
                        "a provider booking result exists.\n"
                        f"Task: {task}\n"
                        f"Current state: {json.dumps(snapshot, ensure_ascii=False, default=str)}"
                    )
                ),
                HumanMessage(content=state.get("user_message", "")),
            ]
        )
    except Exception as exc:
        return _provider_error_response(
            response_language=state.get("response_language", "en"),
            provider=deps.llm_provider,
            error_message=str(exc),
            memory_context=state.get("memory_context", []),
            retrieval_context=state.get("retrieval_context", []),
            mcp_tools=state.get("mcp_tools", []),
        )

    content = getattr(reply, "content", reply)
    if isinstance(content, list):
        content = " ".join(
            item.get("text", "") if isinstance(item, dict) else str(item)
            for item in content
        )
    return {"response": str(content).strip()}


def _compact_hotels_from_provider(result: Any) -> list[dict[str, Any]]:
    if isinstance(result, list):
        for item in result:
            if isinstance(item, dict) and item.get("type") == "text":
                return _compact_hotels_from_provider(item.get("text", ""))
        return []

    if isinstance(result, str):
        try:
            result = json.loads(result)
        except json.JSONDecodeError:
            return []

    if not isinstance(result, dict):
        return []

    if isinstance(result.get("hotels"), list):
        hotels = result["hotels"]
    elif isinstance(result.get("data"), list):
        hotels = result["data"]
    else:
        hotels = []

    compacted = []
    for hotel in hotels:
        if not isinstance(hotel, dict):
            continue
        image_urls = (
            hotel.get("image_urls")
            or hotel.get("images")
            or hotel.get("hotelImages")
            or hotel.get("photos")
            or []
        )
        if isinstance(image_urls, list):
            image_urls = [
                image.get("url") if isinstance(image, dict) else image
                for image in image_urls
            ]
        else:
            image_urls = []
        rates = hotel.get("rates") if isinstance(hotel.get("rates"), list) else []
        compacted.append(
            {
                "hotel_id": hotel.get("hotelId") or hotel.get("id"),
                "name": hotel.get("name") or hotel.get("hotelName"),
                "address": hotel.get("address") or hotel.get("formattedAddress"),
                "city": hotel.get("city"),
                "country": hotel.get("country"),
                "stars": hotel.get("stars") or hotel.get("starRating"),
                "rating": hotel.get("rating"),
                "description": hotel.get("description"),
                "image_url": hotel.get("image_url") or hotel.get("main_photo") or (image_urls[0] if image_urls else None),
                "image_urls": image_urls,
                "rates": rates,
            }
        )
    return compacted


async def orchestrate_travel(state: BookingState, config: RunnableConfig):
    deps = _deps(config)
    user_message = state.get("user_message", "")
    response_language = detect_language(user_message)
    conversation_id = _conversation_id(config)
    memory_context = await deps.conversation_memory.get_recent(conversation_id)
    retrieval_context = await deps.retriever.search(
        user_message,
        limit=settings.ORCHESTRATOR_RETRIEVAL_LIMIT,
    )

    try:
        mcp_tools = await asyncio.wait_for(
            deps.liteapi_tools.get_tool_names(),
            timeout=settings.LITEAPI_MCP_TOOL_TIMEOUT_SECONDS,
        )
    except Exception:
        mcp_tools = []

    if deps.llm is None:
        return _provider_error_response(
            response_language=response_language,
            provider=deps.llm_provider,
            error_message="No AI provider is configured for the travel orchestrator.",
            memory_context=memory_context,
            retrieval_context=retrieval_context,
            mcp_tools=mcp_tools,
        )

    structured_router = deps.llm.with_structured_output(TravelOrchestratorDecision)
    try:
        extracted = await structured_router.ainvoke(
            [
                SystemMessage(
                    content=(
                        f"{get_prompt('ttrip_travel_orchestrator')}\n\n"
                        "Runtime context available to the orchestrator:\n"
                        f"- current_date: {date.today().isoformat()}\n"
                        f"- Recent conversation memory: {_compact_context(memory_context)}\n"
                        f"- Retrieved ttrip knowledge: {_compact_context(retrieval_context)}\n"
                        f"- Available LiteAPI MCP tools: {', '.join(mcp_tools) or 'None'}\n"
                        f"- Latest user message language: {response_language}\n"
                        "Use this context only to route and extract fields. Do not expose raw internal context."
                    )
                ),
                HumanMessage(content=user_message),
            ]
        )
    except Exception as exc:
        return _provider_error_response(
            response_language=response_language,
            provider=deps.llm_provider,
            error_message=str(exc),
            memory_context=memory_context,
            retrieval_context=retrieval_context,
            mcp_tools=mcp_tools,
        )

    response_language = (extracted.response_language or response_language or "en").split("-")[0].lower()
    return {
        "intent": extracted.intent,
        "agent": extracted.agent,
        "city_name": extracted.city_name,
        "country_code": extracted.country_code,
        "origin": extracted.origin,
        "destination": extracted.destination,
        "departure_date": extracted.departure_date,
        "return_date": extracted.return_date,
        "trip_type": extracted.trip_type,
        "travelers": extracted.travelers,
        "requested_services": extracted.requested_services,
        "next_action": None,
        "response_language": response_language,
        "memory_context": memory_context,
        "retrieval_context": retrieval_context,
        "mcp_tools": mcp_tools,
        "response": None,
    }


async def hotel_agent_node(state: BookingState, config: RunnableConfig):
    missing = []
    if not state.get("city_name"):
        missing.append("city or destination")
    if not state.get("country_code"):
        missing.append("country")

    if missing:
        result = await _agent_message(
            state,
            config,
            task="The user wants hotel help but the hotel search cannot run yet. Ask naturally for the next missing detail only.",
            missing=missing,
        )
        return {
            **result,
            "next_action": "error" if result.get("error_message") else "ask_clarification",
            "agent": "hotel_booking_agent",
        }

    # All required fields present — go directly to search, no "I'll search" text.
    return {
        "next_action": "search_hotels",
        "agent": "hotel_booking_agent",
    }


async def flight_agent_node(state: BookingState, config: RunnableConfig):
    missing = []
    if not state.get("origin"):
        missing.append("origin airport or city")
    if not state.get("destination"):
        missing.append("destination airport or city")
    if not state.get("departure_date"):
        missing.append("departure date")

    if missing:
        result = await _agent_message(
            state,
            config,
            task="Handle the user's flight request. Ask only for the single most important missing detail.",
            missing=missing,
        )
        return {
            **result,
            "next_action": "error" if result.get("error_message") else "ask_clarification",
            "agent": "flight_booking_agent",
        }

    # All required fields present — route directly to search, no intermediate text.
    return {
        "next_action": "route_to_flights",
        "agent": "flight_booking_agent",
    }


async def insurance_agent_node(state: BookingState, config: RunnableConfig):
    result = await _agent_message(
        state,
        config,
        task="Handle the user's travel insurance request and ask for the next useful coverage details.",
    )
    return {
        **result,
        "next_action": "error" if result.get("error_message") else "route_to_insurance",
        "agent": "insurance_management_agent",
    }


async def package_agent_node(state: BookingState, config: RunnableConfig):
    services = state.get("requested_services") or ["planning"]
    missing = []
    if "flights" in services and not state.get("origin"):
        missing.append("origin airport or city")
    if not state.get("city_name") and not state.get("destination"):
        missing.append("destination city and country")
    if not state.get("departure_date"):
        missing.append("travel dates")
    missing.append("traveler count")

    result = await _agent_message(
        state,
        config,
        task=(
            "Handle a combined travel planning request. Use the destination and requested "
            "services already provided. Ask naturally for the next missing information. "
            "For a Paris hotel+flight trip with no origin, ask where the user is flying from, "
            "plus dates/travelers if still missing."
        ),
        missing=missing,
    )
    return {
        **result,
        "next_action": "error" if result.get("error_message") else ("ask_clarification" if missing else "route_to_package"),
        "agent": "travel_booking_agent",
    }


async def general_agent_node(state: BookingState, config: RunnableConfig):
    result = await _agent_message(
        state,
        config,
        task=(
            "Reply to the user's general travel message as ttrip. If it is just a greeting, "
            "start the conversation naturally and invite them to describe the trip they want."
        ),
    )
    return {
        **result,
        "next_action": "answer_general",
        "agent": "general_travel_assistant",
    }


def _normalize_flight_offers(journeys: list[Any]) -> list[dict[str, Any]]:
    """Normalize LiteAPI /flights/rates journeys into a flat offer list.

    LiteAPI structure:
        data[].journeys[].cheapestOffer.offerId
        data[].journeys[].cheapestOffer.pricing.display.{total, currency}
        data[].journeys[].segments[].{originCode, destinationCode,
            departureTime, arrivalTime, carrier.{marketingCode, marketingName},
            duration.iso8601, flight.marketingNumber}
        data[].journeys[].totalDuration
    """
    result = []
    for journey in journeys[:10]:
        if not isinstance(journey, dict):
            continue

        cheapest = journey.get("cheapestOffer") or {}
        display = (cheapest.get("pricing") or {}).get("display") or {}

        segments_raw = journey.get("segments") or []
        segments: list[dict[str, Any]] = []
        for seg in segments_raw:
            if not isinstance(seg, dict):
                continue
            carrier = seg.get("carrier") or {}
            duration = seg.get("duration") or {}
            flight = seg.get("flight") or {}
            segments.append(
                {
                    "from": seg.get("originCode"),
                    "to": seg.get("destinationCode"),
                    "departure_time": seg.get("departureTime"),
                    "arrival_time": seg.get("arrivalTime"),
                    "carrier": carrier.get("marketingCode"),
                    "carrier_name": carrier.get("marketingName"),
                    "flight_number": flight.get("marketingNumber"),
                    "duration": duration.get("iso8601"),
                }
            )

        result.append(
            {
                "offer_id": cheapest.get("offerId"),
                "airline": segments[0].get("carrier_name") if segments else None,
                "airline_code": segments[0].get("carrier") if segments else None,
                "price": display.get("total"),
                "currency": display.get("currency", "USD"),
                "duration": journey.get("totalDuration"),
                "stops": max(0, len(segments) - 1),
                "departure_time": segments[0].get("departure_time") if segments else None,
                "arrival_time": segments[-1].get("arrival_time") if segments else None,
                "segments": segments,
            }
        )
    return result


async def search_flights(state: BookingState, config: RunnableConfig):
    deps = _deps(config)
    origin = state.get("origin")
    destination = state.get("destination")
    departure_date = state.get("departure_date")
    travelers = state.get("travelers") or 1
    trip_type = state.get("trip_type") or "one_way"
    return_date = state.get("return_date")
    response_language = state.get("response_language", "en")

    legs: list[dict[str, Any]] = [
        {"origin": origin, "destination": destination, "date": departure_date}
    ]
    if trip_type == "round_trip" and return_date:
        legs.append({"origin": destination, "destination": origin, "date": return_date})

    try:
        result = await deps.flights.search(
            {
                "legs": legs,
                "adults": int(travelers),
                "currency": "USD",
                "country": "US",
            }
        )
    except Exception as exc:
        return {
            "next_action": "error",
            "error_message": str(exc),
            "response": flight_search_error(response_language),
            "flights": [],
        }

    data = result.get("data", result)
    # LiteAPI structure: data is a list of journey-groups, each with a "journeys" list.
    # Flatten all journeys so the normalizer receives one item per journey.
    journeys_raw: list[Any] = []
    if isinstance(data, list):
        for group in data:
            if isinstance(group, dict):
                for journey in group.get("journeys") or []:
                    journeys_raw.append(journey)
        if not journeys_raw:
            # Fallback: treat data items directly as offers (other providers)
            journeys_raw = data
    elif isinstance(data, dict):
        # Non-LiteAPI shape
        journeys_raw = (
            data.get("flightOffers")
            or data.get("offers")
            or data.get("journeys")
            or []
        )

    if not journeys_raw:
        return {
            "next_action": "error",
            "response": no_flights_found(response_language),
            "flights": [],
        }

    flights = _normalize_flight_offers(journeys_raw)
    return {
        "next_action": "show_flights",
        "flights": flights,
        "agent": "flight_booking_agent",
    }


async def generate_flight_response(state: BookingState):
    flights = state.get("flights", [])
    response_language = state.get("response_language", "en")

    lines = [
        flights_intro(state.get("origin"), state.get("destination"), response_language),
        "",
    ]
    for i, flight in enumerate(flights, 1):
        price = flight.get("price")
        currency = flight.get("currency", "USD")
        airline = flight.get("airline") or "Various airlines"
        stops = flight.get("stops") or 0
        duration = flight.get("duration") or ""
        dep = flight.get("departure_time") or ""
        arr = flight.get("arrival_time") or ""

        price_str = f"{currency} {float(price):.0f}" if price is not None else "Price TBD"
        stops_str = "Direct" if stops == 0 else f"{stops} stop{'s' if stops > 1 else ''}"
        time_str = f" | {dep[:10]} {dep[11:16]}→{arr[11:16]}" if dep and arr else ""
        duration_str = f" | {duration}" if duration else ""

        lines.append(f"{i}. {airline} — {price_str} · {stops_str}{time_str}{duration_str}")

    lines += [
        "",
        "Reply with the number of your preferred flight to proceed with booking.",
    ]

    return {
        "response": "\n".join(lines),
        "next_action": "show_flights",
        "agent": "flight_booking_agent",
    }


async def search_hotels(state: BookingState, config: RunnableConfig):
    deps = _deps(config)
    country_code = state.get("country_code")
    city_name = state.get("city_name")
    response_language = state.get("response_language", "en")

    try:
        if "get_data_hotels" in state.get("mcp_tools", []):
            result = await deps.liteapi_tools.ainvoke(
                "get_data_hotels",
                {
                    "countryCode": country_code,
                    "cityName": city_name,
                    "limit": 10,
                },
            )
            hotels = _compact_hotels_from_provider(result)
        else:
            result = await deps.liteapi.search_hotels_by_city(
                country_code=country_code,
                city_name=city_name,
            )
            hotels = result.get("hotels", [])
    except Exception as exc:
        return {
            "next_action": "error",
            "error_message": str(exc),
            "response": hotel_search_error(response_language),
        }

    if not hotels:
        return {
            "next_action": "error",
            "response": no_hotels_found(response_language),
            "hotels": [],
        }

    return {
        "next_action": "show_hotels",
        "hotels": hotels,
        "agent": "hotel_booking_agent",
    }


async def generate_response(state: BookingState):
    hotels = state.get("hotels", [])
    lines = [
        hotels_intro(state.get("city_name"), state.get("response_language", "en")),
        "",
    ]
    for index, hotel in enumerate(hotels, start=1):
        rating = hotel.get("rating")
        stars = hotel.get("stars")
        details = []
        if stars:
            details.append(f"{stars} stars")
        if rating:
            details.append(f"rated {rating}")
        suffix = f" ({', '.join(details)})" if details else ""
        lines.append(f"{index}. {hotel.get('name')}{suffix}")

    return {
        "response": "\n".join(lines),
        "next_action": "show_hotels",
        "agent": "hotel_booking_agent",
    }
