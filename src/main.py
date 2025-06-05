#!/usr/bin/env python3
"""
Main entry point for the Ilograph MCP Server.
"""

import asyncio
import click
import logging
import signal
import sys
from pathlib import Path

from .mcp.server import IlographMCPServer
from .utils.config import Config

logger = logging.getLogger(__name__)

@click.command()
@click.option("--host", default="localhost", help="Host to bind to")
@click.option("--port", default=8000, type=int, help="Port to bind to")
@click.option("--config-file", type=click.Path(exists=True), help="Configuration file path")
@click.option("--log-level", default="INFO", help="Logging level")
@click.option("--log-file", type=click.Path(), help="Log file path")
def main(host: str, port: int, config_file: str, log_level: str, log_file: str):
    """Run the Ilograph MCP Server."""
    
    # Load configuration
    if config_file:
        config = Config.from_file(config_file)
    else:
        config = Config.from_env()
    
    # Override config with CLI arguments
    if host != "localhost":
        config.host = host
    if port != 8000:
        config.port = port
    if log_level != "INFO":
        config.log_level = log_level
    if log_file:
        config.log_file = log_file
    
    # Initialize server
    server = IlographMCPServer(config)
    
    # Set up signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, shutting down...")
        server.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Run the server
        logger.info("Starting Ilograph MCP Server...")
        server.run(host=config.host, port=config.port)
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        sys.exit(1)

@click.command()
@click.argument("project_path", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option("--format", "-f", default="ilograph", help="Output format (ilograph, svg, png) - requires API key for rendering")
@click.option("--language", "-l", multiple=True, help="Languages to analyze")
def analyze(project_path: str, output: str, format: str, language: tuple):
    """Analyze a codebase and generate .ilograph diagram file."""
    
    async def run_analysis():
        config = Config.from_env()
        server = IlographMCPServer(config)
        
        # Run analysis
        analysis_result = await server.tools.analyze_codebase(
            project_path, 
            languages=list(language) if language else None
        )
        
        # Generate diagram
        diagram_result = await server.tools.generate_diagram(
            analysis_result, 
            output_format=format
        )
        
        # Save result
        if format == "ilograph":
            output_path = output or "diagram.ilograph"
            await server.tools.save_diagram(
                diagram_result.get("data", ""),
                output_path,
                format
            )
            print(f"Analysis complete. Ilograph file saved to {output_path}")
            print("You can open this file directly in the Ilograph editor.")
        else:
            # For rendering formats, check if data is available
            if diagram_result.get("success"):
                output_path = output or f"diagram.{format}"
                await server.tools.save_diagram(
                    diagram_result.get("data", ""),
                    output_path,
                    format
                )
                print(f"Analysis complete. Rendered diagram saved to {output_path}")
            else:
                print(f"Rendering failed: {diagram_result.get('error', 'Unknown error')}")
                print("Consider using --format ilograph to generate .ilograph files without API key.")
    
    asyncio.run(run_analysis())

@click.group()
def cli():
    """Ilograph MCP Server CLI."""
    pass

cli.add_command(main, name="serve")
cli.add_command(analyze)

if __name__ == "__main__":
    cli() 