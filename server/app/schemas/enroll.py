from __future__ import annotations

from pydantic import BaseModel, Field


class EnrollIn(BaseModel):
    lock_id: int
    account_id: int
    images_base64: list[str] = Field(min_length=5)


class EnrollOut(BaseModel):
    template_id: int
    model_key: str
    shots_count: int
    quality_score: float


class VerifyIn(BaseModel):
    lock_id: int
    image_base64: str
    source: str = Field(default="web")  # web/mobile/device
    device_uid: str | None = None


class VerifyOut(BaseModel):
    success: bool
    matched_account_id: int | None
    score: float
    threshold_used: float