from typing import Any

from app.services.liteapi_service import LiteAPIService


class LiteAPIFlightsService:
    def __init__(self, client: LiteAPIService | None = None):
        self.client = client or LiteAPIService()

    async def search(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self.client.request(
            "POST",
            "/flights/rates",
            json=payload,
            timeout=45.0,
        )

    async def verify(self, offer_id: str) -> dict[str, Any]:
        return await self.client.request(
            "POST",
            "/flights/verify",
            json={"offerId": offer_id},
            timeout=30.0,
        )

    async def prebook(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self.client.request(
            "POST",
            "/flights/prebooks",
            json=payload,
            timeout=60.0,
        )

    async def attach_services(
        self,
        prebook_id: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        return await self.client.request(
            "POST",
            f"/flights/prebooks/{prebook_id}/services",
            json=payload,
            timeout=60.0,
        )

    async def book(
        self,
        prebook_id: str,
        payment: dict[str, Any],
    ) -> dict[str, Any]:
        return await self.client.request(
            "POST",
            "/flights/bookings",
            json={
                "prebookId": prebook_id,
                "payment": payment,
            },
            timeout=60.0,
        )

    async def get_booking(self, booking_id: str) -> dict[str, Any]:
        return await self.client.request(
            "GET",
            f"/flights/bookings/{booking_id}",
            timeout=30.0,
        )

    async def cancel_booking(self, booking_id: str) -> dict[str, Any]:
        return await self.client.request(
            "DELETE",
            f"/flights/bookings/{booking_id}",
            timeout=30.0,
        )

    async def list_bookings(
        self,
        airline_pnr: str | None = None,
        last_name: str | None = None,
    ) -> dict[str, Any]:
        params = {}
        if airline_pnr and last_name:
            params = {"airlinePnr": airline_pnr, "lastName": last_name}

        return await self.client.request(
            "GET",
            "/flights/bookings",
            params=params,
            timeout=30.0,
        )
