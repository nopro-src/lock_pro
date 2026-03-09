from __future__ import annotations

from pydantic import BaseModel, Field
from app.models.lock_member import LockRole
from typing import Optional
from datetime import datetime


class LockCreateIn(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    code: str = Field(min_length=6, max_length=64)
    threshold_override: float | None = Field(default=None, ge=0.1, le=0.99)


class LockOut(BaseModel):
    id: int
    name: str
    code: str
    owner_id: int
    threshold_override: float | None


class MemberAddIn(BaseModel):
    account_id: int
    role: LockRole


class MemberOut(BaseModel):
    id: int
    lock_id: int
    account_id: int
    role: LockRole
# class LockDashboardOut(BaseModel):
#     id: int
#     name: str
#     location: Optional[str] = None
#     status: Optional[str] = None
#     device_status: Optional[str] = None
#     last_seen_at: Optional[datetime] = None
#     member_count: int = 0