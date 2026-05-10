"""
LiteAPI connection and testing service.
"""

import httpx

from app.config import settings


LITEAPI_BASE_URL = "https://api.liteapi.travel/v3.0"


def test_liteapi_connection():
    """
    Test the LiteAPI connection by fetching a small hotel list.
    Returns a structured result without exposing the API key.
    """
    api_key = settings.LITE_API

    if not api_key:
        return {
            "status": "error",
            "message": "LITE_API is not configured",
        }

    url = f"{LITEAPI_BASE_URL}/data/hotels"
    headers = {
        "X-API-Key": api_key,
        "Accept": "application/json",
    }
    params = {
        "countryCode": "IT",
        "cityName": "Rome",
    }

    try:
        response = httpx.get(url, headers=headers, params=params, timeout=15.0)
        response.raise_for_status()
        data = response.json()
        hotels = data.get("data", []) if isinstance(data, dict) else []
        hotel_ids = data.get("hotelIds", []) if isinstance(data, dict) else []

        return {
            "status": "ok",
            "message": "LiteAPI connection successful",
            "sample_query": params,
            "result_count": len(hotels),
            "total": data.get("total") if isinstance(data, dict) else None,
            "sample_hotel_ids": hotel_ids[:5],
            "sample_hotels": [
                {
                    "id": hotel.get("id"),
                    "name": hotel.get("name"),
                    "city": hotel.get("city"),
                    "country": hotel.get("country"),
                }
                for hotel in hotels[:3]
            ],
        }
    except httpx.HTTPStatusError as exc:
        return {
            "status": "error",
            "message": "LiteAPI returned an error",
            "detail": str(exc),
            "response": exc.response.text,
        }
    except httpx.RequestError as exc:
        return {
            "status": "error",
            "message": "Failed to reach LiteAPI",
            "detail": str(exc),
        }


if __name__ == "__main__":
    print(test_liteapi_connection())
