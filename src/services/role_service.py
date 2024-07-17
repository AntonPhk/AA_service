from typing import Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from models import Role
from src.repositories.permission_repository import PermissionRepository
from src.services.token_service import TokenService
from src.schemas.roles_and_permissions import RoleBaseSchema
from src.repositories.roles_repository import RoleRepository
from src.repositories.core import get_async_session
from fastapi import Depends
from src.services.exceptions import (
    RoleNotFoundException,
    DuplicatePermissionException,
    DuplicateRoleException,
    PermissionNotFoundException,
)


class RoleService:
    def __init__(
        self,
        token_service: TokenService,
        session: AsyncSession = Depends(get_async_session),
    ) -> None:
        self.session = session
        self.token_service = token_service
        self.role_repo = RoleRepository(self.session)
        self.permission_repo = PermissionRepository(self.session)

    async def create_role(self, token: str, role: RoleBaseSchema) -> Role:
        self.token_service.validate_role(token, "admin")
        try:
            role = await self.role_repo.create(data=role)
            return role
        except IntegrityError:
            raise DuplicateRoleException

    async def get_role(self, token: str, role_name: str) -> Role:
        self.token_service.validate_role(token, "admin")
        role = await self.role_repo.get_by_name(name=role_name)
        if not role:
            raise RoleNotFoundException
        return role

    async def get_role_by_id(self, token: str, role_id: int) -> Role:
        self.token_service.validate_role(token, "admin")
        role = await self.role_repo.get_by_id(entity_id=role_id)
        if not role:
            raise RoleNotFoundException
        return role

    async def get_all_roles(
        self,
        token: str,
        page: int = 1,
        limit: int = 10,
        order_by: str = "asc",
        sort_by: Optional[str] = None,
    ) -> list[Role]:
        self.token_service.validate_role(token, "admin")
        roles = await self.role_repo.get_all(page=page, limit=limit, order_by=order_by)
        return roles

    async def add_permission_to_role(
        self, token: str, role_name: str, permission_name: str
    ) -> Role:
        self.token_service.validate_role(token, "admin")
        role = await self.role_repo.get_by_name(role_name)
        permission = await self.permission_repo.get_by_name(permission_name)

        if permission in role.permissions:
            raise DuplicatePermissionException

        role.permissions.append(permission)

        await self.session.commit()
        await self.session.refresh(role)
        return role

    async def remove_permission_from_role(
        self, token: str, role_name: str, permission_name: str
    ) -> Role:
        self.token_service.validate_role(token, "admin")
        role = await self.role_repo.get_by_name(role_name)
        permission = await self.permission_repo.get_by_name(permission_name)

        if permission not in role.permissions:
            raise PermissionNotFoundException

        role.permissions.remove(permission)
        await self.session.commit()
        await self.session.refresh(role)
        return role

    async def update_role_by_id(
        self, token: str, role_id: int, role: RoleBaseSchema
    ) -> Role:
        self.token_service.validate_role(token, "admin")
        try:
            role = await self.role_repo.update(entity_id=role_id, data=role)
        except IntegrityError:
            raise DuplicateRoleException
        if not role:
            raise RoleNotFoundException
        return role

    async def delete_role_by_id(self, token: str, role_id: int) -> dict:
        self.token_service.validate_role(token, "admin")
        if not await self.role_repo.delete(entity_id=role_id):
            raise RoleNotFoundException

        return {"message": "Role deleted successfully."}
