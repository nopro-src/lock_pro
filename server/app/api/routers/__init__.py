from fastapi import APIRouter
from .auth import router as auth_router
from .locks import router as locks_router
from .users import router as users_router
from .enroll import router as enroll_router
from .verify import router as verify_router
from .logs import router as logs_router
from .system import router as system_router
from .device import router as device_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(locks_router, prefix="/locks", tags=["locks"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(enroll_router, prefix="/enroll", tags=["enroll"])
api_router.include_router(verify_router, prefix="/verify", tags=["verify"])
api_router.include_router(logs_router, prefix="/logs", tags=["logs"])
api_router.include_router(system_router, prefix="/system", tags=["system"])
api_router.include_router(device_router, prefix="/device", tags=["device"])