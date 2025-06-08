"""
HTTP client utility for the Ilograph MCP Server.

This module provides HTTP request capabilities with retry logic, caching integration,
and proper error handling for fetching content from Ilograph sources.
"""

import asyncio
import logging
from typing import Optional
from urllib.parse import urljoin

import httpx
from httpx import HTTPStatusError, RequestError, Response

logger = logging.getLogger(__name__)


class IlographHTTPClient:
    """HTTP client with retry logic and error handling for Ilograph sources."""

    def __init__(self, timeout: int = 30, max_retries: int = 3):
        """
        Initialize the HTTP client.

        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.base_urls = {
            "docs": "https://www.ilograph.com/docs/",
            "spec": "https://www.ilograph.com/docs/spec/",
            "icons": "https://www.ilograph.com/docs/iconlist.txt",
        }

        # Headers to mimic a real browser request
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

    async def fetch_with_retry(self, url: str, method: str = "GET", **kwargs) -> Optional[Response]:
        """
        Fetch URL with retry logic and comprehensive error handling.

        Args:
            url: URL to fetch
            method: HTTP method (default: GET)
            **kwargs: Additional httpx request parameters

        Returns:
            Response object if successful, None if all retries failed
        """
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                logger.debug(f"Fetching {url} (attempt {attempt + 1}/{self.max_retries + 1})")

                async with httpx.AsyncClient(
                    timeout=self.timeout, headers=self.headers, follow_redirects=True
                ) as client:
                    response = await client.request(method, url, **kwargs)
                    response.raise_for_status()

                    logger.info(f"Successfully fetched {url} ({response.status_code})")
                    return response

            except HTTPStatusError as e:
                last_exception = e
                logger.warning(f"HTTP {e.response.status_code} error for {url}: {e}")

                # Don't retry client errors (4xx)
                if 400 <= e.response.status_code < 500:
                    logger.error(f"Client error {e.response.status_code} for {url}, not retrying")
                    break

            except RequestError as e:
                last_exception = e
                logger.warning(f"Request error for {url}: {e}")

            except Exception as e:
                last_exception = e
                logger.error(f"Unexpected error fetching {url}: {e}")

            # Wait before retry (exponential backoff)
            if attempt < self.max_retries:
                wait_time = 2**attempt
                logger.debug(f"Waiting {wait_time}s before retry...")
                await asyncio.sleep(wait_time)

        logger.error(
            f"Failed to fetch {url} after {self.max_retries + 1} attempts: {last_exception}"
        )
        return None

    def get_documentation_url(self, section: str) -> str:
        """
        Get the full URL for a documentation section.

        Args:
            section: Documentation section name

        Returns:
            Full URL for the documentation section
        """
        # Map section names to their URL paths
        section_paths = {
            "resources": "editing/resources/",
            "relation-perspectives": "editing/perspectives/relation-perspectives/",
            "sequence-perspectives": "editing/perspectives/sequence-perspectives/",
            "references": "editing/perspectives/references/",
            "advanced-references": "editing/perspectives/advanced-references/",
            "resource-sizes-and-positions": "editing/perspectives/resource-sizes-and-positions/",
            "parent-overrides": "editing/perspectives/parent-overrides/",
            "perspectives-other-properties": "editing/perspectives/other-properties/",
            "icons": "editing/icons/",
            "walkthroughs": "editing/walkthroughs/",
            "contexts": "editing/contexts/",
            "imports": "editing/imports/",
            "markdown": "editing/markdown/",
            "tutorial": "editing/tutorial/",
        }

        if section in section_paths:
            return urljoin(self.base_urls["docs"], section_paths[section])
        else:
            # Default to treating as a direct path
            return urljoin(self.base_urls["docs"], section.rstrip("/") + "/")

    async def fetch_documentation_html(self, section: str) -> Optional[str]:
        """
        Fetch HTML content for a documentation section.

        Args:
            section: Documentation section name

        Returns:
            HTML content as string if successful, None otherwise
        """
        url = self.get_documentation_url(section)
        response = await self.fetch_with_retry(url)

        if response is None:
            return None

        try:
            return response.text
        except Exception as e:
            logger.error(f"Error reading response text from {url}: {e}")
            return None

    async def fetch_specification_html(self) -> Optional[str]:
        """
        Fetch HTML content for the Ilograph specification.

        Returns:
            HTML content as string if successful, None otherwise
        """
        response = await self.fetch_with_retry(self.base_urls["spec"])

        if response is None:
            return None

        try:
            return response.text
        except Exception as e:
            logger.error(f"Error reading specification response text: {e}")
            return None

    async def fetch_icon_catalog(self) -> Optional[str]:
        """
        Fetch the icon catalog text file.

        Returns:
            Icon catalog content as string if successful, None otherwise
        """
        response = await self.fetch_with_retry(self.base_urls["icons"])

        if response is None:
            return None

        try:
            return response.text
        except Exception as e:
            logger.error(f"Error reading icon catalog response text: {e}")
            return None


# Global HTTP client instance
_http_client: Optional[IlographHTTPClient] = None


def get_http_client() -> IlographHTTPClient:
    """Get the global HTTP client instance."""
    global _http_client
    if _http_client is None:
        _http_client = IlographHTTPClient()
    return _http_client
