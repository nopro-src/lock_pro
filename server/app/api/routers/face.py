from __future__ import annotations

import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import db_dep, get_face_registry
from app.schemas.enroll import EnrollIn, EnrollOut, VerifyIn, VerifyOut
from app.security.deps import get_current_account
from app.services.face_service import FaceService
from app.exceptions import ForbiddenError, NotFoundError, http_403, http_404, http_422
from app.ws.manager import WsManager
from app.schemas.ws import WsEvent

router = APIRouter(tags=["face"])
logger = logging.getLogger("api.face")

_ws_manager: WsManager | None = None


def get_ws_manager() -> WsManager:
    global _ws_manager
    if _ws_manager is None:
        _ws_manager = WsManager()
    return _ws_manager


@router.post("/api/enroll", response_model=EnrollOut)
async def enroll(payload: EnrollIn, db: Session = Depends(db_dep), acct=Depends(get_current_account)):
    try:
        t = FaceService(db, get_face_registry()).enroll(acct.id, payload.lock_id, payload.account_id, payload.images_base64)
        # ws event
        await get_ws_manager().broadcast(
            WsEvent(type="ENROLL", lock_id=payload.lock_id, payload={"account_id": payload.account_id, "template_id": t.id})
        )
        return EnrollOut(template_id=t.id, model_key=t.model_key, shots_count=t.shots_count, quality_score=t.quality_score)
    except ForbiddenError as e:
        raise http_403(str(e))
    except NotFoundError as e:
        raise http_404(str(e))
    except Exception as e:
        raise http_422(str(e))


@router.post("/api/verify", response_model=VerifyOut)
async def verify(payload: VerifyIn, db: Session = Depends(db_dep), acct=Depends(get_current_account)):
    # USER allowed if is member; we validate by requiring role USER (or higher)
    # We'll reuse lock_service inside face_service verify flow, but verify itself doesn't check membership.
    # For security: require at least USER membership.
    from app.services.lock_service import LockService
    from app.models.lock_member import LockRole

    try:
        LockService(db).require_member_role(payload.lock_id, acct.id, LockRole.USER)
    except Exception as e:
        raise http_403(str(e))

    try:
        res = FaceService(db, get_face_registry()).verify(payload.lock_id, payload.image_base64, payload.source, payload.device_uid)
        await get_ws_manager().broadcast(
            WsEvent(
                type="VERIFY",
                lock_id=payload.lock_id,
                payload={
                    "success": res["success"],
                    "matched_account_id": res["matched_account_id"],
                    "score": res["score"],
                    "threshold_used": res["threshold_used"],
                },
            )
        )
        if res.get("device_command_id"):
            await get_ws_manager().broadcast(
                WsEvent(type="LOCK_CMD", lock_id=payload.lock_id, payload={"command_id": res["device_command_id"], "type": "OPEN"})
            )
        return VerifyOut(
            success=bool(res["success"]),
            matched_account_id=res["matched_account_id"],
            score=float(res["score"]),
            threshold_used=float(res["threshold_used"]),
        )
    except NotFoundError as e:
        raise http_404(str(e))
    except Exception as e:
        raise http_422(str(e))