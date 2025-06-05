"""
Base classes for code analysis.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from enum import Enum

class EntityType(Enum):
    """Types of architectural entities that can be discovered."""
    CLASS = "class"
    INTERFACE = "interface"
    FUNCTION = "function"
    METHOD = "method"
    MODULE = "module"
    PACKAGE = "package"
    SERVICE = "service"
    DATABASE = "database"
    API_ENDPOINT = "api_endpoint"
    COMPONENT = "component"

class RelationshipType(Enum):
    """Types of relationships between entities."""
    INHERITS = "inherits"
    IMPLEMENTS = "implements"
    DEPENDS_ON = "depends_on"
    CALLS = "calls"
    IMPORTS = "imports"
    CONTAINS = "contains"
    USES = "uses"
    COMMUNICATES_WITH = "communicates_with"

@dataclass
class Entity:
    """Represents a code entity (class, function, module, etc.)."""
    id: str
    name: str
    type: EntityType
    file_path: str
    line_number: Optional[int] = None
    description: Optional[str] = None
    properties: Dict[str, Any] = field(default_factory=dict)
    perspectives: Set[str] = field(default_factory=set)

@dataclass
class Relationship:
    """Represents a relationship between two entities."""
    from_entity_id: str
    to_entity_id: str
    type: RelationshipType
    label: Optional[str] = None
    properties: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AnalysisResult:
    """Results of codebase analysis."""
    entities: List[Entity] = field(default_factory=list)
    relationships: List[Relationship] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_entity(self, entity: Entity) -> None:
        """Add an entity to the analysis results."""
        self.entities.append(entity)
    
    def add_relationship(self, relationship: Relationship) -> None:
        """Add a relationship to the analysis results."""
        self.relationships.append(relationship)
    
    def get_entities_by_type(self, entity_type: EntityType) -> List[Entity]:
        """Get all entities of a specific type."""
        return [e for e in self.entities if e.type == entity_type]
    
    def get_entity_by_id(self, entity_id: str) -> Optional[Entity]:
        """Get an entity by its ID."""
        return next((e for e in self.entities if e.id == entity_id), None)

class CodeAnalyzer(ABC):
    """Abstract base class for code analyzers."""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.supported_extensions: Set[str] = set()
        self.result = AnalysisResult()
    
    @abstractmethod
    def analyze_file(self, file_path: Path) -> None:
        """Analyze a single file and update the result."""
        pass
    
    @abstractmethod
    def can_analyze(self, file_path: Path) -> bool:
        """Check if this analyzer can handle the given file."""
        pass
    
    def analyze_directory(self, directory: Path, recursive: bool = True) -> AnalysisResult:
        """Analyze all supported files in a directory."""
        self.result = AnalysisResult()
        
        if recursive:
            files = directory.rglob("*")
        else:
            files = directory.glob("*")
        
        for file_path in files:
            if file_path.is_file() and self.can_analyze(file_path):
                try:
                    self.analyze_file(file_path)
                except Exception as e:
                    # Log error but continue analysis
                    self.result.metadata.setdefault("errors", []).append(
                        f"Error analyzing {file_path}: {str(e)}"
                    )
        
        return self.result
    
    def _generate_entity_id(self, name: str, file_path: str, line_number: Optional[int] = None) -> str:
        """Generate a unique ID for an entity."""
        base_id = f"{Path(file_path).stem}.{name}"
        if line_number is not None:
            base_id += f":{line_number}"
        return base_id 