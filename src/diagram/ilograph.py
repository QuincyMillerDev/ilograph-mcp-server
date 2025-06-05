"""
Ilograph diagram generation and schema management.
"""

import yaml
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Set, Union
from pydantic import BaseModel, Field

from ..analysis.base import AnalysisResult, Entity, Relationship, EntityType, RelationshipType

@dataclass
class IlographResource:
    """Ilograph resource representation matching .ilograph format."""
    name: str
    id: Optional[str] = None
    subtitle: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    children: Optional[List[str]] = None

@dataclass 
class IlographRelation:
    """Ilograph relation representation matching .ilograph format."""
    from_: Union[str, List[str]]
    to_: Union[str, List[str]]
    label: Optional[str] = None
    color: Optional[str] = None

@dataclass
class IlographPerspective:
    """Ilograph perspective representation."""
    name: str
    relations: List[IlographRelation]

@dataclass
class IlographDiagram:
    """Complete Ilograph diagram matching .ilograph format."""
    resources: List[IlographResource]
    perspectives: List[IlographPerspective]
    
    def to_yaml(self) -> str:
        """Convert to YAML string matching .ilograph format."""
        # Convert to dictionary format expected by Ilograph
        diagram_dict = {
            "resources": {}
        }
        
        # Add resources
        for resource in self.resources:
            resource_name = resource.name
            resource_data = {}
            
            if resource.subtitle:
                resource_data["subtitle"] = resource.subtitle
            if resource.color:
                resource_data["color"] = resource.color
            if resource.icon:
                resource_data["icon"] = resource.icon
            if resource.children:
                resource_data["children"] = resource.children
                
            # Only add resource data if it has properties
            if resource_data:
                diagram_dict["resources"][resource_name] = resource_data
            else:
                # Empty resource (just name)
                diagram_dict["resources"][resource_name] = None
        
        # Add perspectives
        perspectives_dict = {}
        for perspective in self.perspectives:
            relations = []
            for relation in perspective.relations:
                relation_data = {
                    "from": relation.from_,
                    "to": relation.to_
                }
                if relation.label:
                    relation_data["label"] = relation.label
                if relation.color:
                    relation_data["color"] = relation.color
                relations.append(relation_data)
            
            perspectives_dict[perspective.name] = {
                "relations": relations
            }
        
        diagram_dict["perspectives"] = perspectives_dict
        
        return yaml.dump(diagram_dict, default_flow_style=False, sort_keys=False)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API usage."""
        return {
            "resources": [asdict(r) for r in self.resources],
            "perspectives": [asdict(p) for p in self.perspectives]
        }

class IlographGenerator:
    """Generates Ilograph diagrams from analysis results."""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self._entity_type_mapping = {
            EntityType.CLASS: {"color": "Green", "icon": "AWS/Compute/EC2/Instance"},
            EntityType.INTERFACE: {"color": "Blue", "icon": "AWS/Compute/EC2/Instance"},
            EntityType.FUNCTION: {"color": "Orange", "icon": "AWS/Compute/Lambda/Lambda Function"},
            EntityType.METHOD: {"color": "Yellow", "icon": "AWS/Compute/Lambda/Lambda Function"},
            EntityType.MODULE: {"color": "Purple", "icon": "AWS/General/General/Documents"},
            EntityType.PACKAGE: {"color": "Indigo", "icon": "AWS/General/General/Documents"},
            EntityType.SERVICE: {"color": "Red", "icon": "AWS/Compute/EC2/Instance"},
            EntityType.DATABASE: {"color": "Brown", "icon": "AWS/Database/RDS/RDS Instance"},
            EntityType.API_ENDPOINT: {"color": "Teal", "icon": "AWS/Networking & CDN/API Gateway/API Gateway"},
            EntityType.COMPONENT: {"color": "Gray", "icon": "AWS/General/General/General"},
        }
        
        self._relationship_color_mapping = {
            RelationshipType.INHERITS: "Green",
            RelationshipType.IMPLEMENTS: "Blue", 
            RelationshipType.DEPENDS_ON: "Orange",
            RelationshipType.CALLS: "Purple",
            RelationshipType.IMPORTS: "Gray",
            RelationshipType.CONTAINS: "Brown",
            RelationshipType.USES: "Indigo",
            RelationshipType.COMMUNICATES_WITH: "Red",
        }
    
    def generate(self, analysis_result: AnalysisResult) -> IlographDiagram:
        """Generate an Ilograph diagram from analysis results."""
        # Convert entities to resources
        resources = []
        for entity in analysis_result.entities:
            resource = self._entity_to_resource(entity)
            resources.append(resource)
        
        # Generate perspectives with relationships
        perspectives = self._generate_perspectives(analysis_result)
        
        return IlographDiagram(resources=resources, perspectives=perspectives)
    
    def _entity_to_resource(self, entity: Entity) -> IlographResource:
        """Convert an Entity to an IlographResource."""
        entity_config = self._entity_type_mapping.get(
            entity.type, 
            {"color": "Gray", "icon": "AWS/General/General/General"}
        )
        
        # Build subtitle from properties
        subtitle_parts = []
        if entity.line_number:
            subtitle_parts.append(f"Line {entity.line_number}")
        if entity.properties.get("parameters"):
            params = entity.properties["parameters"]
            subtitle_parts.append(f"({', '.join(params)})")
        
        subtitle = " | ".join(subtitle_parts) if subtitle_parts else None
        
        return IlographResource(
            name=entity.name,
            id=entity.id,
            subtitle=subtitle,
            color=entity_config["color"],
            icon=entity_config["icon"]
        )
    
    def _generate_perspectives(self, analysis_result: AnalysisResult) -> List[IlographPerspective]:
        """Generate perspectives with relations from the analysis."""
        # Collect all unique perspectives from entities
        all_perspectives: Set[str] = set()
        for entity in analysis_result.entities:
            all_perspectives.update(entity.perspectives)
        
        perspectives = []
        
        # Create perspective-specific views
        for perspective_name in sorted(all_perspectives):
            relations = self._create_relations_for_perspective(analysis_result, perspective_name)
            if relations:  # Only add perspective if it has relations
                perspectives.append(IlographPerspective(name=perspective_name, relations=relations))
        
        # Add a default "Dependencies" perspective with all relationships
        all_relations = []
        for relationship in analysis_result.relationships:
            relation = self._relationship_to_relation(relationship)
            all_relations.append(relation)
        
        if all_relations:
            perspectives.insert(0, IlographPerspective(name="Dependencies", relations=all_relations))
        
        return perspectives
    
    def _create_relations_for_perspective(self, analysis_result: AnalysisResult, perspective_name: str) -> List[IlographRelation]:
        """Create relations for a specific perspective."""
        relations = []
        
        # Filter entities for this perspective
        perspective_entities = [e for e in analysis_result.entities if perspective_name in e.perspectives]
        perspective_entity_ids = {e.id for e in perspective_entities}
        
        # Include relationships where both entities are in this perspective
        for relationship in analysis_result.relationships:
            if (relationship.from_entity_id in perspective_entity_ids and 
                relationship.to_entity_id in perspective_entity_ids):
                relation = self._relationship_to_relation(relationship)
                relations.append(relation)
        
        return relations
    
    def _relationship_to_relation(self, relationship: Relationship) -> IlographRelation:
        """Convert a Relationship to an IlographRelation."""
        color = self._relationship_color_mapping.get(relationship.type, "Gray")
        
        # Extract entity names from IDs for cleaner display
        from_name = relationship.from_entity_id.split('.')[-1]  # Get last part after dot
        to_name = relationship.to_entity_id.split('.')[-1]
        
        return IlographRelation(
            from_=from_name,
            to_=to_name,
            label=relationship.label or relationship.type.value.replace('_', ' ').title(),
            color=color
        ) 