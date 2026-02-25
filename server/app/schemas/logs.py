from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel


class AccessLogOut(BaseModel):
    id: int
    lock_id: int
    matched_account_id: int | None
    score: float
    threshold_used: float
    success: bool
    source: str
    device_id: int | None
    created_at: datetime