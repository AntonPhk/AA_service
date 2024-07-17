from typing import Optional

from sqlalchemy.orm import selectinload

from src.models.user import Role, Permission
from sqlalchemy import select, asc, desc
from src.repositories.core import BaseRepository
from src.services.exceptions import (
    RoleNotFoundException,
)


class RoleRepository(BaseRepository):
    model = Role
    permissions = Permission

    async def get_by_name(self, name: str):
        stmt = (
            select(self.model)
            .where(self.model.name == name)
            .options(selectinload(self.model.permissions))
        )

        result = await self.db.execute(stmt)
        if not (role := result.scalars().first()):
            raise RoleNotFoundException
        return role

    async def get_all(
        self,
        page: int = 1,
        limit: int = 10,
        order_by: str = "asc",
        sort_by: Optional[str] = None,
    ):
        stmt = select(self.model).options(selectinload(self.model.permissions))

        if sort_by:
            sort_column = getattr(self.model, sort_by, None)
            if sort_column:
                if order_by == "asc":
                    stmt = stmt.order_by(asc(sort_column))
                elif order_by == "desc":
                    stmt = stmt.order_by(desc(sort_column))

        offset_value = (page - 1) * limit
        stmt = stmt.offset(offset_value).limit(limit)

        result = await self.db.execute(stmt)
        instances = result.scalars().all()
        return instances
