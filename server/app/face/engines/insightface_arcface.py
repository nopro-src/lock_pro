import numpy as np
from app.face.base import FaceEngineBase
from app.core.exceptions import bad_request


class InsightFaceArcFaceEngine(FaceEngineBase):
    """
    Uses insightface.app.FaceAnalysis with buffalo_l (ArcFace).
    Detect + align + embedding.
    """

    def __init__(self, model_key: str) -> None:
        self._model_key = model_key
        try:
            from insightface.app import FaceAnalysis  # type: ignore
        except Exception as e:
            raise RuntimeError(
                "InsightFace is not available. Please install insightface + onnxruntime."
            ) from e

        # ctx_id = 0 if GPU; -1 for CPU
        self._app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
        self._app.prepare(ctx_id=-1, det_size=(640, 640))

        # buffalo_l embed dim is usually 512
        self._dim = 512

    @property
    def model_key(self) -> str:
        return self._model_key

    @property
    def dim(self) -> int:
        return self._dim

    def embed(self, bgr_image: np.ndarray) -> np.ndarray:
        faces = self._app.get(bgr_image)
        if not faces:
            raise bad_request("No face detected")

        # pick the biggest face
        faces = sorted(faces, key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1]), reverse=True)
        emb = faces[0].embedding.astype(np.float32)

        # normalize
        norm = np.linalg.norm(emb) + 1e-12
        emb = emb / norm
        return emb