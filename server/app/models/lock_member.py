from __future__ import annotations

from datetime import datetime
from enum import Enum
from sqlalchemy import DateTime, ForeignKey, Enum as SAEnum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class LockRole(str, Enum):
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    USER = "USER"


class LockMember(Base):
    __tablename__ = "lock_members"
    __table_args__ = (UniqueConstraint("lock_id", "account_id", name="uq_lock_member"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    lock_id: Mapped[int] = mapped_column(ForeignKey("locks.id"), nullable=False, index=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), nullable=False, index=True)
    role: Mapped[LockRole] = mapped_column(SAEnum(LockRole), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)