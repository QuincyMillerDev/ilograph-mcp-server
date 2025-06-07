"""
Ilograph MCP Server - A FastMCP server for Ilograph diagram creation and validation.

This package provides AI agents with comprehensive context and tools to create 
accurate, valid Ilograph diagrams. The server acts as a domain expert for 
Ilograph syntax, best practices, and validation.
"""

__version__ = "0.1.0"
__author__ = "Quincy Miller"

from .server import create_server

__all__ = ["create_server"] 