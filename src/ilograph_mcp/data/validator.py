"""
Ilograph syntax validator implementation.

This module contains the core validation logic for Ilograph markup syntax.
"""

import yaml
from typing import Dict, List, Any


class IlographValidator:
    """Validates Ilograph markup syntax according to the official specification."""
    
    def __init__(self):
        """Initialize the validator with specification data."""
        # Valid values from Ilograph spec
        self.valid_resource_styles = ['default', 'plural', 'dashed', 'outline', 'flat']
        self.valid_icon_styles = ['default', 'silhouette']
        self.valid_orientations = ['leftToRight', 'topToBottom', 'ring']
        self.valid_arrow_directions = ['forward', 'backward', 'bidirectional']
        self.valid_additional_contexts = ['all', 'none', 'super-only', 'sub-only']
        self.valid_top_level_props = [
            'resources', 'perspectives', 'imports', 'contexts', 
            'description', 'defaultContextDisplayName'
        ]
        self.restricted_chars = ['/', '^', '*', '[', ']', ',']
        self.step_fields = ['to', 'toAndBack', 'toAsync', 'restartAt']
    
    async def validate(self, diagram_code: str) -> Dict[str, Any]:
        """
        Validate Ilograph markup syntax and return detailed feedback.
        
        Args:
            diagram_code: The Ilograph YAML/markup code to validate
            
        Returns:
            Dictionary with validation results
        """
        result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "suggestions": []
        }
        
        try:
            # Parse YAML
            try:
                data = yaml.safe_load(diagram_code)
            except yaml.YAMLError as e:
                result["valid"] = False
                result["errors"].append(f"YAML parsing error: {str(e)}")
                return result
            
            if not isinstance(data, dict):
                result["valid"] = False
                result["errors"].append("Ilograph markup must be a YAML object/dictionary")
                return result
            
            # Validate top-level structure
            self._validate_top_level(data, result)
            
            # Validate resources
            if 'resources' in data:
                self._validate_resources(data['resources'], result)
            
            # Validate perspectives
            if 'perspectives' in data:
                self._validate_perspectives(data['perspectives'], result)
            
            # Set valid flag based on errors
            if result["errors"]:
                result["valid"] = False
            
            # Add general suggestions if no specific issues found
            self._add_general_suggestions(data, result)
            
        except Exception as e:
            result["valid"] = False
            result["errors"].append(f"Validation error: {str(e)}")
        
        return result
    
    def _validate_top_level(self, data: Dict[str, Any], result: Dict[str, List[str]]) -> None:
        """Validate top-level properties."""
        for key in data.keys():
            if key not in self.valid_top_level_props:
                result["warnings"].append(
                    f"Unknown top-level property: '{key}'. "
                    f"Valid properties are: {self.valid_top_level_props}"
                )
    
    def _validate_resources(self, resources: Any, result: Dict[str, List[str]]) -> None:
        """Validate resources array."""
        if not isinstance(resources, list):
            result["errors"].append("'resources' must be an array")
            return
        
        for i, resource in enumerate(resources):
            if not isinstance(resource, dict):
                result["errors"].append(f"Resource {i}: must be an object")
                continue
            
            self._validate_resource(resource, i, result)
    
    def _validate_resource(self, resource: Dict[str, Any], index: int, result: Dict[str, List[str]]) -> None:
        """Validate a single resource."""
        # Required field validation
        if 'name' not in resource:
            result["errors"].append(f"Resource {index}: 'name' is required")
        else:
            name = resource['name']
            # Check for restricted characters in name
            if any(char in name for char in self.restricted_chars):
                if 'id' not in resource:
                    result["errors"].append(
                        f"Resource '{name}': When name contains restricted characters "
                        f"({', '.join(self.restricted_chars)}), 'id' must be defined"
                    )
        
        # Validate color if present
        if 'color' in resource:
            color = resource['color']
            # Basic color validation (hex or X11 color names)
            if not (color.startswith('#') or color.isalpha()):
                result["warnings"].append(
                    f"Resource '{resource.get('name', index)}': "
                    f"Color '{color}' may not be valid"
                )
        
        # Validate style if present
        if 'style' in resource:
            if resource['style'] not in self.valid_resource_styles:
                result["errors"].append(
                    f"Resource '{resource.get('name', index)}': "
                    f"Style must be one of {self.valid_resource_styles}"
                )
        
        # Validate iconStyle if present
        if 'iconStyle' in resource:
            if resource['iconStyle'] not in self.valid_icon_styles:
                result["errors"].append(
                    f"Resource '{resource.get('name', index)}': "
                    f"iconStyle must be one of {self.valid_icon_styles}"
                )
        
        # Validate ID if present
        if 'id' in resource:
            resource_id = resource['id']
            if any(char in resource_id for char in self.restricted_chars):
                result["errors"].append(
                    f"Resource '{resource.get('name', index)}': "
                    f"ID cannot contain restricted characters ({', '.join(self.restricted_chars)})"
                )
        
        # Add suggestions
        if 'icon' not in resource and 'color' not in resource:
            result["suggestions"].append(
                f"Resource '{resource.get('name', index)}': "
                f"Consider adding an icon or color for better visual distinction"
            )
    
    def _validate_perspectives(self, perspectives: Any, result: Dict[str, List[str]]) -> None:
        """Validate perspectives array."""
        if not isinstance(perspectives, list):
            result["errors"].append("'perspectives' must be an array")
            return
        
        for i, perspective in enumerate(perspectives):
            if not isinstance(perspective, dict):
                result["errors"].append(f"Perspective {i}: must be an object")
                continue
            
            self._validate_perspective(perspective, i, result)
    
    def _validate_perspective(self, perspective: Dict[str, Any], index: int, result: Dict[str, List[str]]) -> None:
        """Validate a single perspective."""
        # Required field validation
        if 'name' not in perspective:
            result["errors"].append(f"Perspective {index}: 'name' is required")
        
        # Validate orientation if present
        if 'orientation' in perspective:
            if perspective['orientation'] not in self.valid_orientations:
                result["errors"].append(
                    f"Perspective '{perspective.get('name', index)}': "
                    f"orientation must be one of {self.valid_orientations}"
                )
        
        # Validate arrowDirection if present
        if 'arrowDirection' in perspective:
            if perspective['arrowDirection'] not in self.valid_arrow_directions:
                result["errors"].append(
                    f"Perspective '{perspective.get('name', index)}': "
                    f"arrowDirection must be one of {self.valid_arrow_directions}"
                )
        
        # Validate additionalContext if present
        if 'additionalContext' in perspective:
            if perspective['additionalContext'] not in self.valid_additional_contexts:
                result["errors"].append(
                    f"Perspective '{perspective.get('name', index)}': "
                    f"additionalContext must be one of {self.valid_additional_contexts}"
                )
        
        # Validate relations
        if 'relations' in perspective:
            self._validate_relations(perspective['relations'], perspective.get('name', index), result)
        
        # Validate sequence
        if 'sequence' in perspective:
            self._validate_sequence(perspective['sequence'], perspective.get('name', index), result)
    
    def _validate_relations(self, relations: List[Dict[str, Any]], perspective_name: str, result: Dict[str, List[str]]) -> None:
        """Validate relations in a perspective."""
        for i, relation in enumerate(relations):
            if 'from' not in relation and 'to' not in relation:
                result["errors"].append(
                    f"Perspective '{perspective_name}', Relation {i}: "
                    f"Either 'from' or 'to' must be defined"
                )
            
            if 'arrowDirection' in relation:
                if relation['arrowDirection'] not in self.valid_arrow_directions:
                    result["errors"].append(
                        f"Perspective '{perspective_name}', Relation {i}: "
                        f"arrowDirection must be one of {self.valid_arrow_directions}"
                    )
    
    def _validate_sequence(self, sequence: Dict[str, Any], perspective_name: str, result: Dict[str, List[str]]) -> None:
        """Validate sequence in a perspective."""
        if 'start' not in sequence:
            result["errors"].append(
                f"Perspective '{perspective_name}': sequence requires 'start' property"
            )
        
        if 'steps' in sequence:
            for i, step in enumerate(sequence['steps']):
                if not any(field in step for field in self.step_fields):
                    result["errors"].append(
                        f"Perspective '{perspective_name}', Step {i}: "
                        f"Must define one of {self.step_fields}"
                    )
    
    def _add_general_suggestions(self, data: Dict[str, Any], result: Dict[str, List[str]]) -> None:
        """Add general suggestions if no specific issues found."""
        if result["valid"] and not result["warnings"] and not result["suggestions"]:
            if 'resources' not in data and 'perspectives' not in data:
                result["suggestions"].append(
                    "Consider adding resources and perspectives to create a meaningful diagram"
                )
            elif 'resources' in data and 'perspectives' not in data:
                result["suggestions"].append(
                    "Consider adding perspectives to show relationships between resources"
                )
            elif 'perspectives' in data and 'resources' not in data:
                result["suggestions"].append(
                    "Consider adding resources to populate your perspectives"
                ) 