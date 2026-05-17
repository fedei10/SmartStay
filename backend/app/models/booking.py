from typing import Any

from sqlalchemy import JSON, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models import Base, EntityStateMixin, TimestampMixin


class BookingSession(Base, TimestampMixin, EntityStateMixin):
    __tablename__ = "booking_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    clerk_user_id: Mapped[str] = mapped_column(String(255), index=True)
    booking_type: Mapped[str] = mapped_column(String(32), index=True)
    status: Mapped[str] = mapped_column(String(64), index=True)
    offer_id: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    prebook_id: Mapped[str | None] = mapped_column(String(512), nullable=True)
    transaction_id: Mapped[str | None] = mapped_column(String(512), nullable=True)
    secret_key: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    currency: Mapped[str | None] = mapped_column(String(8), nullable=True)
    verified_price: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    provider_payload: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)


class Booking(Base, TimestampMixin, EntityStateMixin):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    session_id: Mapped[int | None] = mapped_column(
        ForeignKey("booking_sessions.id"),
        nullable=True,
        index=True,
    )
    clerk_user_id: Mapped[str] = mapped_column(String(255), index=True)
    booking_type: Mapped[str] = mapped_column(String(32), index=True)
    provider_booking_id: Mapped[str] = mapped_column(String(512), index=True)
    provider_reference: Mapped[str | None] = mapped_column(String(512), nullable=True)
    status: Mapped[str] = mapped_column(String(64), index=True)
    total_charged: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    currency: Mapped[str | None] = mapped_column(String(8), nullable=True)
    provider_payload: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
