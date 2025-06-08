"""
Example Diagram Tools for Ilograph MCP Server.

This module provides tools for accessing static Ilograph example diagrams.
It allows AI agents to fetch fully-formed diagrams for learning and reference,
complete with metadata about the patterns and concepts they demonstrate.
"""

import logging
from pathlib import Path
from typing import Optional, List, Dict, Any, Literal

from fastmcp import FastMCP, Context
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Base path for example files
EXAMPLES_DIR = Path(__file__).parent.parent / "static" / "examples"

class ExampleMetadata(BaseModel):
    """Defines the metadata structure for an Ilograph example."""
    name: str
    category: Literal["beginner", "intermediate", "advanced"]
    description: str
    learning_objectives: List[str] = Field(default_factory=list)
    patterns_demonstrated: List[str] = Field(default_factory=list)

    @property
    def file_path(self) -> Path:
        """Returns the full path to the example file."""
        return EXAMPLES_DIR / self.name

# In-memory database of example diagrams and their metadata.
# This acts as a manifest, providing rich context for each example.
EXAMPLES_DATABASE: Dict[str, ExampleMetadata] = {
    "serverless-on-aws.ilograph": ExampleMetadata(
        name="serverless-on-aws.ilograph",
        category="intermediate",
        description="A comprehensive diagram of a serverless web application architecture on AWS, using services like Lambda, API Gateway, S3, and DynamoDB.",
        learning_objectives=[
            "Understand how to model serverless architectures.",
            "Learn the relationships between API Gateway, Lambda, and DynamoDB.",
            "See how to represent S3 buckets for static content hosting."
        ],
        patterns_demonstrated=["Serverless", "AWS", "API Gateway", "Lambda", "DynamoDB", "Microservices"]
    ),
    "stack-overflow-architecture-2016.ilograph": ExampleMetadata(
        name="stack-overflow-architecture-2016.ilograph",
        category="advanced",
        description="The 2016 architecture of Stack Overflow, showcasing a high-traffic, resilient web application with a mix of .NET technologies, Redis, and SQL Server.",
        learning_objectives=[
            "Analyze a real-world, high-scale web architecture.",
            "Understand patterns for redundancy, caching, and load balancing.",
            "Learn to model complex interactions between various services and data stores."
        ],
        patterns_demonstrated=["Web Architecture", "High Availability", "Caching", "Load Balancing", "SQL", "Redis"]
    ),
    "aws-distributed-load-testing.ilograph": ExampleMetadata(
        name="aws-distributed-load-testing.ilograph",
        category="advanced",
        description="A sophisticated AWS architecture for a distributed load testing solution, featuring containerized tasks, event-driven flows, and detailed networking.",
        learning_objectives=[
            "Model complex, event-driven systems on AWS.",
            "Understand how to represent container orchestration with Fargate.",
            "Learn advanced networking concepts like VPCs, subnets, and security groups."
        ],
        patterns_demonstrated=["Cloud Architecture", "Distributed Systems", "Event-Driven", "AWS Fargate", "Networking", "Scalability"]
    ),
}

def _get_example_summary(metadata: ExampleMetadata) -> Dict[str, Any]:
    """Returns a concise summary of an example."""
    return metadata.model_dump(include={'name', 'category', 'description'})


def register_example_tools(mcp: FastMCP) -> None:
    """Register the example diagram tools with the FastMCP server."""

    @mcp.tool(
        name="list_examples",
        annotations={
            "title": "List Available Example Diagrams",
            "readOnlyHint": True,
            "description": "Lists available Ilograph example diagrams with their categories and descriptions."
        }
    )
    async def list_examples_tool(
        category: Optional[Literal["beginner", "intermediate", "advanced"]] = None
    ) -> Dict[str, Any]:
        """
        Lists available Ilograph example diagrams, optionally filtering by category.

        Args:
            category: Filter examples by complexity ('beginner', 'intermediate', 'advanced').

        Returns:
            A dictionary containing a list of available examples and a message guiding the user.
        """
        examples_to_list = EXAMPLES_DATABASE.values()
        if category:
            examples_to_list = [ex for ex in examples_to_list if ex.category == category]

        if not examples_to_list:
            return {
                "message": f"No examples found for category '{category}'. Try again without a category to see all examples."
            }

        return {
            "examples": [_get_example_summary(ex) for ex in examples_to_list],
            "message": "To get the full content of an example, use the 'fetch_example' tool with its 'example_name'."
        }

    @mcp.tool(
        name="fetch_example",
        annotations={
            "title": "Get Example Diagram",
            "readOnlyHint": True,
            "description": "Retrieves a specific Ilograph example diagram with its content and rich metadata."
        }
    )
    async def fetch_example_tool(example_name: str, ctx: Context) -> Dict[str, Any]:
        """
        Retrieves a static example diagram with its content and learning context.

        Args:
            example_name: The filename of the example to fetch (e.g., 'serverless-on-aws.ilograph').

        Returns:
            A dictionary containing the example's content, metadata, learning objectives, and patterns.
        """
        await ctx.info(f"Attempting to fetch example: {example_name}")
        metadata = EXAMPLES_DATABASE.get(example_name)

        if not metadata:
            await ctx.error(f"Example '{example_name}' not found.")
            available = ", ".join(EXAMPLES_DATABASE.keys())
            return {
                "error": "not_found",
                "message": f"Example '{example_name}' not found. Use the 'list_examples' tool to see available examples.",
                "available_examples": available.split(", ")
            }

        file_path = metadata.file_path
        if not file_path.is_file():
            await ctx.error(f"Example file not found on disk: {file_path}")
            return {
                "error": "internal_error",
                "message": "The example file could not be found on the server, even though it is listed in the database."
            }

        try:
            content = file_path.read_text(encoding="utf-8")
            await ctx.info(f"Successfully read example file: {example_name}")
            response = metadata.model_dump()
            response["content"] = content
            return response
        except Exception as e:
            await ctx.error(f"Failed to read example file '{example_name}': {e}")
            logger.exception(f"Error reading example file {file_path}")
            return {
                "error": "internal_error",
                "message": f"An unexpected error occurred while reading the example file: {e}"
            }


def get_example_tool_info() -> dict:
    """Get information about the example tools for registration."""
    return {
        "name": "example_tools",
        "description": "Provides access to static Ilograph example diagrams with rich metadata.",
        "tools": [
            "list_examples",
            "fetch_example"
        ]
    } 