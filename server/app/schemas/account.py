from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


class UserCreateIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(default="", max_length=255)
    is_active: bool = True


class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    is_active: bool