# ==============================================================================
# REDIS CACHE BACKEND IMPLEMENTATION
# ==============================================================================
# Complete implementation of the CacheBackend abstract interface using Redis.
# Handles high-performance key-value storage, automatic JSON serialization and 
# deserialization, default TTL expiration fallbacks, and connection health checks.
# ==============================================================================

import json
from typing import Any, Optional

import redis

from app.cache.base import CacheBackend
from app.config.settings import settings


class RedisCache(CacheBackend):
    # Redis-backed concrete caching engine adhering to CacheBackend interface.

    def __init__(
        self,
        redis_url: Optional[str] = None,
        default_ttl: int = 3600,
    ) -> None:
        # Initialize Redis client with connection URL and default TTL.
        self.default_ttl = default_ttl
        self.client = redis.Redis.from_url(
            redis_url or settings.redis_url,
            decode_responses=True,
        )

    def get(self, key: str) -> Optional[Any]:
        #Retrieve and deserialize a value from Redis by key.
        #Attempts JSON parsing on hit; falls back to raw string if decoding fails.
        
        value = self.client.get(key)
        if value is None:
            return None

        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value

    def set(self,key: str,value: Any,ttl: Optional[int] = None,) -> bool:
        # Serialize and store a key-value pair with expiration time (TTL).
        if not isinstance(value, str):
            value = json.dumps(value)

        return bool(self.client.setex(key,ttl or self.default_ttl,value,))

    def delete(self, key: str) -> bool:
        # Remove a key from Redis. Returns True if deleted, False if missing.
        return bool(self.client.delete(key))

    def exists(self, key: str) -> bool:
        # Check whether a key exists in Redis.
        return bool(self.client.exists(key))

    def clear(self) -> bool:
        # Flush all keys in the current Redis database.
        return bool(self.client.flushdb())

    def ping(self) -> bool:
        # Verify Redis connection health via PING command.
        try:
            return bool(self.client.ping())
        except redis.RedisError:
            return False