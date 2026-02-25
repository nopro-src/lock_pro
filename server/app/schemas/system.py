from __future__ import annotations

from pydantic import BaseModel


class SystemInfoOut(BaseModel):
    app_name: str
    env: str
    face_model_key: str
    default_threshold: float