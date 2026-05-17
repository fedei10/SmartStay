import pytest

from app.services.liteapi_service import LiteAPIService


@pytest.mark.asyncio
async def test_liteapi_request_handles_empty_204_response(monkeypatch):
    class Response:
        status_code = 204
        content = b""

        def raise_for_status(self):
            return None

        def json(self):
            raise AssertionError("json should not be called for empty 204 responses")

    class AsyncClient:
        def __init__(self, timeout):
            self.timeout = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

        async def request(self, *args, **kwargs):
            return Response()

    monkeypatch.setattr("app.services.liteapi_service.httpx.AsyncClient", AsyncClient)

    result = await LiteAPIService(api_key="test-key").request(
        "PUT",
        "/bookings/bk_123",
        booking_api=True,
    )

    assert result == {}
