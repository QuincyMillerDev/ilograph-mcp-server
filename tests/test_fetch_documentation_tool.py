"""
Tests for the fetch_documentation_tool in the Ilograph MCP Server.

This module tests the documentation fetching tools using FastMCP's in-memory testing
patterns with proper mocking of HTTP requests and error handling scenarios.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastmcp import FastMCP, Client


@pytest.fixture
def mock_fetcher():
    """Create a mock fetcher with test data."""
    mock = MagicMock()

    # Mock supported sections
    mock.get_supported_documentation_sections.return_value = {
        "resources": "Resource tree organization, hierarchies, instanceOf patterns",
        "relation-perspectives": "Arrow connections, from/to properties, routing, labels",
        "contexts": "Multiple context views with roots, extends inheritance",
        "tutorial": "Complete tutorial for learning Ilograph diagram creation",
    }

    # Mock health check response
    mock.health_check = AsyncMock(
        return_value={
            "status": "healthy",
            "services": {
                "documentation": {"status": "healthy", "url": "https://www.ilograph.com/docs/"},
                "specification": {
                    "status": "healthy",
                    "url": "https://www.ilograph.com/docs/spec/",
                },
            },
            "cache_stats": {
                "total_entries": 3,
                "valid_entries": 3,
                "expired_entries": 0,
                "keys": ["docs_resources", "docs_contexts", "specification"],
            },
        }
    )

    return mock


def create_test_server():
    """Create a test server with documentation tools registered."""
    from ilograph_mcp.tools.register_fetch_documentation_tools import (
        register_fetch_documentation_tool,
    )

    server = FastMCP("TestIlographServer")
    register_fetch_documentation_tool(server)
    return server


class TestFetchDocumentationTool:
    """Test cases for the fetch_documentation_tool."""

    async def test_fetch_valid_section(self, mock_fetcher):
        """Test fetching a valid documentation section."""
        mock_content = """# Resources in Ilograph

Resources are the building blocks of your Ilograph diagrams. They represent 
the components in your system and can be organized in hierarchical structures.

## Basic Resource Structure

```yaml
resources:
  - name: "My Service"
    type: "service"
    children:
      - name: "Database"
        type: "database"
```

This example shows a basic service with a database component."""

        mock_fetcher.fetch_documentation_section = AsyncMock(return_value=mock_content)

        with patch(
            "ilograph_mcp.tools.register_fetch_documentation_tools.get_fetcher",
            return_value=mock_fetcher,
        ):
            mcp_server = create_test_server()
            async with Client(mcp_server) as client:
                result = await client.call_tool(
                    "fetch_documentation_tool", {"section": "resources"}
                )

                assert len(result) == 1
                response_text = result[0].text

                # Check that the response contains the expected content
                assert "# Ilograph Documentation: Resources" in response_text
                assert "**Section:** resources" in response_text
                assert "Resource tree organization" in response_text
                assert mock_content in response_text
                assert "https://www.ilograph.com/docs/editing/resources/" in response_text

                # Verify the fetcher was called correctly
                mock_fetcher.fetch_documentation_section.assert_called_once_with("resources")

    async def test_fetch_invalid_section(self, mock_fetcher):
        """Test fetching an invalid documentation section."""
        with patch(
            "ilograph_mcp.tools.register_fetch_documentation_tools.get_fetcher",
            return_value=mock_fetcher,
        ):
            mcp_server = create_test_server()
            async with Client(mcp_server) as client:
                result = await client.call_tool(
                    "fetch_documentation_tool", {"section": "invalid-section"}
                )

                assert len(result) == 1
                response_text = result[0].text

                # Check error message
                assert "Error:" in response_text
                assert "Unsupported section 'invalid-section'" in response_text
                assert "Available sections:" in response_text
                assert "resources" in response_text

    async def test_fetch_empty_section(self, mock_fetcher):
        """Test fetching with empty section parameter."""
        with patch(
            "ilograph_mcp.tools.register_fetch_documentation_tools.get_fetcher",
            return_value=mock_fetcher,
        ):
            mcp_server = create_test_server()
            async with Client(mcp_server) as client:
                result = await client.call_tool("fetch_documentation_tool", {"section": ""})

                assert len(result) == 1
                response_text = result[0].text

                # Check error message
                assert "Error:" in response_text
                assert "Section parameter is required" in response_text

    async def test_fetch_network_failure(self, mock_fetcher):
        """Test handling of network failures when fetching documentation."""
        mock_fetcher.fetch_documentation_section = AsyncMock(return_value=None)

        with patch(
            "ilograph_mcp.tools.register_fetch_documentation_tools.get_fetcher",
            return_value=mock_fetcher,
        ):
            mcp_server = create_test_server()
            async with Client(mcp_server) as client:
                result = await client.call_tool(
                    "fetch_documentation_tool", {"section": "resources"}
                )

                assert len(result) == 1
                response_text = result[0].text

                # Check error message
                assert "Error:" in response_text
                assert "Failed to fetch documentation for section 'resources'" in response_text
                assert "temporarily unavailable" in response_text

    async def test_fetch_unexpected_error(self, mock_fetcher):
        """Test handling of unexpected errors during fetching."""
        mock_fetcher.fetch_documentation_section = AsyncMock(
            side_effect=Exception("Network timeout")
        )

        with patch(
            "ilograph_mcp.tools.register_fetch_documentation_tools.get_fetcher",
            return_value=mock_fetcher,
        ):
            mcp_server = create_test_server()
            async with Client(mcp_server) as client:
                result = await client.call_tool(
                    "fetch_documentation_tool", {"section": "resources"}
                )

                assert len(result) == 1
                response_text = result[0].text

                # Check error message (should not expose internal details)
                assert "Error:" in response_text
                assert "unexpected error occurred" in response_text
                assert "Network timeout" not in response_text  # Internal error should be hidden


class TestListDocumentationSections:
    """Test cases for the list_documentation_sections tool."""

    async def test_list_sections_success(self, mock_fetcher):
        """Test successfully listing documentation sections."""
        with patch(
            "ilograph_mcp.tools.register_fetch_documentation_tools.get_fetcher",
            return_value=mock_fetcher,
        ):
            mcp_server = create_test_server()
            async with Client(mcp_server) as client:
                result = await client.call_tool("list_documentation_sections", {})

                assert len(result) == 1
                response_text = result[0].text

                # Check response format
                assert "# Available Ilograph Documentation Sections" in response_text
                assert "## resources" in response_text
                assert "## relation-perspectives" in response_text
                assert "## contexts" in response_text
                assert "## tutorial" in response_text

                # Check descriptions are included
                assert "Resource tree organization" in response_text
                assert "Arrow connections" in response_text
                assert "Multiple context views" in response_text

                # Check usage instructions
                assert "fetch_documentation_tool(section='resources')" in response_text

    async def test_list_sections_error(self, mock_fetcher):
        """Test error handling when listing sections fails."""
        mock_fetcher.get_supported_documentation_sections.side_effect = Exception("Cache error")

        with patch(
            "ilograph_mcp.tools.register_fetch_documentation_tools.get_fetcher",
            return_value=mock_fetcher,
        ):
            mcp_server = create_test_server()
            async with Client(mcp_server) as client:
                result = await client.call_tool("list_documentation_sections", {})

                assert len(result) == 1
                response_text = result[0].text

                # Check error message
                assert "Error:" in response_text
                assert "Error listing documentation sections" in response_text


class TestCheckDocumentationHealth:
    """Test cases for the check_documentation_health tool."""

    async def test_health_check_healthy(self, mock_fetcher):
        """Test health check when all services are healthy."""
        with patch(
            "ilograph_mcp.tools.register_fetch_documentation_tools.get_fetcher",
            return_value=mock_fetcher,
        ):
            mcp_server = create_test_server()
            async with Client(mcp_server) as client:
                result = await client.call_tool("check_documentation_health", {})

                assert len(result) == 1
                response_text = result[0].text

                # Check response format
                assert "# Documentation Service Health Report" in response_text
                assert "**Overall Status:** HEALTHY" in response_text

                # Check service status
                assert "## Service Connectivity" in response_text
                assert "✅ **Documentation**: HEALTHY" in response_text
                assert "✅ **Specification**: HEALTHY" in response_text
                assert "https://www.ilograph.com/docs/" in response_text

                # Check cache statistics
                assert "## Cache Statistics" in response_text
                assert "**Total Entries:** 3" in response_text
                assert "**Valid Entries:** 3" in response_text
                assert "**Expired Entries:** 0" in response_text
                assert "docs_resources" in response_text

                # Check status message
                assert "All services are operational" in response_text

    async def test_health_check_degraded(self, mock_fetcher):
        """Test health check when some services are unhealthy."""
        # Mock degraded health status
        mock_fetcher.health_check = AsyncMock(
            return_value={
                "status": "degraded",
                "services": {
                    "documentation": {"status": "healthy", "url": "https://www.ilograph.com/docs/"},
                    "specification": {
                        "status": "unhealthy",
                        "url": "https://www.ilograph.com/docs/spec/",
                        "error": "Connection timeout",
                    },
                },
                "unhealthy_services": ["specification"],
                "cache_stats": {
                    "total_entries": 1,
                    "valid_entries": 1,
                    "expired_entries": 0,
                    "keys": ["docs_resources"],
                },
            }
        )

        with patch(
            "ilograph_mcp.tools.register_fetch_documentation_tools.get_fetcher",
            return_value=mock_fetcher,
        ):
            mcp_server = create_test_server()
            async with Client(mcp_server) as client:
                result = await client.call_tool("check_documentation_health", {})

                assert len(result) == 1
                response_text = result[0].text

                # Check response format
                assert "**Overall Status:** DEGRADED" in response_text
                assert "✅ **Documentation**: HEALTHY" in response_text
                assert "❌ **Specification**: UNHEALTHY" in response_text
                assert "Error: Connection timeout" in response_text
                assert "Some services are experiencing issues: specification" in response_text

    async def test_health_check_error(self, mock_fetcher):
        """Test error handling when health check fails."""
        mock_fetcher.health_check = AsyncMock(side_effect=Exception("Health check failed"))

        with patch(
            "ilograph_mcp.tools.register_fetch_documentation_tools.get_fetcher",
            return_value=mock_fetcher,
        ):
            mcp_server = create_test_server()
            async with Client(mcp_server) as client:
                result = await client.call_tool("check_documentation_health", {})

                assert len(result) == 1
                response_text = result[0].text

                # Check error message
                assert "Error:" in response_text
                assert "Error performing health check" in response_text


class TestToolIntegration:
    """Integration tests for the documentation tools."""

    async def test_all_tools_registered(self):
        """Test that all expected tools are registered with the server."""
        mcp_server = create_test_server()
        async with Client(mcp_server) as client:
            tools = await client.list_tools()

            tool_names = [tool.name for tool in tools]

            # Check all expected tools are present
            assert "fetch_documentation_tool" in tool_names
            assert "list_documentation_sections" in tool_names
            assert "check_documentation_health" in tool_names

            # Check tool metadata
            fetch_tool = next(tool for tool in tools if tool.name == "fetch_documentation_tool")
            # Check that the description contains key information (it's the full docstring)
            assert (
                "Fetches and formats narrative documentation from Ilograph website"
                in fetch_tool.description
            )
            # Check that the section parameter is present in the schema
            assert "section" in fetch_tool.inputSchema.get("properties", {})

    async def test_workflow_list_then_fetch(self, mock_fetcher):
        """Test a typical workflow: list sections, then fetch one."""
        mock_content = "# Tutorial Content\nThis is tutorial content."
        mock_fetcher.fetch_documentation_section = AsyncMock(return_value=mock_content)

        with patch(
            "ilograph_mcp.tools.register_fetch_documentation_tools.get_fetcher",
            return_value=mock_fetcher,
        ):
            mcp_server = create_test_server()
            async with Client(mcp_server) as client:
                # First, list available sections
                list_result = await client.call_tool("list_documentation_sections", {})
                assert "tutorial" in list_result[0].text

                # Then fetch a specific section
                fetch_result = await client.call_tool(
                    "fetch_documentation_tool", {"section": "tutorial"}
                )
                assert "Tutorial Content" in fetch_result[0].text
                assert mock_content in fetch_result[0].text

                # Verify calls
                mock_fetcher.get_supported_documentation_sections.assert_called()
                mock_fetcher.fetch_documentation_section.assert_called_with("tutorial")


class TestRealFetcher:
    """Integration tests that test the tools with the actual fetcher to ensure they work end-to-end."""

    async def test_fetch_actual_documentation(self):
        """Test fetching actual documentation without mocking."""
        mcp_server = create_test_server()
        async with Client(mcp_server) as client:
            # Test fetching a real section
            result = await client.call_tool("fetch_documentation_tool", {"section": "resources"})

            assert len(result) == 1
            response_text = result[0].text

            # Check that we get real content
            assert "# Ilograph Documentation: Resources" in response_text
            assert "**Section:** resources" in response_text
            assert "https://www.ilograph.com/docs/editing/resources/" in response_text
            # Should contain actual documentation content
            assert len(response_text) > 1000  # Real content should be substantial

    async def test_list_actual_sections(self):
        """Test listing actual sections without mocking."""
        mcp_server = create_test_server()
        async with Client(mcp_server) as client:
            result = await client.call_tool("list_documentation_sections", {})

            assert len(result) == 1
            response_text = result[0].text

            # Check response format
            assert "# Available Ilograph Documentation Sections" in response_text
            # Should contain all the real sections
            assert "resources" in response_text
            assert "tutorial" in response_text
            assert "contexts" in response_text

    async def test_actual_health_check(self):
        """Test actual health check without mocking."""
        mcp_server = create_test_server()
        async with Client(mcp_server) as client:
            result = await client.call_tool("check_documentation_health", {})

            assert len(result) == 1
            response_text = result[0].text

            # Check response format
            assert "# Documentation Service Health Report" in response_text
            assert "**Overall Status:**" in response_text
            assert "## Service Connectivity" in response_text
            assert "## Cache Statistics" in response_text
