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
- **✅ Diagram Validation**: Comprehensive YAML and Ilograph schema validation with detailed error messages
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

The server provides 9 main tools for accessing Ilograph documentation, specifications, examples, and validation:

1. **`fetch_documentation_tool`** - Fetches comprehensive documentation from Ilograph's official website
2. **`list_documentation_sections`** - Lists all available documentation sections with descriptions
3. **`check_documentation_health`** - Performs health checks and returns cache statistics
4. **`list_examples`** - Lists available Ilograph example diagrams with categories
5. **`fetch_example`** - Retrieves specific example diagrams with metadata and learning context
6. **`fetch_spec_tool`** - Fetches the official Ilograph specification with complete property definitions
7. **`check_spec_health`** - Performs health checks specifically on the specification service
8. **`validate_diagram_tool`** - Validates Ilograph diagram syntax and provides detailed error messages
9. **`get_validation_help`** - Provides comprehensive guidance on diagram validation and common issues

For detailed tool documentation, see [docs/TOOLS.md](docs/TOOLS.md).


## Documentation

- **[Tools Reference](docs/TOOLS.md)** - Detailed documentation for all available tools
- **[Architecture](docs/ARCHITECTURE.md)** - Technical architecture and design decisions
- **[Contributing](docs/CONTRIBUTING.md)** - Development setup and contribution guidelines

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Links

- [Ilograph Documentation](https://www.ilograph.com/docs/)
- [FastMCP Framework](https://github.com/jlowin/fastmcp)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Issue Tracker](https://github.com/QuincyMillerDev/ilograph-mcp-server/issues)

---

**Built with ❤️ for the Ilograph community**
