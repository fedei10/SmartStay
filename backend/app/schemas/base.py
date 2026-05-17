from datetime import datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field


T = TypeVar("T")


class EntityRead(BaseModel):
    id: int
    is_default: bool = False
    can_deleted: bool = True
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True, extra="ignore")


class Pagination(BaseModel):
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1)
    total: int = Field(default=0, ge=0)

    model_config = ConfigDict(extra="forbid")


class PaginatedData(BaseModel, Generic[T]):
    items: list[T]
    pagination: Pagination

    model_config = ConfigDict(extra="forbid")


class ApiResponse(BaseModel, Generic[T]):
    code: int
    message: str
    data: T | None = None

    model_config = ConfigDict(extra="forbid")


def success_response(
    data: Any = None,
    message: str = "success",
    code: int = 200,
) -> dict[str, Any]:
    return {
        "code": code,
        "message": message,
        "data": data,
    }


def error_response(
    message: str,
    code: int = 400,
    data: Any = None,
) -> dict[str, Any]:
    return {
        "code": code,
        "message": message,
        "data": data,
    }
