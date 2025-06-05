"""
Perspective management for Ilograph diagrams.
"""

from typing import Dict, List, Optional, Set
from ..analysis.base import AnalysisResult, EntityType

class PerspectiveManager:
    """Manages different perspectives for Ilograph diagrams."""
    
    def __init__(self):
        self.default_perspectives = {
            "Architecture": {
                "description": "High-level architectural view",
                "entity_types": {EntityType.CLASS, EntityType.MODULE, EntityType.PACKAGE, EntityType.SERVICE},
                "show_relationships": True
            },
            "Object-Oriented": {
                "description": "Object-oriented design view",
                "entity_types": {EntityType.CLASS, EntityType.INTERFACE, EntityType.METHOD},
                "show_relationships": True
            },
            "Functions": {
                "description": "Functional programming view",
                "entity_types": {EntityType.FUNCTION, EntityType.MODULE},
                "show_relationships": True
            },
            "Services": {
                "description": "Service-oriented architecture view",
                "entity_types": {EntityType.SERVICE, EntityType.API_ENDPOINT, EntityType.DATABASE},
                "show_relationships": True
            },
            "Data Flow": {
                "description": "Data flow and dependencies",
                "entity_types": {EntityType.DATABASE, EntityType.API_ENDPOINT, EntityType.SERVICE},
                "show_relationships": True
            }
        }
    
    def get_available_perspectives(self, analysis_result: AnalysisResult) -> List[str]:
        """
        Get list of available perspectives based on analysis results.
        
        Args:
            analysis_result: Analysis results to examine
            
        Returns:
            List of perspective names
        """
        # Collect perspectives from entities
        found_perspectives: Set[str] = set()
        for entity in analysis_result.entities:
            found_perspectives.update(entity.perspectives)
        
        # Add default perspectives if relevant entity types are found
        entity_types_in_result = {entity.type for entity in analysis_result.entities}
        
        for perspective_name, perspective_config in self.default_perspectives.items():
            required_types = perspective_config["entity_types"]
            if required_types.intersection(entity_types_in_result):
                found_perspectives.add(perspective_name)
        
        return sorted(list(found_perspectives))
    
    def filter_entities_for_perspective(
        self, 
        analysis_result: AnalysisResult, 
        perspective_name: str
    ) -> AnalysisResult:
        """
        Filter analysis results for a specific perspective.
        
        Args:
            analysis_result: Original analysis results
            perspective_name: Name of perspective to filter for
            
        Returns:
            Filtered analysis results
        """
        # TODO: Implement perspective-based filtering
        # For now, return the original results
        return analysis_result
    
    def customize_perspective(
        self,
        name: str,
        description: str,
        entity_types: Set[EntityType],
        show_relationships: bool = True
    ) -> None:
        """
        Add or customize a perspective.
        
        Args:
            name: Perspective name
            description: Perspective description
            entity_types: Set of entity types to include
            show_relationships: Whether to show relationships
        """
        self.default_perspectives[name] = {
            "description": description,
            "entity_types": entity_types,
            "show_relationships": show_relationships
        } 