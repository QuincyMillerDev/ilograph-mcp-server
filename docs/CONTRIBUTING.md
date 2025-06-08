# Contributing to Ilograph MCP Server

Thank you for your interest in contributing to the Ilograph MCP Server! This guide will help you set up your development environment and understand our contribution process.

## Development Setup

### Prerequisites

- Python 3.11 or higher
- [uv](https://docs.astral.sh/uv/) package manager (recommended)

### Initial Setup

1. **Fork and Clone the Repository**
   ```bash
   git clone https://github.com/your-username/ilograph-mcp-server.git
   cd ilograph-mcp-server
   ```

2. **Install Dependencies**
   ```bash
   # Install all dependencies including development tools
   uv sync --all-extras
   ```

3. **Verify Installation**
   ```bash
   # Test that the server can be imported
   uv run python -c "from ilograph_mcp import create_server; print('✅ Installation successful')"
   ```

## Running Tests Locally

To ensure your changes pass the CI pipeline, run these commands locally:

### Core Test Suite
```bash
# Run all tests
uv run pytest

# Run tests with verbose output
uv run pytest --verbose --tb=short

# Run with coverage report
uv run pytest --cov=src/ilograph_mcp

# Run specific test file
uv run pytest tests/test_fetch_documentation_tool.py
```

### Code Formatting and Linting

**Format your code** (these commands will modify files):
```bash
# Format code with black
uv run black src/ tests/

# Sort imports with isort
uv run isort src/ tests/
```


**Check formatting** (these commands only check, same as CI):
```bash
# Check code formatting
uv run black --check --diff src/ tests/

# Check import sorting
uv run isort --check-only --diff src/ tests/

# Type checking
uv run mypy src/

# (No additional linting tools configured)
```

### Security Checks
```bash
# Check for known security vulnerabilities
uv run safety check

# Security linting
uv run bandit -r src/
```

### Integration Tests
```bash
# Test server startup and tool registration
uv run python -c "
from ilograph_mcp import create_server
from fastmcp import Client
import asyncio

async def test_tools():
    server = create_server()
    async with Client(server) as client:
        tools = await client.list_tools()
        print(f'✅ {len(tools)} tools registered successfully')

asyncio.run(test_tools())
"
```

## Project Structure

Understanding the codebase structure:

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

- **Tools**: MCP tools that agents can call for functionality
- **Core**: Business logic for content fetching and caching
- **Utils**: Shared utility functions for HTTP and markdown processing
- **Static**: Example Ilograph diagrams for reference
- **Tests**: Comprehensive test suite with mocking and integration tests

## Contribution Process

### 1. Create a Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes

Follow these guidelines:
- **FastMCP Best Practices**: Use `@mcp.tool()` decorators with proper type hints
- **Error Handling**: Implement comprehensive error handling with meaningful messages
- **Documentation**: Update docstrings and documentation for any new functionality
- **Testing**: Add tests for new features and bug fixes

### 3. Test Your Changes

Run the complete test suite locally:
```bash
# Format code
uv run black src/ tests/
uv run isort src/ tests/

# Run all checks
uv run pytest
uv run mypy src/
uv run safety check
```

### 4. Commit and Push

```bash
git add .
git commit -m "feat: add new functionality"
git push origin feature/your-feature-name
```

### 5. Submit a Pull Request

1. Create a pull request on GitHub
2. Ensure all CI checks pass
3. Request review from maintainers
4. Address any feedback

## Code Quality Standards

This project maintains high code quality through several tools:

### Code Formatting
- **Black**: Automatic code formatting
- **isort**: Import statement sorting

### Type Safety
- **mypy**: Static type checking
- **Type hints**: Required for all function signatures

### Security Scanning
- **bandit**: Security vulnerability scanning

### Testing
- **pytest**: Testing framework with async support
- **Coverage**: Minimum coverage requirements
- **Integration tests**: Real server startup and tool registration

## Adding New Tools

When adding new MCP tools:

1. **Create the tool function** in `src/ilograph_mcp/tools/`
2. **Use proper decorators**: `@mcp.tool()` with annotations
3. **Add comprehensive docstrings** (these become tool descriptions)
4. **Implement error handling** using the established patterns
5. **Add unit tests** in `tests/`
6. **Update documentation** if needed

Example tool structure:
```python
@mcp.tool(
    annotations={
        "title": "Tool Title",
        "readOnlyHint": True,
        "description": "Brief description of tool functionality"
    }
)
async def your_tool_name(parameter: str, ctx: Context) -> dict:
    """
    Detailed description of what the tool does.
    
    Args:
        parameter: Description of the parameter
        ctx: FastMCP context for logging and HTTP requests
        
    Returns:
        dict: Description of return value structure
    """
    try:
        await ctx.info(f"Processing {parameter}...")
        # Tool implementation
        return {"success": True, "data": result}
    except Exception as e:
        await ctx.error(f"Error: {str(e)}")
        return {"success": False, "error": str(e)}
```

## Getting Help

- **Issues**: Report bugs or request features on GitHub Issues
- **Discussions**: Ask questions in GitHub Discussions
- **Documentation**: Check the [documentation](../README.md) for usage examples

## Release Process

Releases are automated through GitHub Actions:
1. Changes are merged to `main` branch
2. CI/CD pipeline runs all tests and checks
3. Package is built and artifacts are created
4. Releases are tagged following semantic versioning

Thank you for contributing to the Ilograph MCP Server! 🎉 