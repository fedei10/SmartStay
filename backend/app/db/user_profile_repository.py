from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repository import BaseRepository
from app.models.user_profile import UserProfile


class UserProfileRepository(BaseRepository[UserProfile]):
    def __init__(self, session: AsyncSession):
        super().__init__(UserProfile, session)

    async def get_by_clerk_user_id(self, clerk_user_id: str) -> UserProfile | None:
        result = await self.session.execute(
            select(UserProfile).where(
                UserProfile.clerk_user_id == clerk_user_id,
                UserProfile.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def upsert_by_clerk_user_id(
        self,
        clerk_user_id: str,
        data: dict,
    ) -> UserProfile:
        profile = await self.get_by_clerk_user_id(clerk_user_id)
        if profile is None:
            payload = {"clerk_user_id": clerk_user_id, **data}
            return await self.store(payload)

        for field, value in data.items():
            setattr(profile, field, value)

        await self.session.commit()
        await self.session.refresh(profile)
        return profile
