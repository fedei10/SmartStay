from typing import Any

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


class HotelGuest(StrictSchema):
    occupancyNumber: int = Field(default=1, ge=1)
    firstName: str = Field(..., min_length=1)
    lastName: str = Field(..., min_length=1)
    email: str = Field(..., min_length=3)


class HotelHolder(StrictSchema):
    firstName: str = Field(..., min_length=1)
    lastName: str = Field(..., min_length=1)
    email: str = Field(..., min_length=3)


class HotelPayment(StrictSchema):
    method: str = "TRANSACTION_ID"
    transactionId: str = Field(..., min_length=1)


class HotelBookRequest(StrictSchema):
    prebookId: str = Field(..., min_length=1)
    holder: HotelHolder
    payment: HotelPayment
    guests: list[HotelGuest] = Field(..., min_length=1)


class ProviderResponse(StrictSchema):
    data: dict[str, Any]
