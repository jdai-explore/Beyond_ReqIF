"""
Common Widgets Module
====================

This module provides reusable GUI components and widgets used throughout
the ReqIF Tool Suite interface. Includes status bars, progress dialogs,
file selectors, and specialized requirement display widgets.

Classes:
    StatusBar: Application status bar with progress indication
    ProgressDialog: Modal progress dialog with cancellation
    FileSelector: File/folder selection widget with validation
    RequirementTable: Advanced table widget for requirements
    DiffViewer: Text difference viewer with syntax highlighting
    SearchWidget: Advanced search widget with filters
    ToolTip: Tooltip widget for help text
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from typing import Optional, Callable, List, Dict, Any
import threading
import time
from datetime import datetime
import logging

from utils.logger import get_logger
from utils.helpers import format_file_size, format_timestamp

logger = get_logger(__name__)


class ToolTip:
    """
    Tooltip widget that shows help text on hover
    """
    
    def __init__(self, widget, text: str, delay: int = 500):
        """
        Initialize tooltip
        
        Args:
            widget: Widget to attach tooltip to
            text: Tooltip text to display
            delay: Delay in milliseconds before showing tooltip
        """
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tooltip_window = None
        self.timer_id = None
        
        # Bind events
        self.widget.bind('<Enter>', self.on_enter)
        self.widget.bind('<Leave>', self.on_leave)
        self.widget.bind('<Motion>', self.on_motion)
    
    def on_enter(self, event):
        """Handle mouse enter event"""
        self.schedule_tooltip(event)
    
    def on_leave(self, event):
        """Handle mouse leave event"""
        self.cancel_tooltip()
        self.hide_tooltip()
    
    def on_motion(self, event):
        """Handle mouse motion event"""
        self.cancel_tooltip()
        self.schedule_tooltip(event)
    
    def schedule_tooltip(self, event):
        """Schedule tooltip to appear after delay"""
        self.cancel_tooltip()
        self.timer_id = self.widget.after(self.delay, lambda: self.show_tooltip(event))
    
    def cancel_tooltip(self):
        """Cancel scheduled tooltip"""
        if self.timer_id:
            self.widget.after_cancel(self.timer_id)
            self.timer_id = None
    
    def show_tooltip(self, event):
        """Show the tooltip"""
        if self.tooltip_window:
            return
        
        x = event.x_root + 10
        y = event.y_root + 10
        
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(
            self.tooltip_window,
            text=self.text,
            background="lightyellow",
            relief="solid",
            borderwidth=1,
            font=("Arial", 9),
            justify=tk.LEFT
        )
        label.pack()
    
    def hide_tooltip(self):
        """Hide the tooltip"""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


class StatusBar:
    """
    Application status bar with message display and progress indication
    """
    
    def __init__(self, parent):
        """Initialize status bar"""
        self.parent = parent
        self.setup_statusbar()
    
    def setup_statusbar(self):
        """Setup the status bar widgets"""
        self.frame = ttk.Frame(self.parent, relief='sunken', borderwidth=1)
        
        # Status label
        self.status_var = tk.StringVar()
        self.status_label = ttk.Label(self.frame, textvariable=self.status_var)
        self.status_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Progress bar (initially hidden)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.frame, 
            variable=self.progress_var,
            mode='determinate',
            length=200
        )
        
        # Time label
        self.time_var = tk.StringVar()
        self.time_label = ttk.Label(self.frame, textvariable=self.time_var)
        self.time_label.pack(side=tk.RIGHT, padx=(0, 5))
        
        # Update time
        self.update_time()
    
    def set_status(self, message: str):
        """Set status message"""
        self.status_var.set(message)
        logger.debug("Status: %s", message)
    
    def show_progress(self, show: bool = True):
        """Show or hide progress bar"""
        if show:
            self.progress_bar.pack(side=tk.RIGHT, padx=(10, 10))
        else:
            self.progress_bar.pack_forget()
    
    def set_progress(self, value: float):
        """Set progress bar value (0-100)"""
        self.progress_var.set(value)
    
    def update_time(self):
        """Update time display"""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_var.set(current_time)
        # Schedule next update
        self.frame.after(1000, self.update_time)


class ProgressDialog:
    """
    Modal progress dialog with cancellation support
    """
    
    def __init__(self, parent, title: str, message: str, can_cancel: bool = True):
        """
        Initialize progress dialog
        
        Args:
            parent: Parent window
            title: Dialog title
            message: Progress message
            can_cancel: Whether dialog can be cancelled
        """
        self.parent = parent
        self.can_cancel = can_cancel
        self.cancelled = False
        
        self.setup_dialog(title, message)
    
    def setup_dialog(self, title: str, message: str):
        """Setup the progress dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(title)
        self.dialog.geometry("400x150")
        self.dialog.resizable(False, False)
        
        # Center dialog
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center on parent
        self.center_dialog()
        
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Message label
        self.message_var = tk.StringVar(value=message)
        message_label = ttk.Label(main_frame, textvariable=self.message_var)
        message_label.pack(pady=(0, 20))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            main_frame,
            variable=self.progress_var,
            mode='indeterminate',
            length=300
        )
        self.progress_bar.pack(pady=(0, 20))
        self.progress_bar.start()
        
        # Cancel button
        if self.can_cancel:
            cancel_button = ttk.Button(main_frame, text="Cancel", command=self.cancel)
            cancel_button.pack()
        
        # Handle window close
        self.dialog.protocol("WM_DELETE_WINDOW", self.cancel if self.can_cancel else lambda: None)
    
    def center_dialog(self):
        """Center dialog on parent window"""
        self.dialog.update_idletasks()
        
        # Get parent position and size
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        # Get dialog size
        dialog_width = self.dialog.winfo_width()
        dialog_height = self.dialog.winfo_height()
        
        # Calculate position
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.dialog.geometry(f"+{x}+{y}")
    
    def update_message(self, message: str):
        """Update progress message"""
        self.message_var.set(message)
        self.dialog.update()
    
    def update_progress(self, value: float):
        """Update progress value (0-100)"""
        self.progress_bar.config(mode='determinate')
        self.progress_var.set(value)
        self.dialog.update()
    
    def cancel(self):
        """Cancel the operation"""
        self.cancelled = True
        self.close()
    
    def close(self):
        """Close the dialog"""
        try:
            self.progress_bar.stop()
            self.dialog.destroy()
        except:
            pass  # Dialog may already be destroyed
    
    def is_cancelled(self) -> bool:
        """Check if operation was cancelled"""
        return self.cancelled


class FileSelector:
    """
    File/folder selection widget with validation and recent files
    """
    
    def __init__(self, parent, placeholder: str, callback: Callable, 
                 file_types: List = None, select_folders: bool = False):
        """
        Initialize file selector
        
        Args:
            parent: Parent widget
            placeholder: Placeholder text
            callback: Callback function when file is selected
            file_types: File types for dialog
            select_folders: Whether to select folders instead of files
        """
        self.parent = parent
        self.placeholder = placeholder
        self.callback = callback
        self.file_types = file_types or [("All files", "*.*")]
        self.select_folders = select_folders
        
        self.setup_widget()
    
    def setup_widget(self):
        """Setup the file selector widget"""
        # Main frame
        self.frame = ttk.Frame(self.parent)
        
        # Path entry
        self.path_var = tk.StringVar()
        self.path_entry = ttk.Entry(self.frame, textvariable=self.path_var, width=50)
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Browse button
        browse_text = "Browse Folder" if self.select_folders else "Browse File"
        self.browse_button = ttk.Button(self.frame, text=browse_text, command=self.browse)
        self.browse_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Bind events
        self.path_entry.bind('<Return>', self.on_path_entered)
        self.path_entry.bind('<FocusOut>', self.validate_path)
        
        # Set placeholder
        self.set_placeholder()
    
    def set_placeholder(self):
        """Set placeholder text"""
        self.path_var.set(self.placeholder)
        self.path_entry.config(foreground='gray')
        
        def on_focus_in(event):
            if self.path_var.get() == self.placeholder:
                self.path_var.set('')
                self.path_entry.config(foreground='black')
        
        def on_focus_out(event):
            if not self.path_var.get():
                self.set_placeholder()
        
        self.path_entry.bind('<FocusIn>', on_focus_in)
        self.path_entry.bind('<FocusOut>', on_focus_out)
    
    def browse(self):
        """Open file/folder browser"""
        try:
            if self.select_folders:
                path = filedialog.askdirectory(title="Select Folder")
            else:
                path = filedialog.askopenfilename(
                    title="Select File",
                    filetypes=self.file_types
                )
            
            if path:
                self.set_path(path)
                self.callback(path)
        
        except Exception as e:
            logger.error("Error in file browser: %s", str(e))
            messagebox.showerror("Error", f"Failed to open file browser: {str(e)}")
    
    def on_path_entered(self, event):
        """Handle path entered manually"""
        path = self.path_var.get().strip()
        if path and path != self.placeholder:
            if self.validate_path():
                self.callback(path)
    
    def validate_path(self, event=None) -> bool:
        """Validate the entered path"""
        path = self.path_var.get().strip()
        
        if not path or path == self.placeholder:
            return False
        
        path_obj = Path(path)
        
        if self.select_folders:
            valid = path_obj.exists() and path_obj.is_dir()
        else:
            valid = path_obj.exists() and path_obj.is_file()
        
        # Update entry color based on validation
        if valid:
            self.path_entry.config(foreground='black')
        else:
            self.path_entry.config(foreground='red')
        
        return valid
    
    def set_path(self, path: str):
        """Set the path programmatically"""
        self.path_entry.config(foreground='black')
        self.path_var.set(path)
    
    def get_path(self) -> Optional[str]:
        """Get the current path"""
        path = self.path_var.get().strip()
        return path if path != self.placeholder else None
    
    def grid(self, **kwargs):
        """Grid the widget"""
        self.frame.grid(**kwargs)
    
    def pack(self, **kwargs):
        """Pack the widget"""
        self.frame.pack(**kwargs)


class RequirementTable:
    """
    Advanced table widget for displaying requirements with sorting and filtering
    """
    
    def __init__(self, parent, columns: List[str], on_select: Callable = None):
        """
        Initialize requirement table
        
        Args:
            parent: Parent widget
            columns: List of column names
            on_select: Callback when row is selected
        """
        self.parent = parent
        self.columns = columns
        self.on_select = on_select
        self.data = []
        self.filtered_data = []
        self.sort_column = None
        self.sort_reverse = False
        
        self.setup_table()
    
    def setup_table(self):
        """Setup the table widget"""
        # Main frame
        self.frame = ttk.Frame(self.parent)
        
        # Create treeview
        self.tree = ttk.Treeview(self.frame, columns=self.columns, show='headings', height=15)
        
        # Configure columns
        for col in self.columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_by_column(c))
            self.tree.column(col, width=150, minwidth=100)
        
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
        
        # Bind events
        if self.on_select:
            self.tree.bind('<<TreeviewSelect>>', self.on_selection_changed)
    
    def load_data(self, data: List[List]):
        """Load data into the table"""
        self.data = data
        self.filtered_data = data.copy()
        self.refresh_display()
    
    def refresh_display(self):
        """Refresh the table display"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add data
        for row in self.filtered_data:
            self.tree.insert('', tk.END, values=row)
    
    def sort_by_column(self, column: str):
        """Sort table by column"""
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False
        
        # Get column index
        col_index = self.columns.index(column)
        
        # Sort data
        self.filtered_data.sort(key=lambda x: str(x[col_index]), reverse=self.sort_reverse)
        
        # Refresh display
        self.refresh_display()
        
        # Update column heading
        for col in self.columns:
            if col == column:
                direction = ' ↓' if self.sort_reverse else ' ↑'
                self.tree.heading(col, text=col + direction)
            else:
                self.tree.heading(col, text=col)
    
    def filter_data(self, filter_func: Callable):
        """Filter data using a filter function"""
        self.filtered_data = [row for row in self.data if filter_func(row)]
        self.refresh_display()
    
    def clear_filters(self):
        """Clear all filters"""
        self.filtered_data = self.data.copy()
        self.refresh_display()
    
    def on_selection_changed(self, event):
        """Handle selection change"""
        if self.on_select:
            selection = self.tree.selection()
            if selection:
                item = selection[0]
                values = self.tree.item(item, 'values')
                self.on_select(values)
    
    def get_selected_data(self):
        """Get selected row data"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            return self.tree.item(item, 'values')
        return None
    
    def pack(self, **kwargs):
        """Pack the widget"""
        self.frame.pack(**kwargs)
    
    def grid(self, **kwargs):
        """Grid the widget"""
        self.frame.grid(**kwargs)


class DiffViewer:
    """
    Text difference viewer with syntax highlighting
    """
    
    def __init__(self, parent):
        """Initialize diff viewer"""
        self.parent = parent
        self.setup_viewer()
    
    def setup_viewer(self):
        """Setup the diff viewer"""
        # Main frame
        self.frame = ttk.Frame(self.parent)
        
        # Text widget with scrollbar
        self.text_widget = tk.Text(self.frame, wrap=tk.WORD, font=('Courier', 10))
        scrollbar = ttk.Scrollbar(self.frame, orient=tk.VERTICAL, command=self.text_widget.yview)
        self.text_widget.configure(yscrollcommand=scrollbar.set)
        
        # Grid layout
        self.text_widget.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configure grid weights
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)
        
        # Configure tags for syntax highlighting
        self.text_widget.tag_configure("added", background="lightgreen", foreground="darkgreen")
        self.text_widget.tag_configure("removed", background="lightcoral", foreground="darkred")
        self.text_widget.tag_configure("context", foreground="black")
        self.text_widget.tag_configure("info", foreground="blue", font=('Courier', 10, 'bold'))
    
    def display_diff(self, diff_text: str):
        """Display diff text with highlighting"""
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete(1.0, tk.END)
        
        lines = diff_text.split('\n')
        
        for line in lines:
            if line.startswith('+++') or line.startswith('---') or line.startswith('@@'):
                # File info or hunk header
                self.text_widget.insert(tk.END, line + '\n', "info")
            elif line.startswith('+'):
                # Added line
                self.text_widget.insert(tk.END, line + '\n', "added")
            elif line.startswith('-'):
                # Removed line
                self.text_widget.insert(tk.END, line + '\n', "removed")
            else:
                # Context line
                self.text_widget.insert(tk.END, line + '\n', "context")
        
        self.text_widget.config(state=tk.DISABLED)
    
    def display_text(self, text: str):
        """Display plain text"""
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.insert(tk.END, text)
        self.text_widget.config(state=tk.DISABLED)
    
    def clear(self):
        """Clear the viewer"""
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.config(state=tk.DISABLED)
    
    def pack(self, **kwargs):
        """Pack the widget"""
        self.frame.pack(**kwargs)
    
    def grid(self, **kwargs):
        """Grid the widget"""
        self.frame.grid(**kwargs)


class SearchWidget:
    """
    Advanced search widget with filters and options
    """
    
    def __init__(self, parent, on_search: Callable, on_clear: Callable = None):
        """
        Initialize search widget
        
        Args:
            parent: Parent widget
            on_search: Callback when search is performed
            on_clear: Callback when search is cleared
        """
        self.parent = parent
        self.on_search = on_search
        self.on_clear = on_clear
        
        self.setup_widget()
    
    def setup_widget(self):
        """Setup the search widget"""
        # Main frame
        self.frame = ttk.LabelFrame(self.parent, text="Search", padding="5")
        
        # Search entry frame
        search_frame = ttk.Frame(self.frame)
        search_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Search entry
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=40)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Search button
        self.search_button = ttk.Button(search_frame, text="Search", command=self.perform_search)
        self.search_button.pack(side=tk.LEFT, padx=(5, 0))
        
        # Clear button
        self.clear_button = ttk.Button(search_frame, text="Clear", command=self.clear_search)
        self.clear_button.pack(side=tk.LEFT, padx=(5, 0))
        
        # Options frame
        options_frame = ttk.Frame(self.frame)
        options_frame.pack(fill=tk.X)
        
        # Search options
        self.case_sensitive_var = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Case sensitive", 
                       variable=self.case_sensitive_var).pack(side=tk.LEFT)
        
        self.whole_words_var = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Whole words", 
                       variable=self.whole_words_var).pack(side=tk.LEFT, padx=(10, 0))
        
        self.regex_var = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Regular expression", 
                       variable=self.regex_var).pack(side=tk.LEFT, padx=(10, 0))
        
        # Bind Enter key
        self.search_entry.bind('<Return>', lambda e: self.perform_search())
        
        # Bind real-time search (optional)
        # self.search_var.trace('w', lambda *args: self.perform_search())
    
    def perform_search(self):
        """Perform search"""
        search_term = self.search_var.get().strip()
        
        if search_term:
            search_options = {
                'case_sensitive': self.case_sensitive_var.get(),
                'whole_words': self.whole_words_var.get(),
                'regex': self.regex_var.get()
            }
            
            self.on_search(search_term, search_options)
    
    def clear_search(self):
        """Clear search"""
        self.search_var.set('')
        if self.on_clear:
            self.on_clear()
    
    def set_search_term(self, term: str):
        """Set search term programmatically"""
        self.search_var.set(term)
    
    def get_search_term(self) -> str:
        """Get current search term"""
        return self.search_var.get().strip()
    
    def pack(self, **kwargs):
        """Pack the widget"""
        self.frame.pack(**kwargs)
    
    def grid(self, **kwargs):
        """Grid the widget"""
        self.frame.grid(**kwargs)


class CollapsibleFrame:
    """
    Collapsible frame widget that can be expanded/collapsed
    """
    
    def __init__(self, parent, title: str, expanded: bool = True):
        """
        Initialize collapsible frame
        
        Args:
            parent: Parent widget
            title: Frame title
            expanded: Initial expanded state
        """
        self.parent = parent
        self.title = title
        self.expanded = expanded
        
        self.setup_frame()
    
    def setup_frame(self):
        """Setup the collapsible frame"""
        # Main frame
        self.main_frame = ttk.Frame(self.parent)
        
        # Header frame with toggle button
        self.header_frame = ttk.Frame(self.main_frame)
        self.header_frame.pack(fill=tk.X)
        
        # Toggle button
        self.toggle_button = ttk.Button(
            self.header_frame,
            text=self.get_toggle_text(),
            command=self.toggle,
            width=len(self.title) + 4
        )
        self.toggle_button.pack(side=tk.LEFT)
        
        # Content frame
        self.content_frame = ttk.Frame(self.main_frame)
        
        # Show/hide content based on initial state
        if self.expanded:
            self.content_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
    
    def get_toggle_text(self) -> str:
        """Get toggle button text"""
        arrow = "▼" if self.expanded else "▶"
        return f"{arrow} {self.title}"
    
    def toggle(self):
        """Toggle expanded/collapsed state"""
        self.expanded = not self.expanded
        
        # Update button text
        self.toggle_button.config(text=self.get_toggle_text())
        
        # Show/hide content
        if self.expanded:
            self.content_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        else:
            self.content_frame.pack_forget()
    
    def expand(self):
        """Expand the frame"""
        if not self.expanded:
            self.toggle()
    
    def collapse(self):
        """Collapse the frame"""
        if self.expanded:
            self.toggle()
    
    def pack(self, **kwargs):
        """Pack the widget"""
        self.main_frame.pack(**kwargs)
    
    def grid(self, **kwargs):
        """Grid the widget"""
        self.main_frame.grid(**kwargs)


# Utility functions for common widget operations

def create_labeled_entry(parent, label_text: str, entry_width: int = 20) -> tuple:
    """
    Create a labeled entry widget
    
    Args:
        parent: Parent widget
        label_text: Label text
        entry_width: Entry width
        
    Returns:
        Tuple of (frame, label, entry, variable)
    """
    frame = ttk.Frame(parent)
    
    label = ttk.Label(frame, text=label_text)
    label.pack(side=tk.LEFT)
    
    var = tk.StringVar()
    entry = ttk.Entry(frame, textvariable=var, width=entry_width)
    entry.pack(side=tk.LEFT, padx=(5, 0))
    
    return frame, label, entry, var


def create_button_frame(parent, buttons: List[Dict[str, Any]]) -> ttk.Frame:
    """
    Create a frame with multiple buttons
    
    Args:
        parent: Parent widget
        buttons: List of button specifications
                Each dict should have: 'text', 'command', and optional 'style'
        
    Returns:
        Button frame
    """
    frame = ttk.Frame(parent)
    
    for button_spec in buttons:
        button = ttk.Button(
            frame,
            text=button_spec['text'],
            command=button_spec['command']
        )
        
        if 'style' in button_spec:
            button.config(style=button_spec['style'])
        
        button.pack(side=tk.LEFT, padx=(0, 5))
    
    return frame


def show_info_dialog(parent, title: str, message: str, details: str = None):
    """
    Show an information dialog with optional details
    
    Args:
        parent: Parent window
        title: Dialog title
        message: Main message
        details: Optional detailed information
    """
    dialog = tk.Toplevel(parent)
    dialog.title(title)
    dialog.geometry("500x400" if details else "400x200")
    dialog.resizable(True, True)
    
    # Center dialog
    dialog.transient(parent)
    dialog.grab_set()
    
    main_frame = ttk.Frame(dialog, padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Message
    message_label = ttk.Label(main_frame, text=message, wraplength=450)
    message_label.pack(pady=(0, 20))
    
    # Details (if provided)
    if details:
        details_label = ttk.Label(main_frame, text="Details:")
        details_label.pack(anchor=tk.W)
        
        details_text = tk.Text(main_frame, wrap=tk.WORD, height=15)
        details_scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=details_text.yview)
        details_text.configure(yscrollcommand=details_scrollbar.set)
        
        details_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        details_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        details_text.insert(tk.END, details)
        details_text.config(state=tk.DISABLED)
    
    # OK button
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(side=tk.BOTTOM, pady=(20, 0))
    
    ttk.Button(button_frame, text="OK", command=dialog.destroy).pack()


def validate_number_entry(value: str, min_val: float = None, max_val: float = None) -> bool:
    """
    Validate numeric entry
    
    Args:
        value: String value to validate
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        
    Returns:
        True if valid number within range
    """
    if not value:
        return True  # Allow empty
    
    try:
        num_val = float(value)
        
        if min_val is not None and num_val < min_val:
            return False
        
        if max_val is not None and num_val > max_val:
            return False
        
        return True
    
    except ValueError:
        return False