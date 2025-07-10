#!/usr/bin/env python3
"""
VisualizerGUI - Updated Version
Pure tkinter with dynamic field detection - no hardcoded field assumptions
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import os
from typing import List, Dict, Any, Optional, Set


class VisualizerGUI:
    """
    Native Requirements Visualizer GUI with Dynamic Field Detection
    """
    
    def __init__(self, parent: tk.Widget, requirements: List[Dict[str, Any]], filename: str):
        self.parent = parent
        self.requirements = requirements
        self.filename = filename
        self.filtered_requirements = requirements.copy()
        
        # Create independent window
        self.window = tk.Toplevel(parent)
        self.window.title(f"Requirements Analysis - {os.path.basename(filename)}")
        self.window.geometry("1200x800")
        
        # Ensure window independence
        self.window.transient(parent)
        self.window.focus_set()
        
        # Search and filter state
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._on_search_change)
        
        # Dynamic field detection
        self.available_fields = self._detect_available_fields()
        self.visible_columns = self._determine_optimal_columns()
        
        # Statistics
        self.stats = self._calculate_statistics()
        
        # Setup GUI
        self.setup_gui()
        
        # Populate data
        self.populate_data()
        
        # Handle window closing
        self.window.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _detect_available_fields(self) -> Set[str]:
        """Detect which fields are actually available in the requirements"""
        available_fields = set()
        
        if not self.requirements:
            return {'id'}
        
        for req in self.requirements:
            if isinstance(req, dict):
                # Add main fields (excluding internal ones)
                for field_name in req.keys():
                    if not field_name.startswith('_') and field_name not in ['content', 'raw_attributes']:
                        available_fields.add(field_name)
                
                # Add attribute fields with prefix
                attributes = req.get('attributes', {})
                if isinstance(attributes, dict):
                    for attr_name in attributes.keys():
                        available_fields.add(f'attr_{attr_name}')
        
        # Ensure 'id' is always included
        available_fields.add('id')
        
        return available_fields
    
    def _determine_optimal_columns(self) -> List[str]:
        """Determine optimal columns to display based on actual data"""
        if not self.requirements or not self.available_fields:
            return ['id']
        
        # Always start with id
        selected_columns = ['id']
        
        # Calculate field quality scores based on content
        field_scores = {}
        
        # Score regular fields
        regular_fields = [f for f in self.available_fields if not f.startswith('attr_') and f != 'id']
        for field in regular_fields:
            filled_count = 0
            total_length = 0
            
            for req in self.requirements:
                if isinstance(req, dict):
                    value = req.get(field, '')
                    if value and str(value).strip():
                        filled_count += 1
                        total_length += len(str(value))
            
            if self.requirements:
                fill_rate = filled_count / len(self.requirements)
                avg_length = total_length / max(filled_count, 1)
                # Score based on fill rate and content quality
                field_scores[field] = fill_rate * min(avg_length / 50, 1.0)  # Normalize length factor
        
        # Score attribute fields
        attr_fields = [f for f in self.available_fields if f.startswith('attr_')]
        for field in attr_fields:
            attr_name = field[5:]  # Remove 'attr_' prefix
            filled_count = 0
            total_length = 0
            
            for req in self.requirements:
                if isinstance(req, dict):
                    attributes = req.get('attributes', {})
                    if isinstance(attributes, dict):
                        value = attributes.get(attr_name, '')
                        if value and str(value).strip():
                            filled_count += 1
                            total_length += len(str(value))
            
            if self.requirements:
                fill_rate = filled_count / len(self.requirements)
                avg_length = total_length / max(filled_count, 1)
                # Score based on fill rate and content quality
                field_scores[field] = fill_rate * min(avg_length / 50, 1.0)
        
        # Sort fields by score (highest first)
        sorted_fields = sorted(field_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Add high-scoring fields up to a reasonable limit
        max_columns = 8  # Reasonable limit for UI
        for field_name, score in sorted_fields:
            if len(selected_columns) >= max_columns:
                break
            if score > 0.1:  # Only include fields with decent content
                selected_columns.append(field_name)
        
        # Ensure we have at least a few columns
        if len(selected_columns) == 1 and sorted_fields:
            # Add top 3 fields regardless of score
            for field_name, _ in sorted_fields[:3]:
                if field_name not in selected_columns:
                    selected_columns.append(field_name)
        
        return selected_columns
    
    def setup_gui(self):
        """Setup native GUI with dynamic field support"""
        # Create main container
        self.main_frame = tk.Frame(self.window, padx=20, pady=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create sections
        self._create_header_section()
        self._create_control_section()
        self._create_content_section()
        self._create_status_section()
    
    def _create_header_section(self):
        """Create header with file info and search"""
        header_frame = tk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # File info
        info_frame = tk.Frame(header_frame)
        info_frame.pack(side=tk.LEFT)
        
        title_label = tk.Label(info_frame, text="Requirements Analysis", 
                              font=('Arial', 18, 'bold'))
        title_label.pack(anchor=tk.W)
        
        file_label = tk.Label(info_frame, text=f"File: {os.path.basename(self.filename)}",
                             font=('Arial', 11))
        file_label.pack(anchor=tk.W, pady=(5, 0))
        
        count_label = tk.Label(info_frame, text=f"Total Requirements: {len(self.requirements)}",
                              font=('Arial', 11), fg='darkblue')
        count_label.pack(anchor=tk.W, pady=(3, 0))
        
        # Display available fields info
        fields_info = tk.Label(info_frame, text=f"Available Fields: {len(self.available_fields)}",
                              font=('Arial', 10), fg='darkgreen')
        fields_info.pack(anchor=tk.W, pady=(2, 0))
        
        # Search section
        search_frame = tk.Frame(header_frame)
        search_frame.pack(side=tk.RIGHT, padx=(25, 0))
        
        tk.Label(search_frame, text="Search:", font=('Arial', 12, 'bold')).pack(side=tk.LEFT, padx=(0, 10))
        
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, width=35, 
                               font=('Arial', 11), relief='sunken', bd=2)
        search_entry.pack(side=tk.LEFT)
        
        clear_btn = tk.Button(search_frame, text="Clear", width=8, command=self._clear_search,
                             font=('Arial', 10), relief='raised', bd=2, padx=12, pady=4,
                             cursor='hand2')
        clear_btn.pack(side=tk.LEFT, padx=(10, 0))
    
    def _create_control_section(self):
        """Create control buttons"""
        control_frame = tk.Frame(self.main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Left side buttons
        left_buttons = tk.Frame(control_frame)
        left_buttons.pack(side=tk.LEFT)
        
        tk.Button(left_buttons, text="📊 Statistics", command=self._show_statistics,
                 font=('Arial', 11, 'bold'), relief='raised', bd=2,
                 padx=20, pady=6, cursor='hand2', bg='lightcyan').pack(side=tk.LEFT, padx=(0, 15))
        
        tk.Button(left_buttons, text="🔍 Field Analysis", command=self._show_field_analysis,
                 font=('Arial', 11, 'bold'), relief='raised', bd=2,
                 padx=20, pady=6, cursor='hand2', bg='lightyellow').pack(side=tk.LEFT, padx=(0, 15))
        
        tk.Button(left_buttons, text="📄 Export CSV", command=self._export_csv,
                 font=('Arial', 11, 'bold'), relief='raised', bd=2,
                 padx=20, pady=6, cursor='hand2', bg='lightgreen').pack(side=tk.LEFT, padx=(0, 15))
        
        tk.Button(left_buttons, text="🔄 Refresh", command=self._refresh_view,
                 font=('Arial', 11), relief='raised', bd=2,
                 padx=20, pady=6, cursor='hand2').pack(side=tk.LEFT, padx=(0, 25))
        
        # Filter info on the right
        self.filter_info_label = tk.Label(control_frame,
                                         text=f"Showing: {len(self.filtered_requirements)} of {len(self.requirements)} requirements",
                                         font=('Arial', 11))
        self.filter_info_label.pack(side=tk.RIGHT)
    
    def _create_content_section(self):
        """Create main content area with treeview"""
        content_frame = tk.Frame(self.main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview with scrollbars
        tree_frame = tk.Frame(content_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview
        self.tree = ttk.Treeview(tree_frame, selectmode='extended')
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=v_scrollbar.set)
        
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.configure(xscrollcommand=h_scrollbar.set)
        
        # Bind events
        self.tree.bind('<Double-1>', self._on_double_click)
        self.tree.bind('<Button-1>', self._on_click)
    
    def _create_status_section(self):
        """Create status bar"""
        status_frame = tk.Frame(self.main_frame, relief='sunken', bd=2)
        status_frame.pack(fill=tk.X, pady=(20, 0))
        
        self.status_label = tk.Label(status_frame, text="Ready", font=('Arial', 10), 
                                    anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, padx=12, pady=8)
        
        # Selection info
        self.selection_label = tk.Label(status_frame, text="", font=('Arial', 10))
        self.selection_label.pack(side=tk.RIGHT, padx=12, pady=8)
    
    def populate_data(self):
        """Populate treeview with requirements data"""
        try:
            # Configure treeview columns
            self._configure_treeview_columns()
            
            # Insert data
            self._insert_requirements_data()
            
            # Update status
            self.status_label.configure(text="Data loaded successfully", fg='darkgreen')
            
        except Exception as e:
            self.status_label.configure(text=f"Error loading data: {str(e)}", fg='red')
            messagebox.showerror("Data Loading Error", f"Failed to load requirements data:\n{str(e)}")
    
    def _configure_treeview_columns(self):
        """Configure treeview columns based on detected fields"""
        if not self.visible_columns:
            self.visible_columns = ['id']
        
        # Configure columns (first column goes in tree, rest in columns)
        tree_column = self.visible_columns[0]
        other_columns = self.visible_columns[1:] if len(self.visible_columns) > 1 else []
        
        self.tree['columns'] = other_columns
        self.tree['show'] = 'tree headings'
        
        # Configure tree column
        tree_display_name = self._format_field_name(tree_column)
        self.tree.heading('#0', text=tree_display_name, anchor=tk.W)
        self.tree.column('#0', width=120, minwidth=80)
        
        # Configure other columns
        for col in other_columns:
            display_name = self._format_field_name(col)
            self.tree.heading(col, text=display_name, anchor=tk.W)
            
            # Set column width based on field type and content
            if col.startswith('attr_'):
                width = 200  # Attributes might have longer content
            elif col == 'type':
                width = 120
            elif col == 'identifier':
                width = 150
            else:
                width = 180
                
            self.tree.column(col, width=width, minwidth=80)
    
    def _format_field_name(self, field_name: str) -> str:
        """Format field name for display"""
        if field_name.startswith('attr_'):
            # Remove 'attr_' prefix and format attribute name
            attr_name = field_name[5:]
            return attr_name.replace('_', ' ').title()
        else:
            # Format regular field names
            formatted = field_name.replace('_', ' ').title()
            # Special cases
            if formatted == 'Id':
                return 'ID'
            return formatted
    
    def _insert_requirements_data(self):
        """Insert requirements data into treeview with dynamic fields"""
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if not self.visible_columns:
            return
        
        tree_column = self.visible_columns[0]
        other_columns = self.visible_columns[1:] if len(self.visible_columns) > 1 else []
        
        # Insert filtered requirements
        for i, req in enumerate(self.filtered_requirements):
            try:
                if not isinstance(req, dict):
                    continue
                
                # Get tree column value
                tree_value = self._get_field_value(req, tree_column)
                
                # Get values for other columns
                values = []
                for col in other_columns:
                    value = self._get_field_value(req, col)
                    # Clean and truncate value
                    value_str = str(value).strip()
                    if len(value_str) > 100:
                        value_str = value_str[:97] + "..."
                    values.append(value_str)
                
                # Insert item with requirement index as tag
                item_id = self.tree.insert('', 'end', text=tree_value, values=values, tags=[f"req_{i}"])
                
            except Exception as e:
                print(f"Error inserting requirement {i}: {e}")
                continue
    
    def _get_field_value(self, req: Dict[str, Any], field_name: str) -> str:
        """Get field value from requirement with proper handling"""
        try:
            if field_name.startswith('attr_'):
                # Attribute field
                attr_name = field_name[5:]
                attributes = req.get('attributes', {})
                if isinstance(attributes, dict):
                    return str(attributes.get(attr_name, ''))
                return ''
            else:
                # Regular field
                return str(req.get(field_name, ''))
        except Exception as e:
            print(f"Error getting field value for {field_name}: {e}")
            return ''
    
    def _calculate_statistics(self):
        """Calculate statistics about the requirements with dynamic field detection"""
        if not self.requirements:
            return {
                'total_count': 0,
                'field_coverage': {},
                'attribute_coverage': {},
                'total_fields': 0,
                'avg_fields_per_req': 0
            }
        
        stats = {
            'total_count': len(self.requirements),
            'field_coverage': {},
            'attribute_coverage': {},
            'total_fields': len(self.available_fields),
            'avg_fields_per_req': 0
        }
        
        # Calculate field coverage
        regular_fields = [f for f in self.available_fields if not f.startswith('attr_')]
        attribute_fields = [f for f in self.available_fields if f.startswith('attr_')]
        
        # Analyze regular field coverage
        for field in regular_fields:
            filled_count = 0
            for req in self.requirements:
                if isinstance(req, dict) and req.get(field, ''):
                    if str(req[field]).strip():
                        filled_count += 1
            
            stats['field_coverage'][field] = {
                'count': filled_count,
                'percentage': (filled_count / len(self.requirements)) * 100
            }
        
        # Analyze attribute coverage
        for attr_field in attribute_fields:
            attr_name = attr_field[5:]  # Remove 'attr_' prefix
            filled_count = 0
            for req in self.requirements:
                if isinstance(req, dict):
                    attributes = req.get('attributes', {})
                    if isinstance(attributes, dict) and attributes.get(attr_name, ''):
                        if str(attributes[attr_name]).strip():
                            filled_count += 1
            
            stats['attribute_coverage'][attr_name] = {
                'count': filled_count,
                'percentage': (filled_count / len(self.requirements)) * 100
            }
        
        # Calculate average fields per requirement
        total_filled_fields = 0
        for req in self.requirements:
            if isinstance(req, dict):
                req_field_count = 0
                # Count regular fields
                for field in regular_fields:
                    if req.get(field, '') and str(req[field]).strip():
                        req_field_count += 1
                
                # Count attributes
                attributes = req.get('attributes', {})
                if isinstance(attributes, dict):
                    for attr_value in attributes.values():
                        if attr_value and str(attr_value).strip():
                            req_field_count += 1
                
                total_filled_fields += req_field_count
        
        stats['avg_fields_per_req'] = total_filled_fields / len(self.requirements)
        
        return stats
    
    def _on_search_change(self, *args):
        """Handle search text changes with dynamic field support"""
        search_text = self.search_var.get().lower().strip()
        
        if not search_text:
            self.filtered_requirements = self.requirements.copy()
        else:
            self.filtered_requirements = []
            for req in self.requirements:
                if not isinstance(req, dict):
                    continue
                
                # Build searchable text from all available fields
                searchable_texts = []
                
                # Add regular fields
                for field in self.available_fields:
                    if not field.startswith('attr_'):
                        value = req.get(field, '')
                        if value:
                            searchable_texts.append(str(value).lower())
                
                # Add attributes
                attributes = req.get('attributes', {})
                if isinstance(attributes, dict):
                    for attr_value in attributes.values():
                        if attr_value:
                            searchable_texts.append(str(attr_value).lower())
                
                # Check if search text is found
                searchable_text = ' '.join(searchable_texts)
                if search_text in searchable_text:
                    self.filtered_requirements.append(req)
        
        # Update display
        self._insert_requirements_data()
        self._update_filter_info()
    
    def _clear_search(self):
        """Clear search filter"""
        self.search_var.set('')
    
    def _update_filter_info(self):
        """Update filter information display"""
        total = len(self.requirements)
        showing = len(self.filtered_requirements)
        
        if showing == total:
            self.filter_info_label.configure(
                text=f"Showing: {showing} requirements", fg='black'
            )
        else:
            self.filter_info_label.configure(
                text=f"Showing: {showing} of {total} requirements (filtered)", fg='darkorange'
            )
    
    def _refresh_view(self):
        """Refresh the view"""
        # Recalculate optimal columns in case data changed
        self.visible_columns = self._determine_optimal_columns()
        self.stats = self._calculate_statistics()
        self.populate_data()
        self.status_label.configure(text="View refreshed", fg='darkgreen')
    
    def _show_statistics(self):
        """Show statistics dialog with dynamic field information"""
        stats_window = tk.Toplevel(self.window)
        stats_window.title("Requirements Statistics")
        stats_window.geometry("600x500")
        stats_window.transient(self.window)
        
        main_frame = tk.Frame(stats_window, padx=25, pady=25)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        tk.Label(main_frame, text="Requirements Statistics", 
                font=('Arial', 16, 'bold')).pack(pady=(0, 20))
        
        # Create notebook for different stats
        stats_notebook = ttk.Notebook(main_frame)
        stats_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Overview tab
        self._create_overview_stats_tab(stats_notebook)
        
        # Field coverage tab
        self._create_field_coverage_tab(stats_notebook)
        
        # Attribute coverage tab
        self._create_attribute_coverage_tab(stats_notebook)
        
        # Close button
        tk.Button(main_frame, text="Close", command=stats_window.destroy,
                 font=('Arial', 11), relief='raised', bd=2, padx=20, pady=6,
                 cursor='hand2').pack(pady=(20, 0))
    
    def _create_overview_stats_tab(self, parent_notebook):
        """Create overview statistics tab"""
        overview_frame = tk.Frame(parent_notebook)
        parent_notebook.add(overview_frame, text="Overview")
        
        stats_frame = tk.Frame(overview_frame, padx=20, pady=20)
        stats_frame.pack(fill=tk.BOTH, expand=True)
        
        # Basic statistics
        basic_stats = [
            ("Total Requirements", self.stats['total_count'], 'darkblue'),
            ("Available Fields", self.stats['total_fields'], 'darkgreen'),
            ("Avg Fields per Requirement", f"{self.stats['avg_fields_per_req']:.1f}", 'darkorange'),
            ("Displayed Columns", len(self.visible_columns), 'purple')
        ]
        
        for i, (label, value, color) in enumerate(basic_stats):
            frame = tk.Frame(stats_frame)
            frame.pack(fill=tk.X, pady=8)
            
            tk.Label(frame, text=f"{label}:", font=('Arial', 12, 'bold')).pack(side=tk.LEFT)
            tk.Label(frame, text=str(value), font=('Arial', 12), fg=color).pack(side=tk.RIGHT)
        
        # Field types breakdown
        regular_count = len([f for f in self.available_fields if not f.startswith('attr_')])
        attr_count = len([f for f in self.available_fields if f.startswith('attr_')])
        
        tk.Label(stats_frame, text="\nField Types:", font=('Arial', 14, 'bold')).pack(pady=(20, 10))
        
        type_stats = [
            ("Regular Fields", regular_count, 'darkblue'),
            ("Attribute Fields", attr_count, 'darkgreen')
        ]
        
        for label, value, color in type_stats:
            frame = tk.Frame(stats_frame)
            frame.pack(fill=tk.X, pady=5)
            
            tk.Label(frame, text=f"{label}:", font=('Arial', 11, 'bold')).pack(side=tk.LEFT)
            tk.Label(frame, text=str(value), font=('Arial', 11), fg=color).pack(side=tk.RIGHT)
    
    def _create_field_coverage_tab(self, parent_notebook):
        """Create field coverage statistics tab"""
        field_frame = tk.Frame(parent_notebook)
        parent_notebook.add(field_frame, text="Field Coverage")
        
        # Create scrollable frame
        canvas = tk.Canvas(field_frame)
        scrollbar = ttk.Scrollbar(field_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Field coverage content
        content_frame = tk.Frame(scrollable_frame, padx=20, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(content_frame, text="Regular Field Coverage", 
                font=('Arial', 14, 'bold')).pack(pady=(0, 15))
        
        # Sort fields by coverage percentage
        field_coverage = self.stats.get('field_coverage', {})
        sorted_fields = sorted(field_coverage.items(), key=lambda x: x[1]['percentage'], reverse=True)
        
        for field_name, coverage in sorted_fields:
            frame = tk.Frame(content_frame)
            frame.pack(fill=tk.X, pady=3)
            
            display_name = self._format_field_name(field_name)
            percentage = coverage['percentage']
            count = coverage['count']
            
            # Color based on coverage
            if percentage >= 75:
                color = 'darkgreen'
            elif percentage >= 50:
                color = 'darkorange'
            else:
                color = 'darkred'
            
            tk.Label(frame, text=f"{display_name}:", font=('Arial', 11)).pack(side=tk.LEFT)
            tk.Label(frame, text=f"{count}/{self.stats['total_count']} ({percentage:.1f}%)", 
                    font=('Arial', 11), fg=color).pack(side=tk.RIGHT)
    
    def _create_attribute_coverage_tab(self, parent_notebook):
        """Create attribute coverage statistics tab"""
        attr_frame = tk.Frame(parent_notebook)
        parent_notebook.add(attr_frame, text="Attribute Coverage")
        
        # Create scrollable frame
        canvas = tk.Canvas(attr_frame)
        scrollbar = ttk.Scrollbar(attr_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Attribute coverage content
        content_frame = tk.Frame(scrollable_frame, padx=20, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(content_frame, text="Attribute Field Coverage", 
                font=('Arial', 14, 'bold')).pack(pady=(0, 15))
        
        # Sort attributes by coverage percentage
        attr_coverage = self.stats.get('attribute_coverage', {})
        sorted_attrs = sorted(attr_coverage.items(), key=lambda x: x[1]['percentage'], reverse=True)
        
        if not sorted_attrs:
            tk.Label(content_frame, text="No attributes found in requirements", 
                    font=('Arial', 11), fg='gray').pack(pady=20)
        else:
            for attr_name, coverage in sorted_attrs:
                frame = tk.Frame(content_frame)
                frame.pack(fill=tk.X, pady=3)
                
                percentage = coverage['percentage']
                count = coverage['count']
                
                # Color based on coverage
                if percentage >= 75:
                    color = 'darkgreen'
                elif percentage >= 50:
                    color = 'darkorange'
                else:
                    color = 'darkred'
                
                tk.Label(frame, text=f"{attr_name}:", font=('Arial', 11)).pack(side=tk.LEFT)
                tk.Label(frame, text=f"{count}/{self.stats['total_count']} ({percentage:.1f}%)", 
                        font=('Arial', 11), fg=color).pack(side=tk.RIGHT)
    
    def _show_field_analysis(self):
        """Show detailed field analysis dialog"""
        analysis_window = tk.Toplevel(self.window)
        analysis_window.title("Field Analysis")
        analysis_window.geometry("700x600")
        analysis_window.transient(self.window)
        
        main_frame = tk.Frame(analysis_window, padx=25, pady=25)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        tk.Label(main_frame, text="Detailed Field Analysis", 
                font=('Arial', 16, 'bold')).pack(pady=(0, 20))
        
        # Create treeview for field analysis
        tree_frame = tk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ['type', 'coverage', 'avg_length', 'quality']
        analysis_tree = ttk.Treeview(tree_frame, columns=columns, show='tree headings')
        analysis_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure columns
        analysis_tree.heading('#0', text='Field Name', anchor=tk.W)
        analysis_tree.column('#0', width=200, minwidth=150)
        
        column_config = {
            'type': ('Type', 80, 60),
            'coverage': ('Coverage', 100, 80),
            'avg_length': ('Avg Length', 100, 80),
            'quality': ('Quality', 80, 60)
        }
        
        for col, (display_name, width, minwidth) in column_config.items():
            analysis_tree.heading(col, text=display_name, anchor=tk.W)
            analysis_tree.column(col, width=width, minwidth=minwidth)
        
        # Add scrollbar
        v_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=analysis_tree.yview)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        analysis_tree.configure(yscrollcommand=v_scroll.set)
        
        # Populate with field analysis data
        self._populate_field_analysis(analysis_tree)
        
        # Close button
        tk.Button(main_frame, text="Close", command=analysis_window.destroy,
                 font=('Arial', 11), relief='raised', bd=2, padx=20, pady=6,
                 cursor='hand2').pack(pady=(20, 0))
    
    def _populate_field_analysis(self, tree):
        """Populate field analysis tree with detailed information"""
        # Analyze each field
        for field_name in sorted(self.available_fields):
            try:
                if field_name.startswith('attr_'):
                    field_type = 'Attribute'
                    attr_name = field_name[5:]
                    # Analyze attribute
                    coverage_data = self.stats['attribute_coverage'].get(attr_name, {'count': 0, 'percentage': 0})
                    
                    # Calculate average length
                    total_length = 0
                    filled_count = 0
                    for req in self.requirements:
                        if isinstance(req, dict):
                            attributes = req.get('attributes', {})
                            if isinstance(attributes, dict):
                                value = attributes.get(attr_name, '')
                                if value and str(value).strip():
                                    total_length += len(str(value))
                                    filled_count += 1
                    
                    avg_length = total_length / max(filled_count, 1)
                    display_name = attr_name
                else:
                    field_type = 'Regular'
                    coverage_data = self.stats['field_coverage'].get(field_name, {'count': 0, 'percentage': 0})
                    
                    # Calculate average length
                    total_length = 0
                    filled_count = 0
                    for req in self.requirements:
                        if isinstance(req, dict):
                            value = req.get(field_name, '')
                            if value and str(value).strip():
                                total_length += len(str(value))
                                filled_count += 1
                    
                    avg_length = total_length / max(filled_count, 1)
                    display_name = self._format_field_name(field_name)
                
                # Calculate quality score
                coverage_pct = coverage_data['percentage']
                length_score = min(avg_length / 50, 1.0)  # Normalize to 0-1
                quality_score = (coverage_pct / 100) * 0.7 + length_score * 0.3
                
                if quality_score >= 0.8:
                    quality = 'Excellent'
                elif quality_score >= 0.6:
                    quality = 'Good'
                elif quality_score >= 0.4:
                    quality = 'Fair'
                else:
                    quality = 'Poor'
                
                values = [
                    field_type,
                    f"{coverage_data['percentage']:.1f}%",
                    f"{avg_length:.0f} chars",
                    quality
                ]
                
                tree.insert('', 'end', text=display_name, values=values)
                
            except Exception as e:
                print(f"Error analyzing field {field_name}: {e}")
    
    def _export_csv(self):
        """Export filtered requirements to CSV with dynamic fields"""
        if not self.filtered_requirements:
            messagebox.showwarning("No Data", "No requirements to export.")
            return
        
        try:
            filename = filedialog.asksaveasfilename(
                title="Export Requirements to CSV",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile=f"requirements_export_{len(self.filtered_requirements)}_items.csv"
            )
            
            if not filename:
                return
            
            # Collect all possible fields from filtered requirements
            all_fields = set()
            for req in self.filtered_requirements:
                if isinstance(req, dict):
                    # Add main fields
                    for field_name in req.keys():
                        if not field_name.startswith('_') and field_name not in ['content', 'raw_attributes']:
                            all_fields.add(field_name)
                    
                    # Add attribute fields
                    attributes = req.get('attributes', {})
                    if isinstance(attributes, dict):
                        for attr_name in attributes.keys():
                            all_fields.add(f'attr_{attr_name}')
            
            # Sort fields for consistent column order
            sorted_fields = sorted(all_fields)
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                # Create header with formatted names
                header = [self._format_field_name(field) for field in sorted_fields]
                writer = csv.writer(csvfile)
                writer.writerow(header)
                
                # Write data
                for req in self.filtered_requirements:
                    if isinstance(req, dict):
                        row = []
                        for field in sorted_fields:
                            value = self._get_field_value(req, field)
                            row.append(value)
                        writer.writerow(row)
            
            messagebox.showinfo("Export Complete", 
                               f"Successfully exported {len(self.filtered_requirements)} requirements to:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export CSV:\n{str(e)}")
    
    def _on_double_click(self, event):
        """Handle double-click on requirement"""
        item_id = self.tree.selection()[0] if self.tree.selection() else None
        if item_id:
            self._show_requirement_details(item_id)
    
    def _on_click(self, event):
        """Handle single click to update selection info"""
        selected_count = len(self.tree.selection())
        if selected_count == 0:
            self.selection_label.configure(text="")
        elif selected_count == 1:
            self.selection_label.configure(text="1 requirement selected")
        else:
            self.selection_label.configure(text=f"{selected_count} requirements selected")
    
    def _show_requirement_details(self, item_id):
        """Show detailed requirement information with dynamic fields"""
        try:
            # Get requirement index from tags
            tags = self.tree.item(item_id, 'tags')
            req_index = None
            for tag in tags:
                if tag.startswith('req_'):
                    req_index = int(tag[4:])
                    break
            
            if req_index is None or req_index >= len(self.filtered_requirements):
                messagebox.showerror("Error", "Could not find requirement data.")
                return
            
            # Get requirement data
            req = self.filtered_requirements[req_index]
            req_text = self.tree.item(item_id, 'text')
            
            # Create details window
            details_window = tk.Toplevel(self.window)
            details_window.title(f"Requirement Details - {req_text}")
            details_window.geometry("750x650")
            details_window.transient(self.window)
            
            main_frame = tk.Frame(details_window, padx=25, pady=25)
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Title - use best available display text
            display_text = self._get_requirement_display_text(req)
            tk.Label(main_frame, text=f"Requirement: {display_text}", 
                    font=('Arial', 16, 'bold')).pack(anchor=tk.W, pady=(0, 20))
            
            # Details in scrollable text
            text_frame = tk.Frame(main_frame)
            text_frame.pack(fill=tk.BOTH, expand=True)
            
            details_text = tk.Text(text_frame, wrap=tk.WORD, font=('Arial', 11))
            details_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=details_text.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            details_text.configure(yscrollcommand=scrollbar.set)
            
            # Populate details with dynamic fields
            self._populate_requirement_details(details_text, req)
            
            details_text.configure(state=tk.DISABLED)
            
            # Close button
            tk.Button(main_frame, text="Close", command=details_window.destroy,
                     font=('Arial', 11), relief='raised', bd=2, padx=20, pady=6,
                     cursor='hand2').pack(pady=(20, 0))
            
        except Exception as e:
            messagebox.showerror("Details Error", f"Failed to show requirement details:\n{str(e)}")
    
    def _get_requirement_display_text(self, req: Dict[str, Any]) -> str:
        """Get best display text for requirement using dynamic fields"""
        try:
            if not isinstance(req, dict):
                return "Invalid requirement"
            
            # Try different fields in priority order
            candidates = []
            
            # Check for identifier if different from id
            if req.get('identifier') and req.get('identifier') != req.get('id'):
                candidates.append(req['identifier'])
            
            # Check for type
            if req.get('type'):
                candidates.append(req['type'])
            
            # Check attributes for display-worthy content
            attributes = req.get('attributes', {})
            if isinstance(attributes, dict):
                # Look for text-like attributes
                for attr_name, attr_value in attributes.items():
                    if attr_value and len(str(attr_value).strip()) > 0:
                        display_value = str(attr_value)
                        if len(display_value) > 50:
                            display_value = display_value[:50] + "..."
                        candidates.append(display_value)
                        break  # Use first meaningful attribute
            
            # Return best candidate or fallback to ID
            return candidates[0] if candidates else req.get('id', 'Unknown')
            
        except Exception as e:
            print(f"Error getting display text: {e}")
            return req.get('id', 'Unknown')
    
    def _populate_requirement_details(self, text_widget, requirement: Dict):
        """Populate requirement details with all available fields"""
        try:
            if not isinstance(requirement, dict):
                text_widget.insert(tk.END, "Invalid requirement data")
                return
            
            # Display regular fields (excluding internal ones)
            excluded_fields = {'attributes', 'raw_attributes', 'content'}
            regular_fields = []
            
            for field_name, field_value in requirement.items():
                if field_name not in excluded_fields and not field_name.startswith('_'):
                    if field_value and str(field_value).strip():
                        regular_fields.append((field_name, field_value))
            
            # Sort fields for consistent display
            regular_fields.sort(key=lambda x: x[0])
            
            # Display regular fields
            if regular_fields:
                text_widget.insert(tk.END, "=== REQUIREMENT FIELDS ===\n\n")
                for field_name, field_value in regular_fields:
                    display_name = self._format_field_name(field_name)
                    text_widget.insert(tk.END, f"{display_name}: {field_value}\n\n")
            
            # Display attributes
            attributes = requirement.get('attributes', {})
            if isinstance(attributes, dict) and attributes:
                text_widget.insert(tk.END, "=== ATTRIBUTES ===\n\n")
                
                # Sort attributes for consistent display
                sorted_attrs = sorted(attributes.items())
                
                for attr_name, attr_value in sorted_attrs:
                    if attr_value and str(attr_value).strip():
                        text_widget.insert(tk.END, f"{attr_name}: {attr_value}\n\n")
            
            # Display raw attributes if different and present
            raw_attributes = requirement.get('raw_attributes', {})
            if isinstance(raw_attributes, dict) and raw_attributes and raw_attributes != attributes:
                text_widget.insert(tk.END, "=== RAW ATTRIBUTE REFERENCES ===\n\n")
                
                sorted_raw_attrs = sorted(raw_attributes.items())
                
                for attr_ref, attr_value in sorted_raw_attrs:
                    if attr_value and str(attr_value).strip():
                        text_widget.insert(tk.END, f"{attr_ref}: {attr_value}\n\n")
            
            # If no meaningful content found
            if not regular_fields and not attributes:
                text_widget.insert(tk.END, "No meaningful content found in this requirement.\n")
                text_widget.insert(tk.END, f"Raw data: {requirement}")
                
        except Exception as e:
            text_widget.insert(tk.END, f"Error displaying requirement details: {str(e)}")
    
    def _on_closing(self):
        """Handle window closing"""
        try:
            self.window.destroy()
        except:
            pass