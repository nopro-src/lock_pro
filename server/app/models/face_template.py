from __future__ import annotations

from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, LargeBinary, String, Integer, Float, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class FaceTemplate(Base):
    __tablename__ = "face_templates"
    __table_args__ = (
        Index("ix_face_templates_lock_model", "lock_id", "model_key"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    lock_id: Mapped[int] = mapped_column(ForeignKey("locks.id"), nullable=False, index=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), nullable=False, index=True)

    model_key: Mapped[str] = mapped_column(String(128), nullable=False)
    embedding_dim: Mapped[int] = mapped_column(Integer, nullable=False)
    embedding_blob: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)

    shots_count: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    quality_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)