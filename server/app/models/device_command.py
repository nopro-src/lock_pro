from __future__ import annotations

from datetime import datetime
from enum import Enum
from sqlalchemy import DateTime, ForeignKey, String, Enum as SAEnum, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CommandType(str, Enum):
    OPEN = "OPEN"
    DENY = "DENY"
    ALARM = "ALARM"


class DeviceCommand(Base):
    __tablename__ = "device_commands"

    id: Mapped[int] = mapped_column(primary_key=True)
    lock_id: Mapped[int] = mapped_column(ForeignKey("locks.id"), nullable=False, index=True)

    command_type: Mapped[CommandType] = mapped_column(SAEnum(CommandType), nullable=False)
    payload_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)