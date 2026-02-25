from sqlalchemy.orm import Session
from sqlalchemy import select, delete
from app.db.models import FaceTemplate


def upsert_template(
    db: Session,
    lock_id: int,
    account_id: int,
    model_key: str,
    dim: int,
    embedding: bytes,
    shots: int,
) -> FaceTemplate:
    # keep exactly 1 template per (lock, account, model_key) for simplicity (average of shots)
    existing = db.execute(
        select(FaceTemplate).where(
            FaceTemplate.lock_id == lock_id,
            FaceTemplate.account_id == account_id,
            FaceTemplate.model_key == model_key,
        )
    ).scalar_one_or_none()

    if existing:
        existing.dim = dim
        existing.embedding = embedding
        existing.shots = shots
        db.commit()
        db.refresh(existing)
        return existing

    tpl = FaceTemplate(
        lock_id=lock_id,
        account_id=account_id,
        model_key=model_key,
        dim=dim,
        embedding=embedding,
        shots=shots,
    )
    db.add(tpl)
    db.commit()
    db.refresh(tpl)
    return tpl


def list_templates_for_lock_model(db: Session, lock_id: int, model_key: str) -> list[FaceTemplate]:
    return list(
        db.execute(
            select(FaceTemplate).where(FaceTemplate.lock_id == lock_id, FaceTemplate.model_key == model_key)
        ).scalars().all()
    )


def delete_templates_for_account_lock(db: Session, lock_id: int, account_id: int) -> None:
    db.execute(delete(FaceTemplate).where(FaceTemplate.lock_id == lock_id, FaceTemplate.account_id == account_id))
    db.commit()