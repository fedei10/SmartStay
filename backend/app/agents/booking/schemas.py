from pydantic import BaseModel, Field


class SearchExtraction(BaseModel):
    wants_hotel_search: bool = Field(default=True)
    city_name: str | None = None
    country_code: str | None = None
