"""
Examples resource for the Ilograph MCP Server.

This module provides access to static .ilograph example files that demonstrate
various Ilograph diagram patterns and use cases.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List

from fastmcp import FastMCP

logger = logging.getLogger(__name__)

# Get the path to the examples directory
EXAMPLES_DIR = Path(__file__).parent.parent / "static" / "examples"

# Enhanced example metadata for comprehensive categorization and filtering
EXAMPLE_METADATA = {
    "serverless-on-aws.ilograph": {
        "title": "Serverless on AWS",
        "description": "Modern serverless application demonstrating event-driven architecture with managed AWS services including Lambda, API Gateway, and DynamoDB",
        "category": "serverless",
        "cloud_provider": "aws",
        "complexity": "beginner",
        "architecture_patterns": ["serverless", "event-driven", "api-first", "microservices"],
        "services": ["lambda", "api-gateway", "dynamodb", "s3", "cognito", "cloudfront", "ses"],
        "use_cases": ["serverless", "microservices", "event-driven", "web-api", "saas-application"],
        "learning_objectives": ["Serverless patterns", "AWS Lambda functions", "API design", "NoSQL databases", "CDN integration"],
        "estimated_components": 25,
        "perspectives_count": 3
    },
    "aws-distributed-load-testing.ilograph": {
        "title": "AWS Distributed Load Testing",
        "description": "Complete distributed load testing architecture on AWS using Lambda, ECS, and managed services for scalable performance testing",
        "category": "distributed-testing",
        "cloud_provider": "aws",
        "complexity": "intermediate",
        "architecture_patterns": ["microservices", "event-driven", "managed-services", "containerization"],
        "services": ["lambda", "ecs", "s3", "cloudformation", "sqs", "cloudwatch", "ecr", "iam"],
        "use_cases": ["load-testing", "performance-testing", "aws-architecture", "devops", "monitoring"],
        "learning_objectives": ["AWS service integration", "distributed architectures", "infrastructure as code", "container orchestration"],
        "estimated_components": 35,
        "perspectives_count": 2
    },
    "stack-overflow-architecture-2016.ilograph": {
        "title": "Stack Overflow Architecture (2016)",
        "description": "Physical datacenter architecture showing Stack Overflow's high-availability infrastructure with detailed hardware and software stack",
        "category": "datacenter",
        "cloud_provider": "on-premises",
        "complexity": "advanced",
        "architecture_patterns": ["high-availability", "load-balancing", "database-clustering", "cdn-integration"],
        "services": ["sql-server", "redis", "elasticsearch", "iis", "haproxy", "fastly"],
        "use_cases": ["web-application", "high-availability", "database-architecture", "datacenter-design", "enterprise-scale"],
        "learning_objectives": ["Physical infrastructure", "high availability patterns", "database scaling", "load balancing", "network architecture"],
        "estimated_components": 50,
        "perspectives_count": 4
    }
}


def register_examples_resources(mcp: FastMCP) -> None:
    """Register all examples-related resources with the FastMCP server."""
    
    @mcp.resource("ilograph://examples")
    async def get_examples_catalog() -> str:
        """
        Comprehensive catalog of all available Ilograph example diagrams.
        
        Provides complete discoverability for MCP clients including metadata,
        categorization, and individual resource URIs for each example.
        
        Returns:
            JSON string containing complete examples catalog with:
            - List of all examples with rich metadata
            - Filtering dimensions (categories, cloud providers, complexity levels)
            - Individual resource URIs for each example
            - Learning progression information
        """
        try:
            if not EXAMPLES_DIR.exists():
                logger.error(f"Examples directory not found: {EXAMPLES_DIR}")
                return json.dumps({
                    "error": "Examples directory not found",
                    "available_examples": []
                })
            
            examples = []
            for file_path in EXAMPLES_DIR.glob("*.ilograph"):
                filename = file_path.name
                metadata = EXAMPLE_METADATA.get(filename, {
                    "title": filename.replace(".ilograph", "").replace("-", " ").title(),
                    "description": f"Ilograph diagram example: {filename}",
                    "category": "general",
                    "cloud_provider": "unknown",
                    "complexity": "unknown",
                    "services": [],
                    "use_cases": []
                })
                
                examples.append({
                    "filename": filename,
                    "resource_uri": f"ilograph://examples/{filename}",
                    "size_bytes": file_path.stat().st_size,
                    **metadata
                })
            
            # Sort by complexity and then by title
            complexity_order = {"beginner": 0, "intermediate": 1, "advanced": 2, "unknown": 3}
            examples.sort(key=lambda x: (
                complexity_order.get(x["complexity"], 999), 
                x["title"]
            ))
            
            # Extract all unique values for filtering
            all_categories = list(set(ex["category"] for ex in examples))
            all_cloud_providers = list(set(ex["cloud_provider"] for ex in examples))
            all_complexity_levels = list(set(ex["complexity"] for ex in examples))
            all_architecture_patterns = list(set(pattern for ex in examples for pattern in ex.get("architecture_patterns", [])))
            all_services = list(set(service for ex in examples for service in ex.get("services", [])))
            all_use_cases = list(set(use_case for ex in examples for use_case in ex.get("use_cases", [])))
            
            result = {
                "examples": examples,
                "total_count": len(examples),
                "filtering_dimensions": {
                    "categories": sorted(all_categories),
                    "cloud_providers": sorted(all_cloud_providers),
                    "complexity_levels": ["beginner", "intermediate", "advanced"],  # Ordered progression
                    "architecture_patterns": sorted(all_architecture_patterns),
                    "services": sorted(all_services),
                    "use_cases": sorted(all_use_cases)
                },
                "learning_progression": {
                    "beginner": [ex for ex in examples if ex["complexity"] == "beginner"],
                    "intermediate": [ex for ex in examples if ex["complexity"] == "intermediate"],
                    "advanced": [ex for ex in examples if ex["complexity"] == "advanced"]
                }
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            logger.error(f"Error listing examples: {e}")
            return json.dumps({
                "error": f"Failed to list examples: {str(e)}",
                "available_examples": []
            })
    
    @mcp.resource("ilograph://examples/{filename}")
    async def get_example_content(filename: str) -> str:
        """
        Get specific Ilograph example diagram content and metadata.
        
        Provides the complete .ilograph file content along with comprehensive
        metadata including learning objectives, architecture patterns, and 
        categorization information.
        
        Args:
            filename: The filename of the example (e.g., 'serverless-on-aws.ilograph')
                     Can be provided with or without the .ilograph extension
            
        Returns:
            JSON string containing:
            - Raw .ilograph file content
            - Complete metadata and categorization
            - File statistics (size, line count)
            - Learning context and objectives
        """
        try:
            # Sanitize filename to prevent directory traversal
            if ".." in filename or "/" in filename or "\\" in filename:
                return json.dumps({
                    "error": "Invalid filename: path traversal not allowed",
                    "filename": filename
                })
            
            if not filename.endswith(".ilograph"):
                filename = f"{filename}.ilograph"
            
            file_path = EXAMPLES_DIR / filename
            
            if not file_path.exists():
                available_files = [f.name for f in EXAMPLES_DIR.glob("*.ilograph")]
                return json.dumps({
                    "error": f"Example file not found: {filename}",
                    "available_files": available_files
                })
            
            content = file_path.read_text(encoding="utf-8")
            metadata = EXAMPLE_METADATA.get(filename, {
                "title": filename.replace(".ilograph", "").replace("-", " ").title(),
                "description": f"Ilograph diagram example: {filename}",
                "category": "general",
                "cloud_provider": "unknown",
                "complexity": "unknown",
                "architecture_patterns": [],
                "services": [],
                "use_cases": [],
                "learning_objectives": [],
                "estimated_components": 0,
                "perspectives_count": 1
            })
            
            result = {
                "filename": filename,
                "resource_uri": f"ilograph://examples/{filename}",
                "content": content,
                "metadata": metadata,
                "file_stats": {
                    "size_bytes": len(content.encode("utf-8")),
                    "line_count": len(content.splitlines()),
                    "estimated_components": metadata.get("estimated_components", 0),
                    "perspectives_count": metadata.get("perspectives_count", 1)
                },
                "learning_context": {
                    "complexity": metadata.get("complexity", "unknown"),
                    "learning_objectives": metadata.get("learning_objectives", []),
                    "architecture_patterns": metadata.get("architecture_patterns", []),
                    "related_services": metadata.get("services", [])
                }
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            logger.error(f"Error reading example file {filename}: {e}")
            return json.dumps({
                "error": f"Failed to read example file: {str(e)}",
                "filename": filename
            }) 