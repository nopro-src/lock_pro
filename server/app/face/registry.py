from __future__ import annotations

from typing import Dict
from app.face.engine_base import FaceEngineBase


class FaceEngineRegistry:
    def __init__(self):
        self._engines: Dict[str, FaceEngineBase] = {}

    def register(self, engine: FaceEngineBase) -> None:
        self._engines[engine.model_key] = engine

    def get(self, model_key: str) -> FaceEngineBase:
        if model_key not in self._engines:
            raise RuntimeError(f"Face engine not registered for model_key={model_key}")
        return self._engines[model_key]