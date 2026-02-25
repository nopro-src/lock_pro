import numpy as np
from sqlalchemy.orm import Session
from app.face.base import FaceEngineBase
from app.utils.image_io import dataurl_to_bgr
from app.utils.numpy_io import emb_to_bytes
from app.db.repositories import templates_repo, locks_repo
from app.core.exceptions import forbidden, bad_request
from app.config import settings


def _mean_embeddings(embs: list[np.ndarray]) -> np.ndarray:
    m = np.mean(np.stack(embs, axis=0), axis=0).astype(np.float32)
    m = m / (np.linalg.norm(m) + 1e-12)
    return m


def enroll_5shots(
    db: Session,
    engine: FaceEngineBase,
    lock_id: int,
    actor_account_id: int,
    target_account_id: int,
    images_base64: list[str],
):
    mem = locks_repo.get_membership(db, lock_id, actor_account_id)
    if not mem:
        raise forbidden("Not a member of this lock")

    if len(images_base64) != settings.ENROLL_SHOTS:
        raise bad_request(f"Require exactly {settings.ENROLL_SHOTS} images")

    embs: list[np.ndarray] = []
    for b64 in images_base64:
        bgr = dataurl_to_bgr(b64)
        emb = engine.embed(bgr)
        embs.append(emb)

    mean_emb = _mean_embeddings(embs)
    tpl = templates_repo.upsert_template(
        db=db,
        lock_id=lock_id,
        account_id=target_account_id,
        model_key=engine.model_key,
        dim=engine.dim,
        embedding=emb_to_bytes(mean_emb),
        shots=len(images_base64),
    )
    return tpl