"""
Main FastMCP server implementation for Ilograph.

This module sets up the FastMCP server and registers all tools, resources, and prompts.
"""

import logging
from fastmcp import FastMCP

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_server() -> FastMCP:
    """
    Create and configure the Ilograph MCP server.
    
    Returns:
        FastMCP: Configured server instance
    """
    # Create server with comprehensive metadata and instructions
    mcp = FastMCP(
        name="Ilograph Context Server",
        instructions="""
        This server provides comprehensive Ilograph diagram creation and validation tools.
        It acts as a dynamic domain expert for Ilograph syntax, best practices, and validation.
        It can also provide documentation about Ilograph concepts, such as perspectives, resources, and contexts.
        """
    )
    
    # TODO: Register all tools when implemented
    # register_all_tools(mcp)

    return mcp


if __name__ == "__main__":
    # Only create server when run directly
    mcp = create_server()
    mcp.run() 