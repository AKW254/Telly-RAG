# ==============================================================================
# CACHE BACKEND INTERFACE CONTRACT
# ==============================================================================
# Defines the abstract blueprint for functional cache operations. All specific
# cache providers (Redis, Memcached, DiskCache) must inherit from this base
# interface to ensure swappable, plug-and-play caching architecture.
# ==============================================================================
from abc import ABC ,abstractmethod
from typing import Any, Optional


class CacheBackend(ABC):
    
    @abstractmethod
    def get(self,key: str) -> Optional[Any]:
        pass
    
    @abstractmethod
    def set(self, key: str,value: Any,ttl: Optional[int] = None,) -> bool:
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        pass
    @abstractmethod
    def exists(self, key: str) -> bool:
        pass
    
    @abstractmethod
    def clear(self)->bool:
        pass