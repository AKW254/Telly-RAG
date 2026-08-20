#lru(Least Recently Used) is is a built-in memoization decorator from Python's standard functools module.
from functools import lru_cache

from app.cache.base import CacheBackend
from app.cache.redis_cache import RedisCache
#This decorator remembers the result of a function so Python does not have to run it again
#Python skips creating a new connection. It gives you back the saved RedisCache connection instantly.
@lru_cache
def get_cache() -> CacheBackend:
    return RedisCache()