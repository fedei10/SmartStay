from fastapi import APIRouter, HTTPException, Request

from app.agents.booking.dependencies import BookingDeps
from app.core.metrics import agent_requests_total
from app.schemas.base import success_response
from app.schemas.chat import ChatRequest

router = APIRouter(prefix="/chat", tags=["Chat"])

INTERNAL_PAYMENT_VERIFIED_MESSAGE = "__internal_payment_verified__"


async def _handle_payment_continuation(
    payload: ChatRequest,
    deps: BookingDeps,
) -> dict:
    """Handle the post-payment booking-finalization flow.

    Called when the frontend sends the internal payment-verified sentinel after
    the user completes the LiteAPI payment SDK flow.
    """
    conversation_id = payload.conversation_id
    booking_state = await deps.conversation_memory.get_booking_state(conversation_id)

    # Record that payment succeeded.
    booking_state["payment_status"] = "completed"
    if payload.payment_transaction_id:
        booking_state["payment_transaction_id"] = payload.payment_transaction_id
    if payload.payment_prebook_id:
        booking_state["payment_prebook_id"] = payload.payment_prebook_id
    await deps.conversation_memory.set_booking_state(conversation_id, booking_state)

    # Resolve the identifiers we need for booking.
    prebook_id = booking_state.get("payment_prebook_id") or payload.payment_prebook_id
    transaction_id = (
        booking_state.get("payment_transaction_id") or payload.payment_transaction_id
    )

    # Check whether guest details are already known.
    guest_first = booking_state.get("guest_first_name")
    guest_last = booking_state.get("guest_last_name")
    guest_email = booking_state.get("guest_email")

    if not all([guest_first, guest_last, guest_email]):
        return success_response(
            message="chat routed",
            data={
                "conversation_id": conversation_id,
                "message": (
                    "Payment successful! To finalize your booking, please share the main "
                    "guest's first name, last name, and email address."
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

    # All details present – call LiteAPI book endpoint.
    try:
        result = await deps.hotels.book(
            {
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
                "guests": [
                    {
                        "occupancyNumber": 1,
                        "firstName": guest_first,
                        "lastName": guest_last,
                        "email": guest_email,
                    }
                ],
            }
        )

        booking_state["booking_status"] = "confirmed"
        await deps.conversation_memory.set_booking_state(conversation_id, booking_state)

        booking_data = result.get("data", result)
        booking_id = booking_data.get("bookingId") or booking_data.get("booking_id", "N/A")
        confirmation_code = booking_data.get("hotelConfirmationCode", "N/A")

        return success_response(
            message="chat routed",
            data={
                "conversation_id": conversation_id,
                "message": (
                    f"Your hotel booking is confirmed!\n"
                    f"Booking ID: {booking_id}\n"
                    f"Confirmation code: {confirmation_code}\n\n"
                    "Thank you for booking with ttrip. Is there anything else I can help you with?"
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
                    f"Payment was received, but the booking could not be finalized: {exc}. "
                    "Please contact support with your transaction details."
                ),
                "intent": "hotel_booking",
                "agent": "hotel_booking_agent",
                "next_action": "error",
                "metadata": {
                    "booking_status": "booking_failed",
                    "error_message": str(exc),
                },
            },
        )


@router.post("")
async def chat(payload: ChatRequest, request: Request):
    deps: BookingDeps = request.app.state.booking_deps

    # ── Payment continuation shortcut ──────────────────────────────────────
    if payload.payment_completed and payload.message == INTERNAL_PAYMENT_VERIFIED_MESSAGE:
        return await _handle_payment_continuation(payload, deps)

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
                }
            },
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Agent request failed: {exc}",
        ) from exc

    # ── Persist prebook state when the agent returns payment metadata ──────
    metadata = result.get("metadata") or {}
    prebook_id = metadata.get("payment_prebook_id")
    transaction_id = metadata.get("payment_transaction_id")
    if prebook_id or transaction_id:
        booking_state = await deps.conversation_memory.get_booking_state(
            payload.conversation_id
        )
        if prebook_id:
            booking_state["payment_prebook_id"] = prebook_id
        if transaction_id:
            booking_state["payment_transaction_id"] = transaction_id
        booking_state["payment_status"] = "payment_required"
        await deps.conversation_memory.set_booking_state(
            payload.conversation_id, booking_state
        )

    # ── Append interaction to conversation memory ──────────────────────────
    await deps.conversation_memory.append_interaction(
        payload.conversation_id,
        user_message=payload.message,
        assistant_message=result.get("response"),
        metadata={
            "intent": result.get("intent"),
            "agent": result.get("agent"),
            "next_action": result.get("next_action"),
            "requested_services": result.get("requested_services", []),
            "city_name": result.get("city_name"),
            "country_code": result.get("country_code"),
            "origin": result.get("origin"),
            "destination": result.get("destination"),
            "departure_date": result.get("departure_date"),
            "return_date": result.get("return_date"),
        },
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
                "hotels": result.get("hotels", [])
                if result.get("next_action") == "show_hotels"
                else [],
                "flights": result.get("flights", [])
                if result.get("next_action") == "show_flights"
                else [],
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
                "flight": {
                    "origin": result.get("origin"),
                    "destination": result.get("destination"),
                    "departure_date": result.get("departure_date"),
                    "return_date": result.get("return_date"),
                }
                if result.get("agent") == "flight_booking_agent"
                else None,
            },
        },
    )
