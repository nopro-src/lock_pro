from app.face.base import FaceEngineBase
from app.face.engines.insightface_arcface import InsightFaceArcFaceEngine


def get_engine(model_key: str) -> FaceEngineBase:
    # Map model_key -> engine
    if model_key == "insightface_arcface_buffalo_l_v1":
        return InsightFaceArcFaceEngine(model_key=model_key)
    raise ValueError(f"Unknown MODEL_KEY: {model_key}")