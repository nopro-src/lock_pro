from __future__ import annotations

from fastapi import APIRouter

from app.schemas.system import SystemInfoOut
from app.services.system_service import SystemService

router = APIRouter(prefix="/api/system", tags=["system"])


@router.get("/info", response_model=SystemInfoOut)
def info():
    return SystemInfoOut(**SystemService().info())
# def get_system_info():
#     return system_service.get_info()