from __future__ import annotations

from datetime import datetime
from enum import Enum
from sqlalchemy import DateTime, ForeignKey, String, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DeviceStatus(str, Enum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    UNKNOWN = "UNKNOWN"


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(primary_key=True)
    lock_id: Mapped[int] = mapped_column(ForeignKey("locks.id"), nullable=False, index=True)

    device_uid: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    firmware_version: Mapped[str] = mapped_column(String(64), default="", nullable=False)
    status: Mapped[DeviceStatus] = mapped_column(SAEnum(DeviceStatus), default=DeviceStatus.UNKNOWN, nullable=False)
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)