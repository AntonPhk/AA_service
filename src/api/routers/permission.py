from typing import Annotated, Any

from fastapi import APIRouter, Depends

from src.services.utils import oauth2_scheme
from src.schemas.roles_and_permissions import (
    PermissionBaseSchema,
    PermissionResponseSchema,
)
from src.api.dependencies import get_permission_service
from src.services.permission_service import PermissionService

router = APIRouter(prefix="/permission", tags=["permission"])


@router.post("/create", response_model=PermissionResponseSchema)
async def create_permission(
    token: Annotated[str, Depends(oauth2_scheme)],
    permission: PermissionBaseSchema,
    permission_service: PermissionService = Depends(get_permission_service),
):
    return await permission_service.create_permission(
        token=token, permission=permission
    )


@router.get("/all", response_model=list[PermissionResponseSchema])
async def get_all_permissions(
    token: Annotated[str, Depends(oauth2_scheme)],
    page: int = 1,
    limit: int = 10,
    order_by: str = "asc",
    sort_by: Any = None,
    permission_service: PermissionService = Depends(get_permission_service),
):
    return await permission_service.get_all_permissions(
        token=token, page=page, limit=limit, order_by=order_by, sort_by=sort_by
    )


@router.get("", response_model=PermissionResponseSchema)
async def get_permission(
    token: Annotated[str, Depends(oauth2_scheme)],
    permission_name: str,
    permission_service: PermissionService = Depends(get_permission_service),
):
    return await permission_service.get_permission(
        token=token, permission=permission_name
    )


@router.get("/{permission_id}", response_model=PermissionResponseSchema)
async def get_permission_by_id(
    token: Annotated[str, Depends(oauth2_scheme)],
    permission_id: int,
    permission_service: PermissionService = Depends(get_permission_service),
):
    return await permission_service.get_permission_by_id(
        token=token, permission_id=permission_id
    )


@router.patch("/{permission_id}", response_model=PermissionResponseSchema)
async def update_permission(
    token: Annotated[str, Depends(oauth2_scheme)],
    permission_id: int,
    permission: PermissionBaseSchema,
    permission_service: PermissionService = Depends(get_permission_service),
):
    return await permission_service.update_permission_by_id(
        token=token, permission_id=permission_id, permission=permission
    )


@router.delete("/{permission_id}")
async def delete_permission(
    token: Annotated[str, Depends(oauth2_scheme)],
    permission_id: int,
    permission_service: PermissionService = Depends(get_permission_service),
):
    return await permission_service.delete_permission_by_id(
        token=token, permission_id=permission_id
    )
