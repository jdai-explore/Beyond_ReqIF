#!/usr/bin/env python3
"""
Enhanced Folder Comparison Results GUI - Native Version
Added individual file statistics display without impacting existing functionality
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import os
from typing import Dict, List, Any, Optional
from comparison_gui import ComparisonResultsGUI


class FolderComparisonResultsGUI:
    """
    Enhanced Folder Comparison Results GUI with individual file statistics
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
        
        # Individual file statistics (NEW)
        self.individual_stats = results.get('individual_file_statistics', {})
        
        # Storage for file data (to avoid treeview column issues)
        self.item_file_data = {}
        
        # Setup GUI
        self.setup_gui()
        
        # Handle window closing
        self.window.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def setup_gui(self):
        """Setup enhanced native GUI with individual file statistics"""
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
        self._create_individual_insights_summary(summary_frame)  # NEW
    
    def _create_folder_summary(self, parent, folder_stats):
        """Create folder-level summary (unchanged)"""
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
        """Create requirements-level summary (unchanged)"""
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
        """NEW: Create individual file insights summary"""
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
        """Calculate insights from individual file statistics"""
        insights = {
            'total_files_analyzed': 0,
            'parsing_errors': 0,
            'largest_change_pct': 0,
            'avg_file_size_mb': 0,
            'files_with_significant_changes': 0  # >10% change
        }
        
        file_sizes = []
        
        # Analyze matched files
        matched_files = self.individual_stats.get('matched_files', {})
        insights['total_files_analyzed'] += len(matched_files)
        
        for file_path, file_data in matched_files.items():
            stats = file_data.get('comparison_stats', {})
            change_pct = stats.get('change_percentage', 0)
            
            if change_pct > insights['largest_change_pct']:
                insights['largest_change_pct'] = change_pct
            
            if change_pct > 10:
                insights['files_with_significant_changes'] += 1
            
            # Collect file sizes
            file1_size = file_data.get('file1_info', {}).get('size', 0)
            file2_size = file_data.get('file2_info', {}).get('size', 0)
            file_sizes.extend([file1_size, file2_size])
        
        # Analyze added files
        added_files = self.individual_stats.get('added_files', {})
        insights['total_files_analyzed'] += len(added_files)
        
        for file_path, file_data in added_files.items():
            if not file_data.get('parsing_success', True):
                insights['parsing_errors'] += 1
            
            file_size = file_data.get('file_info', {}).get('size', 0)
            file_sizes.append(file_size)
        
        # Analyze deleted files
        deleted_files = self.individual_stats.get('deleted_files', {})
        insights['total_files_analyzed'] += len(deleted_files)
        
        for file_path, file_data in deleted_files.items():
            if not file_data.get('parsing_success', True):
                insights['parsing_errors'] += 1
            
            file_size = file_data.get('file_info', {}).get('size', 0)
            file_sizes.append(file_size)
        
        # Calculate average file size
        if file_sizes:
            avg_size_bytes = sum(file_sizes) / len(file_sizes)
            insights['avg_file_size_mb'] = avg_size_bytes / (1024 * 1024)
        
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
        self._create_individual_stats_tab()          # NEW: Individual file statistics
        self._create_comparison_analysis_tab()       # NEW: Comparison analysis
    
    def _create_hierarchical_results_tab(self):
        """Create hierarchical results display tab (original functionality)"""
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
        
        # Create treeview with columns
        columns = ['status', 'type', 'changes', 'match_type']
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='tree headings')
        
        # Configure columns
        self.tree.heading('#0', text='File/Folder', anchor=tk.W)
        self.tree.column('#0', width=400, minwidth=200)
        
        column_config = {
            'status': ('Status', 120, 80),
            'type': ('Type', 100, 80),
            'changes': ('Changes', 200, 120),
            'match_type': ('Match', 100, 80)
        }
        
        for col, (display_name, width, minwidth) in column_config.items():
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
    
    def _create_individual_stats_tab(self):
        """NEW: Create individual file statistics tab"""
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
        """Create matched files statistics tab"""
        matched_frame = tk.Frame(parent_notebook)
        parent_notebook.add(matched_frame, text=f"🔄 Matched ({len(self.individual_stats.get('matched_files', {}))})")
        
        # Create treeview for matched files
        tree_frame = tk.Frame(matched_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ['match_type', 'similarity', 'changes', 'change_pct', 'file1_size', 'file2_size', 'requirements']
        matched_tree = ttk.Treeview(tree_frame, columns=columns, show='tree headings')
        
        # Configure columns
        matched_tree.heading('#0', text='File Path', anchor=tk.W)
        matched_tree.column('#0', width=300, minwidth=200)
        
        column_config = {
            'match_type': ('Match Type', 80, 60),
            'similarity': ('Similarity', 80, 60),
            'changes': ('Changes', 120, 80),
            'change_pct': ('Change %', 70, 50),
            'file1_size': ('Size 1 (MB)', 90, 70),
            'file2_size': ('Size 2 (MB)', 90, 70),
            'requirements': ('Reqs (1→2)', 100, 80)
        }
        
        for col, (display_name, width, minwidth) in column_config.items():
            matched_tree.heading(col, text=display_name, anchor=tk.W)
            matched_tree.column(col, width=width, minwidth=minwidth)
        
        # Pack with scrollbars
        matched_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        v_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=matched_tree.yview)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        matched_tree.configure(yscrollcommand=v_scroll.set)
        
        # Populate matched files data
        for file_path, file_data in self.individual_stats.get('matched_files', {}).items():
            stats = file_data.get('comparison_stats', {})
            
            # Calculate display values
            match_type = file_data.get('match_type', 'unknown')
            similarity = f"{file_data.get('similarity', 0):.2f}"
            
            # Changes summary
            changes = []
            if stats.get('added_count', 0) > 0:
                changes.append(f"+{stats['added_count']}")
            if stats.get('deleted_count', 0) > 0:
                changes.append(f"-{stats['deleted_count']}")
            if stats.get('modified_count', 0) > 0:
                changes.append(f"~{stats['modified_count']}")
            
            changes_str = ", ".join(changes) if changes else "None"
            change_pct = f"{stats.get('change_percentage', 0):.1f}%"
            
            # File sizes
            file1_size = f"{file_data.get('file1_info', {}).get('size', 0) / (1024*1024):.1f}"
            file2_size = f"{file_data.get('file2_info', {}).get('size', 0) / (1024*1024):.1f}"
            
            # Requirements count
            reqs1 = stats.get('total_file1', 0)
            reqs2 = stats.get('total_file2', 0)
            reqs_str = f"{reqs1}→{reqs2}"
            
            values = [match_type, similarity, changes_str, change_pct, file1_size, file2_size, reqs_str]
            
            # Add color coding based on change percentage
            item_id = matched_tree.insert('', 'end', text=file_path, values=values)
            
            # Tag for color coding
            if stats.get('change_percentage', 0) > 20:
                matched_tree.set(item_id, 'tag', 'high_change')
            elif stats.get('change_percentage', 0) > 5:
                matched_tree.set(item_id, 'tag', 'medium_change')
            else:
                matched_tree.set(item_id, 'tag', 'low_change')
    
    def _create_added_files_stats_tab(self, parent_notebook):
        """Create added files statistics tab"""
        added_frame = tk.Frame(parent_notebook)
        parent_notebook.add(added_frame, text=f"➕ Added ({len(self.individual_stats.get('added_files', {}))})")
        
        # Create treeview for added files
        tree_frame = tk.Frame(added_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ['requirements', 'file_size', 'parsing_status', 'error']
        added_tree = ttk.Treeview(tree_frame, columns=columns, show='tree headings')
        
        # Configure columns
        added_tree.heading('#0', text='File Path', anchor=tk.W)
        added_tree.column('#0', width=400, minwidth=250)
        
        column_config = {
            'requirements': ('Requirements', 100, 80),
            'file_size': ('Size (MB)', 80, 60),
            'parsing_status': ('Status', 80, 60),
            'error': ('Error Details', 300, 200)
        }
        
        for col, (display_name, width, minwidth) in column_config.items():
            added_tree.heading(col, text=display_name, anchor=tk.W)
            added_tree.column(col, width=width, minwidth=minwidth)
        
        # Pack with scrollbars
        added_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        v_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=added_tree.yview)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        added_tree.configure(yscrollcommand=v_scroll.set)
        
        # Populate added files data
        for file_path, file_data in self.individual_stats.get('added_files', {}).items():
            req_count = file_data.get('requirement_count', 0)
            file_size = file_data.get('file_size_mb', 0)
            parsing_success = file_data.get('parsing_success', False)
            error = file_data.get('error', '') if not parsing_success else ''
            
            status = "✓ Success" if parsing_success else "❌ Error"
            
            values = [str(req_count), f"{file_size:.1f}", status, error]
            
            added_tree.insert('', 'end', text=file_path, values=values)
    
    def _create_deleted_files_stats_tab(self, parent_notebook):
        """Create deleted files statistics tab"""
        deleted_frame = tk.Frame(parent_notebook)
        parent_notebook.add(deleted_frame, text=f"➖ Deleted ({len(self.individual_stats.get('deleted_files', {}))})")
        
        # Create treeview for deleted files
        tree_frame = tk.Frame(deleted_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ['requirements', 'file_size', 'parsing_status', 'error']
        deleted_tree = ttk.Treeview(tree_frame, columns=columns, show='tree headings')
        
        # Configure columns
        deleted_tree.heading('#0', text='File Path', anchor=tk.W)
        deleted_tree.column('#0', width=400, minwidth=250)
        
        column_config = {
            'requirements': ('Requirements', 100, 80),
            'file_size': ('Size (MB)', 80, 60),
            'parsing_status': ('Status', 80, 60),
            'error': ('Error Details', 300, 200)
        }
        
        for col, (display_name, width, minwidth) in column_config.items():
            deleted_tree.heading(col, text=display_name, anchor=tk.W)
            deleted_tree.column(col, width=width, minwidth=minwidth)
        
        # Pack with scrollbars
        deleted_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        v_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=deleted_tree.yview)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        deleted_tree.configure(yscrollcommand=v_scroll.set)
        
        # Populate deleted files data
        for file_path, file_data in self.individual_stats.get('deleted_files', {}).items():
            req_count = file_data.get('requirement_count', 0)
            file_size = file_data.get('file_size_mb', 0)
            parsing_success = file_data.get('parsing_success', False)
            error = file_data.get('error', '') if not parsing_success else ''
            
            status = "✓ Success" if parsing_success else "❌ Error"
            
            values = [str(req_count), f"{file_size:.1f}", status, error]
            
            deleted_tree.insert('', 'end', text=file_path, values=values)
    
    def _create_comparison_analysis_tab(self):
        """NEW: Create comparison analysis tab with insights"""
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
        """Create analysis content with insights and recommendations"""
        # Title
        tk.Label(parent, text="Folder Comparison Analysis", 
                font=('Arial', 16, 'bold')).pack(pady=(20, 30), padx=20)
        
        # Key insights section
        insights_frame = tk.LabelFrame(parent, text="Key Insights", 
                                      font=('Arial', 12, 'bold'), padx=15, pady=15)
        insights_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        insights = self._generate_analysis_insights()
        
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
        
        recommendations = self._generate_recommendations()
        
        for i, rec in enumerate(recommendations):
            rec_frame = tk.Frame(recommendations_frame)
            rec_frame.pack(fill=tk.X, pady=5)
            
            # Recommendation priority and text
            tk.Label(rec_frame, text=rec['priority'], font=('Arial', 11, 'bold'), 
                    fg=rec['color']).pack(side=tk.LEFT, padx=(0, 10))
            tk.Label(rec_frame, text=rec['text'], font=('Arial', 11), 
                    wraplength=600, justify=tk.LEFT).pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def _generate_analysis_insights(self):
        """Generate key insights from the comparison data"""
        insights = []
        
        folder_stats = self.results.get('folder_statistics', {})
        req_stats = self.results.get('aggregated_statistics', {})
        
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
        individual_insights = self._calculate_individual_insights()
        
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
        
        return insights
    
    def _generate_recommendations(self):
        """Generate recommendations based on analysis"""
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
        """Generate detailed individual file statistics text"""
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
                size1 = file_data.get('file1_info', {}).get('size', 0) / (1024*1024)
                size2 = file_data.get('file2_info', {}).get('size', 0) / (1024*1024)
                lines.append(f"   File Size: {size1:.1f}MB → {size2:.1f}MB")
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
        
        return '\n'.join(lines)
    
    # Original methods (unchanged functionality)
    def _populate_hierarchical_tree(self):
        """Populate the hierarchical tree view (unchanged)"""
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
        """Build hierarchical folder structure from file results (unchanged)"""
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
            
            self._add_to_folder_structure(structure, file_node, file_info.get('parent_dir', ''))
        
        return structure
    
    def _add_to_folder_structure(self, structure, file_node, parent_dir):
        """Add file node to folder structure (unchanged)"""
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
        """Recursively insert folder nodes into tree (unchanged)"""
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
            
            values = [
                file_node['status'],
                file_node['type'].replace('_', ' ').title(),
                file_node['changes'],
                file_node['match_type']
            ]
            
            item_id = self.tree.insert(parent_id, 'end', 
                                      text=f"{icon} {filename}",
                                      values=values,
                                      tags=[tag])
            
            # Store file data for drill-down using item tags
            # Note: Cannot use tree.set() for non-column data, so we'll store in a separate dict
            if not hasattr(self, 'item_file_data'):
                self.item_file_data = {}
            self.item_file_data[item_id] = file_node
        
        # Insert subfolders
        for folder_name, folder_data in structure.get('folders', {}).items():
            # Count files in this folder (recursive)
            file_count = self._count_files_recursive(folder_data)
            
            folder_item_id = self.tree.insert(parent_id, 'end',
                                             text=f"📁 {folder_name}",
                                             values=['Folder', 'Directory', f"{file_count} files", 'N/A'],
                                             tags=['folder'])
            
            # Recursively insert subfolder contents
            self._insert_folder_nodes(folder_data, folder_item_id)
    
    def _count_files_recursive(self, folder_data):
        """Count files recursively in folder structure (unchanged)"""
        count = len(folder_data.get('files', []))
        
        for subfolder_data in folder_data.get('folders', {}).values():
            count += self._count_files_recursive(subfolder_data)
        
        return count
    
    def _get_file_status(self, file_result):
        """Get status for matched file (unchanged)"""
        stats = file_result.get('statistics', {})
        
        total_changes = (stats.get('added_count', 0) + 
                        stats.get('deleted_count', 0) + 
                        stats.get('modified_count', 0))
        
        if total_changes > 0:
            return 'Modified'
        else:
            return 'Unchanged'
    
    def _get_file_changes_summary(self, file_result):
        """Get changes summary for matched file (unchanged)"""
        stats = file_result.get('statistics', {})
        
        added = stats.get('added_count', 0)
        deleted = stats.get('deleted_count', 0)
        modified = stats.get('modified_count', 0)
        
        changes = []
        if added > 0:
            changes.append(f"+{added}")
        if deleted > 0:
            changes.append(f"-{deleted}")
        if modified > 0:
            changes.append(f"~{modified}")
        
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
        """NEW: Export individual file statistics to CSV"""
        try:
            filename = filedialog.asksaveasfilename(
                title="Export Individual File Statistics",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile="individual_file_statistics.csv"
            )
            
            if not filename:
                return
            
            import csv
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                writer.writerow([
                    'Category', 'File_Path', 'Match_Type', 'Similarity', 
                    'Requirements_Original', 'Requirements_Modified', 
                    'Added_Reqs', 'Deleted_Reqs', 'Modified_Reqs', 'Unchanged_Reqs',
                    'Change_Percentage', 'File_Size_Original_MB', 'File_Size_Modified_MB',
                    'Parsing_Success', 'Error_Details'
                ])
                
                # Matched files
                for file_path, file_data in self.individual_stats.get('matched_files', {}).items():
                    stats = file_data.get('comparison_stats', {})
                    
                    writer.writerow([
                        'Matched',
                        file_path,
                        file_data.get('match_type', ''),
                        f"{file_data.get('similarity', 0):.3f}",
                        stats.get('total_file1', 0),
                        stats.get('total_file2', 0),
                        stats.get('added_count', 0),
                        stats.get('deleted_count', 0),
                        stats.get('modified_count', 0),
                        stats.get('unchanged_count', 0),
                        f"{stats.get('change_percentage', 0):.2f}",
                        f"{file_data.get('file1_info', {}).get('size', 0) / (1024*1024):.2f}",
                        f"{file_data.get('file2_info', {}).get('size', 0) / (1024*1024):.2f}",
                        'True',
                        ''
                    ])
                
                # Added files
                for file_path, file_data in self.individual_stats.get('added_files', {}).items():
                    writer.writerow([
                        'Added',
                        file_path,
                        'N/A',
                        'N/A',
                        0,
                        file_data.get('requirement_count', 0),
                        file_data.get('requirement_count', 0),
                        0,
                        0,
                        0,
                        'N/A',
                        'N/A',
                        f"{file_data.get('file_size_mb', 0):.2f}",
                        str(file_data.get('parsing_success', False)),
                        file_data.get('error', '')
                    ])
                
                # Deleted files
                for file_path, file_data in self.individual_stats.get('deleted_files', {}).items():
                    writer.writerow([
                        'Deleted',
                        file_path,
                        'N/A',
                        'N/A',
                        file_data.get('requirement_count', 0),
                        0,
                        0,
                        file_data.get('requirement_count', 0),
                        0,
                        0,
                        'N/A',
                        f"{file_data.get('file_size_mb', 0):.2f}",
                        'N/A',
                        str(file_data.get('parsing_success', False)),
                        file_data.get('error', '')
                    ])
            
            messagebox.showinfo("Export Complete", 
                               f"Individual file statistics exported to:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Export Error", 
                               f"Failed to export individual statistics:\n{str(e)}")
    
    # Remaining original methods (unchanged)
    def _on_tree_double_click(self, event):
        """Handle double-click on tree item (unchanged)"""
        item_id = self.tree.selection()[0] if self.tree.selection() else None
        if not item_id:
            return
        
        tags = self.tree.item(item_id, 'tags')
        
        if 'matched_file' in tags:
            # Show detailed file comparison - get data from our storage dict
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
        """Show detailed comparison for a file (unchanged)"""
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
        """Handle tree node expansion (unchanged)"""
        item_id = self.tree.selection()[0] if self.tree.selection() else None
        if item_id:
            self.expanded_nodes.add(item_id)
    
    def _on_tree_collapse(self, event):
        """Handle tree node collapse (unchanged)"""
        item_id = self.tree.selection()[0] if self.tree.selection() else None
        if item_id and item_id in self.expanded_nodes:
            self.expanded_nodes.remove(item_id)
    
    def _expand_all(self):
        """Expand all tree nodes (unchanged)"""
        def expand_recursive(item_id):
            self.tree.item(item_id, open=True)
            for child_id in self.tree.get_children(item_id):
                expand_recursive(child_id)
        
        for root_item in self.tree.get_children():
            expand_recursive(root_item)
    
    def _collapse_all(self):
        """Collapse all tree nodes (unchanged)"""
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
        """Handle window closing (unchanged)"""
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
    print("Enhanced Folder Comparison Results GUI - Native Version")
    print("New features:")
    print("- Individual file statistics display")
    print("- Enhanced export capabilities")
    print("- Analysis insights and recommendations")
    print("- Backward compatibility maintained")