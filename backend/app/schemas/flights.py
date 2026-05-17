from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")


class FlightLeg(StrictSchema):
    origin: str = Field(..., min_length=3, max_length=3)
    destination: str = Field(..., min_length=3, max_length=3)
    date: str
    direction: Literal["OUTBOUND", "INBOUND"] | None = None


class FlightSearchRequest(StrictSchema):
    legs: list[FlightLeg] = Field(..., min_length=1)
    adults: int = Field(default=1, ge=1)
    children: int = Field(default=0, ge=0)
    infants: int = Field(default=0, ge=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    country: str = Field(default="US", min_length=2, max_length=2)
    cabin: str | None = None


class FlightVerifyRequest(StrictSchema):
    offerId: str = Field(..., min_length=1)


class PassengerDocument(StrictSchema):
    type: str = "PASSPORT"
    number: str = Field(..., min_length=1)
    issuingCountry: str = Field(..., min_length=2, max_length=2)
    nationality: str = Field(..., min_length=2, max_length=2)
    expirationDate: str = Field(..., min_length=1)


class FlightContact(StrictSchema):
    firstName: str = Field(..., min_length=1)
    lastName: str = Field(..., min_length=1)
    email: str = Field(..., min_length=3)
    phone: str = Field(..., min_length=5)


class FlightPassenger(StrictSchema):
    type: str = "ADT"
    firstName: str = Field(..., min_length=1)
    lastName: str = Field(..., min_length=1)
    birthday: str = Field(..., min_length=1)
    gender: str = Field(..., min_length=1)
    document: PassengerDocument | None = None


class FlightPrebookRequest(StrictSchema):
    offerId: str = Field(..., min_length=1)
    usePaymentSdk: bool = True
    contact: FlightContact
    passengers: list[FlightPassenger] = Field(..., min_length=1)

    @model_validator(mode="after")
    def require_adult_passenger_details(self):
        missing_documents = [
            passenger.firstName
            for passenger in self.passengers
            if passenger.document is None
        ]
        if missing_documents:
            raise ValueError("Passenger document details are required before flight prebook")
        return self


class FlightAttachServicesRequest(StrictSchema):
    services: list[dict[str, Any]] = Field(default_factory=list)


class FlightBookRequest(StrictSchema):
    prebookId: str = Field(..., min_length=1)
    transactionId: str = Field(..., min_length=1)
