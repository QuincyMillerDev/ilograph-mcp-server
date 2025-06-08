"""
Main FastMCP server implementation for Ilograph.

This module sets up the FastMCP server and registers all tools, resources, and prompts.
"""

import logging

from fastmcp import FastMCP

from ilograph_mcp.tools.register_example_tools import register_example_tools
from ilograph_mcp.tools.register_fetch_documentation_tools import register_fetch_documentation_tool

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_server() -> FastMCP:
    """
    Create and configure the Ilograph MCP server.

    Returns:
        FastMCP: Configured server instance
    """
    # Create server with comprehensive metadata and instructions
    mcp: FastMCP = FastMCP(
        name="Ilograph Context Server",
        instructions="""
        This server provides comprehensive Ilograph diagram creation and validation tools.
        It acts as a dynamic domain expert for Ilograph syntax, best practices, and validation.
        It can also provide documentation about Ilograph concepts, such as perspectives, resources, and contexts.

        Available tools:
        - fetch_documentation_tool: Fetches comprehensive documentation from Ilograph's official docs
        - list_documentation_sections: Lists all available documentation sections
        - check_documentation_health: Checks service connectivity and cache status
        - list_examples: Lists available example diagrams
        - fetch_example: Fetches a specific example diagram by name
        """,
    )

    # Register all tools
    register_fetch_documentation_tool(mcp)
    logger.info("Registered fetch_documentation_tool")

    register_example_tools(mcp)
    logger.info("Registered example_tools")

    return mcp


def main() -> None:
    """Main entry point for the Ilograph MCP server."""
    mcp = create_server()
    mcp.run()


if __name__ == "__main__":
    main()
