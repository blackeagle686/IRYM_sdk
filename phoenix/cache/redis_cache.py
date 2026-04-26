import json
import redis.asyncio as redis
from typing import Any, Optional
from phoenix.cache.base import BaseCache
from phoenix.core.config import config

class RedisCache(BaseCache):
    def __init__(self):
        self.redis = None

    async def init(self):
        self.redis = redis.from_url(config.REDIS_URL, decode_responses=True)

    async def get(self, key: str) -> Optional[Any]:
        if not self.redis:
            await self.init()
        value = await self.redis.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None

    async def set(self, key: str, value: Any, ttl: int) -> None:
        if not self.redis:
            await self.init()
        try:
            serialized_value = json.dumps(value)
        except TypeError:
            serialized_value = str(value)
        await self.redis.set(key, serialized_value, ex=ttl)

    async def delete(self, key: str) -> None:
        if not self.redis:
            await self.init()
        await self.redis.delete(key)
