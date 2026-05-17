from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.base import EntityRead


BookingType = Literal["HOTEL", "FLIGHT", "PACKAGE"]
BookingStatus = Literal[
    "SEARCHING",
    "SELECTED",
    "VERIFIED",
    "PREBOOKED",
    "SERVICES_ATTACHED",
    "PAYMENT_PENDING",
    "PAYMENT_CONFIRMED",
    "BOOKING",
    "CONFIRMED",
    "FAILED",
    "EXPIRED",
]


class BookingSessionCreate(BaseModel):
    clerk_user_id: str = Field(..., min_length=1)
    booking_type: BookingType
    status: BookingStatus = "SEARCHING"
    offer_id: str | None = None
    prebook_id: str | None = None
    transaction_id: str | None = None
    secret_key: str | None = None
    verified_price: float | None = None
    currency: str | None = Field(default=None, min_length=3, max_length=8)
    provider_payload: dict[str, Any] | None = None

    model_config = ConfigDict(extra="forbid")


class BookingSessionUpdate(BaseModel):
    status: BookingStatus | None = None
    offer_id: str | None = None
    prebook_id: str | None = None
    transaction_id: str | None = None
    secret_key: str | None = None
    verified_price: float | None = None
    currency: str | None = Field(default=None, min_length=3, max_length=8)
    provider_payload: dict[str, Any] | None = None

    model_config = ConfigDict(extra="forbid")


class BookingSessionRead(EntityRead):
    clerk_user_id: str
    booking_type: BookingType
    status: BookingStatus
    offer_id: str | None = None
    prebook_id: str | None = None
    transaction_id: str | None = None
    secret_key: str | None = None
    verified_price: float | None = None
    currency: str | None = None
    provider_payload: dict[str, Any] | None = None


class BookingCreate(BaseModel):
    clerk_user_id: str = Field(..., min_length=1)
    session_id: int | None = None
    booking_type: Literal["HOTEL", "FLIGHT"]
    provider_booking_id: str = Field(..., min_length=1)
    provider_reference: str | None = None
    status: str = Field(..., min_length=1)
    total_charged: float | None = None
    currency: str | None = Field(default=None, min_length=3, max_length=8)
    provider_payload: dict[str, Any] | None = None

    model_config = ConfigDict(extra="forbid")


class BookingRead(EntityRead):
    clerk_user_id: str
    session_id: int | None = None
    booking_type: Literal["HOTEL", "FLIGHT"]
    provider_booking_id: str
    provider_reference: str | None = None
    status: str
    total_charged: float | None = None
    currency: str | None = None
    provider_payload: dict[str, Any] | None = None
