from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.booking_repository import BookingDBRepository
from app.db.database import async_get_db
from app.models.booking import Booking
from app.schemas.base import success_response
from app.services.liteapi_flights_service import LiteAPIFlightsService
from app.services.liteapi_hotels_service import LiteAPIHotelsService

router = APIRouter(prefix="/bookings", tags=["Bookings"])


def _serialize(b: Booking) -> dict[str, Any]:
    payload = b.provider_payload or {}
    cancellation = payload.get("cancellation") if isinstance(payload.get("cancellation"), dict) else {}
    base = {
        "id": b.id,
        "booking_type": b.booking_type.lower(),
        "booking_reference": b.provider_booking_id,
        "provider_booking_id": b.provider_booking_id,
        "provider_reference": b.provider_reference,
        "status": b.status.lower(),
        "currency": b.currency or "",
        "total_amount": float(b.total_charged) if b.total_charged else 0,
        "payment_status": "succeeded",
        "updated_at": b.updated_at.isoformat(),
        "created_at": b.created_at.isoformat(),
        "cancellation_status": cancellation.get("status"),
        "cancellation_fee": cancellation.get("cancellation_fee"),
        "refund_amount": cancellation.get("refund_amount"),
        "cancellation_currency": cancellation.get("currency"),
    }
    if b.booking_type == "HOTEL":
        base.update({
            "hotel_name": payload.get("hotelName") or payload.get("hotel_name", "Hotel"),
            "checkin_date": payload.get("checkin") or payload.get("checkin_date", ""),
            "checkout_date": payload.get("checkout") or payload.get("checkout_date", ""),
            "room_type": payload.get("roomType") or payload.get("room_type"),
            "guests": payload.get("guests"),
        })
    else:
        base.update({
            "hotel_name": "",
            "flight_reference": b.provider_reference,
            "origin": payload.get("origin", ""),
            "destination": payload.get("destination", ""),
            "departure_date": payload.get("departure_date", ""),
            "return_date": payload.get("return_date"),
            "checkin_date": payload.get("departure_date", ""),
            "checkout_date": payload.get("return_date", ""),
            "airline": payload.get("airline"),
            "passengers": payload.get("passengers", []),
        })
    return base


@router.get("/{user_id}")
async def list_user_bookings(
    user_id: str,
    type: str | None = Query(default=None, description="HOTEL or FLIGHT"),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=50, ge=1, le=100),
    db: AsyncSession = Depends(async_get_db),
):
    repo = BookingDBRepository(db)
    bookings, total = await repo.list_for_user(
        user_id=user_id,
        booking_type=type,
        page=page,
        per_page=per_page,
    )
    return [_serialize(b) for b in bookings]


@router.put("/{booking_reference}/cancel")
@router.post("/{booking_reference}/cancel")
@router.put("/reference/{booking_reference}/cancel")
@router.post("/reference/{booking_reference}/cancel")
async def cancel_booking(
    booking_reference: str,
    user_id: str = Query(..., description="Clerk user ID"),
    reason: str | None = Query(default=None),
    db: AsyncSession = Depends(async_get_db),
):
    repo = BookingDBRepository(db)
    booking = await repo.get_by_reference(booking_reference, user_id)

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.status.upper().startswith("CANCELLED"):
        raise HTTPException(status_code=400, detail="Booking is already cancelled")

    cancellation_result: dict[str, Any] = {}
    try:
        if booking.booking_type == "HOTEL":
            cancellation_result = await LiteAPIHotelsService().cancel_booking(
                booking.provider_booking_id,
            )
        else:
            cancellation_result = await LiteAPIFlightsService().cancel_booking(
                booking.provider_booking_id,
            )
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code not in {404, 410}:
            try:
                detail: Any = exc.response.json()
            except ValueError:
                detail = exc.response.text
            raise HTTPException(status_code=exc.response.status_code, detail=detail) from exc
        cancellation_result = {
            "data": {
                "bookingId": booking.provider_booking_id,
                "status": "CANCELLED",
                "provider_error": "booking id not found at provider",
            },
        }

    cancellation_data = cancellation_result.get("data", cancellation_result)
    if not isinstance(cancellation_data, dict):
        cancellation_data = {}

    cancellation_status = str(cancellation_data.get("status") or "CANCELLED")
    local_status = (
        cancellation_status
        if cancellation_status.upper().startswith("CANCELLED")
        else "CANCELLED"
    )

    cancelled = await repo.cancel_by_reference(
        booking_reference,
        user_id,
        status=local_status.upper(),
        cancellation={
            "bookingId": cancellation_data.get("bookingId") or booking.provider_booking_id,
            "status": local_status.upper(),
            "cancellation_fee": cancellation_data.get("cancellation_fee"),
            "refund_amount": cancellation_data.get("refund_amount"),
            "currency": cancellation_data.get("currency") or booking.currency,
        },
    )
    if not cancelled:
        raise HTTPException(status_code=404, detail="Booking not found")
    return _serialize(cancelled)  # type: ignore[arg-type]
