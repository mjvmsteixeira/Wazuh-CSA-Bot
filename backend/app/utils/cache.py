"""Redis cache utility module."""

import json
import redis
from typing import Any, Optional
from functools import wraps

from app.config import settings
from app.utils.logger import logger


class RedisCache:
    """Redis cache client wrapper."""

    def __init__(self):
        """Initialize Redis client."""
        self.client: Optional[redis.Redis] = None
        self.enabled = settings.enable_redis_cache

        if self.enabled and settings.redis_url:
            try:
                self.client = redis.from_url(
                    settings.redis_url,
                    decode_responses=True,
                    socket_connect_timeout=5
                )
                # Test connection
                self.client.ping()
                logger.info("Redis cache connected successfully")
            except Exception as e:
                logger.warning(f"Failed to connect to Redis: {e}. Cache disabled.")
                self.enabled = False
                self.client = None
        else:
            logger.info("Redis cache is disabled")

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None
        """
        if not self.enabled or not self.client:
            return None

        try:
            value = self.client.get(key)
            if value:
                logger.debug(f"Cache HIT: {key}")
                return json.loads(value)
            logger.debug(f"Cache MISS: {key}")
            return None
        except Exception as e:
            logger.error(f"Error getting cache key {key}: {e}")
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (uses default from settings if None)

        Returns:
            True if successful, False otherwise
        """
        if not self.enabled or not self.client:
            return False

        try:
            ttl = ttl or settings.redis_ttl_default
            serialized = json.dumps(value)
            self.client.setex(key, ttl, serialized)
            logger.debug(f"Cache SET: {key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.error(f"Error setting cache key {key}: {e}")
            return False

    def delete(self, key: str) -> bool:
        """
        Delete key from cache.

        Args:
            key: Cache key

        Returns:
            True if successful, False otherwise
        """
        if not self.enabled or not self.client:
            return False

        try:
            self.client.delete(key)
            logger.debug(f"Cache DELETE: {key}")
            return True
        except Exception as e:
            logger.error(f"Error deleting cache key {key}: {e}")
            return False

    def clear_pattern(self, pattern: str) -> int:
        """
        Clear all keys matching pattern.

        Args:
            pattern: Key pattern (e.g., "agents:*")

        Returns:
            Number of keys deleted
        """
        if not self.enabled or not self.client:
            return 0

        try:
            keys = self.client.keys(pattern)
            if keys:
                count = self.client.delete(*keys)
                logger.debug(f"Cache CLEAR: {pattern} ({count} keys)")
                return count
            return 0
        except Exception as e:
            logger.error(f"Error clearing cache pattern {pattern}: {e}")
            return 0


# Global cache instance
cache = RedisCache()


def cached(key_prefix: str, ttl: Optional[int] = None):
    """
    Decorator for caching function results.

    Args:
        key_prefix: Prefix for cache key
        ttl: Time to live in seconds

    Example:
        @cached("agents", ttl=300)
        async def get_agents():
            return await fetch_agents()
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            key_parts = [key_prefix, func.__name__]
            if args:
                key_parts.extend(str(arg) for arg in args)
            if kwargs:
                key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            cache_key = ":".join(key_parts)

            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            # Execute function and cache result
            result = await func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result

        return wrapper
    return decorator
