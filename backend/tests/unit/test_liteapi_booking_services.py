from unittest.mock import AsyncMock

import pytest

from app.schemas.flights import (
    FlightAttachServicesRequest,
    FlightBookRequest,
    FlightSearchRequest,
)
from app.schemas.hotels import HotelBookRequest, HotelPrebookRequest
from app.services.liteapi_flights_service import LiteAPIFlightsService
from app.services.liteapi_hotels_service import LiteAPIHotelsService


class DummyClient:
    def __init__(self):
        self.request = AsyncMock(return_value={"ok": True})


@pytest.mark.asyncio
async def test_hotel_prebook_full_passes_optional_query_params():
    client = DummyClient()
    service = LiteAPIHotelsService(client)
    payload = HotelPrebookRequest(
        offerId="offer-1",
        usePaymentSdk=True,
        voucherCode="SPRING",
        bedTypeIds=[1, 2],
        includeCreditBalance=True,
    )

    await service.prebook_full(
        payload.model_dump(exclude_none=True),
        timeout_seconds=30,
        include_credit_balance=True,
    )

    client.request.assert_awaited_once_with(
        "POST",
        "/rates/prebook",
        booking_api=True,
        params={"timeout": 30, "includeCreditBalance": True},
        json=payload.model_dump(exclude_none=True),
        timeout=35.0,
    )


@pytest.mark.asyncio
async def test_hotel_booking_lookup_routes_use_booking_api():
    client = DummyClient()
    service = LiteAPIHotelsService(client)

    await service.get_prebook("pb_123")
    await service.get_booking("bk_123")
    await service.list_bookings()

    assert client.request.await_args_list[0].args == ("GET", "/prebooks/pb_123")
    assert client.request.await_args_list[0].kwargs["booking_api"] is True
    assert client.request.await_args_list[1].args == ("GET", "/bookings/bk_123")
    assert client.request.await_args_list[1].kwargs["booking_api"] is True
    assert client.request.await_args_list[2].args == ("GET", "/bookings")
    assert client.request.await_args_list[2].kwargs["booking_api"] is True


@pytest.mark.asyncio
async def test_hotel_cancel_booking_uses_liteapi_put_endpoint():
    client = DummyClient()
    service = LiteAPIHotelsService(client)

    await service.cancel_booking("bk_123")

    client.request.assert_awaited_once_with(
        "PUT",
        "/bookings/bk_123",
        booking_api=True,
        timeout=30.0,
    )


@pytest.mark.asyncio
async def test_hotel_room_search_maps_visual_search_params():
    client = DummyClient()
    service = LiteAPIHotelsService(client)

    await service.search_rooms(
        query="luxury modernist comfort",
        limit=12,
        city="Paris",
        country="FR",
        latitude=None,
    )

    client.request.assert_awaited_once_with(
        "GET",
        "/data/hotels/room-search",
        params={
            "query": "luxury modernist comfort",
            "limit": 12,
            "city": "Paris",
            "country": "FR",
        },
        timeout=20.0,
    )


@pytest.mark.asyncio
async def test_hotel_semantic_search_maps_query_params():
    client = DummyClient()
    service = LiteAPIHotelsService(client)

    await service.semantic_search(query="romantic getaway in London", limit=4, min_rating=8)

    client.request.assert_awaited_once_with(
        "GET",
        "/data/hotels/semantic-search",
        params={
            "query": "romantic getaway in London",
            "limit": 4,
            "min_rating": 8,
        },
        timeout=20.0,
    )


@pytest.mark.asyncio
async def test_hotel_ask_question_maps_hotel_context_params():
    client = DummyClient()
    service = LiteAPIHotelsService(client)

    await service.ask_question(
        hotel_id="lp1897",
        query="Is there parking available?",
        allow_web_search=True,
    )

    client.request.assert_awaited_once_with(
        "GET",
        "/data/hotel/ask",
        params={
            "hotelId": "lp1897",
            "query": "Is there parking available?",
            "allowWebSearch": True,
        },
        timeout=20.0,
    )


def test_flight_book_request_supports_legacy_transaction_id_shape():
    payload = FlightBookRequest(
        prebookId="pre_123",
        transactionId="tx_123",
    )

    assert payload.payment == {
        "method": "TRANSACTION_ID",
        "transactionId": "tx_123",
    }


def test_flight_book_request_supports_credit_payment_shape():
    payload = FlightBookRequest(
        prebookId="pre_123",
        payment={"method": "CREDIT"},
    )

    assert payload.payment == {"method": "CREDIT"}


def test_flight_search_request_supports_legs_filters_and_sort():
    payload = FlightSearchRequest(
        legs=[
            {
                "origin": "TUN",
                "destination": "CDG",
                "date": "2026-06-10",
                "direction": "OUTBOUND",
                "filters": {"maxStops": 1},
            }
        ],
        adults=1,
        currency="EUR",
        cabinClass="ECONOMY",
        filters={
            "maxStops": 1,
            "includesCheckedBag": True,
            "refundableOnly": False,
        },
        sort={"sortBy": "price", "sortOrder": "asc"},
    )

    dumped = payload.model_dump(exclude_none=True)

    assert dumped["legs"][0]["filters"] == {"maxStops": 1}
    assert dumped["filters"]["includesCheckedBag"] is True
    assert dumped["sort"] == {"sortBy": "price", "sortOrder": "asc"}


def test_flight_attach_services_request_supports_selected_services_and_legacy_services_key():
    payload = FlightAttachServicesRequest(
        services=[
            {
                "passengerIndex": 0,
                "serviceId": "svc_123",
                "quantity": 1,
            }
        ]
    )

    assert payload.selectedServices == [
        {
            "passengerIndex": 0,
            "serviceId": "svc_123",
            "quantity": 1,
        }
    ]


def test_hotel_book_request_supports_extended_provider_fields():
    payload = HotelBookRequest(
        prebookId="pre_123",
        clientReference="client-1",
        holder={
            "firstName": "Jane",
            "lastName": "Doe",
            "email": "jane@example.com",
            "phone": "+123456789",
        },
        guests=[
            {
                "occupancyNumber": 1,
                "firstName": "Jane",
                "lastName": "Doe",
                "email": "jane@example.com",
                "remarks": "quiet room",
            }
        ],
        metadata={
            "ip": "203.0.113.10",
            "country": "US",
            "language": "en-US",
        },
        payment={"method": "ACC_CREDIT_CARD"},
        guestPayment={
            "method": "CREDIT_CARD",
            "phone": "+123456789",
            "payee_last_name": "Doe",
            "payee_first_name": "Jane",
            "last_4_digits": "4242",
        },
    )

    assert payload.payment.method == "ACC_CREDIT_CARD"
    assert payload.metadata is not None
    assert payload.guestPayment is not None


@pytest.mark.asyncio
async def test_flight_booking_service_uses_payment_payload_directly():
    client = DummyClient()
    service = LiteAPIFlightsService(client)

    await service.book("pre_123", {"method": "CREDIT"})

    client.request.assert_awaited_once_with(
        "POST",
        "/flights/bookings",
        json={"prebookId": "pre_123", "payment": {"method": "CREDIT"}},
        timeout=60.0,
    )
