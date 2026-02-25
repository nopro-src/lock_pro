from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, DateTime, ForeignKey, Boolean, LargeBinary, Float, UniqueConstraint
from datetime import datetime
from typing import Optional, List


class Base(DeclarativeBase):
    pass


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(255), default="")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    memberships: Mapped[List["LockMember"]] = relationship(back_populates="account", cascade="all, delete-orphan")
    templates: Mapped[List["FaceTemplate"]] = relationship(back_populates="account", cascade="all, delete-orphan")


class Lock(Base):
    __tablename__ = "locks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    code: Mapped[str] = mapped_column(String(64), unique=True, index=True)  # pair code for ESP32 later
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    members: Mapped[List["LockMember"]] = relationship(back_populates="lock", cascade="all, delete-orphan")
    templates: Mapped[List["FaceTemplate"]] = relationship(back_populates="lock", cascade="all, delete-orphan")


class LockMember(Base):
    __tablename__ = "lock_members"
    __table_args__ = (UniqueConstraint("lock_id", "account_id", name="uq_lock_account"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    lock_id: Mapped[int] = mapped_column(ForeignKey("locks.id", ondelete="CASCADE"))
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id", ondelete="CASCADE"))
    role: Mapped[str] = mapped_column(String(20))  # OWNER | USER
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    lock: Mapped["Lock"] = relationship(back_populates="members")
    account: Mapped["Account"] = relationship(back_populates="memberships")


class FaceTemplate(Base):
    __tablename__ = "face_templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    lock_id: Mapped[int] = mapped_column(ForeignKey("locks.id", ondelete="CASCADE"), index=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id", ondelete="CASCADE"), index=True)

    model_key: Mapped[str] = mapped_column(String(128), index=True)
    dim: Mapped[int] = mapped_column(Integer)
    embedding: Mapped[bytes] = mapped_column(LargeBinary)

    # optional meta
    shots: Mapped[int] = mapped_column(Integer, default=5)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    lock: Mapped["Lock"] = relationship(back_populates="templates")
    account: Mapped["Account"] = relationship(back_populates="templates")


class AccessLog(Base):
    __tablename__ = "access_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    lock_id: Mapped[int] = mapped_column(ForeignKey("locks.id", ondelete="CASCADE"), index=True)

    matched_account_id: Mapped[Optional[int]] = mapped_column(ForeignKey("accounts.id", ondelete="SET NULL"), nullable=True)
    score: Mapped[float] = mapped_column(Float, default=0.0)
    success: Mapped[bool] = mapped_column(Boolean, default=False)

    # source = web | mobile | esp32 (future)
    source: Mapped[str] = mapped_column(String(32), default="web")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)