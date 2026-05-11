from typing import Any

import httpx

from app.core.config import settings


LITEAPI_BASE_URL = "https://api.liteapi.travel/v3.0"


class LiteAPIService:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or settings.LITEAPI_API_KEY

    def _headers(self) -> dict[str, str]:
        if not self.api_key:
            raise ValueError("LITEAPI_API_KEY is not configured")

        return {
            "X-API-Key": self.api_key,
            "Accept": "application/json",
        }

    async def search_hotels_by_city(
        self,
        country_code: str,
        city_name: str,
        limit: int = 5,
    ) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                f"{LITEAPI_BASE_URL}/data/hotels",
                headers=self._headers(),
                params={
                    "countryCode": country_code,
                    "cityName": city_name,
                },
            )
            response.raise_for_status()

        data = response.json()
        hotels = data.get("data", []) if isinstance(data, dict) else []

        return {
            "total": data.get("total") if isinstance(data, dict) else None,
            "result_count": len(hotels),
            "hotels": [
                {
                    "hotel_id": hotel.get("id"),
                    "name": hotel.get("name"),
                    "address": hotel.get("address"),
                    "city": hotel.get("city"),
                    "country": hotel.get("country"),
                    "stars": hotel.get("stars"),
                    "rating": hotel.get("rating"),
                }
                for hotel in hotels[:limit]
            ],
        }
