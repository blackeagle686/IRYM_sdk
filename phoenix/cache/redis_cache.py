import json
import redis.asyncio as redis
from typing import Any, Optional
from phoenix.cache.base import BaseCache
from phoenix.core.config import config
from phoenix.observability.logger import get_logger

logger = get_logger("Phoenix AI.Cache.Redis")

class RedisCache(BaseCache):
    def __init__(self):
        self.redis = None
        self._failed = False

    async def init(self):
        try:
            self.redis = redis.from_url(config.REDIS_URL, decode_responses=True)
            # Ping to verify connection
            await self.redis.ping()
            self._failed = False
        except Exception as e:
            logger.warning(f"Failed to connect to Redis at {config.REDIS_URL}: {e}. Caching disabled.")
            self.redis = None
            self._failed = True

    async def get(self, key: str) -> Optional[Any]:
        if self._failed:
            return None
            
        if not self.redis:
            await self.init()
            if self._failed: return None
            
        try:
            value = await self.redis.get(key)
            if value:
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
        except Exception:
            self._failed = True
        return None

    async def set(self, key: str, value: Any, ttl: int) -> None:
        if self._failed:
            return
            
        if not self.redis:
            await self.init()
            if self._failed: return
            
        try:
            serialized_value = json.dumps(value)
            await self.redis.set(key, serialized_value, ex=ttl)
        except Exception:
            self._failed = True

    async def delete(self, key: str) -> None:
        if self._failed:
            return
            
        if not self.redis:
            await self.init()
            if self._failed: return
            
        try:
            await self.redis.delete(key)
        except Exception:
            self._failed = True
