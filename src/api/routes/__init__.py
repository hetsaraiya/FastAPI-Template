"""
API route modules.
"""

from fastapi import APIRouter

from src.api.routes.auth import router as auth_router
from src.api.routes.user import router as user_router
from src.api.routes.device import router as device_router
from src.api.routes.mandi import router as mandi_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(user_router)
api_router.include_router(device_router)
api_router.include_router(mandi_router)

__all__ = ["api_router"]