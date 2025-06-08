# Architecture

The Ilograph MCP Server is built with a modular, scalable architecture designed for high performance and maintainability. This document provides detailed technical information about the system design and implementation patterns.

## System Overview

The server acts as a **dynamic Ilograph domain expert**, providing AI agents with comprehensive access to live Ilograph documentation and examples through a FastMCP-based architecture.

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP Client Layer                         │
│           (Cursor, GitHub Copilot, etc.)                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   FastMCP Server                            │
│                 (Tool Registration)                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Tool Layer                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ Documentation   │  │ Example Access  │  │ Health Checks   │ │
│  │ Tools           │  │ Tools           │  │ Tools           │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Core Layer                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ Content Fetcher │  │ Cache System    │  │ Content Parser  │ │
│  │ (HTTP Client)   │  │ (TTL-based)     │  │ (HTML→Markdown) │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  External Sources                           │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ Ilograph Docs   │  │ Static Examples │  │ Icon Catalog    │ │
│  │ (ilograph.com)  │  │ (Local Files)   │  │ (Future)        │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Project Structure

```
src/ilograph_mcp/
├── __init__.py              # Package exports and public API
├── server.py                # Main FastMCP server instance
├── core/
│   ├── __init__.py
│   ├── fetcher.py          # HTTP content fetching with retry logic
│   ├── cache.py            # TTL-based in-memory caching system
│   └── content_processor.py # Content processing and sanitization
├── tools/
│   ├── __init__.py
│   ├── fetch_documentation_tool.py  # Documentation access tools
│   └── register_example_tools.py    # Example diagram tools
├── utils/
│   ├── __init__.py
│   ├── http_client.py      # HTTP client with connection pooling
│   ├── markdown_converter.py       # HTML to Markdown conversion
│   ├── content_sanitizer.py        # Content cleaning utilities
│   └── llm_formatter.py            # LLM-optimized formatting
└── static/
    └── examples/
        ├── aws-distributed-load-testing.ilograph
        ├── stack-overflow-architecture-2016.ilograph
        └── serverless-on-aws.ilograph
```

## Core Components

### 1. FastMCP Server (`server.py`)

The main server instance built on the FastMCP framework:

```python
@mcp.tool()
async def example_tool(parameter: str, ctx: Context) -> dict:
    """FastMCP tool with proper annotations and error handling."""
    # Tool implementation with context logging
```

**Key Features:**
- **Decorator-based Tools**: Uses `@mcp.tool()` for exposing functionality
- **Async/Await Support**: First-class async support for I/O operations
- **Context Integration**: Built-in logging, HTTP requests, and progress reporting
- **Type Safety**: Pydantic integration for request/response validation

### 2. Content Fetcher (`core/fetcher.py`)

Handles dynamic content retrieval from external sources:

```python
class ContentFetcher:
    async def fetch_documentation(self, section: str) -> str:
        """Fetch and process documentation from ilograph.com"""
        # HTTP request with caching and error handling
        
    async def fetch_icon_catalog(self) -> List[dict]:
        """Fetch live icon catalog for search functionality"""
        # Dynamic catalog retrieval
```

**Features:**
- **Connection Pooling**: Efficient HTTP client with reused connections
- **Retry Logic**: Exponential backoff for transient failures
- **Rate Limiting**: Intelligent throttling for external API calls
- **Error Recovery**: Graceful degradation with fallback strategies

### 3. Caching System (`core/cache.py`)

Multi-tier TTL-based caching for optimal performance:

```python
class TTLCache:
    def __init__(self):
        self.cache_tiers = {
            "raw_html": {"ttl": 86400, "max_size_mb": 50},
            "processed_markdown": {"ttl": 86400, "max_size_mb": 100},
            "structured_data": {"ttl": 43200, "max_size_mb": 25},
        }
```

**Cache Strategies:**
- **Raw HTML Content**: 24h TTL for source HTML
- **Processed Markdown**: 24h TTL for converted content
- **Structured Data**: 12h TTL for parsed/indexed content
- **Memory Management**: Automatic eviction based on size and TTL

### 4. Content Processing (`utils/markdown_converter.py`)

Converts HTML documentation to LLM-optimized markdown:

```python
class IlographMarkdownConverter:
    def convert_html_to_markdown(self, html: str) -> str:
        """Convert HTML to clean, structured markdown"""
        # HTML parsing, content extraction, and formatting
```

**Processing Pipeline:**
1. **HTML Parsing**: BeautifulSoup-based parsing with error handling
2. **Content Extraction**: Intelligent main content identification
3. **Navigation Removal**: Strip sidebars, ads, and navigation elements
4. **Link Resolution**: Convert relative to absolute URLs
5. **Code Preservation**: Maintain YAML syntax highlighting
6. **Markdown Generation**: Clean, structured output for LLM consumption

## Tool Architecture

### Tool Registration Pattern

```python
# Individual tool files export registration functions
def register_documentation_tools(mcp: FastMCP) -> None:
    """Register all documentation-related tools"""
    
    @mcp.tool(annotations={
        "title": "Fetch Documentation",
        "readOnlyHint": True,
        "description": "Fetches Ilograph documentation sections"
    })
    async def fetch_documentation_tool(section: str, ctx: Context) -> str:
        # Tool implementation
```

### Error Handling Pattern

All tools follow consistent error handling:

```python
async def tool_implementation(param: str, ctx: Context) -> dict:
    try:
        await ctx.info(f"Processing {param}...")
        result = await process_content(param)
        return {"success": True, "data": result}
    except ValidationError as e:
        await ctx.error(f"Validation error: {str(e)}")
        return {"success": False, "error": "validation", "message": str(e)}
    except Exception as e:
        await ctx.error(f"Unexpected error: {str(e)}")
        return {"success": False, "error": "internal", "message": "Service unavailable"}
```

## Performance Characteristics

### Response Time Targets
- **Documentation Fetching**: < 500ms (cached), < 2s (fresh)
- **Example Access**: < 100ms (always cached)
- **Health Checks**: < 200ms
- **List Operations**: < 100ms

### Caching Strategy
- **Hit Rate Target**: > 90% for documentation requests
- **Memory Usage**: < 200MB for cache storage
- **TTL Management**: Automatic cleanup and refresh
- **Fallback Handling**: Serve stale content if fresh unavailable

### Scalability Considerations
- **Concurrent Requests**: Support for 100+ concurrent tool calls
- **Memory Efficiency**: Streaming for large content
- **Connection Limits**: Configurable HTTP client pool sizes
- **Rate Limiting**: Respectful external API usage

## Testing Architecture

### Test Structure
```
tests/
```
**SEE https://gofastmcp.com/patterns/testing**

### Test Patterns
- **Async Testing**: Full async/await support with pytest-asyncio
- **Mocking**: External service mocking for reliable tests
- **Fixtures**: Reusable test data and server instances
- **Coverage**: Comprehensive coverage requirements (>90%)