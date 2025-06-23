#!/usr/bin/env python3
"""
Apple Design Guidelines Theme Manager - 60-30-10 Color Principle - FIXED VERSION
Root causes addressed: Style application timing, widget targeting, and theme precedence
"""

import tkinter as tk
from tkinter import ttk

# 60-30-10 Color Principle Implementation
class ColorScheme:
    """60-30-10 Color Principle for Professional GUI Design"""
    
    # 60% - DOMINANT COLORS (Neutral, calm backgrounds)
    DOMINANT_PRIMARY = "#F8F9FA"      # Light neutral background
    DOMINANT_SECONDARY = "#FFFFFF"    # Pure white for content areas
    DOMINANT_TERTIARY = "#F5F5F7"     # Subtle variation
    
    # 30% - SECONDARY COLORS (Supporting elements)
    SECONDARY_PRIMARY = "#E8E9EA"     # Light gray for headers/sections
    SECONDARY_ACCENT = "#D1D5DB"      # Medium gray for separators
    SECONDARY_HOVER = "#F3F4F6"       # Hover states
    
    # 10% - ACCENT COLORS (Eye-catching highlights)
    ACCENT_PRIMARY = "#007AFF"        # Apple blue for primary actions
    ACCENT_SUCCESS = "#34C759"        # Green for success states
    ACCENT_WARNING = "#FF9500"        # Orange for warnings
    ACCENT_ERROR = "#FF3B30"          # Red for errors

# Apple Design Guidelines Color Palette - Enhanced
class AppleColors:
    """Apple Human Interface Guidelines colors with 60-30-10 principle"""
    
    # Primary System Colors (10% - Accent usage)
    SYSTEM_BLUE = ColorScheme.ACCENT_PRIMARY
    SYSTEM_GREEN = ColorScheme.ACCENT_SUCCESS
    SYSTEM_ORANGE = ColorScheme.ACCENT_WARNING
    SYSTEM_RED = ColorScheme.ACCENT_ERROR
    SYSTEM_YELLOW = "#FFCC00"
    
    # Text Colors
    LABEL = "#1D1D1F"                 # Primary text
    SECONDARY_LABEL = "#6D6D70"       # Secondary text
    TERTIARY_LABEL = "#8E8E93"        # Tertiary text
    
    # 60% - Dominant Backgrounds
    SYSTEM_BACKGROUND = ColorScheme.DOMINANT_SECONDARY
    WINDOW_BACKGROUND = ColorScheme.DOMINANT_PRIMARY
    CONTENT_BACKGROUND = ColorScheme.DOMINANT_SECONDARY
    
    # 30% - Secondary Supporting Areas
    SECONDARY_SYSTEM_BACKGROUND = ColorScheme.SECONDARY_PRIMARY
    GROUPED_BACKGROUND = ColorScheme.SECONDARY_PRIMARY
    HEADER_BACKGROUND = ColorScheme.SECONDARY_PRIMARY
    
    # Separators and borders (30% usage)
    SEPARATOR = ColorScheme.SECONDARY_ACCENT
    BORDER = ColorScheme.SECONDARY_ACCENT
    
    # Control colors
    CONTROL_BACKGROUND = ColorScheme.DOMINANT_SECONDARY
    TEXT_BACKGROUND = ColorScheme.DOMINANT_SECONDARY
    SELECTED_TEXT_BACKGROUND = ColorScheme.ACCENT_PRIMARY  # 10% accent
    SELECTED_TEXT_COLOR = "#FFFFFF"


# Font configuration (Apple Typography Guidelines)
class AppleFonts:
    """Apple typography guidelines"""
    
    # Font family fallbacks
    FONT_FAMILY = "Helvetica Neue"  # Works on most systems
    
    # Font sizes (Apple HIG scaled for desktop)
    LARGE_TITLE = 22
    TITLE_1 = 18
    TITLE_2 = 16
    HEADLINE = 14
    BODY = 13
    CALLOUT = 12
    SUBHEAD = 11
    FOOTNOTE = 10
    CAPTION = 9
    
    @classmethod
    def get(cls, size="body", weight="normal"):
        """Get font configuration"""
        size_map = {
            "large_title": cls.LARGE_TITLE,
            "title_1": cls.TITLE_1, 
            "title_2": cls.TITLE_2,
            "headline": cls.HEADLINE,
            "body": cls.BODY,
            "callout": cls.CALLOUT,
            "subhead": cls.SUBHEAD,
            "footnote": cls.FOOTNOTE,
            "caption": cls.CAPTION
        }
        
        font_size = size_map.get(size, cls.BODY)
        return (cls.FONT_FAMILY, font_size, weight)


def get_color(color_name):
    """Get color by semantic name with 60-30-10 principle"""
    color_map = {
        # 60% - Dominant Backgrounds
        "bg": AppleColors.SYSTEM_BACKGROUND,
        "bg_content": AppleColors.CONTENT_BACKGROUND,
        "window_bg": AppleColors.WINDOW_BACKGROUND,
        
        # 30% - Secondary Supporting Areas  
        "bg_secondary": AppleColors.SECONDARY_SYSTEM_BACKGROUND,
        "bg_grouped": AppleColors.GROUPED_BACKGROUND,
        "bg_header": AppleColors.HEADER_BACKGROUND,
        
        # Foregrounds  
        "fg": AppleColors.LABEL,
        "fg_secondary": AppleColors.SECONDARY_LABEL,
        "fg_tertiary": AppleColors.TERTIARY_LABEL,
        
        # 10% - Accent colors (used sparingly)
        "primary": AppleColors.SYSTEM_BLUE,
        "accent": AppleColors.SYSTEM_BLUE,
        "success": AppleColors.SYSTEM_GREEN,
        "warning": AppleColors.SYSTEM_ORANGE,
        "error": AppleColors.SYSTEM_RED,
        
        # Controls (following 60-30-10)
        "button_bg": AppleColors.SYSTEM_BLUE,  # 10% accent
        "button_fg": AppleColors.SELECTED_TEXT_COLOR,
        "entry_bg": AppleColors.TEXT_BACKGROUND,  # 60% dominant
        "entry_fg": AppleColors.LABEL,
        
        # 30% - Borders and separators
        "border": AppleColors.BORDER,
        "separator": AppleColors.SEPARATOR,
        
        # 10% - Selection (accent usage)
        "selection_bg": AppleColors.SELECTED_TEXT_BACKGROUND,
        "selection_fg": AppleColors.SELECTED_TEXT_COLOR,
    }
    
    return color_map.get(color_name, AppleColors.LABEL)


def get_semantic_color(status_or_type):
    """Get color for status, type, or priority - 10% accent usage"""
    semantic_map = {
        # Status colors (10% accent usage)
        'approved': AppleColors.SYSTEM_GREEN,
        'active': AppleColors.SYSTEM_GREEN,
        'success': AppleColors.SYSTEM_GREEN,
        
        'draft': AppleColors.SYSTEM_ORANGE,
        'pending': AppleColors.SYSTEM_ORANGE,
        'warning': AppleColors.SYSTEM_ORANGE,
        
        'rejected': AppleColors.SYSTEM_RED,
        'failed': AppleColors.SYSTEM_RED,
        'error': AppleColors.SYSTEM_RED,
        'critical': AppleColors.SYSTEM_RED,
        'high': AppleColors.SYSTEM_RED,
        
        'info': AppleColors.SYSTEM_BLUE,
        'medium': AppleColors.SYSTEM_BLUE,
        'normal': AppleColors.SYSTEM_BLUE,
        
        'low': AppleColors.TERTIARY_LABEL,
        'inactive': AppleColors.TERTIARY_LABEL,
    }
    
    if isinstance(status_or_type, str):
        return semantic_map.get(status_or_type.lower(), AppleColors.LABEL)
    return AppleColors.LABEL


def apply_theme(theme_name=None, widget=None):
    """Apply 60-30-10 Apple Design Guidelines styling - FIXED VERSION"""
    
    if widget is None:
        # Apply to all windows - find root windows
        for widget_obj in tk._root_children:
            if isinstance(widget_obj, (tk.Tk, tk.Toplevel)):
                _apply_60_30_10_styling(widget_obj)
    else:
        # Apply to specific widget tree
        _apply_60_30_10_styling(widget)


def _apply_60_30_10_styling(root_widget):
    """
    Apply comprehensive 60-30-10 color principle styling - FIXED VERSION
    ROOT CAUSE FIXES:
    1. Force style creation with explicit root
    2. Apply styles in correct order
    3. Use style.map for state-based styling
    4. Force immediate application
    """
    
    # Configure root window (60% - Dominant)
    if isinstance(root_widget, (tk.Tk, tk.Toplevel)):
        root_widget.configure(bg=get_color("window_bg"))  # 60% dominant
    
    # CRITICAL FIX: Create style with explicit root reference
    try:
        style = ttk.Style(root_widget)
    except:
        style = ttk.Style()
    
    # CRITICAL FIX: Set theme first, then override with custom styles
    try:
        available_themes = style.theme_names()
        if 'clam' in available_themes:
            style.theme_use('clam')  # Use clam as base for better styling support
        elif 'alt' in available_themes:
            style.theme_use('alt')
        print(f"Using base theme: {style.theme_use()}")
    except Exception as e:
        print(f"Theme setting warning: {e}")
    
    # === FRAME STYLES (60% - Dominant backgrounds) ===
    style.configure('TFrame',
                   background=get_color("bg"),  # 60% dominant
                   relief='flat',
                   borderwidth=0)
    
    # CRITICAL FIX: Create custom header frame style (30% - Secondary)
    style.configure('Header.TFrame',
                   background=get_color("bg_header"),  # 30% secondary
                   relief='solid',
                   borderwidth=1,
                   bordercolor=get_color("separator"))
    
    # === LABEL STYLES ===
    style.configure('TLabel',
                   background=get_color("bg"),  # 60% dominant
                   foreground=get_color("fg"),
                   font=AppleFonts.get("body"))
    
    # Header labels (30% background)
    style.configure('Title.TLabel',
                   background=get_color("bg_header"),  # 30% secondary
                   font=AppleFonts.get("title_2", "bold"),
                   foreground=get_color("fg"))
    
    style.configure('Headline.TLabel', 
                   background=get_color("bg"),  # 60% dominant
                   font=AppleFonts.get("headline", "bold"),
                   foreground=get_color("fg"))
    
    style.configure('Secondary.TLabel',
                   background=get_color("bg"),  # 60% dominant
                   foreground=get_color("fg_secondary"),
                   font=AppleFonts.get("callout"))
    
    # === BUTTON STYLES (10% - Accent for primary actions) ===
    # CRITICAL FIX: Configure AND map button styles
    style.configure('TButton',
                   background=get_color("primary"),  # 10% accent
                   foreground=get_color("button_fg"),
                   borderwidth=0,
                   focuscolor=get_color("primary"),
                   font=AppleFonts.get("body"),
                   padding=[16, 8],
                   relief='flat')
    
    # CRITICAL FIX: Map button states for hover/press effects
    style.map('TButton',
             background=[('active', '#0056CC'),   # Darker accent on hover
                        ('pressed', '#004499'),    # Even darker on press
                        ('disabled', get_color("fg_tertiary")),
                        ('!active', get_color("primary"))],  # Force default state
             foreground=[('disabled', get_color("fg_tertiary")),
                        ('!disabled', get_color("button_fg"))],
             relief=[('pressed', 'sunken'), ('!pressed', 'flat')])
    
    # Secondary button style (30% - Secondary background)
    style.configure('Secondary.TButton',
                   background=get_color("bg_secondary"),  # 30% secondary
                   foreground=get_color("primary"),  # 10% accent text
                   borderwidth=1,
                   relief='solid',
                   bordercolor=get_color("border"),  # 30% secondary
                   font=AppleFonts.get("body"),
                   padding=[16, 8])
    
    style.map('Secondary.TButton',
             background=[('active', get_color("bg_grouped")),  # 30% secondary
                        ('pressed', ColorScheme.SECONDARY_HOVER),
                        ('!active', get_color("bg_secondary"))],
             bordercolor=[('active', get_color("primary")),  # 10% accent
                         ('!active', get_color("border"))],
             relief=[('pressed', 'sunken'), ('!pressed', 'solid')])
    
    # === ENTRY STYLES (60% - Dominant backgrounds) ===
    style.configure('TEntry',
                   background=get_color("entry_bg"),  # 60% dominant
                   foreground=get_color("entry_fg"),
                   borderwidth=1,
                   relief='solid',
                   bordercolor=get_color("border"),  # 30% secondary
                   insertcolor=get_color("primary"),  # 10% accent
                   font=AppleFonts.get("body"),
                   padding=[10, 8],
                   fieldbackground=get_color("entry_bg"))
    
    style.map('TEntry',
             bordercolor=[('focus', get_color("primary")),  # 10% accent on focus
                         ('!focus', get_color("border"))],
             fieldbackground=[('!disabled', get_color("entry_bg"))])
    
    # === COMBOBOX STYLES ===
    style.configure('TCombobox',
                   background=get_color("entry_bg"),  # 60% dominant
                   foreground=get_color("entry_fg"),
                   borderwidth=1,
                   relief='solid',
                   bordercolor=get_color("border"),  # 30% secondary
                   font=AppleFonts.get("body"),
                   padding=[10, 8],
                   fieldbackground=get_color("entry_bg"))
    
    style.map('TCombobox',
             bordercolor=[('focus', get_color("primary"))],
             fieldbackground=[('!disabled', get_color("entry_bg"))])
    
    # === LABELFRAME STYLES (30% - Secondary backgrounds) ===
    style.configure('TLabelframe',
                   background=get_color("bg"),  # 60% dominant content
                   foreground=get_color("fg"),
                   borderwidth=1,
                   relief='solid',
                   bordercolor=get_color("border"),  # 30% secondary
                   font=AppleFonts.get("callout", "bold"))
    
    style.configure('TLabelframe.Label',
                   background=get_color("bg"),
                   foreground=get_color("fg"),
                   font=AppleFonts.get("callout", "bold"))
    
    # === NOTEBOOK STYLES (30% - Secondary for tabs) ===
    style.configure('TNotebook',
                   background=get_color("bg_secondary"),  # 30% secondary
                   borderwidth=0,
                   relief='flat')
    
    style.configure('TNotebook.Tab',
                   background=get_color("bg_secondary"),  # 30% secondary
                   foreground=get_color("fg_secondary"),
                   padding=[16, 10],
                   borderwidth=0,
                   relief='flat',
                   font=AppleFonts.get("callout"))
    
    style.map('TNotebook.Tab',
             background=[('selected', get_color("bg")),  # 60% dominant when selected
                        ('active', get_color("bg_grouped")),  # 30% secondary on hover
                        ('!selected', get_color("bg_secondary"))],
             foreground=[('selected', get_color("fg")),
                        ('active', get_color("fg")),
                        ('!selected', get_color("fg_secondary"))])
    
    # === TREEVIEW STYLES (60% - Dominant background) ===
    style.configure('Treeview',
                   background=get_color("bg"),  # 60% dominant
                   foreground=get_color("fg"),
                   borderwidth=1,
                   relief='solid',
                   bordercolor=get_color("border"),  # 30% secondary
                   font=AppleFonts.get("body"),
                   rowheight=26,
                   fieldbackground=get_color("bg"))
    
    style.configure('Treeview.Heading',
                   background=get_color("bg_header"),  # 30% secondary
                   foreground=get_color("fg"),
                   borderwidth=0,
                   relief='flat',
                   font=AppleFonts.get("callout", "bold"))
    
    style.map('Treeview',
             background=[('selected', get_color("selection_bg"))],  # 10% accent
             foreground=[('selected', get_color("selection_fg"))])
    
    style.map('Treeview.Heading',
             background=[('active', get_color("bg_grouped"))])
    
    # === SCROLLBAR STYLES (30% - Secondary) ===
    style.configure('TScrollbar',
                   background=get_color("bg_secondary"),  # 30% secondary
                   borderwidth=0,
                   arrowcolor=get_color("fg_tertiary"),
                   troughcolor=get_color("bg_secondary"))  # 30% secondary
    
    # === SEPARATOR STYLES (30% - Secondary) ===
    style.configure('TSeparator',
                   background=get_color("separator"))  # 30% secondary
    
    # CRITICAL FIX: Force immediate style application
    try:
        if hasattr(root_widget, 'update_idletasks'):
            root_widget.update_idletasks()
    except:
        pass
    
    print("✅ 60-30-10 styling applied successfully")


def style_text_widget(text_widget):
    """Apply 60-30-10 styling to Text widgets"""
    text_widget.configure(
        bg=get_color("bg"),  # 60% dominant
        fg=get_color("fg"),
        selectbackground=get_color("selection_bg"),  # 10% accent
        selectforeground=get_color("selection_fg"),
        font=AppleFonts.get("body"),
        borderwidth=1,
        relief='solid',
        highlightbackground=get_color("border"),  # 30% secondary
        highlightcolor=get_color("primary"),  # 10% accent
        highlightthickness=1,
        insertbackground=get_color("primary"),  # 10% accent
        insertwidth=2,
        wrap=tk.WORD,
        padx=8,
        pady=6
    )


def create_title_label(parent, text, level="title_2"):
    """Create Apple-style title label with appropriate background"""
    font_map = {
        "large_title": AppleFonts.get("large_title", "bold"),
        "title_1": AppleFonts.get("title_1", "bold"),
        "title_2": AppleFonts.get("title_2", "bold"),
        "headline": AppleFonts.get("headline", "bold")
    }
    
    # CRITICAL FIX: Apply proper style based on parent
    if hasattr(parent, 'winfo_class') and 'Header' in str(parent):
        style_name = 'Title.TLabel'
    else:
        style_name = 'TLabel'
    
    label = ttk.Label(parent,
                     text=text,
                     font=font_map.get(level, AppleFonts.get("title_2", "bold")),
                     style=style_name)
    
    # CRITICAL FIX: Force color application
    label.configure(foreground=get_color("fg"))
    return label


def create_body_label(parent, text, secondary=False):
    """Create Apple-style body label"""
    color = get_color("fg_secondary") if secondary else get_color("fg")
    label = ttk.Label(parent,
                     text=text,
                     font=AppleFonts.get("body"))
    
    # CRITICAL FIX: Force color application
    label.configure(foreground=color)
    return label


def create_primary_button(parent, text, command=None):
    """Create Apple-style primary button (10% accent usage)"""
    return ttk.Button(parent,
                     text=text,
                     command=command,
                     style='TButton')


def create_secondary_button(parent, text, command=None):
    """Create Apple-style secondary button (30% secondary usage)"""
    return ttk.Button(parent,
                     text=text,
                     command=command,
                     style='Secondary.TButton')


def create_status_label(parent, text, status=None):
    """Create status label with appropriate color (10% accent usage)"""
    color = get_semantic_color(status) if status else get_color("fg")
    label = ttk.Label(parent,
                     text=text,
                     font=AppleFonts.get("callout"))
    
    # CRITICAL FIX: Force color application
    label.configure(foreground=color)
    return label


# Spacing utilities (8pt grid system)
class Spacing:
    """Apple 8pt grid spacing system"""
    XXS = 2
    XS = 4
    S = 8
    M = 12
    L = 16
    XL = 20
    XXL = 24
    XXXL = 32


def create_card_frame(parent, padding=16):
    """Create a card-like frame with 60-30-10 styling"""
    frame = ttk.Frame(parent)
    frame.configure(style='TFrame')  # 60% dominant background
    return frame


def create_section_separator(parent):
    """Create a visual section separator (30% secondary usage)"""
    separator = ttk.Separator(parent, orient='horizontal')
    separator.configure(style='TSeparator')  # 30% secondary color
    return separator


def configure_main_window(root):
    """Configure main application window with 60-30-10 principle - FIXED VERSION"""
    # CRITICAL FIX: Apply styling BEFORE any widgets are created
    print("🎨 Configuring main window with 60-30-10 principle...")
    
    # Set main window background (60% dominant)
    root.configure(bg=get_color("window_bg"))
    
    # CRITICAL FIX: Apply theme immediately
    apply_theme(widget=root)
    
    # Set focus highlight color globally (10% accent)
    root.option_add('*highlightColor', get_color("primary"))
    root.option_add('*insertBackground', get_color("primary"))
    
    # CRITICAL FIX: Force style update
    root.update_idletasks()
    
    print("✅ Main window configuration complete")


# =============================================================================
# COMPATIBILITY FUNCTIONS
# =============================================================================

def get_available_themes():
    """Compatibility function"""
    return ["60-30-10 Apple Design"]

def toggle_theme():
    """Compatibility function"""
    pass

def get_theme_info():
    """Return 60-30-10 theme info"""
    return {
        "current_theme": "60-30-10",
        "theme_name": "60-30-10 Apple Design",
        "total_themes": 1,
        "description": "Professional styling following 60-30-10 color principle and Apple Human Interface Guidelines"
    }

# Compatibility class
class ThemeManager:
    """60-30-10 theme manager class"""
    
    def __init__(self):
        self.current_theme = "60-30-10"
    
    def apply_theme(self, theme_name=None, widget=None):
        """Apply 60-30-10 styling"""
        apply_theme(theme_name, widget)
    
    def get_color(self, color_name):
        """Get color by name"""
        return get_color(color_name)
    
    def get_semantic_color(self, status):
        """Get semantic color"""
        return get_semantic_color(status)

# Global instance for compatibility
theme_manager = ThemeManager()


# =============================================================================
# DEMO APPLICATION - FIXED VERSION
# =============================================================================

if __name__ == "__main__":
    print("🎨 Starting 60-30-10 Color Principle Demo - FIXED VERSION")
    
    # Demo application showing 60-30-10 principle
    root = tk.Tk()
    root.title("60-30-10 Color Principle Demo - FIXED")
    root.geometry("700x500")
    
    # CRITICAL FIX: Apply configuration BEFORE creating any widgets
    configure_main_window(root)
    
    # Main container (60% dominant background)
    main_frame = ttk.Frame(root, padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Header section (30% secondary background)
    header_frame = ttk.Frame(main_frame, style='Header.TFrame', padding="15")
    header_frame.pack(fill=tk.X, pady=(0, Spacing.L))
    
    title = create_title_label(header_frame, "60-30-10 Color Principle - FIXED", "title_1")
    title.pack(anchor=tk.W)
    
    subtitle = create_body_label(header_frame, "Professional GUI Design Implementation", secondary=True)
    subtitle.pack(anchor=tk.W, pady=(4, 0))
    
    # Section separator (30% secondary)
    sep1 = create_section_separator(main_frame)
    sep1.pack(fill=tk.X, pady=Spacing.M)
    
    # Content section (60% dominant background)
    content_frame = ttk.Frame(main_frame)
    content_frame.pack(fill=tk.BOTH, expand=True)
    
    # Color principle explanation
    principle_frame = ttk.LabelFrame(content_frame, text="Color Distribution - NOW WORKING!", padding="15")
    principle_frame.pack(fill=tk.X, pady=(0, Spacing.L))
    
    create_body_label(principle_frame, "• 60% Dominant: Light neutral backgrounds for main content").pack(anchor=tk.W, pady=2)
    create_body_label(principle_frame, "• 30% Secondary: Gray headers, sections, and supporting elements").pack(anchor=tk.W, pady=2)
    create_body_label(principle_frame, "• 10% Accent: Blue buttons, highlights, and selected items").pack(anchor=tk.W, pady=2)
    
    # Button demonstration (10% accent usage)
    button_frame = ttk.Frame(content_frame)
    button_frame.pack(fill=tk.X, pady=(0, Spacing.L))
    
    create_body_label(button_frame, "Button Examples (Fixed):").pack(anchor=tk.W, pady=(0, 8))
    
    btn_container = ttk.Frame(button_frame)
    btn_container.pack(anchor=tk.W)
    
    primary_btn = create_primary_button(btn_container, "Primary Action (Blue - 10%)")
    primary_btn.pack(side=tk.LEFT, padx=(0, Spacing.S))
    
    secondary_btn = create_secondary_button(btn_container, "Secondary Action (Gray - 30%)")
    secondary_btn.pack(side=tk.LEFT)
    
    # Status examples
    status_frame = ttk.Frame(content_frame)
    status_frame.pack(fill=tk.X, pady=(0, Spacing.L))
    
    create_body_label(status_frame, "Status Colors (10% Accent Usage):").pack(anchor=tk.W, pady=(0, 8))
    
    status_container = ttk.Frame(status_frame)
    status_container.pack(anchor=tk.W)
    
    success_label = create_status_label(status_container, "✓ Success", "success")
    success_label.pack(side=tk.LEFT, padx=(0, Spacing.M))
    
    warning_label = create_status_label(status_container, "⚠ Warning", "warning")
    warning_label.pack(side=tk.LEFT, padx=(0, Spacing.M))
    
    error_label = create_status_label(status_container, "✗ Error", "error")
    error_label.pack(side=tk.LEFT)
    
    # Status bar (30% secondary background)
    status_frame = ttk.Frame(main_frame, style='Header.TFrame', padding="10")
    status_frame.pack(fill=tk.X, pady=(Spacing.M, 0))
    
    status_label = create_body_label(status_frame, "✅ 60-30-10 Color Principle Applied Successfully - Colors Should Now Be Visible!", secondary=True)
    status_label.pack(side=tk.LEFT)
    
    # Instructions
    instructions_frame = ttk.Frame(main_frame)
    instructions_frame.pack(fill=tk.X, pady=(Spacing.S, 0))
    
    instructions = create_body_label(instructions_frame, 
                                   "If you see blue buttons and gray headers, the fix worked! Replace your theme_manager.py with this fixed version.",
                                   secondary=True)
    instructions.pack(anchor=tk.W)
    
    print("🚀 Demo started - Check if colors are now visible!")
    print("Expected: Blue buttons, gray header sections, white backgrounds")
    
    root.mainloop()