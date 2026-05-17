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
async def prebook_hotel(payload: HotelPrebookRequest):
    service = LiteAPIHotelsService()
    try:
        return success_response(
            message="hotel prebook created",
            data=await service.prebook(
                offer_id=payload.offerId,
                use_payment_sdk=payload.usePaymentSdk,
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


@router.get("/{hotel_id}")
async def get_hotel_details(
    hotel_id: str,
    timeout: int = Query(default=4, ge=1, le=20),
):
    service = LiteAPIHotelsService()
    try:
        return success_response(
            message="hotel details fetched",
            data=await service.get_details(hotel_id=hotel_id, timeout_seconds=timeout),
        )
    except httpx.HTTPStatusError as exc:
        raise _provider_error(exc) from exc
