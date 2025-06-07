"""
Validation tools for Ilograph syntax and diagrams.

This module provides tools for validating Ilograph markup syntax and returning 
detailed feedback on errors, warnings, and suggestions.
"""

import yaml
from typing import Dict, List, Any
from fastmcp import FastMCP

from ..data.validator import IlographValidator


def register_validation_tools(mcp: FastMCP) -> None:
    """Register all validation tools with the MCP server."""
    
    @mcp.tool()
    async def validate_ilograph_syntax(diagram_code: str) -> Dict[str, Any]:
        """
        Validate Ilograph markup syntax and return detailed feedback.
        
        This tool parses Ilograph YAML markup and validates it against the official
        Ilograph specification. It checks for syntax errors, required fields, 
        valid property values, and provides suggestions for improvements.
        
        Args:
            diagram_code: The Ilograph YAML/markup code to validate
            
        Returns:
            Dictionary with validation results:
            - valid (bool): Whether the diagram is syntactically valid
            - errors (list): List of error messages for invalid syntax
            - warnings (list): List of warning messages for potential issues  
            - suggestions (list): List of suggestions for improvements
        """
        validator = IlographValidator()
        return await validator.validate(diagram_code) 