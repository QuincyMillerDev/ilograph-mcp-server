# Ilograph MCP Server

> **⚠️ Important Note (2025):** Most MCP clients (Cursor, GitHub Copilot, etc.) currently only support MCP **tools**, not resources or prompts. This server is designed with tool-first architecture to ensure compatibility with all current MCP clients.

A FastMCP server that provides AI agents with comprehensive access to Ilograph documentation and guidance for creating accurate, valid Ilograph diagrams. The server acts as a dynamic domain expert, fetching live content from official Ilograph sources.

[![CI/CD Pipeline](https://github.com/your-org/ilograph-mcp-server/actions/workflows/ci.yml/badge.svg)](https://github.com/QuincyMillerDev/ilograph-mcp-server/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastMCP](https://img.shields.io/badge/FastMCP-2.7.0+-green.svg)](https://github.com/jlowin/fastmcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- **📚 Live Documentation Access**: Fetches up-to-date documentation from official Ilograph sources
- **🔍 Comprehensive Section Coverage**: Access to all major Ilograph concepts (resources, perspectives, contexts, etc.)
- **⚡ Intelligent Caching**: TTL-based caching with fallback strategies for optimal performance
- **🛠️ Tool-First Design**: Compatible with all current MCP clients (Cursor, GitHub Copilot, etc.)
- **📋 Example Library**: Curated collection of real-world Ilograph diagrams
- **🔄 Health Monitoring**: Built-in service health checks and status reporting

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/ilograph-mcp-server.git
cd ilograph-mcp-server

# Install with uv (recommended)
uv sync

# Or with pip
pip install -e .
```

### Running the Server

```bash
# Using uv
uv run python -m ilograph_mcp.server

# Or using the installed script
ilograph-mcp

# Or directly
python src/ilograph_mcp/server.py
```

### Using as a Library

```python
from ilograph_mcp import create_server

# Create and run the server
mcp = create_server()
mcp.run()
```

## Available Tools

The server provides comprehensive tools for accessing Ilograph documentation and examples:

### 1. `fetch_documentation_tool`
Fetches comprehensive documentation from Ilograph's official website.

**Parameters:**
- `section` (str): Documentation section to fetch

**Supported Sections:**
- `resources` - Resource tree organization, hierarchies, instanceOf patterns
- `relation-perspectives` - Arrow connections, from/to properties, routing
- `sequence-perspectives` - Time-based diagrams with steps, bidirectional flows
- `references` - Resource reference patterns and advanced referencing
- `advanced-references` - Complex reference scenarios and usage patterns
- `resource-sizes-and-positions` - Layout control, resource sizing, visual hierarchy
- `parent-overrides` - Resource parent overrides in perspectives
- `perspectives-other-properties` - Additional perspective properties and options
- `icons` - Icon system with iconStyle, icon paths, and categorization
- `walkthroughs` - Interactive step-by-step guides through diagrams
- `contexts` - Multiple context views with roots, extends inheritance
- `imports` - Namespace management with from/namespace properties
- `markdown` - Rich text support in descriptions, notes, and diagram text
- `tutorial` - Complete tutorial for learning Ilograph diagram creation

### 2. `list_documentation_sections`
Lists all available documentation sections with descriptions and usage examples.

### 3. `check_documentation_health`
Performs health checks on the documentation service and returns cache statistics.

### 4. `list_examples`
Lists available Ilograph example diagrams with their categories and descriptions.

**Parameters:**
- `category` (optional): Filter examples by complexity ('beginner', 'intermediate', 'advanced')

**Available Examples:**
- `serverless-on-aws.ilograph` - Serverless web application architecture on AWS (intermediate)
- `stack-overflow-architecture-2016.ilograph` - High-traffic web application with .NET, Redis, SQL Server (advanced)
- `aws-distributed-load-testing.ilograph` - Distributed load testing solution with containerized tasks (advanced)

### 5. `fetch_example`
Retrieves a specific Ilograph example diagram with its content and rich metadata.

**Parameters:**
- `example_name` (str): The filename of the example to fetch (e.g., 'serverless-on-aws.ilograph')

**Returns:**
- Complete diagram content
- Learning objectives
- Patterns demonstrated
- Category and description

> **Note:** Additional tools for validation, icon search, and specification reference are planned for future releases.

## Example Usage

```python
from fastmcp import Client
from ilograph_mcp import create_server

async def example_usage():
    mcp = create_server()
    
    async with Client(mcp) as client:
        # List available sections
        sections = await client.call_tool("list_documentation_sections", {})
        print("Available sections:", sections)
        
        # Fetch specific documentation
        docs = await client.call_tool("fetch_documentation_tool", {
            "section": "resources"
        })
        print("Documentation:", docs)
        
        # List example diagrams
        examples = await client.call_tool("list_examples", {
            "category": "intermediate"
        })
        print("Available examples:", examples)
        
        # Fetch specific example
        example = await client.call_tool("fetch_example", {
            "example_name": "serverless-on-aws.ilograph"
        })
        print("Example diagram:", example)
        
        # Check service health
        health = await client.call_tool("check_documentation_health", {})
        print("Health status:", health)
```

## Architecture

```
src/ilograph_mcp/
├── __init__.py              # Package exports
├── server.py                # Main FastMCP server
├── core/
│   ├── fetcher.py          # HTTP content fetching
│   └── cache.py            # TTL-based caching system
├── tools/
│   ├── fetch_documentation_tool.py  # Documentation tools
│   └── register_example_tools.py    # Example diagram tools
├── utils/
│   ├── http_client.py      # HTTP client with retry logic
│   └── markdown_converter.py       # HTML to Markdown conversion
└── static/
    └── examples/
        ├── aws-distributed-load-testing.ilograph
        ├── stack-overflow-architecture-2016.ilograph
        └── serverless-on-aws.ilograph
```

## Development

### Setup Development Environment

```bash
# Install development dependencies
uv sync --extra dev

# Run tests
uv run pytest

# Format code
uv run black src/ tests/
uv run isort src/ tests/

# Type checking
uv run mypy src/
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/ilograph_mcp

# Run specific test file
uv run pytest tests/test_fetch_documentation_tool.py
```

### Project Structure

- **Tools**: MCP tools that agents can call for functionality
- **Core**: Business logic for content fetching and caching
- **Utils**: Shared utility functions for HTTP and markdown processing
- **Static**: Example Ilograph diagrams for reference
- **Tests**: Comprehensive test suite with mocking and integration tests

## Configuration

### Running Options

The server can be run with different transport protocols:

```bash
# Default: STDIO transport
python src/ilograph_mcp/server.py

# With specific transport (would require code modification)
# mcp.run(transport="streamable-http", host="127.0.0.1", port=8000)
```

### MCP Transport Protocols

The server supports FastMCP transport protocols:

- **stdio**: Standard for Cursor and most MCP clients (default)
- **Streamable HTTP**: For web-based integrations
- **SSE**: Server-Sent Events (deprecated, use Streamable HTTP instead)

## Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature-name`
3. **Make your changes** following the project conventions
4. **Add tests** for new functionality
5. **Run the test suite**: `uv run pytest`
6. **Submit a pull request**

### Code Quality

This project uses several tools for code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **mypy**: Type checking
- **pytest**: Testing framework

All checks must pass before merging.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Links

- [Ilograph Documentation](https://www.ilograph.com/docs/)
- [FastMCP Framework](https://github.com/jlowin/fastmcp)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Issue Tracker](https://github.com/your-org/ilograph-mcp-server/issues)

## Roadmap

### Current Status (v0.1.0)
- ✅ Documentation fetching tools
- ✅ Caching system
- ✅ Health monitoring
- ✅ Example diagram library

### Planned Features
- 🔲 Diagram syntax validation
- 🔲 Icon search and recommendation
- 🔲 Specification reference tool
- 🔲 Best practices guidance
- 🔲 Template generation

---

**Built with ❤️ for the Ilograph community**
