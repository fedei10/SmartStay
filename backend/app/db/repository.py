from datetime import UTC, datetime
from typing import Any, Generic, TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Base


ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    def __init__(self, model: type[ModelT], session: AsyncSession):
        self.model = model
        self.session = session

    async def get__all(
        self,
        *,
        page: int = 1,
        per_page: int = 20,
        include_deleted: bool = False,
    ) -> tuple[list[ModelT], int]:
        query = select(self.model)
        count_query = select(func.count()).select_from(self.model)

        if hasattr(self.model, "deleted_at") and not include_deleted:
            query = query.where(self.model.deleted_at.is_(None))
            count_query = count_query.where(self.model.deleted_at.is_(None))

        result = await self.session.execute(
            query.offset((page - 1) * per_page).limit(per_page)
        )
        total = await self.session.scalar(count_query)
        return list(result.scalars().all()), int(total or 0)

    async def get_by_id(
        self,
        entity_id: int,
        *,
        include_deleted: bool = False,
    ) -> ModelT | None:
        query = select(self.model).where(self.model.id == entity_id)
        if hasattr(self.model, "deleted_at") and not include_deleted:
            query = query.where(self.model.deleted_at.is_(None))

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def store(self, data: dict[str, Any]) -> ModelT:
        entity = self.model(**data)
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def update(self, entity_id: int, data: dict[str, Any]) -> ModelT | None:
        entity = await self.get_by_id(entity_id)
        if entity is None:
            return None

        for field, value in data.items():
            setattr(entity, field, value)

        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def soft_deleted(self, entity_id: int) -> ModelT | None:
        entity = await self.get_by_id(entity_id)
        if entity is None or not hasattr(entity, "deleted_at"):
            return None
        if hasattr(entity, "can_deleted") and not entity.can_deleted:
            return None

        entity.deleted_at = datetime.now(UTC)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def restore(self, entity_id: int) -> ModelT | None:
        entity = await self.get_by_id(entity_id, include_deleted=True)
        if entity is None or not hasattr(entity, "deleted_at"):
            return None

        entity.deleted_at = None
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def get_all_soft_deleted(
        self,
        *,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list[ModelT], int]:
        if not hasattr(self.model, "deleted_at"):
            return [], 0

        query = select(self.model).where(self.model.deleted_at.is_not(None))
        count_query = select(func.count()).select_from(self.model).where(
            self.model.deleted_at.is_not(None)
        )
        result = await self.session.execute(
            query.offset((page - 1) * per_page).limit(per_page)
        )
        total = await self.session.scalar(count_query)
        return list(result.scalars().all()), int(total or 0)

    async def hard_soft_deleted(self, entity_id: int) -> bool:
        entity = await self.get_by_id(entity_id, include_deleted=True)
        if entity is None:
            return False
        if hasattr(entity, "can_deleted") and not entity.can_deleted:
            return False

        await self.session.delete(entity)
        await self.session.commit()
        return True
