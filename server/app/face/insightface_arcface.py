from __future__ import annotations

import numpy as np

from app.face.engine_base import FaceEngineBase


class InsightFaceArcFaceBuffaloL(FaceEngineBase):
    def __init__(self, model_key: str = "insightface_arcface_buffalo_l_v1"):
        self._model_key = model_key
        self._app = None
        self._dim = 512

        try:
            from insightface.app import FaceAnalysis  # type: ignore
        except Exception as e:
            raise RuntimeError(
                "InsightFace not installed. Install optional deps: insightface, onnxruntime. "
                f"Original error: {e}"
            )

        self._app = FaceAnalysis(name="buffalo_l")
        # ctx_id: -1 CPU, 0 GPU
        self._app.prepare(ctx_id=-1, det_size=(640, 640))

    @property
    def model_key(self) -> str:
        return self._model_key

    @property
    def embedding_dim(self) -> int:
        return self._dim

    def extract_embedding(self, bgr_image: np.ndarray) -> tuple[np.ndarray, dict]:
        faces = self._app.get(bgr_image)
        if not faces:
            raise ValueError("No face detected")

        faces_sorted = sorted(
            faces,
            key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1]),
            reverse=True,
        )
        f = faces_sorted[0]

        emb = np.asarray(f.embedding, dtype=np.float32)
        meta = {
            "bbox": [float(x) for x in f.bbox],
            "det_score": float(getattr(f, "det_score", 0.0)),
            "face_count": int(len(faces)),
            "all_bboxes": [
                [float(x) for x in face.bbox]
                for face in faces_sorted
            ],
        }

        pose = getattr(f, "pose", None)
        if pose is not None:
            try:
                meta["pose"] = [float(p) for p in pose]
            except Exception:
                pass

        return emb, meta