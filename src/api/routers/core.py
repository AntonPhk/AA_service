from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from starlette import status
from src.repositories.core import get_async_session
from src.services.exceptions import ExternalErrorException

router = APIRouter(prefix="", tags=["core"])


@router.get("/healthcheck", status_code=200)
async def healthcheck(
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    try:
        stmt = text("SELECT 1")
        await session.execute(stmt)
        return {"status": status.HTTP_200_OK}
    except Exception:
        raise ExternalErrorException
