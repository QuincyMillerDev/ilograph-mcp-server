"""
Resources for the Ilograph MCP Server.

This package contains all the MCP resources (@mcp.resource() decorated functions)
for exposing specifications, documentation, icons, and examples.
"""

# Resources will be imported here when implemented
# from .specification import get_specification
# from .icons import get_icon_catalog
# from .documentation import get_documentation
from .examples import register_examples_resources

__all__ = [
    # "get_specification",
    # "get_icon_catalog",
    # "get_documentation",
    "register_examples_resources",
] 