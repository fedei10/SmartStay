from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repository import BaseRepository
from app.models.booking import Booking


class BookingDBRepository(BaseRepository[Booking]):
    def __init__(self, session: AsyncSession):
        super().__init__(Booking, session)

    async def list_for_user(
        self,
        user_id: str,
        booking_type: str | None = None,
        page: int = 1,
        per_page: int = 50,
    ) -> tuple[list[Booking], int]:
        base_filter = [
            Booking.clerk_user_id == user_id,
            Booking.deleted_at.is_(None),
        ]
        if booking_type:
            base_filter.append(Booking.booking_type == booking_type.upper())

        query = (
            select(Booking)
            .where(*base_filter)
            .order_by(Booking.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        count_q = select(func.count()).select_from(Booking).where(*base_filter)

        result = await self.session.execute(query)
        total = await self.session.scalar(count_q)
        return list(result.scalars().all()), int(total or 0)

    async def get_by_reference(self, reference: str, user_id: str) -> Booking | None:
        for col in (Booking.provider_booking_id, Booking.provider_reference):
            result = await self.session.execute(
                select(Booking)
                .where(
                    col == reference,
                    Booking.clerk_user_id == user_id,
                    Booking.deleted_at.is_(None),
                )
                .order_by(Booking.created_at.desc())
            )
            booking = result.scalars().first()
            if booking:
                return booking
        return None

    async def cancel_by_reference(
        self,
        reference: str,
        user_id: str,
        *,
        status: str = "CANCELLED",
        cancellation: dict | None = None,
    ) -> Booking | None:
        booking = await self.get_by_reference(reference, user_id)
        if not booking:
            return None
        booking.status = status
        if cancellation:
            booking.provider_payload = {
                **(booking.provider_payload or {}),
                "cancellation": cancellation,
            }
        await self.session.commit()
        await self.session.refresh(booking)
        return booking
