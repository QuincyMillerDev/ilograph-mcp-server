"""
Main MCP server implementation for Ilograph diagram generation.
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, Optional
from fastmcp import FastMCP

from .tools import MCPTools
from ..utils.config import Config
from ..utils.logging_config import setup_logging

logger = logging.getLogger(__name__)

class IlographMCPServer:
    """Main MCP server for Ilograph diagram generation."""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.mcp = FastMCP("Ilograph Diagram Generator")
        self.tools = MCPTools(self.config)
        
        # Setup logging
        setup_logging(self.config.log_level, self.config.log_file)
        
        # Register tools
        self._register_tools()
        
        logger.info("Ilograph MCP Server initialized")
    
    def _register_tools(self) -> None:
        """Register all MCP tools."""
        
        @self.mcp.tool()
        async def analyze_codebase(
            project_root: str,
            languages: Optional[list] = None,
            recursive: bool = True,
            exclude_patterns: Optional[list] = None
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
            return await self.tools.analyze_codebase(
                project_root, languages, recursive, exclude_patterns
            )
        
        @self.mcp.tool()
        async def generate_diagram(
            analysis_result: Dict,
            output_format: str = "json",
            perspectives: Optional[list] = None
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
            return await self.tools.generate_diagram(
                analysis_result, output_format, perspectives
            )
        
        @self.mcp.tool()
        async def save_diagram(
            diagram_data: str,
            output_path: str,
            format_type: str = "json"
        ) -> Dict:
            """
            Save a diagram to a file.
            
            Args:
                diagram_data: The diagram data to save
                output_path: Path where to save the diagram
                format_type: Type of data being saved
                
            Returns:
                Dictionary with save status and metadata
            """
            return await self.tools.save_diagram(diagram_data, output_path, format_type)
        
        @self.mcp.tool()
        async def render_diagram(
            schema_json: str,
            output_format: str = "svg",
            perspective: str = "All",
            output_path: Optional[str] = None
        ) -> Dict:
            """
            Render an Ilograph diagram using the Export API.
            
            Args:
                schema_json: Ilograph schema as JSON string
                output_format: Output format ('svg', 'png', 'html', 'pdf')
                perspective: Perspective to render
                output_path: Optional path to save the rendered diagram
                
            Returns:
                Dictionary with render status and metadata
            """
            return await self.tools.render_diagram(
                schema_json, output_format, perspective, output_path
            )
        
        @self.mcp.tool()
        async def get_supported_languages() -> Dict:
            """
            Get list of supported programming languages.
            
            Returns:
                Dictionary containing supported languages and their extensions
            """
            return await self.tools.get_supported_languages()
        
        @self.mcp.tool()
        async def health_check() -> Dict:
            """
            Check the health status of the MCP server and its dependencies.
            
            Returns:
                Dictionary containing health status information
            """
            return await self.tools.health_check()
        
        @self.mcp.tool()
        async def get_diagram_perspectives(analysis_result: Dict) -> Dict:
            """
            Get available perspectives from analysis results.
            
            Args:
                analysis_result: Analysis results from analyze_codebase
                
            Returns:
                Dictionary containing available perspectives
            """
            return await self.tools.get_diagram_perspectives(analysis_result)
    
    def run(self, host: str = "localhost", port: int = 8000) -> None:
        """
        Run the MCP server.
        
        Args:
            host: Host to bind to
            port: Port to bind to
        """
        logger.info(f"Starting Ilograph MCP Server on {host}:{port}")
        try:
            self.mcp.run(host=host, port=port)
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
        except Exception as e:
            logger.error(f"Server error: {str(e)}")
            raise
    
    async def run_async(self, host: str = "localhost", port: int = 8000) -> None:
        """
        Run the MCP server asynchronously.
        
        Args:
            host: Host to bind to
            port: Port to bind to
        """
        logger.info(f"Starting Ilograph MCP Server on {host}:{port}")
        try:
            await self.mcp.run_async(host=host, port=port)
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
        except Exception as e:
            logger.error(f"Server error: {str(e)}")
            raise
    
    def stop(self) -> None:
        """Stop the MCP server."""
        logger.info("Stopping Ilograph MCP Server")
        # FastMCP doesn't have a built-in stop method, so we'll rely on the event loop 