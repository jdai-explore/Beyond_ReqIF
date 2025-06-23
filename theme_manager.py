#!/usr/bin/env python3
"""
Simplified Theme Manager - Universal Button Fix
Ensures button text is visible on ALL platforms including Mac
"""

import tkinter as tk
from tkinter import ttk
import sys

# Simple color definitions
COLORS = {
    'bg': '#FFFFFF',
    'fg': '#000000',
    'bg_secondary': '#F0F0F0',
    'fg_secondary': '#666666',
    'primary': '#0078D4',
    'success': '#107C10',
    'warning': '#FF8C00',
    'error': '#D13438',
    'border': '#D0D0D0'
}

def get_color(color_name):
    """Get color by name"""
    return COLORS.get(color_name, '#000000')

def get_semantic_color(status_or_type):
    """Get color for status"""
    status_map = {
        'success': COLORS['success'],
        'warning': COLORS['warning'],
        'error': COLORS['error'],
        'info': COLORS['primary']
    }
    if isinstance(status_or_type, str):
        return status_map.get(status_or_type.lower(), COLORS['fg'])
    return COLORS['fg']

def is_mac():
    """Check if running on macOS"""
    return sys.platform.startswith('darwin')

def apply_theme(widget=None, theme_name=None):
    """Apply basic theme - simplified"""
    # Just set basic window background
    if widget and hasattr(widget, 'configure'):
        try:
            widget.configure(bg=COLORS['bg'])
        except:
            pass

def configure_main_window(root):
    """Configure main window - simplified"""
    root.configure(bg=COLORS['bg'])

# FIXED: Universal button functions that work on ALL platforms
def create_primary_button(parent, text, command=None):
    """Create primary button that works on all platforms"""
    if is_mac():
        # Use ttk.Button for Mac with forced text color
        style = ttk.Style()
        
        # Configure primary button style for Mac
        style.configure('Primary.TButton',
                       foreground='white',
                       font=('Arial', 10, 'bold'),
                       padding=[15, 8])
        
        # Map states to ensure text stays visible
        style.map('Primary.TButton',
                 foreground=[('active', 'white'),
                            ('pressed', 'white'),
                            ('disabled', '#CCCCCC'),
                            ('!active', 'white')])
        
        button = ttk.Button(parent, text=text, command=command, style='Primary.TButton')
        
        # Force configure after creation
        try:
            button.configure(style='Primary.TButton')
        except:
            pass
        
    else:
        # Use tk.Button for Windows/Linux with explicit colors
        button = tk.Button(parent, text=text, command=command,
                          bg=COLORS['primary'], fg='white', font=('Arial', 10, 'bold'),
                          relief='flat', borderwidth=0, padx=15, pady=8,
                          activebackground='#005A9E', activeforeground='white',
                          disabledforeground='#CCCCCC')
    
    return button

def create_secondary_button(parent, text, command=None):
    """Create secondary button that works on all platforms"""
    if is_mac():
        # Use ttk.Button for Mac with forced text color
        style = ttk.Style()
        
        # Configure secondary button style for Mac
        style.configure('Secondary.TButton',
                       foreground='black',
                       font=('Arial', 10),
                       padding=[15, 8])
        
        # Map states to ensure text stays visible
        style.map('Secondary.TButton',
                 foreground=[('active', 'black'),
                            ('pressed', 'black'),
                            ('disabled', '#888888'),
                            ('!active', 'black')])
        
        button = ttk.Button(parent, text=text, command=command, style='Secondary.TButton')
        
        # Force configure after creation
        try:
            button.configure(style='Secondary.TButton')
        except:
            pass
        
    else:
        # Use tk.Button for Windows/Linux with explicit colors
        button = tk.Button(parent, text=text, command=command,
                          bg=COLORS['bg_secondary'], fg=COLORS['fg'], font=('Arial', 10),
                          relief='solid', borderwidth=1, padx=15, pady=8,
                          activebackground='#E0E0E0', activeforeground=COLORS['fg'],
                          disabledforeground='#888888')
    
    return button

# Helper functions
def create_title_label(parent, text, level="title"):
    """Create simple title label"""
    return tk.Label(parent, text=text, font=('Arial', 14, 'bold'), bg=COLORS['bg'], fg=COLORS['fg'])

def create_body_label(parent, text, secondary=False):
    """Create simple body label"""
    color = COLORS['fg_secondary'] if secondary else COLORS['fg']
    return tk.Label(parent, text=text, font=('Arial', 10), bg=COLORS['bg'], fg=color)

def create_section_separator(parent):
    """Create simple separator"""
    return ttk.Separator(parent, orient='horizontal')

def style_text_widget(text_widget):
    """Style text widget simply"""
    text_widget.configure(bg=COLORS['bg'], fg=COLORS['fg'], font=('Arial', 10))

# Compatibility classes
class Spacing:
    """Simple spacing values"""
    XS = 4
    S = 8
    M = 12
    L = 16
    XL = 20
    XXL = 24

class AppleColors:
    """Compatibility class"""
    WINDOW_BACKGROUND = COLORS['bg']
    SYSTEM_BACKGROUND = COLORS['bg']

class AppleFonts:
    """Compatibility class"""
    @staticmethod
    def get(size="body", weight="normal"):
        return ('Arial', 10, weight)

# Compatibility functions
def get_available_themes():
    return ["Default"]

def toggle_theme():
    pass

def get_theme_info():
    return {"current_theme": "Default", "theme_name": "Default"}

class ThemeManager:
    def __init__(self):
        self.current_theme = "Default"
    
    def apply_theme(self, theme_name=None, widget=None):
        apply_theme(widget, theme_name)
    
    def get_color(self, color_name):
        return get_color(color_name)
    
    def get_semantic_color(self, status):
        return get_semantic_color(status)

theme_manager = ThemeManager()

if __name__ == "__main__":
    # Test the button fixes
    root = tk.Tk()
    root.title(f"Universal Button Test - {sys.platform}")
    root.geometry("600x400")
    
    configure_main_window(root)
    
    frame = tk.Frame(root, bg=COLORS['bg'])
    frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    title = create_title_label(frame, "Universal Button Test")
    title.pack(pady=10)
    
    platform_info = create_body_label(frame, f"Platform: {sys.platform} | Mac Mode: {is_mac()}", secondary=True)
    platform_info.pack(pady=5)
    
    # Test buttons
    btn1 = create_primary_button(frame, "Primary Button - Should Have White Text on Blue")
    btn1.pack(pady=10)
    
    btn2 = create_secondary_button(frame, "Secondary Button - Should Have Black Text on Gray")
    btn2.pack(pady=10)
    
    # Instructions
    instructions = create_body_label(frame, 
                                   "Both buttons above should have clearly visible text.\n"
                                   "If text is invisible, there may be a platform-specific issue.",
                                   secondary=True)
    instructions.pack(pady=20)
    
    root.mainloop()