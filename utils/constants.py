"""
Application Constants
====================

This module contains all application-wide constants, configuration values,
and settings used throughout the ReqIF Tool Suite.

Classes:
    AppConfig: Main application configuration
    FileFormats: Supported file formats
    UIConstants: User interface constants
    
Constants:
    APP_CONFIG: Main application configuration instance
    SUPPORTED_FORMATS: List of supported file formats
    DEFAULT_SETTINGS: Default application settings
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Any
import os


@dataclass
class AppConfig:
    """Main application configuration"""
    
    # Application Information
    APP_NAME: str = "ReqIF Tool Suite"
    VERSION: str = "2.0.0"
    AUTHOR: str = "ReqIF Tool Suite Team"
    EMAIL: str = "support@reqif-tools.com"
    WEBSITE: str = "https://reqif-tools.com"
    GITHUB_URL: str = "https://github.com/your-org/reqif-tool-suite"
    
    # Application Paths
    APP_DIR: Path = Path(__file__).parent.parent.absolute()
    RESOURCES_DIR: Path = APP_DIR / "resources"
    ICONS_DIR: Path = RESOURCES_DIR / "icons"
    THEMES_DIR: Path = RESOURCES_DIR / "themes"
    TEMPLATES_DIR: Path = RESOURCES_DIR / "templates"
    CONFIG_DIR: Path = RESOURCES_DIR / "config"
    
    # User Data Directories
    USER_DATA_DIR: Path = Path.home() / ".reqif_tool_suite"
    USER_CONFIG_DIR: Path = USER_DATA_DIR / "config"
    USER_CACHE_DIR: Path = USER_DATA_DIR / "cache"
    USER_LOGS_DIR: Path = USER_DATA_DIR / "logs"
    USER_BACKUPS_DIR: Path = USER_DATA_DIR / "backups"
    USER_EXPORTS_DIR: Path = USER_DATA_DIR / "exports"
    USER_PLUGINS_DIR: Path = USER_DATA_DIR / "plugins"
    
    # Window Configuration
    DEFAULT_WINDOW_WIDTH: int = 1200
    DEFAULT_WINDOW_HEIGHT: int = 800
    MIN_WINDOW_WIDTH: int = 800
    MIN_WINDOW_HEIGHT: int = 600
    MAX_WINDOW_WIDTH: int = 2560
    MAX_WINDOW_HEIGHT: int = 1440
    
    # File Constraints
    MAX_FILE_SIZE: int = 500 * 1024 * 1024  # 500 MB
    MAX_FOLDER_FILES: int = 1000
    MAX_REQUIREMENTS_DISPLAY: int = 10000
    
    # Performance Settings
    DEFAULT_THREAD_COUNT: int = 4
    MAX_THREAD_COUNT: int = 16
    CACHE_SIZE_MB: int = 100
    MAX_RECENT_FILES: int = 20
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FILE_MAX_SIZE: int = 10 * 1024 * 1024  # 10 MB
    LOG_FILE_BACKUP_COUNT: int = 5
    
    # Network Settings
    REQUEST_TIMEOUT: int = 30
    MAX_RETRIES: int = 3
    USER_AGENT: str = f"{APP_NAME}/{VERSION}"


@dataclass
class FileFormat:
    """File format specification"""
    name: str
    extension: str
    description: str
    mime_type: str
    supports_compression: bool = False
    is_binary: bool = False


# Supported file formats
REQIF_FORMAT = FileFormat(
    name="ReqIF",
    extension=".reqif",
    description="Requirements Interchange Format",
    mime_type="application/xml",
    supports_compression=False,
    is_binary=False
)

REQIFZ_FORMAT = FileFormat(
    name="ReqIF Archive",
    extension=".reqifz", 
    description="Compressed ReqIF Archive",
    mime_type="application/zip",
    supports_compression=True,
    is_binary=True
)

CSV_FORMAT = FileFormat(
    name="CSV",
    extension=".csv",
    description="Comma Separated Values",
    mime_type="text/csv",
    supports_compression=False,
    is_binary=False
)

EXCEL_FORMAT = FileFormat(
    name="Excel",
    extension=".xlsx",
    description="Microsoft Excel Workbook",
    mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    supports_compression=True,
    is_binary=True
)

JSON_FORMAT = FileFormat(
    name="JSON",
    extension=".json",
    description="JavaScript Object Notation",
    mime_type="application/json",
    supports_compression=False,
    is_binary=False
)

PDF_FORMAT = FileFormat(
    name="PDF",
    extension=".pdf",
    description="Portable Document Format",
    mime_type="application/pdf",
    supports_compression=False,
    is_binary=True
)

# List of all supported formats
SUPPORTED_FORMATS = [
    REQIF_FORMAT,
    REQIFZ_FORMAT,
    CSV_FORMAT,
    EXCEL_FORMAT,
    JSON_FORMAT,
    PDF_FORMAT
]

# Input formats (what we can read)
INPUT_FORMATS = [REQIF_FORMAT, REQIFZ_FORMAT]

# Output formats (what we can export to)
OUTPUT_FORMATS = [CSV_FORMAT, EXCEL_FORMAT, JSON_FORMAT, PDF_FORMAT]


class UIConstants:
    """User interface constants"""
    
    # Fonts
    DEFAULT_FONT_FAMILY = "Segoe UI"
    DEFAULT_FONT_SIZE = 9
    HEADER_FONT_SIZE = 12
    TITLE_FONT_SIZE = 16
    MONOSPACE_FONT_FAMILY = "Consolas"
    
    # Colors
    PRIMARY_COLOR = "#2563eb"
    SECONDARY_COLOR = "#64748b"
    SUCCESS_COLOR = "#059669"
    WARNING_COLOR = "#d97706"
    ERROR_COLOR = "#dc2626"
    INFO_COLOR = "#0891b2"
    LIGHT_COLOR = "#f8fafc"
    DARK_COLOR = "#0f172a"
    BORDER_COLOR = "#e2e8f0"
    
    # Status Colors
    ADDED_COLOR = "#dcfce7"     # Light green
    MODIFIED_COLOR = "#fef3c7"   # Light yellow
    DELETED_COLOR = "#fee2e2"    # Light red
    UNCHANGED_COLOR = "#f1f5f9"  # Light gray
    
    # Text Colors
    ADDED_TEXT_COLOR = "#15803d"
    MODIFIED_TEXT_COLOR = "#a16207"
    DELETED_TEXT_COLOR = "#dc2626"
    UNCHANGED_TEXT_COLOR = "#475569"
    
    # Icons (Unicode/Emoji)
    ICONS = {
        'app': '📋',
        'compare': '📊',
        'visualize': '📋',
        'file': '📄',
        'folder': '📁',
        'settings': '⚙️',
        'help': '❓',
        'about': 'ℹ️',
        'export': '📤',
        'import': '📥',
        'search': '🔍',
        'filter': '🔽',
        'refresh': '🔄',
        'back': '⬅️',
        'forward': '➡️',
        'up': '⬆️',
        'down': '⬇️',
        'close': '❌',
        'minimize': '➖',
        'maximize': '⬜',
        'success': '✅',
        'warning': '⚠️',
        'error': '❌',
        'info': 'ℹ️',
        'question': '❓',
        'loading': '⏳',
        'save': '💾',
        'open': '📂',
        'new': '📄',
        'edit': '✏️',
        'delete': '🗑️',
        'copy': '📋',
        'paste': '📄',
        'cut': '✂️',
        'undo': '↶',
        'redo': '↷'
    }
    
    # Padding and Margins
    SMALL_PADDING = 5
    MEDIUM_PADDING = 10
    LARGE_PADDING = 20
    
    # Widget Sizes
    BUTTON_WIDTH = 100
    BUTTON_HEIGHT = 30
    ENTRY_WIDTH = 200
    LISTBOX_HEIGHT = 10
    TEXT_AREA_HEIGHT = 20
    
    # Dialog Sizes
    SMALL_DIALOG_SIZE = (400, 300)
    MEDIUM_DIALOG_SIZE = (600, 450)
    LARGE_DIALOG_SIZE = (800, 600)
    EXTRA_LARGE_DIALOG_SIZE = (1000, 750)


class ComparisonConstants:
    """Constants for comparison operations"""
    
    # Comparison Modes
    BASIC_MODE = "basic"
    DETAILED_MODE = "detailed"
    FUZZY_MODE = "fuzzy"
    STRUCTURAL_MODE = "structural"
    
    # Matching Strategies
    ID_ONLY_MATCHING = "id_only"
    ID_AND_TEXT_MATCHING = "id_and_text"
    FUZZY_MATCHING = "fuzzy_matching"
    CONTENT_BASED_MATCHING = "content_based"
    
    # Similarity Thresholds
    DEFAULT_SIMILARITY_THRESHOLD = 0.8
    MIN_SIMILARITY_THRESHOLD = 0.1
    MAX_SIMILARITY_THRESHOLD = 1.0
    
    # Diff Limits
    MAX_DIFF_LINES = 1000
    MAX_DIFF_CONTEXT = 3
    
    # Performance Limits
    MAX_REQUIREMENTS_FOR_FUZZY = 5000
    BATCH_SIZE = 100


class AnalysisConstants:
    """Constants for analysis operations"""
    
    # Analysis Modes
    BASIC_ANALYSIS = "basic"
    DETAILED_ANALYSIS = "detailed"
    COMPREHENSIVE_ANALYSIS = "comprehensive"
    CUSTOM_ANALYSIS = "custom"
    
    # Quality Score Ranges
    EXCELLENT_QUALITY_MIN = 90
    GOOD_QUALITY_MIN = 70
    FAIR_QUALITY_MIN = 50
    POOR_QUALITY_MIN = 30
    
    # Text Analysis
    MIN_TEXT_LENGTH = 10
    IDEAL_TEXT_LENGTH_MIN = 50
    IDEAL_TEXT_LENGTH_MAX = 500
    MAX_TEXT_LENGTH = 2000
    
    # Readability
    IDEAL_READABILITY_MIN = 8
    IDEAL_READABILITY_MAX = 12
    
    # Complexity
    LOW_COMPLEXITY_MAX = 30
    IDEAL_COMPLEXITY_MIN = 20
    IDEAL_COMPLEXITY_MAX = 60
    HIGH_COMPLEXITY_MIN = 70


class ValidationConstants:
    """Constants for validation operations"""
    
    # File Validation
    REQUIRED_XML_ELEMENTS = ['REQ-IF', 'THE-HEADER', 'CORE-CONTENT']
    REQUIRED_NAMESPACES = ['http://www.omg.org/spec/ReqIF/20110401/reqif.xsd']
    
    # Requirement ID Patterns
    STANDARD_ID_PATTERN = r'^[A-Z]{2,}-\d+$'
    FLEXIBLE_ID_PATTERN = r'^[A-Za-z0-9_-]+$'
    
    # Attribute Requirements
    ESSENTIAL_ATTRIBUTES = ['TYPE', 'STATUS', 'PRIORITY']
    RECOMMENDED_ATTRIBUTES = ['DESCRIPTION', 'AUTHOR', 'CREATED', 'MODIFIED']


class ExportConstants:
    """Constants for export operations"""
    
    # CSV Export
    CSV_DELIMITER = ','
    CSV_QUOTE_CHAR = '"'
    CSV_ENCODING = 'utf-8-sig'  # With BOM for Excel compatibility
    
    # Excel Export
    EXCEL_MAX_ROWS = 1048576
    EXCEL_MAX_COLUMNS = 16384
    EXCEL_SHEET_NAME_MAX_LENGTH = 31
    
    # PDF Export
    PDF_PAGE_SIZE = 'A4'
    PDF_MARGIN = 20
    PDF_FONT_SIZE = 10
    PDF_TITLE_FONT_SIZE = 16
    
    # JSON Export
    JSON_INDENT = 2
    JSON_ENCODING = 'utf-8'


class NetworkConstants:
    """Constants for network operations"""
    
    # HTTP
    DEFAULT_TIMEOUT = 30
    MAX_RETRIES = 3
    RETRY_DELAY = 1.0
    
    # User Agent
    USER_AGENT = f"{AppConfig.APP_NAME}/{AppConfig.VERSION}"
    
    # API Endpoints (for future use)
    API_BASE_URL = "https://api.reqif-tools.com/v1"
    UPDATE_CHECK_URL = f"{API_BASE_URL}/version/check"
    FEEDBACK_URL = f"{API_BASE_URL}/feedback"


class SecurityConstants:
    """Security-related constants"""
    
    # File Security
    ALLOWED_EXTENSIONS = {'.reqif', '.reqifz'}
    BLOCKED_EXTENSIONS = {'.exe', '.bat', '.cmd', '.scr', '.pif', '.com'}
    
    # Path Security
    MAX_PATH_LENGTH = 260  # Windows limit
    FORBIDDEN_PATH_CHARS = ['<', '>', ':', '"', '|', '?', '*']
    
    # Content Security
    MAX_ATTRIBUTE_LENGTH = 10000
    MAX_TEXT_LENGTH = 100000


class LoggingConstants:
    """Logging configuration constants"""
    
    # Log Levels
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    
    # Log Formats
    DETAILED_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
    SIMPLE_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    CONSOLE_FORMAT = "%(levelname)s: %(message)s"
    
    # Log Files
    APP_LOG_FILE = "app.log"
    ERROR_LOG_FILE = "error.log"
    DEBUG_LOG_FILE = "debug.log"
    
    # Rotation
    MAX_LOG_SIZE = 10 * 1024 * 1024  # 10 MB
    MAX_LOG_FILES = 5


# Default application settings
DEFAULT_SETTINGS = {
    # General Settings
    'export_directory': str(AppConfig.USER_EXPORTS_DIR),
    'create_backups': True,
    'validate_files': True,
    'remember_recent_files': True,
    'recent_files_limit': 10,
    
    # Comparison Settings
    'comparison_mode': ComparisonConstants.DETAILED_MODE,
    'matching_strategy': ComparisonConstants.ID_ONLY_MATCHING,
    'ignore_whitespace': False,
    'case_sensitive': True,
    'include_attributes': True,
    'similarity_threshold': ComparisonConstants.DEFAULT_SIMILARITY_THRESHOLD,
    
    # Interface Settings
    'theme': 'default',
    'font_size': UIConstants.DEFAULT_FONT_SIZE,
    'remember_window_state': True,
    'confirm_exit': False,
    'show_tooltips': True,
    'show_status_bar': True,
    'animate_ui': True,
    
    # Analysis Settings
    'analysis_mode': AnalysisConstants.DETAILED_ANALYSIS,
    'include_text_analysis': True,
    'include_attribute_analysis': True,
    'include_quality_metrics': True,
    
    # Advanced Settings
    'log_level': LoggingConstants.INFO,
    'enable_file_logging': True,
    'cache_size_mb': AppConfig.CACHE_SIZE_MB,
    'max_threads': AppConfig.DEFAULT_THREAD_COUNT,
    'debug_mode': False,
    'verbose_logging': False,
    
    # Export Settings
    'default_export_format': 'csv',
    'include_timestamps': True,
    'csv_delimiter': ExportConstants.CSV_DELIMITER,
    'excel_include_charts': True,
    'pdf_include_images': True,
    
    # Performance Settings
    'enable_caching': True,
    'auto_save_interval': 300,  # 5 minutes
    'max_undo_levels': 50,
    
    # Privacy Settings
    'send_usage_statistics': False,
    'check_for_updates': True,
    'auto_update': False
}

# Environment-specific settings
DEVELOPMENT_SETTINGS = {
    'debug_mode': True,
    'log_level': LoggingConstants.DEBUG,
    'verbose_logging': True,
    'enable_file_logging': True,
    'send_usage_statistics': False
}

PRODUCTION_SETTINGS = {
    'debug_mode': False,
    'log_level': LoggingConstants.INFO,
    'verbose_logging': False,
    'enable_file_logging': True,
    'send_usage_statistics': True
}

# Temporary directory prefix
TEMP_DIR_PREFIX = "reqif_tool_"

# Application instance
APP_CONFIG = AppConfig()

# File type associations for dialogs
FILE_TYPE_FILTERS = {
    'reqif_files': [("ReqIF files", "*.reqif *.reqifz"), ("All files", "*.*")],
    'export_files': [
        ("CSV files", "*.csv"),
        ("Excel files", "*.xlsx"),
        ("JSON files", "*.json"),
        ("PDF files", "*.pdf"),
        ("All files", "*.*")
    ],
    'all_files': [("All files", "*.*")]
}

# Regular expressions for validation
REGEX_PATTERNS = {
    'requirement_id': ValidationConstants.STANDARD_ID_PATTERN,
    'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
    'version': r'^\d+\.\d+\.\d+$',
    'url': r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:\w*))?)?$'
}

# Error messages
ERROR_MESSAGES = {
    'file_not_found': "The specified file could not be found.",
    'invalid_format': "The file format is not supported or is corrupted.",
    'permission_denied': "Permission denied. Please check file permissions.",
    'disk_full': "Insufficient disk space to complete the operation.",
    'memory_error': "Insufficient memory to complete the operation.",
    'timeout_error': "The operation timed out. Please try again.",
    'network_error': "Network connection error. Please check your internet connection.",
    'unknown_error': "An unexpected error occurred. Please try again."
}

# Success messages
SUCCESS_MESSAGES = {
    'file_saved': "File saved successfully.",
    'export_complete': "Export completed successfully.",
    'comparison_complete': "Comparison completed successfully.",
    'analysis_complete': "Analysis completed successfully.",
    'settings_saved': "Settings saved successfully.",
    'backup_created': "Backup created successfully."
}

# Help URLs
HELP_URLS = {
    'user_guide': f"{AppConfig.GITHUB_URL}/wiki/User-Guide",
    'api_reference': f"{AppConfig.GITHUB_URL}/wiki/API-Reference",
    'troubleshooting': f"{AppConfig.GITHUB_URL}/wiki/Troubleshooting",
    'faq': f"{AppConfig.GITHUB_URL}/wiki/FAQ",
    'contact': f"{AppConfig.WEBSITE}/contact"
}

# Feature flags (for gradual rollout of new features)
FEATURE_FLAGS = {
    'enable_plugins': False,
    'enable_cloud_sync': False,
    'enable_collaboration': False,
    'enable_ai_suggestions': False,
    'enable_advanced_search': True,
    'enable_bulk_operations': True,
    'enable_custom_themes': False,
    'enable_scripting': False
}

def get_user_data_dir() -> Path:
    """Get the user data directory, creating it if necessary"""
    user_dir = APP_CONFIG.USER_DATA_DIR
    user_dir.mkdir(parents=True, exist_ok=True)
    return user_dir

def get_config_dir() -> Path:
    """Get the user configuration directory, creating it if necessary"""
    config_dir = APP_CONFIG.USER_CONFIG_DIR
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir

def get_cache_dir() -> Path:
    """Get the user cache directory, creating it if necessary"""
    cache_dir = APP_CONFIG.USER_CACHE_DIR
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir

def get_logs_dir() -> Path:
    """Get the user logs directory, creating it if necessary"""
    logs_dir = APP_CONFIG.USER_LOGS_DIR
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir

def get_backups_dir() -> Path:
    """Get the user backups directory, creating it if necessary"""
    backups_dir = APP_CONFIG.USER_BACKUPS_DIR
    backups_dir.mkdir(parents=True, exist_ok=True)
    return backups_dir

def is_development_mode() -> bool:
    """Check if running in development mode"""
    return os.getenv('REQIF_ENV', 'production').lower() == 'development'

def get_environment_settings() -> Dict[str, Any]:
    """Get environment-specific settings"""
    if is_development_mode():
        return {**DEFAULT_SETTINGS, **DEVELOPMENT_SETTINGS}
    else:
        return {**DEFAULT_SETTINGS, **PRODUCTION_SETTINGS}