import json
import redis.asyncio as redis
from typing import Any, Optional
from IRYM_sdk.cache.base import BaseCache
from IRYM_sdk.core.config import config

class RedisCache(BaseCache):
    def __init__(self):
        self.redis = None

    async def init(self):
        self.redis = redis.from_url(config.REDIS_URL, decode_responses=True)

    async def get(self, key: str) -> Optional[Any]:
        if not self.redis:
            raise RuntimeError("RedisCache is not initialized. Call init() first.")
        value = await self.redis.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None

    async def set(self, key: str, value: Any, ttl: int) -> None:
        if not self.redis:
            raise RuntimeError("RedisCache is not initialized. Call init() first.")
        try:
            serialized_value = json.dumps(value)
        except TypeError:
            serialized_value = str(value)
        await self.redis.set(key, serialized_value, ex=ttl)

    async def delete(self, key: str) -> None:
        if not self.redis:
            raise RuntimeError("RedisCache is not initialized. Call init() first.")
        await self.redis.delete(key)
