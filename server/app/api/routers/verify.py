from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.deps import get_db, get_current_account, get_face_engine, get_ws_manager
from app.api.schemas.verify import VerifyIn, VerifyOut
from app.services.verify_service import verify_1n
from app.core.events import EventType
from app.services.device_service import build_lock_command

router = APIRouter()


@router.post("", response_model=VerifyOut)
async def verify(payload: VerifyIn, db: Session = Depends(get_db), acc=Depends(get_current_account),
                 engine=Depends(get_face_engine), ws=Depends(get_ws_manager)):
    result = verify_1n(
        db=db,
        engine=engine,
        lock_id=payload.lock_id,
        actor_account_id=acc.id,
        image_base64=payload.image,
        source=payload.source,
    )

    await ws.broadcast({
        "type": EventType.VERIFY,
        "lock_id": payload.lock_id,
        "success": result["success"],
        "best_account_id": result["best_account_id"],
        "score": result["score"],
        "threshold": result["threshold"],
        "model_key": result["model_key"],
    })

    # Prepare future ESP32 command broadcast (web can see it now)
    cmd = build_lock_command(
        lock_id=payload.lock_id,
        action=("OPEN" if result["success"] else "DENY"),
        ok=result["success"],
        reason=("FACE_MATCH" if result["success"] else "FACE_FAIL"),
    )
    await ws.broadcast(cmd)

    return VerifyOut(**result)