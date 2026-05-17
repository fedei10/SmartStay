from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")


class HotelOccupancy(StrictSchema):
    adults: int = Field(default=2, ge=1)
    children: list[int] | None = None


class HotelRatesRequest(StrictSchema):
    occupancies: list[HotelOccupancy] = Field(default_factory=lambda: [HotelOccupancy()])
    currency: str = Field(default="USD", min_length=3, max_length=3)
    guestNationality: str = Field(default="US", min_length=2, max_length=2)
    checkin: str
    checkout: str
    placeId: str | None = None
    aiSearch: str | None = None
    roomMapping: bool = True
    maxRatesPerHotel: int | None = 1
    includeHotelData: bool = True
    hotelIds: list[str] | None = None

    @model_validator(mode="after")
    def validate_search_target(self):
        if not self.placeId and not self.aiSearch and not self.hotelIds:
            raise ValueError("Provide placeId, aiSearch, or hotelIds")
        return self


class HotelPrebookRequest(StrictSchema):
    offerId: str = Field(..., min_length=1)
    usePaymentSdk: bool = True
    voucherCode: str | None = None
    addons: list[dict[str, Any]] | None = None
    bedTypeIds: list[int] | None = None
    includeCreditBalance: bool | None = None


class HotelGuest(StrictSchema):
    occupancyNumber: int = Field(default=1, ge=1)
    remarks: str | None = None
    firstName: str = Field(..., min_length=1)
    lastName: str = Field(..., min_length=1)
    email: str = Field(..., min_length=3)
    phone: str | None = None


class HotelHolder(StrictSchema):
    firstName: str = Field(..., min_length=1)
    lastName: str = Field(..., min_length=1)
    email: str = Field(..., min_length=3)
    phone: str | None = None


class HotelBookMetadata(StrictSchema):
    ip: str | None = None
    country: str | None = None
    language: str | None = None
    platform: str | None = None
    device_id: str | None = None
    user_agent: str | None = None
    utm_medium: str | None = None
    utm_source: str | None = None
    utm_campaign: str | None = None


class HotelGuestPaymentAddress(StrictSchema):
    city: str | None = None
    address: str | None = None
    country: str | None = None
    postal_code: str | None = None


class HotelGuestPayment(StrictSchema):
    phone: str = Field(..., min_length=1)
    method: str = Field(..., min_length=1)
    payee_last_name: str = Field(..., min_length=1)
    payee_first_name: str = Field(..., min_length=1)
    last_4_digits: str = Field(..., min_length=1)
    address: HotelGuestPaymentAddress | None = None


class HotelAccountPayment(StrictSchema):
    method: Literal["ACC_CREDIT_CARD", "WALLET", "CREDIT"]


class HotelTransactionPayment(StrictSchema):
    method: Literal["TRANSACTION_ID"]
    transactionId: str = Field(..., min_length=1)


class HotelBookRequest(StrictSchema):
    prebookId: str = Field(..., min_length=1)
    clientReference: str | None = None
    holder: HotelHolder
    guests: list[HotelGuest] = Field(..., min_length=1)
    metadata: HotelBookMetadata | None = None
    payment: HotelAccountPayment | HotelTransactionPayment
    guestPayment: HotelGuestPayment | None = None


class ProviderResponse(StrictSchema):
    data: dict[str, Any]
