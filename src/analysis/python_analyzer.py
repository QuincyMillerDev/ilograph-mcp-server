"""
Python code analyzer using AST parsing.
"""

import ast
from pathlib import Path
from typing import Dict, Optional

from .base import (
    CodeAnalyzer, Entity, Relationship, EntityType, RelationshipType
)

class PythonAnalyzer(CodeAnalyzer):
    """Analyzer for Python code using AST parsing."""
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.supported_extensions = {".py"}
        self.current_file_path: Optional[str] = None
        self.current_module_name: Optional[str] = None
    
    def can_analyze(self, file_path: Path) -> bool:
        """Check if this analyzer can handle Python files."""
        return file_path.suffix in self.supported_extensions
    
    def analyze_file(self, file_path: Path) -> None:
        """Analyze a Python file using AST parsing."""
        self.current_file_path = str(file_path)
        self.current_module_name = file_path.stem
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        try:
            tree = ast.parse(content, filename=str(file_path))
            visitor = PythonASTVisitor(self, self.current_file_path)
            visitor.visit(tree)
        except SyntaxError as e:
            self.result.metadata.setdefault("syntax_errors", []).append(
                f"Syntax error in {file_path}: {str(e)}"
            )

class PythonASTVisitor(ast.NodeVisitor):
    """AST visitor for extracting architectural information from Python code."""
    
    def __init__(self, analyzer: PythonAnalyzer, file_path: str):
        self.analyzer = analyzer
        self.file_path = file_path
        self.current_class: Optional[str] = None
        self.imports: Dict[str, str] = {}  # alias -> module mapping
    
    def visit_Import(self, node: ast.Import) -> None:
        """Handle import statements."""
        for alias in node.names:
            module_name = alias.name
            alias_name = alias.asname or alias.name
            self.imports[alias_name] = module_name
            
            # Create import relationship
            current_module_id = self.analyzer._generate_entity_id(
                Path(self.file_path).stem, self.file_path
            )
            imported_module_id = module_name
            
            relationship = Relationship(
                from_entity_id=current_module_id,
                to_entity_id=imported_module_id,
                type=RelationshipType.IMPORTS,
                label=f"imports {module_name}"
            )
            self.analyzer.result.add_relationship(relationship)
        
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Handle from ... import statements."""
        if node.module:
            for alias in node.names:
                imported_name = alias.name
                alias_name = alias.asname or alias.name
                full_name = f"{node.module}.{imported_name}"
                self.imports[alias_name] = full_name
                
                # Create import relationship
                current_module_id = self.analyzer._generate_entity_id(
                    Path(self.file_path).stem, self.file_path
                )
                
                relationship = Relationship(
                    from_entity_id=current_module_id,
                    to_entity_id=full_name,
                    type=RelationshipType.IMPORTS,
                    label=f"imports {imported_name} from {node.module}"
                )
                self.analyzer.result.add_relationship(relationship)
        
        self.generic_visit(node)
    
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Handle class definitions."""
        class_id = self.analyzer._generate_entity_id(
            node.name, self.file_path, node.lineno
        )
        
        entity = Entity(
            id=class_id,
            name=node.name,
            type=EntityType.CLASS,
            file_path=self.file_path,
            line_number=node.lineno,
            description=ast.get_docstring(node),
            perspectives={"Classes", "Architecture", "Object-Oriented"}
        )
        
        # Add class properties
        entity.properties["methods"] = []
        entity.properties["decorators"] = [d.id for d in node.decorator_list if isinstance(d, ast.Name)]
        
        self.analyzer.result.add_entity(entity)
        
        # Handle inheritance
        for base in node.bases:
            if isinstance(base, ast.Name):
                base_class_id = self._resolve_name(base.id)
                relationship = Relationship(
                    from_entity_id=class_id,
                    to_entity_id=base_class_id,
                    type=RelationshipType.INHERITS,
                    label="inherits from"
                )
                self.analyzer.result.add_relationship(relationship)
        
        # Visit class body with current class context
        old_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = old_class
    
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Handle function and method definitions."""
        if self.current_class:
            # This is a method
            entity_type = EntityType.METHOD
            entity_id = self.analyzer._generate_entity_id(
                f"{self.current_class}.{node.name}", self.file_path, node.lineno
            )
            perspectives = {"Methods", "Object-Oriented"}
            
            # Add to class's methods list
            class_id = self.analyzer._generate_entity_id(
                self.current_class, self.file_path
            )
            class_entity = self.analyzer.result.get_entity_by_id(class_id)
            if class_entity:
                class_entity.properties["methods"].append(node.name)
        else:
            # This is a module-level function
            entity_type = EntityType.FUNCTION
            entity_id = self.analyzer._generate_entity_id(
                node.name, self.file_path, node.lineno
            )
            perspectives = {"Functions", "Architecture"}
        
        entity = Entity(
            id=entity_id,
            name=node.name,
            type=entity_type,
            file_path=self.file_path,
            line_number=node.lineno,
            description=ast.get_docstring(node),
            perspectives=perspectives
        )
        
        # Add function/method properties
        entity.properties["parameters"] = [arg.arg for arg in node.args.args]
        entity.properties["decorators"] = [d.id for d in node.decorator_list if isinstance(d, ast.Name)]
        entity.properties["is_async"] = isinstance(node, ast.AsyncFunctionDef)
        
        self.analyzer.result.add_entity(entity)
        
        # If this is a method, create a relationship to the containing class
        if self.current_class:
            class_id = self.analyzer._generate_entity_id(
                self.current_class, self.file_path
            )
            relationship = Relationship(
                from_entity_id=class_id,
                to_entity_id=entity_id,
                type=RelationshipType.CONTAINS,
                label="contains method"
            )
            self.analyzer.result.add_relationship(relationship)
        
        self.generic_visit(node)
    
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Handle async function definitions."""
        self.visit_FunctionDef(node)
    
    def _resolve_name(self, name: str) -> str:
        """Resolve a name to its full module path if it's an import."""
        return self.imports.get(name, f"{Path(self.file_path).stem}.{name}") 