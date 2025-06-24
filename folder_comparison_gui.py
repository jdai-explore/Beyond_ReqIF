#!/usr/bin/env python3
"""
Folder Comparison Results GUI - Native Version
Pure tkinter hierarchical display for folder comparison results
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import os
from typing import Dict, List, Any, Optional
from comparison_gui import ComparisonResultsGUI


class FolderComparisonResultsGUI:
    """
    Folder Comparison Results GUI - Native Version with hierarchical display
    """
    
    def __init__(self, parent: tk.Widget, results: Dict[str, Any]):
        self.parent = parent
        self.results = results
        
        # Create independent window
        self.window = tk.Toplevel(parent)
        self.window.title("Folder Comparison Results")
        self.window.geometry("1500x900")
        
        # Ensure window independence
        self.window.transient(parent)
        self.window.focus_set()
        
        # State tracking
        self.expanded_nodes = set()
        self.file_comparison_windows = {}
        
        # Setup GUI
        self.setup_gui()
        
        # Handle window closing
        self.window.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def setup_gui(self):
        """Setup native GUI with hierarchical display"""
        # Create main container
        self.main_frame = tk.Frame(self.window, padx=20, pady=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create sections
        self._create_header_section()
        self._create_summary_section()
        self._create_hierarchical_results_section()
        self._create_controls_section()
    
    def _create_header_section(self):
        """Create header with folder paths"""
        header_frame = tk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Title
        title_label = tk.Label(header_frame, text="Folder Comparison Results", 
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
    
    def _create_summary_section(self):
        """Create summary statistics section"""
        summary_frame = tk.LabelFrame(self.main_frame, text="Summary Statistics", 
                                     font=('Arial', 12, 'bold'), padx=15, pady=15)
        summary_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Get statistics
        folder_stats = self.results.get('folder_statistics', {})
        req_stats = self.results.get('aggregated_statistics', {})
        
        # Create summary sections
        self._create_folder_summary(summary_frame, folder_stats)
        self._create_requirements_summary(summary_frame, req_stats)
    
    def _create_folder_summary(self, parent, folder_stats):
        """Create folder-level summary"""
        folder_frame = tk.LabelFrame(parent, text="File Changes", font=('Arial', 11, 'bold'))
        folder_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        
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
        req_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(20, 0))
        
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
    
    def _create_hierarchical_results_section(self):
        """Create hierarchical results display with tree view"""
        results_frame = tk.LabelFrame(self.main_frame, text="Detailed Results", 
                                     font=('Arial', 12, 'bold'), padx=10, pady=10)
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create tree view frame
        tree_frame = tk.Frame(results_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Instructions
        instruction_label = tk.Label(tree_frame, 
                                    text="📁 Expand folders to see files • 📄 Double-click files to view detailed comparison",
                                    font=('Arial', 10), fg='darkblue')
        instruction_label.pack(anchor=tk.W, pady=(0, 10))
        
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
    
    def _populate_hierarchical_tree(self):
        """Populate the hierarchical tree view"""
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
        """Recursively insert folder nodes into tree"""
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
            
            # Store file data for drill-down
            self.tree.set(item_id, 'file_data', file_node)
        
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
        """Count files recursively in folder structure"""
        count = len(folder_data.get('files', []))
        
        for subfolder_data in folder_data.get('folders', {}).values():
            count += self._count_files_recursive(subfolder_data)
        
        return count
    
    def _get_file_status(self, file_result):
        """Get status for matched file"""
        stats = file_result.get('statistics', {})
        
        total_changes = (stats.get('added_count', 0) + 
                        stats.get('deleted_count', 0) + 
                        stats.get('modified_count', 0))
        
        if total_changes > 0:
            return 'Modified'
        else:
            return 'Unchanged'
    
    def _get_file_changes_summary(self, file_result):
        """Get changes summary for matched file"""
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
        """Create control buttons"""
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
        
        # Export button
        tk.Button(left_buttons, text="📄 Export Summary", command=self._export_summary,
                 font=('Arial', 11, 'bold'), relief='raised', bd=2,
                 padx=20, pady=6, cursor='hand2', bg='lightblue').pack(side=tk.LEFT, padx=(0, 15))
        
        # Close button
        tk.Button(controls_frame, text="✖️ Close", command=self._on_closing,
                 font=('Arial', 11), relief='raised', bd=2,
                 padx=20, pady=6, cursor='hand2').pack(side=tk.RIGHT)
    
    def _on_tree_double_click(self, event):
        """Handle double-click on tree item"""
        item_id = self.tree.selection()[0] if self.tree.selection() else None
        if not item_id:
            return
        
        tags = self.tree.item(item_id, 'tags')
        
        if 'matched_file' in tags:
            # Show detailed file comparison
            file_data = self.tree.set(item_id, 'file_data')
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
        """Export folder comparison summary"""
        try:
            filename = filedialog.asksaveasfilename(
                title="Export Folder Comparison Summary",
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                initialfile="folder_comparison_summary.txt"
            )
            
            if not filename:
                return
            
            # Generate summary using folder_comparator export method
            from folder_comparator import FolderComparator
            comparator = FolderComparator()
            summary = comparator.export_folder_summary(self.results)
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(summary)
            
            messagebox.showinfo("Export Complete", 
                               f"Folder comparison summary exported to:\n{filename}")
            
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
    print("Folder Comparison Results GUI - Native Version")
    print("Provides hierarchical display of folder comparison results")
    
    # Example test data structure
    test_results = {
        'folder1_path': '/path/to/original/folder',
        'folder2_path': '/path/to/modified/folder',
        'folder_statistics': {
            'files_added': 2,
            'files_deleted': 1,
            'files_with_changes': 3,
            'files_unchanged': 5,
            'comparison_errors': 0
        },
        'aggregated_statistics': {
            'total_requirements_added': 15,
            'total_requirements_deleted': 8,
            'total_requirements_modified': 22,
            'total_requirements_unchanged': 150,
            'overall_change_percentage': 23.1
        },
        'file_results': {
            'matched_files': [],
            'added_files': [],
            'deleted_files': []
        }
    }
    
    print("Folder Comparison GUI ready for integration!")