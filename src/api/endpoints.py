from fastapi import APIRouter

from src.api.routes.user import router as user_router
from src.api.routes.authentication import router as auth_router

router = APIRouter()

router.include_router(router=user_router)
router.include_router(router=auth_router)
