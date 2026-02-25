from __future__ import annotations

import base64
import numpy as np
import cv2

from app.config import settings


class QualityResult:
    def __init__(self, ok: bool, score: float, reasons: list[str], metrics: dict):
        self.ok = ok
        self.score = score
        self.reasons = reasons
        self.metrics = metrics

    def to_dict(self) -> dict:
        return {"ok": self.ok, "score": self.score, "reasons": self.reasons, "metrics": self.metrics}


def b64_to_bgr(image_base64: str) -> np.ndarray:
    raw = base64.b64decode(image_base64.split(",")[-1])
    arr = np.frombuffer(raw, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Invalid image")
    return img


def compute_brightness(bgr: np.ndarray) -> float:
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    return float(np.mean(gray))


def compute_blur_laplacian_var(bgr: np.ndarray) -> float:
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())


def face_area_ratio_from_bbox(bgr: np.ndarray, bbox: list[float]) -> float:
    h, w = bgr.shape[:2]
    x1, y1, x2, y2 = bbox
    face_area = max(0.0, (x2 - x1)) * max(0.0, (y2 - y1))
    img_area = float(h * w)
    if img_area <= 0:
        return 0.0
    return float(face_area / img_area)


def gate_quality(bgr: np.ndarray, meta: dict) -> QualityResult:
    reasons: list[str] = []
    metrics: dict = {}

    brightness = compute_brightness(bgr)
    blur_var = compute_blur_laplacian_var(bgr)
    metrics["brightness"] = brightness
    metrics["blur_laplacian_var"] = blur_var

    ok = True

    if brightness < settings.QUALITY_MIN_BRIGHTNESS:
        ok = False
        reasons.append("Too dark")
    if brightness > settings.QUALITY_MAX_BRIGHTNESS:
        ok = False
        reasons.append("Too bright")

    # blur: Laplacian variance smaller => more blur
    if blur_var < settings.QUALITY_MAX_BLUR_LAPLACIAN_VAR:
        ok = False
        reasons.append("Too blurry")

    bbox = meta.get("bbox")
    if bbox:
        ratio = face_area_ratio_from_bbox(bgr, bbox)
        metrics["face_area_ratio"] = ratio
        if ratio < settings.QUALITY_MIN_FACE_AREA_RATIO:
            ok = False
            reasons.append("Face too small")
    else:
        # if no bbox, still allow (engine may not provide), but penalize score
        metrics["face_area_ratio"] = None
        reasons.append("No bbox meta (cannot validate face size)")

    # pose check if available: assume [yaw, pitch, roll] or similar; keep defensive
    pose = meta.get("pose")
    if isinstance(pose, list) and len(pose) >= 2:
        yaw = float(pose[0])
        pitch = float(pose[1])
        metrics["yaw"] = yaw
        metrics["pitch"] = pitch
        if abs(yaw) > settings.QUALITY_MAX_POSE_YAW_DEG:
            ok = False
            reasons.append("Yaw too large")
        if abs(pitch) > settings.QUALITY_MAX_POSE_PITCH_DEG:
            ok = False
            reasons.append("Pitch too large")

    # score: simple heuristic (0..1)
    # higher blur_var, brightness within range, bigger face => better score
    score = 1.0
    if not ok:
        score = 0.3
    else:
        score = min(1.0, max(0.0, (blur_var / 300.0))) * 0.5 + 0.5

    return QualityResult(ok=ok, score=float(score), reasons=reasons, metrics=metrics)