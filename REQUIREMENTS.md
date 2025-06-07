# Ilograph MCP Server Requirements Document

## Overview

Build a **FastMCP server** that acts as a **dynamic Ilograph domain expert**, providing AI agents with comprehensive, up-to-date Ilograph knowledge through intelligent content sourcing. Based on research of successful MCP server patterns and the actual Ilograph platform, this server will fetch and cache content from official sources rather than maintaining static copies, **except for a small set of example diagrams, which are stored as static .ilograph files in the server**.

**Core Principle**: AI agents handle codebase analysis; this FastMCP server provides everything needed to create perfect Ilograph diagrams using live, authoritative data from Ilograph's official sources, with a static example library for reference.

## Research Findings & Technical Direction

### Existing MCP Server Patterns Analysis
Research of successful MCP servers (WebMCP, Graphlit MCP, etc.) reveals:
- **Dynamic Content Fetching**: Modern servers fetch from external APIs/sources in real-time
- **Intelligent Caching**: TTL-based caching with fallback strategies
- **Resource Organization**: Hierarchical URIs that mirror source structure
- **Focused Tools**: Single-purpose tools that compose well
- **Performance-First**: Sub-500ms responses through smart caching

### Ilograph Platform Analysis
From https://www.ilograph.com/ research:
- **Live Icon Catalog**: 2000+ icons at https://www.ilograph.com/docs/iconlist.txt
- **Dynamic Documentation**: Actively maintained docs at https://www.ilograph.com/docs/
- **Comprehensive Specification**: Complete YAML format at https://www.ilograph.com/docs/spec/
- **Real Examples**: Reference implementations at https://app.ilograph.com/lib/

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
│       │   └── parser.py          # HTML to Markdown conversion
│       ├── tools/
│       │   ├── __init__.py
│       │   ├── syntax_validator.py    # @mcp.tool() for validation
│       │   ├── icon_recommender.py   # @mcp.tool() for icon suggestions
│       │   ├── icon_search.py        # @mcp.tool() for icon search
│       │   └── spec_query.py         # @mcp.tool() for spec queries
│       ├── resources/
│       │   ├── __init__.py
│       │   ├── specification.py      # @mcp.resource() for live spec
│       │   ├── icons.py             # @mcp.resource() for icon catalog
│       │   ├── documentation.py     # @mcp.resource() for docs
│       │   └── examples.py          # @mcp.resource() for static examples
│       ├── static/
│       │   └── examples/
│       │       ├── aws-distributed-load-testing.ilograph
│       │       ├── demo.ilograph
│       │       └── stack-overflow-architecture.ilograph
│       └── utils/
│           ├── __init__.py
│           ├── http_client.py       # HTTP client with retry/cache
│           ├── markdown_converter.py
│           └── icon_classifier.py
├── tests/
│   ├── __init__.py
├── .gitignore
├── .python-version                 # Python version for uv
├── LICENSE
├── README.md
├── pyproject.toml                  # Modern Python packaging
└── uv.l
```

## Core Requirements

### 1. **Dynamic Resource System**

#### 1.1 Live Ilograph Specification
- **Resource URI**: `ilograph://spec/current`
- **Source**: https://www.ilograph.com/docs/spec/
- **Update Strategy**: Cache with 24-hour TTL, refresh on-demand
- **Content Processing**: HTML → Markdown conversion for LLM consumption
- **Fallback**: Embedded specification snapshot for offline operation

#### 1.2 Dynamic Icon Catalog
- **Resource URI**: `ilograph://icons/catalog`
- **Source**: https://www.ilograph.com/docs/iconlist.txt
- **Update Strategy**: Cache with 24-hour TTL
- **Content Processing**: Parse icon paths, categorize by service/type
- **Index Structure**:
  ```
  {
    "aws": {"compute": [...], "database": [...], "networking": [...]},
    "azure": {"compute": [...], "database": [...], "networking": [...]},
    "gcp": {"compute": [...], "database": [...], "networking": [...]},
    "networking": [...],
    "general": [...]
  }
  ```

#### 1.3 Live Documentation Resources
- **Resource URI Pattern**: `ilograph://docs/{section}`
- **Source**: https://www.ilograph.com/docs/
- **Sections**:
  - `getting-started` - Ilograph basics and browsing
  - `editing` - Complete editing handbook
  - `resources` - Resource definition guide
  - `perspectives` - Perspective types and configuration
  - `icons` - Icon system and usage
  - `imports` - Import system documentation
  - `contexts` - Context system guide
  - `walkthroughs` - Walkthrough creation
- **Processing**: Convert HTML docs to structured markdown with section headers

#### 1.4 Example Library (Static)
- **Resource URI**: `ilograph://examples`
- **Source**: Three official examples from the Ilograph cloud webapp:
  - https://app.ilograph.com/demo.ilograph.Ilograph
  - https://app.ilograph.com/demo.ilograph.AWS%2520Distributed-Load-Testing
  - https://app.ilograph.com/demo.ilograph.Stack%2520Overflow%2520Architecture%2520(2016)
- **Content**: These diagrams are stored as static `.ilograph` files in the server repository, as they do not update frequently and are difficult to extract programmatically from the webapp.
- **Categories**: Serverless on AWS, Distributed Load Testing on AWS, Physical Datacenter Architecture
- **Processing**: Parse .ilograph files

### 2. **Intelligent Tools**

#### 2.1 Enhanced Syntax Validation
```python
from fastmcp import FastMCP

mcp = FastMCP("Ilograph Expert")

@mcp.tool()
async def validate_ilograph_syntax(diagram_code: str) -> dict:
    """
    Validate Ilograph markup syntax against live official specification.
    
    Uses real-time specification data to ensure validation is always current.
    Provides detailed error reporting with suggestions for fixes.
    
    Args:
        diagram_code: The Ilograph YAML markup to validate
        
    Returns:
        Dictionary with validation results including errors, warnings, and suggestions
    """
    # Implementation will validate against live spec
    return {
        "valid": bool,
        "errors": [{"line": int, "message": str, "severity": str}],
        "warnings": [{"line": int, "message": str, "suggestion": str}],
        "suggestions": [{"type": str, "description": str, "example": str}]
    }
```

#### 2.2 Smart Icon Recommendation
```python
@mcp.tool()
async def recommend_icons(component_names: list[str]) -> dict:
    """
    Recommend appropriate icons for given component names using live icon catalog.
    
    Uses semantic matching and pattern recognition against the current icon set.
    Considers AWS, Azure, GCP, and generic icon categories.
    
    Args:
        component_names: List of component names to get icon recommendations for
        
    Returns:
        Dictionary mapping component names to icon recommendations
    """
    # Implementation will use live icon catalog
    return {
        "component_name": {
            "icon": "primary_recommendation",
            "alternatives": ["alt1", "alt2", "alt3"],
            "category": "aws|azure|gcp|networking|general",
            "confidence": "high|medium|low",
            "reasoning": "why this icon was recommended"
        }
    }
```

#### 2.3 Advanced Icon Search
```python
@mcp.tool()
async def search_icons_by_keyword(
    keyword: str, 
    category: str = "", 
    limit: int = 10
) -> dict:
    """
    Search live icon catalog by keyword with fuzzy matching and semantic search.
    
    Searches across icon names, paths, and inferred categories.
    Supports cloud provider filtering and semantic similarity.
    
    Args:
        keyword: Search term (e.g., "database", "compute", "lambda")
        category: Optional filter (AWS, Azure, GCP, Networking)
        limit: Maximum results to return
        
    Returns:
        Dictionary with search results and metadata
    """
    # Implementation will search live icon catalog
    return {
        "results": [
            {
                "name": "extracted_name",
                "path": "full/icon/path",
                "category": "service_category", 
                "provider": "aws|azure|gcp|general",
                "relevance_score": 0.95
            }
        ],
        "total_found": int,
        "search_metadata": {
            "query_time_ms": int,
            "cache_hit": bool
        }
    }
```

#### 2.4 Specification Query Tool
```python
@mcp.tool()
async def query_specification(
    query_type: str,
    property_name: str = "",
    context: str = ""
) -> dict:
    """
    Query live Ilograph specification for specific syntax or property information.
    
    Provides precise, current specification details for any Ilograph feature.
    Includes examples and usage patterns from official documentation.
    
    Args:
        query_type: "property", "perspective", "relation", "sequence", "context"
        property_name: Specific property to query (e.g., "arrowDirection")
        context: Additional context for the query
        
    Returns:
        Dictionary with specification details and examples
    """
    # Implementation will query live specification
    return {
        "specification": "detailed_spec_info",
        "valid_values": ["allowed_values"],
        "examples": ["usage_examples"],
        "best_practices": ["recommendations"],
        "related_properties": ["related_properties"]
    }
```

### 3. **Caching and Performance System**

#### 3.1 Simple In-Memory Caching Strategy
For this lightweight MVP server, caching will use a single in-memory cache with a basic TTL (time-to-live) for dynamic resources (specification, icon catalog, documentation). This approach is consistent with best practices for lightweight MCP servers, as seen in open-source reference implementations and guides ([Leanware MCP Guide](https://www.leanware.co/insights/model-context-protocol-guide), [modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers)).

- Use a Python dictionary or similar structure to store cached content in memory.
- Each cache entry includes a timestamp; entries are refreshed if expired (default TTL: 24h for spec/docs, 12h for icons).
- On cache miss or expiry, fetch fresh content from the source and update the cache.
- No persistent disk cache or fallback static content for dynamic resources (static examples are always available).
- Cache can be invalidated manually (e.g., via a refresh endpoint or on server restart).
- This keeps the server simple, fast, and easy to maintain for MVP.

#### 3.2 Content Fetching Engine
```python
class IlographContentFetcher:
    """Handles fetching and processing from Ilograph sources with in-memory caching."""

    async def fetch_icon_catalog(self) -> dict:
        """Fetch and parse iconlist.txt, using in-memory cache with TTL."""

    async def fetch_documentation_section(self, section: str) -> str:
        """Fetch and convert docs to markdown, using in-memory cache with TTL."""

    async def fetch_specification(self) -> dict:
        """Fetch and parse specification, using in-memory cache with TTL."""
```

### 4. **Resource Organization**

#### 4.1 Hierarchical Resource Structure
```
ilograph://
├── spec/
│   └── current                    # Live specification (https://www.ilograph.com/docs/spec)
├── docs/
│   ├── getting-started/           # What is Ilograph, browsing diagrams, first diagram tutorial
│   ├── editing/                   # Editing handbook, resources, perspectives, walkthroughs, icons, markdown
│   │   ├── resources/             # Defining and organizing system components
│   │   ├── perspectives/          # Creating different views (relation, sequence, advanced references, etc.)
│   │   ├── walkthroughs/          # Step-by-step guided tours
│   │   ├── icons/                 # Icon usage and system
│   │   ├── markdown/              # Markdown support in diagrams
│   │   ├── contexts/              # Contextual views (advanced)
│   │   ├── imports/               # Importing and reusing diagrams/components
│   │   └── resource-sizes-and-positions/ # Adjusting resource layout
│   ├── team-workspaces/           # Team collaboration features
│   ├── team-workspace-api/        # Programmatic access to team features
│   ├── cli-and-export-api/        # CLI and export API documentation
│   └── ilograph-for-confluence-cloud/ # Confluence integration docs
├── icons/
│   ├── catalog                    # Complete icon catalog (parsed from iconlist.txt)
│   └── iconlist.txt               # Raw icon list (https://www.ilograph.com/docs/iconlist.txt)
├── examples/
│   └── sample-diagrams            # Static .ilograph files for official examples
└── blog/
    └── posts/                     # Blog posts and guides (e.g., multiperspective diagramming)
```

- All documentation sections should be accessible as resources under `ilograph://docs/` with subpaths matching the official documentation structure.
- The icon catalog and iconlist are under `ilograph://icons/`.
- Static example diagrams are under `ilograph://examples/`.
- Blog and advanced guides are under `ilograph://blog/`.

This structure matches the sitemap and documentation organization of the official Ilograph platform ([Ilograph Docs](https://www.ilograph.com/docs/), [llms.txt]).

### 5. **Error Handling and Reliability**

#### 5.1 Graceful Degradation Strategy
- If a dynamic resource fetch fails and the cache is empty, return a clear error message indicating the resource is temporarily unavailable.
- If the cache is expired but still contains data, serve the stale data with a warning.
- Static example files are always available and not affected by cache state.
- No complex fallback layers are needed for this MVP.

## Success Criteria

### Functional Requirements
- ✅ Always serve current Ilograph specification and icon catalog
- ✅ Sub-500ms response times for cached content
- ✅ 99%+ cache hit rate for common operations
- ✅ Graceful degradation when sources unavailable
- ✅ Complete icon search and recommendation capabilities
- ✅ Comprehensive diagram validation and enhancement

### Quality Metrics
- **Content Freshness**: <24h
- **Performance**: <500ms cached, <2s fresh fetch
- **Reliability**: 99.9% uptime with graceful degradation
- **Cache Efficiency**: >90% hit rate for icons, >80% for docs
- **Accuracy**: Zero false positives in validation

### User Experience
- **AI Agent Integration**: Seamless MCP client compatibility
- **Developer Experience**: Clear error messages and suggestions
- **Content Quality**: Always current, authoritative Ilograph information
- **Performance**: Fast enough for real-time diagram assistance

This dynamic approach ensures the MCP server always provides current, authoritative Ilograph information while maintaining high performance through intelligent caching and optimized content delivery.

## Implementation Plan

This plan covers the full scope of the Ilograph MCP Server project, including dynamic content sourcing, intelligent caching, static example library, and robust error handling.

### Phase 1: Core Infrastructure & Static Example Library
- Set up FastMCP server with project structure and configuration.
- Implement static example library:
  - Extract and store the three official .ilograph examples in an `examples/` directory.
  - Expose a resource at `ilograph://examples` to list and serve these files.
  - Add filtering/categorization if needed.
- Add basic server health check and logging.

### Phase 2: Dynamic Resource System
- Implement dynamic fetching and caching for:
  - Ilograph specification (`ilograph://spec/current`)
  - Icon catalog (`ilograph://icons/catalog`)
  - Documentation sections (`ilograph://docs/{section}`)
- Convert HTML docs/spec to Markdown for LLM consumption.
- Implement a simple in-memory cache with TTL for all dynamic resources. No disk or multi-tier cache is required.

### Phase 3: Intelligent Tools
- Implement tools for:
  - Syntax validation against live spec
  - Icon recommendation using the live icon catalog
  - Icon search by keyword/category
  - Specification query tool
- Use Pydantic for input validation and type safety.
- Add comprehensive docstrings and usage examples for all tools.

### Phase 4: Testing & Documentation
- Write unit and integration tests for all resources and tools.
- Test error conditions, edge cases, and cache behavior.
- Document all endpoints, tools, and usage patterns.
- Provide example requests and responses.

### Phase 6: Deployment & Operations
- Package server for deployment (include static examples, config, etc.).
- Add health checks and status endpoints.
- Set up structured logging and monitoring.
- Ensure environment variable support for configuration.
- Validate deployment in target environments.

### Optional Enhancements (Post-MVP)
- Add richer metadata extraction from .ilograph examples.
- Implement advanced diagram enhancement tools.
- Support additional dynamic resources or integrations as needed.

---

This phased plan ensures a robust, maintainable, and performant MCP server that meets all requirements for dynamic Ilograph knowledge delivery, with a clear path for future enhancements.
