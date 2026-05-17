from typing import Any

import httpx
from fastapi import APIRouter, HTTPException, Query

from app.schemas.base import success_response
from app.schemas.flights import (
    FlightAttachServicesRequest,
    FlightBookRequest,
    FlightPrebookRequest,
    FlightSearchRequest,
    FlightVerifyRequest,
)
from app.services.liteapi_flights_service import LiteAPIFlightsService


router = APIRouter(prefix="/flights", tags=["Flights"])


def _provider_error(exc: httpx.HTTPStatusError) -> HTTPException:
    try:
        detail: Any = exc.response.json()
    except ValueError:
        detail = exc.response.text
    if exc.response.status_code == 404:
        detail = {
            "message": "The flight offer may have expired. Restart search and do not reuse the old offerId.",
            "provider": detail,
        }
    return HTTPException(status_code=exc.response.status_code, detail=detail)


@router.post("/search")
async def search_flights(payload: FlightSearchRequest):
    service = LiteAPIFlightsService()
    try:
        return success_response(
            message="flight search completed",
            data=await service.search(payload.model_dump(exclude_none=True)),
        )
    except httpx.HTTPStatusError as exc:
        raise _provider_error(exc) from exc


@router.post("/verify")
async def verify_flight_offer(payload: FlightVerifyRequest):
    service = LiteAPIFlightsService()
    try:
        return success_response(
            message="flight offer verified",
            data=await service.verify(payload.offerId),
        )
    except httpx.HTTPStatusError as exc:
        raise _provider_error(exc) from exc


@router.post("/prebook")
async def prebook_flight(payload: FlightPrebookRequest):
    service = LiteAPIFlightsService()
    try:
        return success_response(
            message="flight prebook created",
            data=await service.prebook(payload.model_dump(exclude_none=True)),
        )
    except httpx.HTTPStatusError as exc:
        raise _provider_error(exc) from exc


@router.post("/prebooks/{prebook_id}/services")
async def attach_flight_services(
    prebook_id: str,
    payload: FlightAttachServicesRequest,
):
    service = LiteAPIFlightsService()
    try:
        return success_response(
            message="flight services attached",
            data=await service.attach_services(
                prebook_id=prebook_id,
                payload=payload.model_dump(exclude_none=True),
            ),
        )
    except httpx.HTTPStatusError as exc:
        raise _provider_error(exc) from exc


@router.post("/book")
async def book_flight(payload: FlightBookRequest):
    service = LiteAPIFlightsService()
    try:
        return success_response(
            message="flight booking completed",
            data=await service.book(
                prebook_id=payload.prebookId,
                transaction_id=payload.transactionId,
            ),
        )
    except httpx.HTTPStatusError as exc:
        raise _provider_error(exc) from exc


@router.get("/bookings/{booking_id}")
async def get_flight_booking(booking_id: str):
    service = LiteAPIFlightsService()
    try:
        return success_response(
            message="flight booking fetched",
            data=await service.get_booking(booking_id),
        )
    except httpx.HTTPStatusError as exc:
        raise _provider_error(exc) from exc


@router.get("/bookings")
async def list_flight_bookings(
    airline_pnr: str | None = Query(default=None),
    last_name: str | None = Query(default=None),
):
    if bool(airline_pnr) != bool(last_name):
        raise HTTPException(
            status_code=400,
            detail="airline_pnr and last_name must be provided together",
        )

    service = LiteAPIFlightsService()
    try:
        return success_response(
            message="flight bookings fetched",
            data=await service.list_bookings(
                airline_pnr=airline_pnr,
                last_name=last_name,
            ),
        )
    except httpx.HTTPStatusError as exc:
        raise _provider_error(exc) from exc
