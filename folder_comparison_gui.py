# folder_comparison_gui.py - Updated for new comparison structure
"""
Folder Comparison GUI - Updated for new comparison categories
Now handles: Added, Deleted, Content Changed, Structural Changes, Unchanged
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, List, Tuple, Optional, Any
import threading
from datetime import datetime
import json

from reqif_comparator import compare_requirements
from folder_comparator import FolderComparator


class FolderComparisonGUI:
    """Main GUI for folder comparison with updated statistics and visualization"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("ReqIF Folder Comparison Tool - Updated")
        self.root.geometry("1400x900")
        
        # Data storage
        self.folder_results: Dict[str, Any] = {}
        self.current_comparison = None
        self.folder_comparator = FolderComparator()
        
        # UI state
        self.is_comparing = False
        self.selected_file = None
        
        self.setup_ui()
        self.setup_styles()
        
    def setup_styles(self):
        """Setup custom styles for the updated interface"""
        style = ttk.Style()
        
        # Define colors for new change types
        self.change_colors = {
            'added': '#2E7D32',          # Green for added
            'deleted': '#C62828',        # Red for deleted  
            'content_modified': '#FF8F00', # Orange for content changes
            'structural_only': '#1976D2', # Blue for structural changes
            'unchanged': '#424242'        # Gray for unchanged
        }
        
        # Configure treeview tags
        style.configure("Added.Treeview", foreground=self.change_colors['added'])
        style.configure("Deleted.Treeview", foreground=self.change_colors['deleted'])
        style.configure("ContentModified.Treeview", foreground=self.change_colors['content_modified'])
        style.configure("StructuralOnly.Treeview", foreground=self.change_colors['structural_only'])
        style.configure("Unchanged.Treeview", foreground=self.change_colors['unchanged'])
        
    def setup_ui(self):
        """Setup the main UI with updated layout"""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Setup components
        self.setup_folder_selection(main_frame)
        self.setup_progress_section(main_frame)
        self.setup_results_section(main_frame)
        self.setup_status_bar()
        
    def setup_folder_selection(self, parent):
        """Setup folder selection section"""
        selection_frame = ttk.LabelFrame(parent, text="Folder Selection", padding=10)
        selection_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Folder 1
        ttk.Label(selection_frame, text="Original Folder:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.folder1_var = tk.StringVar()
        ttk.Entry(selection_frame, textvariable=self.folder1_var, width=60).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(selection_frame, text="Browse", 
                  command=lambda: self.browse_folder(self.folder1_var)).grid(row=0, column=2)
        
        # Folder 2
        ttk.Label(selection_frame, text="Modified Folder:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.folder2_var = tk.StringVar()
        ttk.Entry(selection_frame, textvariable=self.folder2_var, width=60).grid(row=1, column=1, padx=(0, 10), pady=(10, 0))
        ttk.Button(selection_frame, text="Browse", 
                  command=lambda: self.browse_folder(self.folder2_var)).grid(row=1, column=2, pady=(10, 0))
        
        # Control buttons
        button_frame = ttk.Frame(selection_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=(20, 0))
        
        self.compare_btn = ttk.Button(button_frame, text="Start Comparison", 
                                    command=self.start_comparison, style="Accent.TButton")
        self.compare_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_btn = ttk.Button(button_frame, text="Stop", 
                                 command=self.stop_comparison, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="Export Results", 
                  command=self.export_results).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="Clear Results", 
                  command=self.clear_results).pack(side=tk.LEFT)
        
    def setup_progress_section(self, parent):
        """Setup progress tracking section"""
        progress_frame = ttk.LabelFrame(parent, text="Progress", padding=10)
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                          length=400, mode='determinate')
        self.progress_bar.pack(pady=(0, 10))
        
        # Progress labels
        label_frame = ttk.Frame(progress_frame)
        label_frame.pack(fill=tk.X)
        
        self.current_file_label = ttk.Label(label_frame, text="Ready to compare")
        self.current_file_label.pack(side=tk.LEFT)
        
        self.progress_label = ttk.Label(label_frame, text="")
        self.progress_label.pack(side=tk.RIGHT)
        
    def setup_results_section(self, parent):
        """Setup results display section with updated layout"""
        results_frame = ttk.LabelFrame(parent, text="Comparison Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create paned window for resizable layout
        paned = ttk.PanedWindow(results_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - File tree and statistics
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)
        
        # Updated statistics panel
        self.setup_statistics_panel(left_frame)
        
        # File tree
        tree_frame = ttk.LabelFrame(left_frame, text="Files with Changes", padding=5)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # File tree with scrollbar
        tree_container = ttk.Frame(tree_frame)
        tree_container.pack(fill=tk.BOTH, expand=True)
        
        self.file_tree = ttk.Treeview(tree_container, columns=('status', 'changes'), 
                                     show='tree headings', height=15)
        self.file_tree.heading('#0', text='File Path')
        self.file_tree.heading('status', text='Status')
        self.file_tree.heading('changes', text='Changes')
        
        self.file_tree.column('#0', width=300)
        self.file_tree.column('status', width=120)
        self.file_tree.column('changes', width=100)
        
        # Scrollbars for tree
        tree_scroll_y = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.file_tree.yview)
        tree_scroll_x = ttk.Scrollbar(tree_container, orient=tk.HORIZONTAL, command=self.file_tree.xview)
        self.file_tree.configure(yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
        
        self.file_tree.grid(row=0, column=0, sticky='nsew')
        tree_scroll_y.grid(row=0, column=1, sticky='ns')
        tree_scroll_x.grid(row=1, column=0, sticky='ew')
        
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)
        
        # Bind tree selection
        self.file_tree.bind('<<TreeviewSelect>>', self.on_file_select)
        self.file_tree.bind('<Double-1>', self.on_file_double_click)
        
        # Right panel - Detailed comparison view
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=2)
        
        detail_label = ttk.Label(right_frame, text="Detailed Comparison", font=('TkDefaultFont', 10, 'bold'))
        detail_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Updated notebook with new tabs
        self.detail_notebook = ttk.Notebook(right_frame)
        self.detail_notebook.pack(fill=tk.BOTH, expand=True)
        
        self.setup_detail_tabs()
        
    def setup_statistics_panel(self, parent):
        """Setup updated statistics panel"""
        stats_frame = ttk.LabelFrame(parent, text="Summary Statistics", padding=10)
        stats_frame.pack(fill=tk.X)
        
        # Create grid for statistics
        self.stats_labels = {}
        
        # Row 0: File counts
        ttk.Label(stats_frame, text="Total Files:", font=('TkDefaultFont', 9, 'bold')).grid(row=0, column=0, sticky=tk.W)
        self.stats_labels['total_files'] = ttk.Label(stats_frame, text="0")
        self.stats_labels['total_files'].grid(row=0, column=1, sticky=tk.W, padx=(10, 20))
        
        ttk.Label(stats_frame, text="Files with Changes:", font=('TkDefaultFont', 9, 'bold')).grid(row=0, column=2, sticky=tk.W)
        self.stats_labels['files_changed'] = ttk.Label(stats_frame, text="0")
        self.stats_labels['files_changed'].grid(row=0, column=3, sticky=tk.W, padx=(10, 0))
        
        # Row 1: Requirement changes (Updated categories)
        ttk.Label(stats_frame, text="Requirements Added:", 
                 foreground=self.change_colors['added']).grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        self.stats_labels['added'] = ttk.Label(stats_frame, text="0", 
                                              foreground=self.change_colors['added'])
        self.stats_labels['added'].grid(row=1, column=1, sticky=tk.W, padx=(10, 20), pady=(10, 0))
        
        ttk.Label(stats_frame, text="Requirements Deleted:", 
                 foreground=self.change_colors['deleted']).grid(row=1, column=2, sticky=tk.W, pady=(10, 0))
        self.stats_labels['deleted'] = ttk.Label(stats_frame, text="0", 
                                                foreground=self.change_colors['deleted'])
        self.stats_labels['deleted'].grid(row=1, column=3, sticky=tk.W, padx=(10, 0), pady=(10, 0))
        
        # Row 2: Content and structural changes
        ttk.Label(stats_frame, text="Content Modified:", 
                 foreground=self.change_colors['content_modified']).grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
        self.stats_labels['content_modified'] = ttk.Label(stats_frame, text="0", 
                                                         foreground=self.change_colors['content_modified'])
        self.stats_labels['content_modified'].grid(row=2, column=1, sticky=tk.W, padx=(10, 20), pady=(5, 0))
        
        ttk.Label(stats_frame, text="Structural Changes:", 
                 foreground=self.change_colors['structural_only']).grid(row=2, column=2, sticky=tk.W, pady=(5, 0))
        self.stats_labels['structural_only'] = ttk.Label(stats_frame, text="0", 
                                                        foreground=self.change_colors['structural_only'])
        self.stats_labels['structural_only'].grid(row=2, column=3, sticky=tk.W, padx=(10, 0), pady=(5, 0))
        
        # Row 3: Unchanged
        ttk.Label(stats_frame, text="Unchanged:", 
                 foreground=self.change_colors['unchanged']).grid(row=3, column=0, sticky=tk.W, pady=(5, 0))
        self.stats_labels['unchanged'] = ttk.Label(stats_frame, text="0", 
                                                  foreground=self.change_colors['unchanged'])
        self.stats_labels['unchanged'].grid(row=3, column=1, sticky=tk.W, padx=(10, 20), pady=(5, 0))
        
        # Configure column weights
        for i in range(4):
            stats_frame.grid_columnconfigure(i, weight=1)
            
    def setup_detail_tabs(self):
        """Setup updated detail tabs for new comparison structure"""
        # Added Requirements tab
        self.added_frame = ttk.Frame(self.detail_notebook)
        self.detail_notebook.add(self.added_frame, text="Added Requirements")
        self.setup_change_tab(self.added_frame, "added")
        
        # Deleted Requirements tab  
        self.deleted_frame = ttk.Frame(self.detail_notebook)
        self.detail_notebook.add(self.deleted_frame, text="Deleted Requirements")
        self.setup_change_tab(self.deleted_frame, "deleted")
        
        # Content Changes tab (NEW - replaces old Modified tab)
        self.content_frame = ttk.Frame(self.detail_notebook)
        self.detail_notebook.add(self.content_frame, text="Content Changes")
        self.setup_change_tab(self.content_frame, "content_modified")
        
        # Structural Changes tab (NEW)
        self.structural_frame = ttk.Frame(self.detail_notebook)
        self.detail_notebook.add(self.structural_frame, text="Structural Changes")
        self.setup_change_tab(self.structural_frame, "structural_only")
        
        # Unchanged Requirements tab
        self.unchanged_frame = ttk.Frame(self.detail_notebook)
        self.detail_notebook.add(self.unchanged_frame, text="Unchanged")
        self.setup_change_tab(self.unchanged_frame, "unchanged")
        
        # Summary tab with detailed statistics
        self.summary_frame = ttk.Frame(self.detail_notebook)
        self.detail_notebook.add(self.summary_frame, text="Summary")
        self.setup_summary_tab()
        
    def setup_change_tab(self, parent, change_type):
        """Setup individual change type tab"""
        # Create text widget with scrollbar
        text_frame = ttk.Frame(parent)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget = tk.Text(text_frame, wrap=tk.WORD, font=('Consolas', 10))
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Store reference for later updates
        setattr(self, f"{change_type}_text", text_widget)
        
    def setup_summary_tab(self):
        """Setup summary tab with detailed statistics"""
        summary_container = ttk.Frame(self.summary_frame)
        summary_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Summary text area
        self.summary_text = tk.Text(summary_container, wrap=tk.WORD, font=('Consolas', 10), state=tk.DISABLED)
        summary_scroll = ttk.Scrollbar(summary_container, orient=tk.VERTICAL, command=self.summary_text.yview)
        self.summary_text.configure(yscrollcommand=summary_scroll.set)
        
        self.summary_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        summary_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
    def setup_status_bar(self):
        """Setup status bar"""
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def browse_folder(self, var):
        """Browse for folder selection"""
        folder = filedialog.askdirectory()
        if folder:
            var.set(folder)
            
    def start_comparison(self):
        """Start folder comparison with updated progress tracking"""
        folder1 = self.folder1_var.get().strip()
        folder2 = self.folder2_var.get().strip()
        
        if not folder1 or not folder2:
            messagebox.showerror("Error", "Please select both folders")
            return
            
        if not os.path.exists(folder1) or not os.path.exists(folder2):
            messagebox.showerror("Error", "One or both folders do not exist")
            return
            
        # Clear previous results
        self.clear_results()
        
        # Update UI state
        self.is_comparing = True
        self.compare_btn.configure(state=tk.DISABLED)
        self.stop_btn.configure(state=tk.NORMAL)
        
        # Start comparison in separate thread
        self.comparison_thread = threading.Thread(
            target=self.run_comparison,
            args=(folder1, folder2),
            daemon=True
        )
        self.comparison_thread.start()
        
    def run_comparison(self, folder1: str, folder2: str):
        """Run comparison in background thread"""
        try:
            self.update_status("Starting comparison...")
            
            def progress_callback(current: int, total: int, filename: str):
                if self.is_comparing:  # Check if we should continue
                    progress = (current / total) * 100 if total > 0 else 0
                    self.root.after(0, self.update_progress, progress, f"Processing: {filename}", current, total)
            
            # Run comparison
            self.folder_results = self.folder_comparator.compare_folders(
                folder1, folder2, progress_callback
            )
            
            if self.is_comparing:  # Only update if not stopped
                self.root.after(0, self.comparison_complete)
                
        except Exception as e:
            if self.is_comparing:
                self.root.after(0, self.comparison_error, str(e))
                
    def update_progress(self, progress: float, message: str, current: int, total: int):
        """Update progress display"""
        self.progress_var.set(progress)
        self.current_file_label.configure(text=message)
        self.progress_label.configure(text=f"{current}/{total} files")
        self.root.update_idletasks()
        
    def comparison_complete(self):
        """Handle comparison completion with updated statistics"""
        self.is_comparing = False
        self.compare_btn.configure(state=tk.NORMAL)
        self.stop_btn.configure(state=tk.DISABLED)
        
        self.update_status("Comparison completed")
        self.current_file_label.configure(text="Comparison completed")
        self.progress_var.set(100)
        
        # Update all displays
        self.update_statistics()
        self.update_file_tree()
        self.update_summary()
        
        # Show completion message
        stats = self.folder_results.get('statistics', {})
        total_changes = (stats.get('total_added', 0) + stats.get('total_deleted', 0) + 
                        stats.get('total_content_modified', 0) + stats.get('total_structural_only', 0))
        
        messagebox.showinfo(
            "Comparison Complete", 
            f"Comparison completed successfully!\n\n"
            f"Files processed: {stats.get('total_files', 0)}\n"
            f"Files with changes: {stats.get('files_with_changes', 0)}\n"
            f"Total requirement changes: {total_changes}"
        )
        
    def comparison_error(self, error_msg: str):
        """Handle comparison error"""
        self.is_comparing = False
        self.compare_btn.configure(state=tk.NORMAL)
        self.stop_btn.configure(state=tk.DISABLED)
        
        self.update_status(f"Comparison failed: {error_msg}")
        messagebox.showerror("Comparison Error", f"An error occurred during comparison:\n\n{error_msg}")
        
    def stop_comparison(self):
        """Stop ongoing comparison"""
        self.is_comparing = False
        self.compare_btn.configure(state=tk.NORMAL)
        self.stop_btn.configure(state=tk.DISABLED)
        self.update_status("Comparison stopped by user")
        
    def update_statistics(self):
        """Update statistics display with new categories"""
        if not self.folder_results:
            return
            
        stats = self.folder_results.get('statistics', {})
        
        # Update basic file statistics
        self.stats_labels['total_files'].configure(text=str(stats.get('total_files', 0)))
        self.stats_labels['files_changed'].configure(text=str(stats.get('files_with_changes', 0)))
        
        # Update requirement change statistics (new categories)
        self.stats_labels['added'].configure(text=str(stats.get('total_added', 0)))
        self.stats_labels['deleted'].configure(text=str(stats.get('total_deleted', 0)))
        self.stats_labels['content_modified'].configure(text=str(stats.get('total_content_modified', 0)))
        self.stats_labels['structural_only'].configure(text=str(stats.get('total_structural_only', 0)))
        self.stats_labels['unchanged'].configure(text=str(stats.get('total_unchanged', 0)))
        
    def update_file_tree(self):
        """Update file tree with clearer change indicators"""
        # Clear existing items
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
            
        if not self.folder_results:
            return
            
        # Add files with changes
        for file_path, file_result in self.folder_results.get('file_results', {}).items():
            # Determine primary change type for display
            changes = file_result.get('comparison', {})
            
            # Count different types of changes
            added_count = len(changes.get('added', []))
            deleted_count = len(changes.get('deleted', []))
            content_count = len(changes.get('content_modified', []))
            structural_count = len(changes.get('structural_only', []))
            
            total_changes = added_count + deleted_count + content_count + structural_count
            
            if total_changes == 0:
                continue  # Skip files with no changes
                
            # Determine status and change summary
            if added_count > 0 and deleted_count == 0 and content_count == 0 and structural_count == 0:
                status = "Added Only"
                tag = "added"
            elif deleted_count > 0 and added_count == 0 and content_count == 0 and structural_count == 0:
                status = "Deleted Only"
                tag = "deleted"
            elif content_count > 0 and structural_count == 0:
                status = "Content Changes"
                tag = "content_modified"
            elif structural_count > 0 and content_count == 0:
                status = "Structural Only"
                tag = "structural_only"
            else:
                status = "Mixed Changes"
                tag = "content_modified"  # Default to content modified color
                
            # Create change summary
            change_parts = []
            if added_count > 0:
                change_parts.append(f"+{added_count}")
            if deleted_count > 0:
                change_parts.append(f"-{deleted_count}")
            if content_count > 0:
                change_parts.append(f"~{content_count}")
            if structural_count > 0:
                change_parts.append(f"#{structural_count}")
                
            change_summary = " ".join(change_parts)
            
            # Insert into tree
            item_id = self.file_tree.insert('', 'end', text=file_path, 
                                          values=(status, change_summary),
                                          tags=(tag,))
            
            # Configure tag colors
            self.file_tree.tag_configure(tag, foreground=self.change_colors[tag])
            
    def update_summary(self):
        """Update summary tab with detailed analysis"""
        if not self.folder_results:
            return
            
        self.summary_text.configure(state=tk.NORMAL)
        self.summary_text.delete(1.0, tk.END)
        
        stats = self.folder_results.get('statistics', {})
        
        # Generate detailed summary
        summary_lines = [
            "FOLDER COMPARISON SUMMARY",
            "=" * 50,
            "",
            f"Comparison completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Original folder: {self.folder1_var.get()}",
            f"Modified folder: {self.folder2_var.get()}",
            "",
            "FILE STATISTICS:",
            f"  Total files processed: {stats.get('total_files', 0)}",
            f"  Files with changes: {stats.get('files_with_changes', 0)}",
            f"  Files unchanged: {stats.get('total_files', 0) - stats.get('files_with_changes', 0)}",
            "",
            "REQUIREMENT CHANGES:",
            f"  Added requirements: {stats.get('total_added', 0)}",
            f"  Deleted requirements: {stats.get('total_deleted', 0)}",
            f"  Content modified: {stats.get('total_content_modified', 0)}",
            f"  Structural changes only: {stats.get('total_structural_only', 0)}",
            f"  Unchanged requirements: {stats.get('total_unchanged', 0)}",
            "",
            "CHANGE ANALYSIS:",
            f"  Files with only additions: {stats.get('files_added_only', 0)}",
            f"  Files with only deletions: {stats.get('files_deleted_only', 0)}",
            f"  Files with content changes: {stats.get('files_content_modified', 0)}",
            f"  Files with structural changes: {stats.get('files_structural_only', 0)}",
            f"  Files with mixed changes: {stats.get('files_mixed_changes', 0)}",
        ]
        
        # Add attribute analysis if available
        if 'attribute_analysis' in stats:
            attr_analysis = stats['attribute_analysis']
            summary_lines.extend([
                "",
                "ATTRIBUTE ANALYSIS:",
                f"  Commonly added attributes: {', '.join(attr_analysis.get('added_attributes', [])) or 'None'}",
                f"  Commonly removed attributes: {', '.join(attr_analysis.get('removed_attributes', [])) or 'None'}",
            ])
        
        summary_text = "\n".join(summary_lines)
        self.summary_text.insert(1.0, summary_text)
        self.summary_text.configure(state=tk.DISABLED)
        
    def on_file_select(self, event):
        """Handle file selection in tree"""
        selection = self.file_tree.selection()
        if not selection:
            return
            
        item_id = selection[0]
        file_path = self.file_tree.item(item_id, 'text')
        
        self.selected_file = file_path
        self.update_detail_view(file_path)
        
    def on_file_double_click(self, event):
        """Handle double-click on file tree item"""
        selection = self.file_tree.selection()
        if not selection:
            return
            
        item_id = selection[0]
        file_path = self.file_tree.item(item_id, 'text')
        
        # Show detailed comparison in popup window
        self.show_detailed_comparison(file_path)
        
    def update_detail_view(self, file_path: str):
        """Update detail view for selected file with new categories"""
        if not self.folder_results or file_path not in self.folder_results.get('file_results', {}):
            return
            
        file_result = self.folder_results['file_results'][file_path]
        comparison = file_result.get('comparison', {})
        
        # Update each tab with appropriate content
        self.update_tab_content('added', comparison.get('added', []))
        self.update_tab_content('deleted', comparison.get('deleted', []))
        self.update_tab_content('content_modified', comparison.get('content_modified', []))
        self.update_tab_content('structural_only', comparison.get('structural_only', []))
        self.update_tab_content('unchanged', comparison.get('unchanged', []))
        
    def update_tab_content(self, tab_type: str, requirements: List[Dict]):
        """Update content for specific tab type"""
        text_widget = getattr(self, f"{tab_type}_text", None)
        if not text_widget:
            return
            
        text_widget.delete(1.0, tk.END)
        
        if not requirements:
            text_widget.insert(1.0, f"No {tab_type.replace('_', ' ')} requirements found.")
            return
            
        # Format content based on tab type
        if tab_type == 'content_modified':
            content = self.format_content_modified_requirements(requirements)
        elif tab_type == 'structural_only':
            content = self.format_structural_only_requirements(requirements)
        else:
            content = self.format_basic_requirements(requirements, tab_type)
            
        text_widget.insert(1.0, content)
        
    def format_content_modified_requirements(self, requirements: List[Dict]) -> str:
        """Format content modified requirements showing actual changes"""
        lines = [f"Content Modified Requirements ({len(requirements)} total):", "=" * 60, ""]
        
        for i, req in enumerate(requirements, 1):
            lines.append(f"{i}. Requirement ID: {req.get('identifier', 'Unknown')}")
            
            # Show what changed in content
            if 'changes' in req:
                changes = req['changes']
                lines.append("   Content Changes:")
                for field, change_info in changes.items():
                    if isinstance(change_info, dict) and 'old' in change_info and 'new' in change_info:
                        lines.append(f"     {field}:")
                        lines.append(f"       Old: {change_info['old']}")
                        lines.append(f"       New: {change_info['new']}")
                    else:
                        lines.append(f"     {field}: {change_info}")
            
            # Show common attributes (unchanged)
            if 'common_attributes' in req:
                common_attrs = req['common_attributes']
                if common_attrs:
                    lines.append("   Common attributes: " + ", ".join(common_attrs.keys()))
            
            lines.append("")  # Empty line between requirements
            
        return "\n".join(lines)
        
    def format_structural_only_requirements(self, requirements: List[Dict]) -> str:
        """Format structural-only requirements showing attribute differences"""
        lines = [f"Structural Changes Only ({len(requirements)} total):", "=" * 60, ""]
        
        for i, req in enumerate(requirements, 1):
            lines.append(f"{i}. Requirement ID: {req.get('identifier', 'Unknown')}")
            
            # Show structural differences
            if 'structural_changes' in req:
                struct_changes = req['structural_changes']
                
                if 'added_attributes' in struct_changes:
                    added_attrs = struct_changes['added_attributes']
                    if added_attrs:
                        lines.append("   Added attributes:")
                        for attr, value in added_attrs.items():
                            lines.append(f"     + {attr}: {value}")
                
                if 'removed_attributes' in struct_changes:
                    removed_attrs = struct_changes['removed_attributes']
                    if removed_attrs:
                        lines.append("   Removed attributes:")
                        for attr, value in removed_attrs.items():
                            lines.append(f"     - {attr}: {value}")
            
            # Show that content is identical
            lines.append("   Content: Identical in both versions")
            lines.append("")  # Empty line between requirements
            
        return "\n".join(lines)
        
    def format_basic_requirements(self, requirements: List[Dict], tab_type: str) -> str:
        """Format basic requirements for added/deleted/unchanged tabs"""
        title_map = {
            'added': 'Added Requirements',
            'deleted': 'Deleted Requirements', 
            'unchanged': 'Unchanged Requirements'
        }
        
        title = title_map.get(tab_type, tab_type.replace('_', ' ').title())
        lines = [f"{title} ({len(requirements)} total):", "=" * 60, ""]
        
        for i, req in enumerate(requirements, 1):
            lines.append(f"{i}. Requirement ID: {req.get('identifier', 'Unknown')}")
            
            # Show basic requirement info
            if 'the_value' in req:
                value = req['the_value']
                if len(value) > 100:
                    value = value[:100] + "..."
                lines.append(f"   Content: {value}")
            
            # Show key attributes
            key_attrs = ['req_type', 'last_change', 'spec_hierarchy']
            for attr in key_attrs:
                if attr in req:
                    lines.append(f"   {attr.replace('_', ' ').title()}: {req[attr]}")
            
            lines.append("")  # Empty line between requirements
            
        return "\n".join(lines)
        
    def show_detailed_comparison(self, file_path: str):
        """Show detailed comparison in popup window"""
        if not self.folder_results or file_path not in self.folder_results.get('file_results', {}):
            return
            
        # Create popup window
        popup = tk.Toplevel(self.root)
        popup.title(f"Detailed Comparison - {os.path.basename(file_path)}")
        popup.geometry("900x700")
        
        # Create notebook for detailed view
        notebook = ttk.Notebook(popup)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        file_result = self.folder_results['file_results'][file_path]
        comparison = file_result.get('comparison', {})
        
        # Add tabs for each change type that has content
        for change_type in ['added', 'deleted', 'content_modified', 'structural_only', 'unchanged']:
            requirements = comparison.get(change_type, [])
            if requirements:  # Only add tab if there are requirements
                tab_frame = ttk.Frame(notebook)
                notebook.add(tab_frame, text=f"{change_type.replace('_', ' ').title()} ({len(requirements)})")
                
                # Add text widget with scrollbar
                text_frame = ttk.Frame(tab_frame)
                text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                
                text_widget = tk.Text(text_frame, wrap=tk.WORD, font=('Consolas', 9))
                scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
                text_widget.configure(yscrollcommand=scrollbar.set)
                
                text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                
                # Format and insert content
                if change_type == 'content_modified':
                    content = self.format_content_modified_requirements(requirements)
                elif change_type == 'structural_only':
                    content = self.format_structural_only_requirements(requirements)
                else:
                    content = self.format_basic_requirements(requirements, change_type)
                    
                text_widget.insert(1.0, content)
                text_widget.configure(state=tk.DISABLED)
        
        # Add close button
        close_btn = ttk.Button(popup, text="Close", command=popup.destroy)
        close_btn.pack(pady=10)
        
    def export_results(self):
        """Export comparison results with updated format"""
        if not self.folder_results:
            messagebox.showwarning("Export", "No comparison results to export")
            return
            
        # Ask user for export file
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[
                ("JSON files", "*.json"),
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ],
            title="Export Comparison Results"
        )
        
        if not filename:
            return
            
        try:
            if filename.endswith('.txt'):
                self.export_as_text(filename)
            else:
                self.export_as_json(filename)
                
            messagebox.showinfo("Export", f"Results exported successfully to:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export results:\n{str(e)}")
            
    def export_as_json(self, filename: str):
        """Export results as JSON"""
        # Create export data with metadata
        export_data = {
            'metadata': {
                'export_time': datetime.now().isoformat(),
                'original_folder': self.folder1_var.get(),
                'modified_folder': self.folder2_var.get(),
                'comparison_version': '2.0'  # Updated version
            },
            'statistics': self.folder_results.get('statistics', {}),
            'file_results': self.folder_results.get('file_results', {})
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, default=str)
            
    def export_as_text(self, filename: str):
        """Export results as formatted text"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("REQIF FOLDER COMPARISON RESULTS\n")
            f.write("=" * 50 + "\n\n")
            
            f.write(f"Export Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Original Folder: {self.folder1_var.get()}\n")
            f.write(f"Modified Folder: {self.folder2_var.get()}\n\n")
            
            # Write statistics
            stats = self.folder_results.get('statistics', {})
            f.write("SUMMARY STATISTICS:\n")
            f.write("-" * 30 + "\n")
            f.write(f"Total Files: {stats.get('total_files', 0)}\n")
            f.write(f"Files with Changes: {stats.get('files_with_changes', 0)}\n")
            f.write(f"Requirements Added: {stats.get('total_added', 0)}\n")
            f.write(f"Requirements Deleted: {stats.get('total_deleted', 0)}\n")
            f.write(f"Content Modified: {stats.get('total_content_modified', 0)}\n")
            f.write(f"Structural Changes: {stats.get('total_structural_only', 0)}\n")
            f.write(f"Unchanged: {stats.get('total_unchanged', 0)}\n\n")
            
            # Write file details
            f.write("FILE DETAILS:\n")
            f.write("-" * 30 + "\n")
            
            for file_path, file_result in self.folder_results.get('file_results', {}).items():
                comparison = file_result.get('comparison', {})
                
                # Count changes
                added_count = len(comparison.get('added', []))
                deleted_count = len(comparison.get('deleted', []))
                content_count = len(comparison.get('content_modified', []))
                structural_count = len(comparison.get('structural_only', []))
                
                total_changes = added_count + deleted_count + content_count + structural_count
                
                if total_changes > 0:
                    f.write(f"\nFile: {file_path}\n")
                    f.write(f"  Added: {added_count}\n")
                    f.write(f"  Deleted: {deleted_count}\n")
                    f.write(f"  Content Modified: {content_count}\n")
                    f.write(f"  Structural Changes: {structural_count}\n")
                    
    def clear_results(self):
        """Clear all comparison results"""
        self.folder_results = {}
        self.selected_file = None
        
        # Clear statistics
        for label in self.stats_labels.values():
            label.configure(text="0")
            
        # Clear file tree
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
            
        # Clear detail tabs
        for tab_type in ['added', 'deleted', 'content_modified', 'structural_only', 'unchanged']:
            text_widget = getattr(self, f"{tab_type}_text", None)
            if text_widget:
                text_widget.delete(1.0, tk.END)
                
        # Clear summary
        if hasattr(self, 'summary_text'):
            self.summary_text.configure(state=tk.NORMAL)
            self.summary_text.delete(1.0, tk.END)
            self.summary_text.configure(state=tk.DISABLED)
            
        # Reset progress
        self.progress_var.set(0)
        self.current_file_label.configure(text="Ready to compare")
        self.progress_label.configure(text="")
        
        self.update_status("Results cleared")
        
    def update_status(self, message: str):
        """Update status bar message"""
        self.status_var.set(message)
        self.root.update_idletasks()


def main():
    """Main function to run the updated folder comparison GUI"""
    root = tk.Tk()
    app = FolderComparisonGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()