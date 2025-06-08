# Tools Reference

The Ilograph MCP Server provides comprehensive tools for accessing Ilograph documentation, examples, diagram validation, and icon searching. All tools are designed to be compatible with current MCP clients (Cursor, GitHub Copilot, etc.) that support the tools specification.

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

### 6. `fetch_spec_tool`

Fetches the official Ilograph specification from the authoritative source with complete property definitions.

**Parameters:**
None

**Returns:**
Complete specification in markdown format containing:
- Top-level properties table (resources, perspectives, imports, contexts, etc.)
- Resource properties and types (name, subtitle, description, color, style, etc.)
- Perspective properties and types (id, name, notes, color, extends, relations, etc.)
- Relation, Sequence, Step definitions with all properties
- Context, Layout, Import specifications
- All property types and required/optional flags

This tool provides the authoritative reference for all Ilograph properties, perfect for validation and quick property lookups.

**Example Usage:**
```python
spec = await client.call_tool("fetch_spec_tool", {})
```

### 7. `check_spec_health`

Performs health checks specifically on the specification fetching service.

**Parameters:**
None

**Returns:**
Health status report focused on specification service including:
- Specification endpoint connectivity status
- Specification cache information
- Response time metrics
- Service availability status

**Example Usage:**
```python
spec_health = await client.call_tool("check_spec_health", {})
```

### 8. `validate_diagram_tool`

Validates Ilograph diagram syntax and provides detailed error messages with suggestions.

**Parameters:**
- `content` (str): The Ilograph diagram content as a string

**Returns:**
Dictionary containing comprehensive validation results:
- `success` (bool): Overall validation success status
- `yaml_valid` (bool): Whether YAML syntax is valid
- `schema_valid` (bool): Whether Ilograph schema is valid
- `summary`: Object with total counts of errors, warnings, and info messages
- `errors`: Array of error objects with messages, locations, and suggestions
- `warnings`: Array of warning objects for non-critical issues
- `info`: Array of informational messages and suggestions
- `assessment`: Human-readable overall assessment

This tool performs comprehensive validation in two stages:
1. **YAML Syntax Check**: Ensures the diagram is valid YAML
2. **Ilograph Schema Validation**: Checks Ilograph-specific requirements like required properties, valid property names, and relationship structures

**Example Usage:**
```python
diagram_content = '''
resources:
- name: Web Server
  subtitle: Frontend
  description: Serves the web application
  children:
  - name: Load Balancer
    description: Distributes traffic

perspectives:
- name: System Overview
  relations:
  - from: User
    to: Web Server
    label: HTTPS requests
'''

result = await client.call_tool("validate_diagram_tool", {
    "content": diagram_content
})

if result["success"]:
    print("✅ Diagram is valid!")
    if result["warnings"]:
        print(f"⚠️  {len(result['warnings'])} suggestions for improvement")
else:
    print("❌ Diagram has errors:")
    for error in result["errors"]:
        print(f"  - {error['message']}")
        if error.get("suggestion"):
            print(f"    Suggestion: {error['suggestion']}")
```

### 9. `get_validation_help`

Provides comprehensive guidance on Ilograph diagram validation and common issues.

**Parameters:**
None

**Returns:**
Detailed validation help in markdown format including:
- Overview of the validation process
- Common YAML syntax issues and solutions
- Ilograph schema requirements
- Valid property lists and examples
- Tips for successful diagram creation
- References to other helpful tools

**Example Usage:**
```python
help_content = await client.call_tool("get_validation_help", {})
print(help_content)  # Displays comprehensive validation guidance
```

### 10. `search_icons_tool`

Searches the current icon catalog with semantic matching and provider filtering.

**Parameters:**
- `query` (str): Search term (e.g., 'database', 'aws lambda', 'kubernetes', 'storage')
- `provider` (optional str): Filter by provider ('AWS', 'Azure', 'GCP', 'Networking')

**Returns:**
List of matching icons with paths, categories, and usage information. Each icon dict contains:
- `path`: The icon path for use in Ilograph diagrams
- `provider`: The cloud provider or category (AWS, Azure, GCP, Networking)
- `category`: The service category (e.g., 'Compute', 'Database', 'Analytics')
- `name`: The specific icon name
- `usage`: Example usage string for Ilograph diagrams

**Example Usage:**
```python
# Search for database icons
database_icons = await client.call_tool("search_icons_tool", {
    "query": "database"
})

# Search for AWS compute icons
aws_compute = await client.call_tool("search_icons_tool", {
    "query": "compute",
    "provider": "AWS"
})
```

### 11. `list_icon_providers_tool`

Lists all available icon providers and their categories.

**Parameters:**
None

**Returns:**
Dictionary containing provider information with categories and icon counts for each provider (AWS, Azure, GCP, Networking).

**Example Usage:**
```python
providers = await client.call_tool("list_icon_providers_tool", {})
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

> **Note:** Additional advanced tools are planned for future releases.

### Planned Tools
- **Best Practices Guidance**: AI-powered suggestions for diagram improvements
- **Template Generation**: Generate diagram templates based on common patterns
- **Advanced Validation**: Extended validation with cross-reference checking and best practice analysis

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
        
        # 6. Get specification for property reference
        spec = await client.call_tool("fetch_spec_tool", {})
        
        # 7. Check specification service health
        spec_health = await client.call_tool("check_spec_health", {})
        
        # 8. Validate a diagram (example)
        test_diagram = '''
        resources:
        - name: Test Resource
          description: A simple test
        '''
        
        validation_result = await client.call_tool("validate_diagram_tool", {
            "content": test_diagram
        })
        
        # 9. Get validation help if needed
        if not validation_result["success"]:
            help_content = await client.call_tool("get_validation_help", {})
        
        # 10. Search for appropriate icons
        database_icons = await client.call_tool("search_icons_tool", {
            "query": "database",
            "provider": "AWS"
        })
        
        # 11. Get icon provider information
        icon_providers = await client.call_tool("list_icon_providers_tool", {})
        
        # Now use the documentation, examples, specification, and icons to create diagrams
        return {
            "documentation": resources_docs,
            "example": example,
            "specification": spec,
            "spec_health": spec_health,
            "validation": validation_result,
            "icons": database_icons,
            "icon_providers": icon_providers,
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