# Ilograph MCP Server Requirements Document

## Overview

Build a FastMCP server that provides AI agents (like Cursor) with comprehensive context and tools to create accurate, valid Ilograph diagrams. The server acts as a domain expert for Ilograph syntax, best practices, and validation.

## Core Requirements

### 1. **Resources** (Static Context Provision)

#### 1.1 Ilograph Syntax Reference
- **Resource URI**: `ilograph://syntax-reference`
- **Purpose**: Provide complete Ilograph syntax documentation
- **Content**: 
  - Resource definition syntax (attributes: color, subtitle, icon, etc.)
  - Perspective types (relational, sequence, etc.)
  - Relationship definition patterns
  - Multi-reference matching and wildcards
  - Built-in icon catalog (AWS, Azure, GCP, networking)

#### 1.2 Component Templates Library
- **Resource URI**: `ilograph://templates`
- **Purpose**: Provide pre-built templates for common architectures
- **Content**:
  - Microservices architecture template
  - Data pipeline template
  - API flow template
  - Cloud infrastructure template (AWS/Azure/GCP)
  - Database relationship template

#### 1.3 Best Practices Guide
- **Resource URI**: `ilograph://best-practices`
- **Purpose**: Provide curated best practices for effective diagrams
- **Content**:
  - Naming conventions for resources
  - Color coding standards
  - When to use different perspective types
  - Icon selection guidelines
  - Diagram organization principles

#### 1.4 Icon Catalog
- **Resource URI**: `ilograph://icons`
- **Purpose**: Provide searchable icon reference
- **Content**:
  - Complete list of available icons by category
  - Icon naming conventions
  - Usage examples for common icons

### 2. **Tools** (Interactive Capabilities)

#### 2.1 Syntax Validation Tool
```python
@mcp.tool()
async def validate_ilograph_syntax(diagram_code: str) -> dict:
    """Validate Ilograph markup syntax and return detailed feedback"""
    # Returns: {"valid": bool, "errors": [], "warnings": [], "suggestions": []}
```

#### 2.2 Component Extraction Tool
```python
@mcp.tool()
async def extract_architectural_components(
    description: str, 
    context_type: str = "general"
) -> dict:
    """Extract likely Ilograph components from natural language description"""
    # Returns: {"resources": [], "potential_relations": [], "suggested_icons": {}}
```

#### 2.3 Template Suggestion Tool
```python
@mcp.tool()
async def suggest_diagram_template(
    architecture_type: str,
    components: list = []
) -> dict:
    """Suggest appropriate Ilograph template based on architecture description"""
    # Returns: {"template_name": str, "template_code": str, "customization_hints": []}
```

#### 2.4 Icon Recommendation Tool
```python
@mcp.tool()
async def recommend_icons(component_names: list) -> dict:
    """Recommend appropriate icons for given component names"""
    # Returns: {"component_name": {"icon": "suggested_icon", "alternatives": []}}
```

#### 2.5 Diagram Enhancement Tool
```python
@mcp.tool()
async def enhance_diagram(
    base_diagram: str,
    enhancement_type: str = "styling"
) -> str:
    """Enhance existing Ilograph diagram with styling, icons, or structure improvements"""
```

### 3. **Prompts** (Interaction Templates)

#### 3.1 Create Architecture Diagram Prompt
```python
@mcp.prompt("create-architecture-diagram")
def architecture_diagram_prompt(
    system_description: str,
    components: str = "",
    focus_area: str = "overview"
) -> str:
    """Generate an Ilograph architecture diagram from system description"""
```

#### 3.2 Create Sequence Diagram Prompt
```python
@mcp.prompt("create-sequence-diagram") 
def sequence_diagram_prompt(
    process_description: str,
    data_flow: str = "",
    timing_requirements: str = ""
) -> str:
    """Generate Ilograph sequence diagram showing process flow"""
```

#### 3.3 Diagram Review Prompt
```python
@mcp.prompt("review-diagram")
def diagram_review_prompt(
    diagram_code: str,
    review_focus: str = "completeness"
) -> str:
    """Review Ilograph diagram for accuracy, completeness, and best practices"""
```

## Technical Implementation Requirements

### 4. **Data Management**

#### 4.1 Content Storage Structure
```
data/
├── syntax/
│   ├── resources.md          # Resource definition syntax
│   ├── perspectives.md       # Perspective types and syntax
│   └── relations.md          # Relationship definitions
├── templates/
│   ├── microservices.ilograph
│   ├── data_pipeline.ilograph
│   ├── api_flow.ilograph
│   └── cloud_infrastructure.ilograph
├── icons/
│   ├── aws_icons.json
│   ├── azure_icons.json
│   ├── gcp_icons.json
│   └── generic_icons.json
└── best_practices/
    ├── naming_conventions.md
    ├── color_coding.md
    └── organization_principles.md
```

#### 4.2 Content Loading System
```python
class IlographContentLoader:
    def load_syntax_reference(self) -> str
    def load_templates(self) -> dict
    def load_icons_catalog(self) -> dict
    def load_best_practices(self) -> str
```

### 5. **Validation Engine**

#### 5.1 Syntax Parser
- Parse Ilograph markup to identify:
  - Resource definitions and attributes
  - Perspective structures
  - Relation syntax
  - Reference patterns

#### 5.2 Validation Rules
- Check required attributes for resources
- Validate perspective structure
- Verify icon names against catalog
- Check relation syntax
- Validate multi-reference patterns

### 6. **Integration Requirements**

#### 6.1 FastMCP Server Setup
```python
from fastmcp import FastMCP

mcp = FastMCP("Ilograph Context Server")

# Configure with proper error handling
# Implement async capabilities for I/O operations
# Add logging for debugging and monitoring
```

#### 6.2 Cursor Integration
- **Transport**: stdio (standard for Cursor MCP integration)
- **Configuration**: Compatible with Cursor's mcp.json format
- **Performance**: Fast response times for real-time assistance

## User Experience Flow

### 7. **Primary Use Cases**

#### 7.1 Generate New Diagram
1. User: "Create sequence diagram showing S3 → API → Frontend"
2. Cursor: Analyzes user's code context
3. Cursor: Uses `create-sequence-diagram` prompt with MCP server
4. Cursor: References syntax and templates via resources
5. Cursor: Validates result using validation tool
6. Cursor: Returns valid Ilograph markup to user

#### 7.2 Validate Existing Diagram
1. User: Provides Ilograph code for review
2. Cursor: Uses validation tool to check syntax
3. Cursor: Uses review prompt for comprehensive feedback
4. Cursor: Suggests improvements using enhancement tool

#### 7.3 Enhance Diagram
1. User: "Add proper icons to this diagram"
2. Cursor: Uses icon recommendation tool
3. Cursor: Applies enhancements using enhancement tool
4. Cursor: Validates final result

## Success Criteria

### 8. **Quality Metrics**
- **Accuracy**: Generated diagrams are syntactically valid Ilograph code
- **Completeness**: Diagrams include appropriate icons, colors, and structure
- **Performance**: Sub-second response times for most operations
- **Reliability**: Consistent validation and suggestion quality

### 9. **Functional Requirements**
- ✅ Validate any Ilograph markup syntax
- ✅ Suggest appropriate templates for common architectures
- ✅ Recommend icons based on component names/types
- ✅ Provide comprehensive syntax reference
- ✅ Generate enhancement suggestions
- ✅ Support multiple diagram types (architecture, sequence, data flow)

This requirements document provides a comprehensive foundation for building an MCP server that transforms AI agents into Ilograph experts, enabling them to create professional, accurate diagrams with minimal user intervention.