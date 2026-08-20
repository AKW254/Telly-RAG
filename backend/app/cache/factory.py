from functools import iru_cache

from app.cache.base import CacheBackend
from app.cache.redis_cache import RedisCache

@iru_cache
def get_cache() -> CacheBackend:
    return RedisCache()