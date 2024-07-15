from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from src.schemas.user import UserResponseSchema, UserUpdateSchema
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


@router.get("/me/{user_id}", response_model=UserResponseSchema)
async def get_user_by_id(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_id: UUID,
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.get_user_by_id(token=token, user_id=user_id)


@router.patch("/me", response_model=UserUpdateSchema)
async def update_user(
    update_info: UserUpdateSchema,
    token: Annotated[str, Depends(oauth2_scheme)],
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.update_user(token=token, user=update_info)


@router.patch("/me/{user_id}", response_model=UserUpdateSchema)
async def update_user_by_id(
    update_info: UserUpdateSchema,
    user_id: UUID,
    token: Annotated[str, Depends(oauth2_scheme)],
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.update_user_by_id(
        token=token, user_id=user_id, user=update_info
    )


@router.delete("/me")
async def delete_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.delete_user(token=token)


@router.delete("/me{user_id}")
async def delete_user_by_id(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_id: UUID,
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.delete_user_by_id(token=token, user_id=user_id)
