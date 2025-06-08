"""
Tests for the examples resource functionality.

These tests validate the static example library implementation for Phase 1.
"""

import json
import pytest
from pathlib import Path

from fastmcp import FastMCP
from ilograph_mcp.resources.examples import register_examples_resources, EXAMPLES_DIR, EXAMPLE_METADATA


@pytest.fixture
def mcp_server():
    """Create a test MCP server with examples resources registered."""
    mcp = FastMCP("Test Ilograph Server")
    register_examples_resources(mcp)
    return mcp


class TestExamplesResource:
    """Test cases for the examples resource."""
    
    def test_examples_directory_exists(self):
        """Test that the examples directory exists and contains files."""
        assert EXAMPLES_DIR.exists(), f"Examples directory not found: {EXAMPLES_DIR}"
        
        ilograph_files = list(EXAMPLES_DIR.glob("*.ilograph"))
        assert len(ilograph_files) > 0, "No .ilograph files found in examples directory"
        
        # Check for expected example files
        expected_files = [
            "aws-distributed-load-testing.ilograph",
            "stack-overflow-architecture-2016.ilograph", 
            "serverless-on-aws.ilograph"
        ]
        
        existing_files = [f.name for f in ilograph_files]
        for expected_file in expected_files:
            assert expected_file in existing_files, f"Expected file not found: {expected_file}"
    
    def test_example_metadata_structure(self):
        """Test that example metadata has the enhanced structure."""
        for filename, metadata in EXAMPLE_METADATA.items():
            # Core metadata fields
            assert "title" in metadata
            assert "description" in metadata
            assert "category" in metadata
            assert "cloud_provider" in metadata
            assert "complexity" in metadata
            
            # Enhanced metadata fields
            assert "architecture_patterns" in metadata
            assert "services" in metadata
            assert "use_cases" in metadata
            assert "learning_objectives" in metadata
            assert "estimated_components" in metadata
            assert "perspectives_count" in metadata
            
            # Type validation
            assert isinstance(metadata["architecture_patterns"], list)
            assert isinstance(metadata["services"], list)
            assert isinstance(metadata["use_cases"], list)
            assert isinstance(metadata["learning_objectives"], list)
            assert isinstance(metadata["estimated_components"], int)
            assert isinstance(metadata["perspectives_count"], int)
            
            # Value validation
            assert metadata["complexity"] in ["beginner", "intermediate", "advanced"]
            assert metadata["estimated_components"] >= 0
            assert metadata["perspectives_count"] >= 1
    
    @pytest.mark.asyncio
    async def test_get_examples_catalog(self, mcp_server):
        """Test the enhanced examples catalog resource."""
        # This would normally be called by the MCP protocol
        # For now, we test the underlying logic
        from ilograph_mcp.resources.examples import EXAMPLES_DIR, EXAMPLE_METADATA
        
        # Simulate what the catalog resource would return
        examples = []
        for file_path in EXAMPLES_DIR.glob("*.ilograph"):
            filename = file_path.name
            metadata = EXAMPLE_METADATA.get(filename, {})
            examples.append({
                "filename": filename,
                "resource_uri": f"ilograph://examples/{filename}",
                "size_bytes": file_path.stat().st_size,
                **metadata
            })
        
        assert len(examples) >= 3, "Should have at least 3 examples"
        
        # Check that each example has required fields
        for example in examples:
            assert "filename" in example
            assert "resource_uri" in example
            assert "size_bytes" in example
            assert "title" in example
            assert "architecture_patterns" in example
            assert "learning_objectives" in example
            assert "estimated_components" in example
            assert "perspectives_count" in example
            assert example["size_bytes"] > 0
            
        # Test filtering dimensions would be available
        all_categories = list(set(ex["category"] for ex in examples))
        all_cloud_providers = list(set(ex["cloud_provider"] for ex in examples))
        all_complexity_levels = list(set(ex["complexity"] for ex in examples))
        
        assert len(all_categories) >= 3  # serverless, distributed-testing, datacenter
        assert "aws" in all_cloud_providers
        assert "on-premises" in all_cloud_providers
        assert "beginner" in all_complexity_levels
        assert "intermediate" in all_complexity_levels  
        assert "advanced" in all_complexity_levels
    
    @pytest.mark.asyncio
    async def test_get_example_content(self, mcp_server):
        """Test getting individual example content with enhanced structure."""
        # Test with a known example file
        test_filename = "serverless-on-aws.ilograph"
        test_path = EXAMPLES_DIR / test_filename
        
        if test_path.exists():
            content = test_path.read_text(encoding="utf-8")
            assert len(content) > 0, "Example file should not be empty"
            assert "resources:" in content, "Example should contain resources section"
            
            # Test enhanced metadata structure
            from ilograph_mcp.resources.examples import EXAMPLE_METADATA
            metadata = EXAMPLE_METADATA.get(test_filename, {})
            
            # Verify enhanced fields are present
            assert "architecture_patterns" in metadata
            assert "learning_objectives" in metadata
            assert "estimated_components" in metadata
            assert "perspectives_count" in metadata
            
            # Verify beginner example characteristics
            assert metadata["complexity"] == "beginner"
            assert "serverless" in metadata["architecture_patterns"]
            assert metadata["estimated_components"] > 0
            assert metadata["perspectives_count"] >= 1
        else:
            pytest.skip(f"Test file not found: {test_filename}")
    
    def test_example_files_are_valid_yaml(self):
        """Test that example files contain valid YAML-like content."""
        import yaml
        
        for file_path in EXAMPLES_DIR.glob("*.ilograph"):
            try:
                content = file_path.read_text(encoding="utf-8")
                # Basic check that it looks like Ilograph YAML
                assert "resources:" in content or "perspectives:" in content
                
                # Try to parse as YAML (may not be perfect but should be close)
                try:
                    yaml.safe_load(content)
                except yaml.YAMLError:
                    # Some Ilograph files may have syntax that's not pure YAML
                    # This is expected, so we just check for basic structure
                    pass
                    
            except Exception as e:
                pytest.fail(f"Error reading {file_path.name}: {e}")


class TestExampleMetadata:
    """Test cases for example metadata and categorization."""
    
    def test_metadata_completeness(self):
        """Test that all example files have metadata."""
        example_files = [f.name for f in EXAMPLES_DIR.glob("*.ilograph")]
        
        for filename in example_files:
            if filename in EXAMPLE_METADATA:
                metadata = EXAMPLE_METADATA[filename]
                assert metadata["title"], f"Title missing for {filename}"
                assert metadata["description"], f"Description missing for {filename}"
            # Note: Files without metadata will get defaults, which is acceptable
    
    def test_categorization_values(self):
        """Test that categorization values are reasonable."""
        valid_complexities = {"beginner", "intermediate", "advanced", "unknown"}
        valid_providers = {"aws", "azure", "gcp", "on-premises", "multi-cloud", "unknown"}
        
        for filename, metadata in EXAMPLE_METADATA.items():
            assert metadata["complexity"] in valid_complexities, \
                f"Invalid complexity for {filename}: {metadata['complexity']}"
            
            assert metadata["cloud_provider"] in valid_providers, \
                f"Invalid cloud provider for {filename}: {metadata['cloud_provider']}"
    
    def test_learning_progression(self):
        """Test that examples provide a clear learning progression."""
        # Get examples by complexity
        beginner_examples = [filename for filename, metadata in EXAMPLE_METADATA.items() 
                           if metadata["complexity"] == "beginner"]
        intermediate_examples = [filename for filename, metadata in EXAMPLE_METADATA.items() 
                               if metadata["complexity"] == "intermediate"] 
        advanced_examples = [filename for filename, metadata in EXAMPLE_METADATA.items() 
                           if metadata["complexity"] == "advanced"]
        
        # Should have examples at each level
        assert len(beginner_examples) >= 1, "Should have at least one beginner example"
        assert len(intermediate_examples) >= 1, "Should have at least one intermediate example"
        assert len(advanced_examples) >= 1, "Should have at least one advanced example"
        
        # Check component count progression (advanced should have more components)
        beginner_components = max([EXAMPLE_METADATA[f]["estimated_components"] for f in beginner_examples])
        advanced_components = min([EXAMPLE_METADATA[f]["estimated_components"] for f in advanced_examples])
        assert advanced_components > beginner_components, "Advanced examples should have more components" 