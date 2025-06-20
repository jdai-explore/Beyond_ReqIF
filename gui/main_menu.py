"""
Main Menu GUI Module
===================

This module provides the main application menu interface for the ReqIF Tool Suite.
It serves as the central navigation hub for accessing different tools and features.

Classes:
    MainMenuGUI: Main application menu interface
    RecentFilesPanel: Panel for displaying recent files
    QuickActionsPanel: Panel for quick actions and shortcuts
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from typing import Optional, Callable, Dict, Any, List
import logging
from datetime import datetime

# Import project modules
from .comparison_gui import ComparisonGUI
from .visualizer_gui import VisualizerGUI
from .common_widgets import StatusBar, FileSelector
from .dialogs import SettingsDialog, AboutDialog, ErrorDialog
from utils.config import ConfigManager
from utils.logger import get_logger
from utils.helpers import format_file_size, format_timestamp
from core.file_manager import FileManager

logger = get_logger(__name__)


class RecentFilesPanel:
    """Panel for displaying and managing recent files"""
    
    def __init__(self, parent, file_manager: FileManager, on_file_selected: Callable):
        self.parent = parent
        self.file_manager = file_manager
        self.on_file_selected = on_file_selected
        
        self.setup_panel()
        self.refresh_recent_files()
    
    def setup_panel(self):
        """Setup the recent files panel"""
        # Recent files frame
        self.frame = ttk.LabelFrame(self.parent, text="Recent Files", padding="10")
        
        # Create treeview for recent files
        columns = ('File', 'Path', 'Modified', 'Size')
        self.tree = ttk.Treeview(self.frame, columns=columns, show='headings', height=8)
        
        # Configure columns
        self.tree.heading('File', text='File Name')
        self.tree.heading('Path', text='Path')
        self.tree.heading('Modified', text='Last Modified')
        self.tree.heading('Size', text='Size')
        
        self.tree.column('File', width=200, minwidth=150)
        self.tree.column('Path', width=300, minwidth=200)
        self.tree.column('Modified', width=150, minwidth=100)
        self.tree.column('Size', width=100, minwidth=80)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(self.frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(self.frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Configure grid weights
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)
        
        # Buttons frame
        buttons_frame = ttk.Frame(self.frame)
        buttons_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Button(buttons_frame, text="Open Selected", 
                  command=self.open_selected_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Remove Selected", 
                  command=self.remove_selected_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Clear All", 
                  command=self.clear_all_files).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Refresh", 
                  command=self.refresh_recent_files).pack(side=tk.RIGHT)
        
        # Bind double-click event
        self.tree.bind('<Double-1>', lambda e: self.open_selected_file())
        
        # Context menu
        self.setup_context_menu()
    
    def setup_context_menu(self):
        """Setup right-click context menu"""
        self.context_menu = tk.Menu(self.tree, tearoff=0)
        self.context_menu.add_command(label="Open", command=self.open_selected_file)
        self.context_menu.add_command(label="Show in Explorer", command=self.show_in_explorer)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Remove from List", command=self.remove_selected_file)
        self.context_menu.add_command(label="Clear All", command=self.clear_all_files)
        
        def show_context_menu(event):
            try:
                self.context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.context_menu.grab_release()
        
        self.tree.bind('<Button-3>', show_context_menu)  # Right-click
    
    def refresh_recent_files(self):
        """Refresh the recent files display"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get recent files from file manager
        recent_files = self.file_manager.get_recent_files(limit=20)
        
        for file_info in recent_files:
            file_path = Path(file_info['path'])
            
            try:
                if file_path.exists():
                    stat = file_path.stat()
                    size_str = format_file_size(stat.st_size)
                    modified_str = format_timestamp(datetime.fromtimestamp(stat.st_mtime))
                else:
                    size_str = "N/A"
                    modified_str = "File not found"
                
                self.tree.insert('', tk.END, values=(
                    file_path.name,
                    str(file_path.parent),
                    modified_str,
                    size_str
                ), tags=('valid' if file_path.exists() else 'invalid',))
                
            except Exception as e:
                logger.warning("Error processing recent file %s: %s", file_path, str(e))
        
        # Configure tags
        self.tree.tag_configure('invalid', foreground='gray')
    
    def open_selected_file(self):
        """Open the selected file"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a file to open.")
            return
        
        item = selection[0]
        values = self.tree.item(item, 'values')
        file_name = values[0]
        file_dir = values[1]
        file_path = Path(file_dir) / file_name
        
        if not file_path.exists():
            messagebox.showerror("File Not Found", f"The file '{file_path}' no longer exists.")
            self.refresh_recent_files()
            return
        
        # Call the file selected callback
        self.on_file_selected(str(file_path))
    
    def remove_selected_file(self):
        """Remove selected file from recent files"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a file to remove.")
            return
        
        item = selection[0]
        values = self.tree.item(item, 'values')
        file_name = values[0]
        file_dir = values[1]
        file_path = Path(file_dir) / file_name
        
        # Remove from file manager
        self.file_manager.recent_files_manager.remove_recent_file(file_path)
        
        # Remove from tree
        self.tree.delete(item)
    
    def clear_all_files(self):
        """Clear all recent files"""
        if messagebox.askyesno("Clear All", "Are you sure you want to clear all recent files?"):
            self.file_manager.recent_files_manager.clear_recent_files()
            self.refresh_recent_files()
    
    def show_in_explorer(self):
        """Show selected file in system file explorer"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.tree.item(item, 'values')
        file_name = values[0]
        file_dir = values[1]
        file_path = Path(file_dir) / file_name
        
        if file_path.exists():
            import platform
            import subprocess
            
            try:
                if platform.system() == "Windows":
                    subprocess.run(["explorer", "/select,", str(file_path)])
                elif platform.system() == "Darwin":  # macOS
                    subprocess.run(["open", "-R", str(file_path)])
                else:  # Linux
                    subprocess.run(["xdg-open", str(file_path.parent)])
            except Exception as e:
                logger.error("Failed to show file in explorer: %s", str(e))
                messagebox.showerror("Error", "Failed to open file explorer.")


class QuickActionsPanel:
    """Panel for quick actions and shortcuts"""
    
    def __init__(self, parent, on_action: Callable):
        self.parent = parent
        self.on_action = on_action
        
        self.setup_panel()
    
    def setup_panel(self):
        """Setup the quick actions panel"""
        self.frame = ttk.LabelFrame(self.parent, text="Quick Actions", padding="10")
        
        # Action buttons
        actions = [
            ("Compare Two Files", "compare_files", "Quickly compare two ReqIF files"),
            ("Visualize File", "visualize_file", "Open and visualize a ReqIF file"),
            ("Browse Folder", "browse_folder", "Browse and compare entire folders"),
            ("Open Recent", "open_recent", "Open a recently used file"),
            ("Settings", "settings", "Configure application settings"),
            ("Help", "help", "View help and documentation")
        ]
        
        for i, (text, action, tooltip) in enumerate(actions):
            btn = ttk.Button(self.frame, text=text, 
                           command=lambda a=action: self.on_action(a))
            btn.grid(row=i//2, column=i%2, sticky=(tk.W, tk.E), 
                    padx=5, pady=2)
            
            # Add tooltip
            self.create_tooltip(btn, tooltip)
        
        # Configure grid weights
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)
    
    def create_tooltip(self, widget, text):
        """Create a tooltip for a widget"""
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = tk.Label(tooltip, text=text, background="lightyellow",
                           relief="solid", borderwidth=1, font=("Arial", 8))
            label.pack()
            
            widget.tooltip = tooltip
        
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip
        
        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)


class MainMenuGUI:
    """
    Main Menu GUI
    
    Provides the main application interface with navigation to different tools,
    recent files management, and quick actions.
    """
    
    def __init__(self, root: tk.Tk, config: ConfigManager):
        """
        Initialize the main menu GUI
        
        Args:
            root: Tkinter root window
            config: Configuration manager instance
        """
        self.root = root
        self.config = config
        self.file_manager = FileManager()
        
        # Current active GUI (comparison or visualizer)
        self.active_gui = None
        
        # Setup the interface
        self.setup_gui()
        
        logger.info("Main Menu GUI initialized")
    
    def setup_gui(self):
        """Setup the main menu interface"""
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.root.title("ReqIF Tool Suite - Main Menu")
        
        # Create main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create header
        self.create_header(main_container)
        
        # Create main content area
        content_frame = ttk.Frame(main_container)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        
        # Create tool selection area
        self.create_tool_selection(content_frame)
        
        # Create side panel with recent files and quick actions
        self.create_side_panel(content_frame)
        
        # Create status bar
        self.create_status_bar(main_container)
        
        # Configure grid weights
        content_frame.columnconfigure(0, weight=2)
        content_frame.columnconfigure(1, weight=1)
        content_frame.rowconfigure(0, weight=1)
    
    def create_header(self, parent):
        """Create the application header"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Application title
        title_label = ttk.Label(header_frame, text="ReqIF Tool Suite", 
                               font=('Segoe UI', 24, 'bold'))
        title_label.pack(side=tk.LEFT)
        
        # Version and menu buttons
        right_frame = ttk.Frame(header_frame)
        right_frame.pack(side=tk.RIGHT)
        
        # Version label
        version_label = ttk.Label(right_frame, text="v2.0.0", 
                                 font=('Segoe UI', 10), foreground='gray')
        version_label.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Menu buttons
        ttk.Button(right_frame, text="Settings", 
                  command=self.show_settings).pack(side=tk.RIGHT, padx=(0, 5))
        ttk.Button(right_frame, text="Help", 
                  command=self.show_help).pack(side=tk.RIGHT, padx=(0, 5))
        ttk.Button(right_frame, text="About", 
                  command=self.show_about).pack(side=tk.RIGHT, padx=(0, 5))
    
    def create_tool_selection(self, parent):
        """Create the main tool selection area"""
        tools_frame = ttk.Frame(parent)
        tools_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 20))
        
        # Description
        desc_label = ttk.Label(tools_frame, 
                              text="Choose a tool to work with ReqIF files:",
                              font=('Segoe UI', 12))
        desc_label.pack(pady=(0, 30))
        
        # Tool buttons container
        buttons_frame = ttk.Frame(tools_frame)
        buttons_frame.pack(expand=True)
        
        # Compare tool button
        self.create_tool_button(
            buttons_frame, 
            "📊", 
            "ReqIF Compare",
            "Compare two ReqIF files\nor folders side-by-side",
            self.open_compare_tool,
            row=0, column=0
        )
        
        # Visualizer tool button
        self.create_tool_button(
            buttons_frame,
            "📋", 
            "ReqIF Visualizer",
            "View and analyze ReqIF\nfiles in Excel-like format",
            self.open_visualizer,
            row=0, column=1
        )
        
        # Configure button frame
        buttons_frame.columnconfigure(0, weight=1)
        buttons_frame.columnconfigure(1, weight=1)
    
    def create_tool_button(self, parent, icon, title, description, command, row, column):
        """Create a tool selection button"""
        # Main button frame
        button_frame = ttk.Frame(parent, relief='raised', borderwidth=2)
        button_frame.grid(row=row, column=column, padx=20, pady=10, sticky=(tk.W, tk.E))
        
        # Icon
        icon_label = ttk.Label(button_frame, text=icon, font=('Segoe UI', 40))
        icon_label.pack(pady=(20, 10))
        
        # Title
        title_label = ttk.Label(button_frame, text=title, 
                               font=('Segoe UI', 14, 'bold'))
        title_label.pack()
        
        # Description
        desc_label = ttk.Label(button_frame, text=description, 
                              font=('Segoe UI', 10), justify=tk.CENTER)
        desc_label.pack(pady=(5, 15))
        
        # Action button
        action_btn = ttk.Button(button_frame, text=f"Open {title}", 
                               command=command, style="Accent.TButton")
        action_btn.pack(pady=(0, 20), padx=20)
        
        # Make entire frame clickable
        def on_click(event):
            command()
        
        for widget in [button_frame, icon_label, title_label, desc_label]:
            widget.bind('<Button-1>', on_click)
            widget.configure(cursor="hand2")
    
    def create_side_panel(self, parent):
        """Create the side panel with recent files and quick actions"""
        side_frame = ttk.Frame(parent)
        side_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Recent files panel
        self.recent_files_panel = RecentFilesPanel(
            side_frame, 
            self.file_manager, 
            self.on_recent_file_selected
        )
        self.recent_files_panel.frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Quick actions panel
        self.quick_actions_panel = QuickActionsPanel(
            side_frame,
            self.on_quick_action
        )
        self.quick_actions_panel.frame.pack(fill=tk.X)
    
    def create_status_bar(self, parent):
        """Create the status bar"""
        self.status_bar = StatusBar(parent)
        self.status_bar.frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(10, 0))
        
        # Set initial status
        self.status_bar.set_status("Ready")
    
    def open_compare_tool(self):
        """Open the ReqIF comparison tool"""
        try:
            self.status_bar.set_status("Opening comparison tool...")
            self.active_gui = ComparisonGUI(self.root, self.config, self.return_to_main_menu)
            logger.info("Opened comparison tool")
        except Exception as e:
            logger.error("Failed to open comparison tool: %s", str(e))
            ErrorDialog.show_error(self.root, "Failed to open comparison tool", str(e))
            self.status_bar.set_status("Error opening comparison tool")
    
    def open_visualizer(self):
        """Open the ReqIF visualizer"""
        try:
            self.status_bar.set_status("Opening visualizer...")
            self.active_gui = VisualizerGUI(self.root, self.config, self.return_to_main_menu)
            logger.info("Opened visualizer")
        except Exception as e:
            logger.error("Failed to open visualizer: %s", str(e))
            ErrorDialog.show_error(self.root, "Failed to open visualizer", str(e))
            self.status_bar.set_status("Error opening visualizer")
    
    def return_to_main_menu(self):
        """Return to the main menu from a tool"""
        try:
            # Cleanup active GUI
            if self.active_gui:
                if hasattr(self.active_gui, 'cleanup'):
                    self.active_gui.cleanup()
                self.active_gui = None
            
            # Recreate main menu
            self.setup_gui()
            
            # Refresh recent files
            self.recent_files_panel.refresh_recent_files()
            
            self.status_bar.set_status("Returned to main menu")
            logger.info("Returned to main menu")
            
        except Exception as e:
            logger.error("Error returning to main menu: %s", str(e))
            ErrorDialog.show_error(self.root, "Error returning to main menu", str(e))
    
    def on_recent_file_selected(self, file_path: str):
        """Handle recent file selection"""
        try:
            # Determine appropriate tool based on file or user choice
            choice = messagebox.askyesnocancel(
                "Open File",
                f"How would you like to open '{Path(file_path).name}'?\n\n"
                "Yes - Open in Visualizer\n"
                "No - Open in Comparison Tool\n"
                "Cancel - Don't open"
            )
            
            if choice is True:
                # Open in visualizer
                self.open_visualizer()
                if self.active_gui and hasattr(self.active_gui, 'load_file'):
                    self.active_gui.load_file(file_path)
            elif choice is False:
                # Open in comparison tool
                self.open_compare_tool()
                if self.active_gui and hasattr(self.active_gui, 'set_file1'):
                    self.active_gui.set_file1(file_path)
            
        except Exception as e:
            logger.error("Error opening recent file %s: %s", file_path, str(e))
            ErrorDialog.show_error(self.root, "Error opening file", str(e))
    
    def on_quick_action(self, action: str):
        """Handle quick action selection"""
        try:
            if action == "compare_files":
                self.open_compare_tool()
            elif action == "visualize_file":
                self.open_visualizer()
            elif action == "browse_folder":
                folder_path = filedialog.askdirectory(title="Select Folder to Browse")
                if folder_path:
                    self.open_compare_tool()
                    if self.active_gui and hasattr(self.active_gui, 'set_folder1'):
                        self.active_gui.set_folder1(folder_path)
            elif action == "open_recent":
                recent_files = self.file_manager.get_recent_files(limit=1)
                if recent_files:
                    self.on_recent_file_selected(recent_files[0]['path'])
                else:
                    messagebox.showinfo("No Recent Files", "No recent files available.")
            elif action == "settings":
                self.show_settings()
            elif action == "help":
                self.show_help()
                
        except Exception as e:
            logger.error("Error handling quick action %s: %s", action, str(e))
            ErrorDialog.show_error(self.root, f"Error with action '{action}'", str(e))
    
    def show_settings(self):
        """Show application settings dialog"""
        try:
            SettingsDialog(self.root, self.config)
        except Exception as e:
            logger.error("Error showing settings: %s", str(e))
            ErrorDialog.show_error(self.root, "Error opening settings", str(e))
    
    def show_about(self):
        """Show about dialog"""
        try:
            AboutDialog(self.root)
        except Exception as e:
            logger.error("Error showing about dialog: %s", str(e))
            ErrorDialog.show_error(self.root, "Error opening about dialog", str(e))
    
    def show_help(self):
        """Show help documentation"""
        try:
            import webbrowser
            help_url = "https://github.com/your-org/reqif-tool-suite/docs"
            webbrowser.open(help_url)
        except Exception as e:
            logger.error("Error opening help: %s", str(e))
            messagebox.showinfo("Help", 
                              "Help documentation is available at:\n"
                              "https://github.com/your-org/reqif-tool-suite/docs")
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            if self.active_gui and hasattr(self.active_gui, 'cleanup'):
                self.active_gui.cleanup()
            
            if hasattr(self, 'file_manager'):
                self.file_manager.cleanup()
            
            logger.info("Main Menu GUI cleanup completed")
            
        except Exception as e:
            logger.error("Error during main menu cleanup: %s", str(e))