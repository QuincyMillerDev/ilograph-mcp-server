"""
Content loader for Ilograph MCP Server.

This module handles loading and managing static content like templates, 
syntax references, icon catalogs, and best practices guides.
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional


class ContentLoader:
    """Loads and manages static content for the Ilograph MCP server."""
    
    def __init__(self, data_root: Optional[Path] = None):
        """
        Initialize the content loader.
        
        Args:
            data_root: Root directory for data files. Defaults to project data directory.
        """
        if data_root is None:
            # Default to project data directory
            self.data_root = Path(__file__).parent.parent.parent.parent / "data"
        else:
            self.data_root = data_root
    
    def load_icon_catalog(self) -> List[str]:
        """
        Load the complete icon catalog.
        
        Returns:
            List of available icon paths
        """
        icon_file = self.data_root / "iconlist.txt"
        
        if not icon_file.exists():
            return []
        
        try:
            with open(icon_file, 'r', encoding='utf-8') as f:
                icons = [line.strip() for line in f if line.strip()]
            return icons
        except Exception:
            return []
    
    def search_icons(self, query: str, category: Optional[str] = None) -> List[str]:
        """
        Search for icons matching a query.
        
        Args:
            query: Search term to match against icon names
            category: Optional category filter (e.g., 'AWS', 'Azure', 'GCP')
            
        Returns:
            List of matching icon paths
        """
        icons = self.load_icon_catalog()
        query_lower = query.lower()
        
        # Filter by category if specified
        if category:
            icons = [icon for icon in icons if icon.startswith(category)]
        
        # Search for query in icon path
        matching_icons = [
            icon for icon in icons 
            if query_lower in icon.lower()
        ]
        
        return matching_icons[:20]  # Limit results
    
    def get_icon_categories(self) -> List[str]:
        """
        Get all available icon categories.
        
        Returns:
            List of icon categories
        """
        icons = self.load_icon_catalog()
        categories = set()
        
        for icon in icons:
            if '/' in icon:
                category = icon.split('/')[0]
                categories.add(category)
        
        return sorted(list(categories))
    
    def load_syntax_reference(self) -> str:
        """
        Load Ilograph syntax reference documentation.
        
        Returns:
            Syntax reference content as markdown
        """
        # For now, return embedded content. In the future, this could load from files.
        return """
# Ilograph Syntax Reference

## Top-level Properties

- `resources`: Array of resource definitions
- `perspectives`: Array of perspective definitions  
- `imports`: Array of import definitions
- `contexts`: Array of context definitions
- `description`: Diagram description (supports markdown)
- `defaultContextDisplayName`: Default context display name

## Resource Properties

- `name` (required): Resource name/identifier
- `subtitle`: Subtitle text
- `description`: Description (supports markdown)
- `color`: Text color (X11 color name or hex)
- `backgroundColor`: Background color
- `style`: Border style (default, plural, dashed, outline, flat)
- `icon`: Icon path
- `iconStyle`: Icon rendering (default, silhouette)
- `children`: Array of child resources
- `id`: Alternative identifier
- `url`: External URL

## Perspective Properties

- `name` (required): Perspective name
- `relations`: Array of relation definitions
- `sequence`: Sequence definition for sequence perspectives
- `orientation`: Layout direction (leftToRight, topToBottom, ring)
- `arrowDirection`: Default arrow direction (forward, backward, bidirectional)
"""
    
    def load_best_practices(self) -> str:
        """
        Load best practices guide.
        
        Returns:
            Best practices content as markdown
        """
        return """
# Ilograph Best Practices

## Resource Naming
- Use clear, descriptive names
- Avoid special characters (/, ^, *, [, ], ,) in names
- Use consistent naming conventions

## Visual Design
- Use colors to group related resources
- Choose appropriate icons for resource types
- Keep consistent visual styling

## Perspective Organization
- Create multiple perspectives for different views
- Use sequence perspectives for process flows
- Use relation perspectives for architecture views

## Structure
- Organize resources hierarchically when appropriate
- Use contexts to group related resources
- Keep perspectives focused and clear
""" 