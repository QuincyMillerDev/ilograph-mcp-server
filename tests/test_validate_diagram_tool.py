"""
Tests for the validate_diagram_tool in the Ilograph MCP Server.

This module tests the diagram validation tools using FastMCP's in-memory testing
patterns with comprehensive YAML and Ilograph schema validation scenarios.
"""

import json
from unittest.mock import patch

import pytest
from fastmcp import Client, FastMCP

from ilograph_mcp.tools.register_validate_diagram_tool import (
    IlographValidator,
    ValidationResult,
    format_validation_result,
    register_validate_diagram_tool,
)


@pytest.fixture
def mcp_server():
    """Create a test FastMCP server with validation tools registered."""
    server = FastMCP("TestIlographServer")
    register_validate_diagram_tool(server)
    return server


class TestIlographValidator:
    """Test cases for the IlographValidator class."""

    def test_validator_initialization(self):
        """Test that the validator initializes with expected properties."""
        validator = IlographValidator()

        assert "resources" in validator.known_top_level_properties
        assert "perspectives" in validator.known_top_level_properties
        assert "contexts" in validator.known_top_level_properties
        assert "imports" in validator.known_top_level_properties
        assert "layout" in validator.known_top_level_properties

        assert "name" in validator.known_resource_properties
        assert "id" in validator.known_resource_properties
        assert "children" in validator.known_resource_properties
        assert "instanceOf" in validator.known_resource_properties

        assert "from" in validator.known_relation_properties
        assert "to" in validator.known_relation_properties
        assert "arrowDirection" in validator.known_relation_properties

    def test_validate_yaml_syntax_valid(self):
        """Test validation of valid YAML content."""
        validator = IlographValidator()
        result = ValidationResult(success=True)

        valid_yaml = """
resources:
- name: Test Resource
  description: A test resource
"""

        data = validator.validate_yaml_syntax(valid_yaml, result)

        assert result.yaml_valid is True
        assert data is not None
        assert "resources" in data
        assert len(result.errors) == 0

    def test_validate_yaml_syntax_invalid(self):
        """Test validation of invalid YAML content."""
        validator = IlographValidator()
        result = ValidationResult(success=True)

        invalid_yaml = """
resources:
- name: Test Resource
  description: A test resource
    invalid_indentation: bad
"""

        data = validator.validate_yaml_syntax(invalid_yaml, result)

        assert result.yaml_valid is False
        assert data is None
        assert len(result.errors) == 1
        assert "Invalid YAML syntax" in result.errors[0].message

    def test_validate_top_level_structure_valid(self):
        """Test validation of valid top-level structure."""
        validator = IlographValidator()
        result = ValidationResult(success=True)

        data = {"resources": [], "perspectives": []}

        validator.validate_top_level_structure(data, result)

        assert len(result.errors) == 0
        assert len(result.warnings) == 0

    def test_validate_top_level_structure_unknown_property(self):
        """Test validation with unknown top-level property."""
        validator = IlographValidator()
        result = ValidationResult(success=True)

        data = {"resources": [], "unknown_property": "value"}

        validator.validate_top_level_structure(data, result)

        assert len(result.errors) == 0
        assert len(result.warnings) == 1
        assert "Unknown top-level property: 'unknown_property'" in result.warnings[0].message

    def test_validate_top_level_structure_no_resources(self):
        """Test validation with no resources section."""
        validator = IlographValidator()
        result = ValidationResult(success=True)

        data = {"perspectives": []}

        validator.validate_top_level_structure(data, result)

        assert len(result.errors) == 0
        assert len(result.warnings) == 1
        assert "No 'resources' section found" in result.warnings[0].message

    def test_validate_resources_valid(self):
        """Test validation of valid resources."""
        validator = IlographValidator()
        result = ValidationResult(success=True)

        resources = [
            {"name": "Resource 1", "description": "First resource"},
            {"id": "resource-2", "name": "Resource 2"},
        ]

        validator.validate_resources(resources, result)

        assert len(result.errors) == 0

    def test_validate_resources_invalid_format(self):
        """Test validation of resources with invalid format."""
        validator = IlographValidator()
        result = ValidationResult(success=True)

        resources = "not a list"

        validator.validate_resources(resources, result)

        assert len(result.errors) == 1
        assert "The 'resources' property must be a list" in result.errors[0].message

    def test_validate_resource_missing_name_and_id(self):
        """Test validation of resource missing both name and id."""
        validator = IlographValidator()
        result = ValidationResult(success=True)
        resource_ids = set()

        resource = {"description": "Resource without name or id"}

        validator.validate_resource(resource, result, "resources[0]", resource_ids)

        assert len(result.errors) == 1
        assert "Resource must have either 'name' or 'id' property" in result.errors[0].message

    def test_validate_resource_duplicate_id(self):
        """Test validation of resources with duplicate IDs."""
        validator = IlographValidator()
        result = ValidationResult(success=True)
        resource_ids = {"existing-id"}

        resource = {"id": "existing-id", "name": "Duplicate"}

        validator.validate_resource(resource, result, "resources[0]", resource_ids)

        assert len(result.errors) == 1
        assert "Duplicate resource ID: 'existing-id'" in result.errors[0].message

    def test_validate_resource_unknown_property(self):
        """Test validation of resource with unknown property."""
        validator = IlographValidator()
        result = ValidationResult(success=True)
        resource_ids = set()

        resource = {"name": "Test", "unknown_prop": "value"}

        validator.validate_resource(resource, result, "resources[0]", resource_ids)

        assert len(result.errors) == 0
        assert len(result.warnings) == 1
        assert "Unknown resource property: 'unknown_prop'" in result.warnings[0].message

    def test_validate_resource_instanceOf_namespace(self):
        """Test validation of instanceOf with namespace format."""
        validator = IlographValidator()
        result = ValidationResult(success=True)
        resource_ids = set()

        resource = {"name": "Test", "instanceOf": "AWS::EC2::Instance"}

        validator.validate_resource(resource, result, "resources[0]", resource_ids)

        assert len(result.errors) == 0
        assert len(result.warnings) == 0

    def test_validate_resource_instanceOf_no_namespace(self):
        """Test validation of instanceOf without namespace format."""
        validator = IlographValidator()
        result = ValidationResult(success=True)
        resource_ids = set()

        resource = {"name": "Test", "instanceOf": "SomeResource"}

        validator.validate_resource(resource, result, "resources[0]", resource_ids)

        assert len(result.errors) == 0
        assert len(result.info) == 1
        assert "instanceOf without namespace" in result.info[0].message

    def test_validate_relation_valid(self):
        """Test validation of valid relation."""
        validator = IlographValidator()
        result = ValidationResult(success=True)

        relation = {"from": "Resource A", "to": "Resource B", "label": "connects to"}

        validator.validate_relation(relation, result, "relations[0]")

        assert len(result.errors) == 0

    def test_validate_relation_missing_from_to(self):
        """Test validation of relation missing from/to properties."""
        validator = IlographValidator()
        result = ValidationResult(success=True)

        relation = {"label": "incomplete relation"}

        validator.validate_relation(relation, result, "relations[0]")

        assert len(result.errors) == 1
        assert "Relation must have both 'from' and 'to' properties" in result.errors[0].message

    def test_validate_relation_invalid_arrow_direction(self):
        """Test validation of relation with invalid arrowDirection."""
        validator = IlographValidator()
        result = ValidationResult(success=True)

        relation = {"from": "A", "to": "B", "arrowDirection": "invalid_direction"}

        validator.validate_relation(relation, result, "relations[0]")

        assert len(result.errors) == 1
        assert "Invalid arrowDirection: 'invalid_direction'" in result.errors[0].message

    def test_validate_relation_valid_arrow_directions(self):
        """Test validation of relation with valid arrowDirection values."""
        validator = IlographValidator()

        valid_directions = ["forward", "backward", "bidirectional"]

        for direction in valid_directions:
            result = ValidationResult(success=True)
            relation = {"from": "A", "to": "B", "arrowDirection": direction}

            validator.validate_relation(relation, result, "relations[0]")

            assert len(result.errors) == 0, f"Direction '{direction}' should be valid"

    def test_validate_imports_valid(self):
        """Test validation of valid imports."""
        validator = IlographValidator()
        result = ValidationResult(success=True)

        imports = [{"from": "ilograph/aws", "namespace": "AWS"}, {"from": "ilograph/azure"}]

        validator.validate_imports(imports, result)

        assert len(result.errors) == 0

    def test_validate_imports_missing_from(self):
        """Test validation of imports missing 'from' property."""
        validator = IlographValidator()
        result = ValidationResult(success=True)

        imports = [{"namespace": "AWS"}]

        validator.validate_imports(imports, result)

        assert len(result.errors) == 1
        assert "Import must have 'from' property" in result.errors[0].message


class TestValidateDiagramTool:
    """Test cases for the validate_diagram_tool."""

    async def test_validate_valid_diagram(self, mcp_server):
        """Test validation of a valid Ilograph diagram."""
        valid_diagram = """
resources:
- name: Web Server
  subtitle: Frontend
  description: Serves the web application
  children:
  - name: Load Balancer
    description: Distributes traffic

perspectives:
- name: System Overview
  relations:
  - from: User
    to: Web Server
    label: HTTPS requests
"""

        async with Client(mcp_server) as client:
            result = await client.call_tool("validate_diagram_tool", {"content": valid_diagram})

            assert len(result) == 1
            response_data = json.loads(result[0].text)

            assert response_data["success"] is True
            assert response_data["yaml_valid"] is True
            assert response_data["schema_valid"] is True
            assert response_data["assessment"] == "Valid"
            assert response_data["summary"]["total_errors"] == 0

    async def test_validate_diagram_with_warnings(self, mcp_server):
        """Test validation of diagram that has warnings but is valid."""
        diagram_with_warnings = """
resources:
- name: Web Server
  unknown_property: some_value

unknown_top_level: value
"""

        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "validate_diagram_tool", {"content": diagram_with_warnings}
            )

            assert len(result) == 1
            response_data = json.loads(result[0].text)

            assert response_data["success"] is True
            assert response_data["yaml_valid"] is True
            assert response_data["schema_valid"] is True
            assert response_data["assessment"] == "Valid with suggestions"
            assert response_data["summary"]["total_warnings"] > 0

    async def test_validate_invalid_yaml(self, mcp_server):
        """Test validation of invalid YAML content."""
        invalid_yaml = """
resources:
- name: Web Server
  description: Missing quote
    invalid_indentation: bad
"""

        async with Client(mcp_server) as client:
            result = await client.call_tool("validate_diagram_tool", {"content": invalid_yaml})

            assert len(result) == 1
            response_data = json.loads(result[0].text)

            assert response_data["success"] is False
            assert response_data["yaml_valid"] is False
            assert response_data["schema_valid"] is False
            assert response_data["assessment"] == "Invalid - contains errors"
            assert response_data["summary"]["total_errors"] > 0

    async def test_validate_diagram_with_schema_errors(self, mcp_server):
        """Test validation of diagram with Ilograph schema errors."""
        invalid_schema = """
resources:
- description: Resource without name or id

perspectives:
- relations:
  - from: A
    # missing 'to' property
"""

        async with Client(mcp_server) as client:
            result = await client.call_tool("validate_diagram_tool", {"content": invalid_schema})

            assert len(result) == 1
            response_data = json.loads(result[0].text)

            assert response_data["success"] is False
            assert response_data["yaml_valid"] is True
            assert response_data["schema_valid"] is False
            assert response_data["assessment"] == "Invalid - contains errors"
            assert response_data["summary"]["total_errors"] > 0

    async def test_validate_empty_content(self, mcp_server):
        """Test validation with empty content."""
        async with Client(mcp_server) as client:
            result = await client.call_tool("validate_diagram_tool", {"content": ""})

            assert len(result) == 1
            response_data = json.loads(result[0].text)

            assert response_data["success"] is False
            assert response_data["assessment"] == "Invalid - no content provided"
            assert "Content is empty" in response_data["errors"][0]["message"]

    async def test_validate_no_content(self, mcp_server):
        """Test validation without content parameter."""
        async with Client(mcp_server) as client:
            # This should raise a ToolError because content is a required parameter
            with pytest.raises(
                Exception
            ):  # FastMCP will raise validation error for missing required param
                await client.call_tool("validate_diagram_tool", {})

    async def test_validate_complex_valid_diagram(self, mcp_server):
        """Test validation of a complex but valid diagram."""
        complex_diagram = """
imports:
- from: ilograph/aws
  namespace: AWS

resources:
- name: Web Application
  children:
  - id: frontend
    name: Frontend
    instanceOf: AWS::S3::Bucket
    description: Static website hosting
  - id: backend
    name: Backend API
    instanceOf: AWS::Lambda::Function
    children:
    - name: Database
      instanceOf: AWS::DynamoDB::Table

perspectives:
- name: Architecture Overview
  relations:
  - from: frontend
    to: backend
    label: API calls
    arrowDirection: forward
  - from: backend
    to: Database
    label: queries
    arrowDirection: bidirectional

- name: Data Flow
  sequences:
  - start: User
    steps:
    - to: frontend
      label: visits site
    - to: backend
      label: makes request
    - to: Database
      label: fetches data
"""

        async with Client(mcp_server) as client:
            result = await client.call_tool("validate_diagram_tool", {"content": complex_diagram})

            assert len(result) == 1
            response_data = json.loads(result[0].text)

            assert response_data["success"] is True
            assert response_data["yaml_valid"] is True
            assert response_data["schema_valid"] is True


class TestGetValidationHelp:
    """Test cases for the get_validation_help tool."""

    async def test_get_validation_help(self, mcp_server):
        """Test getting validation help content."""
        async with Client(mcp_server) as client:
            result = await client.call_tool("get_validation_help", {})

            assert len(result) == 1
            help_content = result[0].text

            # Check that help content contains expected sections
            assert "# Ilograph Diagram Validation Help" in help_content
            assert "## Validation Process" in help_content
            assert "## Common Issues and Solutions" in help_content
            assert "### YAML Syntax Errors" in help_content
            assert "### Ilograph Schema Issues" in help_content
            assert "## Valid Top-Level Properties" in help_content
            assert "## Example Valid Structure" in help_content
            assert "## Getting More Help" in help_content
            assert "## Tips for Success" in help_content

            # Check for specific guidance
            assert "fetch_spec_tool()" in help_content
            assert "fetch_documentation_tool" in help_content
            assert "fetch_example_tool()" in help_content


class TestValidationResultFormatting:
    """Test cases for validation result formatting."""

    def test_format_validation_result_success(self):
        """Test formatting of successful validation result."""
        result = ValidationResult(success=True, yaml_valid=True, schema_valid=True)
        result.add_info("Diagram structure looks good!")

        formatted = format_validation_result(result)

        assert formatted["success"] is True
        assert formatted["yaml_valid"] is True
        assert formatted["schema_valid"] is True
        assert formatted["assessment"] == "Valid"
        assert formatted["summary"]["total_errors"] == 0
        assert formatted["summary"]["total_info"] == 1

    def test_format_validation_result_with_warnings(self):
        """Test formatting of validation result with warnings."""
        result = ValidationResult(success=True, yaml_valid=True, schema_valid=True)
        result.add_warning("Unknown property found")

        formatted = format_validation_result(result)

        assert formatted["success"] is True
        assert formatted["assessment"] == "Valid with suggestions"
        assert formatted["summary"]["total_warnings"] == 1

    def test_format_validation_result_with_errors(self):
        """Test formatting of validation result with errors."""
        result = ValidationResult(success=False, yaml_valid=False, schema_valid=False)
        result.add_error("Invalid YAML syntax")

        formatted = format_validation_result(result)

        assert formatted["success"] is False
        assert formatted["assessment"] == "Invalid - contains errors"
        assert formatted["summary"]["total_errors"] == 1


class TestToolIntegration:
    """Integration tests for the validation tools."""

    async def test_all_tools_registered(self, mcp_server):
        """Test that both validation tools are registered."""
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            tool_names = {tool.name for tool in tools}

            assert "validate_diagram_tool" in tool_names
            assert "get_validation_help" in tool_names

            # Check metadata for validation tool
            validation_tool = next(tool for tool in tools if tool.name == "validate_diagram_tool")
            assert "Validates Ilograph YAML syntax" in validation_tool.description
            assert validation_tool.inputSchema is not None

    async def test_workflow_help_then_validate(self, mcp_server):
        """Test workflow of getting help then validating a diagram."""
        async with Client(mcp_server) as client:
            # First get help
            help_result = await client.call_tool("get_validation_help", {})
            assert len(help_result) == 1
            assert "Validation Help" in help_result[0].text

            # Then validate a simple diagram
            simple_diagram = """
resources:
- name: Simple Resource
"""

            validation_result = await client.call_tool(
                "validate_diagram_tool", {"content": simple_diagram}
            )
            assert len(validation_result) == 1
            response_data = json.loads(validation_result[0].text)
            assert response_data["success"] is True


class TestErrorHandling:
    """Test error handling scenarios."""

    async def test_validation_tool_exception_handling(self, mcp_server):
        """Test that unexpected exceptions are handled gracefully."""
        with patch(
            "ilograph_mcp.tools.register_validate_diagram_tool.IlographValidator.validate",
            side_effect=Exception("Unexpected error"),
        ):
            async with Client(mcp_server) as client:
                result = await client.call_tool(
                    "validate_diagram_tool", {"content": "test: content"}
                )

                assert len(result) == 1
                response_data = json.loads(result[0].text)

                assert response_data["success"] is False
                assert response_data["assessment"] == "Error - validation failed"
                assert "unexpected error occurred" in response_data["errors"][0]["message"]
                # Should not expose internal error details
                assert "Unexpected error" not in response_data["errors"][0]["message"]

    async def test_help_tool_exception_handling(self, mcp_server):
        """Test that help tool handles exceptions gracefully."""
        with patch("builtins.open", side_effect=Exception("File error")):
            async with Client(mcp_server) as client:
                result = await client.call_tool("get_validation_help", {})

                assert len(result) == 1
                # Should still return help content since it's hardcoded
                assert "# Ilograph Diagram Validation Help" in result[0].text
