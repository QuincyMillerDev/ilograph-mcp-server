"""
Fetch Documentation Tool for Ilograph MCP Server.

This tool provides access to comprehensive Ilograph documentation sections,
converting HTML content to clean markdown format optimized for LLM consumption.
Includes caching, error handling, and detailed logging following FastMCP patterns.
"""

import logging
from fastmcp import FastMCP, Context

from ..core.fetcher import get_fetcher

logger = logging.getLogger(__name__)


def register_fetch_documentation_tool(mcp: FastMCP) -> None:
    """Register the fetch documentation tool with the FastMCP server."""

    @mcp.tool(
        annotations={
            "title": "Fetch Ilograph Documentation",
            "readOnlyHint": True,
            "description": "Fetches narrative documentation from ilograph.com with explanations and examples",
        }
    )
    async def fetch_documentation_tool(section: str, ctx: Context) -> str:
        """
        Fetches and formats narrative documentation from Ilograph website.

        This tool provides detailed explanations, tutorials, and examples for learning
        Ilograph concepts and implementation patterns. Content is fetched from the official
        Ilograph documentation site and converted to clean markdown format.

        Args:
            section: Documentation section to fetch. Supported sections:
                    - 'resources' -> Resource tree organization, hierarchies, instanceOf patterns
                    - 'relation-perspectives' -> Arrow connections, from/to properties, routing, labels
                    - 'sequence-perspectives' -> Time-based diagrams with steps, bidirectional flows
                    - 'references' -> Resource reference patterns and advanced referencing
                    - 'advanced-references' -> Complex reference scenarios and usage patterns
                    - 'resource-sizes-and-positions' -> Layout control, resource sizing, visual hierarchy
                    - 'parent-overrides' -> Resource parent overrides in perspectives with scale properties
                    - 'perspectives-other-properties' -> Additional perspective properties and options
                    - 'icons' -> Icon system with iconStyle, icon paths, and categorization
                    - 'walkthroughs' -> Interactive step-by-step guides through diagrams
                    - 'contexts' -> Multiple context views with roots, extends inheritance
                    - 'imports' -> Namespace management with from/namespace properties, component reuse
                    - 'markdown' -> Rich text support in descriptions, notes, and diagram text
                    - 'tutorial' -> Complete tutorial for learning Ilograph diagram creation

        Returns:
            str: Clean markdown content with detailed explanations, examples, and best practices
        """
        # Validate and normalize section parameter
        if not section or not isinstance(section, str):
            error_msg = "Section parameter is required and must be a non-empty string"
            await ctx.error(error_msg)
            return f"Error: {error_msg}"

        section = section.strip().lower()

        # Get fetcher instance
        fetcher = get_fetcher()
        supported_sections = fetcher.get_supported_documentation_sections()

        # Validate section name
        if section not in supported_sections:
            available_sections = ", ".join(sorted(supported_sections.keys()))
            error_msg = f"Unsupported section '{section}'. Available sections: {available_sections}"
            await ctx.error(error_msg)
            return f"Error: {error_msg}"

        try:
            # Log the request
            await ctx.info(f"Fetching Ilograph documentation for section: {section}")

            # Fetch documentation content
            content = await fetcher.fetch_documentation_section(section)

            if content is None:
                error_msg = f"Failed to fetch documentation for section '{section}'. The content may be temporarily unavailable."
                await ctx.error(error_msg)
                return f"Error: {error_msg}"

            # Add metadata header to the content
            section_description = supported_sections[section]
            content_with_header = f"""# Ilograph Documentation: {section.replace('-', ' ').title()}

**Section:** {section}  
**Description:** {section_description}  
**Source:** https://www.ilograph.com/docs/editing/{section.replace('-', '/')}/  
**Last Updated:** Fetched on demand from official Ilograph documentation

---

{content}

---

*This documentation was fetched from the official Ilograph website and converted to markdown format for easy consumption. For the most up-to-date information, visit the official documentation at https://www.ilograph.com/docs/*
"""

            await ctx.info(
                f"Successfully fetched documentation for section '{section}' ({len(content)} characters)"
            )
            return content_with_header

        except Exception as e:
            error_msg = f"Unexpected error fetching documentation for section '{section}': {str(e)}"
            await ctx.error(error_msg)
            return f"Error: An unexpected error occurred while fetching the documentation. Please try again later."

    @mcp.tool(
        annotations={
            "title": "List Available Documentation Sections",
            "readOnlyHint": True,
            "description": "Lists all available Ilograph documentation sections with descriptions",
        }
    )
    async def list_documentation_sections(ctx: Context) -> str:
        """
        Lists all available Ilograph documentation sections with descriptions.

        This tool provides an overview of all available documentation sections
        that can be fetched using the fetch_documentation_tool.

        Returns:
            str: Formatted list of available documentation sections with descriptions
        """
        try:
            await ctx.info("Listing available Ilograph documentation sections")

            fetcher = get_fetcher()
            supported_sections = fetcher.get_supported_documentation_sections()

            # Format the sections list
            sections_md = "# Available Ilograph Documentation Sections\n\n"
            sections_md += "The following documentation sections are available for fetching:\n\n"

            for section, description in sorted(supported_sections.items()):
                url = f"https://www.ilograph.com/docs/editing/{section.replace('-', '/')}/"
                sections_md += f"## {section}\n"
                sections_md += f"**Description:** {description}  \n"
                sections_md += f"**URL:** {url}  \n"
                sections_md += f"**Usage:** Use `fetch_documentation_tool(section='{section}')` to fetch this content\n\n"

            sections_md += "---\n\n"
            sections_md += "*To fetch any of these sections, use the `fetch_documentation_tool` with the section name as the parameter.*"

            await ctx.info(f"Listed {len(supported_sections)} available documentation sections")
            return sections_md

        except Exception as e:
            error_msg = f"Error listing documentation sections: {str(e)}"
            await ctx.error(error_msg)
            return f"Error: {error_msg}"

    @mcp.tool(
        annotations={
            "title": "Check Documentation Service Health",
            "readOnlyHint": True,
            "description": "Checks the health and connectivity of the documentation fetching service",
        }
    )
    async def check_documentation_health(ctx: Context) -> str:
        """
        Checks the health and connectivity of the documentation fetching service.

        This tool performs connectivity tests and returns status information about
        the documentation fetching capabilities, including cache statistics.

        Returns:
            str: Health status report with service connectivity and cache information
        """
        try:
            await ctx.info("Performing documentation service health check")

            fetcher = get_fetcher()
            health_info = await fetcher.health_check()

            # Format health report
            health_md = "# Documentation Service Health Report\n\n"
            health_md += f"**Overall Status:** {health_info['status'].upper()}\n\n"

            # Service status
            health_md += "## Service Connectivity\n\n"
            for service, info in health_info["services"].items():
                status_emoji = "✅" if info["status"] == "healthy" else "❌"
                health_md += f"{status_emoji} **{service.title()}**: {info['status'].upper()}\n"
                health_md += f"   - URL: {info['url']}\n"
                if "error" in info:
                    health_md += f"   - Error: {info['error']}\n"
                health_md += "\n"

            # Cache statistics
            cache_stats = health_info["cache_stats"]
            health_md += "## Cache Statistics\n\n"
            health_md += f"- **Total Entries:** {cache_stats['total_entries']}\n"
            health_md += f"- **Valid Entries:** {cache_stats['valid_entries']}\n"
            health_md += f"- **Expired Entries:** {cache_stats['expired_entries']}\n"

            if cache_stats["keys"]:
                health_md += f"- **Cached Keys:** {', '.join(cache_stats['keys'])}\n"

            health_md += "\n---\n\n"

            if health_info["status"] == "healthy":
                health_md += "*All services are operational and ready to fetch documentation.*"
            elif health_info["status"] == "degraded":
                unhealthy = health_info.get("unhealthy_services", [])
                health_md += f"*Some services are experiencing issues: {', '.join(unhealthy)}. Documentation fetching may be limited.*"

            await ctx.info(f"Health check completed - Status: {health_info['status']}")
            return health_md

        except Exception as e:
            error_msg = f"Error performing health check: {str(e)}"
            await ctx.error(error_msg)
            return f"Error: {error_msg}"


def get_tool_info() -> dict:
    """Get information about the documentation tools for registration."""
    return {
        "name": "fetch_documentation_tool",
        "description": "Fetches comprehensive Ilograph documentation with markdown formatting",
        "tools": [
            "fetch_documentation_tool",
            "list_documentation_sections",
            "check_documentation_health",
        ],
    }
