"""
Fetch Icons Tool for Ilograph MCP Server.

This tool provides access to the live Ilograph icon catalog from ilograph.com/docs/iconlist.txt,
enabling semantic search and provider filtering for icon discovery.
Includes caching, error handling, and detailed logging following FastMCP patterns.
"""

import logging
from typing import Any, Dict, List, Optional

from fastmcp import Context, FastMCP

from ..core.fetcher import get_fetcher

logger = logging.getLogger(__name__)


def register_fetch_icons_tool(mcp: FastMCP) -> None:
    """Register the fetch icons tool with the FastMCP server."""

    @mcp.tool(
        annotations={
            "title": "Search Ilograph Icons",
            "readOnlyHint": True,
            "description": "Searches the live icon catalog with semantic matching and provider filtering",
        }
    )
    async def search_icons_tool(
        query: str, provider: Optional[str] = None, ctx: Optional[Context] = None
    ) -> List[Dict[str, Any]]:
        """
        Searches the current icon catalog with semantic matching.

        This tool fetches the live icon catalog from Ilograph and provides intelligent
        search capabilities to help find appropriate icons for diagram resources.

        Args:
            query: Search term (e.g., 'database', 'aws lambda', 'kubernetes', 'storage')
            provider: Optional filter by provider ('AWS', 'Azure', 'GCP', 'Networking')

        Returns:
            list: Matching icons with paths, categories, and usage information.
                  Each icon dict contains:
                  - path: The icon path for use in Ilograph diagrams
                  - provider: The cloud provider or category (AWS, Azure, GCP, Networking)
                  - category: The service category (e.g., 'Compute', 'Database', 'Analytics')
                  - name: The specific icon name
                  - usage: Example usage string for Ilograph diagrams
        """
        # Validate input parameters
        if not query or not isinstance(query, str):
            error_msg = "Query parameter is required and must be a non-empty string"
            if ctx:
                await ctx.error(error_msg)
            return [{"error": error_msg}]

        query = query.strip().lower()
        if not query:
            error_msg = "Query parameter cannot be empty or only whitespace"
            if ctx:
                await ctx.error(error_msg)
            return [{"error": error_msg}]

        # Normalize and validate provider filter
        if provider:
            provider = provider.strip()
            valid_providers = ["AWS", "Azure", "GCP", "Networking"]
            if provider not in valid_providers:
                error_msg = (
                    f"Invalid provider '{provider}'. Valid providers: {', '.join(valid_providers)}"
                )
                if ctx:
                    await ctx.error(error_msg)
                return [{"error": error_msg}]

        try:
            # Log the search request
            provider_filter = f" (filtered by {provider})" if provider else ""
            if ctx:
                await ctx.info(f"Searching Ilograph icons for '{query}'{provider_filter}")

            # Get fetcher instance
            fetcher = get_fetcher()

            # Search icons
            icons = await fetcher.search_icons(query, provider)

            if icons is None:
                error_msg = (
                    "Failed to fetch icon catalog. The service may be temporarily unavailable."
                )
                if ctx:
                    await ctx.error(error_msg)
                return [{"error": error_msg}]

            if not icons:
                # No matches found
                provider_note = f" in {provider}" if provider else ""
                if ctx:
                    await ctx.info(f"No icons found matching '{query}'{provider_note}")
                return [
                    {
                        "message": f"No icons found matching '{query}'{provider_note}",
                        "suggestion": "Try broader search terms like 'database', 'compute', 'storage', or 'network'",
                        "available_providers": ["AWS", "Azure", "GCP", "Networking"],
                    }
                ]

            # Log successful search
            result_count = len(icons)
            if ctx:
                await ctx.info(f"Found {result_count} icons matching '{query}'{provider_filter}")

            return icons

        except Exception as e:
            error_msg = f"Unexpected error searching icons: {str(e)}"
            if ctx:
                await ctx.error(error_msg)
            return [
                {
                    "error": "An unexpected error occurred while searching icons. Please try again later."
                }
            ]

    @mcp.tool(
        annotations={
            "title": "List Available Icon Providers",
            "readOnlyHint": True,
            "description": "Lists all available icon providers and categories from the icon catalog",
        }
    )
    async def list_icon_providers_tool(ctx: Optional[Context] = None) -> Dict[str, Any]:
        """
        Lists all available icon providers and their categories.

        This tool provides an overview of the icon catalog structure,
        showing available providers and their service categories.

        Returns:
            dict: Provider information with categories and icon counts
        """
        try:
            if ctx:
                await ctx.info("Fetching icon provider information")

            # Get fetcher instance
            fetcher = get_fetcher()

            # Get provider information
            provider_info = await fetcher.get_icon_providers()

            if provider_info is None:
                error_msg = "Failed to fetch icon provider information. The service may be temporarily unavailable."
                if ctx:
                    await ctx.error(error_msg)
                return {"error": error_msg}

            if ctx:
                await ctx.info(
                    f"Retrieved information for {len(provider_info.get('providers', {}))} icon providers"
                )
            return provider_info

        except Exception as e:
            error_msg = f"Error fetching icon provider information: {str(e)}"
            if ctx:
                await ctx.error(error_msg)
            return {"error": error_msg}

    @mcp.tool(
        annotations={
            "title": "Get Icon Catalog Stats",
            "readOnlyHint": True,
            "description": "Gets statistics about the icon catalog including total counts and provider breakdown",
        }
    )
    async def get_icon_stats_tool(ctx: Optional[Context] = None) -> Dict[str, Any]:
        """
        Gets comprehensive statistics about the icon catalog.

        This tool provides detailed statistics about the icon catalog,
        including total counts, provider breakdown, and category information.

        Returns:
            dict: Comprehensive icon catalog statistics
        """
        try:
            if ctx:
                await ctx.info("Generating icon catalog statistics")

            # Get fetcher instance
            fetcher = get_fetcher()

            # Get catalog statistics
            stats = await fetcher.get_icon_catalog_stats()

            if stats is None:
                error_msg = "Failed to generate icon catalog statistics. The service may be temporarily unavailable."
                if ctx:
                    await ctx.error(error_msg)
                return {"error": error_msg}

            if ctx:
                await ctx.info("Successfully generated icon catalog statistics")
            return stats

        except Exception as e:
            error_msg = f"Error generating icon catalog statistics: {str(e)}"
            if ctx:
                await ctx.error(error_msg)
            return {"error": error_msg}

    @mcp.tool(
        annotations={
            "title": "Check Icon Service Health",
            "readOnlyHint": True,
            "description": "Checks the health and connectivity of the icon catalog service",
        }
    )
    async def check_icons_health_tool(ctx: Optional[Context] = None) -> str:
        """
        Checks the health and connectivity of the icon catalog service.

        This tool performs connectivity tests specifically for the icon catalog endpoint
        and returns status information about icon fetching capabilities.

        Returns:
            str: Health status report with icon service connectivity and cache information
        """
        try:
            if ctx:
                await ctx.info("Performing icon service health check")

            fetcher = get_fetcher()

            # Get overall health info and extract icon-specific information
            health_info = await fetcher.health_check()

            # Extract icon service status
            icon_service = health_info["services"].get("icons", {})
            icon_status = icon_service.get("status", "unknown")

            # Format health report
            health_md = "# Icon Service Health Report\n\n"
            health_md += f"**Overall Status:** {icon_status.upper()}\n\n"

            # Icon endpoint status
            health_md += "## Icon Catalog Endpoint\n\n"
            status_emoji = "✅" if icon_status == "healthy" else "❌"
            health_md += f"{status_emoji} **Ilograph Icon List**: {icon_status.upper()}\n"
            health_md += f"   - URL: {icon_service.get('url', 'https://www.ilograph.com/docs/iconlist.txt')}\n"

            if "error" in icon_service:
                health_md += f"   - Error: {icon_service['error']}\n"

            # Cache information for icons
            cache_stats = health_info.get("cache_stats", {})
            cached_keys = cache_stats.get("keys", [])
            icons_cached = "icon_catalog" in cached_keys

            health_md += "\n## Icon Catalog Cache\n\n"
            health_md += f"- **Cached:** {'Yes' if icons_cached else 'No'}\n"
            health_md += (
                f"- **Total Cache Entries:** {cache_stats.get('total_entries', 'Unknown')}\n"
            )
            health_md += (
                f"- **Valid Cache Entries:** {cache_stats.get('valid_entries', 'Unknown')}\n"
            )

            # Icon catalog statistics if available
            if icons_cached and icon_status == "healthy":
                try:
                    stats = await fetcher.get_icon_catalog_stats()
                    if stats and "total_icons" in stats:
                        health_md += f"- **Total Icons Available:** {stats['total_icons']}\n"
                        health_md += (
                            f"- **Providers Available:** {len(stats.get('providers', {}))}\n"
                        )
                except Exception as e:
                    # Don't fail health check if stats aren't available
                    # Log at debug level to avoid cluttering health check output
                    if ctx:
                        await ctx.debug(f"Icon stats unavailable during health check: {str(e)}")

            health_md += "\n---\n\n"

            if icon_status == "healthy":
                health_md += (
                    "*Icon service is operational and ready to search the latest icon catalog.*"
                )
            else:
                health_md += "*Icon service is experiencing issues. Icon searching may be limited.*"

            if ctx:
                await ctx.info(f"Icon health check completed - Status: {icon_status}")
            return health_md

        except Exception as e:
            error_msg = f"Error performing icon health check: {str(e)}"
            if ctx:
                await ctx.error(error_msg)
            return f"Error: {error_msg}"


def get_tool_info() -> dict:
    """Get information about the icon tools for registration."""
    return {
        "name": "search_icons_tool",
        "description": "Searches the live Ilograph icon catalog with semantic matching and filtering",
        "tools": [
            "search_icons_tool",
            "list_icon_providers_tool",
            "get_icon_stats_tool",
            "check_icons_health_tool",
        ],
    }
