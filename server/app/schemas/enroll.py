from __future__ import annotations

from pydantic import BaseModel, Field, model_validator


class EnrollIn(BaseModel):
    lock_id: int
    account_id: int | None = None
    target_account_id: int | None = None

    images_base64: list[str] = Field(min_length=5)

    @model_validator(mode="after")
    def _normalize(self):
        # allow either account_id or target_account_id
        if self.target_account_id is None and self.account_id is not None:
            self.target_account_id = self.account_id

        if self.target_account_id is None:
            raise ValueError("Missing target_account_id (or account_id)")

        return self


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