"""
Configuration management for the Ilograph MCP server.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@dataclass
class Config:
    """Configuration settings for the Ilograph MCP server."""
    
    # Server settings
    host: str = field(default_factory=lambda: os.getenv("MCP_HOST", "localhost"))
    port: int = field(default_factory=lambda: int(os.getenv("MCP_PORT", "8000")))
    
    # Ilograph API settings
    ilograph_api_key: Optional[str] = field(default_factory=lambda: os.getenv("ILOGRAPH_API_KEY"))
    ilograph_api_base_url: str = field(default_factory=lambda: os.getenv("ILOGRAPH_API_BASE_URL", "https://export.ilograph.com"))
    
    # Analysis settings
    max_file_size_mb: int = field(default_factory=lambda: int(os.getenv("MAX_FILE_SIZE_MB", "10")))
    max_analysis_time_seconds: int = field(default_factory=lambda: int(os.getenv("MAX_ANALYSIS_TIME_SECONDS", "120")))
    
    # Default exclude patterns for analysis
    default_exclude_patterns: List[str] = field(default_factory=lambda: [
        "**/.git/**",
        "**/.venv/**",
        "**/venv/**",
        "**/node_modules/**",
        "**/__pycache__/**",
        "**/.pytest_cache/**",
        "**/build/**",
        "**/dist/**",
        "**/.tox/**",
        "**/.coverage/**",
        "**/coverage/**"
    ])
    
    # Supported languages configuration
    supported_languages: Dict[str, List[str]] = field(default_factory=lambda: {
        "python": [".py"],
        "javascript": [".js", ".ts", ".jsx", ".tsx"],
        "java": [".java"]
    })
    
    # Logging settings
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    log_file: Optional[str] = field(default_factory=lambda: os.getenv("LOG_FILE"))
    log_format: str = field(default_factory=lambda: os.getenv(
        "LOG_FORMAT", 
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    ))
    
    # Performance settings
    enable_caching: bool = field(default_factory=lambda: os.getenv("ENABLE_CACHING", "true").lower() == "true")
    cache_ttl_seconds: int = field(default_factory=lambda: int(os.getenv("CACHE_TTL_SECONDS", "3600")))
    
    # Security settings
    require_api_key: bool = field(default_factory=lambda: os.getenv("REQUIRE_API_KEY", "false").lower() == "true")
    allowed_hosts: List[str] = field(default_factory=lambda: os.getenv("ALLOWED_HOSTS", "*").split(","))
    
    # Output settings
    default_output_dir: str = field(default_factory=lambda: os.getenv("DEFAULT_OUTPUT_DIR", "./output"))
    max_output_file_size_mb: int = field(default_factory=lambda: int(os.getenv("MAX_OUTPUT_FILE_SIZE_MB", "100")))
    
    def __post_init__(self):
        """Post-initialization validation and setup."""
        # Ensure output directory exists
        Path(self.default_output_dir).mkdir(parents=True, exist_ok=True)
        
        # Validate numeric settings
        if self.port < 1 or self.port > 65535:
            raise ValueError(f"Invalid port number: {self.port}")
        
        if self.max_file_size_mb <= 0:
            raise ValueError(f"Invalid max_file_size_mb: {self.max_file_size_mb}")
        
        if self.max_analysis_time_seconds <= 0:
            raise ValueError(f"Invalid max_analysis_time_seconds: {self.max_analysis_time_seconds}")
    
    @classmethod
    def from_env(cls) -> "Config":
        """Create configuration from environment variables."""
        return cls()
    
    @classmethod
    def from_file(cls, config_file: str) -> "Config":
        """Create configuration from a file (future implementation)."""
        # TODO: Implement YAML/TOML configuration file support
        raise NotImplementedError("File-based configuration not yet implemented")
    
    def get_max_file_size_bytes(self) -> int:
        """Get maximum file size in bytes."""
        return self.max_file_size_mb * 1024 * 1024
    
    def get_max_output_file_size_bytes(self) -> int:
        """Get maximum output file size in bytes."""
        return self.max_output_file_size_mb * 1024 * 1024
    
    def is_file_supported(self, file_path: Path) -> bool:
        """Check if a file is supported for analysis."""
        suffix = file_path.suffix.lower()
        for extensions in self.supported_languages.values():
            if suffix in extensions:
                return True
        return False
    
    def get_language_for_file(self, file_path: Path) -> Optional[str]:
        """Get the language for a given file."""
        suffix = file_path.suffix.lower()
        for language, extensions in self.supported_languages.items():
            if suffix in extensions:
                return language
        return None 