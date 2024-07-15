from fastapi import APIRouter
from src.api.routers.auth import router as auth_router
from src.api.routers.user import router as user_router
from src.api.routers.core import router as core_router

router = APIRouter(prefix="/api")
router.include_router(auth_router)
router.include_router(user_router)
router.include_router(core_router)
