"""
Fetch Specification Tool for Ilograph MCP Server.

This tool provides access to the official Ilograph specification from ilograph.com/docs/spec/,
converting HTML content to clean markdown format optimized for LLM consumption.
Includes caching, error handling, and detailed logging following FastMCP patterns.
"""

import logging

from fastmcp import Context, FastMCP

from ..core.fetcher import get_fetcher

logger = logging.getLogger(__name__)


def register_fetch_spec_tool(mcp: FastMCP) -> None:
    """Register the fetch specification tool with the FastMCP server."""

    @mcp.tool(
        annotations={
            "title": "Fetch Ilograph Specification",
            "readOnlyHint": True,
            "description": "Fetches the concise Ilograph specification with property definitions and types",
        }
    )
    async def fetch_spec_tool(ctx: Context) -> str:
        """
        Fetches the official Ilograph specification from https://www.ilograph.com/docs/spec/

        This tool provides the authoritative reference for all Ilograph properties, types,
        and requirements in a structured table format - perfect for validation and quick lookups.

        Returns:
            str: Complete specification in markdown format with:
                 - Top-level properties table
                 - Resource properties and types
                 - Perspective properties and types
                 - Relation, Sequence, Step definitions
                 - Context, Layout, Import specifications
                 - All property types and requirements
        """
        try:
            # Log the request
            await ctx.info("Fetching Ilograph specification from official source")

            # Get fetcher instance
            fetcher = get_fetcher()

            # Fetch specification content
            content = await fetcher.fetch_specification()

            if content is None:
                error_msg = "Failed to fetch Ilograph specification. The content may be temporarily unavailable."
                await ctx.error(error_msg)
                return f"Error: {error_msg}"

            # Add metadata header to the content
            content_with_header = f"""# Ilograph Specification

**Source:** https://www.ilograph.com/docs/spec/  
**Description:** Official Ilograph YAML format specification with complete property definitions  
**Last Updated:** Fetched on demand from official Ilograph documentation  

This specification provides the authoritative reference for all Ilograph diagram properties, 
types, and requirements. Use this for validation, quick property lookups, and understanding 
the complete Ilograph schema.

---

{content}

---

*This specification was fetched from the official Ilograph website and converted to markdown format for easy consumption. For the most up-to-date information, visit https://www.ilograph.com/docs/spec/*
"""

            await ctx.info(
                f"Successfully fetched Ilograph specification ({len(content)} characters)"
            )
            return content_with_header

        except Exception as e:
            error_msg = f"Unexpected error fetching Ilograph specification: {str(e)}"
            await ctx.error(error_msg)
            return f"Error: An unexpected error occurred while fetching the specification. Please try again later."

    @mcp.tool(
        annotations={
            "title": "Check Specification Service Health",
            "readOnlyHint": True,
            "description": "Checks the health and connectivity of the specification fetching service",
        }
    )
    async def check_spec_health(ctx: Context) -> str:
        """
        Checks the health and connectivity of the specification fetching service.

        This tool performs connectivity tests specifically for the specification endpoint
        and returns status information about spec fetching capabilities.

        Returns:
            str: Health status report with spec service connectivity and cache information
        """
        try:
            await ctx.info("Performing specification service health check")

            fetcher = get_fetcher()

            # Get overall health info and extract spec-specific information
            health_info = await fetcher.health_check()

            # Extract specification service status
            spec_service = health_info["services"].get("specification", {})
            spec_status = spec_service.get("status", "unknown")

            # Format health report
            health_md = "# Specification Service Health Report\n\n"
            health_md += f"**Overall Status:** {spec_status.upper()}\n\n"

            # Specification endpoint status
            health_md += "## Specification Endpoint\n\n"
            status_emoji = "✅" if spec_status == "healthy" else "❌"
            health_md += f"{status_emoji} **Ilograph Spec Endpoint**: {spec_status.upper()}\n"
            health_md += (
                f"   - URL: {spec_service.get('url', 'https://www.ilograph.com/docs/spec/')}\n"
            )

            if "error" in spec_service:
                health_md += f"   - Error: {spec_service['error']}\n"

            # Cache information for spec
            cache_stats = health_info.get("cache_stats", {})
            cached_keys = cache_stats.get("keys", [])
            spec_cached = "specification" in cached_keys

            health_md += "\n## Specification Cache\n\n"
            health_md += f"- **Cached:** {'Yes' if spec_cached else 'No'}\n"
            health_md += (
                f"- **Total Cache Entries:** {cache_stats.get('total_entries', 'Unknown')}\n"
            )
            health_md += (
                f"- **Valid Cache Entries:** {cache_stats.get('valid_entries', 'Unknown')}\n"
            )

            health_md += "\n---\n\n"

            if spec_status == "healthy":
                health_md += (
                    "*Specification service is operational and ready to fetch the latest spec.*"
                )
            else:
                health_md += (
                    "*Specification service is experiencing issues. Spec fetching may be limited.*"
                )

            await ctx.info(f"Spec health check completed - Status: {spec_status}")
            return health_md

        except Exception as e:
            error_msg = f"Error performing spec health check: {str(e)}"
            await ctx.error(error_msg)
            return f"Error: {error_msg}"


def get_tool_info() -> dict:
    """Get information about the specification tools for registration."""
    return {
        "name": "fetch_spec_tool",
        "description": "Fetches the official Ilograph specification with structured property definitions",
        "tools": [
            "fetch_spec_tool",
            "check_spec_health",
        ],
    }
