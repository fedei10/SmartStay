from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")


class FlightLeg(StrictSchema):
    origin: str = Field(..., min_length=3, max_length=3)
    destination: str = Field(..., min_length=3, max_length=3)
    date: str
    direction: Literal["OUTBOUND", "INBOUND"] | None = None
    filters: dict[str, Any] | None = None


class FlightSearchFilters(StrictSchema):
    arrivalTimeBefore: str | None = None
    cabinClass: str | None = None
    cabinClassMatch: Literal["exactly", "at_least"] | None = None
    changeableOnly: bool | None = None
    departureTimeBefore: str | None = None
    excludeConnectionAirports: list[str] | None = None
    excludeOvernight: bool | None = None
    flightNumbers: list[str] | None = None
    flightNumbersMatch: Literal["any", "all"] | None = None
    includesCarryOnBag: bool | None = None
    includesCheckedBag: bool | None = None
    legDurations: list[dict[str, Any]] | None = None
    maxDuration: int | None = Field(default=None, ge=1)
    maxPrice: float | None = Field(default=None, ge=0)
    minPrice: float | None = Field(default=None, ge=0)
    maxStops: int | None = Field(default=None, ge=-1, le=2)
    refundableOnly: bool | None = None
    showCheapestOfferOnly: bool | None = None


class FlightSort(StrictSchema):
    sortBy: Literal["price", "duration", "departure", "arrival", "stops"]
    sortOrder: Literal["asc", "desc"] = "asc"


class FlightSearchRequest(StrictSchema):
    legs: list[FlightLeg] = Field(..., min_length=1)
    adults: int = Field(default=1, ge=1)
    children: int = Field(default=0, ge=0)
    infants: int = Field(default=0, ge=0)
    childrenAges: list[int] | None = None
    infantAges: list[int] | None = None
    currency: str = Field(default="USD", min_length=3, max_length=3)
    country: str = Field(default="US", min_length=2, max_length=2)
    cabinClass: Literal["ECONOMY", "PREMIUM_ECONOMY", "BUSINESS", "FIRST"] | None = None
    maxStops: int | None = Field(default=None, ge=-1, le=2)
    filters: FlightSearchFilters | None = None
    sort: FlightSort | None = None


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
    selectedServices: list[dict[str, Any]] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def support_legacy_services_key(cls, value: Any):
        if isinstance(value, dict) and "selectedServices" not in value and "services" in value:
            normalized = dict(value)
            normalized["selectedServices"] = normalized.pop("services")
            return normalized
        return value


class FlightBookRequest(StrictSchema):
    prebookId: str = Field(..., min_length=1)
    payment: dict[str, Any] | None = None
    transactionId: str | None = Field(default=None, min_length=1)

    @model_validator(mode="after")
    def normalize_payment(self):
        if self.payment is not None:
            method = self.payment.get("method")
            transaction_id = self.payment.get("transactionId")
            if method == "TRANSACTION_ID" and not transaction_id:
                raise ValueError("payment.transactionId is required when payment.method is TRANSACTION_ID")
            if method not in {"TRANSACTION_ID", "CREDIT"}:
                raise ValueError("payment.method must be TRANSACTION_ID or CREDIT")
            return self

        if not self.transactionId:
            raise ValueError("transactionId is required when payment is not provided")

        self.payment = {
            "method": "TRANSACTION_ID",
            "transactionId": self.transactionId,
        }
        return self
