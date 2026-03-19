from __future__ import annotations

import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import db_dep, get_face_registry
from app.schemas.enroll import EnrollIn, EnrollOut, VerifyIn, VerifyOut
from app.security.deps import get_current_account
from app.services.face_service import FaceService
from app.exceptions import ForbiddenError, NotFoundError, http_403, http_404, http_422

router = APIRouter(tags=["face"])
logger = logging.getLogger("api.face")


@router.post("/api/enroll", response_model=EnrollOut)
def enroll(payload: EnrollIn, db: Session = Depends(db_dep), acct=Depends(get_current_account)):
    try:
        t = FaceService(db, get_face_registry()).enroll(
            actor_account_id=acct.id,
            lock_id=payload.lock_id,
            target_account_id=int(payload.target_account_id),
            images_base64=payload.images_base64,
        )

        return EnrollOut(
            template_id=t.id,
            model_key=t.model_key,
            shots_count=t.shots_count,
            quality_score=t.quality_score,
        )
    except ForbiddenError as e:
        logger.error("enroll_forbidden", exc_info=e)
        raise http_403(str(e))
    except NotFoundError as e:
        logger.error("enroll_notfound", exc_info=e)
        raise http_404(str(e))
    except Exception as e:
        logger.error("enroll_error", exc_info=e)
        raise http_422(str(e))


@router.post("/api/verify", response_model=VerifyOut)
def verify(payload: VerifyIn, db: Session = Depends(db_dep), acct=Depends(get_current_account)):
    try:
        res = FaceService(db, get_face_registry()).verify(
            lock_id=payload.lock_id,
            image_base64=payload.image_base64,
            source=payload.source,
            device_uid=payload.device_uid,
        )

        return VerifyOut(
            success=bool(res["success"]),
            matched_account_id=res["matched_account_id"],
            score=float(res["score"]),
            threshold_used=float(res["threshold_used"]),
            result=res.get("result"),
        )
    except NotFoundError as e:
        raise http_404(str(e))
    except Exception as e:
        logger.error("verify_error", exc_info=e)
        raise http_422(str(e))