import numpy as np
from sqlalchemy.orm import Session
from app.face.base import FaceEngineBase
from app.utils.image_io import dataurl_to_bgr
from app.utils.numpy_io import bytes_to_emb
from app.db.repositories import templates_repo, logs_repo, locks_repo
from app.core.exceptions import forbidden, bad_request
from app.config import settings


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    # embeddings already normalized
    return float(np.dot(a, b))


def verify_1n(
    db: Session,
    engine: FaceEngineBase,
    lock_id: int,
    actor_account_id: int | None,
    image_base64: str,
    source: str = "web",
):
    # actor can be None (esp32 future)
    if actor_account_id is not None:
        mem = locks_repo.get_membership(db, lock_id, actor_account_id)
        if not mem:
            raise forbidden("Not a member of this lock")

    bgr = dataurl_to_bgr(image_base64)
    q = engine.embed(bgr)

    templates = templates_repo.list_templates_for_lock_model(db, lock_id=lock_id, model_key=engine.model_key)
    if not templates:
        raise bad_request("No enrolled templates yet")

    best_score = -1.0
    best_acc_id: int | None = None

    for tpl in templates:
        emb = bytes_to_emb(tpl.embedding, tpl.dim)
        s = cosine(q, emb)
        if s > best_score:
            best_score = s
            best_acc_id = tpl.account_id

    ok = best_score >= settings.THRESH
    logs_repo.create_log(db, lock_id=lock_id, matched_account_id=(best_acc_id if ok else None), score=best_score, success=ok, source=source)

    return {
        "success": ok,
        "best_account_id": best_acc_id if ok else None,
        "score": best_score,
        "threshold": settings.THRESH,
        "model_key": engine.model_key,
    }