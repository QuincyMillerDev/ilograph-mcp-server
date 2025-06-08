# Tools Reference

The Ilograph MCP Server provides comprehensive tools for accessing Ilograph documentation and examples. All tools are designed to be compatible with current MCP clients (Cursor, GitHub Copilot, etc.) that support the tools specification.

## Available Tools

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

**Returns:**
Clean markdown content with detailed explanations, examples, and best practices.

**Example Usage:**
```python
docs = await client.call_tool("fetch_documentation_tool", {
    "section": "resources"
})
```

### 2. `list_documentation_sections`

Lists all available documentation sections with descriptions and usage examples.

**Parameters:**
None

**Returns:**
Formatted list of available documentation sections with descriptions and guidance on when to use each section.

**Example Usage:**
```python
sections = await client.call_tool("list_documentation_sections", {})
```

### 3. `check_documentation_health`

Performs health checks on the documentation service and returns cache statistics.

**Parameters:**
None

**Returns:**
Health status report with service connectivity and cache information including:
- Service connectivity status
- Cache hit/miss statistics
- Available documentation sections
- System performance metrics

**Example Usage:**
```python
health = await client.call_tool("check_documentation_health", {})
```

### 4. `list_examples`

Lists available Ilograph example diagrams with their categories and descriptions.

**Parameters:**
- `category` (optional): Filter examples by complexity ('beginner', 'intermediate', 'advanced')

**Available Examples:**
- `serverless-on-aws.ilograph` - Serverless web application architecture on AWS (intermediate)
- `stack-overflow-architecture-2016.ilograph` - High-traffic web application with .NET, Redis, SQL Server (advanced)
- `aws-distributed-load-testing.ilograph` - Distributed load testing solution with containerized tasks (advanced)

**Returns:**
Dictionary containing a list of available examples and guidance message.

**Example Usage:**
```python
# List all examples
examples = await client.call_tool("list_examples", {})

# Filter by category
intermediate_examples = await client.call_tool("list_examples", {
    "category": "intermediate"
})
```

### 5. `fetch_example`

Retrieves a specific Ilograph example diagram with its content and rich metadata.

**Parameters:**
- `example_name` (str): The filename of the example to fetch (e.g., 'serverless-on-aws.ilograph')

**Returns:**
Dictionary containing:
- Complete diagram content
- Learning objectives
- Patterns demonstrated
- Category and description
- Metadata about the example

**Example Usage:**
```python
example = await client.call_tool("fetch_example", {
    "example_name": "serverless-on-aws.ilograph"
})
```

## Tool Design Principles

### Compatibility
All tools are designed with the **tool-first** approach to ensure compatibility with current MCP clients that only support the tools specification (not resources or prompts).

### Error Handling
All tools implement comprehensive error handling with:
- Structured error responses
- Meaningful error messages
- Graceful fallbacks where possible
- Logging for debugging

### Performance
- **Intelligent Caching**: TTL-based caching with fallback strategies
- **Sub-500ms Response Times**: Optimized for agent workflows
- **Connection Pooling**: Efficient HTTP client with retry logic

### Content Processing
- **LLM-Optimized Output**: Content formatted for AI agent consumption
- **Clean Markdown**: HTML converted to clean, structured markdown
- **Preserved Code Examples**: YAML code blocks with proper syntax highlighting
- **Absolute Links**: All relative links converted to absolute URLs

## Future Tools (Planned)

> **Note:** Additional tools for validation, icon search, and specification reference are planned for future releases.

### Planned Tools
- **Diagram Syntax Validation**: Validate Ilograph YAML syntax and structure
- **Icon Search and Recommendation**: Search the live icon catalog with semantic matching
- **Specification Reference**: Access to concise Ilograph specification for quick lookups
- **Best Practices Guidance**: AI-powered suggestions for diagram improvements
- **Template Generation**: Generate diagram templates based on common patterns

## Integration Examples

### Complete Workflow Example
```python
from fastmcp import Client
from ilograph_mcp import create_server

async def create_diagram_workflow():
    mcp = create_server()
    
    async with Client(mcp) as client:
        # 1. Check service health
        health = await client.call_tool("check_documentation_health", {})
        print("Service status:", health)
        
        # 2. List available documentation
        sections = await client.call_tool("list_documentation_sections", {})
        print("Available sections:", sections)
        
        # 3. Fetch specific documentation
        resources_docs = await client.call_tool("fetch_documentation_tool", {
            "section": "resources"
        })
        
        # 4. Get example for reference
        examples = await client.call_tool("list_examples", {
            "category": "intermediate"
        })
        
        # 5. Fetch specific example
        example = await client.call_tool("fetch_example", {
            "example_name": "serverless-on-aws.ilograph"
        })
        
        # Now use the documentation and examples to create diagrams
        return {
            "documentation": resources_docs,
            "example": example
        }
```

### Error Handling Example
```python
async def safe_tool_usage():
    mcp = create_server()
    
    async with Client(mcp) as client:
        try:
            result = await client.call_tool("fetch_documentation_tool", {
                "section": "invalid-section"
            })
            
            if isinstance(result, dict) and not result.get("success", True):
                print(f"Tool error: {result.get('error', 'Unknown error')}")
                return None
                
            return result
            
        except Exception as e:
            print(f"Client error: {e}")
            return None
```

## Tool Response Formats

### Success Response
Most tools return structured responses:
```python
{
    "success": True,
    "data": "content or structured data",
    "metadata": {
        "source_url": "https://...",
        "cache_hit": True,
        "processing_time": "0.123s"
    }
}
```

### Error Response
```python
{
    "success": False,
    "error": "error_type",
    "message": "Human-readable error message",
    "details": "Additional error context"
}
```

### Content-Only Response
Some tools return direct content for simpler integration:
```python
"# Documentation Content\n\nMarkdown formatted content..."
``` 