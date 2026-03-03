from __future__ import annotations

import logging
import numpy as np
from sqlalchemy.orm import Session

from app.config import settings
from app.face.registry import FaceEngineRegistry
from app.face.quality import b64_to_bgr, gate_quality
from app.repos.face_template_repo import FaceTemplateRepo
from app.repos.access_log_repo import AccessLogRepo
from app.repos.lock_repo import LockRepo
from app.repos.device_repo import DeviceRepo
from app.services.lock_service import LockService
from app.services.device_service import DeviceService
from app.models.access_log import AccessSource
from app.models.device_command import CommandType
from app.models.lock_member import LockRole
from app.exceptions import ForbiddenError, NotFoundError

logger = logging.getLogger("services.face")


# ==========================
# Utility
# ==========================

def l2_normalize(v: np.ndarray) -> np.ndarray:
    v = v.astype(np.float32)
    n = np.linalg.norm(v) + 1e-12
    return v / n


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(l2_normalize(a), l2_normalize(b)))


def pack_embedding(v: np.ndarray) -> bytes:
    return v.astype(np.float32).tobytes()


def unpack_embedding(blob: bytes, dim: int) -> np.ndarray:
    v = np.frombuffer(blob, dtype=np.float32)
    if v.size != dim:
        raise ValueError("Embedding dim mismatch")
    return v


# ==========================
# Service
# ==========================

class FaceService:
    def __init__(self, db: Session, registry: FaceEngineRegistry):
        self.db = db
        self.registry = registry
        self.templates = FaceTemplateRepo(db)
        self.logs = AccessLogRepo(db)
        self.locks_repo = LockRepo(db)
        self.lock_service = LockService(db)
        self.device_repo = DeviceRepo(db)
        self.device_service = DeviceService(db)

    # ======================================================
    # ENROLL
    # ======================================================

    def enroll(
        self,
        *,
        actor_account_id: int,
        lock_id: int,
        target_account_id: int,
        images_base64: list[str],
    ):
        """
        OWNER enroll face cho USER.
        """

        # 1️ Kiểm tra quyền (chỉ OWNER của lock)
        self.lock_service.require_member_role(
            lock_id,
            actor_account_id,
            LockRole.OWNER,
        )

        # 2️ Kiểm tra user được enroll có thuộc lock không
        try:
            self.lock_service.require_member_role(
                lock_id,
                target_account_id,
                LockRole.USER,
            )
        except Exception:
            raise ForbiddenError("Target account is not a member of this lock")

        # 3️ Validate số ảnh
        if len(images_base64) < settings.FACE_ENROLL_SHOTS_MIN:
            raise ValueError(
                f"Need at least {settings.FACE_ENROLL_SHOTS_MIN} shots"
            )

        engine = self.registry.get(settings.FACE_MODEL_KEY)

        embeddings: list[np.ndarray] = []
        quality_scores: list[float] = []

        for b64 in images_base64:
            bgr = b64_to_bgr(b64)
            emb, meta = engine.extract_embedding(bgr)

            q = gate_quality(bgr, meta)
            if not q.ok:
                raise ValueError(
                    f"Quality gate failed: {q.reasons} metrics={q.metrics}"
                )

            embeddings.append(l2_normalize(emb))
            quality_scores.append(q.score)

        # 4️ 5-shot mean embedding
        mean_emb = l2_normalize(
            np.mean(np.stack(embeddings, axis=0), axis=0)
        )

        quality_score = float(np.mean(np.array(quality_scores)))

        # 5️ Lưu template
        template = self.templates.create(
            lock_id=lock_id,
            account_id=target_account_id,
            model_key=engine.model_key,
            embedding_dim=engine.embedding_dim,
            embedding_blob=pack_embedding(mean_emb),
            shots_count=len(images_base64),
            quality_score=quality_score,
        )

        self.db.commit()
        return template

    # ======================================================
    # VERIFY
    # ======================================================

    def verify(
        self,
        lock_id: int,
        image_base64: str,
        source: str,
        device_uid: str | None,
    ):
        lock = self.locks_repo.get(lock_id)
        if not lock:
            raise NotFoundError("Lock not found")

        engine = self.registry.get(settings.FACE_MODEL_KEY)

        bgr = b64_to_bgr(image_base64)
        emb, meta = engine.extract_embedding(bgr)

        # 1️ Quality gate
        q = gate_quality(bgr, meta)

        threshold_used = float(
            lock.threshold_override or settings.FACE_DEFAULT_THRESHOLD
        )

        if not q.ok:
            row = self.logs.create(
                lock_id=lock_id,
                matched_account_id=None,
                score=0.0,
                threshold_used=threshold_used,
                success=False,
                source=AccessSource(source),
                device_id=None,
            )
            self.db.commit()

            return {
                "success": False,
                "matched_account_id": None,
                "score": 0.0,
                "threshold_used": threshold_used,
                "log_id": row.id,
                "quality": q.to_dict(),
                "topk": [],
            }

        # 2️ So sánh với templates
        probe = l2_normalize(emb)
        templates = self.templates.list_by_lock_and_model(
            lock_id, engine.model_key
        )

        if not templates:
            raise NotFoundError("No face templates enrolled for this lock")

        scored: list[tuple[float, int]] = []

        for t in templates:
            vec = unpack_embedding(t.embedding_blob, t.embedding_dim)
            s = cosine_similarity(probe, vec)
            scored.append((s, t.account_id))

        scored.sort(key=lambda x: x[0], reverse=True)

        topk = scored[: max(1, settings.FACE_TOP_K)]

        best_score = topk[0][0]
        best_account_id = topk[0][1]

        success = bool(best_score >= threshold_used)

        # 3️ Device mapping
        device_id = None
        if device_uid:
            d = self.device_repo.get_by_uid(lock_id, device_uid)
            if d:
                device_id = d.id

        # 4️⃣ Log access
        row = self.logs.create(
            lock_id=lock_id,
            matched_account_id=best_account_id if success else None,
            score=float(best_score),
            threshold_used=threshold_used,
            success=success,
            source=AccessSource(source),
            device_id=device_id,
        )
        self.db.commit()

        # 5️⃣ Create OPEN command nếu thành công
        cmd_id = None
        if success:
            cmd = self.device_service.create_command(
                lock_id,
                CommandType.OPEN,
                {
                    "reason": "face_verified",
                    "score": float(best_score),
                },
            )
            cmd_id = cmd.id

        return {
            "success": success,
            "matched_account_id": best_account_id if success else None,
            "score": float(best_score),
            "threshold_used": threshold_used,
            "log_id": row.id,
            "device_command_id": cmd_id,
            "quality": q.to_dict(),
            "topk": [
                {"score": float(s), "account_id": int(aid)}
                for s, aid in topk
            ],
        }