"""
Visualizer GUI Module
====================

This module provides the graphical interface for visualizing and analyzing ReqIF files.
It includes Excel-like table views, detailed requirement inspection, and comprehensive
statistical analysis with interactive charts and reports.

Classes:
    VisualizerGUI: Main visualizer interface
    RequirementTableView: Excel-like table view for requirements
    RequirementDetailsView: Detailed view of individual requirements
    StatisticsView: Statistical analysis and charts view
    SearchAndFilterPanel: Advanced search and filtering capabilities
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
from typing import Optional, Callable, Dict, Any, List
import logging
from datetime import datetime
import threading

# Import project modules
from .common_widgets import StatusBar, FileSelector, ProgressDialog, RequirementTable, SearchWidget
from .dialogs import ErrorDialog, ProgressDialog as ProgressDlg, FileInfoDialog
from core.reqif_parser import ReqIFParser
from core.reqif_analyzer import ReqIFAnalyzer, AnalysisOptions, AnalysisMode
from core.file_manager import FileManager
from exporters.csv_exporter import CSVExporter
from exporters.excel_exporter import ExcelExporter
from utils.config import ConfigManager
from utils.logger import get_logger
from utils.helpers import format_timestamp, format_file_size

logger = get_logger(__name__)


class SearchAndFilterPanel:
    """Panel for advanced search and filtering"""
    
    def __init__(self, parent, on_search_callback: Callable):
        self.parent = parent
        self.on_search_callback = on_search_callback
        
        self.setup_panel()
    
    def setup_panel(self):
        """Setup the search and filter panel"""
        self.frame = ttk.LabelFrame(self.parent, text="Search & Filter", padding="5")
        
        # Search controls
        search_frame = ttk.Frame(self.frame)
        search_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Search entry
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=(5, 5))
        
        # Search button
        ttk.Button(search_frame, text="Search", command=self.perform_search).pack(side=tk.LEFT)
        ttk.Button(search_frame, text="Clear", command=self.clear_search).pack(side=tk.LEFT, padx=(5, 0))
        
        # Filter controls
        filter_frame = ttk.Frame(self.frame)
        filter_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Filter by type
        ttk.Label(filter_frame, text="Type:").pack(side=tk.LEFT)
        self.type_var = tk.StringVar()
        self.type_combo = ttk.Combobox(filter_frame, textvariable=self.type_var, 
                                      width=15, state="readonly")
        self.type_combo.pack(side=tk.LEFT, padx=(5, 10))
        
        # Filter by status
        ttk.Label(filter_frame, text="Status:").pack(side=tk.LEFT)
        self.status_var = tk.StringVar()
        self.status_combo = ttk.Combobox(filter_frame, textvariable=self.status_var,
                                        width=15, state="readonly")
        self.status_combo.pack(side=tk.LEFT, padx=(5, 10))
        
        # Apply filters button
        ttk.Button(filter_frame, text="Apply Filters", 
                  command=self.apply_filters).pack(side=tk.LEFT, padx=(10, 0))
        
        # Bind Enter key to search
        self.search_entry.bind('<Return>', lambda e: self.perform_search())
        
        # Bind combo selection events
        self.type_combo.bind('<<ComboboxSelected>>', lambda e: self.apply_filters())
        self.status_combo.bind('<<ComboboxSelected>>', lambda e: self.apply_filters())
    
    def update_filter_options(self, requirements: Dict[str, Any]):
        """Update filter combo box options based on current requirements"""
        # Extract unique types and statuses
        types = set(['All'])
        statuses = set(['All'])
        
        for req in requirements.values():
            for attr_name, attr_value in req.attributes.items():
                if 'type' in attr_name.lower():
                    types.add(str(attr_value))
                elif 'status' in attr_name.lower():
                    statuses.add(str(attr_value))
        
        # Update combo boxes
        self.type_combo['values'] = sorted(list(types))
        self.status_combo['values'] = sorted(list(statuses))
        
        # Set default selections
        if not self.type_var.get():
            self.type_var.set('All')
        if not self.status_var.get():
            self.status_var.set('All')
    
    def perform_search(self):
        """Perform text search"""
        search_term = self.search_var.get().strip()
        self.on_search_callback('search', search_term)
    
    def clear_search(self):
        """Clear search and filters"""
        self.search_var.set('')
        self.type_var.set('All')
        self.status_var.set('All')
        self.on_search_callback('clear', None)
    
    def apply_filters(self):
        """Apply selected filters"""
        filters = {
            'type': self.type_var.get() if self.type_var.get() != 'All' else None,
            'status': self.status_var.get() if self.status_var.get() != 'All' else None
        }
        self.on_search_callback('filter', filters)


class RequirementTableView:
    """Excel-like table view for requirements"""
    
    def __init__(self, parent, on_requirement_selected: Callable):
        self.parent = parent
        self.on_requirement_selected = on_requirement_selected
        self.current_requirements = {}
        self.filtered_requirements = {}
        
        self.setup_view()
    
    def setup_view(self):
        """Setup the table view"""
        self.frame = ttk.Frame(self.parent)
        
        # Create treeview
        columns = ('ID', 'Text', 'Type', 'Status', 'Priority', 'Attributes')
        self.tree = ttk.Treeview(self.frame, columns=columns, show='headings', height=20)
        
        # Configure column headings and widths
        self.tree.heading('ID', text='Requirement ID', command=lambda: self.sort_by_column('ID'))
        self.tree.heading('Text', text='Requirement Text', command=lambda: self.sort_by_column('Text'))
        self.tree.heading('Type', text='Type', command=lambda: self.sort_by_column('Type'))
        self.tree.heading('Status', text='Status', command=lambda: self.sort_by_column('Status'))
        self.tree.heading('Priority', text='Priority', command=lambda: self.sort_by_column('Priority'))
        self.tree.heading('Attributes', text='Other Attributes', command=lambda: self.sort_by_column('Attributes'))
        
        # Set column widths
        self.tree.column('ID', width=150, minwidth=100)
        self.tree.column('Text', width=400, minwidth=200)
        self.tree.column('Type', width=100, minwidth=80)
        self.tree.column('Status', width=100, minwidth=80)
        self.tree.column('Priority', width=100, minwidth=80)
        self.tree.column('Attributes', width=200, minwidth=150)
        
        # Add scrollbars
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
        self.tree.bind('<Double-1>', self.on_double_click)
        self.tree.bind('<<TreeviewSelect>>', self.on_selection_change)
        
        # Context menu
        self.setup_context_menu()
        
        # Sorting state
        self.sort_column = None
        self.sort_reverse = False
    
    def setup_context_menu(self):
        """Setup right-click context menu"""
        self.context_menu = tk.Menu(self.tree, tearoff=0)
        self.context_menu.add_command(label="View Details", command=self.view_selected_details)
        self.context_menu.add_command(label="Copy ID", command=self.copy_selected_id)
        self.context_menu.add_command(label="Copy Text", command=self.copy_selected_text)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Export Selected", command=self.export_selected)
        
        def show_context_menu(event):
            try:
                # Select item under cursor
                item = self.tree.identify_row(event.y)
                if item:
                    self.tree.selection_set(item)
                    self.context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.context_menu.grab_release()
        
        self.tree.bind('<Button-3>', show_context_menu)  # Right-click
    
    def load_requirements(self, requirements: Dict[str, Any]):
        """Load requirements into the table"""
        self.current_requirements = requirements
        self.filtered_requirements = requirements.copy()
        self.refresh_display()
    
    def refresh_display(self):
        """Refresh the table display"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add requirements to tree
        for req_id, req in self.filtered_requirements.items():
            # Truncate text for display
            text = req.text[:100] + ('...' if len(req.text) > 100 else '')
            
            # Extract common attributes
            attributes = req.attributes
            req_type = self.get_attribute_value(attributes, 'type')
            status = self.get_attribute_value(attributes, 'status')
            priority = self.get_attribute_value(attributes, 'priority')
            
            # Create summary of other attributes
            other_attrs = []
            for key, value in attributes.items():
                if not any(keyword in key.lower() for keyword in ['type', 'status', 'priority']):
                    other_attrs.append(f"{key}: {value}")
            other_attrs_str = '; '.join(other_attrs[:3])  # Show first 3
            if len(other_attrs) > 3:
                other_attrs_str += '...'
            
            # Insert into tree
            self.tree.insert('', tk.END, values=(
                req_id, text, req_type, status, priority, other_attrs_str
            ))
    
    def get_attribute_value(self, attributes: Dict[str, Any], attr_type: str) -> str:
        """Get attribute value by type (case-insensitive)"""
        for key, value in attributes.items():
            if attr_type.lower() in key.lower():
                return str(value)
        return 'N/A'
    
    def sort_by_column(self, column: str):
        """Sort table by column"""
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False
        
        # Get all items with their values
        items = []
        for item in self.tree.get_children():
            values = self.tree.item(item, 'values')
            items.append((values, item))
        
        # Sort by the selected column
        column_index = ['ID', 'Text', 'Type', 'Status', 'Priority', 'Attributes'].index(column)
        items.sort(key=lambda x: x[0][column_index], reverse=self.sort_reverse)
        
        # Rearrange items in tree
        for index, (values, item) in enumerate(items):
            self.tree.move(item, '', index)
        
        # Update column heading to show sort direction
        for col in ['ID', 'Text', 'Type', 'Status', 'Priority', 'Attributes']:
            if col == column:
                direction = ' ↓' if self.sort_reverse else ' ↑'
                self.tree.heading(col, text=col + direction)
            else:
                self.tree.heading(col, text=col)
    
    def filter_requirements(self, search_term: str = None, filters: Dict[str, str] = None):
        """Filter requirements based on search term and filters"""
        filtered = {}
        
        for req_id, req in self.current_requirements.items():
            # Apply text search
            if search_term:
                search_lower = search_term.lower()
                if not (search_lower in req_id.lower() or 
                       search_lower in req.text.lower() or
                       any(search_lower in str(v).lower() for v in req.attributes.values())):
                    continue
            
            # Apply attribute filters
            if filters:
                if filters.get('type') and filters['type'] != self.get_attribute_value(req.attributes, 'type'):
                    continue
                if filters.get('status') and filters['status'] != self.get_attribute_value(req.attributes, 'status'):
                    continue
            
            filtered[req_id] = req
        
        self.filtered_requirements = filtered
        self.refresh_display()
    
    def clear_filters(self):
        """Clear all filters and show all requirements"""
        self.filtered_requirements = self.current_requirements.copy()
        self.refresh_display()
    
    def on_double_click(self, event):
        """Handle double-click on requirement"""
        self.view_selected_details()
    
    def on_selection_change(self, event):
        """Handle selection change"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            values = self.tree.item(item, 'values')
            req_id = values[0]
            
            if req_id in self.current_requirements:
                self.on_requirement_selected(req_id, self.current_requirements[req_id])
    
    def view_selected_details(self):
        """View details of selected requirement"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a requirement to view details.")
            return
        
        item = selection[0]
        values = self.tree.item(item, 'values')
        req_id = values[0]
        
        if req_id in self.current_requirements:
            self.show_requirement_details(req_id, self.current_requirements[req_id])
    
    def show_requirement_details(self, req_id: str, requirement):
        """Show detailed view of requirement"""
        detail_window = tk.Toplevel(self.parent)
        detail_window.title(f"Requirement Details - {req_id}")
        detail_window.geometry("800x600")
        
        # Create notebook for different views
        notebook = ttk.Notebook(detail_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Text tab
        text_frame = ttk.Frame(notebook)
        notebook.add(text_frame, text="Text")
        
        text_widget = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        text_widget.insert(tk.END, requirement.text)
        text_widget.config(state=tk.DISABLED)
        
        # Attributes tab
        if requirement.attributes:
            attr_frame = ttk.Frame(notebook)
            notebook.add(attr_frame, text="Attributes")
            
            # Create treeview for attributes
            attr_columns = ('Attribute', 'Value')
            attr_tree = ttk.Treeview(attr_frame, columns=attr_columns, show='headings')
            
            attr_tree.heading('Attribute', text='Attribute Name')
            attr_tree.heading('Value', text='Value')
            
            attr_tree.column('Attribute', width=200)
            attr_tree.column('Value', width=400)
            
            # Add scrollbar
            attr_scrollbar = ttk.Scrollbar(attr_frame, orient=tk.VERTICAL, command=attr_tree.yview)
            attr_tree.configure(yscrollcommand=attr_scrollbar.set)
            
            # Pack widgets
            attr_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
            attr_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
            
            # Populate attributes
            for attr_name, attr_value in sorted(requirement.attributes.items()):
                attr_tree.insert('', tk.END, values=(attr_name, attr_value))
    
    def copy_selected_id(self):
        """Copy selected requirement ID to clipboard"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            values = self.tree.item(item, 'values')
            req_id = values[0]
            
            self.parent.clipboard_clear()
            self.parent.clipboard_append(req_id)
            messagebox.showinfo("Copied", f"Requirement ID '{req_id}' copied to clipboard.")
    
    def copy_selected_text(self):
        """Copy selected requirement text to clipboard"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            values = self.tree.item(item, 'values')
            req_id = values[0]
            
            if req_id in self.current_requirements:
                req_text = self.current_requirements[req_id].text
                self.parent.clipboard_clear()
                self.parent.clipboard_append(req_text)
                messagebox.showinfo("Copied", "Requirement text copied to clipboard.")
    
    def export_selected(self):
        """Export selected requirements"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select requirements to export.")
            return
        
        # Get selected requirement IDs
        selected_ids = []
        for item in selection:
            values = self.tree.item(item, 'values')
            selected_ids.append(values[0])
        
        # Create filtered requirements dict
        selected_requirements = {req_id: req for req_id, req in self.current_requirements.items() 
                               if req_id in selected_ids}
        
        # Export dialog would go here
        messagebox.showinfo("Export", f"Would export {len(selected_requirements)} selected requirements.")


class RequirementDetailsView:
    """Detailed view of individual requirements"""
    
    def __init__(self, parent):
        self.parent = parent
        self.current_requirement = None
        
        self.setup_view()
    
    def setup_view(self):
        """Setup the details view"""
        self.frame = ttk.LabelFrame(self.parent, text="Requirement Details", padding="5")
        
        # Create notebook for different detail views
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Text view
        self.text_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.text_frame, text="Text")
        
        self.text_widget = scrolledtext.ScrolledText(self.text_frame, wrap=tk.WORD, height=10)
        self.text_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Attributes view
        self.attr_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.attr_frame, text="Attributes")
        
        # Create attributes table
        attr_columns = ('Name', 'Value', 'Type')
        self.attr_tree = ttk.Treeview(self.attr_frame, columns=attr_columns, show='headings', height=8)
        
        for col in attr_columns:
            self.attr_tree.heading(col, text=col)
            self.attr_tree.column(col, width=150)
        
        attr_scrollbar = ttk.Scrollbar(self.attr_frame, orient=tk.VERTICAL, command=self.attr_tree.yview)
        self.attr_tree.configure(yscrollcommand=attr_scrollbar.set)
        
        self.attr_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        attr_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
        # Metadata view
        self.meta_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.meta_frame, text="Metadata")
        
        self.meta_text = scrolledtext.ScrolledText(self.meta_frame, wrap=tk.WORD, height=8)
        self.meta_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Initially show placeholder
        self.show_placeholder()
    
    def show_placeholder(self):
        """Show placeholder when no requirement is selected"""
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.insert(tk.END, "Select a requirement from the table above to view details...")
        self.text_widget.config(state=tk.DISABLED)
        
        # Clear attributes
        for item in self.attr_tree.get_children():
            self.attr_tree.delete(item)
        
        # Clear metadata
        self.meta_text.config(state=tk.NORMAL)
        self.meta_text.delete(1.0, tk.END)
        self.meta_text.config(state=tk.DISABLED)
    
    def display_requirement(self, req_id: str, requirement):
        """Display requirement details"""
        self.current_requirement = requirement
        
        # Update text view
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.insert(tk.END, requirement.text)
        self.text_widget.config(state=tk.DISABLED)
        
        # Update attributes view
        for item in self.attr_tree.get_children():
            self.attr_tree.delete(item)
        
        for attr_name, attr_value in sorted(requirement.attributes.items()):
            value_type = type(attr_value).__name__
            self.attr_tree.insert('', tk.END, values=(attr_name, str(attr_value), value_type))
        
        # Update metadata view
        self.meta_text.config(state=tk.NORMAL)
        self.meta_text.delete(1.0, tk.END)
        
        metadata = f"Requirement ID: {req_id}\n"
        metadata += f"Text Length: {len(requirement.text)} characters\n"
        metadata += f"Word Count: {len(requirement.text.split())}\n"
        metadata += f"Attribute Count: {len(requirement.attributes)}\n"
        
        if hasattr(requirement, 'last_change') and requirement.last_change:
            metadata += f"Last Changed: {requirement.last_change}\n"
        
        if hasattr(requirement, 'long_name') and requirement.long_name:
            metadata += f"Long Name: {requirement.long_name}\n"
        
        self.meta_text.insert(tk.END, metadata)
        self.meta_text.config(state=tk.DISABLED)


class StatisticsView:
    """Statistical analysis and charts view"""
    
    def __init__(self, parent):
        self.parent = parent
        self.analysis_result = None
        
        self.setup_view()
    
    def setup_view(self):
        """Setup the statistics view"""
        self.frame = ttk.LabelFrame(self.parent, text="Statistics & Analysis", padding="5")
        
        # Create notebook for different statistics views
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Overview tab
        self.overview_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.overview_frame, text="Overview")
        
        self.overview_text = scrolledtext.ScrolledText(self.overview_frame, wrap=tk.WORD, height=15)
        self.overview_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Distribution tab
        self.dist_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.dist_frame, text="Distributions")
        
        self.dist_text = scrolledtext.ScrolledText(self.dist_frame, wrap=tk.WORD, height=15)
        self.dist_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Quality tab
        self.quality_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.quality_frame, text="Quality Metrics")
        
        self.quality_text = scrolledtext.ScrolledText(self.quality_frame, wrap=tk.WORD, height=15)
        self.quality_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Initially show placeholder
        self.show_placeholder()
    
    def show_placeholder(self):
        """Show placeholder when no analysis is available"""
        placeholder_text = "Load a ReqIF file to view statistical analysis..."
        
        for text_widget in [self.overview_text, self.dist_text, self.quality_text]:
            text_widget.config(state=tk.NORMAL)
            text_widget.delete(1.0, tk.END)
            text_widget.insert(tk.END, placeholder_text)
            text_widget.config(state=tk.DISABLED)
    
    def display_analysis(self, analysis_result):
        """Display analysis results"""
        self.analysis_result = analysis_result
        
        # Update overview
        self.overview_text.config(state=tk.NORMAL)
        self.overview_text.delete(1.0, tk.END)
        self.overview_text.insert(tk.END, self._generate_overview_text(analysis_result))
        self.overview_text.config(state=tk.DISABLED)
        
        # Update distributions
        self.dist_text.config(state=tk.NORMAL)
        self.dist_text.delete(1.0, tk.END)
        self.dist_text.insert(tk.END, self._generate_distribution_text(analysis_result))
        self.dist_text.config(state=tk.DISABLED)
        
        # Update quality metrics
        self.quality_text.config(state=tk.NORMAL)
        self.quality_text.delete(1.0, tk.END)
        self.quality_text.insert(tk.END, self._generate_quality_text(analysis_result))
        self.quality_text.config(state=tk.DISABLED)
    
    def _generate_overview_text(self, analysis_result) -> str:
        """Generate overview text"""
        stats = analysis_result.requirement_stats
        text_stats = analysis_result.text_stats
        
        overview = "REQUIREMENTS OVERVIEW\n"
        overview += "=" * 50 + "\n\n"
        
        overview += f"Total Requirements: {stats.total_count}\n"
        overview += f"Requirements with Text: {stats.with_text}\n"
        overview += f"Requirements with Attributes: {stats.with_attributes}\n"
        overview += f"Empty Requirements: {stats.empty_requirements}\n\n"
        
        overview += "TEXT STATISTICS\n"
        overview += "-" * 20 + "\n"
        overview += f"Total Characters: {text_stats.total_characters:,}\n"
        overview += f"Total Words: {text_stats.total_words:,}\n"
        overview += f"Total Sentences: {text_stats.total_sentences:,}\n"
        overview += f"Average Words per Requirement: {text_stats.avg_words_per_requirement:.1f}\n"
        overview += f"Average Text Length: {stats.avg_text_length:.1f} characters\n"
        overview += f"Average Readability Score: {text_stats.avg_readability_score:.1f}\n\n"
        
        overview += "ATTRIBUTE STATISTICS\n"
        overview += "-" * 20 + "\n"
        attr_stats = analysis_result.attribute_stats
        overview += f"Unique Attributes: {attr_stats.total_unique_attributes}\n"
        overview += f"Average Attributes per Requirement: {stats.avg_attributes_per_requirement:.1f}\n"
        overview += f"Average Completeness: {attr_stats.avg_completeness:.1%}\n\n"
        
        return overview
    
    def _generate_distribution_text(self, analysis_result) -> str:
        """Generate distribution analysis text"""
        dist_text = "REQUIREMENT DISTRIBUTIONS\n"
        dist_text += "=" * 50 + "\n\n"
        
        # Type distribution
        type_dist = analysis_result.type_distribution
        if type_dist.categories:
            dist_text += "TYPE DISTRIBUTION\n"
            dist_text += "-" * 20 + "\n"
            for category, count in sorted(type_dist.categories.items(), key=lambda x: x[1], reverse=True):
                percentage = type_dist.percentages.get(category, 0)
                dist_text += f"{category}: {count} ({percentage:.1f}%)\n"
            dist_text += "\n"
        
        # Status distribution
        status_dist = analysis_result.status_distribution
        if status_dist.categories:
            dist_text += "STATUS DISTRIBUTION\n"
            dist_text += "-" * 20 + "\n"
            for category, count in sorted(status_dist.categories.items(), key=lambda x: x[1], reverse=True):
                percentage = status_dist.percentages.get(category, 0)
                dist_text += f"{category}: {count} ({percentage:.1f}%)\n"
            dist_text += "\n"
        
        # Priority distribution
        priority_dist = analysis_result.priority_distribution
        if priority_dist.categories:
            dist_text += "PRIORITY DISTRIBUTION\n"
            dist_text += "-" * 20 + "\n"
            for category, count in sorted(priority_dist.categories.items(), key=lambda x: x[1], reverse=True):
                percentage = priority_dist.percentages.get(category, 0)
                dist_text += f"{category}: {count} ({percentage:.1f}%)\n"
            dist_text += "\n"
        
        # Attribute completeness
        attr_stats = analysis_result.attribute_stats
        if attr_stats.attribute_completeness:
            dist_text += "ATTRIBUTE COMPLETENESS\n"
            dist_text += "-" * 20 + "\n"
            sorted_completeness = sorted(attr_stats.attribute_completeness.items(), 
                                       key=lambda x: x[1], reverse=True)
            for attr_name, completeness in sorted_completeness[:10]:  # Top 10
                dist_text += f"{attr_name}: {completeness:.1%}\n"
            dist_text += "\n"
        
        return dist_text
    
    def _generate_quality_text(self, analysis_result) -> str:
        """Generate quality metrics text"""
        quality = analysis_result.quality_metrics
        
        quality_text = "QUALITY METRICS\n"
        quality_text += "=" * 50 + "\n\n"
        
        quality_text += f"Overall Quality Score: {quality.overall_score:.1f}/100\n"
        quality_text += f"Readability Score: {quality.readability_score:.1f}\n"
        quality_text += f"Completeness Score: {quality.completeness_score:.1f}/100\n\n"
        
        # Quality distribution
        if quality.quality_distribution:
            quality_text += "QUALITY DISTRIBUTION\n"
            quality_text += "-" * 20 + "\n"
            for category, count in quality.quality_distribution.items():
                quality_text += f"{category}: {count}\n"
            quality_text += "\n"
        
        # Consistency issues
        if quality.consistency_issues:
            quality_text += "CONSISTENCY ISSUES\n"
            quality_text += "-" * 20 + "\n"
            
            # Group issues by type
            issue_counts = {}
            for issue in quality.consistency_issues:
                issue_type = issue.get('type', 'Unknown')
                issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1
            
            for issue_type, count in sorted(issue_counts.items(), key=lambda x: x[1], reverse=True):
                quality_text += f"{issue_type}: {count} issues\n"
            
            quality_text += f"\nTotal Issues: {len(quality.consistency_issues)}\n\n"
        
        # Recommendations
        if quality.recommendations:
            quality_text += "RECOMMENDATIONS\n"
            quality_text += "-" * 20 + "\n"
            for i, recommendation in enumerate(quality.recommendations, 1):
                quality_text += f"{i}. {recommendation}\n"
            quality_text += "\n"
        
        return quality_text