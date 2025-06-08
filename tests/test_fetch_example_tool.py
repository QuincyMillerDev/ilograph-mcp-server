"""
Tests for the fetch_example_tool in the Ilograph MCP Server.

This module tests the example fetching tools using FastMCP's in-memory testing
patterns, ensuring that example listing and fetching work as expected.
"""

import json
from unittest.mock import MagicMock, patch

import pytest
from fastmcp import Client, FastMCP

from ilograph_mcp.tools.register_example_tools import ExampleMetadata, register_example_tools

# Mock data for testing, mirroring the structure of the real database
MOCK_EXAMPLES_DATABASE = {
    "test-example-intermediate.ilograph": ExampleMetadata(
        name="test-example-intermediate.ilograph",
        category="intermediate",
        description="An intermediate test example.",
        learning_objectives=["Understand intermediate concepts"],
        patterns_demonstrated=["Intermediate Patterns"],
    ),
    "test-example-advanced.ilograph": ExampleMetadata(
        name="test-example-advanced.ilograph",
        category="advanced",
        description="An advanced test example.",
        learning_objectives=["Understand advanced concepts"],
        patterns_demonstrated=["Advanced Patterns", "Scalability"],
    ),
}


@pytest.fixture
def mcp_server():
    """Create a test FastMCP server with example tools registered."""
    server = FastMCP("TestIlographServer")
    register_example_tools(server)
    return server


class TestListExamplesTool:
    """Test cases for the list_examples tool."""

    async def test_list_all_examples(self, mcp_server):
        """Test listing all available examples."""
        with patch(
            "ilograph_mcp.tools.register_example_tools.EXAMPLES_DATABASE", MOCK_EXAMPLES_DATABASE
        ):
            async with Client(mcp_server) as client:
                result = await client.call_tool("list_examples", {})
                assert len(result) == 1
                response_data = json.loads(result[0].text)

                assert "examples" in response_data
                assert len(response_data["examples"]) == 2
                assert (
                    response_data["message"]
                    == "To get the full content of an example, use the 'fetch_example' tool with its 'example_name'."
                )
                # Check if summaries are correct
                names = {ex["name"] for ex in response_data["examples"]}
                assert "test-example-intermediate.ilograph" in names
                assert "test-example-advanced.ilograph" in names

    async def test_list_examples_by_category_found(self, mcp_server):
        """Test filtering examples by a category that exists."""
        with patch(
            "ilograph_mcp.tools.register_example_tools.EXAMPLES_DATABASE", MOCK_EXAMPLES_DATABASE
        ):
            async with Client(mcp_server) as client:
                result = await client.call_tool("list_examples", {"category": "advanced"})
                assert len(result) == 1
                response_data = json.loads(result[0].text)

                assert "examples" in response_data
                assert len(response_data["examples"]) == 1
                assert response_data["examples"][0]["name"] == "test-example-advanced.ilograph"
                assert response_data["examples"][0]["category"] == "advanced"

    async def test_list_examples_by_category_not_found(self, mcp_server):
        """Test filtering examples by a category that has no entries."""
        with patch(
            "ilograph_mcp.tools.register_example_tools.EXAMPLES_DATABASE", MOCK_EXAMPLES_DATABASE
        ):
            async with Client(mcp_server) as client:
                result = await client.call_tool("list_examples", {"category": "beginner"})
                assert len(result) == 1
                response_data = json.loads(result[0].text)

                assert "examples" not in response_data
                assert "message" in response_data
                assert "No examples found for category 'beginner'" in response_data["message"]


class TestFetchExampleTool:
    """Test cases for the fetch_example tool."""

    async def test_fetch_valid_example(self, mcp_server):
        """Test fetching a valid and existing example diagram."""
        with (
            patch(
                "ilograph_mcp.tools.register_example_tools.EXAMPLES_DATABASE",
                MOCK_EXAMPLES_DATABASE,
            ),
            patch("pathlib.Path.is_file", return_value=True),
            patch(
                "pathlib.Path.read_text", return_value="---\ntitle: Test Example Content\n---"
            ) as mock_read_text,
            patch("importlib.metadata.version", return_value="1.0.0"),
        ):

            async with Client(mcp_server) as client:
                example_name = "test-example-advanced.ilograph"
                result = await client.call_tool("fetch_example", {"example_name": example_name})
                assert len(result) == 1
                response_data = json.loads(result[0].text)

                assert response_data["name"] == example_name
                assert response_data["category"] == "advanced"
                assert "content" in response_data
                assert response_data["content"] == "---\ntitle: Test Example Content\n---"
                assert "learning_objectives" in response_data
                mock_read_text.assert_called_once()

    async def test_fetch_non_existent_example(self, mcp_server):
        """Test fetching an example name that is not in the database."""
        with patch(
            "ilograph_mcp.tools.register_example_tools.EXAMPLES_DATABASE", MOCK_EXAMPLES_DATABASE
        ):
            async with Client(mcp_server) as client:
                example_name = "non-existent-example.ilograph"
                result = await client.call_tool("fetch_example", {"example_name": example_name})
                assert len(result) == 1
                response_data = json.loads(result[0].text)

                assert response_data["error"] == "not_found"
                assert f"Example '{example_name}' not found" in response_data["message"]
                assert "available_examples" in response_data
                assert "test-example-intermediate.ilograph" in response_data["available_examples"]

    async def test_fetch_example_file_missing_on_disk(self, mcp_server):
        """Test fetching an example that is in the database but missing from disk."""
        with (
            patch(
                "ilograph_mcp.tools.register_example_tools.EXAMPLES_DATABASE",
                MOCK_EXAMPLES_DATABASE,
            ),
            patch("pathlib.Path.is_file", return_value=False) as mock_is_file,
        ):

            async with Client(mcp_server) as client:
                example_name = "test-example-intermediate.ilograph"
                result = await client.call_tool("fetch_example", {"example_name": example_name})
                assert len(result) == 1
                response_data = json.loads(result[0].text)

                assert response_data["error"] == "internal_error"
                assert "file could not be found on the server" in response_data["message"]
                mock_is_file.assert_called_once()

    async def test_fetch_example_read_io_error(self, mcp_server):
        """Test handling of an IOError when reading an example file."""
        with (
            patch(
                "ilograph_mcp.tools.register_example_tools.EXAMPLES_DATABASE",
                MOCK_EXAMPLES_DATABASE,
            ),
            patch("pathlib.Path.is_file", return_value=True),
            patch("pathlib.Path.read_text", side_effect=IOError("Disk read failed")),
        ):

            async with Client(mcp_server) as client:
                example_name = "test-example-advanced.ilograph"
                result = await client.call_tool("fetch_example", {"example_name": example_name})
                assert len(result) == 1
                response_data = json.loads(result[0].text)

                assert response_data["error"] == "internal_error"
                assert (
                    "An unexpected error occurred while reading the example file"
                    in response_data["message"]
                )


class TestToolIntegration:
    """Integration tests for the example tools."""

    async def test_all_tools_registered(self, mcp_server):
        """Test that both list_examples and fetch_example tools are registered."""
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            tool_names = {tool.name for tool in tools}

            assert "list_examples" in tool_names
            assert "fetch_example" in tool_names

            # Check metadata for one of the tools
            list_tool = next(tool for tool in tools if tool.name == "list_examples")
            assert "Lists available Ilograph example diagrams" in list_tool.description
            assert "category" in list_tool.inputSchema.get("properties", {})

    async def test_workflow_list_then_fetch(self, mcp_server):
        """Test a typical user workflow: listing examples, then fetching one."""
        with (
            patch(
                "ilograph_mcp.tools.register_example_tools.EXAMPLES_DATABASE",
                MOCK_EXAMPLES_DATABASE,
            ),
            patch("pathlib.Path.is_file", return_value=True),
            patch(
                "pathlib.Path.read_text", return_value="---\ncontent for advanced\n---"
            ) as mock_read_text,
            patch("importlib.metadata.version", return_value="1.0.0"),
        ):

            async with Client(mcp_server) as client:
                # 1. List all examples
                list_result = await client.call_tool("list_examples", {})
                list_data = json.loads(list_result[0].text)
                assert len(list_data["examples"]) == 2

                # 2. Get the name of an example from the list
                example_to_fetch = list_data["examples"][1]["name"]
                assert example_to_fetch == "test-example-advanced.ilograph"

                # 3. Fetch that specific example
                fetch_result = await client.call_tool(
                    "fetch_example", {"example_name": example_to_fetch}
                )
                fetch_data = json.loads(fetch_result[0].text)

                assert fetch_data["name"] == example_to_fetch
                assert fetch_data["category"] == "advanced"
                assert fetch_data["content"] == "---\ncontent for advanced\n---"
                mock_read_text.assert_called_once()
