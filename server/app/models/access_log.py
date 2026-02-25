from __future__ import annotations

from datetime import datetime
from enum import Enum
from sqlalchemy import DateTime, ForeignKey, Float, Boolean, String, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AccessSource(str, Enum):
    web = "web"
    mobile = "mobile"
    device = "device"


class AccessLog(Base):
    __tablename__ = "access_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    lock_id: Mapped[int] = mapped_column(ForeignKey("locks.id"), nullable=False, index=True)
    matched_account_id: Mapped[int | None] = mapped_column(ForeignKey("accounts.id"), nullable=True, index=True)

    score: Mapped[float] = mapped_column(Float, nullable=False)
    threshold_used: Mapped[float] = mapped_column(Float, nullable=False)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False)

    source: Mapped[AccessSource] = mapped_column(SAEnum(AccessSource), nullable=False)
    device_id: Mapped[int | None] = mapped_column(ForeignKey("devices.id"), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)