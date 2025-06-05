"""
MCP tools implementation for the Ilograph server.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union
import yaml

from ..analysis.factory import AnalyzerFactory
from ..analysis.base import AnalysisResult
from ..diagram.ilograph import IlographGenerator, IlographDiagram
from ..diagram.renderer import DiagramRenderer
from ..utils.config import Config
from ..utils.validation import validate_path, validate_format

logger = logging.getLogger(__name__)

class MCPTools:
    """Implementation of MCP tools for Ilograph diagram generation."""
    
    def __init__(self, config: Config):
        self.config = config
        self.analyzer_factory = AnalyzerFactory(config.supported_languages)
        self.diagram_generator = IlographGenerator()
        
    async def analyze_codebase(
        self,
        project_root: str,
        languages: Optional[List[str]] = None,
        recursive: bool = True,
        exclude_patterns: Optional[List[str]] = None
    ) -> Dict:
        """
        Analyze a codebase and extract architectural information.
        
        Args:
            project_root: Path to the project root directory
            languages: List of languages to analyze (default: all supported)
            recursive: Whether to analyze subdirectories recursively
            exclude_patterns: List of glob patterns to exclude
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            # Validate project root
            project_path = Path(project_root)
            if not validate_path(project_path):
                return {
                    "success": False,
                    "error": f"Invalid project path: {project_root}"
                }
            
            if not project_path.exists():
                return {
                    "success": False,
                    "error": f"Project path does not exist: {project_root}"
                }
            
            # Set up exclude patterns
            exclude_list = exclude_patterns or []
            exclude_list.extend(self.config.default_exclude_patterns)
            
            # Analyze the codebase
            results = {}
            supported_languages = languages or self.analyzer_factory.get_supported_languages()
            
            for language in supported_languages:
                try:
                    analyzer = self.analyzer_factory.get_analyzer(language)
                    result = analyzer.analyze_directory(project_path, recursive)
                    
                    # Convert to serializable format
                    results[language] = {
                        "entities": [
                            {
                                "id": entity.id,
                                "name": entity.name,
                                "type": entity.type.value,
                                "file_path": entity.file_path,
                                "line_number": entity.line_number,
                                "description": entity.description,
                                "properties": entity.properties,
                                "perspectives": list(entity.perspectives)
                            }
                            for entity in result.entities
                        ],
                        "relationships": [
                            {
                                "from_entity_id": rel.from_entity_id,
                                "to_entity_id": rel.to_entity_id,
                                "type": rel.type.value,
                                "label": rel.label,
                                "properties": rel.properties
                            }
                            for rel in result.relationships
                        ],
                        "metadata": result.metadata
                    }
                except Exception as e:
                    logger.error(f"Error analyzing {language}: {str(e)}")
                    results[language] = {
                        "entities": [],
                        "relationships": [],
                        "metadata": {"error": str(e)}
                    }
            
            return {
                "success": True,
                "analysis_results": results,
                "metadata": {
                    "project_root": str(project_path),
                    "languages_analyzed": list(results.keys()),
                    "total_entities": sum(len(r["entities"]) for r in results.values()),
                    "total_relationships": sum(len(r["relationships"]) for r in results.values())
                }
            }
            
        except Exception as e:
            logger.error(f"Error in analyze_codebase: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def generate_diagram(
        self,
        analysis_result: Dict,
        output_format: str = "json",
        perspectives: Optional[List[str]] = None
    ) -> Dict:
        """
        Generate an Ilograph diagram from analysis results.
        
        Args:
            analysis_result: Analysis results from analyze_codebase
            output_format: Output format ('json', 'svg', 'png', 'html', 'pdf')
            perspectives: List of perspectives to include (default: all)
            
        Returns:
            Dictionary containing diagram data or metadata
        """
        try:
            if not analysis_result.get("success", False):
                return {
                    "success": False,
                    "error": "Invalid analysis results provided"
                }
            
            # Validate output format
            if not validate_format(output_format):
                return {
                    "success": False,
                    "error": f"Unsupported output format: {output_format}"
                }
            
            # Convert analysis results back to internal format
            combined_result = AnalysisResult()
            
            for language_data in analysis_result["analysis_results"].values():
                for entity_data in language_data["entities"]:
                    # Reconstruct entity (simplified for now)
                    pass  # TODO: Implement full reconstruction
                
                for rel_data in language_data["relationships"]:
                    # Reconstruct relationship (simplified for now)
                    pass  # TODO: Implement full reconstruction
            
            # Generate Ilograph diagram
            diagram = self.diagram_generator.generate(combined_result)
            
            if output_format == "ilograph":
                return {
                    "success": True,
                    "format": "ilograph",
                    "data": diagram.to_yaml(),
                    "perspectives": [p.name for p in diagram.perspectives]
                }
            else:
                # For other formats, we need to render using the API
                return await self.render_diagram(
                    diagram.to_yaml(),
                    output_format,
                    perspectives[0] if perspectives else "Dependencies"
                )
                
        except Exception as e:
            logger.error(f"Error in generate_diagram: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def render_diagram(
        self,
        schema_json: str,
        output_format: str = "svg",
        perspective: str = "Dependencies",
        output_path: Optional[str] = None
    ) -> Dict:
        """
        Render an Ilograph diagram using the Export API.
        
        Args:
            schema_json: Ilograph diagram as YAML string
            output_format: Output format ('svg', 'png', 'html', 'pdf')
            perspective: Perspective to render
            output_path: Optional path to save the rendered diagram
            
        Returns:
            Dictionary with render status and metadata
        """
        try:
            if not self.config.ilograph_api_key:
                return {
                    "success": False,
                    "error": "Ilograph API key not configured. Rendering requires API key."
                }
            
            # Parse schema
            schema = yaml.safe_load(schema_json)
            
            # Render using the API
            async with DiagramRenderer(self.config.ilograph_api_key) as renderer:
                content = await renderer.render_perspective(
                    schema, perspective, output_format, output_path
                )
                
                return {
                    "success": True,
                    "format": output_format,
                    "perspective": perspective,
                    "size_bytes": len(content),
                    "output_path": output_path
                }
                
        except Exception as e:
            logger.error(f"Error in render_diagram: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def save_diagram(
        self,
        diagram_data: str,
        output_path: str,
        format_type: str = "ilograph"
    ) -> Dict:
        """
        Save a diagram to a file.
        
        Args:
            diagram_data: The diagram data to save
            output_path: Path where to save the diagram
            format_type: Type of data being saved ('ilograph', 'json', binary formats)
            
        Returns:
            Dictionary with save status and metadata
        """
        try:
            output_file = Path(output_path)
            
            # Add appropriate file extension if not present
            if format_type == "ilograph" and not output_file.suffix:
                output_file = output_file.with_suffix('.ilograph')
            elif format_type == "json" and not output_file.suffix:
                output_file = output_file.with_suffix('.json')
            
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            if format_type in ["ilograph", "json"]:
                # Text formats
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(diagram_data)
            else:
                # Binary formats
                with open(output_file, 'wb') as f:
                    f.write(diagram_data.encode() if isinstance(diagram_data, str) else diagram_data)
            
            return {
                "success": True,
                "output_path": str(output_file),
                "format": format_type,
                "size_bytes": output_file.stat().st_size
            }
            
        except Exception as e:
            logger.error(f"Error in save_diagram: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_supported_languages(self) -> Dict:
        """
        Get list of supported programming languages.
        
        Returns:
            Dictionary containing supported languages and their extensions
        """
        try:
            languages = self.analyzer_factory.get_supported_languages()
            extensions = self.analyzer_factory.get_supported_extensions()
            
            return {
                "success": True,
                "languages": languages,
                "extensions": extensions,
                "mapping": self.config.supported_languages
            }
            
        except Exception as e:
            logger.error(f"Error in get_supported_languages: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def health_check(self) -> Dict:
        """
        Check the health status of the MCP server and its dependencies.
        
        Returns:
            Dictionary containing health status information
        """
        try:
            health_status = {
                "success": True,
                "status": "healthy",
                "checks": {}
            }
            
            # Check Ilograph API connectivity
            if self.config.ilograph_api_key:
                try:
                    async with DiagramRenderer(self.config.ilograph_api_key) as renderer:
                        api_healthy = await renderer.health_check()
                        health_status["checks"]["ilograph_api"] = {
                            "status": "healthy" if api_healthy else "unhealthy",
                            "available": api_healthy
                        }
                except Exception as e:
                    health_status["checks"]["ilograph_api"] = {
                        "status": "error",
                        "error": str(e)
                    }
            else:
                health_status["checks"]["ilograph_api"] = {
                    "status": "not_configured",
                    "message": "API key not provided"
                }
            
            # Check analyzer factory
            try:
                languages = self.analyzer_factory.get_supported_languages()
                health_status["checks"]["analyzers"] = {
                    "status": "healthy",
                    "supported_languages": languages
                }
            except Exception as e:
                health_status["checks"]["analyzers"] = {
                    "status": "error",
                    "error": str(e)
                }
            
            return health_status
            
        except Exception as e:
            logger.error(f"Error in health_check: {str(e)}")
            return {
                "success": False,
                "status": "error",
                "error": str(e)
            }
    
    async def get_diagram_perspectives(self, analysis_result: Dict) -> Dict:
        """
        Get available perspectives from analysis results.
        
        Args:
            analysis_result: Analysis results from analyze_codebase
            
        Returns:
            Dictionary containing available perspectives
        """
        try:
            if not analysis_result.get("success", False):
                return {
                    "success": False,
                    "error": "Invalid analysis results provided"
                }
            
            # Extract all unique perspectives
            perspectives = set()
            for language_data in analysis_result["analysis_results"].values():
                for entity in language_data["entities"]:
                    perspectives.update(entity.get("perspectives", []))
            
            return {
                "success": True,
                "perspectives": sorted(list(perspectives)),
                "total_count": len(perspectives)
            }
            
        except Exception as e:
            logger.error(f"Error in get_diagram_perspectives: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            } 