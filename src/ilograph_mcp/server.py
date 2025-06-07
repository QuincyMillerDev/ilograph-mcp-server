"""
Main FastMCP server implementation for Ilograph.

This module sets up the FastMCP server and registers all tools, resources, and prompts.
"""

from fastmcp import FastMCP
from .tools.validation import register_validation_tools


def create_server() -> FastMCP:
    """
    Create and configure the Ilograph MCP server.
    
    Returns:
        FastMCP: Configured server instance
    """
    mcp = FastMCP("Ilograph Context Server")
    
    # Register all tools
    register_validation_tools(mcp)
    
    # TODO: Register resources when implemented
    # register_syntax_resources(mcp)
    # register_template_resources(mcp)
    # register_icon_resources(mcp)
    
    # TODO: Register prompts when implemented
    # register_diagram_prompts(mcp)
    
    return mcp


# Create the global server instance
mcp = create_server()


if __name__ == "__main__":
    mcp.run() 