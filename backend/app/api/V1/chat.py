import re
from typing import Any

from fastapi import APIRouter, HTTPException, Request

from app.agents.booking.dependencies import BookingDeps
from app.core.logging import logger
from app.core.metrics import agent_requests_total
from app.db.booking_repository import BookingDBRepository
from app.db.database import AsyncSessionLocal
from app.db.user_profile_repository import UserProfileRepository
from app.schemas.base import success_response
from app.schemas.chat import ChatRequest

router = APIRouter(prefix="/chat", tags=["Chat"])


async def _persist_booking(
    user_id: str | None,
    booking_type: str,
    provider_booking_id: str,
    provider_reference: str | None,
    status: str,
    total_charged: float | None,
    currency: str | None,
    payload: dict[str, Any],
) -> None:
    if not user_id or not provider_booking_id or provider_booking_id == "N/A":
        return
    try:
        async with AsyncSessionLocal() as db:
            repo = BookingDBRepository(db)
            await repo.store({
                "clerk_user_id": user_id,
                "booking_type": booking_type.upper(),
                "provider_booking_id": provider_booking_id,
                "provider_reference": provider_reference,
                "status": status.upper(),
                "total_charged": total_charged,
                "currency": currency,
                "provider_payload": payload,
            })
    except Exception as exc:
        logger.warning("booking_persist_failed user=%s type=%s err=%s", user_id, booking_type, exc)

INTERNAL_PAYMENT_VERIFIED_MESSAGE = "__internal_payment_verified__"

_EMAIL_RE = re.compile(r'\b[\w.+\-]+@[\w.\-]+\.[a-zA-Z]{2,}\b')

_BOOKING_MEMORY_FIELDS = {
    "intent",
    "agent",
    "next_action",
    "requested_services",
    "city_name",
    "country_code",
    "checkin_date",
    "checkout_date",
    "guests",
    "rooms",
    "selected_hotel_id",
    "selected_hotel_offer_id",
    "booking_status",
    "booking_type",
    "guest_first_name",
    "guest_last_name",
    "guest_email",
}


def _is_simple_greeting(message: str) -> bool:
    normalized = re.sub(r"[^\w\s\u0600-\u06ff]", "", message.lower()).strip()
    if not normalized:
        return False
    return normalized in {
        "hi",
        "hello",
        "hey",
        "hello there",
        "hi there",
        "good morning",
        "good afternoon",
        "good evening",
        "bonjour",
        "salut",
        "salam",
        "السلام عليكم",
        "مرحبا",
        "أهلا",
    }


async def _handle_simple_greeting(payload: ChatRequest, deps: BookingDeps) -> dict:
    message = "Hi. I can help you find and book a hotel. Which city are you staying in?"
    await deps.conversation_memory.append_interaction(
        payload.conversation_id,
        user_message=payload.message,
        assistant_message=message,
        metadata={
            "intent": "general_travel_question",
            "agent": "general_travel_assistant",
            "next_action": "answer_general",
        },
    )
    return success_response(
        message="chat routed",
        data={
            "conversation_id": payload.conversation_id,
            "message": message,
            "intent": "general_travel_question",
            "agent": "general_travel_assistant",
            "next_action": "answer_general",
            "metadata": {},
        },
    )


async def _persist_conversation_booking_memory(
    conversation_id: str,
    deps: BookingDeps,
    result: dict[str, Any],
) -> dict[str, Any]:
    booking_state = await deps.conversation_memory.get_booking_state(conversation_id)
    for field in _BOOKING_MEMORY_FIELDS:
        value = result.get(field)
        if value is not None and value != []:
            booking_state[field] = value

    if result.get("payment_prebook_id"):
        booking_state["payment_prebook_id"] = result["payment_prebook_id"]
    if result.get("payment_transaction_id"):
        booking_state["payment_transaction_id"] = result["payment_transaction_id"]
    if result.get("payment_prebook_id") or result.get("payment_transaction_id"):
        booking_state["payment_status"] = "payment_required"

    await deps.conversation_memory.set_booking_state(conversation_id, booking_state)
    return booking_state


async def _sync_user_profile_from_payload(
    request: Request,
    payload: ChatRequest,
) -> None:
    if not payload.user_id or not payload.user_profile:
        return

    deps: BookingDeps = request.app.state.booking_deps
    sanitized = deps.conversation_memory.sanitize_user_profile(
        {
            "user_id": payload.user_id,
            **payload.user_profile,
        }
    )
    if len(sanitized) <= 1:
        return

    async with AsyncSessionLocal() as db:
        repo = UserProfileRepository(db)
        await repo.upsert_by_clerk_user_id(
            payload.user_id,
            {k: v for k, v in sanitized.items() if k != "user_id"},
        )
    await deps.conversation_memory.set_user_profile(payload.user_id, sanitized)


async def _load_user_profile(
    request: Request,
    user_id: str | None,
) -> dict[str, Any]:
    if not user_id:
        return {}

    deps: BookingDeps = request.app.state.booking_deps
    profile = await deps.conversation_memory.get_user_profile(user_id)
    if profile:
        return profile

    async with AsyncSessionLocal() as db:
        repo = UserProfileRepository(db)
        entity = await repo.get_by_clerk_user_id(user_id)

    if entity is None:
        return {}

    profile = {
        "user_id": entity.clerk_user_id,
        "first_name": entity.first_name,
        "last_name": entity.last_name,
        "email": entity.email,
        "birthday": entity.birthday,
        "nationality": entity.nationality,
        "phone": entity.phone,
        "passport_number": entity.passport_number,
        "passport_expiry": entity.passport_expiry,
        "home_country": entity.home_country,
    }
    await deps.conversation_memory.set_user_profile(user_id, profile)
    return profile


def _extract_guest_details(message: str) -> dict:
    """Best-effort extraction of first name, last name, email from a free-text message."""
    email_match = _EMAIL_RE.search(message)
    email = email_match.group(0) if email_match else None
    # Remove email and punctuation to get the name
    name_part = _EMAIL_RE.sub("", message).strip().strip(",.;-").strip()
    parts = name_part.split()
    first_name = parts[0].capitalize() if parts else None
    last_name = " ".join(p.capitalize() for p in parts[1:]) if len(parts) > 1 else None
    return {"first_name": first_name, "last_name": last_name, "email": email}


async def _handle_guest_details(
    payload: ChatRequest,
    deps: BookingDeps,
    booking_state: dict,
) -> dict:
    """After hotel payment, collect guest name/email then call book without touching the graph."""
    conversation_id = payload.conversation_id
    extracted = _extract_guest_details(payload.message)

    if extracted["first_name"] and not booking_state.get("guest_first_name"):
        booking_state["guest_first_name"] = extracted["first_name"]
    if extracted["last_name"] and not booking_state.get("guest_last_name"):
        booking_state["guest_last_name"] = extracted["last_name"]
    if extracted["email"] and not booking_state.get("guest_email"):
        booking_state["guest_email"] = extracted["email"]

    await deps.conversation_memory.set_booking_state(conversation_id, booking_state)

    guest_first = booking_state.get("guest_first_name")
    guest_last = booking_state.get("guest_last_name")
    guest_email = booking_state.get("guest_email")

    if not all([guest_first, guest_last, guest_email]):
        missing = [
            f for f, v in [
                ("first name", guest_first),
                ("last name", guest_last),
                ("email address", guest_email),
            ] if not v
        ]
        return success_response(
            message="chat routed",
            data={
                "conversation_id": conversation_id,
                "message": (
                    f"Almost there! Could you also share your {' and '.join(missing)}?"
                ),
                "intent": "hotel_booking",
                "agent": "hotel_booking_agent",
                "next_action": "guest_details_required",
                "metadata": {"booking_status": "guest_details_required"},
            },
        )

    prebook_id = booking_state.get("payment_prebook_id")
    transaction_id = booking_state.get("payment_transaction_id")

    try:
        result = await deps.hotels.book({
            "prebookId": prebook_id,
            "holder": {
                "firstName": guest_first,
                "lastName": guest_last,
                "email": guest_email,
            },
            "payment": {
                "method": "TRANSACTION_ID",
                "transactionId": transaction_id,
            },
            "guests": [{
                "occupancyNumber": 1,
                "firstName": guest_first,
                "lastName": guest_last,
                "email": guest_email,
            }],
        })

        booking_state["booking_status"] = "confirmed"
        await deps.conversation_memory.set_booking_state(conversation_id, booking_state)

        booking_data = result.get("data", result)
        booking_id = booking_data.get("bookingId") or booking_data.get("booking_id", "N/A")
        confirmation_code = booking_data.get("hotelConfirmationCode", "N/A")

        await _persist_booking(
            user_id=payload.user_id,
            booking_type="HOTEL",
            provider_booking_id=str(booking_id),
            provider_reference=str(confirmation_code) if confirmation_code != "N/A" else None,
            status="CONFIRMED",
            total_charged=booking_data.get("totalCharged") or booking_data.get("total_charged"),
            currency=booking_data.get("currency"),
            payload={**booking_data, "checkin": booking_state.get("checkin_date"), "checkout": booking_state.get("checkout_date")},
        )

        return success_response(
            message="chat routed",
            data={
                "conversation_id": conversation_id,
                "message": (
                    f"Your hotel is confirmed, {guest_first}! 🎉\n"
                    f"Booking ID: **{booking_id}**\n"
                    f"Confirmation code: **{confirmation_code}**"
                ),
                "intent": "hotel_booking",
                "agent": "hotel_booking_agent",
                "next_action": "booking_confirmed",
                "metadata": {
                    "booking_status": "confirmed",
                    "state": {
                        "step": "booking_confirmed",
                        "booking_id": booking_id,
                        "confirmation_code": confirmation_code,
                        "booking_type": "hotel",
                    },
                },
            },
        )

    except Exception as exc:
        return success_response(
            message="chat routed",
            data={
                "conversation_id": conversation_id,
                "message": (
                    f"Payment was received but the booking could not be finalised: {exc}. "
                    "Please contact support with your transaction details."
                ),
                "intent": "hotel_booking",
                "agent": "hotel_booking_agent",
                "next_action": "error",
                "metadata": {"booking_status": "booking_failed", "error_message": str(exc)},
            },
        )


async def _handle_payment_continuation(
    payload: ChatRequest,
    deps: BookingDeps,
) -> dict:
    """Called when the frontend sends the payment-verified sentinel."""
    conversation_id = payload.conversation_id
    booking_state = await deps.conversation_memory.get_booking_state(conversation_id)

    booking_state["payment_status"] = "completed"
    if payload.payment_transaction_id:
        booking_state["payment_transaction_id"] = payload.payment_transaction_id
    if payload.payment_prebook_id:
        booking_state["payment_prebook_id"] = payload.payment_prebook_id
    await deps.conversation_memory.set_booking_state(conversation_id, booking_state)

    prebook_id = booking_state.get("payment_prebook_id") or payload.payment_prebook_id
    transaction_id = (
        booking_state.get("payment_transaction_id") or payload.payment_transaction_id
    )
    booking_type = booking_state.get("booking_type", "hotel")

    guest_first = booking_state.get("guest_first_name")
    guest_last = booking_state.get("guest_last_name")
    guest_email = booking_state.get("guest_email")

    if booking_type != "hotel":
        booking_type = "hotel"
        booking_state["booking_type"] = "hotel"

    # Collect guest details if missing, then book.
    if not all([guest_first, guest_last, guest_email]):
        booking_state["booking_status"] = "guest_details_required"
        await deps.conversation_memory.set_booking_state(conversation_id, booking_state)
        return success_response(
            message="chat routed",
            data={
                "conversation_id": conversation_id,
                "message": (
                    "Payment successful! To finalise your booking, please share "
                    "the main guest's first name, last name, and email address."
                ),
                "intent": "hotel_booking",
                "agent": "hotel_booking_agent",
                "next_action": "guest_details_required",
                "metadata": {
                    "booking_status": "guest_details_required",
                    "state": {
                        "step": "guest_details_required",
                        "payment_status": "completed",
                        "prebook_id": prebook_id,
                        "transaction_id": transaction_id,
                    },
                },
            },
        )

    try:
        result = await deps.hotels.book({
            "prebookId": prebook_id,
            "holder": {
                "firstName": guest_first,
                "lastName": guest_last,
                "email": guest_email,
            },
            "payment": {
                "method": "TRANSACTION_ID",
                "transactionId": transaction_id,
            },
            "guests": [{
                "occupancyNumber": 1,
                "firstName": guest_first,
                "lastName": guest_last,
                "email": guest_email,
            }],
        })

        booking_state["booking_status"] = "confirmed"
        await deps.conversation_memory.set_booking_state(conversation_id, booking_state)

        booking_data = result.get("data", result)
        if isinstance(booking_data, list) and booking_data:
            booking_data = booking_data[0]

        booking_id = booking_data.get("bookingId") or booking_data.get("booking_id", "N/A")

        confirmation_code = booking_data.get("hotelConfirmationCode", "N/A")
        confirm_message = (
            f"Your hotel is confirmed! 🎉\n"
            f"Booking ID: **{booking_id}** | Confirmation: **{confirmation_code}**"
        )
        intent_out, agent_out = "hotel_booking", "hotel_booking_agent"
        await _persist_booking(
            user_id=payload.user_id,
            booking_type="HOTEL",
            provider_booking_id=str(booking_id),
            provider_reference=str(confirmation_code) if confirmation_code != "N/A" else None,
            status="CONFIRMED",
            total_charged=booking_data.get("totalCharged") or booking_data.get("total_charged"),
            currency=booking_data.get("currency"),
            payload={**booking_data, "checkin": booking_state.get("checkin_date"), "checkout": booking_state.get("checkout_date")},
        )

        return success_response(
            message="chat routed",
            data={
                "conversation_id": conversation_id,
                "message": confirm_message,
                "intent": intent_out,
                "agent": agent_out,
                "next_action": "booking_confirmed",
                "metadata": {
                    "booking_status": "confirmed",
                    "state": {
                        "step": "booking_confirmed",
                        "booking_id": booking_id,
                        "confirmation_code": confirmation_code,
                        "booking_type": booking_type,
                    },
                },
            },
        )

    except Exception as exc:
        return success_response(
            message="chat routed",
            data={
                "conversation_id": conversation_id,
                "message": (
                    f"Payment was received but the booking could not be finalised: {exc}. "
                    "Please contact support with your transaction details."
                ),
                "intent": f"{booking_type}_booking",
                "agent": f"{booking_type}_booking_agent",
                "next_action": "error",
                "metadata": {"booking_status": "booking_failed", "error_message": str(exc)},
            },
        )


@router.post("")
async def chat(payload: ChatRequest, request: Request):
    deps: BookingDeps = request.app.state.booking_deps
    await _sync_user_profile_from_payload(request, payload)
    await _load_user_profile(request, payload.user_id)

    # ── Payment sentinel ───────────────────────────────────────────────────
    if payload.payment_completed and payload.message == INTERNAL_PAYMENT_VERIFIED_MESSAGE:
        return await _handle_payment_continuation(payload, deps)

    # ── Guest details collection (after hotel payment, before graph) ────────
    # When booking_status == "guest_details_required" we must NOT run the main
    # graph because the reply is booking data, not a new search request.
    booking_state = await deps.conversation_memory.get_booking_state(payload.conversation_id)
    if booking_state.get("booking_status") == "guest_details_required":
        return await _handle_guest_details(payload, deps, booking_state)

    # ── Fast path for greetings ─────────────────────────────────────────────
    # Avoid Elasticsearch, MCP discovery, and two LLM calls for a static hello.
    if _is_simple_greeting(payload.message):
        return await _handle_simple_greeting(payload, deps)

    # ── Normal graph invocation ────────────────────────────────────────────
    try:
        graph = request.app.state.booking_graph
        thread_id = f"conversation:{payload.conversation_id}"
        result = await graph.ainvoke(
            {
                "user_message": payload.message,
                "messages": [{"role": "user", "content": payload.message}],
            },
            config={
                "configurable": {
                    "thread_id": thread_id,
                    "conversation_id": payload.conversation_id,
                    "deps": deps,
                    "user_id": payload.user_id,
                }
            },
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Agent request failed: {exc}") from exc

    # ── Long memory / booking state ────────────────────────────────────────
    # Persist confirmed slots after every turn, not only after prebook. This
    # lets short follow-ups and later requests reuse destination, dates, guests,
    # selected hotel, and payment state even if LangGraph's checkpoint is cold.
    booking_state = await _persist_conversation_booking_memory(
        payload.conversation_id,
        deps,
        result,
    )

    # ── Conversation memory ────────────────────────────────────────────────
    await deps.conversation_memory.append_interaction(
        payload.conversation_id,
        user_message=payload.message,
        assistant_message=result.get("response"),
        metadata={k: v for k, v in {
            "intent": result.get("intent"),
            "agent": result.get("agent"),
            "next_action": result.get("next_action"),
            "requested_services": result.get("requested_services", []),
            "city_name": result.get("city_name"),
            "country_code": result.get("country_code"),
            "checkin_date": result.get("checkin_date"),
            "checkout_date": result.get("checkout_date"),
            "guests": result.get("guests"),
            "selected_hotel_id": result.get("selected_hotel_id"),
            "selected_hotel_offer_id": result.get("selected_hotel_offer_id"),
            "missing_fields": result.get("missing_fields", []),
            "known_booking_state": {
                k: booking_state.get(k)
                for k in [
                    "city_name",
                    "country_code",
                    "checkin_date",
                    "checkout_date",
                    "guests",
                    "selected_hotel_id",
                ]
                if booking_state.get(k) is not None
            },
        }.items() if v is not None},
    )

    if agent_requests_total is not None:
        agent_requests_total.labels(
            agent=result.get("agent") or "unknown",
            intent=result.get("intent") or "unknown",
            next_action=result.get("next_action") or "unknown",
        ).inc()

    return success_response(
        message="chat routed",
        data={
            "conversation_id": payload.conversation_id,
            "intent": result.get("intent"),
            "agent": result.get("agent"),
            "message": result.get("response"),
            "next_action": result.get("next_action"),
            "metadata": {
                "hotels": result.get("hotels", []) if result.get("next_action") == "show_hotels" else [],
                "hotel_rates": result.get("hotel_rates", []) if result.get("next_action") == "show_hotel_rates" else [],
                "hotel_images": result.get("hotel_images", []) if result.get("next_action") == "show_hotel_rates" else [],
                "error_message": result.get("error_message"),
                "mcp_tools": result.get("mcp_tools", []),
                "retrieval_context": result.get("retrieval_context", []),
                "requested_services": result.get("requested_services", []),
                "payment_url": result.get("payment_url"),
                "payment_sdk_secret_key": result.get("payment_sdk_secret_key"),
                "payment_sdk_public_key": result.get("payment_sdk_public_key"),
                "payment_transaction_id": result.get("payment_transaction_id"),
                "payment_prebook_id": result.get("payment_prebook_id"),
                "booking_status": result.get("booking_status"),
                "state": result.get("state"),
            },
        },
    )
