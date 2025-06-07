"""
Tests for Ilograph validation functionality.
"""

import asyncio
import json
import sys
from pathlib import Path

import pytest
import pytest_asyncio

# Add src to Python path for testing
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from fastmcp import Client
from ilograph_mcp import create_server


@pytest.fixture
def mcp_server():
    """Create MCP server for testing."""
    return create_server()


@pytest_asyncio.fixture
async def client(mcp_server):
    """Create MCP client for testing."""
    client = Client(mcp_server)
    async with client:
        yield client


def extract_result(result):
    """Extract JSON data from FastMCP result."""
    # FastMCP returns a list of content objects
    if isinstance(result, list) and len(result) > 0:
        content = result[0]
        if hasattr(content, 'text'):
            return json.loads(content.text)
    return None


@pytest.mark.asyncio
async def test_valid_diagram(client):
    """Test validation of a valid Ilograph diagram."""
    valid_diagram = """
imports: 
- from: ilograph/aws
  namespace: AWS

resources:
- name: Ilograph Web
  subtitle: Web Application
  description: Advanced diagramming web application for creating interactive, multi-perspective diagrams in the browser
  icon: _demo/ilograph.png
  
- name: User
  subtitle: Application User
  description: End user of Ilograph
  icon: AWS/_General/User.svg

perspectives:
- name: Overview
  relations:
  - from: User
    to: Ilograph Web
    label: Uses
    description: Users interact with the Ilograph web application
"""
    
    result = await client.call_tool("validate_ilograph_syntax", {"diagram_code": valid_diagram})
    data = extract_result(result)
    
    assert data is not None
    assert data["valid"] is True
    assert len(data["errors"]) == 0


@pytest.mark.asyncio
async def test_invalid_yaml(client):
    """Test validation of invalid YAML."""
    invalid_yaml = """
resources:
  - name: Test
    invalid_yaml: [
"""
    
    result = await client.call_tool("validate_ilograph_syntax", {"diagram_code": invalid_yaml})
    data = extract_result(result)
    
    assert data is not None
    assert data["valid"] is False
    assert len(data["errors"]) > 0
    assert "YAML parsing error" in data["errors"][0]


@pytest.mark.asyncio
async def test_missing_required_fields(client):
    """Test validation with missing required fields."""
    missing_required = """
resources:
  - subtitle: No name provided
    color: Red

perspectives:
  - relations:
      - from: Test
        to: Other
"""
    
    result = await client.call_tool("validate_ilograph_syntax", {"diagram_code": missing_required})
    data = extract_result(result)
    
    assert data is not None
    assert data["valid"] is False
    assert len(data["errors"]) >= 2  # Missing resource name and perspective name


@pytest.mark.asyncio
async def test_invalid_style_values(client):
    """Test validation with invalid style values."""
    invalid_style = """
resources:
  - name: Test
    style: invalid_style
    iconStyle: invalid_icon_style

perspectives:
  - name: Test
    orientation: invalid_orientation
"""
    
    result = await client.call_tool("validate_ilograph_syntax", {"diagram_code": invalid_style})
    data = extract_result(result)
    
    assert data is not None
    assert data["valid"] is False
    assert len(data["errors"]) >= 3  # Three invalid style values


@pytest.mark.asyncio
async def test_sequence_perspective(client):
    """Test validation of sequence perspective."""
    sequence_diagram = """
resources:
  - name: User
  - name: API
  - name: Database

perspectives:
  - name: Login Flow
    sequence:
      start: User
      steps:
        - to: API
          label: login request
        - to: Database
          label: validate credentials
        - toAndBack: User
          label: response
"""
    
    result = await client.call_tool("validate_ilograph_syntax", {"diagram_code": sequence_diagram})
    data = extract_result(result)
    
    assert data is not None
    assert data["valid"] is True
    assert len(data["errors"]) == 0


if __name__ == "__main__":
    # Run tests manually if called directly
    import asyncio
    
    async def run_manual_test():
        mcp = create_server()
        client = Client(mcp)
        
        async with client:
            # Test valid diagram
            valid_diagram = """
resources:
  - name: Users
    color: Gray
    subtitle: Application users

perspectives:
  - name: Architecture
    relations:
      - from: Users
        to: Service A
"""
            
            result = await client.call_tool("validate_ilograph_syntax", {"diagram_code": valid_diagram})
            data = extract_result(result)
            print(f"Valid diagram test - Valid: {data['valid']}, Errors: {data['errors']}")
    
    asyncio.run(run_manual_test()) 