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

    async def book(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self.client.request(
            "POST",
            "/rates/book",
            booking_api=True,
            json=payload,
            timeout=60.0,
        )

    async def get_details(self, hotel_id: str, timeout_seconds: int = 4) -> dict[str, Any]:
        return await self.client.request(
            "GET",
            "/data/hotel",
            params={"hotelId": hotel_id, "timeout": timeout_seconds},
            timeout=max(float(timeout_seconds) + 5.0, 10.0),
        )
