from typing import Any

import httpx
from langchain_core.tools import tool

from app.core.config import settings


LITEAPI_BASE_URL = "https://api.liteapi.travel/v3.0"


def _compact_hotels(data: dict[str, Any]) -> dict[str, Any]:
    hotels = data.get("data", [])
    return {
        "total": data.get("total"),
        "result_count": len(hotels),
        "hotels": [
            {
                "id": hotel.get("id"),
                "name": hotel.get("name"),
                "city": hotel.get("city"),
                "country": hotel.get("country"),
                "stars": hotel.get("stars"),
                "rating": hotel.get("rating"),
                "address": hotel.get("address"),
            }
            for hotel in hotels[:5]
        ],
    }


@tool
def search_hotels_by_city(country_code: str, city_name: str) -> dict[str, Any]:
    """Search LiteAPI hotels by country code and city name."""
    if not settings.LITEAPI_API_KEY:
        raise ValueError("LITEAPI_API_KEY is not configured")

    response = httpx.get(
        f"{LITEAPI_BASE_URL}/data/hotels",
        headers={
            "X-API-Key": settings.LITEAPI_API_KEY,
            "Accept": "application/json",
        },
        params={
            "countryCode": country_code,
            "cityName": city_name,
        },
        timeout=15.0,
    )
    response.raise_for_status()
    return _compact_hotels(response.json())


def get_hotel_search_tools():
    return [search_hotels_by_city]
