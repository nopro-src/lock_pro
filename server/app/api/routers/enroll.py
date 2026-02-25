from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.deps import get_db, get_current_account, get_face_engine, get_ws_manager
from app.api.schemas.enroll import EnrollIn, EnrollOut
from app.services.enroll_service import enroll_5shots
from app.core.events import EventType

router = APIRouter()


@router.post("", response_model=EnrollOut)
async def enroll(payload: EnrollIn, db: Session = Depends(get_db), acc=Depends(get_current_account),
                 engine=Depends(get_face_engine), ws=Depends(get_ws_manager)):
    tpl = enroll_5shots(
        db=db,
        engine=engine,
        lock_id=payload.lock_id,
        actor_account_id=acc.id,
        target_account_id=payload.target_account_id,
        images_base64=payload.images,
    )

    await ws.broadcast({
        "type": EventType.ENROLL,
        "lock_id": payload.lock_id,
        "account_id": payload.target_account_id,
        "model_key": engine.model_key,
        "shots": tpl.shots,
    })

    return EnrollOut(
        template_id=tpl.id,
        lock_id=tpl.lock_id,
        account_id=tpl.account_id,
        model_key=tpl.model_key,
        dim=tpl.dim,
        shots=tpl.shots,
    )