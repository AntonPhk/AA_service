from typing import Annotated, Any

from fastapi import APIRouter, Depends

from src.services.utils import oauth2_scheme
from src.schemas.roles_and_permissions import (
    RoleBaseSchema,
    RoleWithPermissionsSchema,
    RoleResponseSchema,
)
from src.api.dependencies import get_role_service
from src.services.role_service import RoleService


router = APIRouter(prefix="/role", tags=["role"])


@router.post("/create", response_model=RoleResponseSchema)
async def create_role(
    token: Annotated[str, Depends(oauth2_scheme)],
    role: RoleBaseSchema,
    role_service: RoleService = Depends(get_role_service),
):
    return await role_service.create_role(token=token, role=role)


@router.get("/all", response_model=list[RoleWithPermissionsSchema])
async def get_all_roles(
    token: Annotated[str, Depends(oauth2_scheme)],
    page: int = 1,
    limit: int = 10,
    order_by: str = "asc",
    sort_by: Any = None,
    role_service: RoleService = Depends(get_role_service),
):
    heh = await role_service.get_all_roles(
        token=token, page=page, limit=limit, order_by=order_by, sort_by=sort_by
    )
    return heh


@router.patch("/add_permission", response_model=RoleWithPermissionsSchema)
async def update_role_permission(
    token: Annotated[str, Depends(oauth2_scheme)],
    role_name: str,
    permission_name: str,
    role_service: RoleService = Depends(get_role_service),
):
    return await role_service.add_permission_to_role(
        token=token, role_name=role_name, permission_name=permission_name
    )


@router.patch("/remove_permission", response_model=RoleWithPermissionsSchema)
async def remove_role_permission(
    token: Annotated[str, Depends(oauth2_scheme)],
    role_name: str,
    permission_name: str,
    role_service: RoleService = Depends(get_role_service),
):
    return await role_service.remove_permission_from_role(
        token=token, role_name=role_name, permission_name=permission_name
    )


@router.get("", response_model=RoleWithPermissionsSchema)
async def get_role(
    token: Annotated[str, Depends(oauth2_scheme)],
    role_name: str,
    role_service: RoleService = Depends(get_role_service),
):
    return await role_service.get_role(token=token, role_name=role_name)


@router.get("/{role_id}", response_model=RoleResponseSchema)
async def get_role_by_id(
    token: Annotated[str, Depends(oauth2_scheme)],
    role_id: int,
    role_service: RoleService = Depends(get_role_service),
):
    return await role_service.get_role_by_id(token=token, role_id=role_id)


@router.patch("/{role_id}", response_model=RoleResponseSchema)
async def update_role(
    token: Annotated[str, Depends(oauth2_scheme)],
    role_id: int,
    role: RoleBaseSchema,
    role_service: RoleService = Depends(get_role_service),
):
    return await role_service.update_role_by_id(token=token, role_id=role_id, role=role)


@router.delete("/{role_id}")
async def delete_role(
    token: Annotated[str, Depends(oauth2_scheme)],
    role_id: int,
    role_service: RoleService = Depends(get_role_service),
):
    return await role_service.delete_role_by_id(token=token, role_id=role_id)
