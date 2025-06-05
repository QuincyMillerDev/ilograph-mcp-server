"""
Factory for creating appropriate code analyzers.
"""

from pathlib import Path
from typing import Dict, List, Optional, Type

from .base import CodeAnalyzer
from .python_analyzer import PythonAnalyzer
from .javascript_analyzer import JavaScriptAnalyzer
from .java_analyzer import JavaAnalyzer

class AnalyzerFactory:
    """Factory for creating appropriate code analyzers based on file types."""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self._analyzers: Dict[str, Type[CodeAnalyzer]] = {
            "python": PythonAnalyzer,
            "javascript": JavaScriptAnalyzer,
            "java": JavaAnalyzer,
        }
        self._extension_mapping = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "javascript",
            ".jsx": "javascript",
            ".tsx": "javascript",
            ".java": "java",
        }
    
    def get_analyzer(self, language: str) -> CodeAnalyzer:
        """Get an analyzer for a specific language."""
        if language not in self._analyzers:
            raise ValueError(f"Unsupported language: {language}")
        
        analyzer_class = self._analyzers[language]
        return analyzer_class(self.config)
    
    def get_analyzer_for_file(self, file_path: Path) -> Optional[CodeAnalyzer]:
        """Get an appropriate analyzer for a specific file."""
        extension = file_path.suffix.lower()
        language = self._extension_mapping.get(extension)
        
        if language:
            return self.get_analyzer(language)
        return None
    
    def get_supported_extensions(self) -> List[str]:
        """Get list of all supported file extensions."""
        return list(self._extension_mapping.keys())
    
    def get_supported_languages(self) -> List[str]:
        """Get list of all supported languages."""
        return list(self._analyzers.keys())
    
    def register_analyzer(self, language: str, analyzer_class: Type[CodeAnalyzer], 
                         extensions: List[str]) -> None:
        """Register a new analyzer for a language."""
        self._analyzers[language] = analyzer_class
        for ext in extensions:
            self._extension_mapping[ext.lower()] = language 