from __future__ import annotations

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.face.registry import FaceEngineRegistry
from app.config import settings
from app.face.insightface_arcface import InsightFaceArcFaceBuffaloL
from app.ws.manager import WsManager


_registry: FaceEngineRegistry | None = None


def get_face_registry() -> FaceEngineRegistry:
    global _registry
    if _registry is None:
        reg = FaceEngineRegistry()
        reg.register(InsightFaceArcFaceBuffaloL(model_key=settings.FACE_MODEL_KEY))
        _registry = reg
    return _registry


def preload_face_registry() -> None:
    get_face_registry()


def db_dep(db: Session = Depends(get_db)) -> Session:
    return db


def get_ws_manager(request: Request) -> WsManager:
    return request.app.state.ws_manager