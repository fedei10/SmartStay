from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.schemas.base import EntityRead


class UserCreate(BaseModel):
    clerk_user_id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1, max_length=100)
    username: str = Field(..., min_length=1, max_length=50)
    email: EmailStr

    model_config = ConfigDict(extra="forbid")


class UserRead(EntityRead):
    clerk_user_id: str
    name: str
    username: str
    email: EmailStr
    is_active: bool
