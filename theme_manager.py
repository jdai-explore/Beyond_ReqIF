#!/usr/bin/env python3
"""
Theme Manager Module
Handles professional theming, dark/light modes, and UI styling.
"""

import tkinter as tk
from tkinter import ttk
import json
import os


class ThemeManager:
    """Manages application themes and styling"""
    
    def __init__(self, root):
        self.root = root
        self.current_theme = "light"
        self.themes = self._initialize_themes()
        self.load_user_preferences()
        
    def _initialize_themes(self):
        """Initialize theme definitions"""
        return {
            "light": {
                "name": "Light Professional",
                "bg": "#FFFFFF",
                "fg": "#2C3E50",
                "select_bg": "#E3F2FD",
                "select_fg": "#1976D2",
                "accent": "#2196F3",
                "accent_hover": "#1976D2",
                "secondary": "#F5F5F5",
                "border": "#E0E0E0",
                "success": "#4CAF50",
                "warning": "#FF9800",
                "error": "#F44336",
                "text_bg": "#FAFAFA",
                "button_bg": "#2196F3",
                "button_fg": "#FFFFFF",
                "button_hover": "#1976D2",
                "header_bg": "#ECEFF1",
                "header_fg": "#263238",
                "tooltip_bg": "#263238",
                "tooltip_fg": "#FFFFFF"
            },
            "dark": {
                "name": "Dark Professional",
                "bg": "#1E1E1E",
                "fg": "#E0E0E0",
                "select_bg": "#2D2D2D",
                "select_fg": "#64B5F6",
                "accent": "#64B5F6",
                "accent_hover": "#42A5F5",
                "secondary": "#2D2D2D",
                "border": "#404040",
                "success": "#66BB6A",
                "warning": "#FFB74D",
                "error": "#EF5350",
                "text_bg": "#2D2D2D",
                "button_bg": "#64B5F6",
                "button_fg": "#FFFFFF",
                "button_hover": "#42A5F5",
                "header_bg": "#263238",
                "header_fg": "#ECEFF1",
                "tooltip_bg": "#37474F",
                "tooltip_fg": "#FFFFFF"
            },
            "blue": {
                "name": "Professional Blue",
                "bg": "#F8FAFF",
                "fg": "#1A237E",
                "select_bg": "#E8EAF6",
                "select_fg": "#3F51B5",
                "accent": "#3F51B5",
                "accent_hover": "#303F9F",
                "secondary": "#F3F4F6",
                "border": "#C5CAE9",
                "success": "#388E3C",
                "warning": "#F57C00",
                "error": "#D32F2F",
                "text_bg": "#FFFFFF",
                "button_bg": "#3F51B5",
                "button_fg": "#FFFFFF",
                "button_hover": "#303F9F",
                "header_bg": "#E8EAF6",
                "header_fg": "#1A237E",
                "tooltip_bg": "#1A237E",
                "tooltip_fg": "#FFFFFF"
            }
        }
    
    def apply_theme(self, theme_name=None):
        """Apply a theme to the application"""
        if theme_name:
            self.current_theme = theme_name
            
        theme = self.themes[self.current_theme]
        
        # Configure ttk styles
        style = ttk.Style()
        
        # Configure main window
        self.root.configure(bg=theme["bg"])
        
        # Configure ttk styles
        style.theme_use('clam')  # Use clam as base for better customization
        
        # Configure Notebook (tabs)
        style.configure('TNotebook', 
                       background=theme["bg"],
                       borderwidth=0)
        style.configure('TNotebook.Tab',
                       background=theme["secondary"],
                       foreground=theme["fg"],
                       padding=[20, 8],
                       focuscolor='none')
        style.map('TNotebook.Tab',
                 background=[('selected', theme["accent"]),
                           ('active', theme["accent_hover"])],
                 foreground=[('selected', theme["button_fg"]),
                           ('active', theme["button_fg"])])
        
        # Configure Frames
        style.configure('TFrame',
                       background=theme["bg"],
                       borderwidth=1,
                       relief='flat')
        
        # Configure Labels
        style.configure('TLabel',
                       background=theme["bg"],
                       foreground=theme["fg"])
        style.configure('Header.TLabel',
                       background=theme["header_bg"],
                       foreground=theme["header_fg"],
                       font=('Arial', 12, 'bold'))
        style.configure('Title.TLabel',
                       background=theme["bg"],
                       foreground=theme["accent"],
                       font=('Arial', 16, 'bold'))
        
        # Configure Buttons
        style.configure('TButton',
                       background=theme["button_bg"],
                       foreground=theme["button_fg"],
                       borderwidth=0,
                       focuscolor='none',
                       padding=[10, 5])
        style.map('TButton',
                 background=[('active', theme["button_hover"]),
                           ('pressed', theme["accent_hover"])])
        
        # Accent button style
        style.configure('Accent.TButton',
                       background=theme["accent"],
                       foreground=theme["button_fg"],
                       font=('Arial', 10, 'bold'),
                       padding=[15, 8])
        style.map('Accent.TButton',
                 background=[('active', theme["accent_hover"]),
                           ('pressed', theme["accent"])])
        
        # Configure Entry widgets
        style.configure('TEntry',
                       fieldbackground=theme["text_bg"],
                       background=theme["text_bg"],
                       foreground=theme["fg"],
                       borderwidth=1,
                       relief='solid',
                       bordercolor=theme["border"])
        style.map('TEntry',
                 bordercolor=[('focus', theme["accent"])])
        
        # Configure Treeview
        style.configure('Treeview',
                       background=theme["text_bg"],
                       foreground=theme["fg"],
                       fieldbackground=theme["text_bg"],
                       borderwidth=1,
                       relief='solid')
        style.configure('Treeview.Heading',
                       background=theme["header_bg"],
                       foreground=theme["header_fg"],
                       font=('Arial', 9, 'bold'))
        style.map('Treeview',
                 background=[('selected', theme["select_bg"])],
                 foreground=[('selected', theme["select_fg"])])
        
        # Configure LabelFrame
        style.configure('TLabelframe',
                       background=theme["bg"],
                       foreground=theme["fg"],
                       borderwidth=1,
                       relief='solid',
                       bordercolor=theme["border"])
        style.configure('TLabelframe.Label',
                       background=theme["bg"],
                       foreground=theme["accent"],
                       font=('Arial', 10, 'bold'))
        
        # Configure Scrollbar
        style.configure('TScrollbar',
                       background=theme["secondary"],
                       bordercolor=theme["border"],
                       arrowcolor=theme["fg"],
                       troughcolor=theme["secondary"])
        
        # Configure Progressbar
        style.configure('TProgressbar',
                       background=theme["accent"],
                       troughcolor=theme["secondary"],
                       borderwidth=0,
                       lightcolor=theme["accent"],
                       darkcolor=theme["accent"])
        
        # Store theme colors for custom widgets
        self.colors = theme
        
        # Save current theme
        self.save_user_preferences()
    
    def get_color(self, color_name):
        """Get a color from the current theme"""
        return self.colors.get(color_name, "#000000")
    
    def toggle_theme(self):
        """Toggle between light and dark themes"""
        if self.current_theme == "light":
            self.apply_theme("dark")
        else:
            self.apply_theme("light")
    
    def set_theme(self, theme_name):
        """Set a specific theme"""
        if theme_name in self.themes:
            self.apply_theme(theme_name)
    
    def get_available_themes(self):
        """Get list of available themes"""
        return [(name, data["name"]) for name, data in self.themes.items()]
    
    def save_user_preferences(self):
        """Save user theme preferences"""
        try:
            config_dir = os.path.expanduser("~/.reqif_tool")
            os.makedirs(config_dir, exist_ok=True)
            
            config_file = os.path.join(config_dir, "preferences.json")
            preferences = {
                "theme": self.current_theme
            }
            
            with open(config_file, 'w') as f:
                json.dump(preferences, f, indent=2)
        except Exception:
            pass  # Fail silently if can't save preferences
    
    def load_user_preferences(self):
        """Load user theme preferences"""
        try:
            config_file = os.path.expanduser("~/.reqif_tool/preferences.json")
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    preferences = json.load(f)
                    self.current_theme = preferences.get("theme", "light")
        except Exception:
            self.current_theme = "light"


class ToolTip:
    """Professional tooltip implementation"""
    
    def __init__(self, widget, text, delay=500):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tooltip_window = None
        self.timer_id = None
        
        # Bind events
        self.widget.bind('<Enter>', self.on_enter)
        self.widget.bind('<Leave>', self.on_leave)
        self.widget.bind('<Motion>', self.on_motion)
    
    def on_enter(self, event=None):
        """Mouse entered widget"""
        self.schedule_show()
    
    def on_leave(self, event=None):
        """Mouse left widget"""
        self.cancel_show()
        self.hide()
    
    def on_motion(self, event=None):
        """Mouse moved within widget"""
        self.cancel_show()
        self.schedule_show()
    
    def schedule_show(self):
        """Schedule tooltip to show after delay"""
        self.cancel_show()
        self.timer_id = self.widget.after(self.delay, self.show)
    
    def cancel_show(self):
        """Cancel scheduled tooltip show"""
        if self.timer_id:
            self.widget.after_cancel(self.timer_id)
            self.timer_id = None
    
    def show(self):
        """Show the tooltip"""
        if self.tooltip_window:
            return
        
        x = self.widget.winfo_rootx() + 25
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        
        # Get theme colors if available
        try:
            # Try to get theme from root window
            theme_manager = getattr(self.widget.winfo_toplevel(), 'theme_manager', None)
            if theme_manager:
                bg_color = theme_manager.get_color('tooltip_bg')
                fg_color = theme_manager.get_color('tooltip_fg')
            else:
                bg_color = "#263238"
                fg_color = "#FFFFFF"
        except:
            bg_color = "#263238"
            fg_color = "#FFFFFF"
        
        label = tk.Label(self.tooltip_window,
                        text=self.text,
                        background=bg_color,
                        foreground=fg_color,
                        font=('Arial', 9),
                        relief='solid',
                        borderwidth=1,
                        padx=8,
                        pady=4)
        label.pack()
    
    def hide(self):
        """Hide the tooltip"""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


def add_tooltip(widget, text, delay=500):
    """Convenience function to add tooltip to widget"""
    return ToolTip(widget, text, delay)


# Example usage
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Theme Manager Test")
    root.geometry("600x400")
    
    # Create theme manager
    theme_manager = ThemeManager(root)
    root.theme_manager = theme_manager  # Store reference
    
    # Apply initial theme
    theme_manager.apply_theme()
    
    # Create test widgets
    main_frame = ttk.Frame(root, padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Title
    title_label = ttk.Label(main_frame, text="Theme Manager Demo", style='Title.TLabel')
    title_label.pack(pady=(0, 20))
    
    # Theme selection
    theme_frame = ttk.Frame(main_frame)
    theme_frame.pack(fill=tk.X, pady=(0, 10))
    
    ttk.Label(theme_frame, text="Select Theme:").pack(side=tk.LEFT)
    
    for theme_id, theme_name in theme_manager.get_available_themes():
        btn = ttk.Button(theme_frame, text=theme_name,
                        command=lambda t=theme_id: theme_manager.set_theme(t))
        btn.pack(side=tk.LEFT, padx=(10, 0))
        add_tooltip(btn, f"Switch to {theme_name} theme")
    
    # Sample widgets
    sample_frame = ttk.LabelFrame(main_frame, text="Sample Widgets", padding="10")
    sample_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
    
    ttk.Label(sample_frame, text="Sample label").pack(anchor=tk.W)
    ttk.Entry(sample_frame, value="Sample entry").pack(fill=tk.X, pady=(5, 0))
    ttk.Button(sample_frame, text="Sample Button").pack(pady=(10, 0))
    ttk.Button(sample_frame, text="Accent Button", style='Accent.TButton').pack(pady=(5, 0))
    
    print("Theme Manager loaded successfully!")
    root.mainloop()