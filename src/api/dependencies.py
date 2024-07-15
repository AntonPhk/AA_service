from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession

from src.services.user_service import UserService
from src.repositories.core import get_async_session
from fastapi import Depends


def get_user_service(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> UserService:
    return UserService(session)
