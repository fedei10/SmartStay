## ttrip backend architecture

ttrip uses FastAPI as the backend gateway for a travel-booking microservice
architecture. The gateway owns HTTP routing, request validation, AI orchestration,
and server-side secret injection. Specialized service modules own provider calls
and can later be split into independently deployed services.

### Current service boundaries

- Travel orchestration: `app/agents/booking/travel_orchestrator.py`
- Hotel agent boundary: `app/agents/booking/hotel_agent.py`
- Flight agent boundary: `app/agents/booking/flight_agent.py`
- Insurance agent boundary: `app/agents/booking/insurance_agent.py`
- LiteAPI shared client: `app/services/liteapi_service.py`
- LiteAPI hotel provider service: `app/services/liteapi_hotels_service.py`
- LiteAPI flight provider service: `app/services/liteapi_flights_service.py`

The chat endpoint routes user intent through a LangGraph parent graph. The
`travel_orchestrator` node uses Groq structured output to decide which sub-agent
node should run next; routing is not based on static keyword matching. Provider
calls stay behind service clients or MCP adapters, not inside frontend code.
LiteAPI tool access is configured under `app/coreAgents/mcp` and loaded through
`app/coreAgents/tools/liteapi.py` with LangChain's `MultiServerMCPClient`.

### Gateway routes

- `POST /api/v1/chat`
- `GET /api/v1/hotels/places`
- `POST /api/v1/hotels/rates`
- `POST /api/v1/hotels/prebook`
- `POST /api/v1/hotels/book`
- `GET /api/v1/hotels/{hotel_id}`
- `POST /api/v1/flights/search`
- `POST /api/v1/flights/verify`
- `POST /api/v1/flights/prebook`
- `POST /api/v1/flights/prebooks/{prebook_id}/services`
- `POST /api/v1/flights/book`
- `GET /api/v1/flights/bookings/{booking_id}`
- `GET /api/v1/flights/bookings`

### LiteAPI rules

All LiteAPI calls are server-side. The API key is loaded from `.env` through
Pydantic settings and sent as `X-API-Key`. The frontend must call ttrip
backend routes and must never call LiteAPI directly.

Flight booking is intentionally stricter than hotel booking. Flight offers must
be verified before prebook, stale `offerId` values must not be reused, and
booking must use the latest `transactionId` after prebook or service attachment.

### Entity conventions

Persisted entities should inherit the shared SQLAlchemy mixins when they need
standard lifecycle fields:

- `is_default`
- `can_deleted`
- `created_at`
- `updated_at`
- `deleted_at`

Use `app.db.repository.BaseRepository` for the common data access
surface:

- `get__all`
- `get_by_id`
- `store`
- `update`
- `soft_deleted`
- `restore`
- `hard_soft_deleted`
- `get_all_soft_deleted`

### API response shape

HTTP routes should return the shared envelope:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

For list endpoints, nest items and pagination under `data`:

```json
{
  "code": 200,
  "message": "items fetched",
  "data": {
    "items": [],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 0
    }
  }
}
```

### Auth boundary

User authentication is owned by Clerk. Backend user records should store the
Clerk user id (`clerk_user_id`) and should not own password hashing for normal
application users. When the Next.js frontend is created, use App Router and
Clerk's current `clerkMiddleware()` plus `<ClerkProvider>` setup.

### Pydantic v2 rules

Schemas use Pydantic v2 only:

- Use `model_config = ConfigDict(...)`.
- Use `model_dump(...)` when converting schemas to dictionaries.
- Use `model_validate(...)` when validating external objects.
- Use `extra="forbid"` for API request schemas.
- Use `from_attributes=True` for ORM read schemas.
