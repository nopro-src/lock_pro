from __future__ import annotations

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.face_template import FaceTemplate


class FaceTemplateRepo:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        lock_id: int,
        account_id: int,
        model_key: str,
        embedding_dim: int,
        embedding_blob: bytes,
        shots_count: int,
        quality_score: float,
    ) -> FaceTemplate:
        t = FaceTemplate(
            lock_id=lock_id,
            account_id=account_id,
            model_key=model_key,
            embedding_dim=embedding_dim,
            embedding_blob=embedding_blob,
            shots_count=shots_count,
            quality_score=quality_score,
        )
        self.db.add(t)
        self.db.flush()
        return t

    def list_by_lock_and_model(self, lock_id: int, model_key: str) -> list[FaceTemplate]:
        stmt = select(FaceTemplate).where(FaceTemplate.lock_id == lock_id, FaceTemplate.model_key == model_key)
        return list(self.db.execute(stmt).scalars().all())

    def list_by_lock_and_account(self, lock_id: int, account_id: int, model_key: str) -> list[FaceTemplate]:
        stmt = select(FaceTemplate).where(
            FaceTemplate.lock_id == lock_id,
            FaceTemplate.account_id == account_id,
            FaceTemplate.model_key == model_key,
        )
        return list(self.db.execute(stmt).scalars().all())