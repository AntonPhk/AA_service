import uuid
from typing import Any, Optional

from sqlalchemy.orm import selectinload

from src.models.user import User, Role
from sqlalchemy import select, asc, desc
from src.repositories.core import BaseRepository
from src.services.exceptions import UserNotFoundException


class UserRepository(BaseRepository):
    model = User
    roles = Role

    async def get(self, login: str):
        stmt = (
            select(self.model)
            .where((self.model.email == login) | (self.model.username == login))
            .options(selectinload(User.role))
        )

        result = await self.db.scalars(stmt)
        if not (user := result.first()):
            raise UserNotFoundException
        return user

    async def get_by_id(self, user_id: uuid.UUID):
        stmt = (
            select(self.model)
            .where(self.model.id == user_id)
            .options(selectinload(self.model.role).selectinload(self.roles.permissions))
        )

        result = await self.db.execute(stmt)
        if not (user := result.scalars().first()):
            raise UserNotFoundException
        return user

    async def get_all(
        self,
        page: int = 1,
        limit: int = 10,
        order_by: str = "asc",
        filter_by_role: Optional[str] = None,
        sort_by: Any = None,
    ):
        stmt = select(
            self.model,
        ).options(selectinload(User.role).selectinload(Role.permissions))

        if filter_by_role:
            stmt = stmt.where(User.role.has(name=filter_by_role))

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
        users = result.scalars().all()
        return users
