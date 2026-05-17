from typing import Any

from app.services.liteapi_service import LiteAPIService


class LiteAPIHotelsService:
    def __init__(self, client: LiteAPIService | None = None):
        self.client = client or LiteAPIService()

    async def search_places(self, text_query: str) -> dict[str, Any]:
        return await self.client.request(
            "GET",
            "/data/places",
            params={"textQuery": text_query},
        )

    async def search_rates(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self.client.request(
            "POST",
            "/hotels/rates",
            json=payload,
            timeout=45.0,
        )

    async def prebook(self, offer_id: str, use_payment_sdk: bool = True) -> dict[str, Any]:
        return await self.client.request(
            "POST",
            "/rates/prebook",
            booking_api=True,
            json={
                "usePaymentSdk": use_payment_sdk,
                "offerId": offer_id,
            },
            timeout=60.0,
        )

    async def prebook_full(
        self,
        payload: dict[str, Any],
        *,
        timeout_seconds: int | None = None,
        include_credit_balance: bool | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {}
        if timeout_seconds is not None:
            params["timeout"] = timeout_seconds
        if include_credit_balance is not None:
            params["includeCreditBalance"] = include_credit_balance

        return await self.client.request(
            "POST",
            "/rates/prebook",
            booking_api=True,
            params=params or None,
            json=payload,
            timeout=float(timeout_seconds or 60) + 5.0,
        )

    async def book(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self.client.request(
            "POST",
            "/rates/book",
            booking_api=True,
            json=payload,
            timeout=60.0,
        )

    async def get_prebook(self, prebook_id: str) -> dict[str, Any]:
        return await self.client.request(
            "GET",
            f"/prebooks/{prebook_id}",
            booking_api=True,
            timeout=30.0,
        )

    async def get_booking(self, booking_id: str) -> dict[str, Any]:
        return await self.client.request(
            "GET",
            f"/bookings/{booking_id}",
            booking_api=True,
            timeout=30.0,
        )

    async def list_bookings(self) -> dict[str, Any]:
        return await self.client.request(
            "GET",
            "/bookings",
            booking_api=True,
            timeout=30.0,
        )

    async def cancel_booking(self, booking_id: str) -> dict[str, Any]:
        return await self.client.request(
            "PUT",
            f"/bookings/{booking_id}",
            booking_api=True,
            timeout=30.0,
        )

    async def search_rooms(
        self,
        *,
        query: str,
        limit: int | None = None,
        place_id: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
        radius: float | None = None,
        city: str | None = None,
        country: str | None = None,
    ) -> dict[str, Any]:
        params = {
            "query": query,
            "limit": limit,
            "placeId": place_id,
            "latitude": latitude,
            "longitude": longitude,
            "radius": radius,
            "city": city,
            "country": country,
        }
        return await self.client.request(
            "GET",
            "/data/hotels/room-search",
            params={key: value for key, value in params.items() if value is not None},
            timeout=20.0,
        )

    async def semantic_search(
        self,
        *,
        query: str,
        limit: int = 3,
        min_rating: float = 0,
    ) -> dict[str, Any]:
        return await self.client.request(
            "GET",
            "/data/hotels/semantic-search",
            params={
                "query": query,
                "limit": limit,
                "min_rating": min_rating,
            },
            timeout=20.0,
        )

    async def ask_question(
        self,
        *,
        hotel_id: str,
        query: str,
        allow_web_search: bool = False,
    ) -> dict[str, Any]:
        return await self.client.request(
            "GET",
            "/data/hotel/ask",
            params={
                "hotelId": hotel_id,
                "query": query,
                "allowWebSearch": allow_web_search,
            },
            timeout=20.0,
        )

    async def get_details(
        self,
        hotel_id: str,
        timeout_seconds: int = 4,
        language: str | None = None,
        advanced_accessibility_only: bool | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {"hotelId": hotel_id, "timeout": timeout_seconds}
        if language:
            params["language"] = language
        if advanced_accessibility_only is not None:
            params["advancedAccessibilityOnly"] = advanced_accessibility_only

        return await self.client.request(
            "GET",
            "/data/hotel",
            params=params,
            timeout=max(float(timeout_seconds) + 5.0, 10.0),
        )
