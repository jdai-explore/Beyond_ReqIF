"""
ReqIF Tool Suite - GUI Module
=============================

This module contains all graphical user interface components for the ReqIF Tool Suite.
It provides a modern, intuitive interface for ReqIF file management, comparison,
and visualization.

Modules:
    main_menu: Main application menu and navigation
    comparison_gui: ReqIF file comparison interface
    visualizer_gui: ReqIF file visualization interface
    common_widgets: Reusable GUI components and widgets
    dialogs: Custom dialog boxes and windows
    themes: Theme management and styling

Classes:
    MainMenuGUI: Main application menu interface
    ComparisonGUI: File comparison interface
    VisualizerGUI: File visualization interface
    ThemeManager: Application theme management

Author: ReqIF Tool Suite Team
Version: 2.0.0
License: MIT
"""

from .main_menu import MainMenuGUI
from .comparison_gui import ComparisonGUI
from .visualizer_gui import VisualizerGUI
from .common_widgets import (
    StatusBar, ProgressDialog, FileSelector, 
    RequirementTable, DiffViewer, SearchWidget
)
from .dialogs import (
    SettingsDialog, AboutDialog, ErrorDialog,
    ProgressDialog, FileInfoDialog
)

# Version information
__version__ = "2.0.0"
__author__ = "ReqIF Tool Suite Team"
__email__ = "support@reqif-tools.com"

# Public API
__all__ = [
    # Main GUI classes
    "MainMenuGUI",
    "ComparisonGUI", 
    "VisualizerGUI",
    
    # Common widgets
    "StatusBar",
    "ProgressDialog",
    "FileSelector",
    "RequirementTable",
    "DiffViewer",
    "SearchWidget",
    
    # Dialogs
    "SettingsDialog",
    "AboutDialog",
    "ErrorDialog",
    "FileInfoDialog",
    
    # Utility functions
    "get_gui_version",
    "get_available_themes",
    "apply_theme",
]

def get_gui_version():
    """Get the version of the GUI module"""
    return __version__

def get_available_themes():
    """Get list of available GUI themes"""
    try:
        from .themes import ThemeManager
        theme_manager = ThemeManager()
        return theme_manager.get_available_themes()
    except ImportError:
        return ["default"]

def apply_theme(root, theme_name):
    """
    Apply a theme to the root window
    
    Args:
        root: Tkinter root window
        theme_name: Name of theme to apply
    """
    try:
        from .themes import ThemeManager
        theme_manager = ThemeManager()
        theme_manager.apply_theme(root, theme_name)
    except ImportError:
        pass  # Use default theme if themes module not available

# GUI Constants
DEFAULT_WINDOW_SIZE = (1200, 800)
MIN_WINDOW_SIZE = (800, 600)
DEFAULT_FONT_FAMILY = "Segoe UI"
DEFAULT_FONT_SIZE = 9

# Color scheme
COLORS = {
    'primary': '#2563eb',
    'secondary': '#64748b', 
    'success': '#059669',
    'warning': '#d97706',
    'error': '#dc2626',
    'info': '#0891b2',
    'light': '#f8fafc',
    'dark': '#0f172a',
    'border': '#e2e8f0'
}

# Icon mappings
ICONS = {
    'compare': '📊',
    'visualize': '📋',
    'file': '📄',
    'folder': '📁',
    'settings': '⚙️',
    'help': '❓',
    'export': '📤',
    'import': '📥',
    'search': '🔍',
    'refresh': '🔄',
    'back': '⬅️',
    'forward': '➡️',
    'close': '❌',
    'success': '✅',
    'warning': '⚠️',
    'error': '❌',
    'info': 'ℹ️'
}