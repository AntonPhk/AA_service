from src.models.user import Permission
from sqlalchemy import select
from src.repositories.core import BaseRepository
from src.services.exceptions import (
    PermissionNotFoundException,
)


class PermissionRepository(BaseRepository):
    model = Permission

    async def get_by_name(self, name: str):
        stmt = select(self.model).where(self.model.name == name)

        result = await self.db.execute(stmt)
        if not (role := result.scalars().first()):
            raise PermissionNotFoundException
        return role
