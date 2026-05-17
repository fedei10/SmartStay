from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from app.db.database import AsyncSessionLocal
from app.db.user_profile_repository import UserProfileRepository
from app.schemas.base import success_response

router = APIRouter(prefix="/users", tags=["Users"])


class UserProfile(BaseModel):
    user_id: str
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    birthday: str | None = None          # YYYY-MM-DD
    nationality: str | None = None       # ISO 3166-1 alpha-2
    phone: str | None = None
    passport_number: str | None = None
    passport_expiry: str | None = None   # YYYY-MM-DD
    home_country: str | None = None      # ISO alpha-2, used for flight-first logic


def _serialize_profile(entity) -> dict:
    return {
        "user_id": entity.clerk_user_id,
        "first_name": entity.first_name,
        "last_name": entity.last_name,
        "email": entity.email,
        "birthday": entity.birthday,
        "nationality": entity.nationality,
        "phone": entity.phone,
        "passport_number": entity.passport_number,
        "passport_expiry": entity.passport_expiry,
        "home_country": entity.home_country,
    }


@router.post("/profile")
async def save_profile(profile: UserProfile, request: Request):
    deps = request.app.state.booking_deps
    data = deps.conversation_memory.sanitize_user_profile(profile.model_dump(exclude_none=True))
    if not data.get("user_id"):
        raise HTTPException(status_code=400, detail="user_id is required")

    async with AsyncSessionLocal() as db:
        repo = UserProfileRepository(db)
        entity = await repo.upsert_by_clerk_user_id(
            profile.user_id,
            {k: v for k, v in data.items() if k != "user_id"},
        )

    await deps.conversation_memory.set_user_profile(profile.user_id, data)
    return success_response(message="profile saved", data=_serialize_profile(entity))


@router.get("/profile/{user_id}")
async def get_profile(user_id: str, request: Request):
    deps = request.app.state.booking_deps
    profile = await deps.conversation_memory.get_user_profile(user_id)
    if not profile:
        async with AsyncSessionLocal() as db:
            repo = UserProfileRepository(db)
            entity = await repo.get_by_clerk_user_id(user_id)
        if entity is not None:
            profile = _serialize_profile(entity)
            await deps.conversation_memory.set_user_profile(user_id, profile)
    return success_response(message="profile fetched", data=profile)
