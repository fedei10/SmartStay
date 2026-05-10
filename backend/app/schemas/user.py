from pydantic import BaseModel, EmailStr, ConfigDict


class UserCreate(BaseModel):
    name: str
    username: str
    email: EmailStr
    password: str


class UserRead(BaseModel):
    id: int
    name: str
    username: str
    email: EmailStr
    is_active: bool

    model_config = ConfigDict(from_attributes=True)