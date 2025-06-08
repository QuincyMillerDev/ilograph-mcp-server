"""
Tests for the fetch_icons_tool in the Ilograph MCP Server.

This module tests the icon searching tools using FastMCP's in-memory testing
patterns with proper mocking of HTTP requests and error handling scenarios.
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastmcp import Client, FastMCP


def create_test_server():
    """Create a test server with icon tools registered."""
    from ilograph_mcp.tools.register_fetch_icons_tool import register_fetch_icons_tool

    server = FastMCP("TestIlographServer")
    register_fetch_icons_tool(server)
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
                "icons": {"status": "healthy", "url": "https://www.ilograph.com/docs/iconlist.txt"},
            },
            "cache_stats": {
                "total_entries": 3,
                "valid_entries": 3,
                "expired_entries": 0,
                "keys": ["docs_resources", "specification", "icon_catalog"],
            },
        }
    )

    # Mock icon provider information
    mock.get_icon_providers = AsyncMock(
        return_value={
            "AWS": {
                "categories": ["Analytics", "Compute", "Database", "Networking", "Storage"],
                "total_icons": 150,
            },
            "Azure": {
                "categories": ["Compute", "Databases", "Analytics", "Networking"],
                "total_icons": 80,
            },
            "GCP": {
                "categories": ["Compute", "AI and ML", "Data Analytics", "Storage"],
                "total_icons": 60,
            },
            "Networking": {
                "categories": ["General"],
                "total_icons": 25,
            },
        }
    )

    # Mock catalog statistics
    mock.get_icon_catalog_stats = AsyncMock(
        return_value={
            "total_icons": 315,
            "providers": {
                "AWS": 150,
                "Azure": 80,
                "GCP": 60,
                "Networking": 25,
            },
            "categories": {
                "Compute": 45,
                "Database": 35,
                "Analytics": 30,
                "Networking": 40,
                "Storage": 25,
                "AI and ML": 20,
            },
            "last_updated": "2025-01-13T10:00:00Z",
        }
    )

    return mock


class TestSearchIconsTool:
    """Test cases for the search_icons_tool."""

    async def test_search_icons_success(self, mock_fetcher):
        """Test successfully searching for icons."""
        mock_search_results = [
            {
                "path": "AWS/Database/RDS.svg",
                "provider": "AWS",
                "category": "Database",
                "name": "RDS",
                "usage": 'icon: "AWS/Database/RDS.svg"',
            },
            {
                "path": "AWS/Database/DynamoDB.svg",
                "provider": "AWS",
                "category": "Database",
                "name": "DynamoDB",
                "usage": 'icon: "AWS/Database/DynamoDB.svg"',
            },
            {
                "path": "Azure/Databases/SQL Databases.svg",
                "provider": "Azure",
                "category": "Databases",
                "name": "SQL Databases",
                "usage": 'icon: "Azure/Databases/SQL Databases.svg"',
            },
        ]

        mock_fetcher.search_icons = AsyncMock(return_value=mock_search_results)

        with patch(
            "ilograph_mcp.tools.register_fetch_icons_tool.get_fetcher",
            return_value=mock_fetcher,
        ):
            mcp_server = create_test_server()
            async with Client(mcp_server) as client:
                result = await client.call_tool("search_icons_tool", {"query": "database"})

                assert len(result) == 1
                response_text = result[0].text

                # Check that we got JSON text with icons
                response_data = json.loads(response_text)
                assert isinstance(response_data, list)
                assert len(response_data) == 3

                # Check first icon structure
                first_icon = response_data[0]
                assert first_icon["path"] == "AWS/Database/RDS.svg"
                assert first_icon["provider"] == "AWS"
                assert first_icon["category"] == "Database"
                assert first_icon["name"] == "RDS"
                assert "AWS/Database/RDS.svg" in first_icon["usage"]

                # Verify the fetcher was called correctly
                mock_fetcher.search_icons.assert_called_once_with("database", None)

    async def test_search_icons_with_provider_filter(self, mock_fetcher):
        """Test searching for icons with provider filtering."""
        mock_search_results = [
            {
                "path": "AWS/Database/RDS.svg",
                "provider": "AWS",
                "category": "Database",
                "name": "RDS",
                "usage": 'icon: "AWS/Database/RDS.svg"',
            }
        ]

        mock_fetcher.search_icons = AsyncMock(return_value=mock_search_results)

        with patch(
            "ilograph_mcp.tools.register_fetch_icons_tool.get_fetcher",
            return_value=mock_fetcher,
        ):
            mcp_server = create_test_server()
            async with Client(mcp_server) as client:
                result = await client.call_tool(
                    "search_icons_tool", {"query": "database", "provider": "AWS"}
                )

                assert len(result) == 1
                response_text = result[0].text

                # Check that we got JSON text with filtered results
                response_data = json.loads(response_text)
                # Single result may be returned as a dict or list with one item
                if isinstance(response_data, dict):
                    assert response_data["provider"] == "AWS"
                else:
                    assert isinstance(response_data, list)
                    assert len(response_data) == 1
                    assert response_data[0]["provider"] == "AWS"

                # Verify the fetcher was called with provider filter
                mock_fetcher.search_icons.assert_called_once_with("database", "AWS")

    async def test_search_icons_no_results(self, mock_fetcher):
        """Test searching for icons with no results."""
        mock_fetcher.search_icons = AsyncMock(return_value=[])

        with patch(
            "ilograph_mcp.tools.register_fetch_icons_tool.get_fetcher",
            return_value=mock_fetcher,
        ):
            mcp_server = create_test_server()
            async with Client(mcp_server) as client:
                result = await client.call_tool("search_icons_tool", {"query": "nonexistent"})

                assert len(result) == 1
                response_text = result[0].text

                # Check that we got JSON text with a helpful no-results message
                response_data = json.loads(response_text)
                # No results may be returned as a dict or list with one item
                if isinstance(response_data, dict):
                    message_item = response_data
                else:
                    assert isinstance(response_data, list)
                    assert len(response_data) == 1
                    message_item = response_data[0]
                assert "No icons found matching" in message_item["message"]
                assert "suggestion" in message_item
                assert "available_providers" in message_item

    async def test_search_icons_empty_query(self, mock_fetcher):
        """Test searching with empty query parameter."""
        with patch(
            "ilograph_mcp.tools.register_fetch_icons_tool.get_fetcher",
            return_value=mock_fetcher,
        ):
            mcp_server = create_test_server()
            async with Client(mcp_server) as client:
                result = await client.call_tool("search_icons_tool", {"query": ""})

                assert len(result) == 1
                response_text = result[0].text

                # Check JSON error response
                import json

                response_data = json.loads(response_text)
                # Error may be returned as a dict or list with one item
                if isinstance(response_data, dict):
                    error_item = response_data
                else:
                    assert isinstance(response_data, list)
                    assert len(response_data) == 1
                    error_item = response_data[0]
                assert "error" in error_item
                assert "non-empty string" in error_item["error"]

    async def test_search_icons_missing_query(self, mock_fetcher):
        """Test searching without query parameter."""
        with patch(
            "ilograph_mcp.tools.register_fetch_icons_tool.get_fetcher",
            return_value=mock_fetcher,
        ):
            mcp_server = create_test_server()
            async with Client(mcp_server) as client:
                # This should raise an error due to missing required parameter
                with pytest.raises(Exception):
                    await client.call_tool("search_icons_tool", {})

    async def test_search_icons_invalid_provider(self, mock_fetcher):
        """Test searching with invalid provider filter."""
        with patch(
            "ilograph_mcp.tools.register_fetch_icons_tool.get_fetcher",
            return_value=mock_fetcher,
        ):
            mcp_server = create_test_server()
            async with Client(mcp_server) as client:
                result = await client.call_tool(
                    "search_icons_tool", {"query": "database", "provider": "InvalidProvider"}
                )

                assert len(result) == 1
                response_text = result[0].text

                # Check JSON error response
                import json

                response_data = json.loads(response_text)
                # Error may be returned as a dict or list with one item
                if isinstance(response_data, dict):
                    error_item = response_data
                else:
                    assert isinstance(response_data, list)
                    assert len(response_data) == 1
                    error_item = response_data[0]
                assert "error" in error_item
                assert "Invalid provider" in error_item["error"]
                assert "Valid providers" in error_item["error"]

    async def test_search_icons_fetch_failure(self, mock_fetcher):
        """Test handling of icon search failure."""
        mock_fetcher.search_icons = AsyncMock(return_value=None)

        with patch(
            "ilograph_mcp.tools.register_fetch_icons_tool.get_fetcher",
            return_value=mock_fetcher,
        ):
            mcp_server = create_test_server()
            async with Client(mcp_server) as client:
                result = await client.call_tool("search_icons_tool", {"query": "database"})

                assert len(result) == 1
                response_text = result[0].text

                # Check JSON error response
                import json

                response_data = json.loads(response_text)
                # Error may be returned as a dict or list with one item
                if isinstance(response_data, dict):
                    error_item = response_data
                else:
                    assert isinstance(response_data, list)
                    assert len(response_data) == 1
                    error_item = response_data[0]
                assert "error" in error_item
                assert "Failed to fetch icon catalog" in error_item["error"]

    async def test_search_icons_exception(self, mock_fetcher):
        """Test handling of unexpected errors when searching icons."""
        mock_fetcher.search_icons = AsyncMock(side_effect=Exception("Network error"))

        with patch(
            "ilograph_mcp.tools.register_fetch_icons_tool.get_fetcher",
            return_value=mock_fetcher,
        ):
            mcp_server = create_test_server()
            async with Client(mcp_server) as client:
                result = await client.call_tool("search_icons_tool", {"query": "database"})

                assert len(result) == 1
                response_text = result[0].text

                # Check JSON error response (should not expose internal details)
                import json

                response_data = json.loads(response_text)
                # Error may be returned as a dict or list with one item
                if isinstance(response_data, dict):
                    error_item = response_data
                else:
                    assert isinstance(response_data, list)
                    assert len(response_data) == 1
                    error_item = response_data[0]
                assert "error" in error_item
                assert "unexpected error occurred" in error_item["error"]
                assert "Network error" not in str(error_item)  # Internal error should be hidden


class TestListIconProvidersTool:
    """Test cases for the list_icon_providers_tool."""

    async def test_list_providers_success(self, mock_fetcher):
        """Test successfully listing icon providers."""
        with patch(
            "ilograph_mcp.tools.register_fetch_icons_tool.get_fetcher",
            return_value=mock_fetcher,
        ):
            mcp_server = create_test_server()
            async with Client(mcp_server) as client:
                result = await client.call_tool("list_icon_providers_tool", {})

                assert len(result) == 1
                response_text = result[0].text

                # Check JSON provider structure
                import json

                response_data = json.loads(response_text)
                assert isinstance(response_data, dict)
                assert "AWS" in response_data
                assert "Azure" in response_data
                assert "GCP" in response_data
                assert "Networking" in response_data

                # Check AWS provider details
                aws_info = response_data["AWS"]
                assert "categories" in aws_info
                assert "total_icons" in aws_info
                assert aws_info["total_icons"] == 150
                assert "Analytics" in aws_info["categories"]

    async def test_list_providers_failure(self, mock_fetcher):
        """Test handling of provider listing failure."""
        mock_fetcher.get_icon_providers = AsyncMock(return_value=None)

        with patch(
            "ilograph_mcp.tools.register_fetch_icons_tool.get_fetcher",
            return_value=mock_fetcher,
        ):
            mcp_server = create_test_server()
            async with Client(mcp_server) as client:
                result = await client.call_tool("list_icon_providers_tool", {})

                assert len(result) == 1
                response_text = result[0].text

                # Check JSON error response
                import json

                response_data = json.loads(response_text)
                assert isinstance(response_data, dict)
                assert "error" in response_data
                assert "Failed to fetch icon provider information" in response_data["error"]


class TestGetIconStatsTool:
    """Test cases for the get_icon_stats_tool."""

    async def test_get_stats_success(self, mock_fetcher):
        """Test successfully getting icon catalog statistics."""
        with patch(
            "ilograph_mcp.tools.register_fetch_icons_tool.get_fetcher",
            return_value=mock_fetcher,
        ):
            mcp_server = create_test_server()
            async with Client(mcp_server) as client:
                result = await client.call_tool("get_icon_stats_tool", {})

                assert len(result) == 1
                response_text = result[0].text

                # Check JSON stats structure
                import json

                response_data = json.loads(response_text)
                assert isinstance(response_data, dict)
                assert response_data["total_icons"] == 315
                assert "providers" in response_data
                assert "categories" in response_data
                assert "last_updated" in response_data

                # Check provider breakdown
                providers = response_data["providers"]
                assert providers["AWS"] == 150
                assert providers["Azure"] == 80
                assert providers["GCP"] == 60
                assert providers["Networking"] == 25

    async def test_get_stats_failure(self, mock_fetcher):
        """Test handling of stats generation failure."""
        mock_fetcher.get_icon_catalog_stats = AsyncMock(return_value=None)

        with patch(
            "ilograph_mcp.tools.register_fetch_icons_tool.get_fetcher",
            return_value=mock_fetcher,
        ):
            mcp_server = create_test_server()
            async with Client(mcp_server) as client:
                result = await client.call_tool("get_icon_stats_tool", {})

                assert len(result) == 1
                response_text = result[0].text

                # Check JSON error response
                import json

                response_data = json.loads(response_text)
                assert isinstance(response_data, dict)
                assert "error" in response_data
                assert "Failed to generate icon catalog statistics" in response_data["error"]


class TestToolIntegration:
    """Test integration between different tools."""

    async def test_icon_tools_registered(self):
        """Test that all icon tools are properly registered."""
        mcp_server = create_test_server()
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            tool_names = [tool.name for tool in tools]

            # Check that all expected tools are registered
            expected_tools = [
                "search_icons_tool",
                "list_icon_providers_tool",
                "get_icon_stats_tool",
            ]

            for tool_name in expected_tools:
                assert tool_name in tool_names, f"Tool {tool_name} should be registered"

    async def test_workflow_providers_then_search(self, mock_fetcher):
        """Test a typical workflow: check providers then search for icons."""
        mock_search_results = [
            {
                "path": "AWS/Compute/Lambda.svg",
                "provider": "AWS",
                "category": "Compute",
                "name": "Lambda",
                "usage": 'icon: "AWS/Compute/Lambda.svg"',
            }
        ]
        mock_fetcher.search_icons = AsyncMock(return_value=mock_search_results)

        with patch(
            "ilograph_mcp.tools.register_fetch_icons_tool.get_fetcher",
            return_value=mock_fetcher,
        ):
            mcp_server = create_test_server()
            async with Client(mcp_server) as client:
                # First, list providers to see what's available
                providers_result = await client.call_tool("list_icon_providers_tool", {})
                assert len(providers_result) == 1
                providers_text = providers_result[0].text
                import json

                providers_data = json.loads(providers_text)
                assert "AWS" in providers_data

                # Then search for icons
                search_result = await client.call_tool(
                    "search_icons_tool", {"query": "lambda", "provider": "AWS"}
                )
                assert len(search_result) == 1
                icons_text = search_result[0].text
                icons_data = json.loads(icons_text)
                # Result may be a single dict or list with one item
                if isinstance(icons_data, dict):
                    assert icons_data["name"] == "Lambda"
                else:
                    assert len(icons_data) == 1
                    assert icons_data[0]["name"] == "Lambda"


class TestRealFetcher:
    """Test with actual fetcher implementation (when available)."""

    async def test_search_actual_icons(self):
        """Test searching actual icons (integration test)."""
        # This test uses the real fetcher and makes actual HTTP requests
        # Mark as integration test and skip in unit test runs
        try:
            from ilograph_mcp.core.fetcher import get_fetcher

            mcp_server = create_test_server()
            async with Client(mcp_server) as client:
                result = await client.call_tool("search_icons_tool", {"query": "database"})

                assert len(result) == 1
                response_text = result[0].text

                # Should get some results for a common term like "database"
                import json

                response_data = json.loads(response_text)
                # Result may be a dict, list, or error
                if isinstance(response_data, dict):
                    if "error" not in response_data:
                        # Single icon result
                        assert "path" in response_data
                        assert "provider" in response_data
                        assert "category" in response_data
                        assert "name" in response_data
                        assert "usage" in response_data
                elif (
                    isinstance(response_data, list)
                    and response_data
                    and "error" not in response_data[0]
                ):
                    # Multiple icon results
                    first_icon = response_data[0]
                    assert "path" in first_icon
                    assert "provider" in first_icon
                    assert "category" in first_icon
                    assert "name" in first_icon
                    assert "usage" in first_icon
        except ImportError:
            # Skip if fetcher is not available
            pytest.skip("Fetcher implementation not available")

    async def test_workflow_with_actual_fetcher(self):
        """Test a complete workflow with the actual fetcher."""
        try:
            from ilograph_mcp.core.fetcher import get_fetcher

            mcp_server = create_test_server()
            async with Client(mcp_server) as client:
                # Get providers
                providers_result = await client.call_tool("list_icon_providers_tool", {})
                assert len(providers_result) == 1

                # Search for icons
                search_result = await client.call_tool("search_icons_tool", {"query": "compute"})
                assert len(search_result) == 1

                # Get stats
                stats_result = await client.call_tool("get_icon_stats_tool", {})
                assert len(stats_result) == 1
        except ImportError:
            # Skip if fetcher is not available
            pytest.skip("Fetcher implementation not available")
