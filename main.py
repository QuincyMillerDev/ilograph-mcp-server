#!/usr/bin/env python3
"""
Main entry point for the Ilograph MCP Server.

This script creates and runs the FastMCP server with all registered tools and resources.
"""

import sys
from pathlib import Path

# Add src to Python path for development
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from ilograph_mcp import create_server


def main():
    """Main entry point."""
    mcp = create_server()
    mcp.run()


if __name__ == "__main__":
    main() 