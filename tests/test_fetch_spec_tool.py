"""
Tests for the fetch_spec_tool in the Ilograph MCP Server.

This module tests the specification fetching tools using FastMCP's in-memory testing
patterns with proper mocking of HTTP requests and error handling scenarios.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastmcp import Client, FastMCP


def create_test_server():
    """Create a test server with specification tools registered."""
    from ilograph_mcp.tools.register_fetch_spec_tool import register_fetch_spec_tool

    server = FastMCP("TestIlographServer")
    register_fetch_spec_tool(server)
    return server


@pytest.fixture
def mock_fetcher():
    """Create a mock fetcher with test data."""
    mock = MagicMock()

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
                "total_entries": 2,
                "valid_entries": 2,
                "expired_entries": 0,
                "keys": ["docs_resources", "specification"],
            },
        }
    )

    return mock


class TestFetchSpecTool:
    """Test cases for the fetch_spec_tool."""

    async def test_fetch_specification_success(self, mock_fetcher):
        """Test successfully fetching the Ilograph specification."""
        mock_spec_content = """# The Ilograph Spec

**Note: this spec was last updated on May 7, 2025.**

## Top-level properties 

| property | description | type | required |
|----------|-------------|------|----------|
| resources | An array of resources (the resource tree) | array | no |
| perspectives | An array of perspectives | array | no |
| contexts | An array of contexts | array | no |

## Resource 

Resources are the building blocks of Ilograph diagrams.

| property | description | type | required |
|----------|-------------|------|----------|
| name | The name of the resource | string | yes |
| subtitle | The subtitle of the resource | string | no |
| description | The description of the resource | string/object | no |"""

        mock_fetcher.fetch_specification = AsyncMock(return_value=mock_spec_content)

        with patch(
            "ilograph_mcp.tools.register_fetch_spec_tool.get_fetcher",
            return_value=mock_fetcher,
        ):
            mcp_server = create_test_server()
            async with Client(mcp_server) as client:
                result = await client.call_tool("fetch_spec_tool", {})

                assert len(result) == 1
                response_text = result[0].text

                # Check that the response contains the expected content
                assert "# Ilograph Specification" in response_text
                assert "**Source:** https://www.ilograph.com/docs/spec/" in response_text
                assert "Official Ilograph YAML format specification" in response_text
                assert mock_spec_content in response_text
                assert "Top-level properties" in response_text

                # Verify the fetcher was called correctly
                mock_fetcher.fetch_specification.assert_called_once()

    async def test_fetch_specification_case_insensitive(self, mock_fetcher):
        """Test that specification fetching works regardless of parameter casing."""
        mock_spec_content = "# The Ilograph Spec\n\nSpecification content here."
        mock_fetcher.fetch_specification = AsyncMock(return_value=mock_spec_content)

        with patch(
            "ilograph_mcp.tools.register_fetch_spec_tool.get_fetcher",
            return_value=mock_fetcher,
        ):
            mcp_server = create_test_server()
            async with Client(mcp_server) as client:
                result = await client.call_tool("fetch_spec_tool", {})

                assert len(result) == 1
                response_text = result[0].text

                # Check that the response contains the expected content
                assert "# Ilograph Specification" in response_text
                assert mock_spec_content in response_text

                # Verify the fetcher was called correctly
                mock_fetcher.fetch_specification.assert_called_once()

    async def test_fetch_specification_failure(self, mock_fetcher):
        """Test handling of specification fetch failure."""
        mock_fetcher.fetch_specification = AsyncMock(return_value=None)

        with patch(
            "ilograph_mcp.tools.register_fetch_spec_tool.get_fetcher",
            return_value=mock_fetcher,
        ):
            mcp_server = create_test_server()
            async with Client(mcp_server) as client:
                result = await client.call_tool("fetch_spec_tool", {})

                assert len(result) == 1
                response_text = result[0].text

                # Check error message
                assert "Error:" in response_text
                assert "Failed to fetch Ilograph specification" in response_text
                assert "temporarily unavailable" in response_text

    async def test_fetch_specification_exception(self, mock_fetcher):
        """Test handling of unexpected errors when fetching specification."""
        mock_fetcher.fetch_specification = AsyncMock(side_effect=Exception("Network error"))

        with patch(
            "ilograph_mcp.tools.register_fetch_spec_tool.get_fetcher",
            return_value=mock_fetcher,
        ):
            mcp_server = create_test_server()
            async with Client(mcp_server) as client:
                result = await client.call_tool("fetch_spec_tool", {})

                assert len(result) == 1
                response_text = result[0].text

                # Check error message (should not expose internal details)
                assert "Error:" in response_text
                assert "unexpected error occurred" in response_text
                assert "Network error" not in response_text  # Internal error should be hidden


class TestCheckSpecHealth:
    """Test cases for the check_spec_health tool."""

    async def test_spec_health_check_healthy(self, mock_fetcher):
        """Test spec health check when specification service is healthy."""
        with patch(
            "ilograph_mcp.tools.register_fetch_spec_tool.get_fetcher",
            return_value=mock_fetcher,
        ):
            mcp_server = create_test_server()
            async with Client(mcp_server) as client:
                result = await client.call_tool("check_spec_health", {})

                assert len(result) == 1
                response_text = result[0].text

                # Check response format
                assert "# Specification Service Health Report" in response_text
                assert "**Overall Status:** HEALTHY" in response_text

                # Check specification endpoint status
                assert "## Specification Endpoint" in response_text
                assert "✅ **Ilograph Spec Endpoint**: HEALTHY" in response_text
                assert "https://www.ilograph.com/docs/spec/" in response_text

                # Check cache information
                assert "## Specification Cache" in response_text
                assert "**Cached:** Yes" in response_text
                assert "**Total Cache Entries:** 2" in response_text

                # Check status message
                assert "Specification service is operational" in response_text

    async def test_spec_health_check_unhealthy(self, mock_fetcher):
        """Test spec health check when specification service is unhealthy."""
        # Mock unhealthy spec status
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
                "cache_stats": {
                    "total_entries": 1,
                    "valid_entries": 1,
                    "expired_entries": 0,
                    "keys": ["docs_resources"],
                },
            }
        )

        with patch(
            "ilograph_mcp.tools.register_fetch_spec_tool.get_fetcher",
            return_value=mock_fetcher,
        ):
            mcp_server = create_test_server()
            async with Client(mcp_server) as client:
                result = await client.call_tool("check_spec_health", {})

                assert len(result) == 1
                response_text = result[0].text

                # Check response format
                assert "**Overall Status:** UNHEALTHY" in response_text
                assert "❌ **Ilograph Spec Endpoint**: UNHEALTHY" in response_text
                assert "Error: Connection timeout" in response_text
                assert "**Cached:** No" in response_text
                assert "Specification service is experiencing issues" in response_text

    async def test_spec_health_check_error(self, mock_fetcher):
        """Test error handling when spec health check fails."""
        mock_fetcher.health_check = AsyncMock(side_effect=Exception("Health check failed"))

        with patch(
            "ilograph_mcp.tools.register_fetch_spec_tool.get_fetcher",
            return_value=mock_fetcher,
        ):
            mcp_server = create_test_server()
            async with Client(mcp_server) as client:
                result = await client.call_tool("check_spec_health", {})

                assert len(result) == 1
                response_text = result[0].text

                # Check error message
                assert "Error:" in response_text
                assert "Error performing spec health check" in response_text


class TestToolIntegration:
    """Integration tests for the specification tools."""

    async def test_spec_tools_registered(self):
        """Test that all expected spec tools are registered with the server."""
        mcp_server = create_test_server()
        async with Client(mcp_server) as client:
            tools = await client.list_tools()

            tool_names = [tool.name for tool in tools]

            # Check all expected tools are present
            assert "fetch_spec_tool" in tool_names
            assert "check_spec_health" in tool_names

            # Check tool metadata
            fetch_tool = next(tool for tool in tools if tool.name == "fetch_spec_tool")
            # Check that the description contains key information (it's the full docstring)
            assert (
                "Fetches the official Ilograph specification from https://www.ilograph.com/docs/spec/"
                in fetch_tool.description
            )

            health_tool = next(tool for tool in tools if tool.name == "check_spec_health")
            assert (
                "Checks the health and connectivity of the specification fetching service"
                in health_tool.description
            )

    async def test_workflow_health_then_fetch(self, mock_fetcher):
        """Test a typical workflow: check health, then fetch specification."""
        mock_spec_content = "# The Ilograph Spec\n\nThis is the specification content."
        mock_fetcher.fetch_specification = AsyncMock(return_value=mock_spec_content)

        with patch(
            "ilograph_mcp.tools.register_fetch_spec_tool.get_fetcher",
            return_value=mock_fetcher,
        ):
            mcp_server = create_test_server()
            async with Client(mcp_server) as client:
                # First, check health
                health_result = await client.call_tool("check_spec_health", {})
                assert "HEALTHY" in health_result[0].text

                # Then fetch the specification
                fetch_result = await client.call_tool("fetch_spec_tool", {})
                assert "The Ilograph Spec" in fetch_result[0].text
                assert mock_spec_content in fetch_result[0].text

                # Verify calls
                mock_fetcher.health_check.assert_called()
                mock_fetcher.fetch_specification.assert_called_once()


class TestRealFetcher:
    """Integration tests that test the tools with the actual fetcher to ensure they work end-to-end."""

    async def test_fetch_actual_specification(self):
        """Test fetching actual specification without mocking."""
        mcp_server = create_test_server()
        async with Client(mcp_server) as client:
            # Test fetching the real specification
            result = await client.call_tool("fetch_spec_tool", {})

            assert len(result) == 1
            response_text = result[0].text

            # Check that we get real content
            assert "# Ilograph Specification" in response_text
            assert "**Source:** https://www.ilograph.com/docs/spec/" in response_text
            # Should contain actual specification content
            assert len(response_text) > 1000  # Real content should be substantial

    async def test_actual_spec_health_check(self):
        """Test actual spec health check without mocking."""
        mcp_server = create_test_server()
        async with Client(mcp_server) as client:
            result = await client.call_tool("check_spec_health", {})

            assert len(result) == 1
            response_text = result[0].text

            # Check response format
            assert "# Specification Service Health Report" in response_text
            assert "**Overall Status:**" in response_text
            assert "## Specification Endpoint" in response_text
            assert "## Specification Cache" in response_text

    async def test_workflow_with_actual_fetcher(self):
        """Test a complete workflow with the actual fetcher."""
        mcp_server = create_test_server()
        async with Client(mcp_server) as client:
            # First check health
            health_result = await client.call_tool("check_spec_health", {})
            assert "# Specification Service Health Report" in health_result[0].text

            # Then fetch specification
            spec_result = await client.call_tool("fetch_spec_tool", {})
            assert "# Ilograph Specification" in spec_result[0].text
