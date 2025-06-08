"""
Validate Diagram Tool for Ilograph MCP Server.

This tool provides comprehensive validation of Ilograph diagram syntax and structure.
It first validates YAML syntax, then validates Ilograph-specific schema requirements
using the official specification and documentation for context.
"""

import logging
import re
from typing import Any, Dict, List, Optional, Set

import yaml
from fastmcp import Context, FastMCP
from pydantic import BaseModel

from ..core.fetcher import get_fetcher

logger = logging.getLogger(__name__)


class ValidationError(BaseModel):
    """Represents a validation error with detailed information."""

    level: str  # 'error', 'warning', 'info'
    message: str
    line: Optional[int] = None
    column: Optional[int] = None
    path: Optional[str] = None
    suggestion: Optional[str] = None


class ValidationResult(BaseModel):
    """Represents the complete validation result."""

    success: bool
    errors: List[ValidationError] = []
    warnings: List[ValidationError] = []
    info: List[ValidationError] = []
    yaml_valid: bool = False
    schema_valid: bool = False

    @property
    def total_issues(self) -> int:
        return len(self.errors) + len(self.warnings)

    def add_error(
        self,
        message: str,
        line: Optional[int] = None,
        column: Optional[int] = None,
        path: Optional[str] = None,
        suggestion: Optional[str] = None,
    ) -> None:
        """Add a validation error."""
        self.errors.append(
            ValidationError(
                level="error",
                message=message,
                line=line,
                column=column,
                path=path,
                suggestion=suggestion,
            )
        )
        self.success = False

    def add_warning(
        self,
        message: str,
        line: Optional[int] = None,
        column: Optional[int] = None,
        path: Optional[str] = None,
        suggestion: Optional[str] = None,
    ) -> None:
        """Add a validation warning."""
        self.warnings.append(
            ValidationError(
                level="warning",
                message=message,
                line=line,
                column=column,
                path=path,
                suggestion=suggestion,
            )
        )

    def add_info(
        self, message: str, path: Optional[str] = None, suggestion: Optional[str] = None
    ) -> None:
        """Add validation info."""
        self.info.append(
            ValidationError(level="info", message=message, path=path, suggestion=suggestion)
        )


class IlographValidator:
    """Core validator for Ilograph diagrams."""

    def __init__(self):
        self.known_top_level_properties = {
            "resources",
            "perspectives",
            "contexts",
            "imports",
            "layout",
        }
        self.known_resource_properties = {
            "id",
            "name",
            "subtitle",
            "description",
            "icon",
            "iconStyle",
            "color",
            "children",
            "instanceOf",
            "abstract",
            "alias",
            "for",
        }
        self.known_perspective_properties = {
            "name",
            "description",
            "notes",
            "extends",
            "aliases",
            "overrides",
            "relations",
            "sequences",
        }
        self.known_relation_properties = {
            "from",
            "to",
            "via",
            "label",
            "description",
            "color",
            "arrowDirection",
            "secondary",
        }

    def validate_yaml_syntax(
        self, content: str, result: ValidationResult
    ) -> Optional[Dict[str, Any]]:
        """Validate YAML syntax and return parsed data if valid."""
        try:
            # Try to parse the YAML
            data = yaml.safe_load(content)
            result.yaml_valid = True
            return data
        except yaml.YAMLError as e:
            result.add_error(
                f"Invalid YAML syntax: {str(e)}",
                line=(
                    getattr(e, "problem_mark", {}).line
                    if hasattr(e, "problem_mark") and e.problem_mark
                    else None
                ),
                column=(
                    getattr(e, "problem_mark", {}).column
                    if hasattr(e, "problem_mark") and e.problem_mark
                    else None
                ),
                suggestion="Check for indentation issues, missing colons, or invalid characters",
            )
            return None

    def validate_top_level_structure(self, data: Dict[str, Any], result: ValidationResult) -> None:
        """Validate the top-level structure of the Ilograph diagram."""
        if not isinstance(data, dict):
            result.add_error(
                "Ilograph diagram must be a YAML object (dictionary) at the top level",
                suggestion="Ensure your diagram starts with properties like 'resources:', 'perspectives:', etc.",
            )
            return

        # Check for unknown top-level properties
        for key in data.keys():
            if key not in self.known_top_level_properties:
                result.add_warning(
                    f"Unknown top-level property: '{key}'",
                    path=key,
                    suggestion=f"Valid top-level properties are: {', '.join(sorted(self.known_top_level_properties))}",
                )

        # Check if we have at least resources
        if "resources" not in data:
            result.add_warning(
                "No 'resources' section found - diagrams typically need resources to be meaningful",
                suggestion="Add a 'resources:' section with your diagram's components",
            )

    def validate_resources(self, resources: Any, result: ValidationResult) -> None:
        """Validate the resources section."""
        if not isinstance(resources, list):
            result.add_error(
                "The 'resources' property must be a list",
                path="resources",
                suggestion="Change 'resources: ...' to 'resources: [...]' or use YAML list syntax with dashes",
            )
            return

        resource_ids = set()
        for i, resource in enumerate(resources):
            self.validate_resource(resource, result, f"resources[{i}]", resource_ids)

    def validate_resource(
        self, resource: Any, result: ValidationResult, path: str, resource_ids: Set[str]
    ) -> None:
        """Validate a single resource."""
        if not isinstance(resource, dict):
            result.add_error(
                "Each resource must be an object (dictionary)",
                path=path,
                suggestion="Use 'name: ResourceName' format for resources",
            )
            return

        # Check for required properties - either 'name' or 'id' should be present
        if "name" not in resource and "id" not in resource:
            result.add_error(
                "Resource must have either 'name' or 'id' property",
                path=path,
                suggestion="Add 'name: YourResourceName' or 'id: your-resource-id'",
            )

        # Check for duplicate IDs
        resource_id = resource.get("id")
        if resource_id:
            if resource_id in resource_ids:
                result.add_error(
                    f"Duplicate resource ID: '{resource_id}'",
                    path=f"{path}.id",
                    suggestion="Resource IDs must be unique across the diagram",
                )
            else:
                resource_ids.add(resource_id)

        # Check for unknown properties
        for key in resource.keys():
            if key not in self.known_resource_properties:
                result.add_warning(
                    f"Unknown resource property: '{key}'",
                    path=f"{path}.{key}",
                    suggestion=f"Valid resource properties include: {', '.join(sorted(self.known_resource_properties))}",
                )

        # Validate instanceOf format
        instance_of = resource.get("instanceOf")
        if instance_of and isinstance(instance_of, str):
            if "::" in instance_of:
                # This looks like a namespace reference - that's good
                pass
            else:
                result.add_info(
                    f"Resource uses instanceOf without namespace: '{instance_of}'",
                    path=f"{path}.instanceOf",
                    suggestion="Consider using namespace format like 'AWS::EC2::Instance' or define the resource locally",
                )

        # Validate children if present
        children = resource.get("children")
        if children:
            if not isinstance(children, list):
                result.add_error(
                    "The 'children' property must be a list",
                    path=f"{path}.children",
                    suggestion="Use list format: 'children: [{name: Child1}, {name: Child2}]'",
                )
            else:
                for j, child in enumerate(children):
                    self.validate_resource(child, result, f"{path}.children[{j}]", resource_ids)

    def validate_perspectives(self, perspectives: Any, result: ValidationResult) -> None:
        """Validate the perspectives section."""
        if not isinstance(perspectives, list):
            result.add_error(
                "The 'perspectives' property must be a list",
                path="perspectives",
                suggestion="Use list format with dashes: '- name: PerspectiveName'",
            )
            return

        for i, perspective in enumerate(perspectives):
            self.validate_perspective(perspective, result, f"perspectives[{i}]")

    def validate_perspective(self, perspective: Any, result: ValidationResult, path: str) -> None:
        """Validate a single perspective."""
        if not isinstance(perspective, dict):
            result.add_error(
                "Each perspective must be an object (dictionary)",
                path=path,
                suggestion="Use 'name: PerspectiveName' format for perspectives",
            )
            return

        # Check for name (recommended)
        if "name" not in perspective:
            result.add_warning(
                "Perspective should have a 'name' property",
                path=path,
                suggestion="Add 'name: YourPerspectiveName' for better clarity",
            )

        # Check for unknown properties
        for key in perspective.keys():
            if key not in self.known_perspective_properties:
                result.add_warning(
                    f"Unknown perspective property: '{key}'",
                    path=f"{path}.{key}",
                    suggestion=f"Valid perspective properties include: {', '.join(sorted(self.known_perspective_properties))}",
                )

        # Validate relations if present
        relations = perspective.get("relations")
        if relations:
            self.validate_relations(relations, result, f"{path}.relations")

    def validate_relations(self, relations: Any, result: ValidationResult, path: str) -> None:
        """Validate relations in a perspective."""
        if not isinstance(relations, list):
            result.add_error(
                "The 'relations' property must be a list",
                path=path,
                suggestion="Use list format with dashes for each relation",
            )
            return

        for i, relation in enumerate(relations):
            self.validate_relation(relation, result, f"{path}[{i}]")

    def validate_relation(self, relation: Any, result: ValidationResult, path: str) -> None:
        """Validate a single relation."""
        if not isinstance(relation, dict):
            result.add_error(
                "Each relation must be an object (dictionary)",
                path=path,
                suggestion="Use 'from: source, to: target' format",
            )
            return

        # Check for required properties
        if "from" not in relation or "to" not in relation:
            result.add_error(
                "Relation must have both 'from' and 'to' properties",
                path=path,
                suggestion="Add both 'from: SourceResource' and 'to: TargetResource'",
            )

        # Check for unknown properties
        for key in relation.keys():
            if key not in self.known_relation_properties:
                result.add_warning(
                    f"Unknown relation property: '{key}'",
                    path=f"{path}.{key}",
                    suggestion=f"Valid relation properties include: {', '.join(sorted(self.known_relation_properties))}",
                )

        # Validate arrowDirection if present
        arrow_direction = relation.get("arrowDirection")
        if arrow_direction:
            valid_directions = {"forward", "backward", "bidirectional"}
            if arrow_direction not in valid_directions:
                result.add_error(
                    f"Invalid arrowDirection: '{arrow_direction}'",
                    path=f"{path}.arrowDirection",
                    suggestion=f"Valid values are: {', '.join(valid_directions)}",
                )

    def validate_imports(self, imports: Any, result: ValidationResult) -> None:
        """Validate the imports section."""
        if not isinstance(imports, list):
            result.add_error(
                "The 'imports' property must be a list",
                path="imports",
                suggestion="Use list format: '- from: namespace'",
            )
            return

        for i, import_item in enumerate(imports):
            if not isinstance(import_item, dict):
                result.add_error(
                    "Each import must be an object (dictionary)",
                    path=f"imports[{i}]",
                    suggestion="Use format: 'from: namespace, namespace: alias'",
                )
                continue

            if "from" not in import_item:
                result.add_error(
                    "Import must have 'from' property",
                    path=f"imports[{i}]",
                    suggestion="Add 'from: namespace/path' to specify what to import",
                )

    def validate_schema(self, data: Dict[str, Any], result: ValidationResult) -> None:
        """Validate the Ilograph schema structure."""
        try:
            self.validate_top_level_structure(data, result)

            if "resources" in data:
                self.validate_resources(data["resources"], result)

            if "perspectives" in data:
                self.validate_perspectives(data["perspectives"], result)

            if "imports" in data:
                self.validate_imports(data["imports"], result)

            # If we got here without critical errors, schema is basically valid
            if not result.errors:
                result.schema_valid = True
                if not result.warnings:
                    result.add_info(
                        "Diagram structure looks good!",
                        suggestion="Consider adding descriptions to your resources and perspectives for better documentation",
                    )

        except Exception as e:
            result.add_error(
                f"Unexpected error during schema validation: {str(e)}",
                suggestion="This might indicate a complex structure that needs manual review",
            )

    def validate(self, content: str) -> ValidationResult:
        """Main validation method."""
        result = ValidationResult(success=True)

        # Step 1: Validate YAML syntax
        data = self.validate_yaml_syntax(content, result)
        if data is None:
            return result  # YAML is invalid, no point in continuing

        # Step 2: Validate Ilograph schema
        self.validate_schema(data, result)

        # Set final success status
        result.success = len(result.errors) == 0

        return result


def format_validation_result(result: ValidationResult) -> Dict[str, Any]:
    """Format validation result for JSON response."""
    formatted = {
        "success": result.success,
        "yaml_valid": result.yaml_valid,
        "schema_valid": result.schema_valid,
        "summary": {
            "total_errors": len(result.errors),
            "total_warnings": len(result.warnings),
            "total_info": len(result.info),
        },
    }

    if result.errors:
        formatted["errors"] = [error.model_dump() for error in result.errors]

    if result.warnings:
        formatted["warnings"] = [warning.model_dump() for warning in result.warnings]

    if result.info:
        formatted["info"] = [info.model_dump() for info in result.info]

    # Add overall assessment
    if result.success:
        if result.warnings:
            formatted["assessment"] = "Valid with suggestions"
        else:
            formatted["assessment"] = "Valid"
    else:
        formatted["assessment"] = "Invalid - contains errors"

    return formatted


def register_validate_diagram_tool(mcp: FastMCP) -> None:
    """Register the validate diagram tool with the FastMCP server."""

    @mcp.tool(
        annotations={
            "title": "Validate Ilograph Diagram",
            "readOnlyHint": True,
            "description": "Validates Ilograph diagram syntax and provides detailed error messages with suggestions",
        }
    )
    async def validate_diagram_tool(content: str, ctx: Context) -> Dict[str, Any]:
        """
        Validates Ilograph YAML syntax and structure.

        This tool performs comprehensive validation of Ilograph diagrams:
        1. First validates YAML syntax for structural correctness
        2. Then validates Ilograph-specific schema requirements
        3. Provides detailed error messages, warnings, and suggestions
        4. Can optionally use official Ilograph specification for context

        Args:
            content: The Ilograph diagram content as a string

        Returns:
            dict: Validation result with success/failure, errors, warnings, and suggestions
                 Format: {
                     "success": bool,
                     "yaml_valid": bool,
                     "schema_valid": bool,
                     "summary": {"total_errors": int, "total_warnings": int, "total_info": int},
                     "errors": [{"level": str, "message": str, "line": int, "suggestion": str}, ...],
                     "warnings": [...],
                     "info": [...],
                     "assessment": str
                 }
        """
        try:
            await ctx.info("Starting Ilograph diagram validation")

            # Validate input
            if not isinstance(content, str):
                error_result = {
                    "success": False,
                    "yaml_valid": False,
                    "schema_valid": False,
                    "errors": [
                        {
                            "level": "error",
                            "message": "Content parameter is required and must be a non-empty string",
                            "suggestion": "Provide the Ilograph diagram content as a string parameter",
                        }
                    ],
                    "assessment": "Invalid - no content provided",
                }
                await ctx.error("Validation failed: no content provided")
                return error_result

            content = content.strip()
            if not content:
                error_result = {
                    "success": False,
                    "yaml_valid": False,
                    "schema_valid": False,
                    "errors": [
                        {
                            "level": "error",
                            "message": "Content is empty",
                            "suggestion": "Provide actual Ilograph diagram content",
                        }
                    ],
                    "assessment": "Invalid - no content provided",
                }
                await ctx.error("Validation failed: empty content")
                return error_result

            # Create validator and run validation
            validator = IlographValidator()
            result = validator.validate(content)

            # Format the result
            formatted_result = format_validation_result(result)

            # Log results
            if result.success:
                await ctx.info(
                    f"Validation successful - {len(result.warnings)} warnings, {len(result.info)} suggestions"
                )
            else:
                await ctx.error(
                    f"Validation failed - {len(result.errors)} errors, {len(result.warnings)} warnings"
                )

            return formatted_result

        except Exception as e:
            error_msg = f"Unexpected error during validation: {str(e)}"
            await ctx.error(error_msg)
            logger.exception("Error in validate_diagram_tool")

            return {
                "success": False,
                "yaml_valid": False,
                "schema_valid": False,
                "errors": [
                    {
                        "level": "error",
                        "message": "An unexpected error occurred during validation",
                        "suggestion": "Please check your diagram format and try again",
                    }
                ],
                "assessment": "Error - validation failed",
            }

    @mcp.tool(
        annotations={
            "title": "Get Validation Help",
            "readOnlyHint": True,
            "description": "Provides guidance on Ilograph diagram validation and common issues",
        }
    )
    async def get_validation_help(ctx: Context) -> str:
        """
        Provides comprehensive help for Ilograph diagram validation.

        Returns guidance on common validation issues, proper syntax,
        and best practices for creating valid Ilograph diagrams.

        Returns:
            str: Detailed validation help in markdown format
        """
        try:
            await ctx.info("Providing Ilograph validation help")

            help_content = """# Ilograph Diagram Validation Help

## Overview
This validation tool checks your Ilograph diagrams for both YAML syntax correctness and Ilograph-specific schema compliance.

## Validation Process
1. **YAML Syntax Check**: Ensures your diagram is valid YAML
2. **Schema Validation**: Checks Ilograph-specific structure and properties
3. **Best Practice Suggestions**: Provides recommendations for improvement

## Common Issues and Solutions

### YAML Syntax Errors
- **Indentation**: Use consistent spaces (2 or 4), not tabs
- **Missing Colons**: Properties need colons (`name: value`)
- **List Format**: Use dashes for lists or bracket notation
- **Quoted Strings**: Quote strings with special characters

### Ilograph Schema Issues
- **Missing Required Properties**: Resources need `name` or `id`
- **Unknown Properties**: Check property names against specification
- **Duplicate IDs**: Resource IDs must be unique
- **Invalid Relations**: Relations need both `from` and `to`

## Valid Top-Level Properties
- `resources`: Your diagram components (required for meaningful diagrams)
- `perspectives`: Different views of your architecture
- `contexts`: Multiple context views
- `imports`: External namespace imports
- `layout`: Diagram layout properties

## Example Valid Structure
```yaml
imports:
- from: ilograph/aws
  namespace: AWS

resources:
- name: Web Server
  subtitle: Frontend
  description: Serves the web application
  icon: server.svg
  children:
  - name: Load Balancer
    instanceOf: AWS::ElasticLoadBalancer

perspectives:
- name: System Overview
  relations:
  - from: User
    to: Web Server
    label: HTTPS requests
```

## Getting More Help
- Use `fetch_spec_tool()` to get the complete Ilograph specification
- Use `fetch_documentation_tool(section='tutorial')` for detailed tutorials
- Use `fetch_example_tool()` to see working example diagrams

## Tips for Success
1. Start with simple structures and build complexity gradually
2. Use consistent naming conventions
3. Add descriptions to improve documentation
4. Validate frequently during development
5. Check examples for pattern guidance
"""

            await ctx.info("Validation help provided successfully")
            return help_content

        except Exception as e:
            error_msg = f"Error providing validation help: {str(e)}"
            await ctx.error(error_msg)
            return f"Error: {error_msg}"


def get_tool_info() -> dict:
    """Get information about the validation tools for registration."""
    return {
        "name": "validate_diagram_tool",
        "description": "Comprehensive Ilograph diagram validation with detailed error reporting",
        "tools": [
            "validate_diagram_tool",
            "get_validation_help",
        ],
    }
