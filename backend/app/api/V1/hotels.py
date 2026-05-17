from typing import Any

import httpx
from fastapi import APIRouter, HTTPException, Query

from app.schemas.base import success_response
from app.schemas.hotels import HotelBookRequest, HotelPrebookRequest, HotelRatesRequest
from app.services.liteapi_hotels_service import LiteAPIHotelsService


router = APIRouter(prefix="/hotels", tags=["Hotels"])


def _provider_error(exc: httpx.HTTPStatusError) -> HTTPException:
    try:
        detail: Any = exc.response.json()
    except ValueError:
        detail = exc.response.text
    return HTTPException(status_code=exc.response.status_code, detail=detail)


@router.get("/places")
async def search_places(q: str = Query(..., min_length=1)):
    service = LiteAPIHotelsService()
    try:
        return success_response(
            message="hotel places fetched",
            data=await service.search_places(q),
        )
    except httpx.HTTPStatusError as exc:
        raise _provider_error(exc) from exc


@router.get("/room-search")
async def search_hotel_rooms(
    query: str = Query(..., min_length=1),
    limit: int | None = Query(default=12, ge=1, le=50),
    place_id: str | None = Query(default=None, alias="placeId"),
    latitude: float | None = Query(default=None),
    longitude: float | None = Query(default=None),
    radius: float | None = Query(default=None, ge=0),
    city: str | None = Query(default=None),
    country: str | None = Query(default=None, min_length=2, max_length=2),
):
    service = LiteAPIHotelsService()
    try:
        return success_response(
            message="hotel rooms fetched",
            data=await service.search_rooms(
                query=query,
                limit=limit,
                place_id=place_id,
                latitude=latitude,
                longitude=longitude,
                radius=radius,
                city=city,
                country=country,
            ),
        )
    except httpx.HTTPStatusError as exc:
        raise _provider_error(exc) from exc


@router.get("/semantic-search")
async def search_hotels_semantically(
    query: str = Query(..., min_length=1),
    limit: int = Query(default=3, ge=1, le=25),
    min_rating: float = Query(default=0, ge=0, le=10),
):
    service = LiteAPIHotelsService()
    try:
        return success_response(
            message="semantic hotels fetched",
            data=await service.semantic_search(
                query=query,
                limit=limit,
                min_rating=min_rating,
            ),
        )
    except httpx.HTTPStatusError as exc:
        raise _provider_error(exc) from exc


@router.post("/rates")
async def search_hotel_rates(payload: HotelRatesRequest):
    service = LiteAPIHotelsService()
    try:
        return success_response(
            message="hotel rates fetched",
            data=await service.search_rates(payload.model_dump(exclude_none=True)),
        )
    except httpx.HTTPStatusError as exc:
        raise _provider_error(exc) from exc


@router.post("/prebook")
async def prebook_hotel(
    payload: HotelPrebookRequest,
    timeout: int | None = Query(default=None, ge=1, le=120),
    include_credit_balance: bool | None = Query(default=None),
):
    service = LiteAPIHotelsService()
    try:
        return success_response(
            message="hotel prebook created",
            data=await service.prebook_full(
                payload=payload.model_dump(exclude_none=True),
                timeout_seconds=timeout,
                include_credit_balance=include_credit_balance,
            ),
        )
    except httpx.HTTPStatusError as exc:
        raise _provider_error(exc) from exc


@router.post("/book")
async def book_hotel(payload: HotelBookRequest):
    service = LiteAPIHotelsService()
    try:
        return success_response(
            message="hotel booking completed",
            data=await service.book(payload.model_dump(exclude_none=True)),
        )
    except httpx.HTTPStatusError as exc:
        raise _provider_error(exc) from exc


@router.get("/prebooks/{prebook_id}")
async def get_hotel_prebook(prebook_id: str):
    service = LiteAPIHotelsService()
    try:
        return success_response(
            message="hotel prebook fetched",
            data=await service.get_prebook(prebook_id),
        )
    except httpx.HTTPStatusError as exc:
        raise _provider_error(exc) from exc


@router.get("/bookings/{booking_id}")
async def get_hotel_booking(booking_id: str):
    service = LiteAPIHotelsService()
    try:
        return success_response(
            message="hotel booking fetched",
            data=await service.get_booking(booking_id),
        )
    except httpx.HTTPStatusError as exc:
        raise _provider_error(exc) from exc


@router.get("/bookings")
async def list_hotel_bookings():
    service = LiteAPIHotelsService()
    try:
        return success_response(
            message="hotel bookings fetched",
            data=await service.list_bookings(),
        )
    except httpx.HTTPStatusError as exc:
        raise _provider_error(exc) from exc


@router.get("/{hotel_id}/ask")
async def ask_hotel_question(
    hotel_id: str,
    query: str = Query(..., min_length=1),
    allow_web_search: bool = Query(default=False, alias="allowWebSearch"),
):
    service = LiteAPIHotelsService()
    try:
        return success_response(
            message="hotel question answered",
            data=await service.ask_question(
                hotel_id=hotel_id,
                query=query,
                allow_web_search=allow_web_search,
            ),
        )
    except httpx.HTTPStatusError as exc:
        raise _provider_error(exc) from exc


@router.get("/{hotel_id}")
async def get_hotel_details(
    hotel_id: str,
    timeout: int = Query(default=4, ge=1, le=20),
    language: str | None = Query(default=None),
    advanced_accessibility_only: bool | None = Query(
        default=None,
        alias="advancedAccessibilityOnly",
    ),
):
    service = LiteAPIHotelsService()
    try:
        return success_response(
            message="hotel details fetched",
            data=await service.get_details(
                hotel_id=hotel_id,
                timeout_seconds=timeout,
                language=language,
                advanced_accessibility_only=advanced_accessibility_only,
            ),
        )
    except httpx.HTTPStatusError as exc:
        raise _provider_error(exc) from exc
