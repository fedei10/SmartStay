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
    hotel_search_error,
    hotels_intro,
    no_hotels_found,
    provider_runtime_error,
)
from app.agents.booking.schemas import TravelOrchestratorDecision
from app.agents.booking.state import BookingState
from app.ai.prompt_loader import get_prompt
from app.core.config import settings


# ── Helpers ───────────────────────────────────────────────────────────────────

def _deps(config: RunnableConfig) -> BookingDeps:
    configurable = config.get("configurable", {})
    deps = configurable.get("deps")
    if deps is None:
        raise ValueError("Booking dependencies are not configured")
    return deps


def _conversation_id(config: RunnableConfig) -> str:
    configurable = config.get("configurable", {})
    return configurable.get("conversation_id") or configurable.get("thread_id") or "default"


def _user_id(config: RunnableConfig) -> str | None:
    return config.get("configurable", {}).get("user_id")


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
    has_provider = bool(provider)
    response_message = (
        provider_runtime_error(response_language, provider, error_message)
        if has_provider
        else agent_configuration_error(response_language, provider)
    )
    return {
        "intent": "clarification_needed",
        "agent": "travel_booking_agent",
        "city_name": None,
        "country_code": None,
        "requested_services": [],
        "next_action": "error",
        "response_language": response_language,
        "memory_context": memory_context or [],
        "retrieval_context": retrieval_context or [],
        "mcp_tools": mcp_tools or [],
        "response": response_message,
        "error_message": error_message,
    }


def _state_for_agent(state: BookingState) -> dict[str, Any]:
    snapshot = {
        "latest_user_message": state.get("user_message"),
        "intent": state.get("intent"),
        "requested_services": state.get("requested_services", []),
        "response_language": state.get("response_language", "en"),
        "memory_context": state.get("memory_context", []),
    }
    for field in (
        "city_name", "country_code", "checkin_date", "checkout_date", "guests",
        "guest_first_name", "guest_last_name", "guest_email",
        "selected_hotel_id", "selected_item_index",
    ):
        val = state.get(field)
        if val is not None:
            snapshot[field] = val
    return snapshot


def _keep(new_val, existing_val):
    """Return new_val when the LLM extracted something; otherwise preserve existing state."""
    return new_val if new_val is not None else existing_val


def _normalize_service_choice(message: str | None) -> str | None:
    text = (message or "").strip().lower()
    if text in {"hotel", "hotels", "hôtel", "hôtels"}:
        return "hotels"
    return None


def _is_explicit_service_request(message: str | None) -> bool:
    text = (message or "").lower()
    return any(
        token in text
        for token in (
            "hotel",
            "hotels",
            "hôtel",
            "hôtels",
        )
    )


def _is_generic_trip_request(message: str | None) -> bool:
    text = (message or "").lower()
    return any(
        token in text
        for token in (
            "travel",
            "trip",
            "go to",
            "visit",
            "vacation",
            "holiday",
            "voyage",
            "aller à",
            "je veux aller",
        )
    )


def _service_choice_prompt(language: str, destination_label: str | None = None) -> str:
    destination = destination_label or "your destination"
    if language == "fr":
        return f"Pour {destination}, veux-tu que je cherche des hôtels disponibles ?"
    if language == "ar":
        return f"بالنسبة إلى {destination}، هل تريد أن أبحث عن فنادق متاحة؟"
    return f"For {destination}, would you like me to search available hotels?"


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


# ── Hotel helpers ─────────────────────────────────────────────────────────────

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


def _hotel_identity(hotel: dict[str, Any]) -> str | None:
    return (
        hotel.get("hotel_id")
        or hotel.get("hotelId")
        or hotel.get("id")
        or hotel.get("liteapiHotelId")
    )


def _flatten_room_rates(hotel_data: dict[str, Any]) -> list[dict[str, Any]]:
    room_types = hotel_data.get("roomTypes", []) if isinstance(hotel_data, dict) else []
    flat_rates: list[dict[str, Any]] = []

    for room in room_types:
        offer_id = room.get("offerId")
        for rate in (room.get("rates") or []):
            price_list = (rate.get("retailRate") or {}).get("total") or []
            price = price_list[0].get("amount") if price_list else None
            currency = price_list[0].get("currency", "USD") if price_list else "USD"
            refundable = (rate.get("cancellationPolicies") or {}).get("refundableTag", "")
            taxes = (rate.get("retailRate") or {}).get("taxesAndFees") or []
            taxes_included = any(t.get("included") for t in taxes) if taxes else False

            cancel_policies = rate.get("cancellationPolicies") or {}
            cancel_infos = cancel_policies.get("cancelPolicyInfos") or []
            cancel_deadline = cancel_infos[0].get("cancelTime") if cancel_infos else None

            flat_rates.append({
                "offer_id": offer_id,
                "name": rate.get("name") or "Room",
                "board_name": rate.get("boardName") or "",
                "price": price,
                "currency": currency,
                "refundable": refundable,
                "taxes_included": taxes_included,
                "cancel_deadline": cancel_deadline,
                "mapped_room_id": rate.get("mappedRoomId"),
            })

    return flat_rates


def _normalize_room_name(value: str | None) -> str:
    return " ".join((value or "").lower().split())


def _room_photo_url(room: dict[str, Any]) -> str | None:
    for photo in room.get("photos") or []:
        if not isinstance(photo, dict):
            continue
        for key in ("hd_url", "url", "failoverPhoto"):
            value = photo.get(key)
            if isinstance(value, str) and value:
                return value
    return None


def _room_photo_urls(room: dict[str, Any]) -> list[str]:
    urls: list[str] = []
    seen: set[str] = set()
    for photo in room.get("photos") or []:
        if not isinstance(photo, dict):
            continue
        for key in ("hd_url", "url", "failoverPhoto"):
            value = photo.get(key)
            if isinstance(value, str) and value and value not in seen:
                seen.add(value)
                urls.append(value)
    return urls


def _enrich_rates_with_room_images(
    rates: list[dict[str, Any]],
    hotel_details: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    if not hotel_details:
        return rates

    rooms = hotel_details.get("rooms") or []
    if not isinstance(rooms, list):
        return rates

    room_by_id: dict[str, dict[str, Any]] = {}
    room_by_name: dict[str, dict[str, Any]] = {}
    for room in rooms:
        if not isinstance(room, dict):
            continue
        room_id = room.get("id")
        if room_id is not None:
            room_by_id[str(room_id)] = room
        normalized_name = _normalize_room_name(room.get("roomName"))
        if normalized_name:
            room_by_name[normalized_name] = room

    enriched: list[dict[str, Any]] = []
    for rate in rates:
        room = None
        mapped_room_id = rate.get("mapped_room_id")
        if mapped_room_id is not None:
            room = room_by_id.get(str(mapped_room_id))
        if room is None:
            room = room_by_name.get(_normalize_room_name(rate.get("name")))

        image_url = _room_photo_url(room or {})
        image_urls = _room_photo_urls(room or {})
        enriched.append({
            **rate,
            "image_url": image_url,
            "image_urls": image_urls,
        })

    return enriched


def _compact_available_hotels_from_rates(result: Any) -> list[dict[str, Any]]:
    if not isinstance(result, dict):
        return []

    data = result.get("data") or []
    if not isinstance(data, list):
        return []

    metadata_by_id = {
        hotel_id: hotel
        for hotel in result.get("hotels", [])
        if isinstance(hotel, dict) and (hotel_id := _hotel_identity(hotel))
    }

    compacted: list[dict[str, Any]] = []
    for hotel_data in data:
        if not isinstance(hotel_data, dict):
            continue

        rates = _flatten_room_rates(hotel_data)
        if not rates:
            continue

        hotel_id = _hotel_identity(hotel_data)
        metadata = metadata_by_id.get(hotel_id or "", {})
        source = {**metadata, **hotel_data}
        image_urls = (
            source.get("image_urls")
            or source.get("images")
            or source.get("hotelImages")
            or source.get("photos")
            or []
        )
        if isinstance(image_urls, list):
            image_urls = [
                image.get("url") if isinstance(image, dict) else image
                for image in image_urls
            ]
        else:
            image_urls = []

        compacted.append({
            "hotel_id": hotel_id,
            "name": (
                source.get("name")
                or source.get("hotelName")
                or source.get("hotel_name")
                or "Hotel"
            ),
            "address": source.get("address") or source.get("formattedAddress"),
            "city": source.get("city"),
            "country": source.get("country"),
            "stars": source.get("stars") or source.get("starRating"),
            "rating": source.get("rating"),
            "description": source.get("description") or source.get("hotelDescription"),
            "image_url": (
                source.get("image_url")
                or source.get("main_photo")
                or source.get("thumbnail")
                or (image_urls[0] if image_urls else None)
            ),
            "image_urls": image_urls,
            "rates": rates[:3],
        })

    return [hotel for hotel in compacted if hotel.get("hotel_id")]


def _selected_hotel_from_state(state: BookingState) -> dict[str, Any]:
    selected_id = state.get("selected_hotel_id")
    if not selected_id:
        return {}
    return next(
        (
            hotel
            for hotel in state.get("hotels", [])
            if hotel.get("hotel_id") == selected_id
        ),
        {},
    )


# ── Orchestrator ──────────────────────────────────────────────────────────────

async def orchestrate_travel(state: BookingState, config: RunnableConfig):
    deps = _deps(config)
    user_message = state.get("user_message", "")
    response_language = detect_language(user_message)
    conversation_id = _conversation_id(config)

    user_id = _user_id(config)

    async def _empty_profile():
        return {}

    memory_context, booking_state, user_profile = await asyncio.gather(
        deps.conversation_memory.get_recent(conversation_id),
        deps.conversation_memory.get_booking_state(conversation_id),
        deps.conversation_memory.get_user_profile(user_id) if user_id else _empty_profile(),
    )

    pending_service_choice = state.get("service_selection_required") or booking_state.get("service_selection_required")
    selected_service = _normalize_service_choice(user_message)
    if pending_service_choice:
        if selected_service == "hotels":
            return {
                "intent": "hotel_search",
                "agent": "hotel_booking_agent",
                "requested_services": ["hotels"],
                "service_selection_required": False,
                "response_language": response_language,
                "memory_context": memory_context,
                "retrieval_context": [],
                "mcp_tools": [],
                "response": None,
            }
        return {
            "intent": "clarification_needed",
            "agent": "general_travel_assistant",
            "requested_services": state.get("requested_services", []),
            "service_selection_required": True,
            "response_language": response_language,
            "memory_context": memory_context,
            "retrieval_context": [],
            "mcp_tools": [],
            "next_action": "ask_clarification",
            "response": _service_choice_prompt(response_language, state.get("city_name")),
        }

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

    # Merge user profile into guest fields (profile wins as baseline, state overrides).
    profile_first = user_profile.get("first_name")
    profile_last = user_profile.get("last_name")
    profile_email = user_profile.get("email")

    # Build summary of confirmed fields so the orchestrator never re-asks.
    known_fields: dict[str, Any] = {
        k: v
        for k, v in {
            "city_name": state.get("city_name") or booking_state.get("city_name"),
            "country_code": state.get("country_code") or booking_state.get("country_code"),
            "checkin_date": state.get("checkin_date") or booking_state.get("checkin_date"),
            "checkout_date": state.get("checkout_date") or booking_state.get("checkout_date"),
            "guests": state.get("guests") or booking_state.get("guests"),
            "guest_first_name": state.get("guest_first_name") or profile_first,
            "guest_last_name": state.get("guest_last_name") or profile_last,
            "guest_email": state.get("guest_email") or profile_email,
        }.items()
        if v is not None
    }

    # Tell orchestrator exactly which list is on screen RIGHT NOW (exclusive).
    # Base it on the previous next_action so there's no ambiguity when multiple
    # lists exist in state (e.g. hotels + hotel_rates are both populated but only
    # one screen is visible to the user).
    prev_action = state.get("next_action")
    context_state: dict[str, Any] = {}
    if prev_action == "show_hotel_rates" and state.get("hotel_rates"):
        context_state["hotel_rates_displayed"] = len(state["hotel_rates"])
        context_state["previous_next_action"] = prev_action
    elif prev_action == "show_hotels" and state.get("hotels"):
        context_state["hotels_displayed"] = len(state["hotels"])
        context_state["previous_next_action"] = prev_action
    elif state.get("hotel_rates"):
        context_state["hotel_rates_displayed"] = len(state["hotel_rates"])
        context_state["previous_next_action"] = prev_action
    elif state.get("hotels"):
        context_state["hotels_displayed"] = len(state["hotels"])
        context_state["previous_next_action"] = prev_action

    structured_router = deps.llm.with_structured_output(TravelOrchestratorDecision)
    try:
        extracted = await structured_router.ainvoke(
            [
                SystemMessage(
                    content=(
                        f"{get_prompt('ttrip_travel_orchestrator')}\n\n"
                        "Runtime context available to the orchestrator:\n"
                        f"- current_date: {date.today().isoformat()}\n"
                        f"- Already known booking fields: {json.dumps(known_fields, ensure_ascii=False) if known_fields else 'None'}\n"
                        f"- Conversation screen state: {json.dumps(context_state, ensure_ascii=False) if context_state else 'None'}\n"
                        f"- Recent conversation memory: {_compact_context(memory_context)}\n"
                        f"- Retrieved ttrip knowledge: {_compact_context(retrieval_context)}\n"
                        f"- Available LiteAPI MCP tools: {', '.join(mcp_tools) or 'None'}\n"
                        f"- Latest user message language: {response_language}\n"
                        "IMPORTANT: Fields listed in 'Already known booking fields' are confirmed. "
                        "Do NOT return None for those — carry them forward exactly as-is unless the "
                        "user explicitly changes them. Only extract what is new in the latest message."
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

    requested_services = extracted.requested_services or state.get("requested_services", [])
    explicit_service_request = _is_explicit_service_request(user_message)
    generic_trip_request = _is_generic_trip_request(user_message)
    destination_hint = extracted.city_name or state.get("city_name")

    if (
        generic_trip_request
        and destination_hint
        and not explicit_service_request
        and not requested_services
    ):
        return {
            "intent": "clarification_needed",
            "agent": "general_travel_assistant",
            "city_name": _keep(extracted.city_name, state.get("city_name") or booking_state.get("city_name")),
            "country_code": _keep(extracted.country_code, state.get("country_code") or booking_state.get("country_code")),
            "requested_services": [],
            "service_selection_required": True,
            "next_action": "ask_clarification",
            "response_language": response_language,
            "memory_context": memory_context,
            "retrieval_context": retrieval_context,
            "mcp_tools": mcp_tools,
            "response": _service_choice_prompt(response_language, destination_hint),
        }

    return {
        "intent": extracted.intent,
        "agent": extracted.agent,
        "city_name": _keep(extracted.city_name, state.get("city_name") or booking_state.get("city_name")),
        "country_code": _keep(extracted.country_code, state.get("country_code") or booking_state.get("country_code")),
        "checkin_date": _keep(extracted.checkin_date, state.get("checkin_date") or booking_state.get("checkin_date")),
        "checkout_date": _keep(extracted.checkout_date, state.get("checkout_date") or booking_state.get("checkout_date")),
        "guests": _keep(extracted.guests, state.get("guests") or booking_state.get("guests")),
        "selected_item_index": extracted.selected_item_index,
        "guest_first_name": _keep(extracted.guest_first_name, state.get("guest_first_name") or profile_first),
        "guest_last_name": _keep(extracted.guest_last_name, state.get("guest_last_name") or profile_last),
        "guest_email": _keep(extracted.guest_email, state.get("guest_email") or profile_email),
        "requested_services": requested_services,
        "service_selection_required": False,
        "next_action": None,
        "response_language": response_language,
        "memory_context": memory_context,
        "retrieval_context": retrieval_context,
        "mcp_tools": mcp_tools,
        "response": None,
    }


# ── Hotel search flow ─────────────────────────────────────────────────────────

async def hotel_agent_node(state: BookingState, config: RunnableConfig):
    if state.get("selected_hotel_id") and state.get("checkin_date") and state.get("checkout_date"):
        return {
            "next_action": "search_hotel_rates",
            "agent": "hotel_booking_agent",
        }

    missing = []
    if not state.get("city_name"):
        missing.append("destination city")
    if not state.get("country_code"):
        missing.append("country")
    if not state.get("checkin_date"):
        missing.append("check-in date")
    if not state.get("checkout_date"):
        missing.append("check-out date")

    if missing:
        known = {
            k: v
            for k, v in {
                "city": state.get("city_name"),
                "country_code": state.get("country_code"),
                "checkin": state.get("checkin_date"),
                "checkout": state.get("checkout_date"),
                "guests": state.get("guests"),
            }.items()
            if v is not None
        }
        result = await _agent_message(
            state,
            config,
            task=(
                f"The hotel search is missing: {', '.join(missing)}. "
                f"Already confirmed: {json.dumps(known) if known else 'nothing yet'}. "
                "Ask for the missing information before searching availability. "
                "If both check-in and check-out dates are missing, ask for both in one natural question. "
                "No bullet lists."
            ),
            missing=missing,
        )
        return {
            **result,
            "next_action": "error" if result.get("error_message") else "ask_clarification",
            "agent": "hotel_booking_agent",
        }

    return {
        "next_action": "search_hotels",
        "agent": "hotel_booking_agent",
    }


async def search_hotels(state: BookingState, config: RunnableConfig):
    deps = _deps(config)
    country_code = state.get("country_code")
    city_name = state.get("city_name")
    checkin = state.get("checkin_date")
    checkout = state.get("checkout_date")
    guests = state.get("guests") or 1
    response_language = state.get("response_language", "en")

    missing = [
        label
        for label, value in [
            ("destination city", city_name),
            ("country", country_code),
            ("check-in date", checkin),
            ("check-out date", checkout),
        ]
        if not value
    ]
    if missing:
        result = await _agent_message(
            state,
            config,
            task=(
                "Availability search needs destination and stay dates. "
                f"Ask the user for: {', '.join(missing)}."
            ),
            missing=missing,
        )
        return {
            **result,
            "next_action": "ask_clarification",
            "missing_fields": missing,
            "agent": "hotel_booking_agent",
        }

    try:
        result = await deps.hotels.search_rates({
            "aiSearch": f"Hotels in {city_name}, {country_code}",
            "occupancies": [{"adults": guests}],
            "currency": "USD",
            "guestNationality": "US",
            "checkin": checkin,
            "checkout": checkout,
            "roomMapping": True,
            "maxRatesPerHotel": 1,
            "includeHotelData": True,
        })
        hotels = _compact_available_hotels_from_rates(result)
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

    lines += ["", "Reply with the number of the hotel you'd like to book."]

    return {
        "response": "\n".join(lines),
        "next_action": "show_hotels",
        "agent": "hotel_booking_agent",
    }


# ── Hotel selection → rates → prebook ────────────────────────────────────────

async def hotel_selection_node(state: BookingState, config: RunnableConfig):
    """User picked a hotel from the list. Extract hotel_id and route to rate search."""
    hotels = state.get("hotels", [])
    selected_index = state.get("selected_item_index")
    response_language = state.get("response_language", "en")

    if not hotels or not selected_index:
        result = await _agent_message(
            state, config,
            task="Ask the user which hotel number they'd like from the list shown.",
        )
        return {**result, "next_action": "ask_clarification", "agent": "hotel_booking_agent"}

    idx = selected_index - 1
    if idx < 0 or idx >= len(hotels):
        result = await _agent_message(
            state, config,
            task=f"The user chose option {selected_index} but only {len(hotels)} hotels were shown. Ask them to pick a valid number.",
        )
        return {**result, "next_action": "ask_clarification", "agent": "hotel_booking_agent"}

    hotel = hotels[idx]
    hotel_id = hotel.get("hotel_id")
    missing_dates = [
        label
        for label, value in [
            ("check-in date", state.get("checkin_date")),
            ("check-out date", state.get("checkout_date")),
        ]
        if not value
    ]

    if missing_dates:
        result = await _agent_message(
            state,
            config,
            task=(
                f"The user selected {hotel.get('name') or 'a hotel'}, but room rates need "
                f"{' and '.join(missing_dates)}. Ask for the missing date information before "
                "searching room rates. Keep it to one natural question."
            ),
            missing=missing_dates,
        )
        return {
            **result,
            "selected_hotel_id": hotel_id,
            "missing_fields": missing_dates,
            "next_action": "ask_clarification",
            "agent": "hotel_booking_agent",
        }

    return {
        "selected_hotel_id": hotel_id,
        "hotel_rates": hotel.get("rates", []) if isinstance(hotel.get("rates"), list) else [],
        "next_action": "search_hotel_rates",
        "agent": "hotel_booking_agent",
        "response": None,
    }


async def search_hotel_rates_node(state: BookingState, config: RunnableConfig):
    """Fetch room rates for the selected hotel."""
    deps = _deps(config)
    hotel_id = state.get("selected_hotel_id")
    checkin = state.get("checkin_date")
    checkout = state.get("checkout_date")
    guests = state.get("guests") or 1
    response_language = state.get("response_language", "en")

    missing_dates = [
        label
        for label, value in [
            ("check-in date", checkin),
            ("check-out date", checkout),
        ]
        if not value
    ]
    if missing_dates:
        result = await _agent_message(
            state,
            config,
            task=(
                "Room rates cannot be searched without stay dates. "
                f"Ask the user for {' and '.join(missing_dates)} before continuing."
            ),
            missing=missing_dates,
        )
        return {
            **result,
            "next_action": "ask_clarification",
            "missing_fields": missing_dates,
            "agent": "hotel_booking_agent",
        }

    try:
        result = await deps.hotels.search_rates({
            "hotelIds": [hotel_id],
            "occupancies": [{"adults": guests}],
            "currency": "USD",
            "guestNationality": "US",
            "checkin": checkin,
            "checkout": checkout,
            "roomMapping": True,
        })
    except Exception as exc:
        return {
            "next_action": "error",
            "error_message": str(exc),
            "response": hotel_search_error(response_language),
        }

    # LiteAPI rates response: data[0].roomTypes[].{ offerId, rates[] }
    data = result.get("data") or []
    hotel_data = data[0] if (isinstance(data, list) and data) else {}
    flat_rates = _flatten_room_rates(hotel_data)

    hotel_details: dict[str, Any] | None = None
    try:
        details_result = await deps.hotels.get_details(hotel_id, timeout_seconds=8)
        details_data = details_result.get("data", details_result)
        hotel_details = details_data if isinstance(details_data, dict) else None
    except Exception:
        hotel_details = None

    flat_rates = _enrich_rates_with_room_images(flat_rates, hotel_details)
    if not flat_rates:
        selected_hotel = _selected_hotel_from_state(state)
        fallback_rates = selected_hotel.get("rates") if isinstance(selected_hotel.get("rates"), list) else []
        flat_rates = fallback_rates

    if not flat_rates:
        # No rates available — maybe no dates, inform user
        return {
            "next_action": "error",
            "response": (
                "I couldn't find available rooms for those dates. "
                "Try different check-in and check-out dates."
            ),
            "hotel_rates": [],
        }

    return {
        "next_action": "show_hotel_rates",
        "hotel_rates": flat_rates,
        "agent": "hotel_booking_agent",
    }


async def generate_hotel_rates_response(state: BookingState):
    """Format available room options as a numbered list."""
    rates = state.get("hotel_rates", [])
    hotels = state.get("hotels", [])
    selected_id = state.get("selected_hotel_id")

    hotel_name = next(
        (h.get("name", "") for h in hotels if h.get("hotel_id") == selected_id),
        "",
    )

    if hotel_name:
        intro = f"I found {len(rates)} available room option{'s' if len(rates) != 1 else ''} at **{hotel_name}**."
    else:
        intro = f"I found {len(rates)} available room option{'s' if len(rates) != 1 else ''}."
    lines = [intro, "Select a room below to continue."]

    return {
        "response": "\n".join(lines),
        "next_action": "show_hotel_rates",
        "agent": "hotel_booking_agent",
        "hotel_rates": rates,
        "hotel_images": next(
            (h.get("image_urls", []) for h in hotels if h.get("hotel_id") == selected_id),
            [],
        ),
    }


async def hotel_rate_selection_node(state: BookingState, config: RunnableConfig):
    """User picked a room rate. Extract the offer_id and route to prebook."""
    hotel_rates = state.get("hotel_rates", [])
    selected_index = state.get("selected_item_index")

    if not hotel_rates or not selected_index:
        result = await _agent_message(
            state, config,
            task="Ask the user which room option number they'd like from the list shown.",
        )
        return {**result, "next_action": "ask_clarification", "agent": "hotel_booking_agent"}

    idx = selected_index - 1
    if idx < 0 or idx >= len(hotel_rates):
        result = await _agent_message(
            state, config,
            task=f"Only {len(hotel_rates)} room options available. Ask user to pick a valid number.",
        )
        return {**result, "next_action": "ask_clarification", "agent": "hotel_booking_agent"}

    offer_id = hotel_rates[idx].get("offer_id")
    return {
        "selected_hotel_offer_id": offer_id,
        "next_action": "prebook_hotel",
        "agent": "hotel_booking_agent",
        "response": None,
    }


async def prebook_hotel_node(state: BookingState, config: RunnableConfig):
    """Call /rates/prebook and return Stripe SDK keys to the frontend."""
    deps = _deps(config)
    offer_id = state.get("selected_hotel_offer_id")
    response_language = state.get("response_language", "en")
    conversation_id = _conversation_id(config)

    if not offer_id:
        result = await _agent_message(
            state, config,
            task="Ask the user which room they'd like to select from the options shown.",
        )
        return {**result, "next_action": "ask_clarification", "agent": "hotel_booking_agent"}

    try:
        result = await deps.hotels.prebook(offer_id)
    except Exception as exc:
        return {
            "next_action": "error",
            "error_message": str(exc),
            "response": hotel_search_error(response_language),
            "agent": "hotel_booking_agent",
        }

    data = result.get("data", result)
    prebook_id = data.get("prebookId")
    transaction_id = data.get("transactionId")
    secret_key = data.get("secretKey")
    public_key = "sandbox" if settings.LITEAPI_ENV == "sandbox" else "live"

    # Persist in Redis so _handle_payment_continuation can finalize the booking.
    # Pre-populate guest details from state/profile so we don't have to re-ask after payment.
    booking_state = await deps.conversation_memory.get_booking_state(conversation_id)
    booking_state.update({
        "payment_prebook_id": prebook_id,
        "payment_transaction_id": transaction_id,
        "booking_type": "hotel",
        "guest_first_name": state.get("guest_first_name") or booking_state.get("guest_first_name"),
        "guest_last_name": state.get("guest_last_name") or booking_state.get("guest_last_name"),
        "guest_email": state.get("guest_email") or booking_state.get("guest_email"),
    })
    # Remove None values so missing details still get collected
    booking_state = {k: v for k, v in booking_state.items() if v is not None}
    await deps.conversation_memory.set_booking_state(conversation_id, booking_state)

    return {
        "next_action": "payment_required",
        "agent": "hotel_booking_agent",
        "booking_status": "payment_required",
        "booking_type": "hotel",
        "payment_prebook_id": prebook_id,
        "payment_transaction_id": transaction_id,
        "payment_sdk_secret_key": secret_key,
        "payment_sdk_public_key": public_key,
        "response": (
            "I've reserved your room! Please complete the payment below to confirm your booking. "
            "After payment I'll ask for your name and email to finalise."
        ),
    }


# ── Other agents ──────────────────────────────────────────────────────────────

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
    if not state.get("city_name"):
        missing.append("destination city and country")
    if not state.get("checkin_date") or not state.get("checkout_date"):
        missing.append("hotel dates")
    if not state.get("guests"):
        missing.append("guest count")

    result = await _agent_message(
        state,
        config,
        task=(
            "Handle a combined travel planning request. Use the destination and requested "
            "services already provided. Ask naturally for the next missing information. "
            "Keep the workflow hotel-only and collect hotel destination, dates, and guest count."
        ),
        missing=missing,
    )
    return {
        **result,
        "next_action": "error" if result.get("error_message") else (
            "ask_clarification" if missing else "route_to_package"
        ),
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
