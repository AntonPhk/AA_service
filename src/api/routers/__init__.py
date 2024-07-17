from fastapi import APIRouter
from src.api.routers.auth import router as auth_router
from src.api.routers.user import router as user_router
from src.api.routers.core import router as core_router
from src.api.routers.role import router as role_router
from src.api.routers.permission import router as permission_router

router = APIRouter(prefix="/api")
router.include_router(core_router)
router.include_router(auth_router)
router.include_router(user_router)
router.include_router(role_router)
router.include_router(permission_router)
