from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models import Base, EntityStateMixin, TimestampMixin


class UserProfile(Base, TimestampMixin, EntityStateMixin):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    clerk_user_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    first_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    birthday: Mapped[str | None] = mapped_column(String(32), nullable=True)
    nationality: Mapped[str | None] = mapped_column(String(8), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(64), nullable=True)
    passport_number: Mapped[str | None] = mapped_column(String(64), nullable=True)
    passport_expiry: Mapped[str | None] = mapped_column(String(32), nullable=True)
    home_country: Mapped[str | None] = mapped_column(String(8), nullable=True)
