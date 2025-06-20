"""
ReqIF Tool Suite - Core Module
==============================

This module contains the core business logic for the ReqIF Tool Suite.
It provides the fundamental functionality for parsing, comparing, analyzing,
and managing ReqIF files.

Modules:
    reqif_parser: ReqIF file parsing and structure extraction
    reqif_comparator: File and requirement comparison algorithms
    reqif_analyzer: Statistical analysis and metrics calculation
    file_manager: File I/O operations and management
    
Classes:
    ReqIFParser: Parse ReqIF files into structured data
    ReqIFComparator: Compare ReqIF files and generate differences
    ReqIFAnalyzer: Analyze requirements and generate statistics
    FileManager: Handle file operations and validation

Author: ReqIF Tool Suite Team
Version: 2.0.0
License: MIT
"""

from .reqif_parser import ReqIFParser
from .reqif_comparator import ReqIFComparator
from .reqif_analyzer import ReqIFAnalyzer
from .file_manager import FileManager

# Version information
__version__ = "2.0.0"
__author__ = "ReqIF Tool Suite Team"
__email__ = "support@reqif-tools.com"

# Public API
__all__ = [
    "ReqIFParser",
    "ReqIFComparator", 
    "ReqIFAnalyzer",
    "FileManager",
    "get_version",
    "get_supported_formats",
]

def get_version():
    """Get the version of the core module"""
    return __version__

def get_supported_formats():
    """Get list of supported file formats"""
    return [
        {
            "name": "ReqIF",
            "extension": ".reqif",
            "description": "Requirements Interchange Format",
            "parser": "ReqIFParser"
        },
        {
            "name": "ReqIF Archive", 
            "extension": ".reqifz",
            "description": "Compressed ReqIF Archive",
            "parser": "ReqIFParser"
        }
    ]