# 🎯 Ilograph MCP Server

The Ilograph MCP Server is a [Model Context Protocol (MCP)](https://modelcontextprotocol.io/introduction) server that provides AI agents with comprehensive access to Ilograph documentation, validation tools, and diagram creation guidance. Transform complex architecture documentation with intelligent assistance.

[![CI](https://github.com/QuincyMillerDev/ilograph-mcp-server/actions/workflows/ci.yml/badge.svg)](https://github.com/QuincyMillerDev/ilograph-mcp-server/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastMCP](https://img.shields.io/badge/FastMCP-2.7.0+-green.svg)](https://github.com/jlowin/fastmcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Use Cases

- **Automated Diagram Creation**: Generate Ilograph diagrams through natural language descriptions
- **Real-time Validation**: Validate existing diagrams with detailed error analysis and suggestions
- **Documentation Access**: Get instant access to comprehensive Ilograph documentation and best practices
- **Architecture Guidance**: Receive expert recommendations for diagram structure and icon selection
- **Learning & Examples**: Explore curated diagram examples with detailed explanations

> **Important**: This is an **unofficial, community-driven project** and is **not affiliated with or endorsed by Ilograph LLC**. The server provides educational and development assistance by accessing publicly available Ilograph documentation and resources.

> **Caution**: The outputs and recommendations provided by the MCP server are generated dynamically and may vary based on the query and model. Users should **thoroughly review all outputs** to ensure they align with their project requirements and **verify against official Ilograph documentation** before implementation.

## Prerequisites

1. **Docker**: To run the server in a container, you will need [Docker](https://www.docker.com/) installed and running.
2. **Python 3.11+**: For local installation (alternative to Docker)
3. **MCP-compatible client**: Such as Claude Desktop, VS Code with Copilot, or Cursor

## Quick Start

**Prerequisites**: [Docker](https://www.docker.com/) installed and running

### Add to Your MCP Client

Add this configuration to your MCP client:

**VS Code** (Settings → User Settings JSON or `.vscode/mcp.json`):
```json
{
  "mcp": {
    "servers": {
      "ilograph": {
        "command": "docker",
        "args": ["run", "-i", "--rm", "ghcr.io/quincymillerdev/ilograph-mcp-server:latest"]
      }
    }
  }
}
```

**Claude Desktop**:
```json
{
  "mcpServers": {
    "ilograph": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "ghcr.io/quincymillerdev/ilograph-mcp-server:latest"]
    }
  }
}
```

**Cursor**:
```json
{
  "mcpServers": {
    "ilograph": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "ghcr.io/quincymillerdev/ilograph-mcp-server:latest"]
    }
  }
}
```

That's it! 🎉

## Tool Configuration

### Available Tools

The following tools are available for comprehensive Ilograph workflow support:

| Category | Tool | Description |
|----------|------|-------------|
| **Documentation** | `fetch_documentation_tool` | Fetches comprehensive documentation from Ilograph's official sources with intelligent caching |
| **Documentation** | `list_documentation_sections` | Lists all available documentation sections with descriptions and coverage areas |
| **Documentation** | `check_documentation_health` | Performs health checks and returns cache statistics for documentation service |
| **Specification** | `fetch_spec_tool` | Fetches the official Ilograph specification with complete property definitions and types |
| **Specification** | `check_spec_health` | Performs health checks specifically on the specification service connectivity |
| **Examples** | `list_examples` | Lists available Ilograph example diagrams categorized by complexity and use case |
| **Examples** | `fetch_example` | Retrieves specific example diagrams with metadata, learning context, and explanations |
| **Validation** | `validate_diagram_tool` | Validates Ilograph diagram syntax and provides detailed error messages with suggestions |
| **Validation** | `get_validation_help` | Provides comprehensive guidance on diagram validation and common issues resolution |
| **Icons** | `search_icons_tool` | Searches the live Ilograph icon catalog with semantic matching and provider filtering |
| **Icons** | `list_icon_providers_tool` | Lists all available icon providers (AWS, Azure, GCP, etc.) and their service categories |

### What You Can Do

**"Create an AWS microservices architecture diagram"**
→ Generates complete Ilograph diagram with proper AWS icons, relationships, and best practices

**"Validate my existing Ilograph diagram and suggest improvements"** 
→ Provides detailed error analysis, performance suggestions, and architecture pattern recommendations

**"Show me examples of serverless architectures"**
→ Returns curated examples with explanations, learning objectives, and implementation patterns

**"Find icons for Kubernetes components"**
→ Returns relevant icons with usage examples and provider information

**"Explain Ilograph perspectives and how to use them"**
→ Provides comprehensive documentation with examples and best practices

## Development Setup

Want to contribute or run locally?

```bash
# Clone and build
git clone https://github.com/QuincyMillerDev/ilograph-mcp-server.git
cd ilograph-mcp-server
docker build -t ilograph-mcp-local .

# Use local build
{
  "mcpServers": {
    "ilograph": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "ilograph-mcp-local"]
    }
  }
}
```



## Development

### Prerequisites
- **Python 3.11+** (check [pyproject.toml](./pyproject.toml) for specific version)
- **uv** (recommended) or **pip** for dependency management
- **Docker** (optional, for container builds)

### Development Setup
```bash
# Clone and setup
git clone https://github.com/QuincyMillerDev/ilograph-mcp-server.git
cd ilograph-mcp-server

# Install dependencies
uv sync

# Run the server locally
uv run python -m ilograph_mcp.server
```

### Running Tests
```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=ilograph_mcp

# Run specific test categories
uv run pytest -m unit
uv run pytest -m integration
```

### Available Scripts
```bash
# Development server
uv run python -m ilograph_mcp.server

# Code formatting
uv run black .
uv run isort .

# Type checking
uv run mypy .

# Security scanning
uv run bandit -r src/

# Build package
uv build
```

## Features

- **📚 Live Documentation Access**: Fetches up-to-date documentation from official Ilograph sources
- **🔍 Comprehensive Section Coverage**: Access to all major Ilograph concepts (resources, perspectives, contexts, etc.)
- **✅ Advanced Diagram Validation**: YAML and Ilograph schema validation with detailed error messages and suggestions
- **⚡ Intelligent Caching**: TTL-based caching with fallback strategies for optimal performance
- **🛠️ Tool-First Design**: Compatible with all current MCP clients (Cursor, Claude Desktop, VS Code, etc.)
- **📋 Curated Example Library**: Real-world Ilograph diagrams with learning context and explanations
- **🎨 Smart Icon Search**: Semantic search through Ilograph's icon catalog with provider filtering
- **🔄 Health Monitoring**: Built-in service health checks and status reporting
- **🏗️ Architecture Pattern Detection**: Identifies common patterns and provides optimization suggestions

## Documentation

- **[Tools Reference](docs/TOOLS.md)** - Detailed documentation for all available tools and their usage
- **[Architecture](docs/ARCHITECTURE.md)** - Technical architecture, design decisions, and system overview
- **[Contributing](docs/CONTRIBUTING.md)** - Development setup, guidelines, and contribution process

## Contributing

This is a **community-driven side project** - contributions are welcome! 

### Quick Start for Contributors

1. **Fork** the repository
2. **Clone** your fork: `git clone https://github.com/your-username/ilograph-mcp-server.git`
3. **Install**: `cd ilograph-mcp-server && uv sync`
4. **Test**: `uv run python -m ilograph_mcp.server`
5. **Make changes** and test locally
6. **Submit a Pull Request**

### What We're Looking For

- 🐛 **Bug fixes** - Always appreciated!
- 📚 **Documentation improvements** - Help make things clearer
- ✨ **New Ilograph tools** - Add more functionality
- 🔧 **Code quality** - Refactoring, type hints, etc.

### Before Contributing

- Check [existing issues](https://github.com/QuincyMillerDev/ilograph-mcp-server/issues) first
- For major changes, open an issue to discuss
- Keep changes focused and atomic
- Test your changes locally

**Note**: This is a personal side project, so response times may vary. Thanks for understanding!

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Legal Disclaimer

**This project is not affiliated with, endorsed by, or connected to Ilograph LLC.** This is an independent, community-driven tool that accesses publicly available Ilograph documentation and resources for educational and development purposes.

- The Ilograph name and related trademarks are property of Ilograph LLC
- This tool accesses publicly available documentation under fair use principles
- Users should refer to official Ilograph documentation for authoritative information
- No commercial relationship exists between this project and Ilograph LLC

## Support

- **Bug Reports**: [GitHub Issues](https://github.com/QuincyMillerDev/ilograph-mcp-server/issues)
- **Feature Requests**: [GitHub Issues](https://github.com/QuincyMillerDev/ilograph-mcp-server/issues)
- **Questions & Discussions**: [GitHub Discussions](https://github.com/QuincyMillerDev/ilograph-mcp-server/discussions)
- **Documentation**: [docs/](docs/) directory

## Links

- [Ilograph Official Website](https://www.ilograph.com/)
- [Ilograph Documentation](https://www.ilograph.com/docs/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [FastMCP Framework](https://github.com/jlowin/fastmcp)

---

**Built with ❤️ for the Ilograph community**
