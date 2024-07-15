import uuid
from typing import Any, Optional

from sqlalchemy.orm import selectinload

from src.models.user import User, Role
from src.ports.database_interface import DatabaseInterface
from sqlalchemy import select, update, asc, desc
from pydantic import BaseModel
from src.repositories.core import DBSessionMixin
from src.services.exceptions import UserNotFoundException


class UserRepository(DatabaseInterface, DBSessionMixin):
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
            .options(selectinload(User.role))
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

    async def create(self, user: BaseModel):
        values = user.model_dump()
        new_user = self.model(**values)
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user

    async def update(self, user_id: uuid.UUID, data: BaseModel):
        values = data.model_dump(exclude_unset=True)
        stmt = (
            update(self.model)
            .where(self.model.id == user_id)
            .values(values)
            .returning(self.model)
        )
        updated_user = await self.db.execute(stmt)
        result = updated_user.scalars().first()
        await self.db.commit()
        return result

    async def delete(self, user_id: uuid.UUID):
        user = await self.get_by_id(user_id)
        await self.db.delete(user)
        await self.db.commit()
        return True
