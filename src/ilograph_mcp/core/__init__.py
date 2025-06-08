"""
Core functionality for the Ilograph MCP Server.

This package contains the core infrastructure components including
content fetching, caching, and parsing utilities.
"""

from .cache import MemoryCache, get_cache

# Core components will be imported here when implemented
from .fetcher import IlographContentFetcher, get_fetcher

# from .parser import html_to_markdown

__all__ = [
    "IlographContentFetcher",
    "get_fetcher",
    "MemoryCache",
    "get_cache",
    # "html_to_markdown",
]
