from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


class UserCreateIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(default="", max_length=255)
    is_active: bool = True

    lock_id: int = Field(ge=1)


class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    is_active: bool
    global_role: str