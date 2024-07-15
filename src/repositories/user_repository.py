import uuid

from sqlalchemy.orm import selectinload

from src.models.user import User, Role
from src.ports.database_interface import DatabaseInterface
from sqlalchemy import select, update
from pydantic import BaseModel
from src.repositories.core import DBSessionMixin


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
        result = result.first()
        return result

    async def get_by_id(self, user_id: uuid.UUID):
        stmt = (
            select(self.model)
            .where(self.model.id == user_id)
            .options(selectinload(User.role))
        )

        result = await self.db.execute(stmt)
        user = result.scalars().first()
        return user

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
