from typing import Any
import asyncio

import httpx

from app.core.config import settings
from app.core.logging import logger


LITEAPI_BASE_URL = "https://api.liteapi.travel/v3.0"
LITEAPI_BOOKING_BASE_URL = "https://book.liteapi.travel/v3.0"


class LiteAPIService:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or settings.LITEAPI_API_KEY

    def _headers(self) -> dict[str, str]:
        if not self.api_key:
            raise ValueError("LITEAPI_API_KEY is not configured")

        return {
            "X-API-Key": self.api_key,
            "accept": "application/json",
            "content-type": "application/json",
        }

    async def request(
        self,
        method: str,
        path: str,
        *,
        booking_api: bool = False,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        timeout: float | None = None,
    ) -> dict[str, Any]:
        base_url = LITEAPI_BOOKING_BASE_URL if booking_api else LITEAPI_BASE_URL
        request_timeout = timeout or settings.PROVIDER_REQUEST_TIMEOUT_SECONDS
        last_error: Exception | None = None

        for attempt in range(settings.PROVIDER_MAX_RETRIES + 1):
            try:
                async with httpx.AsyncClient(timeout=request_timeout) as client:
                    response = await client.request(
                        method,
                        f"{base_url}{path}",
                        headers=self._headers(),
                        params=params,
                        json=json,
                    )
                    response.raise_for_status()
                break
            except (httpx.TimeoutException, httpx.HTTPStatusError, httpx.TransportError) as exc:
                last_error = exc
                retryable_status = (
                    isinstance(exc, httpx.HTTPStatusError)
                    and exc.response.status_code in {429, 500, 502, 503, 504}
                )
                retryable_transport = isinstance(
                    exc,
                    (httpx.TimeoutException, httpx.TransportError),
                )
                if attempt >= settings.PROVIDER_MAX_RETRIES or not (
                    retryable_status or retryable_transport
                ):
                    raise

                delay = min(0.5 * (2**attempt), 4.0)
                logger.warning(
                    "liteapi_request_retry method=%s path=%s attempt=%s delay=%s",
                    method,
                    path,
                    attempt + 1,
                    delay,
                )
                await asyncio.sleep(delay)
        else:
            raise last_error or RuntimeError("LiteAPI request failed")

        if response.status_code == 204 or not response.content:
            return {}

        data = response.json()
        return data if isinstance(data, dict) else {"data": data}

    async def search_hotels_by_city(
        self,
        country_code: str,
        city_name: str,
        limit: int = 5,
    ) -> dict[str, Any]:
        data = await self.request(
            "GET",
            "/data/hotels",
            params={
                "countryCode": country_code,
                "cityName": city_name,
            },
            timeout=15.0,
        )
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
                    "description": hotel.get("description"),
                    "image_url": hotel.get("main_photo") or hotel.get("image_url"),
                    "image_urls": hotel.get("images") or hotel.get("hotelImages") or [],
                }
                for hotel in hotels[:limit]
            ],
        }
