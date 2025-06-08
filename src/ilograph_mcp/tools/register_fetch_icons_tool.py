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


def get_tool_info() -> dict:
    """Get information about the icon tools for registration."""
    return {
        "name": "search_icons_tool",
        "description": "Searches the live Ilograph icon catalog with semantic matching and filtering",
        "tools": [
            "search_icons_tool",
            "list_icon_providers_tool",
        ],
    }
