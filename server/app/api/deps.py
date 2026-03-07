from __future__ import annotations

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.face.registry import FaceEngineRegistry
from app.config import settings
from app.face.insightface_arcface import InsightFaceArcFaceBuffaloL


_registry: FaceEngineRegistry | None = None


def get_face_registry() -> FaceEngineRegistry:
    global _registry
    if _registry is None:
        reg = FaceEngineRegistry()
        reg.register(InsightFaceArcFaceBuffaloL(model_key=settings.FACE_MODEL_KEY))
        _registry = reg
    return _registry


def db_dep(db: Session = Depends(get_db)) -> Session:
    return db