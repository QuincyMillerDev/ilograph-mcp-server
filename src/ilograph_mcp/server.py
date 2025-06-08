"""
Main FastMCP server implementation for Ilograph.

This module sets up the FastMCP server and registers all tools, resources, and prompts.
"""

import logging
from fastmcp import FastMCP

from .resources import register_examples_resources

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
        
        ## Available Resources:
        
        ### Example Library (Static - Always Available)
        - ilograph://examples - Complete catalog of curated example diagrams with metadata
          Returns: Comprehensive catalog with filtering dimensions and learning progression
          
        - ilograph://examples/{filename} - Individual example content and metadata
          Examples: 'serverless-on-aws.ilograph', 'aws-distributed-load-testing.ilograph', 'stack-overflow-architecture-2016.ilograph'
          Returns: Full .ilograph content plus learning context and architectural patterns
          
        ## Example Categories Available:
        - Beginner: serverless-on-aws.ilograph (AWS serverless patterns)
        - Intermediate: aws-distributed-load-testing.ilograph (distributed systems)
        - Advanced: stack-overflow-architecture-2016.ilograph (datacenter architecture)
        
        ## Learning Progression:
        Start with serverless examples for basic patterns, progress to distributed testing
        for intermediate concepts, then datacenter architecture for advanced infrastructure.
        
        Each example includes:
        - Architecture patterns demonstrated
        - Services and technologies used
        - Learning objectives and complexity level
        - Component count and perspective information
        
        Use these resources to understand Ilograph syntax patterns and create accurate diagrams.
        """
    )
    
    # Register Phase 1 resources
    register_examples_resources(mcp)
    logger.info("Registered examples resources")
    
    # TODO: Register all tools when implemented in Phase 3
    # register_all_tools(mcp)
    
    # TODO: Register dynamic resources when implemented in Phase 2
    # register_specification_resources(mcp)
    # register_icon_resources(mcp)
    # register_documentation_resources(mcp)
    
    # TODO: Register prompts when implemented
    # register_diagram_prompts(mcp)
    
    logger.info("Ilograph MCP server initialized successfully")
    return mcp


if __name__ == "__main__":
    # Only create server when run directly
    mcp = create_server()
    mcp.run() 