"""
Utility Helper Functions
========================

This module provides utility functions and helpers used throughout
the ReqIF Tool Suite application. Includes text processing, file operations,
data validation, formatting, and other common utilities.

Functions:
    Text Processing:
        normalize_text: Normalize text for comparison
        calculate_text_similarity: Calculate similarity between texts
        extract_keywords: Extract keywords from text
        clean_html: Remove HTML tags from text
        truncate_text: Truncate text with ellipsis
        
    File Operations:
        format_file_size: Format file size in human-readable format
        get_file_extension: Get file extension safely
        sanitize_filename: Clean filename for safe file operations
        ensure_directory: Ensure directory exists
        
    Data Validation:
        validate_email: Validate email address format
        validate_url: Validate URL format
        is_valid_requirement_id: Validate requirement ID format
        check_dependencies: Check for required dependencies
        
    Formatting:
        format_timestamp: Format datetime for display
        format_duration: Format time duration
        format_number: Format numbers with proper separators
        
    System Utilities:
        get_system_info: Get system information
        setup_environment: Setup application environment
        measure_execution_time: Measure function execution time
"""

import re
import os
import sys
import platform
import hashlib
import difflib
import unicodedata
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from urllib.parse import urlparse
import logging

# Try to import optional dependencies
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

try:
    from .constants import REGEX_PATTERNS, ValidationConstants
    from .logger import get_logger
except ImportError:
    # Fallback for when constants/logger not available yet
    REGEX_PATTERNS = {
        'requirement_id': r'^[A-Z]{2,}-\d+$',
        'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
        'url': r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:\w*))?)?$'
    }
    
    class ValidationConstants:
        STANDARD_ID_PATTERN = r'^[A-Z]{2,}-\d+$'
    
    def get_logger(name):
        return logging.getLogger(name)

logger = get_logger(__name__)


# Text Processing Functions
def normalize_text(text: str, 
                  remove_extra_spaces: bool = True,
                  convert_to_lowercase: bool = False,
                  remove_punctuation: bool = False,
                  remove_accents: bool = False) -> str:
    """
    Normalize text for comparison and processing
    
    Args:
        text: Input text to normalize
        remove_extra_spaces: Remove extra whitespace
        convert_to_lowercase: Convert to lowercase
        remove_punctuation: Remove punctuation marks
        remove_accents: Remove accent marks
        
    Returns:
        Normalized text
    """
    if not text:
        return ""
    
    # Remove accents and normalize unicode
    if remove_accents:
        text = unicodedata.normalize('NFD', text)
        text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    
    # Convert to lowercase
    if convert_to_lowercase:
        text = text.lower()
    
    # Remove punctuation
    if remove_punctuation:
        text = re.sub(r'[^\w\s]', ' ', text)
    
    # Remove extra spaces
    if remove_extra_spaces:
        text = ' '.join(text.split())
    
    return text.strip()


def calculate_text_similarity(text1: str, text2: str, method: str = "ratio") -> float:
    """
    Calculate similarity between two texts
    
    Args:
        text1: First text
        text2: Second text
        method: Similarity method ("ratio", "quick_ratio", "real_quick_ratio")
        
    Returns:
        Similarity score between 0.0 and 1.0
    """
    if not text1 and not text2:
        return 1.0
    
    if not text1 or not text2:
        return 0.0
    
    # Normalize texts for comparison
    norm_text1 = normalize_text(text1, convert_to_lowercase=True, remove_extra_spaces=True)
    norm_text2 = normalize_text(text2, convert_to_lowercase=True, remove_extra_spaces=True)
    
    # Use difflib for similarity calculation
    matcher = difflib.SequenceMatcher(None, norm_text1, norm_text2)
    
    if method == "quick_ratio":
        return matcher.quick_ratio()
    elif method == "real_quick_ratio":
        return matcher.real_quick_ratio()
    else:
        return matcher.ratio()


def extract_keywords(text: str, min_length: int = 3, max_keywords: int = 20) -> List[str]:
    """
    Extract keywords from text
    
    Args:
        text: Input text
        min_length: Minimum keyword length
        max_keywords: Maximum number of keywords to return
        
    Returns:
        List of extracted keywords
    """
    if not text:
        return []
    
    # Normalize text
    normalized = normalize_text(text, convert_to_lowercase=True, remove_punctuation=True)
    
    # Split into words
    words = normalized.split()
    
    # Common stop words to exclude
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
        'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after',
        'above', 'below', 'out', 'off', 'over', 'under', 'again', 'further', 'then',
        'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both',
        'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not',
        'only', 'own', 'same', 'so', 'than', 'too', 'very', 'can', 'will', 'just',
        'should', 'now', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have',
        'has', 'had', 'do', 'does', 'did', 'this', 'that', 'these', 'those'
    }
    
    # Filter words
    keywords = []
    for word in words:
        if (len(word) >= min_length and 
            word not in stop_words and 
            word.isalpha()):
            keywords.append(word)
    
    # Remove duplicates while preserving order
    unique_keywords = []
    seen = set()
    for keyword in keywords:
        if keyword not in seen:
            unique_keywords.append(keyword)
            seen.add(keyword)
    
    return unique_keywords[:max_keywords]


def clean_html(text: str) -> str:
    """
    Remove HTML tags from text
    
    Args:
        text: Text containing HTML tags
        
    Returns:
        Text with HTML tags removed
    """
    if not text:
        return ""
    
    # Remove HTML tags
    clean_text = re.sub(r'<[^>]+>', '', text)
    
    # Decode HTML entities
    html_entities = {
        '&amp;': '&',
        '&lt;': '<',
        '&gt;': '>',
        '&quot;': '"',
        '&#39;': "'",
        '&nbsp;': ' '
    }
    
    for entity, char in html_entities.items():
        clean_text = clean_text.replace(entity, char)
    
    # Normalize whitespace
    clean_text = ' '.join(clean_text.split())
    
    return clean_text


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate text to maximum length with suffix
    
    Args:
        text: Text to truncate
        max_length: Maximum length including suffix
        suffix: Suffix to add when truncating
        
    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    if max_length <= len(suffix):
        return suffix[:max_length]
    
    return text[:max_length - len(suffix)] + suffix


# File Operation Functions
def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string (e.g., "1.5 MB")
    """
    if size_bytes == 0:
        return "0 B"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    unit_index = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and unit_index < len(units) - 1:
        size /= 1024.0
        unit_index += 1
    
    if unit_index == 0:
        return f"{int(size)} {units[unit_index]}"
    else:
        return f"{size:.1f} {units[unit_index]}"


def get_file_extension(filename: str) -> str:
    """
    Get file extension safely
    
    Args:
        filename: Filename or path
        
    Returns:
        File extension (including dot) or empty string
    """
    if not filename:
        return ""
    
    path = Path(filename)
    return path.suffix.lower()


def sanitize_filename(filename: str, replacement: str = "_") -> str:
    """
    Sanitize filename for safe file operations
    
    Args:
        filename: Original filename
        replacement: Character to replace invalid characters
        
    Returns:
        Sanitized filename
    """
    if not filename:
        return "unnamed"
    
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    sanitized = filename
    
    for char in invalid_chars:
        sanitized = sanitized.replace(char, replacement)
    
    # Remove control characters
    sanitized = ''.join(c for c in sanitized if ord(c) >= 32)
    
    # Trim whitespace and dots from ends
    sanitized = sanitized.strip('. ')
    
    # Ensure filename is not empty
    if not sanitized:
        sanitized = "unnamed"
    
    # Limit length (Windows has 255 character limit)
    if len(sanitized) > 255:
        name, ext = os.path.splitext(sanitized)
        max_name_length = 255 - len(ext)
        sanitized = name[:max_name_length] + ext
    
    return sanitized


def ensure_directory(directory_path: Union[str, Path]) -> bool:
    """
    Ensure directory exists, create if necessary
    
    Args:
        directory_path: Path to directory
        
    Returns:
        True if directory exists or was created successfully
    """
    try:
        Path(directory_path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error("Failed to create directory %s: %s", directory_path, str(e))
        return False


# Data Validation Functions
def validate_email(email: str) -> bool:
    """
    Validate email address format
    
    Args:
        email: Email address to validate
        
    Returns:
        True if email format is valid
    """
    if not email:
        return False
    
    pattern = REGEX_PATTERNS.get('email', r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    return bool(re.match(pattern, email))


def validate_url(url: str) -> bool:
    """
    Validate URL format
    
    Args:
        url: URL to validate
        
    Returns:
        True if URL format is valid
    """
    if not url:
        return False
    
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def is_valid_requirement_id(req_id: str, pattern: str = None) -> bool:
    """
    Validate requirement ID format
    
    Args:
        req_id: Requirement ID to validate
        pattern: Custom regex pattern (uses default if None)
        
    Returns:
        True if ID format is valid
    """
    if not req_id:
        return False
    
    if pattern is None:
        pattern = ValidationConstants.STANDARD_ID_PATTERN
    
    return bool(re.match(pattern, req_id))


def check_dependencies() -> List[str]:
    """
    Check for required and optional dependencies
    
    Returns:
        List of missing required dependencies
    """
    required_dependencies = [
        'lxml',
        'openpyxl', 
        'reportlab',
        'xlsxwriter'
    ]
    
    optional_dependencies = [
        'psutil',
        'numpy',
        'pandas'
    ]
    
    missing_required = []
    missing_optional = []
    
    for dep in required_dependencies:
        try:
            __import__(dep)
        except ImportError:
            missing_required.append(dep)
    
    for dep in optional_dependencies:
        try:
            __import__(dep)
        except ImportError:
            missing_optional.append(dep)
    
    if missing_optional:
        logger.info("Optional dependencies not available: %s", ', '.join(missing_optional))
    
    return missing_required


# Formatting Functions
def format_timestamp(timestamp: datetime, format_str: str = None) -> str:
    """
    Format datetime for display
    
    Args:
        timestamp: Datetime object to format
        format_str: Custom format string
        
    Returns:
        Formatted timestamp string
    """
    if not timestamp:
        return "N/A"
    
    if format_str is None:
        # Default format
        format_str = "%Y-%m-%d %H:%M:%S"
    
    try:
        return timestamp.strftime(format_str)
    except Exception:
        return str(timestamp)


def format_duration(seconds: float) -> str:
    """
    Format time duration in human-readable format
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    if seconds < 0:
        return "Invalid duration"
    
    if seconds < 1:
        return f"{seconds * 1000:.0f} ms"
    elif seconds < 60:
        return f"{seconds:.1f} seconds"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"


def format_number(number: Union[int, float], decimal_places: int = None) -> str:
    """
    Format numbers with proper separators
    
    Args:
        number: Number to format
        decimal_places: Number of decimal places (auto if None)
        
    Returns:
        Formatted number string
    """
    if number is None:
        return "N/A"
    
    try:
        if isinstance(number, int) or (isinstance(number, float) and number.is_integer()):
            return f"{int(number):,}"
        else:
            if decimal_places is None:
                # Auto-determine decimal places
                if abs(number) >= 100:
                    decimal_places = 1
                elif abs(number) >= 1:
                    decimal_places = 2
                else:
                    decimal_places = 3
            
            return f"{number:,.{decimal_places}f}"
    except Exception:
        return str(number)


# System Utility Functions
def get_system_info() -> Dict[str, Any]:
    """
    Get system information
    
    Returns:
        Dictionary with system information
    """
    info = {
        'platform': platform.system(),
        'platform_release': platform.release(),
        'platform_version': platform.version(),
        'architecture': platform.machine(),
        'processor': platform.processor(),
        'python_version': sys.version,
        'python_executable': sys.executable
    }
    
    # Add memory info if psutil is available
    if HAS_PSUTIL:
        try:
            memory = psutil.virtual_memory()
            info.update({
                'total_memory': memory.total,
                'available_memory': memory.available,
                'memory_percent': memory.percent
            })
            
            disk = psutil.disk_usage('/')
            info.update({
                'total_disk': disk.total,
                'free_disk': disk.free,
                'disk_percent': (disk.used / disk.total) * 100
            })
        except Exception as e:
            logger.debug("Failed to get system stats: %s", str(e))
    
    return info


def setup_environment() -> bool:
    """
    Setup application environment
    
    Returns:
        True if setup successful
    """
    try:
        # Set up directories
        from .constants import get_user_data_dir, get_config_dir, get_cache_dir, get_logs_dir
        
        directories = [
            get_user_data_dir(),
            get_config_dir(),
            get_cache_dir(),
            get_logs_dir()
        ]
        
        for directory in directories:
            if not ensure_directory(directory):
                logger.error("Failed to create directory: %s", directory)
                return False
        
        # Set environment variables if needed
        os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
        
        logger.info("Application environment setup completed")
        return True
        
    except Exception as e:
        logger.error("Failed to setup environment: %s", str(e))
        return False


def measure_execution_time(func: callable) -> Tuple[Any, float]:
    """
    Measure function execution time
    
    Args:
        func: Function to measure (should be a callable with no arguments)
        
    Returns:
        Tuple of (result, execution_time_seconds)
    """
    import time
    
    start_time = time.perf_counter()
    try:
        result = func()
        return result, time.perf_counter() - start_time
    except Exception as e:
        execution_time = time.perf_counter() - start_time
        logger.error("Function execution failed after %.3f seconds: %s", execution_time, str(e))
        raise


# Hash and Encryption Utilities
def calculate_file_hash(file_path: Union[str, Path], algorithm: str = "md5") -> str:
    """
    Calculate hash of a file
    
    Args:
        file_path: Path to file
        algorithm: Hash algorithm (md5, sha1, sha256)
        
    Returns:
        Hex digest of file hash
    """
    try:
        hash_obj = hashlib.new(algorithm)
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_obj.update(chunk)
        
        return hash_obj.hexdigest()
    
    except Exception as e:
        logger.error("Failed to calculate hash for %s: %s", file_path, str(e))
        return ""


def calculate_text_hash(text: str, algorithm: str = "md5") -> str:
    """
    Calculate hash of text
    
    Args:
        text: Text to hash
        algorithm: Hash algorithm
        
    Returns:
        Hex digest of text hash
    """
    try:
        hash_obj = hashlib.new(algorithm)
        hash_obj.update(text.encode('utf-8'))
        return hash_obj.hexdigest()
    except Exception as e:
        logger.error("Failed to calculate text hash: %s", str(e))
        return ""


# Collection Utilities
def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split list into chunks of specified size
    
    Args:
        lst: List to chunk
        chunk_size: Size of each chunk
        
    Returns:
        List of chunked lists
    """
    if chunk_size <= 0:
        return [lst]
    
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    """
    Flatten nested dictionary
    
    Args:
        d: Dictionary to flatten
        parent_key: Parent key prefix
        sep: Separator for nested keys
        
    Returns:
        Flattened dictionary
    """
    items = []
    
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    
    return dict(items)


def deep_merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two dictionaries
    
    Args:
        dict1: First dictionary
        dict2: Second dictionary (takes precedence)
        
    Returns:
        Merged dictionary
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result


# String Utilities
def camel_to_snake(name: str) -> str:
    """
    Convert CamelCase to snake_case
    
    Args:
        name: CamelCase string
        
    Returns:
        snake_case string
    """
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def snake_to_camel(name: str) -> str:
    """
    Convert snake_case to CamelCase
    
    Args:
        name: snake_case string
        
    Returns:
        CamelCase string
    """
    components = name.split('_')
    return ''.join(word.capitalize() for word in components)


# Version Utilities
def compare_versions(version1: str, version2: str) -> int:
    """
    Compare two version strings
    
    Args:
        version1: First version string
        version2: Second version string
        
    Returns:
        -1 if version1 < version2, 0 if equal, 1 if version1 > version2
    """
    def normalize_version(v):
        return [int(x) for x in re.sub(r'[^0-9.]', '', v).split('.')]
    
    try:
        v1_parts = normalize_version(version1)
        v2_parts = normalize_version(version2)
        
        # Pad shorter version with zeros
        max_length = max(len(v1_parts), len(v2_parts))
        v1_parts += [0] * (max_length - len(v1_parts))
        v2_parts += [0] * (max_length - len(v2_parts))
        
        for i in range(max_length):
            if v1_parts[i] < v2_parts[i]:
                return -1
            elif v1_parts[i] > v2_parts[i]:
                return 1
        
        return 0
    
    except Exception:
        # Fallback to string comparison
        if version1 < version2:
            return -1
        elif version1 > version2:
            return 1
        else:
            return 0


def retry_operation(operation: callable, max_retries: int = 3, 
                   delay: float = 1.0, exponential_backoff: bool = True) -> Any:
    """
    Retry an operation with configurable backoff
    
    Args:
        operation: Function to retry
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries
        exponential_backoff: Use exponential backoff
        
    Returns:
        Result of successful operation
        
    Raises:
        Last exception if all retries fail
    """
    import time
    
    last_exception = None
    current_delay = delay
    
    for attempt in range(max_retries + 1):
        try:
            return operation()
        except Exception as e:
            last_exception = e
            
            if attempt < max_retries:
                logger.warning("Operation failed (attempt %d/%d): %s. Retrying in %.1f seconds...", 
                             attempt + 1, max_retries + 1, str(e), current_delay)
                time.sleep(current_delay)
                
                if exponential_backoff:
                    current_delay *= 2
            else:
                logger.error("Operation failed after %d attempts", max_retries + 1)
    
    raise last_exception