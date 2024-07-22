import redis.asyncio as aioredis
from src.core.config import settings


REDIS_URL = settings.redis_url


class TokenWarehouse:
    def __init__(self):
        self._warehouse_url = settings.redis_url
        self._warehouse = aioredis.from_url(self._warehouse_url)

    async def add_token_to_redis(self, user_id: str, token: str) -> bool | dict:
        try:
            await self._warehouse.set(str(user_id), token)
            await self._warehouse.aclose()
            return True
        except Exception as e:
            return {"detail": str(e)}

    async def is_token_exist(self, user_id: str) -> bool:
        result = await self._warehouse.exists(str(user_id))
        await self._warehouse.aclose()
        return result
