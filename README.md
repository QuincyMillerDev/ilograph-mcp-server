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
- **Learning & Examples**: Explore curated diagram examples with detailed explanations

> **Important**: This is an **unofficial, community-driven project** and is **not affiliated with or endorsed by Ilograph LLC**. The server provides educational and development assistance by accessing publicly available Ilograph documentation and resources.

> **Caution**: The outputs and recommendations provided by the MCP server are generated dynamically and may vary based on the query and model. Users should **thoroughly review all outputs** to ensure they align with their project requirements and **verify against official Ilograph documentation** before implementation.

## Prerequisites

1. **Docker**: [Docker](https://www.docker.com/) installed and running
2. **MCP-compatible client**: Claude Desktop, VS Code, Cursor, etc.

## Quick Start
### Add to Your MCP Client

Add this configuration to your MCP client:

**VS Code**:

Add the following JSON block to your User Settings (JSON) file in VS Code. You can do this by pressing Ctrl + Shift + P and typing Preferences: Open User Settings (JSON).

More about using MCP server tools in VS Code's agent mode documentation.
```json
{
  "mcp": {
    "servers": {
      "terraform": {
        "command": "docker",
        "args": [
          "run",
          "-i",
          "--rm",
          "ghcr.io/quincymillerdev/ilograph-mcp-server:latest"
        ]
      }
    }
  }
}
```
Optionally, you can add a similar example (i.e. without the mcp key) to a file called .vscode/mcp.json in your workspace. This will allow you to share the configuration with others.
```json
{
  "servers": {
    "terraform": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "ghcr.io/quincymillerdev/ilograph-mcp-server:latest"
      ]
    }
  }
}
```

**Claude Desktop / Cursor / Jetbrains AI Assistant**:
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



## Contributing

Contributions are welcome! This project needs:

- 🐛 **Bug fixes** - Always appreciated!
- 📚 **Documentation improvements** - Help make things clearer  
- ✨ **New tools** - Add more Ilograph functionality
- 🔧 **Code quality** - Better error handling, etc.

**📖 See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for detailed development setup, testing, and submission guidelines.**

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

## Need Help?

- **Tool Usage**: See the available tools in the table above
- **Issues**: [GitHub Issues](https://github.com/QuincyMillerDev/ilograph-mcp-server/issues)
- **Questions**: [GitHub Discussions](https://github.com/QuincyMillerDev/ilograph-mcp-server/discussions)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Legal Disclaimer

**This project is not affiliated with, endorsed by, or connected to Ilograph LLC.** This is an independent, community-driven tool that accesses publicly available Ilograph documentation and resources for educational and development purposes.

- The Ilograph name and related trademarks are property of Ilograph LLC
- This tool accesses publicly available documentation under fair use principles
- Users should refer to official Ilograph documentation for authoritative information
- No commercial relationship exists between this project and Ilograph LLC

## Links

- [Ilograph Official Website](https://www.ilograph.com/)
- [Ilograph Documentation](https://www.ilograph.com/docs/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [FastMCP Framework](https://github.com/jlowin/fastmcp)

---

**Built with ❤️ for the Ilograph community**
