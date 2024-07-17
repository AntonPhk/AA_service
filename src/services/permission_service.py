from typing import Annotated, Optional
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from models import Permission
from src.repositories.permission_repository import PermissionRepository
from src.schemas.roles_and_permissions import PermissionBaseSchema
from src.repositories.core import get_async_session
from fastapi import Depends
from src.services.token_service import TokenService
from src.services.exceptions import (
    DuplicatePermissionException,
    PermissionNotFoundException,
)


class PermissionService:
    def __init__(
        self,
        token_service: TokenService,
        session: Annotated[AsyncSession, Depends(get_async_session)],
    ) -> None:
        self.session = session
        self.token_service = token_service
        self.repo = PermissionRepository(self.session)

    async def create_permission(
        self,
        token: str,
        permission: PermissionBaseSchema,
    ) -> Permission:
        self.token_service.validate_role(token, "admin")
        try:
            permission = await self.repo.create(data=permission)
        except IntegrityError:
            raise DuplicatePermissionException
        return permission

    async def get_permission(self, token: str, permission: str) -> Permission:
        self.token_service.validate_role(token, "admin")
        permission = await self.repo.get_by_name(name=permission)
        if not permission:
            raise PermissionNotFoundException
        return permission

    async def get_permission_by_id(self, token: str, permission_id: int) -> Permission:
        self.token_service.validate_role(token, "admin")
        permission = await self.repo.get_by_id(entity_id=permission_id)
        if not permission:
            raise PermissionNotFoundException
        return permission

    async def get_all_permissions(
        self,
        token: str,
        page: int = 1,
        limit: int = 10,
        order_by: str = "asc",
        sort_by: Optional[str] = None,
    ) -> list[Permission]:
        self.token_service.validate_role(token, "admin")
        permissions = await self.repo.get_all(
            page=page,
            limit=limit,
            order_by=order_by,
            sort_by=sort_by,
        )
        return permissions

    async def update_permission_by_id(
        self, token: str, permission_id: int, permission: PermissionBaseSchema
    ) -> Permission:
        self.token_service.validate_role(token, "admin")
        try:
            permission = await self.repo.update(
                entity_id=permission_id,
                data=permission,
            )
        except IntegrityError:
            raise DuplicatePermissionException
        if not permission:
            raise PermissionNotFoundException
        return permission

    async def delete_permission_by_id(self, token: str, permission_id: int) -> dict:
        self.token_service.validate_role(token, "admin")
        if not await self.repo.delete(entity_id=permission_id):
            raise PermissionNotFoundException

        return {"message": "Permission deleted successfully."}
