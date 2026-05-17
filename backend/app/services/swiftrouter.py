"""SwiftRouter health-check and availability probe."""

import httpx

from app.core.config import settings


async def check_swiftrouter() -> dict:
    """Return liveness and quota info for the SwiftRouter provider.

    Hits GET /v1/models (the cheapest authenticated endpoint).
    Returns a dict with keys: ok, status_code, error, models.
    """
    api_key = (settings.SWIFTROUTER_API_KEY or "").strip()
    if not api_key:
        return {"ok": False, "error": "SWIFTROUTER_API_KEY not configured", "models": []}

    url = f"{settings.SWIFTROUTER_BASE_URL}/models"
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            response = await client.get(
                url,
                headers={"Authorization": f"Bearer {api_key}"},
            )
        if response.status_code == 200:
            data = response.json()
            model_ids = [m.get("id") for m in data.get("data", []) if m.get("id")]
            return {"ok": True, "status_code": 200, "error": None, "models": model_ids}
        return {
            "ok": False,
            "status_code": response.status_code,
            "error": response.text[:200],
            "models": [],
        }
    except httpx.TimeoutException:
        return {"ok": False, "error": "timeout", "models": []}
    except Exception as exc:
        return {"ok": False, "error": str(exc), "models": []}
