from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List


class Settings(BaseSettings):
    APP_NAME: str = "smart-lock-face"
    ENV: str = "dev"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: str = "http://localhost:8000"

    DB_URL: str = "sqlite:///./smart_lock_face.db"

    JWT_SECRET: str = "CHANGE_ME"
    JWT_ALG: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    MODEL_KEY: str = "insightface_arcface_buffalo_l_v1"
    THRESH: float = 0.70

    ENROLL_SHOTS: int = 5

    @field_validator("CORS_ORIGINS")
    @classmethod
    def _split_origins(cls, v: str) -> str:
        return v

    def cors_origins_list(self) -> List[str]:
        return [x.strip() for x in self.CORS_ORIGINS.split(",") if x.strip()]


settings = Settings()