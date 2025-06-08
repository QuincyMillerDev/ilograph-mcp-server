"""
Simple in-memory cache with TTL for the Ilograph MCP Server.

This module provides a lightweight caching system for dynamic resources like
specifications, documentation, and icon catalogs. Uses in-memory storage with
time-to-live (TTL) expiration for cache entries.
"""

import logging
import time
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class CacheEntry:
    """Represents a single cache entry with data and expiration time."""

    def __init__(self, data: Any, ttl_seconds: int):
        """
        Initialize a cache entry.

        Args:
            data: The data to cache
            ttl_seconds: Time-to-live in seconds
        """
        self.data = data
        self.created_at = time.time()
        self.expires_at = self.created_at + ttl_seconds

    def is_expired(self) -> bool:
        """Check if this cache entry has expired."""
        return time.time() > self.expires_at

    def age_seconds(self) -> float:
        """Get the age of this cache entry in seconds."""
        return time.time() - self.created_at


class MemoryCache:
    """Simple in-memory cache with TTL support."""

    def __init__(self) -> None:
        """Initialize the cache."""
        self._cache: Dict[str, CacheEntry] = {}

    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache.

        Args:
            key: The cache key

        Returns:
            The cached value if it exists and hasn't expired, None otherwise
        """
        if key not in self._cache:
            logger.debug(f"Cache miss for key: {key}")
            return None

        entry = self._cache[key]
        if entry.is_expired():
            logger.debug(f"Cache expired for key: {key} (age: {entry.age_seconds():.1f}s)")
            del self._cache[key]
            return None

        logger.debug(f"Cache hit for key: {key} (age: {entry.age_seconds():.1f}s)")
        return entry.data

    def set(self, key: str, value: Any, ttl_seconds: int = 86400) -> None:
        """
        Set a value in the cache.

        Args:
            key: The cache key
            value: The value to cache
            ttl_seconds: Time-to-live in seconds (default: 24 hours)
        """
        self._cache[key] = CacheEntry(value, ttl_seconds)
        logger.debug(f"Cached key: {key} with TTL: {ttl_seconds}s")

    def delete(self, key: str) -> bool:
        """
        Delete a value from the cache.

        Args:
            key: The cache key

        Returns:
            True if the key was deleted, False if it didn't exist
        """
        if key in self._cache:
            del self._cache[key]
            logger.debug(f"Deleted cache key: {key}")
            return True
        return False

    def clear(self) -> None:
        """Clear all entries from the cache."""
        count = len(self._cache)
        self._cache.clear()
        logger.info(f"Cleared {count} entries from cache")

    def cleanup_expired(self) -> int:
        """
        Remove all expired entries from the cache.

        Returns:
            Number of expired entries removed
        """
        expired_keys = [key for key, entry in self._cache.items() if entry.is_expired()]

        for key in expired_keys:
            del self._cache[key]

        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")

        return len(expired_keys)

    def stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        total_entries = len(self._cache)
        expired_entries = sum(1 for entry in self._cache.values() if entry.is_expired())
        valid_entries = total_entries - expired_entries

        return {
            "total_entries": total_entries,
            "valid_entries": valid_entries,
            "expired_entries": expired_entries,
            "keys": list(self._cache.keys()),
        }


# Global cache instance for the server
cache = MemoryCache()


def get_cache() -> MemoryCache:
    """Get the global cache instance."""
    return cache
