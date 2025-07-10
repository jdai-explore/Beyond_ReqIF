#!/usr/bin/env python3
"""
Enhanced Folder Comparison Results GUI - Updated Version
Dynamic field detection without hardcoded field assumptions
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import os
from typing import Dict, List, Any, Optional, Set
from comparison_gui import ComparisonResultsGUI


class FolderComparisonResultsGUI:
    """
    Enhanced Folder Comparison Results GUI with Dynamic Field Detection
    """
    
    def __init__(self, parent: tk.Widget, results: Dict[str, Any]):
        self.parent = parent
        self.results = results
        
        # Create independent window
        self.window = tk.Toplevel(parent)
        self.window.title("Enhanced Folder Comparison Results")
        self.window.geometry("1600x1000")  # Larger window for additional content
        
        # Ensure window independence
        self.window.transient(parent)
        self.window.focus_set()
        
        # State tracking
        self.expanded_nodes = set()
        self.file_comparison_windows = {}
        
        # Individual file statistics (Enhanced)
        self.individual_stats = results.get('individual_file_statistics', {})
        
        # Dynamic field detection for matched files
        self.available_fields = self._detect_available_fields()
        
        # Storage for file data (to avoid treeview column issues)
        self.item_file_data = {}
        
        # Setup GUI
        self.setup_gui()
        
        # Handle window closing
        self.window.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _detect_available_fields(self) -> Set[str]:
        """Detect available fields from matched files"""
        available_fields = set()
        
        # Check matched files for available fields
        matched_files = self.individual_stats.get('matched_files', {})
        for file_path, file_data in matched_files.items():
            file1_info = file_data.get('file1_info', {})
            file2_info = file_data.get('file2_info', {})
            comparison_stats = file_data.get('comparison_stats', {})
            
            # Add file info fields
            for info in [file1_info, file2_info]:
                if isinstance(info, dict):
                    available_fields.update(info.keys())
            
            # Add comparison stat fields
            if isinstance(comparison_stats, dict):
                available_fields.update(comparison_stats.keys())
        
        # Add standard fields that are always relevant
        available_fields.update(['match_type', 'similarity', 'has_changes'])
        
        return available_fields
    
    def setup_gui(self):
        """Setup enhanced native GUI with dynamic field detection"""
        # Create main container
        self.main_frame = tk.Frame(self.window, padx=20, pady=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create sections
        self._create_header_section()
        self._create_enhanced_summary_section()  # Enhanced with individual stats
        self._create_tabbed_results_section()    # Enhanced with stats tabs
        self._create_controls_section()
    
    def _create_header_section(self):
        """Create header with folder paths"""
        header_frame = tk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Title
        title_label = tk.Label(header_frame, text="Enhanced Folder Comparison Results", 
                              font=('Arial', 18, 'bold'))
        title_label.pack(anchor=tk.W)
        
        # Folder paths
        folder1_path = self.results.get('folder1_path', 'Unknown')
        folder2_path = self.results.get('folder2_path', 'Unknown')
        
        paths_frame = tk.Frame(header_frame)
        paths_frame.pack(anchor=tk.W, pady=(10, 0))
        
        tk.Label(paths_frame, text="Original Folder:", font=('Arial', 11, 'bold')).grid(row=0, column=0, sticky='w', padx=(0, 10))
        tk.Label(paths_frame, text=folder1_path, font=('Arial', 10), fg='darkblue').grid(row=0, column=1, sticky='w')
        
        tk.Label(paths_frame, text="Modified Folder:", font=('Arial', 11, 'bold')).grid(row=1, column=0, sticky='w', padx=(0, 10))
        tk.Label(paths_frame, text=folder2_path, font=('Arial', 10), fg='darkgreen').grid(row=1, column=1, sticky='w')
    
    def _create_enhanced_summary_section(self):
        """Create enhanced summary statistics section with individual file insights"""
        summary_frame = tk.LabelFrame(self.main_frame, text="Summary Statistics", 
                                     font=('Arial', 12, 'bold'), padx=15, pady=15)
        summary_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Get statistics
        folder_stats = self.results.get('folder_statistics', {})
        req_stats = self.results.get('aggregated_statistics', {})
        
        # Create enhanced summary sections
        self._create_folder_summary(summary_frame, folder_stats)
        self._create_requirements_summary(summary_frame, req_stats)
        self._create_individual_insights_summary(summary_frame)  # Enhanced
    
    def _create_folder_summary(self, parent, folder_stats):
        """Create folder-level summary"""
        folder_frame = tk.LabelFrame(parent, text="File Changes", font=('Arial', 11, 'bold'))
        folder_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))
        
        # Folder statistics
        folder_data = [
            ("Added", folder_stats.get('files_added', 0), 'darkgreen'),
            ("Deleted", folder_stats.get('files_deleted', 0), 'darkred'),
            ("Modified", folder_stats.get('files_with_changes', 0), 'darkorange'),
            ("Unchanged", folder_stats.get('files_unchanged', 0), 'darkblue'),
            ("Errors", folder_stats.get('comparison_errors', 0), 'purple')
        ]
        
        for i, (label, count, color) in enumerate(folder_data):
            frame = tk.Frame(folder_frame)
            frame.pack(pady=5, padx=10)
            
            tk.Label(frame, text=label, font=('Arial', 11, 'bold')).pack(side=tk.LEFT)
            tk.Label(frame, text=str(count), font=('Arial', 14, 'bold'), 
                    fg=color).pack(side=tk.RIGHT, padx=(20, 0))
    
    def _create_requirements_summary(self, parent, req_stats):
        """Create requirements-level summary"""
        req_frame = tk.LabelFrame(parent, text="Aggregated Requirement Changes", font=('Arial', 11, 'bold'))
        req_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(15, 15))
        
        # Requirements statistics
        req_data = [
            ("Added", req_stats.get('total_requirements_added', 0), 'darkgreen'),
            ("Deleted", req_stats.get('total_requirements_deleted', 0), 'darkred'),
            ("Modified", req_stats.get('total_requirements_modified', 0), 'darkorange'),
            ("Unchanged", req_stats.get('total_requirements_unchanged', 0), 'darkblue')
        ]
        
        for i, (label, count, color) in enumerate(req_data):
            frame = tk.Frame(req_frame)
            frame.pack(pady=5, padx=10)
            
            tk.Label(frame, text=label, font=('Arial', 11, 'bold')).pack(side=tk.LEFT)
            tk.Label(frame, text=str(count), font=('Arial', 14, 'bold'), 
                    fg=color).pack(side=tk.RIGHT, padx=(20, 0))
        
        # Overall change percentage
        change_pct = req_stats.get('overall_change_percentage', 0)
        change_frame = tk.Frame(req_frame)
        change_frame.pack(pady=(15, 5), padx=10)
        
        tk.Label(change_frame, text="Overall Change", font=('Arial', 11, 'bold')).pack(side=tk.LEFT)
        tk.Label(change_frame, text=f"{change_pct}%", font=('Arial', 14, 'bold'), 
                fg='purple').pack(side=tk.RIGHT, padx=(20, 0))
    
    def _create_individual_insights_summary(self, parent):
        """Create individual file insights summary with dynamic field analysis"""
        insights_frame = tk.LabelFrame(parent, text="Individual File Insights", font=('Arial', 11, 'bold'))
        insights_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(15, 0))
        
        # Calculate insights from individual statistics
        insights = self._calculate_individual_insights()
        
        # Display key insights
        insight_data = [
            ("Files Analyzed", insights.get('total_files_analyzed', 0), 'darkblue'),
            ("Parsing Errors", insights.get('parsing_errors', 0), 'red' if insights.get('parsing_errors', 0) > 0 else 'darkgreen'),
            ("Largest Change", f"{insights.get('largest_change_pct', 0)}%", 'darkorange'),
            ("Avg File Size", f"{insights.get('avg_file_size_mb', 0):.1f}MB", 'darkgray')
        ]
        
        for label, value, color in insight_data:
            frame = tk.Frame(insights_frame)
            frame.pack(pady=5, padx=10)
            
            tk.Label(frame, text=label, font=('Arial', 11, 'bold')).pack(side=tk.LEFT)
            tk.Label(frame, text=str(value), font=('Arial', 14, 'bold'), 
                    fg=color).pack(side=tk.RIGHT, padx=(20, 0))
        
        # Show statistics button
        tk.Button(insights_frame, text="📊 Detailed Stats", 
                 command=self._show_detailed_individual_stats,
                 font=('Arial', 9), relief='raised', bd=2,
                 padx=10, pady=3, cursor='hand2', bg='lightcyan').pack(pady=(10, 5))
    
    def _calculate_individual_insights(self):
        """Calculate insights from individual file statistics with dynamic field analysis"""
        insights = {
            'total_files_analyzed': 0,
            'parsing_errors': 0,
            'largest_change_pct': 0,
            'avg_file_size_mb': 0,
            'files_with_significant_changes': 0,  # >10% change
            'most_common_fields': [],
            'field_diversity': 0
        }
        
        file_sizes = []
        all_fields = set()
        
        # Analyze matched files
        matched_files = self.individual_stats.get('matched_files', {})
        insights['total_files_analyzed'] += len(matched_files)
        
        for file_path, file_data in matched_files.items():
            try:
                stats = file_data.get('comparison_stats', {})
                change_pct = stats.get('change_percentage', 0)
                
                if change_pct > insights['largest_change_pct']:
                    insights['largest_change_pct'] = change_pct
                
                if change_pct > 10:
                    insights['files_with_significant_changes'] += 1
                
                # Collect file sizes
                file1_info = file_data.get('file1_info', {})
                file2_info = file_data.get('file2_info', {})
                
                file1_size = file1_info.get('size', 0) if isinstance(file1_info, dict) else 0
                file2_size = file2_info.get('size', 0) if isinstance(file2_info, dict) else 0
                file_sizes.extend([file1_size, file2_size])
                
                # Collect field information for diversity analysis
                if isinstance(stats, dict):
                    all_fields.update(stats.keys())
                    
            except Exception as e:
                print(f"Error analyzing matched file {file_path}: {e}")
        
        # Analyze added files
        added_files = self.individual_stats.get('added_files', {})
        insights['total_files_analyzed'] += len(added_files)
        
        for file_path, file_data in added_files.items():
            try:
                if not file_data.get('parsing_success', True):
                    insights['parsing_errors'] += 1
                
                file_info = file_data.get('file_info', {})
                if isinstance(file_info, dict):
                    file_size = file_info.get('size', 0)
                    file_sizes.append(file_size)
            except Exception as e:
                print(f"Error analyzing added file {file_path}: {e}")
        
        # Analyze deleted files
        deleted_files = self.individual_stats.get('deleted_files', {})
        insights['total_files_analyzed'] += len(deleted_files)
        
        for file_path, file_data in deleted_files.items():
            try:
                if not file_data.get('parsing_success', True):
                    insights['parsing_errors'] += 1
                
                file_info = file_data.get('file_info', {})
                if isinstance(file_info, dict):
                    file_size = file_info.get('size', 0)
                    file_sizes.append(file_size)
            except Exception as e:
                print(f"Error analyzing deleted file {file_path}: {e}")
        
        # Calculate average file size
        if file_sizes:
            avg_size_bytes = sum(file_sizes) / len(file_sizes)
            insights['avg_file_size_mb'] = avg_size_bytes / (1024 * 1024)
        
        # Calculate field diversity
        insights['field_diversity'] = len(all_fields)
        
        return insights
    
    def _create_tabbed_results_section(self):
        """Create enhanced results section with individual statistics tabs"""
        results_frame = tk.LabelFrame(self.main_frame, text="Detailed Results", 
                                     font=('Arial', 12, 'bold'), padx=10, pady=10)
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook for tabs
        self.results_notebook = ttk.Notebook(results_frame)
        self.results_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self._create_hierarchical_results_tab()      # Original functionality
        self._create_individual_stats_tab()          # Enhanced: Individual file statistics
        self._create_comparison_analysis_tab()       # Enhanced: Comparison analysis
    
    def _create_hierarchical_results_tab(self):
        """Create hierarchical results display tab with dynamic field support"""
        hierarchical_frame = tk.Frame(self.results_notebook)
        self.results_notebook.add(hierarchical_frame, text="📁 File Hierarchy")
        
        # Instructions
        instruction_label = tk.Label(hierarchical_frame, 
                                    text="📁 Expand folders to see files • 📄 Double-click files to view detailed comparison",
                                    font=('Arial', 10), fg='darkblue')
        instruction_label.pack(anchor=tk.W, pady=(10, 10), padx=15)
        
        # Tree frame
        tree_frame = tk.Frame(hierarchical_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        # Create treeview with dynamic columns
        # Detect common fields from file results
        file_results = self.results.get('file_results', {})
        common_fields = self._detect_file_result_fields(file_results)
        
        # Use most relevant fields for tree columns
        tree_columns = ['status', 'type', 'changes', 'match_type']
        if 'file_size' in common_fields:
            tree_columns.append('file_size')
        
        self.tree = ttk.Treeview(tree_frame, columns=tree_columns, show='tree headings')
        
        # Configure columns
        self.tree.heading('#0', text='File/Folder', anchor=tk.W)
        self.tree.column('#0', width=400, minwidth=200)
        
        column_config = {
            'status': ('Status', 120, 80),
            'type': ('Type', 100, 80),
            'changes': ('Changes', 200, 120),
            'match_type': ('Match', 100, 80),
            'file_size': ('Size (MB)', 100, 80)
        }
        
        for col in tree_columns:
            if col in column_config:
                display_name, width, minwidth = column_config[col]
                self.tree.heading(col, text=display_name, anchor=tk.W)
                self.tree.column(col, width=width, minwidth=minwidth)
        
        # Pack treeview with scrollbars
        tree_container = tk.Frame(tree_frame)
        tree_container.pack(fill=tk.BOTH, expand=True)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.tree.yview)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=v_scrollbar.set)
        
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.configure(xscrollcommand=h_scrollbar.set)
        
        # Bind events
        self.tree.bind('<Double-1>', self._on_tree_double_click)
        self.tree.bind('<<TreeviewOpen>>', self._on_tree_expand)
        self.tree.bind('<<TreeviewClose>>', self._on_tree_collapse)
        
        # Populate tree
        self._populate_hierarchical_tree()
    
    def _detect_file_result_fields(self, file_results):
        """Detect common fields in file results"""
        common_fields = set()
        
        for category in ['matched_files', 'added_files', 'deleted_files']:
            files = file_results.get(category, [])
            for file_data in files:
                if isinstance(file_data, dict):
                    common_fields.update(file_data.keys())
        
        return common_fields
    
    def _create_individual_stats_tab(self):
        """Create individual file statistics tab with dynamic field support"""
        stats_frame = tk.Frame(self.results_notebook)
        self.results_notebook.add(stats_frame, text="📊 Individual Files")
        
        # Create sub-notebook for different file categories
        stats_notebook = ttk.Notebook(stats_frame)
        stats_notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Create sub-tabs
        self._create_matched_files_stats_tab(stats_notebook)
        self._create_added_files_stats_tab(stats_notebook)
        self._create_deleted_files_stats_tab(stats_notebook)
    
    def _create_matched_files_stats_tab(self, parent_notebook):
        """Create matched files statistics tab with dynamic columns"""
        matched_frame = tk.Frame(parent_notebook)
        parent_notebook.add(matched_frame, text=f"🔄 Matched ({len(self.individual_stats.get('matched_files', {}))})")
        
        # Create treeview for matched files with dynamic columns
        tree_frame = tk.Frame(matched_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Define base columns that are always relevant
        base_columns = ['match_type', 'similarity', 'changes', 'change_pct']
        
        # Add dynamic columns based on available data
        matched_files = self.individual_stats.get('matched_files', {})
        additional_columns = []
        
        # Check what additional fields are commonly available
        field_counts = {}
        for file_data in matched_files.values():
            file1_info = file_data.get('file1_info', {})
            file2_info = file_data.get('file2_info', {})
            comparison_stats = file_data.get('comparison_stats', {})
            
            # Count occurrences of potentially useful fields
            for info_dict in [file1_info, file2_info, comparison_stats]:
                if isinstance(info_dict, dict):
                    for field in info_dict.keys():
                        if field not in ['full_path', 'relative_path']:  # Skip path fields
                            field_counts[field] = field_counts.get(field, 0) + 1
        
        # Select most common additional fields
        common_threshold = len(matched_files) * 0.5  # Field must be in 50% of files
        for field, count in field_counts.items():
            if count >= common_threshold and field not in base_columns:
                if field in ['size', 'filename', 'modified_time']:
                    additional_columns.append(field)
        
        # Final column list
        columns = base_columns + additional_columns[:3]  # Limit additional columns
        
        matched_tree = ttk.Treeview(tree_frame, columns=columns, show='tree headings')
        
        # Configure columns
        matched_tree.heading('#0', text='File Path', anchor=tk.W)
        matched_tree.column('#0', width=300, minwidth=200)
        
        # Dynamic column configuration
        for col in columns:
            if col == 'match_type':
                matched_tree.heading(col, text='Match Type', anchor=tk.W)
                matched_tree.column(col, width=80, minwidth=60)
            elif col == 'similarity':
                matched_tree.heading(col, text='Similarity', anchor=tk.W)
                matched_tree.column(col, width=80, minwidth=60)
            elif col == 'changes':
                matched_tree.heading(col, text='Changes', anchor=tk.W)
                matched_tree.column(col, width=120, minwidth=80)
            elif col == 'change_pct':
                matched_tree.heading(col, text='Change %', anchor=tk.W)
                matched_tree.column(col, width=70, minwidth=50)
            elif col == 'size':
                matched_tree.heading(col, text='Size (MB)', anchor=tk.W)
                matched_tree.column(col, width=90, minwidth=70)
            elif col == 'filename':
                matched_tree.heading(col, text='Filename', anchor=tk.W)
                matched_tree.column(col, width=150, minwidth=100)
            elif col == 'modified_time':
                matched_tree.heading(col, text='Modified', anchor=tk.W)
                matched_tree.column(col, width=100, minwidth=80)
            else:
                # Generic handling for other fields
                display_name = col.replace('_', ' ').title()
                matched_tree.heading(col, text=display_name, anchor=tk.W)
                matched_tree.column(col, width=100, minwidth=70)
        
        # Pack with scrollbars
        matched_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        v_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=matched_tree.yview)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        matched_tree.configure(yscrollcommand=v_scroll.set)
        
        # Configure color tags for visual feedback
        matched_tree.tag_configure('high_change', background='#ffdddd')  # Light red
        matched_tree.tag_configure('medium_change', background='#fff5dd')  # Light orange
        matched_tree.tag_configure('low_change', background='#ddffdd')  # Light green
        
        # Add legend for color coding
        legend_frame = tk.Frame(matched_frame)
        legend_frame.pack(fill=tk.X, padx=10, pady=(5, 10))
        
        tk.Label(legend_frame, text="Color coding:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        tk.Label(legend_frame, text="Low change (<5%)", bg='#ddffdd', 
                font=('Arial', 9), padx=5).pack(side=tk.LEFT, padx=(10, 5))
        tk.Label(legend_frame, text="Medium change (5-20%)", bg='#fff5dd', 
                font=('Arial', 9), padx=5).pack(side=tk.LEFT, padx=5)
        tk.Label(legend_frame, text="High change (>20%)", bg='#ffdddd', 
                font=('Arial', 9), padx=5).pack(side=tk.LEFT, padx=5)
        
        # Populate matched files data
        for file_path, file_data in matched_files.items():
            try:
                stats = file_data.get('comparison_stats', {})
                
                # Calculate display values dynamically
                values = []
                for col in columns:
                    if col == 'match_type':
                        values.append(file_data.get('match_type', 'unknown'))
                    elif col == 'similarity':
                        similarity = file_data.get('similarity', 0)
                        values.append(f"{similarity:.2f}")
                    elif col == 'changes':
                        changes = []
                        if stats.get('added_count', 0) > 0:
                            changes.append(f"+{stats['added_count']}")
                        if stats.get('deleted_count', 0) > 0:
                            changes.append(f"-{stats['deleted_count']}")
                        if stats.get('modified_count', 0) > 0:
                            changes.append(f"~{stats['modified_count']}")
                        values.append(", ".join(changes) if changes else "None")
                    elif col == 'change_pct':
                        change_pct = stats.get('change_percentage', 0)
                        values.append(f"{change_pct:.1f}%")
                    elif col == 'size':
                        # Try to get size from file info
                        file1_info = file_data.get('file1_info', {})
                        size = file1_info.get('size', 0) if isinstance(file1_info, dict) else 0
                        size_mb = size / (1024*1024) if size > 0 else 0
                        values.append(f"{size_mb:.1f}")
                    elif col == 'filename':
                        file1_info = file_data.get('file1_info', {})
                        filename = file1_info.get('filename', '') if isinstance(file1_info, dict) else ''
                        values.append(filename)
                    elif col == 'modified_time':
                        file1_info = file_data.get('file1_info', {})
                        mod_time = file1_info.get('modified_time', 0) if isinstance(file1_info, dict) else 0
                        if mod_time:
                            import time
                            values.append(time.strftime('%Y-%m-%d', time.localtime(mod_time)))
                        else:
                            values.append('')
                    else:
                        # Try to get value from various sources
                        value = (stats.get(col, '') or 
                                file_data.get('file1_info', {}).get(col, '') or
                                file_data.get('file2_info', {}).get(col, '') or
                                file_data.get(col, ''))
                        values.append(str(value))
                
                # Add item with appropriate tags for color coding
                change_percentage = stats.get('change_percentage', 0)
                if change_percentage > 20:
                    tags = ['high_change']
                elif change_percentage > 5:
                    tags = ['medium_change']
                else:
                    tags = ['low_change']
                
                matched_tree.insert('', 'end', text=file_path, values=values, tags=tags)
                
            except Exception as e:
                print(f"Error populating matched file {file_path}: {e}")
    
    def _create_added_files_stats_tab(self, parent_notebook):
        """Create added files statistics tab with dynamic fields"""
        added_frame = tk.Frame(parent_notebook)
        parent_notebook.add(added_frame, text=f"➕ Added ({len(self.individual_stats.get('added_files', {}))})")
        
        # Create treeview for added files
        tree_frame = tk.Frame(added_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Dynamic columns based on available data
        added_files = self.individual_stats.get('added_files', {})
        base_columns = ['requirements', 'file_size', 'parsing_status']
        
        # Check for additional common fields
        additional_fields = set()
        for file_data in added_files.values():
            file_info = file_data.get('file_info', {})
            if isinstance(file_info, dict):
                additional_fields.update(file_info.keys())
        
        # Add useful additional fields
        useful_additional = ['filename', 'extension', 'parent_dir']
        additional_columns = [f for f in useful_additional if f in additional_fields]
        
        columns = base_columns + additional_columns
        added_tree = ttk.Treeview(tree_frame, columns=columns, show='tree headings')
        
        # Configure columns
        added_tree.heading('#0', text='File Path', anchor=tk.W)
        added_tree.column('#0', width=400, minwidth=250)
        
        for col in columns:
            if col == 'requirements':
                added_tree.heading(col, text='Requirements', anchor=tk.W)
                added_tree.column(col, width=100, minwidth=80)
            elif col == 'file_size':
                added_tree.heading(col, text='Size (MB)', anchor=tk.W)
                added_tree.column(col, width=80, minwidth=60)
            elif col == 'parsing_status':
                added_tree.heading(col, text='Status', anchor=tk.W)
                added_tree.column(col, width=80, minwidth=60)
            else:
                display_name = col.replace('_', ' ').title()
                added_tree.heading(col, text=display_name, anchor=tk.W)
                added_tree.column(col, width=120, minwidth=80)
        
        # Pack with scrollbars
        added_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        v_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=added_tree.yview)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        added_tree.configure(yscrollcommand=v_scroll.set)
        
        # Populate added files data
        for file_path, file_data in added_files.items():
            try:
                values = []
                for col in columns:
                    if col == 'requirements':
                        req_count = file_data.get('requirement_count', 0)
                        values.append(str(req_count))
                    elif col == 'file_size':
                        file_size = file_data.get('file_size_mb', 0)
                        values.append(f"{file_size:.1f}")
                    elif col == 'parsing_status':
                        parsing_success = file_data.get('parsing_success', False)
                        status = "✓ Success" if parsing_success else "❌ Error"
                        values.append(status)
                    else:
                        # Try to get value from file_info
                        file_info = file_data.get('file_info', {})
                        if isinstance(file_info, dict):
                            value = file_info.get(col, '')
                        else:
                            value = file_data.get(col, '')
                        values.append(str(value))
                
                added_tree.insert('', 'end', text=file_path, values=values)
                
            except Exception as e:
                print(f"Error populating added file {file_path}: {e}")
    
    def _create_deleted_files_stats_tab(self, parent_notebook):
        """Create deleted files statistics tab with dynamic fields"""
        deleted_frame = tk.Frame(parent_notebook)
        parent_notebook.add(deleted_frame, text=f"➖ Deleted ({len(self.individual_stats.get('deleted_files', {}))})")
        
        # Create treeview for deleted files
        tree_frame = tk.Frame(deleted_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Similar structure to added files
        deleted_files = self.individual_stats.get('deleted_files', {})
        base_columns = ['requirements', 'file_size', 'parsing_status']
        
        # Check for additional common fields
        additional_fields = set()
        for file_data in deleted_files.values():
            file_info = file_data.get('file_info', {})
            if isinstance(file_info, dict):
                additional_fields.update(file_info.keys())
        
        useful_additional = ['filename', 'extension', 'parent_dir']
        additional_columns = [f for f in useful_additional if f in additional_fields]
        
        columns = base_columns + additional_columns
        deleted_tree = ttk.Treeview(tree_frame, columns=columns, show='tree headings')
        
        # Configure columns (same as added files)
        deleted_tree.heading('#0', text='File Path', anchor=tk.W)
        deleted_tree.column('#0', width=400, minwidth=250)
        
        for col in columns:
            if col == 'requirements':
                deleted_tree.heading(col, text='Requirements', anchor=tk.W)
                deleted_tree.column(col, width=100, minwidth=80)
            elif col == 'file_size':
                deleted_tree.heading(col, text='Size (MB)', anchor=tk.W)
                deleted_tree.column(col, width=80, minwidth=60)
            elif col == 'parsing_status':
                deleted_tree.heading(col, text='Status', anchor=tk.W)
                deleted_tree.column(col, width=80, minwidth=60)
            else:
                display_name = col.replace('_', ' ').title()
                deleted_tree.heading(col, text=display_name, anchor=tk.W)
                deleted_tree.column(col, width=120, minwidth=80)
        
        # Pack with scrollbars
        deleted_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        v_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=deleted_tree.yview)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        deleted_tree.configure(yscrollcommand=v_scroll.set)
        
        # Populate deleted files data
        for file_path, file_data in deleted_files.items():
            try:
                values = []
                for col in columns:
                    if col == 'requirements':
                        req_count = file_data.get('requirement_count', 0)
                        values.append(str(req_count))
                    elif col == 'file_size':
                        file_size = file_data.get('file_size_mb', 0)
                        values.append(f"{file_size:.1f}")
                    elif col == 'parsing_status':
                        parsing_success = file_data.get('parsing_success', False)
                        status = "✓ Success" if parsing_success else "❌ Error"
                        values.append(status)
                    else:
                        # Try to get value from file_info
                        file_info = file_data.get('file_info', {})
                        if isinstance(file_info, dict):
                            value = file_info.get(col, '')
                        else:
                            value = file_data.get(col, '')
                        values.append(str(value))
                
                deleted_tree.insert('', 'end', text=file_path, values=values)
                
            except Exception as e:
                print(f"Error populating deleted file {file_path}: {e}")
    
    def _create_comparison_analysis_tab(self):
        """Create comparison analysis tab with dynamic insights"""
        analysis_frame = tk.Frame(self.results_notebook)
        self.results_notebook.add(analysis_frame, text="📈 Analysis")
        
        # Create scrollable frame
        canvas = tk.Canvas(analysis_frame)
        scrollbar = ttk.Scrollbar(analysis_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Analysis content
        self._create_analysis_content(scrollable_frame)
    
    def _create_analysis_content(self, parent):
        """Create analysis content with dynamic insights and recommendations"""
        # Title
        tk.Label(parent, text="Folder Comparison Analysis", 
                font=('Arial', 16, 'bold')).pack(pady=(20, 30), padx=20)
        
        # Key insights section
        insights_frame = tk.LabelFrame(parent, text="Key Insights", 
                                      font=('Arial', 12, 'bold'), padx=15, pady=15)
        insights_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        insights = self._generate_dynamic_analysis_insights()
        
        for i, insight in enumerate(insights):
            insight_frame = tk.Frame(insights_frame)
            insight_frame.pack(fill=tk.X, pady=5)
            
            # Insight icon and text
            tk.Label(insight_frame, text=insight['icon'], font=('Arial', 14)).pack(side=tk.LEFT, padx=(0, 10))
            tk.Label(insight_frame, text=insight['text'], font=('Arial', 11), 
                    wraplength=600, justify=tk.LEFT).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Recommendations section
        recommendations_frame = tk.LabelFrame(parent, text="Recommendations", 
                                            font=('Arial', 12, 'bold'), padx=15, pady=15)
        recommendations_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        recommendations = self._generate_dynamic_recommendations()
        
        for i, rec in enumerate(recommendations):
            rec_frame = tk.Frame(recommendations_frame)
            rec_frame.pack(fill=tk.X, pady=5)
            
            # Recommendation priority and text
            tk.Label(rec_frame, text=rec['priority'], font=('Arial', 11, 'bold'), 
                    fg=rec['color']).pack(side=tk.LEFT, padx=(0, 10))
            tk.Label(rec_frame, text=rec['text'], font=('Arial', 11), 
                    wraplength=600, justify=tk.LEFT).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Field analysis section
        field_analysis_frame = tk.LabelFrame(parent, text="Field Structure Analysis", 
                                           font=('Arial', 12, 'bold'), padx=15, pady=15)
        field_analysis_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        field_analysis = self._analyze_field_structures()
        
        for analysis_item in field_analysis:
            analysis_frame = tk.Frame(field_analysis_frame)
            analysis_frame.pack(fill=tk.X, pady=3)
            
            tk.Label(analysis_frame, text=analysis_item['label'], font=('Arial', 11, 'bold')).pack(side=tk.LEFT)
            tk.Label(analysis_frame, text=analysis_item['value'], font=('Arial', 11), 
                    fg=analysis_item.get('color', 'black')).pack(side=tk.RIGHT)
    
    def _generate_dynamic_analysis_insights(self):
        """Generate insights based on actual data without hardcoded field assumptions"""
        insights = []
        
        folder_stats = self.results.get('folder_statistics', {})
        req_stats = self.results.get('aggregated_statistics', {})
        individual_insights = self._calculate_individual_insights()
        
        # Overall change magnitude
        change_pct = req_stats.get('overall_change_percentage', 0)
        if change_pct > 30:
            insights.append({
                'icon': '🔥',
                'text': f"High change volume detected: {change_pct}% of requirements were modified. This indicates significant updates between folder versions."
            })
        elif change_pct > 10:
            insights.append({
                'icon': '⚠️',
                'text': f"Moderate changes detected: {change_pct}% of requirements were modified. Review changes carefully before proceeding."
            })
        else:
            insights.append({
                'icon': '✅',
                'text': f"Low change volume: Only {change_pct}% of requirements were modified. This appears to be a minor update."
            })
        
        # File-level changes
        files_changed = folder_stats.get('files_with_changes', 0)
        total_matched = folder_stats.get('total_matched_files', 0)
        
        if total_matched > 0:
            file_change_pct = (files_changed / total_matched) * 100
            if file_change_pct > 50:
                insights.append({
                    'icon': '📁',
                    'text': f"Widespread file changes: {files_changed} out of {total_matched} matched files ({file_change_pct:.1f}%) have changes."
                })
            else:
                insights.append({
                    'icon': '📂',
                    'text': f"Localized changes: {files_changed} out of {total_matched} matched files ({file_change_pct:.1f}%) have changes."
                })
        
        # Added/deleted files
        added_files = folder_stats.get('files_added', 0)
        deleted_files = folder_stats.get('files_deleted', 0)
        
        if added_files > 0 or deleted_files > 0:
            insights.append({
                'icon': '🔄',
                'text': f"Structural changes detected: {added_files} files added, {deleted_files} files deleted. This may indicate reorganization or significant updates."
            })
        
        # Individual file insights
        if individual_insights.get('parsing_errors', 0) > 0:
            insights.append({
                'icon': '❌',
                'text': f"Parsing issues: {individual_insights['parsing_errors']} files had parsing errors. Check file integrity and format compliance."
            })
        
        if individual_insights.get('largest_change_pct', 0) > 50:
            insights.append({
                'icon': '📊',
                'text': f"Significant individual changes: Largest single file change was {individual_insights['largest_change_pct']:.1f}%. Review high-impact files carefully."
            })
        
        # Field diversity insight
        field_diversity = individual_insights.get('field_diversity', 0)
        if field_diversity > 20:
            insights.append({
                'icon': '🎯',
                'text': f"Rich data structure: {field_diversity} different field types detected. Files contain diverse requirement information."
            })
        elif field_diversity < 5:
            insights.append({
                'icon': '📋',
                'text': f"Simple data structure: Only {field_diversity} field types detected. Files have minimal requirement structure."
            })
        
        return insights
    
    def _generate_dynamic_recommendations(self):
        """Generate recommendations based on actual analysis"""
        recommendations = []
        
        folder_stats = self.results.get('folder_statistics', {})
        req_stats = self.results.get('aggregated_statistics', {})
        individual_insights = self._calculate_individual_insights()
        
        # High priority recommendations
        if individual_insights.get('parsing_errors', 0) > 0:
            recommendations.append({
                'priority': 'HIGH:',
                'color': 'red',
                'text': 'Address parsing errors before proceeding. Check the "Individual Files" tab for specific error details.'
            })
        
        if req_stats.get('overall_change_percentage', 0) > 30:
            recommendations.append({
                'priority': 'HIGH:',
                'color': 'red',
                'text': 'Large-scale changes detected. Consider incremental review and testing before deployment.'
            })
        
        # Medium priority recommendations
        if folder_stats.get('files_added', 0) > 5:
            recommendations.append({
                'priority': 'MEDIUM:',
                'color': 'orange',
                'text': 'Multiple new files added. Verify integration and dependencies with existing requirements.'
            })
        
        if individual_insights.get('largest_change_pct', 0) > 20:
            recommendations.append({
                'priority': 'MEDIUM:',
                'color': 'orange',
                'text': 'Some files have significant changes. Focus review on files with >20% modification rate.'
            })
        
        significant_changes = individual_insights.get('files_with_significant_changes', 0)
        if significant_changes > 0:
            recommendations.append({
                'priority': 'MEDIUM:',
                'color': 'orange',
                'text': f'{significant_changes} files have significant changes (>10%). Prioritize review of these files.'
            })
        
        # Field structure recommendations
        field_diversity = individual_insights.get('field_diversity', 0)
        if field_diversity > 15:
            recommendations.append({
                'priority': 'INFO:',
                'color': 'blue',
                'text': 'High field diversity detected. Consider standardizing requirement structure for consistency.'
            })
        
        # Low priority recommendations
        recommendations.append({
            'priority': 'INFO:',
            'color': 'blue',
            'text': 'Use the "File Hierarchy" tab to explore changes by folder structure.'
        })
        
        recommendations.append({
            'priority': 'INFO:',
            'color': 'blue',
            'text': 'Export detailed statistics for documentation and audit trails.'
        })
        
        return recommendations
    
    def _analyze_field_structures(self):
        """Analyze field structures across files"""
        analysis = []
        
        individual_insights = self._calculate_individual_insights()
        matched_files = self.individual_stats.get('matched_files', {})
        
        # Field diversity analysis
        field_diversity = individual_insights.get('field_diversity', 0)
        analysis.append({
            'label': 'Field Types Detected:',
            'value': str(field_diversity),
            'color': 'darkblue'
        })
        
        # File size analysis
        avg_size = individual_insights.get('avg_file_size_mb', 0)
        analysis.append({
            'label': 'Average File Size:',
            'value': f'{avg_size:.1f} MB',
            'color': 'darkgreen'
        })
        
        # Change distribution analysis
        low_change_count = 0
        medium_change_count = 0
        high_change_count = 0
        
        for file_data in matched_files.values():
            stats = file_data.get('comparison_stats', {})
            change_pct = stats.get('change_percentage', 0)
            
            if change_pct < 5:
                low_change_count += 1
            elif change_pct < 20:
                medium_change_count += 1
            else:
                high_change_count += 1
        
        analysis.extend([
            {
                'label': 'Low Change Files (<5%):',
                'value': str(low_change_count),
                'color': 'darkgreen'
            },
            {
                'label': 'Medium Change Files (5-20%):',
                'value': str(medium_change_count),
                'color': 'darkorange'
            },
            {
                'label': 'High Change Files (>20%):',
                'value': str(high_change_count),
                'color': 'darkred'
            }
        ])
        
        return analysis
    
    def _show_detailed_individual_stats(self):
        """Show detailed individual file statistics dialog"""
        stats_window = tk.Toplevel(self.window)
        stats_window.title("Detailed Individual File Statistics")
        stats_window.geometry("700x600")
        stats_window.transient(self.window)
        
        main_frame = tk.Frame(stats_window, padx=25, pady=25)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        tk.Label(main_frame, text="Individual File Statistics Summary", 
                font=('Arial', 16, 'bold')).pack(pady=(0, 20))
        
        # Statistics frame with scrolling
        stats_frame = tk.Frame(main_frame)
        stats_frame.pack(fill=tk.BOTH, expand=True)
        
        text_widget = tk.Text(stats_frame, wrap=tk.WORD, font=('Arial', 11))
        scrollbar = ttk.Scrollbar(stats_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Generate detailed statistics
        detailed_stats = self._generate_detailed_individual_stats()
        text_widget.insert(tk.END, detailed_stats)
        text_widget.configure(state=tk.DISABLED)
        
        # Close button
        tk.Button(main_frame, text="Close", command=stats_window.destroy,
                 font=('Arial', 11), relief='raised', bd=2, padx=20, pady=6,
                 cursor='hand2').pack(pady=(20, 0))
    
    def _generate_detailed_individual_stats(self):
        """Generate detailed individual file statistics text with dynamic field analysis"""
        lines = [
            "DETAILED INDIVIDUAL FILE STATISTICS",
            "=" * 50,
            ""
        ]
        
        # Matched files statistics
        matched_files = self.individual_stats.get('matched_files', {})
        if matched_files:
            lines.extend([
                f"MATCHED FILES ANALYSIS ({len(matched_files)} files)",
                "-" * 40,
                ""
            ])
            
            # Sort by change percentage
            sorted_matched = sorted(matched_files.items(), 
                                  key=lambda x: x[1].get('comparison_stats', {}).get('change_percentage', 0), 
                                  reverse=True)
            
            for file_path, file_data in sorted_matched[:10]:  # Top 10 changed files
                stats = file_data.get('comparison_stats', {})
                change_pct = stats.get('change_percentage', 0)
                
                lines.append(f"📄 {file_path}")
                lines.append(f"   Change Rate: {change_pct:.1f}%")
                lines.append(f"   Match Type: {file_data.get('match_type', 'unknown')}")
                lines.append(f"   Similarity: {file_data.get('similarity', 0):.2f}")
                
                # Requirements changes
                added = stats.get('added_count', 0)
                deleted = stats.get('deleted_count', 0)
                modified = stats.get('modified_count', 0)
                unchanged = stats.get('unchanged_count', 0)
                
                lines.append(f"   Requirements: +{added}, -{deleted}, ~{modified}, ={unchanged}")
                
                # File sizes
                file1_info = file_data.get('file1_info', {})
                file2_info = file_data.get('file2_info', {})
                
                if isinstance(file1_info, dict) and isinstance(file2_info, dict):
                    size1 = file1_info.get('size', 0) / (1024*1024)
                    size2 = file2_info.get('size', 0) / (1024*1024)
                    lines.append(f"   File Size: {size1:.1f}MB → {size2:.1f}MB")
                
                # Show additional detected fields
                available_fields = set()
                for info in [file1_info, file2_info, stats]:
                    if isinstance(info, dict):
                        available_fields.update(info.keys())
                
                interesting_fields = available_fields - {'size', 'filename', 'full_path', 'relative_path'}
                if interesting_fields:
                    field_list = ', '.join(sorted(list(interesting_fields))[:5])
                    lines.append(f"   Available Fields: {field_list}")
                
                lines.append("")
            
            if len(matched_files) > 10:
                lines.append(f"... and {len(matched_files) - 10} more matched files")
                lines.append("")
        
        # Added files statistics
        added_files = self.individual_stats.get('added_files', {})
        if added_files:
            lines.extend([
                f"ADDED FILES ANALYSIS ({len(added_files)} files)",
                "-" * 40,
                ""
            ])
            
            total_added_reqs = 0
            parsing_errors = 0
            
            for file_path, file_data in added_files.items():
                req_count = file_data.get('requirement_count', 0)
                file_size = file_data.get('file_size_mb', 0)
                parsing_success = file_data.get('parsing_success', False)
                
                total_added_reqs += req_count
                if not parsing_success:
                    parsing_errors += 1
                
                status_icon = "✅" if parsing_success else "❌"
                lines.append(f"{status_icon} {file_path}")
                lines.append(f"   Requirements: {req_count}")
                lines.append(f"   File Size: {file_size:.1f}MB")
                
                if not parsing_success:
                    error = file_data.get('error', 'Unknown error')
                    lines.append(f"   Error: {error}")
                
                # Show file info fields if available
                file_info = file_data.get('file_info', {})
                if isinstance(file_info, dict):
                    interesting_fields = set(file_info.keys()) - {'size', 'filename', 'full_path', 'relative_path'}
                    if interesting_fields:
                        field_list = ', '.join(sorted(list(interesting_fields))[:3])
                        lines.append(f"   File Fields: {field_list}")
                
                lines.append("")
            
            lines.extend([
                f"Total Requirements in Added Files: {total_added_reqs}",
                f"Parsing Errors: {parsing_errors}",
                ""
            ])
        
        # Deleted files statistics
        deleted_files = self.individual_stats.get('deleted_files', {})
        if deleted_files:
            lines.extend([
                f"DELETED FILES ANALYSIS ({len(deleted_files)} files)",
                "-" * 40,
                ""
            ])
            
            total_deleted_reqs = 0
            parsing_errors = 0
            
            for file_path, file_data in deleted_files.items():
                req_count = file_data.get('requirement_count', 0)
                file_size = file_data.get('file_size_mb', 0)
                parsing_success = file_data.get('parsing_success', False)
                
                total_deleted_reqs += req_count
                if not parsing_success:
                    parsing_errors += 1
                
                status_icon = "✅" if parsing_success else "❌"
                lines.append(f"{status_icon} {file_path}")
                lines.append(f"   Requirements: {req_count}")
                lines.append(f"   File Size: {file_size:.1f}MB")
                
                if not parsing_success:
                    error = file_data.get('error', 'Unknown error')
                    lines.append(f"   Error: {error}")
                lines.append("")
            
            lines.extend([
                f"Total Requirements in Deleted Files: {total_deleted_reqs}",
                f"Parsing Errors: {parsing_errors}",
                ""
            ])
        
        # Field analysis summary
        lines.extend([
            "FIELD STRUCTURE ANALYSIS",
            "-" * 40,
            ""
        ])
        
        field_analysis = self._analyze_field_structures()
        for analysis_item in field_analysis:
            lines.append(f"{analysis_item['label']} {analysis_item['value']}")
        
        return '\n'.join(lines)
    
    # Original methods (updated for dynamic field support)
    def _populate_hierarchical_tree(self):
        """Populate the hierarchical tree view with dynamic field support"""
        # Clear existing content
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get file results
        file_results = self.results.get('file_results', {})
        
        # Create folder structure
        folder_structure = self._build_folder_structure(file_results)
        
        # Populate tree with folder structure
        self._insert_folder_nodes(folder_structure)
    
    def _build_folder_structure(self, file_results):
        """Build hierarchical folder structure from file results"""
        structure = {
            'folders': {},
            'files': []
        }
        
        # Process matched files
        for file_result in file_results.get('matched_files', []):
            file1_info = file_result.get('file1_info', {})
            file2_info = file_result.get('file2_info', {})
            
            # Use file1 path as primary, fallback to file2
            rel_path = file1_info.get('relative_path', file2_info.get('relative_path', 'unknown'))
            parent_dir = file1_info.get('parent_dir', file2_info.get('parent_dir', ''))
            
            file_node = {
                'type': 'matched_file',
                'relative_path': rel_path,
                'parent_dir': parent_dir,
                'file_result': file_result,
                'status': self._get_file_status(file_result),
                'changes': self._get_file_changes_summary(file_result),
                'match_type': file_result.get('match_type', 'exact')
            }
            
            # Add file size if available
            if isinstance(file1_info, dict) and file1_info.get('size'):
                size_mb = file1_info['size'] / (1024 * 1024)
                file_node['file_size'] = f"{size_mb:.1f}"
            else:
                file_node['file_size'] = 'N/A'
            
            self._add_to_folder_structure(structure, file_node, parent_dir)
        
        # Process added files
        for file_info in file_results.get('added_files', []):
            file_node = {
                'type': 'added_file',
                'relative_path': file_info.get('relative_path', 'unknown'),
                'parent_dir': file_info.get('parent_dir', ''),
                'file_info': file_info,
                'status': 'Added',
                'changes': 'New file',
                'match_type': 'N/A'
            }
            
            # Add file size if available
            if isinstance(file_info, dict) and file_info.get('size'):
                size_mb = file_info['size'] / (1024 * 1024)
                file_node['file_size'] = f"{size_mb:.1f}"
            else:
                file_node['file_size'] = 'N/A'
            
            self._add_to_folder_structure(structure, file_node, file_info.get('parent_dir', ''))
        
        # Process deleted files
        for file_info in file_results.get('deleted_files', []):
            file_node = {
                'type': 'deleted_file',
                'relative_path': file_info.get('relative_path', 'unknown'),
                'parent_dir': file_info.get('parent_dir', ''),
                'file_info': file_info,
                'status': 'Deleted',
                'changes': 'File removed',
                'match_type': 'N/A'
            }
            
            # Add file size if available
            if isinstance(file_info, dict) and file_info.get('size'):
                size_mb = file_info['size'] / (1024 * 1024)
                file_node['file_size'] = f"{size_mb:.1f}"
            else:
                file_node['file_size'] = 'N/A'
            
            self._add_to_folder_structure(structure, file_node, file_info.get('parent_dir', ''))
        
        return structure
    
    def _add_to_folder_structure(self, structure, file_node, parent_dir):
        """Add file node to folder structure"""
        if not parent_dir or parent_dir == '.':
            # Root level file
            structure['files'].append(file_node)
        else:
            # Nested file - create folder hierarchy
            folder_parts = parent_dir.split(os.sep)
            current_level = structure
            
            for part in folder_parts:
                if 'folders' not in current_level:
                    current_level['folders'] = {}
                
                if part not in current_level['folders']:
                    current_level['folders'][part] = {
                        'folders': {},
                        'files': []
                    }
                
                current_level = current_level['folders'][part]
            
            current_level['files'].append(file_node)
    
    def _insert_folder_nodes(self, structure, parent_id=''):
        """Recursively insert folder nodes into tree with dynamic values"""
        # Insert files at current level
        for file_node in structure.get('files', []):
            filename = os.path.basename(file_node['relative_path'])
            
            # Determine icon based on file type
            if file_node['type'] == 'added_file':
                icon = '📄➕'
                tag = 'added_file'
            elif file_node['type'] == 'deleted_file':
                icon = '📄➖'
                tag = 'deleted_file'
            else:
                icon = '📄'
                tag = 'matched_file'
            
            # Build values list dynamically based on tree columns
            values = []
            for col in self.tree['columns']:
                if col == 'status':
                    values.append(file_node['status'])
                elif col == 'type':
                    values.append(file_node['type'].replace('_', ' ').title())
                elif col == 'changes':
                    values.append(file_node['changes'])
                elif col == 'match_type':
                    values.append(file_node['match_type'])
                elif col == 'file_size':
                    values.append(file_node.get('file_size', 'N/A'))
                else:
                    # Handle any additional columns
                    values.append(file_node.get(col, ''))
            
            item_id = self.tree.insert(parent_id, 'end', 
                                      text=f"{icon} {filename}",
                                      values=values,
                                      tags=[tag])
            
            # Store file data for drill-down
            if not hasattr(self, 'item_file_data'):
                self.item_file_data = {}
            self.item_file_data[item_id] = file_node
        
        # Insert subfolders
        for folder_name, folder_data in structure.get('folders', {}).items():
            # Count files in this folder (recursive)
            file_count = self._count_files_recursive(folder_data)
            
            # Build folder values
            folder_values = []
            for col in self.tree['columns']:
                if col == 'status':
                    folder_values.append('Folder')
                elif col == 'type':
                    folder_values.append('Directory')
                elif col == 'changes':
                    folder_values.append(f"{file_count} files")
                elif col == 'match_type':
                    folder_values.append('N/A')
                else:
                    folder_values.append('')
            
            folder_item_id = self.tree.insert(parent_id, 'end',
                                             text=f"📁 {folder_name}",
                                             values=folder_values,
                                             tags=['folder'])
            
            # Recursively insert subfolder contents
            self._insert_folder_nodes(folder_data, folder_item_id)
    
    def _count_files_recursive(self, folder_data):
        """Count files recursively in folder structure"""
        count = len(folder_data.get('files', []))
        
        for subfolder_data in folder_data.get('folders', {}).values():
            count += self._count_files_recursive(subfolder_data)
        
        return count
    
    def _get_file_status(self, file_result):
        """Get status for matched file based on available statistics"""
        stats = file_result.get('statistics', {})
        
        # Check for any type of changes
        change_indicators = ['added_count', 'deleted_count', 'modified_count', 'change_percentage']
        has_changes = False
        
        for indicator in change_indicators:
            if stats.get(indicator, 0) > 0:
                has_changes = True
                break
        
        return 'Modified' if has_changes else 'Unchanged'
    
    def _get_file_changes_summary(self, file_result):
        """Get changes summary for matched file with dynamic field support"""
        stats = file_result.get('statistics', {})
        
        changes = []
        if stats.get('added_count', 0) > 0:
            changes.append(f"+{stats['added_count']}")
        if stats.get('deleted_count', 0) > 0:
            changes.append(f"-{stats['deleted_count']}")
        if stats.get('modified_count', 0) > 0:
            changes.append(f"~{stats['modified_count']}")
        
        if changes:
            return f"Reqs: {', '.join(changes)}"
        else:
            return "No changes"
    
    def _create_controls_section(self):
        """Create enhanced control buttons"""
        controls_frame = tk.Frame(self.main_frame)
        controls_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Left side buttons
        left_buttons = tk.Frame(controls_frame)
        left_buttons.pack(side=tk.LEFT)
        
        # Expand/Collapse buttons
        tk.Button(left_buttons, text="🔽 Expand All", command=self._expand_all,
                 font=('Arial', 10), relief='raised', bd=2,
                 padx=15, pady=5, cursor='hand2').pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(left_buttons, text="🔼 Collapse All", command=self._collapse_all,
                 font=('Arial', 10), relief='raised', bd=2,
                 padx=15, pady=5, cursor='hand2').pack(side=tk.LEFT, padx=(0, 20))
        
        # Export buttons (enhanced)
        tk.Button(left_buttons, text="📄 Export Summary", command=self._export_summary,
                 font=('Arial', 11, 'bold'), relief='raised', bd=2,
                 padx=20, pady=6, cursor='hand2', bg='lightblue').pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(left_buttons, text="📊 Export Individual Stats", command=self._export_individual_stats,
                 font=('Arial', 11, 'bold'), relief='raised', bd=2,
                 padx=20, pady=6, cursor='hand2', bg='lightgreen').pack(side=tk.LEFT, padx=(0, 15))
        
        # Close button
        tk.Button(controls_frame, text="✖️ Close", command=self._on_closing,
                 font=('Arial', 11), relief='raised', bd=2,
                 padx=20, pady=6, cursor='hand2').pack(side=tk.RIGHT)
    
    def _export_individual_stats(self):
        """Export individual file statistics to CSV with dynamic fields"""
        try:
            filename = filedialog.asksaveasfilename(
                title="Export Individual File Statistics",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile="individual_file_statistics.csv"
            )
            
            if not filename:
                return
            
            # Collect all possible fields from all file categories
            all_fields = set(['Category', 'File_Path'])
            
            # Add base fields
            base_fields = ['Match_Type', 'Similarity', 'Requirements_Original', 'Requirements_Modified', 
                          'Added_Reqs', 'Deleted_Reqs', 'Modified_Reqs', 'Unchanged_Reqs',
                          'Change_Percentage', 'Parsing_Success', 'Error_Details']
            all_fields.update(base_fields)
            
            # Add dynamic fields from file info and stats
            for category in ['matched_files', 'added_files', 'deleted_files']:
                files_data = self.individual_stats.get(category, {})
                for file_data in files_data.values():
                    # Add file info fields
                    for info_key in ['file1_info', 'file2_info', 'file_info']:
                        info = file_data.get(info_key, {})
                        if isinstance(info, dict):
                            for field in info.keys():
                                if field not in ['full_path', 'relative_path']:
                                    all_fields.add(f'File_{field}')
                    
                    # Add comparison stats fields
                    stats = file_data.get('comparison_stats', {})
                    if isinstance(stats, dict):
                        for field in stats.keys():
                            all_fields.add(f'Stats_{field}')
            
            # Convert to sorted list
            sorted_fields = sorted(all_fields)
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                writer.writerow(sorted_fields)
                
                # Write matched files
                for file_path, file_data in self.individual_stats.get('matched_files', {}).items():
                    row = self._build_csv_row(sorted_fields, 'Matched', file_path, file_data)
                    writer.writerow(row)
                
                # Write added files
                for file_path, file_data in self.individual_stats.get('added_files', {}).items():
                    row = self._build_csv_row(sorted_fields, 'Added', file_path, file_data)
                    writer.writerow(row)
                
                # Write deleted files
                for file_path, file_data in self.individual_stats.get('deleted_files', {}).items():
                    row = self._build_csv_row(sorted_fields, 'Deleted', file_path, file_data)
                    writer.writerow(row)
            
            messagebox.showinfo("Export Complete", 
                               f"Individual file statistics exported to:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Export Error", 
                               f"Failed to export individual statistics:\n{str(e)}")
    
    def _build_csv_row(self, fields, category, file_path, file_data):
        """Build CSV row with dynamic field support"""
        row = []
        
        for field in fields:
            if field == 'Category':
                row.append(category)
            elif field == 'File_Path':
                row.append(file_path)
            elif field == 'Match_Type':
                row.append(file_data.get('match_type', 'N/A'))
            elif field == 'Similarity':
                similarity = file_data.get('similarity', 0)
                row.append(f"{similarity:.3f}" if similarity else 'N/A')
            elif field.startswith('Requirements_') or field.endswith('_Reqs'):
                stats = file_data.get('comparison_stats', {})
                if field == 'Requirements_Original':
                    row.append(stats.get('total_file1', 0))
                elif field == 'Requirements_Modified':
                    row.append(stats.get('total_file2', 0))
                elif field == 'Added_Reqs':
                    row.append(stats.get('added_count', 0))
                elif field == 'Deleted_Reqs':
                    row.append(stats.get('deleted_count', 0))
                elif field == 'Modified_Reqs':
                    row.append(stats.get('modified_count', 0))
                elif field == 'Unchanged_Reqs':
                    row.append(stats.get('unchanged_count', 0))
                else:
                    row.append('')
            elif field == 'Change_Percentage':
                stats = file_data.get('comparison_stats', {})
                change_pct = stats.get('change_percentage', 0)
                row.append(f"{change_pct:.2f}" if change_pct else 'N/A')
            elif field == 'Parsing_Success':
                row.append(str(file_data.get('parsing_success', True)))
            elif field == 'Error_Details':
                row.append(file_data.get('error', ''))
            elif field.startswith('File_'):
                # Handle file info fields
                field_name = field[5:]  # Remove 'File_' prefix
                for info_key in ['file1_info', 'file2_info', 'file_info']:
                    info = file_data.get(info_key, {})
                    if isinstance(info, dict) and field_name in info:
                        value = info[field_name]
                        if field_name == 'size' and isinstance(value, (int, float)):
                            row.append(f"{value / (1024*1024):.2f}")  # Convert to MB
                        else:
                            row.append(str(value))
                        break
                else:
                    row.append('')
            elif field.startswith('Stats_'):
                # Handle stats fields
                field_name = field[6:]  # Remove 'Stats_' prefix
                stats = file_data.get('comparison_stats', {})
                if isinstance(stats, dict):
                    row.append(str(stats.get(field_name, '')))
                else:
                    row.append('')
            else:
                row.append('')
        
        return row
    
    # Remaining original methods (unchanged functionality)
    def _on_tree_double_click(self, event):
        """Handle double-click on tree item"""
        item_id = self.tree.selection()[0] if self.tree.selection() else None
        if not item_id:
            return
        
        tags = self.tree.item(item_id, 'tags')
        
        if 'matched_file' in tags:
            # Show detailed file comparison
            file_data = self.item_file_data.get(item_id)
            if file_data:
                self._show_file_comparison(file_data)
        elif 'folder' in tags:
            # Toggle folder expansion
            if self.tree.item(item_id, 'open'):
                self.tree.item(item_id, open=False)
            else:
                self.tree.item(item_id, open=True)
    
    def _show_file_comparison(self, file_node):
        """Show detailed comparison for a file"""
        try:
            if file_node['type'] != 'matched_file':
                messagebox.showinfo("No Comparison", 
                                   "Detailed comparison is only available for matched files.")
                return
            
            file_result = file_node.get('file_result')
            if not file_result:
                messagebox.showerror("Error", "No comparison data available for this file.")
                return
            
            # Check if window already exists
            file_path = file_node['relative_path']
            if file_path in self.file_comparison_windows:
                try:
                    # Bring existing window to front
                    self.file_comparison_windows[file_path].window.lift()
                    self.file_comparison_windows[file_path].window.focus_set()
                    return
                except:
                    # Window was closed, remove from tracking
                    del self.file_comparison_windows[file_path]
            
            # Create new comparison window
            comparison_window = ComparisonResultsGUI(self.window, file_result)
            comparison_window.window.title(f"File Comparison - {os.path.basename(file_path)}")
            
            # Track window
            self.file_comparison_windows[file_path] = comparison_window
            
            # Remove from tracking when window is closed
            original_close = comparison_window._on_closing
            def tracked_close():
                if file_path in self.file_comparison_windows:
                    del self.file_comparison_windows[file_path]
                original_close()
            
            comparison_window._on_closing = tracked_close
            comparison_window.window.protocol("WM_DELETE_WINDOW", tracked_close)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to show file comparison:\n{str(e)}")
    
    def _on_tree_expand(self, event):
        """Handle tree node expansion"""
        item_id = self.tree.selection()[0] if self.tree.selection() else None
        if item_id:
            self.expanded_nodes.add(item_id)
    
    def _on_tree_collapse(self, event):
        """Handle tree node collapse"""
        item_id = self.tree.selection()[0] if self.tree.selection() else None
        if item_id and item_id in self.expanded_nodes:
            self.expanded_nodes.remove(item_id)
    
    def _expand_all(self):
        """Expand all tree nodes"""
        def expand_recursive(item_id):
            self.tree.item(item_id, open=True)
            for child_id in self.tree.get_children(item_id):
                expand_recursive(child_id)
        
        for root_item in self.tree.get_children():
            expand_recursive(root_item)
    
    def _collapse_all(self):
        """Collapse all tree nodes"""
        def collapse_recursive(item_id):
            self.tree.item(item_id, open=False)
            for child_id in self.tree.get_children(item_id):
                collapse_recursive(child_id)
        
        for root_item in self.tree.get_children():
            collapse_recursive(root_item)
    
    def _export_summary(self):
        """Export folder comparison summary (enhanced)"""
        try:
            filename = filedialog.asksaveasfilename(
                title="Export Folder Comparison Summary",
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                initialfile="enhanced_folder_comparison_summary.txt"
            )
            
            if not filename:
                return
            
            # Generate enhanced summary using folder_comparator export method
            from folder_comparator import FolderComparator
            comparator = FolderComparator()
            summary = comparator.export_folder_summary_enhanced(self.results)
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(summary)
            
            messagebox.showinfo("Export Complete", 
                               f"Enhanced folder comparison summary exported to:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Export Error", 
                               f"Failed to export summary:\n{str(e)}")
    
    def _on_closing(self):
        """Handle window closing"""
        try:
            # Close all file comparison windows
            for window in list(self.file_comparison_windows.values()):
                try:
                    window.window.destroy()
                except:
                    pass
            
            self.file_comparison_windows.clear()
            
            # Close main window
            self.window.destroy()
        except:
            pass


# Example usage
if __name__ == "__main__":
    print("Enhanced Folder Comparison Results GUI - Updated Version")
    print("New features:")
    print("- Dynamic field detection without hardcoded assumptions")
    print("- Enhanced export capabilities with all detected fields")
    print("- Intelligent analysis insights based on actual data")
    print("- Backward compatibility maintained")