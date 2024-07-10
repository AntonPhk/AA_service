import asyncio
from typing import List

from sqlalchemy.orm import selectinload
from sqlalchemy import select

from src.repositories.core import async_session_builder
from src.core.config import settings
from src.models.user import Roles, Permissions


async def get_existing_roles_permissions(session) -> (List[str], List[str]):
    default_roles = settings.ROLES.split()
    default_permissions = settings.PERMISSIONS.split()

    existing_roles_result = await session.execute(
        select(Roles).where(Roles.name.in_(default_roles))
    )
    existing_permissions_result = await session.execute(
        select(Permissions).where(Permissions.name.in_(default_permissions))
    )

    existing_roles = [role.name for role in existing_roles_result.scalars().all()]
    existing_permissions = [
        permission.name for permission in existing_permissions_result.scalars().all()
    ]

    return existing_roles, existing_permissions


async def add_missing_roles_permissions(
    session, existing_roles: List[str], existing_permissions: List[str]
) -> None:
    default_roles = settings.ROLES.split()
    default_permissions = settings.PERMISSIONS.split()

    for role in default_roles:
        if role not in existing_roles:
            if role == "user":
                session.add(Roles(name=role, id=1))
            if role == "admin":
                session.add(Roles(name=role, id=2))

    for permission in default_permissions:
        if permission not in existing_permissions:
            session.add(Permissions(name=permission))

    await session.commit()


async def link_role_permission(
    session, role_name: str, permission_names: List[str]
) -> None:
    role_stmt = (
        select(Roles)
        .where(Roles.name == role_name)
        .options(selectinload(Roles.permissions))
    )
    role_result = await session.execute(role_stmt)
    role = role_result.scalars().first()

    if role:
        role_permission_names = {perm.name for perm in role.permissions}
        for perm_name in permission_names:
            if perm_name not in role_permission_names:
                permission_stmt = select(Permissions).where(
                    Permissions.name == perm_name
                )
                permission_result = await session.execute(permission_stmt)
                permission = permission_result.scalars().first()
                if permission:
                    role.permissions.append(permission)

        await session.commit()


async def init_default_table_values() -> None:
    async with async_session_builder() as session:
        async with session.begin():
            existing_roles, existing_permissions = await get_existing_roles_permissions(
                session
            )
            await add_missing_roles_permissions(
                session, existing_roles, existing_permissions
            )

    async with async_session_builder() as session:
        async with session.begin():
            await link_role_permission(session, "admin", ["all"])

    async with async_session_builder() as session:
        async with session.begin():
            await link_role_permission(session, "user", ["owner", "read_only"])


def main():
    asyncio.run(init_default_table_values())


if __name__ == "__main__":
    main()
