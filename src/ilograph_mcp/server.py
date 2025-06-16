"""
Main FastMCP server implementation for Ilograph.

This module sets up the FastMCP server and registers all tools, resources, and prompts.
"""

import asyncio
import logging
import signal
import sys
from typing import Any, Optional

from fastmcp import FastMCP

from ilograph_mcp.tools.register_example_tools import register_example_tools
from ilograph_mcp.tools.register_fetch_documentation_tools import register_fetch_documentation_tool
from ilograph_mcp.tools.register_fetch_icons_tool import register_fetch_icons_tool
from ilograph_mcp.tools.register_fetch_spec_tool import register_fetch_spec_tool
from ilograph_mcp.tools.register_validate_diagram_tool import register_validate_diagram_tool

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global server instance for signal handling
_server_instance: Optional[FastMCP] = None


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
        - fetch_spec_tool: Fetches the official Ilograph specification with property definitions
        - check_spec_health: Checks specification service connectivity and cache status
        - list_examples: Lists available example diagrams
        - fetch_example: Fetches a specific example diagram by name
        - validate_diagram_tool: Validates Ilograph diagram syntax and provides detailed error messages
        - get_validation_help: Provides guidance on Ilograph diagram validation and common issues
        """,
    )

    try:
        # Register all tools with error handling
        register_fetch_documentation_tool(mcp)
        logger.info("Registered fetch_documentation_tool")

        register_fetch_spec_tool(mcp)
        logger.info("Registered fetch_spec_tool")

        register_example_tools(mcp)
        logger.info("Registered example_tools")

        register_validate_diagram_tool(mcp)
        logger.info("Registered validate_diagram_tool")

        register_fetch_icons_tool(mcp)
        logger.info("Registered fetch_icons_tool")

    except Exception as e:
        logger.error(f"Error registering tools: {e}")
        raise

    return mcp


def setup_signal_handlers() -> None:
    """Set up signal handlers for graceful shutdown."""

    def signal_handler(signum: int, frame: Any) -> None:
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        if _server_instance:
            # For FastMCP, we'll let the framework handle the shutdown
            logger.info("Server shutdown initiated")
        sys.exit(0)

    # Set up signal handlers for SIGINT and SIGTERM
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def main() -> None:
    """Main entry point for the Ilograph MCP server."""
    global _server_instance

    try:
        # Set up signal handlers
        setup_signal_handlers()

        # Create server instance
        _server_instance = create_server()
        logger.info("Server created successfully")

        # Run the server - FastMCP handles the async event loop
        _server_instance.run()

    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)
    finally:
        logger.info("Server shutdown complete")


if __name__ == "__main__":
    main()
