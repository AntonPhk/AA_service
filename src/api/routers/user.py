from typing import Annotated, Optional, Any
from uuid import UUID

from fastapi import APIRouter, Depends

from src.schemas.user import (
    UserResponseSchema,
    UserUpdateSchema,
    UserResponseByAdminSchema,
    UserUpdateByAdminSchema,
    UserResponseUpdateByAdminSchema,
)
from src.services.user_service import UserService
from src.api.dependencies import get_user_service
from src.services.utils import oauth2_scheme

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/me", response_model=UserResponseSchema)
async def get_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.get_user(token=token)


@router.get("/all", response_model=list[UserResponseByAdminSchema])
async def get_all_users(
    token: Annotated[str, Depends(oauth2_scheme)],
    page: int = 1,
    limit: int = 10,
    order_by: str = "asc",
    filter_by_role: Optional[str] = None,
    sort_by: Any = None,
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.get_all_users(
        token=token,
        page=page,
        limit=limit,
        order_by=order_by,
        filter_by_role=filter_by_role,
        sort_by=sort_by,
    )


@router.patch("/me", response_model=UserUpdateSchema)
async def update_user(
    update_info: UserUpdateSchema,
    token: Annotated[str, Depends(oauth2_scheme)],
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.update_user(token=token, user=update_info)


@router.delete("/me")
async def delete_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.delete_user(token=token)


@router.get("/{user_id}", response_model=UserResponseByAdminSchema)
async def get_user_by_id(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_id: UUID,
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.get_user_by_id(token=token, user_id=user_id)


@router.patch("/{user_id}", response_model=UserResponseUpdateByAdminSchema)
async def update_user_by_id(
    update_info: UserUpdateByAdminSchema,
    user_id: UUID,
    token: Annotated[str, Depends(oauth2_scheme)],
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.update_user_by_id(
        token=token, user_id=user_id, user=update_info
    )


@router.delete("{user_id}")
async def delete_user_by_id(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_id: UUID,
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.delete_user_by_id(token=token, user_id=user_id)
