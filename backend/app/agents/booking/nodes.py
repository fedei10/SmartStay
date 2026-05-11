from langchain_core.runnables import RunnableConfig

from app.agents.booking.dependencies import BookingDeps
from app.agents.booking.schemas import SearchExtraction
from app.agents.booking.state import BookingState


COUNTRY_ALIASES = {
    "italy": "IT",
    "rome": "IT",
    "france": "FR",
    "paris": "FR",
    "spain": "ES",
    "barcelona": "ES",
    "madrid": "ES",
    "united states": "US",
    "usa": "US",
    "new york": "US",
}


def _deps(config: RunnableConfig) -> BookingDeps:
    configurable = config.get("configurable", {})
    deps = configurable.get("deps")
    if deps is None:
        raise ValueError("Booking dependencies are not configured")
    return deps


def _fallback_extract(message: str) -> SearchExtraction:
    normalized = message.lower()
    city_name = None
    country_code = None

    for token, code in COUNTRY_ALIASES.items():
        if token in normalized:
            country_code = code
            if token not in {"italy", "france", "spain", "united states", "usa"}:
                city_name = token.title()
            break

    return SearchExtraction(
        wants_hotel_search="hotel" in normalized or "stay" in normalized,
        city_name=city_name,
        country_code=country_code,
    )


async def parse_intent(state: BookingState, config: RunnableConfig):
    deps = _deps(config)
    user_message = state.get("user_message", "")

    if deps.llm is None:
        extracted = _fallback_extract(user_message)
    else:
        structured_llm = deps.llm.with_structured_output(SearchExtraction)
        extracted = await structured_llm.ainvoke(
            "Extract hotel search slots from the user message. "
            "Use ISO 3166-1 alpha-2 country codes. "
            f"User message: {user_message}"
        )

    return {
        "city_name": extracted.city_name,
        "country_code": extracted.country_code,
    }


async def validate_slots(state: BookingState):
    missing = []
    if not state.get("city_name"):
        missing.append("city")
    if not state.get("country_code"):
        missing.append("country")

    if missing:
        return {
            "next_action": "ask_clarification",
            "response": f"I need the {', '.join(missing)} before I can search hotels.",
        }

    return {
        "next_action": "search_hotels",
    }


async def search_hotels(state: BookingState, config: RunnableConfig):
    deps = _deps(config)
    try:
        result = await deps.liteapi.search_hotels_by_city(
            country_code=state["country_code"],
            city_name=state["city_name"],
        )
    except Exception as exc:
        return {
            "next_action": "error",
            "error_message": str(exc),
            "response": "I could not search hotels right now. Please try again.",
        }

    hotels = result.get("hotels", [])
    if not hotels:
        return {
            "next_action": "error",
            "response": "I did not find hotels for that destination.",
            "hotels": [],
        }

    return {
        "next_action": "show_hotels",
        "hotels": hotels,
    }


async def generate_response(state: BookingState):
    hotels = state.get("hotels", [])
    lines = [
        f"Here are hotels in {state.get('city_name')}:",
        "",
    ]
    for index, hotel in enumerate(hotels, start=1):
        rating = hotel.get("rating")
        stars = hotel.get("stars")
        details = []
        if stars:
            details.append(f"{stars} stars")
        if rating:
            details.append(f"rated {rating}")
        suffix = f" ({', '.join(details)})" if details else ""
        lines.append(f"{index}. {hotel.get('name')}{suffix}")

    return {
        "response": "\n".join(lines),
    }
