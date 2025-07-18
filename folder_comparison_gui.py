#!/usr/bin/env python3
"""
Folder Comparison GUI - Fixed Version
Handles: Added, Deleted, Content Changed, Structural Changes, Unchanged
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, List, Tuple, Optional, Any
import threading
from datetime import datetime
import json

from reqif_comparator import ReqIFComparator
from folder_comparator import FolderComparator


class FolderComparisonGUI:
    """Main GUI for folder comparison with updated statistics and visualization"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("ReqIF Folder Comparison Tool - Updated")
        self.root.geometry("1400x900")
        
        self.folder_results: Dict[str, Any] = {}
        self.current_comparison = None
        self.folder_comparator = FolderComparator()
        
        self.is_comparing = False
        self.selected_file = None
        
        # Define colors for change types
        self.change_colors = {
            'added': '#2E7D32',
            'deleted': '#C62828',
            'content_modified': '#FF8F00',
            'structural_only': '#1976D2',
            'unchanged': '#424242'
        }
        
        self.setup_ui()
        self.setup_styles()
        
    def setup_styles(self):
        """Setup custom styles for the updated interface"""
        style = ttk.Style()
        
        style.configure("Added.Treeview", foreground=self.change_colors['added'])
        style.configure("Deleted.Treeview", foreground=self.change_colors['deleted'])
        style.configure("ContentModified.Treeview", foreground=self.change_colors['content_modified'])
        style.configure("StructuralOnly.Treeview", foreground=self.change_colors['structural_only'])
        style.configure("Unchanged.Treeview", foreground=self.change_colors['unchanged'])
        
    def setup_ui(self):
        """Setup the main UI with updated layout"""
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.setup_folder_selection(main_frame)
        self.setup_progress_section(main_frame)
        self.setup_results_section(main_frame)
        self.setup_status_bar()
        
    def setup_folder_selection(self, parent):
        """Setup folder selection section"""
        selection_frame = ttk.LabelFrame(parent, text="Folder Selection", padding=10)
        selection_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(selection_frame, text="Original Folder:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.folder1_var = tk.StringVar()
        ttk.Entry(selection_frame, textvariable=self.folder1_var, width=60).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(selection_frame, text="Browse", 
                  command=lambda: self.browse_folder(self.folder1_var)).grid(row=0, column=2)
        
        ttk.Label(selection_frame, text="Modified Folder:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.folder2_var = tk.StringVar()
        ttk.Entry(selection_frame, textvariable=self.folder2_var, width=60).grid(row=1, column=1, padx=(0, 10), pady=(10, 0))
        ttk.Button(selection_frame, text="Browse", 
                  command=lambda: self.browse_folder(self.folder2_var)).grid(row=1, column=2, pady=(10, 0))
        
        button_frame = ttk.Frame(selection_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=(20, 0))
        
        self.compare_btn = ttk.Button(button_frame, text="Start Comparison", 
                                    command=self.start_comparison)
        self.compare_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_btn = ttk.Button(button_frame, text="Stop", 
                                 command=self.stop_comparison)
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 10))
        self.stop_btn.config(state=tk.DISABLED)
        
        ttk.Button(button_frame, text="Export Results", 
                  command=self.export_results).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="Clear Results", 
                  command=self.clear_results).pack(side=tk.LEFT)
        
    def setup_progress_section(self, parent):
        """Setup progress tracking section"""
        progress_frame = ttk.LabelFrame(parent, text="Progress", padding=10)
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                          length=400, mode='determinate')
        self.progress_bar.pack(pady=(0, 10))
        
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
        
        paned = ttk.PanedWindow(results_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)
        
        self.setup_statistics_panel(left_frame)
        
        tree_frame = ttk.LabelFrame(left_frame, text="Files with Changes", padding=5)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
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
        
        tree_scroll_y = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.file_tree.yview)
        tree_scroll_x = ttk.Scrollbar(tree_container, orient=tk.HORIZONTAL, command=self.file_tree.xview)
        self.file_tree.configure(yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
        
        self.file_tree.grid(row=0, column=0, sticky='nsew')
        tree_scroll_y.grid(row=0, column=1, sticky='ns')
        tree_scroll_x.grid(row=1, column=0, sticky='ew')
        
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)
        
        self.file_tree.bind('<<TreeviewSelect>>', self.on_file_select)
        self.file_tree.bind('<Double-1>', self.on_file_double_click)
        
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=2)
        
        detail_label = ttk.Label(right_frame, text="Detailed Comparison", font=('TkDefaultFont', 10, 'bold'))
        detail_label.pack(anchor=tk.W, pady=(0, 10))
        
        self.detail_notebook = ttk.Notebook(right_frame)
        self.detail_notebook.pack(fill=tk.BOTH, expand=True)
        
        self.setup_detail_tabs()
        
    def setup_statistics_panel(self, parent):
        """Setup updated statistics panel"""
        stats_frame = ttk.LabelFrame(parent, text="Summary Statistics", padding=10)
        stats_frame.pack(fill=tk.X)
        
        self.stats_labels = {}
        
        ttk.Label(stats_frame, text="Total Files:", font=('TkDefaultFont', 9, 'bold')).grid(row=0, column=0, sticky=tk.W)
        self.stats_labels['total_files'] = ttk.Label(stats_frame, text="0")
        self.stats_labels['total_files'].grid(row=0, column=1, sticky=tk.W, padx=(10, 20))
        
        ttk.Label(stats_frame, text="Files with Changes:", font=('TkDefaultFont', 9, 'bold')).grid(row=0, column=2, sticky=tk.W)
        self.stats_labels['files_changed'] = ttk.Label(stats_frame, text="0")
        self.stats_labels['files_changed'].grid(row=0, column=3, sticky=tk.W, padx=(10, 0))
        
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
        
        ttk.Label(stats_frame, text="Unchanged:", 
                 foreground=self.change_colors['unchanged']).grid(row=3, column=0, sticky=tk.W, pady=(5, 0))
        self.stats_labels['unchanged'] = ttk.Label(stats_frame, text="0", 
                                                  foreground=self.change_colors['unchanged'])
        self.stats_labels['unchanged'].grid(row=3, column=1, sticky=tk.W, padx=(10, 20), pady=(5, 0))
        
        for i in range(4):
            stats_frame.grid_columnconfigure(i, weight=1)
            
    def setup_detail_tabs(self):
        """Setup updated detail tabs for new comparison structure"""
        self.summary_frame = ttk.Frame(self.detail_notebook)
        self.detail_notebook.add(self.summary_frame, text="Summary")
        self.setup_summary_tab()
        
    def setup_summary_tab(self):
        """Setup summary tab with detailed statistics"""
        summary_container = ttk.Frame(self.summary_frame)
        summary_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.summary_text = tk.Text(summary_container, wrap=tk.WORD, font=('Consolas', 10))
        summary_scroll = ttk.Scrollbar(summary_container, orient=tk.VERTICAL, command=self.summary_text.yview)
        self.summary_text.configure(yscrollcommand=summary_scroll.set)
        
        self.summary_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        summary_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.summary_text.config(state=tk.DISABLED)
        
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
            
        self.clear_results()
        
        self.is_comparing = True
        self.compare_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        
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
                if self.is_comparing:
                    progress = (current / total) * 100 if total > 0 else 0
                    self.root.after(0, self.update_progress, progress, f"Processing: {filename}", current, total)
            
            self.folder_results = self.folder_comparator.compare_folders(
                folder1, folder2
            )
            
            if self.is_comparing:
                self.root.after(0, self.comparison_complete)
                
        except Exception as e:
            if self.is_comparing:
                self.root.after(0, self.comparison_error, str(e))
                
    def update_progress(self, progress: float, message: str, current: int, total: int):
        """Update progress display"""
        self.progress_var.set(progress)
        self.current_file_label.config(text=message)
        self.progress_label.config(text=f"{current}/{total} files")
        self.root.update_idletasks()
        
    def comparison_complete(self):
        """Handle comparison completion with updated statistics"""
        self.is_comparing = False
        self.compare_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        
        self.update_status("Comparison completed")
        self.current_file_label.config(text="Comparison completed")
        self.progress_var.set(100)
        
        self.update_statistics()
        self.update_file_tree()
        self.update_summary()
        
        stats = self.folder_results.get('aggregated_statistics', {})
        total_changes = (stats.get('total_requirements_added', 0) + 
                        stats.get('total_requirements_deleted', 0) + 
                        stats.get('total_requirements_content_modified', 0) + 
                        stats.get('total_requirements_structural_only', 0))
        
        messagebox.showinfo(
            "Comparison Complete", 
            f"Comparison completed successfully!\n\n"
            f"Files processed: {self.folder_results.get('folder_statistics', {}).get('total_matched_files', 0)}\n"
            f"Files with changes: {self.folder_results.get('folder_statistics', {}).get('files_with_content_changes', 0)}\n"
            f"Total requirement changes: {total_changes}"
        )
        
    def comparison_error(self, error_msg: str):
        """Handle comparison error"""
        self.is_comparing = False
        self.compare_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        
        self.update_status(f"Comparison failed: {error_msg}")
        messagebox.showerror("Comparison Error", f"An error occurred during comparison:\n\n{error_msg}")
        
    def stop_comparison(self):
        """Stop ongoing comparison"""
        self.is_comparing = False
        self.compare_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.update_status("Comparison stopped by user")
        
    def update_statistics(self):
        """Update statistics display with new categories"""
        if not self.folder_results:
            return
            
        folder_stats = self.folder_results.get('folder_statistics', {})
        req_stats = self.folder_results.get('aggregated_statistics', {})
        
        self.stats_labels['total_files'].config(text=str(folder_stats.get('total_matched_files', 0)))
        self.stats_labels['files_changed'].config(text=str(folder_stats.get('files_with_content_changes', 0)))
        
        self.stats_labels['added'].config(text=str(req_stats.get('total_requirements_added', 0)))
        self.stats_labels['deleted'].config(text=str(req_stats.get('total_requirements_deleted', 0)))
        self.stats_labels['content_modified'].config(text=str(req_stats.get('total_requirements_content_modified', 0)))
        self.stats_labels['structural_only'].config(text=str(req_stats.get('total_requirements_structural_only', 0)))
        self.stats_labels['unchanged'].config(text=str(req_stats.get('total_requirements_unchanged', 0)))
        
    def update_file_tree(self):
        """Update file tree with clearer change indicators"""
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
            
        if not self.folder_results:
            return
            
        individual_stats = self.folder_results.get('individual_file_statistics', {})
        matched_files = individual_stats.get('matched_files', {})
        
        for file_path, file_data in matched_files.items():
            try:
                comparison_stats = file_data.get('comparison_stats', {})
                
                added_count = comparison_stats.get('added_count', 0)
                deleted_count = comparison_stats.get('deleted_count', 0)
                content_count = comparison_stats.get('content_modified_count', 0)
                structural_count = comparison_stats.get('structural_only_count', 0)
                
                total_changes = added_count + deleted_count + content_count + structural_count
                
                if total_changes == 0:
                    continue
                    
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
                    tag = "content_modified"
                    
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
                
                item_id = self.file_tree.insert('', 'end', text=file_path, 
                                              values=(status, change_summary),
                                              tags=(tag,))
                
                self.file_tree.tag_configure(tag, foreground=self.change_colors[tag])
                
            except Exception as e:
                print(f"Error processing file {file_path}: {e}")
                continue
                
        added_files = individual_stats.get('added_files', {})
        for file_path, file_data in added_files.items():
            req_count = file_data.get('requirement_count', 0)
            self.file_tree.insert('', 'end', text=file_path,
                                 values=("File Added", f"+{req_count} reqs"),
                                 tags=("added",))
            self.file_tree.tag_configure("added", foreground=self.change_colors['added'])
            
        deleted_files = individual_stats.get('deleted_files', {})
        for file_path, file_data in deleted_files.items():
            req_count = file_data.get('requirement_count', 0)
            self.file_tree.insert('', 'end', text=file_path,
                                 values=("File Deleted", f"-{req_count} reqs"),
                                 tags=("deleted",))
            self.file_tree.tag_configure("deleted", foreground=self.change_colors['deleted'])
            
    def update_summary(self):
        """Update summary tab with detailed analysis"""
        if not self.folder_results:
            return
            
        self.summary_text.config(state=tk.NORMAL)
        self.summary_text.delete(1.0, tk.END)
        
        try:
            summary_content = self.folder_comparator.export_folder_summary_enhanced(self.folder_results)
            self.summary_text.insert(1.0, summary_content)
        except Exception as e:
            folder_stats = self.folder_results.get('folder_statistics', {})
            req_stats = self.folder_results.get('aggregated_statistics', {})
            
            summary_lines = [
                "FOLDER COMPARISON SUMMARY",
                "=" * 50,
                "",
                f"Comparison completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"Original folder: {self.folder1_var.get()}",
                f"Modified folder: {self.folder2_var.get()}",
                "",
                "FILE STATISTICS:",
                f"  Total files processed: {folder_stats.get('total_matched_files', 0)}",
                f"  Files with changes: {folder_stats.get('files_with_content_changes', 0)}",
                f"  Files unchanged: {folder_stats.get('files_unchanged', 0)}",
                "",
                "REQUIREMENT CHANGES:",
                f"  Added requirements: {req_stats.get('total_requirements_added', 0)}",
                f"  Deleted requirements: {req_stats.get('total_requirements_deleted', 0)}",
                f"  Content modified: {req_stats.get('total_requirements_content_modified', 0)}",
                f"  Structural changes only: {req_stats.get('total_requirements_structural_only', 0)}",
                f"  Unchanged requirements: {req_stats.get('total_requirements_unchanged', 0)}",
                "",
                f"Content Change Rate: {req_stats.get('content_change_percentage', 0)}%",
                f"Overall Change Rate: {req_stats.get('overall_change_percentage', 0)}%",
            ]
            
            summary_text = "\n".join(summary_lines)
            self.summary_text.insert(1.0, summary_text)
        
        self.summary_text.config(state=tk.DISABLED)
        
    def on_file_select(self, event):
        """Handle file selection in tree"""
        selection = self.file_tree.selection()
        if not selection:
            return
            
        item_id = selection[0]
        file_path = self.file_tree.item(item_id, 'text')
        
        self.selected_file = file_path
        
    def on_file_double_click(self, event):
        """Handle double-click on file tree item"""
        selection = self.file_tree.selection()
        if not selection:
            return
            
        item_id = selection[0]
        file_path = self.file_tree.item(item_id, 'text')
        
        self.show_detailed_comparison(file_path)
        
    def show_detailed_comparison(self, file_path: str):
        """Show detailed comparison for selected file"""
        individual_stats = self.folder_results.get('individual_file_statistics', {})
        matched_files = individual_stats.get('matched_files', {})
        
        if file_path not in matched_files:
            messagebox.showinfo("File Details", f"No detailed comparison data available for:\n{file_path}")
            return
            
        file_data = matched_files[file_path]
        comparison_stats = file_data.get('comparison_stats', {})
        
        popup = tk.Toplevel(self.root)
        popup.title(f"File Comparison - {os.path.basename(file_path)}")
        popup.geometry("800x600")
        popup.transient(self.root)
        
        main_frame = tk.Frame(popup, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(main_frame, text=f"Detailed Comparison: {os.path.basename(file_path)}", 
                font=('Arial', 16, 'bold')).pack(anchor=tk.W, pady=(0, 20))
        
        file1_info = file_data.get('file1_info', {})
        file2_info = file_data.get('file2_info', {})
        match_type = file_data.get('match_type', 'unknown')
        
        info_text = f"Match Type: {match_type.title()}\n"
        if file1_info.get('size') and file2_info.get('size'):
            file1_size = round(file1_info['size'] / (1024 * 1024), 2)
            file2_size = round(file2_info['size'] / (1024 * 1024), 2)
            info_text += f"File Sizes: {file1_size}MB → {file2_size}MB\n"
        
        tk.Label(main_frame, text=info_text, font=('Arial', 11), justify=tk.LEFT).pack(anchor=tk.W, pady=(0, 15))
        
        stats_frame = tk.LabelFrame(main_frame, text="Change Statistics", font=('Arial', 12, 'bold'), padx=15, pady=15)
        stats_frame.pack(fill=tk.X, pady=(0, 20))
        
        stats_data = [
            ("Added", comparison_stats.get('added_count', 0), self.change_colors['added']),
            ("Deleted", comparison_stats.get('deleted_count', 0), self.change_colors['deleted']),
            ("Content Modified", comparison_stats.get('content_modified_count', 0), self.change_colors['content_modified']),
            ("Structural Only", comparison_stats.get('structural_only_count', 0), self.change_colors['structural_only']),
            ("Unchanged", comparison_stats.get('unchanged_count', 0), self.change_colors['unchanged'])
        ]
        
        stats_container = tk.Frame(stats_frame)
        stats_container.pack()
        
        for col, (label, count, color) in enumerate(stats_data):
            frame = tk.Frame(stats_container)
            frame.grid(row=0, column=col, padx=15, pady=5)
            
            tk.Label(frame, text=label, font=('Arial', 10, 'bold')).pack()
            tk.Label(frame, text=str(count), font=('Arial', 14, 'bold'), fg=color).pack()
        
        details_frame = tk.LabelFrame(main_frame, text="Change Details", font=('Arial', 12, 'bold'), padx=15, pady=15)
        details_frame.pack(fill=tk.BOTH, expand=True)
        
        details_text = tk.Text(details_frame, wrap=tk.WORD, font=('Arial', 10))
        details_scroll = ttk.Scrollbar(details_frame, orient=tk.VERTICAL, command=details_text.yview)
        details_text.configure(yscrollcommand=details_scroll.set)
        
        details_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        details_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        details_content = []
        
        if comparison_stats.get('content_change_percentage', 0) > 0:
            details_content.append(f"Content Change Rate: {comparison_stats.get('content_change_percentage', 0)}%")
        
        if comparison_stats.get('added_fields'):
            details_content.append(f"Added Fields: {', '.join(comparison_stats['added_fields'])}")
            
        if comparison_stats.get('removed_fields'):
            details_content.append(f"Removed Fields: {', '.join(comparison_stats['removed_fields'])}")
            
        if not details_content:
            details_content.append("No additional change details available.")
            
        details_text.insert(1.0, "\n\n".join(details_content))
        details_text.config(state=tk.DISABLED)
        
        tk.Button(main_frame, text="Close", command=popup.destroy,
                 font=('Arial', 11), relief='raised', bd=2, padx=20, pady=6,
                 cursor='hand2').pack(pady=(20, 0))
        
    def export_results(self):
        """Export comparison results with updated format"""
        if not self.folder_results:
            messagebox.showwarning("Export", "No comparison results to export")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[
                ("Text files", "*.txt"),
                ("JSON files", "*.json"),
                ("CSV files", "*.csv"),
                ("All files", "*.*")
            ],
            title="Export Folder Comparison Results"
        )
        
        if not filename:
            return
            
        try:
            if filename.endswith('.json'):
                self.export_as_json(filename)
            elif filename.endswith('.csv'):
                self.export_as_csv(filename)
            else:
                self.export_as_text(filename)
                
            messagebox.showinfo("Export", f"Results exported successfully to:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export results:\n{str(e)}")
            
    def export_as_json(self, filename: str):
        """Export results as JSON"""
        export_data = {
            'metadata': {
                'export_time': datetime.now().isoformat(),
                'original_folder': self.folder1_var.get(),
                'modified_folder': self.folder2_var.get(),
                'comparison_version': '2.0'
            },
            'folder_statistics': self.folder_results.get('folder_statistics', {}),
            'aggregated_statistics': self.folder_results.get('aggregated_statistics', {}),
            'individual_file_statistics': self.folder_results.get('individual_file_statistics', {}),
            'threading_statistics': self.folder_results.get('threading_statistics', {})
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, default=str)
            
    def export_as_csv(self, filename: str):
        """Export results as CSV"""
        import csv
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            writer.writerow(['File Path', 'Status', 'Added', 'Deleted', 'Content Modified', 'Structural Only', 'Unchanged'])
            
            individual_stats = self.folder_results.get('individual_file_statistics', {})
            matched_files = individual_stats.get('matched_files', {})
            
            for file_path, file_data in matched_files.items():
                comparison_stats = file_data.get('comparison_stats', {})
                
                added = comparison_stats.get('added_count', 0)
                deleted = comparison_stats.get('deleted_count', 0)
                content_mod = comparison_stats.get('content_modified_count', 0)
                structural = comparison_stats.get('structural_only_count', 0)
                unchanged = comparison_stats.get('unchanged_count', 0)
                
                total_changes = added + deleted + content_mod + structural
                status = "Changed" if total_changes > 0 else "Unchanged"
                
                writer.writerow([file_path, status, added, deleted, content_mod, structural, unchanged])
                
            added_files = individual_stats.get('added_files', {})
            for file_path, file_data in added_files.items():
                req_count = file_data.get('requirement_count', 0)
                writer.writerow([file_path, "File Added", req_count, 0, 0, 0, 0])
                
            deleted_files = individual_stats.get('deleted_files', {})
            for file_path, file_data in deleted_files.items():
                req_count = file_data.get('requirement_count', 0)
                writer.writerow([file_path, "File Deleted", 0, req_count, 0, 0, 0])
                
    def export_as_text(self, filename: str):
        """Export results as formatted text"""
        try:
            summary_content = self.folder_comparator.export_folder_summary_enhanced(self.folder_results)
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(summary_content)
                
        except Exception as e:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("REQIF FOLDER COMPARISON RESULTS\n")
                f.write("=" * 50 + "\n\n")
                
                f.write(f"Export Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Original Folder: {self.folder1_var.get()}\n")
                f.write(f"Modified Folder: {self.folder2_var.get()}\n\n")
                
                folder_stats = self.folder_results.get('folder_statistics', {})
                req_stats = self.folder_results.get('aggregated_statistics', {})
                
                f.write("SUMMARY STATISTICS:\n")
                f.write("-" * 30 + "\n")
                f.write(f"Total Files: {folder_stats.get('total_matched_files', 0)}\n")
                f.write(f"Files with Changes: {folder_stats.get('files_with_content_changes', 0)}\n")
                f.write(f"Requirements Added: {req_stats.get('total_requirements_added', 0)}\n")
                f.write(f"Requirements Deleted: {req_stats.get('total_requirements_deleted', 0)}\n")
                f.write(f"Content Modified: {req_stats.get('total_requirements_content_modified', 0)}\n")
                f.write(f"Structural Changes: {req_stats.get('total_requirements_structural_only', 0)}\n")
                f.write(f"Unchanged: {req_stats.get('total_requirements_unchanged', 0)}\n")
                
    def clear_results(self):
        """Clear all comparison results"""
        self.folder_results = {}
        self.selected_file = None
        
        for label in self.stats_labels.values():
            label.config(text="0")
            
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
            
        if hasattr(self, 'summary_text'):
            self.summary_text.config(state=tk.NORMAL)
            self.summary_text.delete(1.0, tk.END)
            self.summary_text.config(state=tk.DISABLED)
            
        self.progress_var.set(0)
        self.current_file_label.config(text="Ready to compare")
        self.progress_label.config(text="")
        
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