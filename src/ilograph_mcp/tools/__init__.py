"""
Tools for the Ilograph MCP Server.

This package contains all MCP tools that provide functionality to AI agents,
including documentation fetching, diagram validation, example access, and more.
"""

from .fetch_documentation_tool import register_fetch_documentation_tool, get_tool_info

__all__ = [
    "register_fetch_documentation_tool",
    "get_tool_info"
] 