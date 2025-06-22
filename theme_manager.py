#!/usr/bin/env python3
"""
Minimal Theme Manager Stub - No Theming
Just provides empty functions for backward compatibility.
"""

# =============================================================================
# MINIMAL STUB FUNCTIONS - NO ACTUAL THEMING
# =============================================================================

def apply_theme(theme_name=None, widget=None):
    """No-op theme application"""
    pass

def get_color(color_name):
    """Return basic colors only"""
    basic_colors = {
        "bg": "#FFFFFF",
        "fg": "#000000", 
        "success": "#008000",
        "error": "#FF0000",
        "warning": "#FFA500",
        "accent": "#0066CC",
        "fg_secondary": "#666666"
    }
    return basic_colors.get(color_name, "#000000")

def get_available_themes():
    """No themes available"""
    return []

def toggle_theme():
    """No-op toggle"""
    pass

def get_theme_info():
    """Basic theme info"""
    return {
        "current_theme": "basic",
        "theme_name": "Basic",
        "total_themes": 0
    }

def set_adaptive_mode(mode):
    """No-op mode setting"""
    pass

def get_semantic_color(token):
    """Map to basic colors"""
    return get_color(token)

def enable_transitions(enabled=True):
    """No-op transitions"""
    pass

# Compatibility class
class ThemeManager:
    def __init__(self):
        pass
    
    def apply_theme(self, theme_name=None, widget=None):
        pass
    
    def get_color(self, color_name):
        return get_color(color_name)

# Global instance for compatibility
theme_manager = ThemeManager()