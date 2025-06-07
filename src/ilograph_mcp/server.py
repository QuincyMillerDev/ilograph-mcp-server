"""
Main FastMCP server implementation for Ilograph.

This module sets up the FastMCP server and registers all tools, resources, and prompts.
"""

from fastmcp import FastMCP


def create_server() -> FastMCP:
    """
    Create and configure the Ilograph MCP server.
    
    Returns:
        FastMCP: Configured server instance
    """
    # Create server with metadata
    mcp = FastMCP(
        name="Ilograph Context Server",
        instructions="""
        This server provides comprehensive Ilograph diagram creation and validation tools.
        Use the tools to validate syntax, search for icons, and get recommendations.
        Use the resources to access documentation, examples, and specifications.
        """
    )
    
    # TODO: Register all tools when implemented
    # register_all_tools(mcp)
    
    # TODO: Register all resources when implemented
    # register_all_resources(mcp)
    
    # TODO: Register prompts when implemented
    # register_diagram_prompts(mcp)
    
    return mcp


if __name__ == "__main__":
    # Only create server when run directly
    mcp = create_server()
    mcp.run() 