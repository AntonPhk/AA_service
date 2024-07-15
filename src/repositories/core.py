from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.core.config import settings
from src.models.core import BaseModel


class DBSessionMixin:
    def __init__(self, db: AsyncSession):
        self.db = db


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
