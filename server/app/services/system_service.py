from __future__ import annotations

from app.config import settings


class SystemService:
    def info(self) -> dict:
        return {
            "app_name": settings.APP_NAME,
            "env": settings.ENV,
            "face_model_key": settings.FACE_MODEL_KEY,
            "default_threshold": settings.FACE_DEFAULT_THRESHOLD,
        }