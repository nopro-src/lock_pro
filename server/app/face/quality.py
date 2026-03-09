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
        return {
            "ok": self.ok,
            "score": self.score,
            "reasons": self.reasons,
            "metrics": self.metrics,
        }


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


def clamp_bbox_to_image(
    bbox: list[float] | tuple[float, float, float, float] | None,
    image_shape: tuple[int, int, int] | tuple[int, int],
) -> tuple[int, int, int, int] | None:
    if not bbox or len(bbox) < 4:
        return None

    h, w = image_shape[:2]
    x1, y1, x2, y2 = bbox[:4]

    x1 = int(max(0, min(round(x1), w - 1)))
    y1 = int(max(0, min(round(y1), h - 1)))
    x2 = int(max(0, min(round(x2), w)))
    y2 = int(max(0, min(round(y2), h)))

    if x2 <= x1 or y2 <= y1:
        return None

    return x1, y1, x2, y2


def crop_face_with_margin(
    bgr: np.ndarray,
    bbox: list[float] | tuple[float, float, float, float] | None,
    margin_ratio: float = 0.10,
) -> np.ndarray:
    """
    Crop face region using bbox, with a small margin around the face.
    Falls back to the full image if bbox is missing/invalid.
    """
    clamped = clamp_bbox_to_image(bbox, bgr.shape)
    if clamped is None:
        return bgr

    h, w = bgr.shape[:2]
    x1, y1, x2, y2 = clamped

    bw = x2 - x1
    bh = y2 - y1

    mx = int(round(bw * margin_ratio))
    my = int(round(bh * margin_ratio))

    x1m = max(0, x1 - mx)
    y1m = max(0, y1 - my)
    x2m = min(w, x2 + mx)
    y2m = min(h, y2 + my)

    if x2m <= x1m or y2m <= y1m:
        return bgr

    return bgr[y1m:y2m, x1m:x2m]


def preprocess_face_for_quality(face_bgr: np.ndarray, target_size: int = 224) -> np.ndarray:
    """
    Normalize the face crop before blur measurement so the metric is more stable
    across devices / resolutions / lighting conditions.
    """
    gray = cv2.cvtColor(face_bgr, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, (target_size, target_size), interpolation=cv2.INTER_LINEAR)

    # Mild local contrast enhancement
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)

    return gray


def compute_blur_laplacian_var(
    bgr: np.ndarray,
    bbox: list[float] | tuple[float, float, float, float] | None = None,
) -> float:
    """
    Measure sharpness on the face crop instead of the whole image.
    Lower variance => blurrier image.
    """
    face = crop_face_with_margin(bgr, bbox=bbox, margin_ratio=0.10)
    gray = preprocess_face_for_quality(face, target_size=224)
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())


def face_area_ratio_from_bbox(bgr: np.ndarray, bbox: list[float]) -> float:
    h, w = bgr.shape[:2]
    clamped = clamp_bbox_to_image(bbox, bgr.shape)
    if clamped is None:
        return 0.0

    x1, y1, x2, y2 = clamped
    face_area = float((x2 - x1) * (y2 - y1))
    img_area = float(h * w)

    if img_area <= 0:
        return 0.0

    return float(face_area / img_area)


def _compute_score(
    brightness: float,
    blur_var: float,
    face_ratio: float | None,
    yaw: float | None,
    pitch: float | None,
) -> float:
    """
    Simple heuristic score in range [0, 1].
    This score is informational; pass/fail is decided by explicit gates.
    """

    # Brightness score
    if settings.QUALITY_MIN_BRIGHTNESS <= brightness <= settings.QUALITY_MAX_BRIGHTNESS:
        brightness_score = 1.0
    else:
        # Penalize gradually when outside allowed range
        if brightness < settings.QUALITY_MIN_BRIGHTNESS:
            diff = settings.QUALITY_MIN_BRIGHTNESS - brightness
        else:
            diff = brightness - settings.QUALITY_MAX_BRIGHTNESS
        brightness_score = max(0.0, 1.0 - (diff / 80.0))

    # Blur score
    blur_score = min(1.0, max(0.0, blur_var / max(settings.QUALITY_MIN_LAPLACIAN_VAR * 2.0, 1.0)))

    # Face size score
    if face_ratio is None:
        face_score = 0.6
    elif face_ratio >= settings.QUALITY_MIN_FACE_AREA_RATIO:
        face_score = min(1.0, face_ratio / max(settings.QUALITY_MIN_FACE_AREA_RATIO * 2.0, 1e-6))
    else:
        face_score = max(0.0, face_ratio / max(settings.QUALITY_MIN_FACE_AREA_RATIO, 1e-6))

    # Pose score
    pose_score = 1.0
    if yaw is not None:
        pose_score *= max(0.0, 1.0 - (abs(yaw) / max(settings.QUALITY_MAX_POSE_YAW_DEG * 2.0, 1.0)))
    if pitch is not None:
        pose_score *= max(0.0, 1.0 - (abs(pitch) / max(settings.QUALITY_MAX_POSE_PITCH_DEG * 2.0, 1.0)))

    score = (
        0.25 * brightness_score
        + 0.40 * blur_score
        + 0.20 * face_score
        + 0.15 * pose_score
    )
    return float(max(0.0, min(1.0, score)))


def gate_quality(bgr: np.ndarray, meta: dict) -> QualityResult:
    reasons: list[str] = []
    metrics: dict = {}

    h, w = bgr.shape[:2]
    metrics["image_width"] = int(w)
    metrics["image_height"] = int(h)

    bbox = meta.get("bbox")
    clamped_bbox = clamp_bbox_to_image(bbox, bgr.shape) if bbox else None

    brightness = compute_brightness(bgr)
    blur_var = compute_blur_laplacian_var(bgr, clamped_bbox)

    metrics["brightness"] = brightness
    metrics["blur_laplacian_var"] = blur_var
    metrics["bbox"] = list(clamped_bbox) if clamped_bbox else None

    ok = True

    # Brightness gates
    if brightness < settings.QUALITY_MIN_BRIGHTNESS:
        ok = False
        reasons.append("Too dark")
    if brightness > settings.QUALITY_MAX_BRIGHTNESS:
        ok = False
        reasons.append("Too bright")

    # Sharpness gate: lower variance => blurrier
    if blur_var < settings.QUALITY_MIN_LAPLACIAN_VAR:
        ok = False
        reasons.append("Too blurry")

    # Face size gate
    face_ratio: float | None
    if clamped_bbox is not None:
        ratio = face_area_ratio_from_bbox(bgr, list(clamped_bbox))
        face_ratio = ratio
        metrics["face_area_ratio"] = ratio
        if ratio < settings.QUALITY_MIN_FACE_AREA_RATIO:
            ok = False
            reasons.append("Face too small")

        x1, y1, x2, y2 = clamped_bbox
        metrics["face_crop_width"] = int(x2 - x1)
        metrics["face_crop_height"] = int(y2 - y1)
    else:
        face_ratio = None
        metrics["face_area_ratio"] = None
        reasons.append("No bbox meta (cannot validate face size)")

    # Pose gate if available
    yaw: float | None = None
    pitch: float | None = None

    pose = meta.get("pose")
    if isinstance(pose, (list, tuple)) and len(pose) >= 2:
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

    score = _compute_score(
        brightness=brightness,
        blur_var=blur_var,
        face_ratio=face_ratio,
        yaw=yaw,
        pitch=pitch,
    )

    return QualityResult(ok=ok, score=score, reasons=reasons, metrics=metrics)