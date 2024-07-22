from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from typing import Any, Optional, Type
from sqlalchemy import select, update, asc, desc
from pydantic import BaseModel

from src.core.config import settings
from src.models.core import BaseModel as CoreBaseModel
from src.ports.database_interface import DatabaseInterface


class DBSessionMixin:
    def __init__(self, db: AsyncSession):
        self.db = db


class BaseRepository(DatabaseInterface, DBSessionMixin):
    model: Type[CoreBaseModel]

    async def get_by_id(self, entity_id: Any):
        stmt = select(self.model).where(self.model.id == entity_id)
        result = await self.db.execute(stmt)
        instance = result.scalars().first()

        return instance

    async def get_all(
        self,
        page: int = 1,
        limit: int = 10,
        order_by: str = "asc",
        sort_by: Optional[str] = None,
    ):
        stmt = select(self.model)

        if sort_by:
            sort_column = getattr(self.model, sort_by, None)
            match order_by:
                case "asc":
                    stmt = stmt.order_by(asc(sort_column))
                case "desc":
                    stmt = stmt.order_by(desc(sort_column))

        offset_value = (page - 1) * limit
        stmt = stmt.offset(offset_value).limit(limit)

        result = await self.db.execute(stmt)
        instances = result.scalars().all()
        return instances

    async def create(self, data: BaseModel):
        values = data.model_dump()
        new_instance = self.model(**values)

        self.db.add(new_instance)
        await self.db.commit()
        await self.db.refresh(new_instance)
        return new_instance

    async def update(self, entity_id: Any, data: BaseModel):
        values = data.model_dump(exclude_unset=True)
        stmt = (
            update(self.model)
            .where(self.model.id == entity_id)
            .values(values)
            .returning(self.model)
        )

        updated_instance = await self.db.execute(stmt)
        result = updated_instance.scalars().first()
        await self.db.commit()
        return result

    async def delete(self, entity_id: Any):
        instance = await self.get_by_id(entity_id)
        if instance:
            await self.db.delete(instance)
            await self.db.commit()
            return True
        else:
            return False


async_engine = create_async_engine(url=settings.postgres_url_async, echo=True)
async_session_builder = async_sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)


async def async_init_db():
    """
    Manually initialize the database
    """
    async with async_engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)


async def clear_db():
    """
    Manually clear the database
    """
    async with async_engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)


async def get_async_session() -> AsyncSession:
    """
    Generator for getting a session
    """
    async with async_session_builder() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
