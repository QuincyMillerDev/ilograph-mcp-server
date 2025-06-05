"""
Tests for the analysis module.
"""

import pytest
from pathlib import Path
from src.analysis.factory import AnalyzerFactory
from src.analysis.python_analyzer import PythonAnalyzer

class TestAnalyzerFactory:
    """Test the analyzer factory."""
    
    def test_get_supported_languages(self):
        """Test getting supported languages."""
        factory = AnalyzerFactory()
        languages = factory.get_supported_languages()
        assert "python" in languages
        assert "javascript" in languages
        assert "java" in languages
    
    def test_get_analyzer_for_python_file(self):
        """Test getting analyzer for Python file."""
        factory = AnalyzerFactory()
        analyzer = factory.get_analyzer_for_file(Path("test.py"))
        assert isinstance(analyzer, PythonAnalyzer)
    
    def test_unsupported_file_extension(self):
        """Test handling of unsupported file extension."""
        factory = AnalyzerFactory()
        analyzer = factory.get_analyzer_for_file(Path("test.xyz"))
        assert analyzer is None

class TestPythonAnalyzer:
    """Test the Python analyzer."""
    
    def test_can_analyze_python_file(self):
        """Test checking if Python files can be analyzed."""
        analyzer = PythonAnalyzer()
        assert analyzer.can_analyze(Path("test.py"))
        assert not analyzer.can_analyze(Path("test.js"))
    
    @pytest.mark.asyncio
    async def test_analyze_simple_python_file(self, tmp_path):
        """Test analyzing a simple Python file."""
        # Create a test Python file
        test_file = tmp_path / "test.py"
        test_file.write_text("""
class TestClass:
    '''A test class.'''
    
    def test_method(self):
        '''A test method.'''
        pass

def test_function():
    '''A test function.'''
    pass
""")
        
        analyzer = PythonAnalyzer()
        analyzer.analyze_file(test_file)
        
        # Check results
        assert len(analyzer.result.entities) >= 3  # class, method, function
        
        # Check for class entity
        classes = analyzer.result.get_entities_by_type(analyzer.result.entities[0].type)
        assert len(classes) >= 1 