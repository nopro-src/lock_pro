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
#     def get_info(self):
#         return {
#             "app_name": "Smart Lock Face Pro",
#             "face_engine": "ArcFace",
#             "transport": "mqtt_stub",
#             "status": "running",
#         }
# system_service = SystemService()