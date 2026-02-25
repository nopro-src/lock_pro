from pydantic import BaseModel
from datetime import datetime


class LogOut(BaseModel):
    id: int
    lock_id: int
    matched_account_id: int | None
    score: float
    success: bool
    source: str
    created_at: datetime