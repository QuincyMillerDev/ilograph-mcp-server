"""
Tools for the Ilograph MCP Server.

This package contains all MCP tools that provide functionality to AI agents,
including documentation fetching, diagram validation, example access, and more.
"""

from .register_example_tools import get_example_tool_info, register_example_tools
from .register_fetch_documentation_tools import get_tool_info, register_fetch_documentation_tool

__all__ = [
    "register_fetch_documentation_tool",
    "get_tool_info",
    "register_example_tools",
    "get_example_tool_info",
]
