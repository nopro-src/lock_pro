from __future__ import annotations

from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Lock(Base):
    __tablename__ = "locks"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)  # pairing code
    owner_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), nullable=False)
    threshold_override: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    owner = relationship("Account")