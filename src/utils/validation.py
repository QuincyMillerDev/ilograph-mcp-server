"""
Validation utilities for the Ilograph MCP server.
"""

import os
from pathlib import Path
from typing import Union

def validate_path(path: Union[str, Path]) -> bool:
    """
    Validate that a path is safe and accessible.
    
    Args:
        path: Path to validate
        
    Returns:
        True if path is valid and safe, False otherwise
    """
    try:
        path_obj = Path(path)
        
        # Check for path traversal attacks
        resolved_path = path_obj.resolve()
        
        # Ensure the path doesn't contain dangerous patterns
        path_str = str(resolved_path)
        dangerous_patterns = ['..', '~']
        
        for pattern in dangerous_patterns:
            if pattern in str(path_obj):
                return False
        
        # Check if path exists and is readable
        if path_obj.exists():
            return os.access(path_obj, os.R_OK)
        
        # If path doesn't exist, check if parent directory is writable
        # (for output paths)
        parent = path_obj.parent
        if parent.exists():
            return os.access(parent, os.W_OK)
        
        return True
        
    except (OSError, ValueError):
        return False

def validate_format(format_type: str) -> bool:
    """
    Validate that an output format is supported.
    
    Args:
        format_type: Format to validate
        
    Returns:
        True if format is supported, False otherwise
    """
    supported_formats = {
        'json', 'svg', 'png', 'html', 'pdf'
    }
    
    return format_type.lower() in supported_formats

def validate_file_size(file_path: Union[str, Path], max_size_bytes: int) -> bool:
    """
    Validate that a file is within size limits.
    
    Args:
        file_path: Path to file to check
        max_size_bytes: Maximum allowed file size in bytes
        
    Returns:
        True if file is within limits, False otherwise
    """
    try:
        path_obj = Path(file_path)
        if not path_obj.exists():
            return True  # Non-existent files are considered valid for creation
        
        file_size = path_obj.stat().st_size
        return file_size <= max_size_bytes
        
    except (OSError, ValueError):
        return False

def validate_project_structure(project_path: Union[str, Path]) -> bool:
    """
    Validate that a project directory has analyzable content.
    
    Args:
        project_path: Path to project directory
        
    Returns:
        True if project contains analyzable files, False otherwise
    """
    try:
        path_obj = Path(project_path)
        
        if not path_obj.exists() or not path_obj.is_dir():
            return False
        
        # Check for common project indicators
        project_files = {
            'pyproject.toml', 'setup.py', 'requirements.txt',  # Python
            'package.json', 'tsconfig.json',  # JavaScript/TypeScript
            'pom.xml', 'build.gradle',  # Java
            'Cargo.toml',  # Rust
            'go.mod',  # Go
        }
        
        for file_name in project_files:
            if (path_obj / file_name).exists():
                return True
        
        # Check for source code files
        source_extensions = {'.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.rs', '.go'}
        
        for file_path in path_obj.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in source_extensions:
                return True
        
        return False
        
    except (OSError, ValueError):
        return False 