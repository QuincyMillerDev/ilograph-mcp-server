"""
Main FastMCP server implementation for Ilograph.

This module sets up the FastMCP server and registers all tools, resources, and prompts.
"""

from fastmcp import FastMCP
from .tools import register_all_tools
from .resources import register_all_resources


def create_server() -> FastMCP:
    """
    Create and configure the Ilograph MCP server.
    
    Returns:
        FastMCP: Configured server instance
    """
    mcp = FastMCP("Ilograph Context Server")
    
    # Register all tools
    register_all_tools(mcp)
    
    # Register all resources  
    register_all_resources(mcp)
    
    # TODO: Register prompts when implemented
    # register_diagram_prompts(mcp)
    
    return mcp


if __name__ == "__main__":
    # Only create server when run directly
    mcp = create_server()
    mcp.run() 