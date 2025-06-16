# Contributing Guide

Thanks for your interest in contributing! This guide covers the development workflow.

## Development Setup

### Prerequisites
- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager

### Getting Started

```bash
# Fork and clone
git clone https://github.com/your-username/ilograph-mcp-server.git
cd ilograph-mcp-server

# Install dependencies
uv sync

# Verify setup
uv run python -c "from ilograph_mcp import create_server; print('✅ Setup successful')"
```

## Development Workflow

### Testing

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test
uv run pytest tests/test_fetch_documentation_tool.py
```

### Code Quality

```bash
# Format code (required before PR)
uv run black src/ tests/
uv run isort src/ tests/

# Type checking
uv run mypy src/

# Security scan
uv run bandit -r src/
```

### Testing the Server

```bash
# Start server locally (for testing)
uv run python -m ilograph_mcp

# Test tool registration
uv run python -c "
from ilograph_mcp import create_server
from fastmcp import Client
import asyncio

async def test():
    server = create_server()
    async with Client(server) as client:
        tools = await client.list_tools()
        print(f'✅ {len(tools)} tools registered')

asyncio.run(test())
"
```

## Contribution Guidelines

### Making Changes

1. **Create a branch**: `git checkout -b feature/your-feature`
2. **Make your changes** with proper error handling
3. **Add tests** for new functionality
4. **Update docstrings** for new tools
5. **Run quality checks** (formatting, tests, type checking)
6. **Submit PR** with clear description

### Adding New Tools

When adding MCP tools:
- Use `@mcp.tool()` decorator
- Add comprehensive docstrings
- Include proper type hints
- Add corresponding tests
- Update the tools table in README.md

### Code Style

- Use `black` for formatting
- Sort imports with `isort`
- Add type hints to function signatures
- Write descriptive docstrings
- Handle errors gracefully with meaningful messages

## Project Structure

```
src/ilograph_mcp/
├── server.py           # Main FastMCP server
├── tools/             # MCP tool implementations
├── core/              # Core business logic
├── utils/             # Shared utilities
└── static/examples/   # Example diagrams
```

## Need Help?

- Check existing issues first
- For major changes, open an issue to discuss
- Ask questions in GitHub Discussions

---

**Keep contributions focused and well-tested!** 🚀 