from fastapi import APIRouter
from app.api.schemas.system import SystemInfoOut
from app.config import settings

router = APIRouter()


@router.get("/info", response_model=SystemInfoOut)
def info():
    return SystemInfoOut(model_key=settings.MODEL_KEY, threshold=settings.THRESH, enroll_shots=settings.ENROLL_SHOTS)