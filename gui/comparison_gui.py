"""
Comparison GUI Module
====================

This module provides the graphical interface for comparing ReqIF files and folders.
It includes side-by-side comparison views, difference highlighting, and detailed
analysis of changes between requirements.

Classes:
    ComparisonGUI: Main comparison interface
    ComparisonResultsPanel: Panel for displaying comparison results
    DifferenceViewer: Widget for viewing requirement differences
    ComparisonSettingsPanel: Panel for comparison settings
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
from typing import Optional, Callable, Dict, Any, List
import logging
from datetime import datetime
import threading

# Import project modules
from .common_widgets import StatusBar, FileSelector, ProgressDialog, DiffViewer
from .dialogs import ErrorDialog, ProgressDialog as ProgressDlg
from core.reqif_comparator import ReqIFComparator, ComparisonOptions, ComparisonMode, MatchingStrategy
from core.file_manager import FileManager
from exporters.csv_exporter import CSVExporter
from exporters.json_exporter import JSONExporter
from utils.config import ConfigManager
from utils.logger import get_logger
from utils.helpers import format_timestamp, format_file_size

logger = get_logger(__name__)


class ComparisonSettingsPanel:
    """Panel for comparison settings and options"""
    
    def __init__(self, parent):
        self.parent = parent
        self.setup_panel()
        
        # Default options
        self.options = ComparisonOptions()
    
    def setup_panel(self):
        """Setup the settings panel"""
        self.frame = ttk.LabelFrame(self.parent, text="Comparison Settings", padding="5")
        
        # Comparison mode
        mode_frame = ttk.Frame(self.frame)
        mode_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(mode_frame, text="Mode:").pack(side=tk.LEFT)
        self.mode_var = tk.StringVar(value="detailed")
        mode_combo = ttk.Combobox(mode_frame, textvariable=self.mode_var, 
                                 values=["basic", "detailed", "fuzzy", "structural"],
                                 state="readonly", width=15)
        mode_combo.pack(side=tk.LEFT, padx=(5, 10))
        
        # Matching strategy
        ttk.Label(mode_frame, text="Matching:").pack(side=tk.LEFT)
        self.matching_var = tk.StringVar(value="id_only")
        matching_combo = ttk.Combobox(mode_frame, textvariable=self.matching_var,
                                     values=["id_only", "id_and_text", "fuzzy_matching", "content_based"],
                                     state="readonly", width=15)
        matching_combo.pack(side=tk.LEFT, padx=(5, 0))
        
        # Options checkboxes
        options_frame = ttk.Frame(self.frame)
        options_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.ignore_whitespace_var = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Ignore whitespace", 
                       variable=self.ignore_whitespace_var).pack(side=tk.LEFT)
        
        self.case_sensitive_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Case sensitive", 
                       variable=self.case_sensitive_var).pack(side=tk.LEFT, padx=(10, 0))
        
        self.include_attributes_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Include attributes", 
                       variable=self.include_attributes_var).pack(side=tk.LEFT, padx=(10, 0))
    
    def get_options(self) -> ComparisonOptions:
        """Get current comparison options"""
        mode_map = {
            "basic": ComparisonMode.BASIC,
            "detailed": ComparisonMode.DETAILED,
            "fuzzy": ComparisonMode.FUZZY,
            "structural": ComparisonMode.STRUCTURAL
        }
        
        matching_map = {
            "id_only": MatchingStrategy.ID_ONLY,
            "id_and_text": MatchingStrategy.ID_AND_TEXT,
            "fuzzy_matching": MatchingStrategy.FUZZY_MATCHING,
            "content_based": MatchingStrategy.CONTENT_BASED
        }
        
        return ComparisonOptions(
            mode=mode_map.get(self.mode_var.get(), ComparisonMode.DETAILED),
            matching_strategy=matching_map.get(self.matching_var.get(), MatchingStrategy.ID_ONLY),
            ignore_whitespace=self.ignore_whitespace_var.get(),
            case_sensitive=self.case_sensitive_var.get(),
            include_attributes=self.include_attributes_var.get()
        )


class ComparisonResultsPanel:
    """Panel for displaying comparison results"""
    
    def __init__(self, parent):
        self.parent = parent
        self.comparison_result = None
        
        self.setup_panel()
    
    def setup_panel(self):
        """Setup the results panel"""
        self.frame = ttk.LabelFrame(self.parent, text="Comparison Results", padding="5")
        
        # Results notebook
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Initially empty - tabs will be created when results are displayed
    
    def display_results(self, comparison_result):
        """Display comparison results"""
        self.comparison_result = comparison_result
        
        # Clear existing tabs
        for tab in self.notebook.tabs():
            self.notebook.forget(tab)
        
        if comparison_result is None:
            return
        
        # Check if this is a single file or folder comparison
        if hasattr(comparison_result, 'added'):
            # Single file comparison
            self._display_single_file_results(comparison_result)
        else:
            # Folder comparison (dictionary of results)
            self._display_folder_results(comparison_result)
    
    def _display_single_file_results(self, result):
        """Display results for single file comparison"""
        # Summary tab
        self._create_summary_tab(result)
        
        # Added requirements tab
        if result.added:
            self._create_requirements_tab("Added", result.added, "added")
        
        # Modified requirements tab
        if result.modified:
            self._create_modified_tab("Modified", result.modified)
        
        # Deleted requirements tab
        if result.deleted:
            self._create_requirements_tab("Deleted", result.deleted, "deleted")
        
        # Unchanged requirements tab (optional)
        if result.unchanged and len(result.unchanged) < 100:  # Don't show if too many
            self._create_requirements_tab("Unchanged", result.unchanged, "unchanged")
    
    def _display_folder_results(self, results):
        """Display results for folder comparison"""
        # Create overview tab
        self._create_folder_overview_tab(results)
        
        # Create tabs for files with changes
        changed_files = {name: result for name, result in results.items() 
                        if hasattr(result, 'added') and (result.added or result.modified or result.deleted)}
        
        for filename, result in list(changed_files.items())[:10]:  # Limit to first 10 files
            self._create_file_summary_tab(filename, result)
    
    def _create_summary_tab(self, result):
        """Create summary tab for single file comparison"""
        summary_frame = ttk.Frame(self.notebook)
        self.notebook.add(summary_frame, text="Summary")
        
        # Create text widget for summary
        summary_text = scrolledtext.ScrolledText(summary_frame, wrap=tk.WORD, height=20)
        summary_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Generate summary content
        summary_content = self._generate_summary_content(result)
        summary_text.insert(tk.END, summary_content)
        summary_text.config(state=tk.DISABLED)
    
    def _create_requirements_tab(self, tab_name, requirements, req_type):
        """Create tab for displaying requirements"""
        req_frame = ttk.Frame(self.notebook)
        self.notebook.add(req_frame, text=f"{tab_name} ({len(requirements)})")
        
        # Create treeview for requirements
        columns = ('ID', 'Text', 'Type', 'Status')
        tree = ttk.Treeview(req_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        tree.heading('ID', text='Requirement ID')
        tree.heading('Text', text='Text Preview')
        tree.heading('Type', text='Type')
        tree.heading('Status', text='Status')
        
        tree.column('ID', width=150, minwidth=100)
        tree.column('Text', width=400, minwidth=200)
        tree.column('Type', width=100, minwidth=80)
        tree.column('Status', width=100, minwidth=80)
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(req_frame, orient=tk.VERTICAL, command=tree.yview)
        h_scrollbar = ttk.Scrollbar(req_frame, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack widgets
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Populate tree
        for req_id, req in requirements.items():
            text_preview = req.text[:100] + "..." if len(req.text) > 100 else req.text
            req_type_attr = req.attributes.get('TYPE', req.attributes.get('type', ''))
            req_status_attr = req.attributes.get('STATUS', req.attributes.get('status', ''))
            
            tree.insert('', tk.END, values=(req_id, text_preview, req_type_attr, req_status_attr))
        
        # Configure colors based on type
        if req_type == "added":
            tree.tag_configure('added', background='lightgreen')
        elif req_type == "deleted":
            tree.tag_configure('deleted', background='lightcoral')
        elif req_type == "unchanged":
            tree.tag_configure('unchanged', background='lightgray')
        
        # Bind double-click to show details
        tree.bind('<Double-1>', lambda e: self._show_requirement_details(tree, requirements))
    
    def _create_modified_tab(self, tab_name, modified_requirements):
        """Create tab for modified requirements with diff view"""
        mod_frame = ttk.Frame(self.notebook)
        self.notebook.add(mod_frame, text=f"{tab_name} ({len(modified_requirements)})")
        
        # Create paned window for list and diff view
        paned = ttk.PanedWindow(mod_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - list of modified requirements
        list_frame = ttk.Frame(paned)
        paned.add(list_frame, weight=1)
        
        ttk.Label(list_frame, text="Modified Requirements:").pack(anchor=tk.W)
        
        self.mod_listbox = tk.Listbox(list_frame)
        self.mod_listbox.pack(fill=tk.BOTH, expand=True)
        
        # Populate listbox
        for req_id in modified_requirements.keys():
            self.mod_listbox.insert(tk.END, req_id)
        
        # Right panel - diff view
        diff_frame = ttk.Frame(paned)
        paned.add(diff_frame, weight=2)
        
        ttk.Label(diff_frame, text="Differences:").pack(anchor=tk.W)
        
        self.diff_viewer = DiffViewer(diff_frame)
        self.diff_viewer.pack(fill=tk.BOTH, expand=True)
        
        # Bind selection event
        self.mod_listbox.bind('<<ListboxSelect>>', 
                             lambda e: self._show_requirement_diff(modified_requirements))
    
    def _create_folder_overview_tab(self, results):
        """Create overview tab for folder comparison"""
        overview_frame = ttk.Frame(self.notebook)
        self.notebook.add(overview_frame, text="Overview")
        
        # Create treeview for file overview
        columns = ('File', 'Status', 'Added', 'Modified', 'Deleted', 'Total')
        tree = ttk.Treeview(overview_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(overview_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=v_scrollbar.set)
        
        # Pack widgets
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Populate tree
        for filename, result in results.items():
            if hasattr(result, 'stats') and result.stats:
                tree.insert('', tk.END, values=(
                    filename,
                    'Changed' if (result.stats.added_count > 0 or 
                                result.stats.modified_count > 0 or 
                                result.stats.deleted_count > 0) else 'Unchanged',
                    result.stats.added_count,
                    result.stats.modified_count,
                    result.stats.deleted_count,
                    result.stats.total_requirements_file1 + result.stats.total_requirements_file2
                ))
            else:
                tree.insert('', tk.END, values=(filename, 'Error', '', '', '', ''))
    
    def _create_file_summary_tab(self, filename, result):
        """Create summary tab for a specific file"""
        file_frame = ttk.Frame(self.notebook)
        self.notebook.add(file_frame, text=filename[:20] + "..." if len(filename) > 20 else filename)
        
        # File summary content
        summary_text = scrolledtext.ScrolledText(file_frame, wrap=tk.WORD, height=15)
        summary_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Generate file-specific summary
        content = f"File: {filename}\n"
        content += "=" * 50 + "\n\n"
        
        if hasattr(result, 'stats') and result.stats:
            content += f"Added Requirements: {result.stats.added_count}\n"
            content += f"Modified Requirements: {result.stats.modified_count}\n"
            content += f"Deleted Requirements: {result.stats.deleted_count}\n"
            content += f"Unchanged Requirements: {result.stats.unchanged_count}\n\n"
        
        # Show sample changes
        if hasattr(result, 'added') and result.added:
            content += "Sample Added Requirements:\n"
            content += "-" * 30 + "\n"
            for i, (req_id, req) in enumerate(list(result.added.items())[:5]):
                content += f"{req_id}: {req.text[:100]}...\n"
            content += "\n"
        
        summary_text.insert(tk.END, content)
        summary_text.config(state=tk.DISABLED)
    
    def _generate_summary_content(self, result):
        """Generate summary content for comparison result"""
        content = "ReqIF Comparison Summary\n"
        content += "=" * 50 + "\n\n"
        
        if hasattr(result, 'file1_info') and result.file1_info:
            content += f"File 1: {result.file1_info.name}\n"
        if hasattr(result, 'file2_info') and result.file2_info:
            content += f"File 2: {result.file2_info.name}\n"
        content += f"Comparison Time: {format_timestamp(datetime.now())}\n\n"
        
        if hasattr(result, 'stats') and result.stats:
            content += "STATISTICS\n"
            content += "-" * 20 + "\n"
            content += f"Total Requirements (File 1): {result.stats.total_requirements_file1}\n"
            content += f"Total Requirements (File 2): {result.stats.total_requirements_file2}\n"
            content += f"Added: {result.stats.added_count}\n"
            content += f"Modified: {result.stats.modified_count}\n"
            content += f"Deleted: {result.stats.deleted_count}\n"
            content += f"Unchanged: {result.stats.unchanged_count}\n"
            content += f"Comparison Time: {result.stats.comparison_time:.2f} seconds\n\n"
        
        # Add comparison settings
        content += "COMPARISON SETTINGS\n"
        content += "-" * 20 + "\n"
        content += f"Mode: {result.comparison_mode.value if hasattr(result, 'comparison_mode') else 'Unknown'}\n"
        content += f"Matching Strategy: {result.matching_strategy.value if hasattr(result, 'matching_strategy') else 'Unknown'}\n\n"
        
        return content
    
    def _show_requirement_details(self, tree, requirements):
        """Show detailed view of selected requirement"""
        selection = tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = tree.item(item, 'values')
        req_id = values[0]
        
        if req_id in requirements:
            req = requirements[req_id]
            
            # Create detail window
            detail_window = tk.Toplevel(self.parent)
            detail_window.title(f"Requirement Details - {req_id}")
            detail_window.geometry("800x600")
            
            # Create text widget
            text_widget = scrolledtext.ScrolledText(detail_window, wrap=tk.WORD)
            text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Add requirement details
            content = f"REQUIREMENT ID: {req_id}\n"
            content += "=" * 50 + "\n\n"
            content += f"TEXT:\n{req.text}\n\n"
            
            if req.attributes:
                content += "ATTRIBUTES:\n"
                content += "-" * 20 + "\n"
                for key, value in req.attributes.items():
                    content += f"{key}: {value}\n"
            
            text_widget.insert(tk.END, content)
            text_widget.config(state=tk.DISABLED)
    
    def _show_requirement_diff(self, modified_requirements):
        """Show diff for selected modified requirement"""
        selection = self.mod_listbox.curselection()
        if not selection:
            return
        
        req_id = self.mod_listbox.get(selection[0])
        if req_id in modified_requirements:
            diff_data = modified_requirements[req_id]
            
            if hasattr(diff_data, 'text_diff') and diff_data.text_diff:
                self.diff_viewer.display_diff(diff_data.text_diff)
            else:
                self.diff_viewer.display_text("No text differences found.")
