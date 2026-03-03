from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "Smart Lock Face Pro"
    ENV: str = Field(default="dev")  # dev | prod
    DEBUG: bool = Field(default=False)

    # Security
    JWT_SECRET_KEY: str = Field(default="CHANGE_ME_SUPER_SECRET")
    JWT_ALG: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=14)

    # Database
    DATABASE_URL: str = Field(default="sqlite:///./dev.db")

    # Face
    FACE_MODEL_KEY: str = Field(default="insightface_arcface_buffalo_l_v1")
    FACE_DEFAULT_THRESHOLD: float = Field(default=0.70)
    FACE_TOP_K: int = Field(default=3)
    FACE_ENROLL_SHOTS_MIN: int = Field(default=5)

    # Quality gates
    QUALITY_MIN_BRIGHTNESS: float = Field(default=60.0)
    QUALITY_MAX_BRIGHTNESS: float = Field(default=200.0)
    QUALITY_MIN_FACE_AREA_RATIO: float = Field(default=0.05)
    QUALITY_MAX_BLUR_LAPLACIAN_VAR: float = Field(default=80.0)
    QUALITY_MAX_POSE_YAW_DEG: float = Field(default=25.0)
    QUALITY_MAX_POSE_PITCH_DEG: float = Field(default=20.0)

    # Web (legacy + new split UIs)
    STATIC_ADMIN_DIR: str = Field(default="../web/admin")
    STATIC_OWNER_DIR: str = Field(default="../web/owner")
    STATIC_USER_DIR: str = Field(default="../web/user")

    # Device / transport
    DEVICE_TRANSPORT: str = Field(default="mqtt_stub")  # mqtt_stub | mqtt | http

    # Logging
    LOG_LEVEL: str = Field(default="INFO")


settings = Settings()