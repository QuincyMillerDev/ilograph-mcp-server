# Ilograph MCP Server Requirements Document

# ⚠️ IMPORTANT: MCP Client Support Limitation (2025)

> **Note (2025):**
> As of early 2025, **Cursor, GitHub Copilot, and most agent IDEs only support MCP tools** (not resources or prompts). This means:
> - **All critical server functionality must be exposed as tools.**
> - Resources and prompts are currently ignored by these clients, though they may be supported in the future.
> - When designing or maintaining this server, prioritize tool-based interfaces for all essential features (validation, example access, spec queries, etc.).
> - Resources and prompts can be included for future compatibility, but should not be relied upon for agent workflows today.
>
> _Revisit this note regularly as MCP client support evolves._
> https://docs.github.com/en/copilot/customizing-copilot/extending-copilot-coding-agent-with-mcp
> As above, Github Copilot only supports Tools as part of the protocol, not resources or prompts

## Overview

Build a **FastMCP server** that acts as a **dynamic Ilograph domain expert**, providing AI agents with comprehensive, up-to-date Ilograph knowledge through intelligent content sourcing. Based on research of successful MCP server patterns and the actual Ilograph platform, this server will fetch and cache content from official sources rather than maintaining static copies, **except for a small set of example diagrams, which are stored as static .ilograph files in the server**.

**Core Principle**: AI agents handle codebase analysis; this FastMCP server provides everything needed to create perfect Ilograph diagrams using live, authoritative data from Ilograph's official sources, with a static example library for reference.

## Research Findings & Technical Direction

### Existing MCP Server Patterns Analysis
Research of successful MCP servers (WebMCP, Graphlit MCP, etc.) reveals:
- **Dynamic Content Fetching**: Modern servers fetch from external APIs/sources in real-time
- **Intelligent Caching**: TTL-based caching with fallback strategies
- **Focused Tools**: Single-purpose tools that compose well
- **Performance-First**: Sub-500ms responses through smart caching

### Ilograph Platform Analysis
From https://www.ilograph.com/ research:
- **Live Icon Catalog**: 200+ icons at https://www.ilograph.com/docs/iconlist.txt
- **Dynamic Documentation**: Actively maintained docs at https://www.ilograph.com/docs/
- **Comprehensive Specification**: Complete YAML format at https://www.ilograph.com/docs/spec/
- **Multi-perspective Documentation**: Resources, Perspectives, Contexts, Walkthroughs, etc.

### FastMCP Framework Analysis
From https://github.com/jlowin/fastmcp research:
- **Decorator-based Tools**: Use `@mcp.tool()` for exposing functionality  
- **Rich Tool Metadata**: Support for annotations, descriptions, type hints
- **Async Support**: First-class async/await patterns for I/O operations
- **Error Handling**: Structured error responses with detailed information
- **Context Access**: `ctx: Context` parameter for logging, HTTP requests, LLM sampling
- **Built-in Validation**: Pydantic integration for robust request/response validation

## Architecture

The project follows a modular architecture with clear separation of concerns:

```
ilograph-mcp-server/
├── .cursor/
├── src/
│   └── ilograph_mcp/
│       ├── __init__.py
│       ├── server.py              # Main FastMCP server instance
│       ├── core/
│       │   ├── __init__.py
│       │   ├── fetcher.py         # Dynamic content fetching
│       │   ├── cache.py           # In-memory caching with TTL
│       │   ├── parser.py          # HTML to Markdown conversion
│       │   └── content_processor.py # LLM-optimized content processing
│       ├── tools/
│       │   ├── __init__.py
│       │   ├── validate_diagram_tool.py    # @mcp.tool() for validation of diagrams syntax
│       │   ├── fetch_example_tool.py        # @mcp.tool() for example access
│       │   ├── fetch_documentation_tool.py   # @mcp.tool() for narrative docs access
│       │   ├── fetch_spec_tool.py           # @mcp.tool() for concise spec reference
│       │   ├── search_icons_tool.py        # @mcp.tool() for icon discovery
│       ├── static/
│       │   └── examples/
│       │       ├── aws-distributed-load-testing.ilograph
│       │       ├── stack-overflow-architecture-2016.ilograph
│       │       └── serverless-on-aws.ilograph
│       └── utils/
│           ├── __init__.py
│           ├── http_client.py       # HTTP client with retry/cache
│           ├── markdown_converter.py
│           ├── icon_classifier.py
│           ├── content_sanitizer.py # Clean HTML for LLM consumption
│           └── llm_formatter.py     # Format content for LLM understanding
├── tests/
│   ├── __init__.py
│   ├── test_tools/
│   └── test_integration/
├── .gitignore
├── .python-version                 # Python version for uv
├── LICENSE
├── README.md
├── pyproject.toml                  # Modern Python packaging
└── uv.lock
```

## Essential Tools for AI Agent Success

Based on analysis of Ilograph documentation and successful MCP server patterns, the following tools are critical for AI agents creating Ilograph diagrams:

### 1. **Core Diagram Tools** (Priority 1 - Must Have)

#### 1.1 Diagram Validator Tool
```python
@mcp.tool(
    annotations={
        "title": "Validate Ilograph Diagram",
        "readOnlyHint": True,
        "description": "Validates Ilograph diagram syntax and provides detailed error messages"
    }
)
async def validate_ilograph_diagram(content: str, ctx: Context) -> dict:
    """
    Validates Ilograph YAML syntax and structure.
    
    Args:
        content: The Ilograph diagram content as a string
        
    Returns:
        dict: Validation result with success/failure, errors, warnings, and suggestions
    """
```

#### 1.2 Example Diagram Access Tool
```python
@mcp.tool(
    annotations={
        "title": "Get Example Diagram",
        "readOnlyHint": True,
        "description": "Retrieves example Ilograph diagrams with metadata and learning context"
    }
)
async def get_example_diagram(example_name: str = None, category: str = None) -> dict:
    """
    Retrieves static example diagrams with learning context.
    
    Args:
        example_name: Specific example filename (e.g., 'serverless-on-aws.ilograph')
        category: Filter by complexity ('beginner', 'intermediate', 'advanced')
        
    Returns:
        dict: Example content, metadata, learning objectives, and patterns demonstrated
    """
```



### 2. **Documentation & Reference Tools** (Priority 1 - Must Have)

#### 2.1 Documentation Tool (Narrative/Tutorial Content)
```python
@mcp.tool(
    annotations={
        "title": "Fetch Ilograph Documentation",
        "readOnlyHint": True,
        "description": "Fetches narrative documentation from ilograph.com with explanations and examples"
    }
)
async def fetch_documentation_tool(section: str, ctx: Context) -> str:
    """
    Fetches and formats narrative documentation from Ilograph website.
    
    This tool provides detailed explanations, tutorials, and examples for learning
    Ilograph concepts and implementation patterns.
    
    Args:
        section: Documentation section to fetch:
                - 'resources' -> https://www.ilograph.com/docs/editing/resources/
                - 'relation-perspectives' -> https://www.ilograph.com/docs/editing/perspectives/relation-perspectives/
                - 'sequence-perspectives' -> https://www.ilograph.com/docs/editing/perspectives/sequence-perspectives/
                - 'references' -> https://www.ilograph.com/docs/editing/perspectives/references/
                - 'advanced-references' -> https://www.ilograph.com/docs/editing/perspectives/advanced-references/
                - 'resource-sizes-and-positions' -> https://www.ilograph.com/docs/editing/perspectives/resource-sizes-and-positions/
                - 'parent-overrides' -> https://www.ilograph.com/docs/editing/perspectives/parent-overrides/
                - 'perspectives-other-properties' -> https://www.ilograph.com/docs/editing/perspectives/other-properties/
                - 'icons' -> https://www.ilograph.com/docs/editing/icons/
                - 'walkthroughs' -> https://www.ilograph.com/docs/editing/walkthroughs/
                - 'contexts' -> https://www.ilograph.com/docs/editing/contexts/
                - 'imports' -> https://www.ilograph.com/docs/editing/imports/
                - 'markdown' -> https://www.ilograph.com/docs/editing/markdown/
                - 'tutorial' -> https://www.ilograph.com/docs/editing/tutorial/
        
    Returns:
        str: Clean markdown with detailed explanations, examples, and best practices
    """
```

#### 2.2 Specification Tool (Reference/Lookup Content)
```python
@mcp.tool(
    annotations={
        "title": "Fetch Ilograph Specification",
        "readOnlyHint": True,
        "description": "Fetches the concise Ilograph specification with property definitions and types"
    }
)
async def fetch_spec_tool(ctx: Context) -> str:
    """
    Fetches the official Ilograph specification from https://www.ilograph.com/docs/spec/
    
    This tool provides the authoritative reference for all Ilograph properties, types,
    and requirements in a structured table format - perfect for validation and quick lookups.
    
    Returns:
        str: Complete specification in markdown format with:
             - Top-level properties table
             - Resource properties and types
             - Perspective properties and types  
             - Relation, Sequence, Step definitions
             - Context, Layout, Import specifications
             - All property types and requirements
    """
```

#### 2.3 Icon Search Tool
```python
@mcp.tool(
    annotations={
        "title": "Search Ilograph Icons",
        "readOnlyHint": True,
        "description": "Searches the live icon catalog with semantic matching"
    }
)
async def search_icons_tool(query: str, provider: str = None, ctx: Context) -> list:
    """
    Searches the current icon catalog with semantic matching.
    
    Args:
        query: Search term (e.g., 'database', 'aws lambda', 'kubernetes')
        provider: Filter by provider ('AWS', 'Azure', 'GCP', 'Networking')
        
    Returns:
        list: Matching icons with paths, categories, and string for usage
    """
```

### 3. **Content Processing Requirements**

#### 3.1 LLM-Optimized Content Processing (Critical for Documentation Tool)
The documentation tool must convert HTML from [Ilograph's docs](https://www.ilograph.com/docs/editing/resources/) into clean, LLM-digestible markdown:

- **HTML to Markdown Conversion**: Clean conversion maintaining structure and code examples
- **Content Sanitization**: Remove navigation elements, sidebars, and ads while preserving technical content
- **Code Example Extraction**: Properly format YAML code blocks with syntax highlighting markers
- **Cross-Reference Resolution**: Convert relative links to absolute URLs (e.g., `/docs/spec/` → `https://www.ilograph.com/docs/spec/`)
- **Structured Data Extraction**: Parse tables, property lists, and syntax definitions into readable format
- **Section Headers**: Preserve hierarchical structure with proper markdown headers
- **Image Handling**: Convert image references to absolute URLs or provide descriptive alt text

#### 3.2 Intelligent Content Caching
```python
# Enhanced caching requirements for LLM-optimized content
class ContentCache:
    # Multi-tier caching strategy:
    # - Raw HTML content (24h TTL)
    # - Processed markdown content (24h TTL) 
    # - Structured data extracts (12h TTL)
    # - Icon catalog with semantic indexing (12h TTL)
    # - Validation rules and patterns (24h TTL)
    
    cache_tiers = {
        "raw_html": {"ttl": 86400, "max_size_mb": 50},
        "processed_markdown": {"ttl": 86400, "max_size_mb": 100},
        "structured_data": {"ttl": 43200, "max_size_mb": 25},
        "icon_index": {"ttl": 43200, "max_size_mb": 10},
        "validation_rules": {"ttl": 86400, "max_size_mb": 5}
    }
```

### 4. **Documentation Coverage Requirements**

The server must provide comprehensive access to all Ilograph documentation areas:

#### 4.1 Core Editing Concepts
- **Resources**: Resource tree organization, hierarchies, instanceOf patterns, abstract resources, children, layout properties, icons, colors
- **Perspectives**: Relation perspectives, sequence perspectives, extends inheritance, aliases, overrides, notes
- **Relations**: Arrow connections with from/to properties, via routing, labels, descriptions, arrowDirection (forward/backward/bidirectional), color, secondary
- **Sequence Perspectives**: Time-based diagrams with start resource, steps (to, toAndBack, toAsync, restartAt), bidirectional flows, labels
- **Contexts**: Multiple context views with roots, extends inheritance, context switching, hidden contexts
- **Aliases**: Convenient names for resource references using alias/for properties, comma-separated identifiers
- **Overrides**: Resource parent overrides in perspectives (resourceId, parentId, scale properties)
- **Slides**: Step-by-step diagram explanations for walkthroughs (text, select, expand, highlight, detail properties)
- **Icons**: Icon system with iconStyle (default, silhouette), icon paths, categorization
- **Imports**: Namespace management with from/namespace properties, component reuse, modular diagrams
- **Layout**: Compactness and sizes properties for child resource organization (proportional, uniform, auto)
- **Markdown**: Rich text support in descriptions, notes, slide text, and diagram descriptions
- **References**: Advanced reference patterns
- **Sizing and Positioning**: Layout control, resource sizing, visual hierarchy

#### 4.2 Advanced Features
- **Walkthroughs**: Interactive step-by-step guides through diagrams
- **Best Practices**: Performance optimization, diagram organization, team collaboration

### 5. **Tool Implementation Patterns**

Based on FastMCP best practices:

#### 5.1 Error Handling Pattern
```python
@mcp.tool()
async def example_tool(parameter: str, ctx: Context) -> dict:
    """Tool with comprehensive error handling."""
    try:
        await ctx.info(f"Processing {parameter}...")
        result = await process_content(parameter)
        await ctx.info("Processing completed successfully")
        return {"success": True, "data": result}
    except ValidationError as e:
        await ctx.error(f"Validation error: {str(e)}")
        return {"success": False, "error": "validation", "message": str(e)}
    except Exception as e:
        await ctx.error(f"Unexpected error: {str(e)}")
        return {"success": False, "error": "internal", "message": "An unexpected error occurred"}
```

#### 5.2 Context Usage Pattern
```python
@mcp.tool()
async def context_aware_tool(query: str, ctx: Context) -> str:
    """Tool demonstrating Context usage for logging and HTTP requests."""
    await ctx.info(f"Fetching documentation for: {query}")
    
    # Use context for HTTP requests with automatic retry/caching
    response = await ctx.http_request("GET", f"https://www.ilograph.com/docs/{query}")
    
    # Use context for progress reporting
    await ctx.report_progress(0.5, "Processing content...")
    
    processed_content = process_html_to_markdown(response.text)
    
    await ctx.info("Documentation retrieved and processed successfully")
    return processed_content
```

### 6. **Testing Requirements**

- **Unit Tests**: Each tool must have comprehensive unit tests using pytest with async support
- **Integration Tests**: Test actual HTTP fetching and caching behavior
- **Error Condition Testing**: Test all error scenarios and edge cases
- **Performance Testing**: Ensure response time requirements are met
- **MCP Protocol Testing**: Use FastMCP's testing utilities for protocol compliance

### 7. **Security Requirements**

- **Input Validation**: All user inputs must be validated and sanitized
- **HTTP Security**: Use proper headers, SSL verification, and timeout handling
- **Path Traversal Prevention**: Sanitize all file paths for static example access
- **Rate Limiting**: Implement intelligent rate limiting for external API calls
- **Error Information**: Never expose internal system details in error messages