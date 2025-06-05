"""
Diagram rendering using Ilograph Export API.
"""

import asyncio
import aiohttp
import os
from pathlib import Path
from typing import Dict, Optional, Union
import logging

from .ilograph import IlographDiagram

logger = logging.getLogger(__name__)

class DiagramRenderer:
    """Renders Ilograph diagrams using the Ilograph Export API."""
    
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://export.ilograph.com"):
        self.api_key = api_key or os.getenv("ILOGRAPH_API_KEY")
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        
        if not self.api_key:
            logger.warning("No Ilograph API key provided. Rendering will not be available.")
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            headers={"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def render_diagram(
        self, 
        diagram: IlographDiagram, 
        output_format: str = "svg",
        output_path: Optional[Union[str, Path]] = None
    ) -> bytes:
        """
        Render an Ilograph diagram to the specified format.
        
        Args:
            diagram: The Ilograph diagram to render
            output_format: Output format ('svg', 'png', 'html', 'pdf')
            output_path: Optional path to save the rendered diagram
            
        Returns:
            Rendered diagram as bytes
        """
        if not self.api_key:
            raise ValueError("Ilograph API key is required for rendering")
        
        if not self.session:
            raise RuntimeError("Renderer must be used as async context manager")
        
        # Prepare the request payload
        payload = {
            "diagram": diagram.to_dict(),
            "format": output_format,
            "options": {
                "width": 1200,
                "height": 800,
                "perspective": "Dependencies"  # Default perspective
            }
        }
        
        # Make the API request
        url = f"{self.base_url}/generate"
        try:
            async with self.session.post(url, json=payload) as response:
                if response.status == 200:
                    content = await response.read()
                    
                    # Save to file if path provided
                    if output_path:
                        output_path = Path(output_path)
                        output_path.parent.mkdir(parents=True, exist_ok=True)
                        with open(output_path, 'wb') as f:
                            f.write(content)
                        logger.info(f"Diagram saved to {output_path}")
                    
                    return content
                else:
                    error_text = await response.text()
                    raise RuntimeError(f"API request failed with status {response.status}: {error_text}")
                    
        except aiohttp.ClientError as e:
            raise RuntimeError(f"Network error during diagram rendering: {str(e)}")
    
    async def render_perspective(
        self,
        diagram: IlographDiagram,
        perspective_name: str,
        output_format: str = "svg",
        output_path: Optional[Union[str, Path]] = None
    ) -> bytes:
        """
        Render a specific perspective of the diagram.
        
        Args:
            diagram: The Ilograph diagram to render
            perspective_name: Name of the perspective to render
            output_format: Output format ('svg', 'png', 'html', 'pdf')
            output_path: Optional path to save the rendered diagram
            
        Returns:
            Rendered diagram as bytes
        """
        if not self.api_key:
            raise ValueError("Ilograph API key is required for rendering")
        
        # Verify perspective exists
        perspective_names = [p.name for p in diagram.perspectives]
        if perspective_name not in perspective_names:
            raise ValueError(f"Perspective '{perspective_name}' not found. Available: {perspective_names}")
        
        # Prepare the request payload with specific perspective
        payload = {
            "diagram": diagram.to_dict(),
            "format": output_format,
            "options": {
                "width": 1200,
                "height": 800,
                "perspective": perspective_name
            }
        }
        
        # Make the API request
        url = f"{self.base_url}/generate"
        try:
            async with self.session.post(url, json=payload) as response:
                if response.status == 200:
                    content = await response.read()
                    
                    # Save to file if path provided
                    if output_path:
                        output_path = Path(output_path)
                        output_path.parent.mkdir(parents=True, exist_ok=True)
                        with open(output_path, 'wb') as f:
                            f.write(content)
                        logger.info(f"Perspective '{perspective_name}' saved to {output_path}")
                    
                    return content
                else:
                    error_text = await response.text()
                    raise RuntimeError(f"API request failed with status {response.status}: {error_text}")
                    
        except aiohttp.ClientError as e:
            raise RuntimeError(f"Network error during diagram rendering: {str(e)}")
    
    def save_ilograph_file(self, diagram: IlographDiagram, output_path: Union[str, Path]) -> None:
        """
        Save the Ilograph diagram as .ilograph file.
        
        Args:
            diagram: The Ilograph diagram to save
            output_path: Path to save the .ilograph file
        """
        output_path = Path(output_path)
        if not output_path.suffix:
            output_path = output_path.with_suffix('.ilograph')
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(diagram.to_yaml())
        
        logger.info(f"Ilograph file saved to {output_path}")
    
    async def health_check(self) -> bool:
        """
        Check if the Ilograph Export API is available.
        
        Returns:
            True if API is healthy, False otherwise
        """
        if not self.api_key or not self.session:
            return False
        
        try:
            url = f"{self.base_url}/health"
            async with self.session.get(url) as response:
                return response.status == 200
        except Exception:
            return False 