# Ilograph MCP Server

A FastMCP server that provides AI agents (like Cursor) with comprehensive context and tools to create accurate, valid Ilograph diagrams. The server acts as a domain expert for Ilograph syntax, best practices, and validation.

## Features

- **Syntax Validation**: Validate Ilograph markup syntax against the official specification
- **Comprehensive Error Reporting**: Detailed errors, warnings, and suggestions
- **Icon Catalog**: Access to complete Ilograph icon library with search capabilities
- **Best Practices**: Curated guidance for creating effective diagrams
- **Template Library**: Pre-built templates for common architectures (coming soon)

## Architecture

The project follows a modular architecture with clear separation of concerns:

```
src/ilograph_mcp/
├── __init__.py              # Package initialization
├── server.py                # Main FastMCP server setup
├── tools/                   # Interactive capabilities (MCP tools)
│   ├── __init__.py
│   └── validation.py        # Syntax validation tool
├── resources/               # Static context provision (MCP resources)
│   └── __init__.py
├── data/                    # Data management and validation logic
│   ├── __init__.py
│   ├── validator.py         # Core validation engine
│   └── loader.py            # Content loading utilities
└── utils/                   # Utility functions
    └── __init__.py
```

## Installation

### Development Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd ilograph-mcp-server
```

2. Install dependencies with uv:
```bash
uv sync
```

3. Install development dependencies:
```bash
uv sync --extra dev
```

### Usage

#### Running the Server

```bash
# Using uv
uv run main.py

# Or directly with Python
python main.py
```

#### Using as a Library

```python
from ilograph_mcp import create_server

mcp = create_server()
mcp.run()
```

## MCP Tools

### validate_ilograph_syntax

Validates Ilograph markup syntax and returns detailed feedback.

**Parameters:**
- `diagram_code` (str): The Ilograph YAML/markup code to validate

**Returns:**
```json
{
  "valid": true,
  "errors": [],
  "warnings": [],
  "suggestions": []
}
```

**Example Usage:**
```python
from fastmcp import Client
from ilograph_mcp import create_server

async def validate_diagram():
    mcp = create_server()
    client = Client(mcp)
    
    async with client:
        result = await client.call_tool("validate_ilograph_syntax", {
            "diagram_code": """
resources:
  - name: Users
    color: Blue
perspectives:
  - name: Overview
    relations:
      - from: Users
        to: System
"""
        })
        print(result)
```

## User Experience Flow

The server is designed to support the following primary use cases:

### 1. Generate New Diagram
1. User: "Create sequence diagram showing S3 → API → Frontend"
2. Cursor: Analyzes user's code context
3. Cursor: Uses MCP server to validate and enhance the generated diagram
4. Cursor: Returns valid Ilograph markup to user

### 2. Validate Existing Diagram
1. User: Provides Ilograph code for review
2. Cursor: Uses validation tool to check syntax
3. Cursor: Suggests improvements using the validation feedback

### 3. Enhance Diagram  
1. User: "Add proper icons to this diagram"
2. Cursor: Uses icon recommendation capabilities
3. Cursor: Validates enhanced result

## Testing

Run tests with pytest:

```bash
# Using uv
uv run pytest

# Or directly
pytest tests/
```

Run tests manually:
```bash
uv run tests/test_validation.py
```

## Development

### Code Quality

The project uses several tools for code quality:

```bash
# Format code
uv run black src/ tests/

# Sort imports  
uv run isort src/ tests/

# Type checking
uv run mypy src/
```

### Project Structure

- **Tools**: Interactive capabilities that agents can call (like validation)
- **Resources**: Static content that agents can access (like syntax reference)
- **Data**: Core business logic and data management
- **Utils**: Shared utility functions

## Configuration

The server can be configured for different MCP transport protocols:

- **stdio**: Standard for Cursor MCP integration
- **HTTP**: For web-based integrations

## Contributing

1. Follow the existing code structure
2. Add tests for new functionality
3. Update documentation as needed
4. Ensure all quality checks pass

## License

[Add license information]

## Links

- [Ilograph Documentation](https://www.ilograph.com/docs/)
- [FastMCP Documentation](https://gofastmcp.com/)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
