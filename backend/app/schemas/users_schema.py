from datetime import datetime
from typing import Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
)

from app.utils.validate_password import (
    validate_password as validate_password_strength,
)


# ==================================================
# User
# ==================================================

class UserBase(BaseModel):
    name: str = Field(..., max_length=255)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(
        ...,
        min_length=8,
        max_length=255,
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        return validate_password_strength(value)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = Field(
        None,
        max_length=255,
    )

    email: Optional[EmailStr] = None

    password: Optional[str] = Field(
        None,
        min_length=8,
        max_length=255,
    )


class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


# ==================================================
# Authentication
# ==================================================

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AuthResponse(Token):
    user: UserResponse