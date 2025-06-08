"""
Content fetcher for the Ilograph MCP Server.

This module handles fetching and processing content from Ilograph sources.
Provides comprehensive documentation fetching with caching, HTML to markdown conversion,
and error handling for reliable content delivery to AI agents.
"""

import logging
import re
from typing import Any, Dict, List, Optional

from ..utils.http_client import get_http_client
from ..utils.markdown_converter import get_markdown_converter
from .cache import get_cache

logger = logging.getLogger(__name__)


class IlographContentFetcher:
    """Handles fetching and processing content from Ilograph sources."""

    def __init__(self) -> None:
        """Initialize the content fetcher."""
        self.http_client = get_http_client()
        self.markdown_converter = get_markdown_converter()
        self.cache = get_cache()

        # Cache TTL settings (in seconds)
        self.cache_ttl = {
            "documentation": 86400,  # 24 hours
            "specification": 86400,  # 24 hours
            "icons": 86400,  # 24 hours
        }

    async def fetch_documentation_section(self, section: str) -> Optional[str]:
        """
        Fetch and convert documentation section to markdown with caching.

        Args:
            section: Documentation section name (e.g., 'resources', 'relation-perspectives')

        Returns:
            Markdown content or None if unavailable
        """
        cache_key = f"docs_{section}"

        # Check cache first
        cached_content = self.cache.get(cache_key)
        if cached_content is not None:
            logger.debug(f"Returning cached documentation for section: {section}")
            return str(cached_content)

        try:
            logger.info(f"Fetching documentation section: {section}")

            # Fetch HTML content
            html_content = await self.http_client.fetch_documentation_html(section)
            if html_content is None:
                logger.error(f"Failed to fetch HTML for section: {section}")
                return None

            # Get source URL for link resolution
            source_url = self.http_client.get_documentation_url(section)

            # Convert to markdown
            markdown_content = self.markdown_converter.convert_html_to_markdown(
                html_content, source_url
            )

            # Cache the result
            self.cache.set(cache_key, markdown_content, self.cache_ttl["documentation"])

            logger.info(f"Successfully processed documentation for section: {section}")
            return markdown_content

        except Exception as e:
            logger.error(f"Error fetching documentation section '{section}': {e}")
            return None

    async def fetch_specification(self) -> Optional[str]:
        """
        Fetch and parse the Ilograph specification with caching.

        Returns:
            Specification content as markdown or None if unavailable
        """
        cache_key = "specification"

        # Check cache first
        cached_content = self.cache.get(cache_key)
        if cached_content is not None:
            logger.debug("Returning cached specification")
            return str(cached_content)

        try:
            logger.info("Fetching Ilograph specification")

            # Fetch HTML content
            html_content = await self.http_client.fetch_specification_html()
            if html_content is None:
                logger.error("Failed to fetch specification HTML")
                return None

            # Convert to markdown
            markdown_content = self.markdown_converter.convert_html_to_markdown(
                html_content, self.http_client.base_urls["spec"]
            )

            # Cache the result
            self.cache.set(cache_key, markdown_content, self.cache_ttl["specification"])

            logger.info("Successfully processed specification")
            return markdown_content

        except Exception as e:
            logger.error(f"Error fetching specification: {e}")
            return None

    async def fetch_icon_catalog(self) -> Optional[str]:
        """
        Fetch and parse the Ilograph icon catalog with caching.

        Returns:
            Icon catalog content or None if unavailable
        """
        cache_key = "icon_catalog"

        # Check cache first
        cached_content = self.cache.get(cache_key)
        if cached_content is not None:
            logger.debug("Returning cached icon catalog")
            return str(cached_content)

        try:
            logger.info("Fetching Ilograph icon catalog")

            # Fetch icon catalog text
            catalog_content = await self.http_client.fetch_icon_catalog()
            if catalog_content is None:
                logger.error("Failed to fetch icon catalog")
                return None

            # Cache the result
            self.cache.set(cache_key, catalog_content, self.cache_ttl["icons"])

            logger.info("Successfully fetched icon catalog")
            return catalog_content

        except Exception as e:
            logger.error(f"Error fetching icon catalog: {e}")
            return None

    def _parse_icon_catalog(self, catalog_content: str) -> List[Dict[str, Any]]:
        """
        Parse the icon catalog text into structured data.

        Args:
            catalog_content: Raw icon catalog text content

        Returns:
            List of icon dictionaries with path, provider, category, and name
        """
        icons = []
        lines = catalog_content.strip().split("\n")

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Example line: "AWS/Analytics/AWS-Athena"
            # Split by '/' to get provider, category, name
            parts = line.split("/")
            if len(parts) >= 3:
                provider = parts[0]
                category = parts[1]
                name = parts[2]

                # Generate usage example
                usage = f'iconStyle: "{line}"'

                icons.append(
                    {
                        "path": line,
                        "provider": provider,
                        "category": category,
                        "name": name,
                        "usage": usage,
                    }
                )

        return icons

    async def search_icons(
        self, query: str, provider: Optional[str] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Search icons with semantic matching and optional provider filtering.

        Args:
            query: Search term (e.g., 'database', 'aws lambda', 'kubernetes')
            provider: Optional provider filter ('AWS', 'Azure', 'GCP', 'Networking')

        Returns:
            List of matching icons or None if catalog unavailable
        """
        try:
            # Fetch catalog content
            catalog_content = await self.fetch_icon_catalog()
            if catalog_content is None:
                return None

            # Parse catalog into structured data
            all_icons = self._parse_icon_catalog(catalog_content)

            # Apply provider filter if specified
            if provider:
                all_icons = [icon for icon in all_icons if icon["provider"] == provider]

            # Perform semantic search
            query_lower = query.lower()
            matching_icons = []

            for icon in all_icons:
                # Check if query matches any part of the icon
                searchable_text = (
                    f"{icon['name']} {icon['category']} {icon['provider']} {icon['path']}".lower()
                )

                # Score based on different types of matches
                score = 0

                # Exact name match (highest priority)
                if query_lower in icon["name"].lower():
                    score += 100

                # Category match
                if query_lower in icon["category"].lower():
                    score += 50

                # Provider match
                if query_lower in icon["provider"].lower():
                    score += 25

                # Path match
                if query_lower in icon["path"].lower():
                    score += 10

                # General text match
                if query_lower in searchable_text:
                    score += 5

                if score > 0:
                    icon_with_score = icon.copy()
                    icon_with_score["_score"] = score
                    matching_icons.append(icon_with_score)

            # Sort by score (descending) and limit results
            matching_icons.sort(key=lambda x: x["_score"], reverse=True)

            # Remove the score from the final results and limit to top 50
            for icon in matching_icons[:50]:
                if "_score" in icon:
                    del icon["_score"]

            return matching_icons[:50]

        except Exception as e:
            logger.error(f"Error searching icons: {e}")
            return None

    async def get_icon_providers(self) -> Optional[Dict[str, Any]]:
        """
        Get information about all available icon providers and their categories.

        Returns:
            Dictionary with provider information or None if catalog unavailable
        """
        try:
            # Fetch catalog content
            catalog_content = await self.fetch_icon_catalog()
            if catalog_content is None:
                return None

            # Parse catalog into structured data
            all_icons = self._parse_icon_catalog(catalog_content)

            # Organize by provider
            providers: Dict[str, Any] = {}
            for icon in all_icons:
                provider = icon["provider"]
                category = icon["category"]

                if provider not in providers:
                    providers[provider] = {"categories": {}, "total_icons": 0}

                if category not in providers[provider]["categories"]:
                    providers[provider]["categories"][category] = 0

                providers[provider]["categories"][category] += 1
                providers[provider]["total_icons"] += 1

            return {
                "providers": providers,
                "total_providers": len(providers),
                "message": f"Found {len(providers)} icon providers with {len(all_icons)} total icons",
            }

        except Exception as e:
            logger.error(f"Error getting icon providers: {e}")
            return None

    async def get_icon_catalog_stats(self) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive statistics about the icon catalog.

        Returns:
            Dictionary with catalog statistics or None if catalog unavailable
        """
        try:
            # Fetch catalog content
            catalog_content = await self.fetch_icon_catalog()
            if catalog_content is None:
                return None

            # Parse catalog into structured data
            all_icons = self._parse_icon_catalog(catalog_content)

            # Generate statistics
            providers: Dict[str, int] = {}
            categories: Dict[str, int] = {}

            for icon in all_icons:
                provider = icon["provider"]
                category = icon["category"]

                # Count by provider
                if provider not in providers:
                    providers[provider] = 0
                providers[provider] += 1

                # Count by category
                if category not in categories:
                    categories[category] = 0
                categories[category] += 1

            # Most common categories
            top_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)[:10]

            return {
                "total_icons": len(all_icons),
                "providers": providers,
                "total_providers": len(providers),
                "total_categories": len(categories),
                "top_categories": [
                    {"name": name, "count": count} for name, count in top_categories
                ],
                "catalog_url": self.http_client.base_urls["icons"],
                "last_updated": "Live from ilograph.com",
            }

        except Exception as e:
            logger.error(f"Error getting icon catalog stats: {e}")
            return None

    def get_supported_documentation_sections(self) -> Dict[str, str]:
        """
        Get the list of supported documentation sections with descriptions.

        Returns:
            Dictionary mapping section names to descriptions
        """
        return {
            "resources": "Resource tree organization, hierarchies, instanceOf patterns, abstract resources",
            "relation-perspectives": "Arrow connections, from/to properties, routing, labels, directions",
            "sequence-perspectives": "Time-based diagrams with steps, bidirectional flows, async operations",
            "references": "Resource reference patterns and advanced referencing techniques",
            "advanced-references": "Complex reference scenarios and advanced usage patterns",
            "resource-sizes-and-positions": "Layout control, resource sizing, visual hierarchy management",
            "parent-overrides": "Resource parent overrides in perspectives with scale properties",
            "perspectives-other-properties": "Additional perspective properties and configuration options",
            "icons": "Icon system with iconStyle, icon paths, and categorization",
            "walkthroughs": "Interactive step-by-step guides through diagrams",
            "contexts": "Multiple context views with roots, extends inheritance, context switching",
            "imports": "Namespace management with from/namespace properties, component reuse",
            "markdown": "Rich text support in descriptions, notes, and diagram text",
            "tutorial": "Complete tutorial for learning Ilograph diagram creation",
        }

    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check of the fetcher by testing connectivity.

        Returns:
            Dictionary with health status information
        """
        health: Dict[str, Any] = {
            "status": "healthy",
            "services": {},
            "cache_stats": self.cache.stats(),
        }

        try:
            # Test documentation endpoint
            test_response = await self.http_client.fetch_with_retry(
                self.http_client.base_urls["docs"], method="HEAD"
            )
            health["services"]["documentation"] = {
                "status": "healthy" if test_response else "unhealthy",
                "url": self.http_client.base_urls["docs"],
            }
        except Exception as e:
            health["services"]["documentation"] = {
                "status": "unhealthy",
                "error": str(e),
                "url": self.http_client.base_urls["docs"],
            }

        try:
            # Test specification endpoint
            test_response = await self.http_client.fetch_with_retry(
                self.http_client.base_urls["spec"], method="HEAD"
            )
            health["services"]["specification"] = {
                "status": "healthy" if test_response else "unhealthy",
                "url": self.http_client.base_urls["spec"],
            }
        except Exception as e:
            health["services"]["specification"] = {
                "status": "unhealthy",
                "error": str(e),
                "url": self.http_client.base_urls["spec"],
            }

        try:
            # Test icons endpoint
            test_response = await self.http_client.fetch_with_retry(
                self.http_client.base_urls["icons"], method="HEAD"
            )
            health["services"]["icons"] = {
                "status": "healthy" if test_response else "unhealthy",
                "url": self.http_client.base_urls["icons"],
            }
        except Exception as e:
            health["services"]["icons"] = {
                "status": "unhealthy",
                "error": str(e),
                "url": self.http_client.base_urls["icons"],
            }

        # Overall status
        unhealthy_services = [
            service for service, info in health["services"].items() if info["status"] == "unhealthy"
        ]

        if unhealthy_services:
            health["status"] = "degraded"
            health["unhealthy_services"] = unhealthy_services

        return health


# Global fetcher instance
fetcher = IlographContentFetcher()


def get_fetcher() -> IlographContentFetcher:
    """Get the global fetcher instance."""
    return fetcher
