#!/usr/bin/env python3
"""
ComparisonGUI - Fixed Version
Pure tkinter with dynamic field detection and clear distinction between
content modifications and structural differences
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import os
from typing import Dict, List, Any, Set
import difflib
import re
import threading
from datetime import datetime

from reqif_parser import ReqIFParser
from reqif_comparator import ReqIFComparator


class ComparisonGUI:
    """Single File Comparison GUI - FIXED CLASS NAME"""
    
    def __init__(self, parent):
        self.parent = parent
        self.root = parent
        
        self.reqif_parser = ReqIFParser()
        self.reqif_comparator = ReqIFComparator()
        
        self.file1_var = tk.StringVar()
        self.file2_var = tk.StringVar()
        self.comparison_result = None
        self.is_comparing = False
        
        self.progress_var = tk.DoubleVar()
        self.progress_label = tk.StringVar()
        self.progress_label.set("Ready to compare")
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        
        self.setup_gui()
        
    def setup_gui(self):
        """Setup the comparison GUI"""
        main_frame = tk.Frame(self.parent, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        self._create_header_section(main_frame)
        self._create_file_selection_section(main_frame)
        self._create_progress_section(main_frame)
        self._create_results_section(main_frame)
        self._create_status_bar()
        
    def _create_header_section(self, parent):
        """Create header section"""
        header_frame = tk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = tk.Label(header_frame, text="Single File Comparison", 
                              font=('Arial', 18, 'bold'))
        title_label.pack(anchor=tk.W)
        
        subtitle_label = tk.Label(header_frame,
                                 text="Compare two ReqIF files to see differences between versions",
                                 font=('Arial', 11))
        subtitle_label.pack(anchor=tk.W, pady=(5, 0))
        
    def _create_file_selection_section(self, parent):
        """Create file selection section"""
        selection_frame = tk.LabelFrame(parent, text="File Selection", 
                                       font=('Arial', 12, 'bold'), padx=15, pady=15)
        selection_frame.pack(fill=tk.X, pady=(0, 20))
        
        # File 1 selection
        file1_frame = tk.Frame(selection_frame)
        file1_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(file1_frame, text="Original File:", font=('Arial', 11, 'bold')).pack(side=tk.LEFT)
        file1_entry = tk.Entry(file1_frame, textvariable=self.file1_var, width=60, 
                              font=('Arial', 10))
        file1_entry.pack(side=tk.LEFT, padx=(10, 10), fill=tk.X, expand=True)
        tk.Button(file1_frame, text="Browse", command=self._browse_file1,
                 font=('Arial', 10), relief='raised', bd=2, padx=15, pady=4,
                 cursor='hand2').pack(side=tk.RIGHT)
        
        # File 2 selection
        file2_frame = tk.Frame(selection_frame)
        file2_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(file2_frame, text="Modified File:", font=('Arial', 11, 'bold')).pack(side=tk.LEFT)
        file2_entry = tk.Entry(file2_frame, textvariable=self.file2_var, width=60, 
                              font=('Arial', 10))
        file2_entry.pack(side=tk.LEFT, padx=(10, 10), fill=tk.X, expand=True)
        tk.Button(file2_frame, text="Browse", command=self._browse_file2,
                 font=('Arial', 10), relief='raised', bd=2, padx=15, pady=4,
                 cursor='hand2').pack(side=tk.RIGHT)
        
        # Control buttons
        button_frame = tk.Frame(selection_frame)
        button_frame.pack(fill=tk.X)
        
        self.compare_btn = tk.Button(button_frame, text="🔍 Compare Files", 
                                    command=self._start_comparison,
                                    font=('Arial', 12, 'bold'), relief='raised', bd=3,
                                    padx=25, pady=8, cursor='hand2', bg='lightgreen')
        self.compare_btn.pack(side=tk.LEFT, padx=(0, 15))
        
        self.clear_btn = tk.Button(button_frame, text="Clear", 
                                  command=self._clear_files,
                                  font=('Arial', 11), relief='raised', bd=2,
                                  padx=20, pady=6, cursor='hand2')
        self.clear_btn.pack(side=tk.LEFT, padx=(0, 15))
        
        self.export_btn = tk.Button(button_frame, text="📄 Export Results", 
                                   command=self._export_results,
                                   font=('Arial', 11), relief='raised', bd=2,
                                   padx=20, pady=6, cursor='hand2')
        self.export_btn.pack(side=tk.LEFT)
        self.export_btn.config(state=tk.DISABLED)
        
    def _create_progress_section(self, parent):
        """Create progress section"""
        progress_frame = tk.LabelFrame(parent, text="Progress", 
                                      font=('Arial', 12, 'bold'), padx=15, pady=15)
        progress_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var,
                                           length=400, mode='determinate')
        self.progress_bar.pack(pady=(0, 10))
        
        self.progress_status_label = tk.Label(progress_frame, textvariable=self.progress_label,
                                             font=('Arial', 10))
        self.progress_status_label.pack()
        
    def _create_results_section(self, parent):
        """Create results section"""
        results_frame = tk.LabelFrame(parent, text="Comparison Results", 
                                     font=('Arial', 12, 'bold'), padx=15, pady=15)
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        self.results_notebook = ttk.Notebook(results_frame)
        self.results_notebook.pack(fill=tk.BOTH, expand=True)
        
    def _create_status_bar(self):
        """Create status bar"""
        status_frame = tk.Frame(self.parent, relief=tk.SUNKEN, bd=1)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = tk.Label(status_frame, textvariable=self.status_var,
                                    font=('Arial', 10), anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, padx=10, pady=5)
        
    def _browse_file1(self):
        """Browse for first file"""
        filename = filedialog.askopenfilename(
            title="Select Original ReqIF File",
            filetypes=[
                ("ReqIF files", "*.reqif"),
                ("ReqIF archives", "*.reqifz"),
                ("XML files", "*.xml"),
                ("All files", "*.*")
            ]
        )
        if filename:
            self.file1_var.set(filename)
            self._update_status(f"Selected original file: {os.path.basename(filename)}")
            
    def _browse_file2(self):
        """Browse for second file"""
        filename = filedialog.askopenfilename(
            title="Select Modified ReqIF File",
            filetypes=[
                ("ReqIF files", "*.reqif"),
                ("ReqIF archives", "*.reqifz"),
                ("XML files", "*.xml"),
                ("All files", "*.*")
            ]
        )
        if filename:
            self.file2_var.set(filename)
            self._update_status(f"Selected modified file: {os.path.basename(filename)}")
            
    def _clear_files(self):
        """Clear selected files"""
        self.file1_var.set("")
        self.file2_var.set("")
        self.comparison_result = None
        self._clear_results()
        self._update_status("Files cleared")
        
    def _start_comparison(self):
        """Start the comparison process"""
        file1 = self.file1_var.get().strip()
        file2 = self.file2_var.get().strip()
        
        if not file1 or not file2:
            messagebox.showerror("Error", "Please select both files for comparison")
            return
            
        if not os.path.exists(file1):
            messagebox.showerror("Error", f"Original file not found:\n{file1}")
            return
            
        if not os.path.exists(file2):
            messagebox.showerror("Error", f"Modified file not found:\n{file2}")
            return
            
        self.compare_btn.config(state=tk.DISABLED, text="Comparing...")
        self.is_comparing = True
        self.progress_var.set(0)
        self.progress_label.set("Starting comparison...")
        
        comparison_thread = threading.Thread(target=self._run_comparison, args=(file1, file2))
        comparison_thread.daemon = True
        comparison_thread.start()
        
    def _run_comparison(self, file1: str, file2: str):
        """Run comparison in background thread"""
        try:
            self._update_progress(10, "Parsing original file...")
            file1_reqs = self.reqif_parser.parse_file(file1)
            
            self._update_progress(30, "Parsing modified file...")
            file2_reqs = self.reqif_parser.parse_file(file2)
            
            self._update_progress(60, "Comparing requirements...")
            comparison_result = self.reqif_comparator.compare_requirements(file1_reqs, file2_reqs)
            
            self._update_progress(90, "Preparing results...")
            self.comparison_result = comparison_result
            
            self.parent.after(0, self._comparison_complete)
            
        except Exception as e:
            self.parent.after(0, lambda: self._comparison_error(str(e)))
            
    def _update_progress(self, percent: int, message: str):
        """Update progress (thread-safe)"""
        def update():
            self.progress_var.set(percent)
            self.progress_label.set(message)
            self.parent.update_idletasks()
        
        self.parent.after(0, update)
        
    def _comparison_complete(self):
        """Handle successful comparison completion"""
        self.is_comparing = False
        self.compare_btn.config(state=tk.NORMAL, text="🔍 Compare Files")
        self.export_btn.config(state=tk.NORMAL)
        self.progress_var.set(100)
        self.progress_label.set("Comparison completed successfully!")
        
        self._display_results()
        
        stats = self.comparison_result.get('statistics', {})
        total_changes = (stats.get('added_count', 0) + stats.get('deleted_count', 0) + 
                        stats.get('content_modified_count', 0) + stats.get('structural_only_count', 0))
        
        self._update_status(f"Comparison complete: {total_changes} changes found")
        
        messagebox.showinfo("Comparison Complete", 
                           f"Comparison completed successfully!\n\n"
                           f"Changes found:\n"
                           f"• Added: {stats.get('added_count', 0)}\n"
                           f"• Deleted: {stats.get('deleted_count', 0)}\n"
                           f"• Content Modified: {stats.get('content_modified_count', 0)}\n"
                           f"• Structural Only: {stats.get('structural_only_count', 0)}\n"
                           f"• Unchanged: {stats.get('unchanged_count', 0)}")
        
    def _comparison_error(self, error_msg: str):
        """Handle comparison error"""
        self.is_comparing = False
        self.compare_btn.config(state=tk.NORMAL, text="🔍 Compare Files")
        self.progress_label.set("Comparison failed")
        self._update_status(f"Comparison failed: {error_msg}")
        
        messagebox.showerror("Comparison Error", 
                           f"An error occurred during comparison:\n\n{error_msg}")
        
    def _display_results(self):
        """Display comparison results in notebook tabs"""
        if not self.comparison_result:
            return
            
        for tab in self.results_notebook.tabs():
            self.results_notebook.forget(tab)
            
        self._create_summary_tab()
        
        categories = [
            ('added', 'Added', 'Requirements only in modified file'),
            ('deleted', 'Deleted', 'Requirements only in original file'),
            ('content_modified', 'Content Modified', 'Requirements with content changes'),
            ('structural_only', 'Structural Only', 'Requirements with structural changes only'),
            ('unchanged', 'Unchanged', 'Identical requirements')
        ]
        
        for category, title, description in categories:
            requirements = self.comparison_result.get(category, [])
            if requirements:
                self._create_results_tab(category, f"{title} ({len(requirements)})", 
                                       requirements, description)
        
    def _create_summary_tab(self):
        """Create summary tab"""
        summary_frame = tk.Frame(self.results_notebook)
        self.results_notebook.add(summary_frame, text="📊 Summary")
        
        text_frame = tk.Frame(summary_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        summary_text = tk.Text(text_frame, wrap=tk.WORD, font=('Consolas', 10))
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=summary_text.yview)
        summary_text.configure(yscrollcommand=scrollbar.set)
        
        summary_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        summary_content = self._generate_summary_text()
        
        summary_text.insert(1.0, summary_content)
        summary_text.config(state=tk.DISABLED)
        
    def _create_results_tab(self, category: str, title: str, requirements: List[Dict], description: str):
        """Create a results tab for a specific category"""
        tab_frame = tk.Frame(self.results_notebook)
        self.results_notebook.add(tab_frame, text=title)
        
        desc_label = tk.Label(tab_frame, text=description, font=('Arial', 11), fg='darkblue')
        desc_label.pack(anchor=tk.W, padx=15, pady=(15, 10))
        
        tree_frame = tk.Frame(tab_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        columns = self._determine_columns(requirements)
        
        tree = ttk.Treeview(tree_frame, columns=columns[1:], show='tree headings', selectmode='extended')
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        tree.heading('#0', text=columns[0], anchor=tk.W)
        tree.column('#0', width=120, minwidth=80)
        
        for col in columns[1:]:
            tree.heading(col, text=self._format_column_name(col), anchor=tk.W)
            tree.column(col, width=150, minwidth=80)
        
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.configure(yscrollcommand=v_scrollbar.set)
        
        self._populate_tree(tree, requirements, columns, category)
        
        tree.bind('<Double-1>', lambda event: self._show_requirement_details(tree, requirements, category))
        
    def _determine_columns(self, requirements: List[Dict]) -> List[str]:
        """Determine optimal columns for display based on actual data"""
        if not requirements:
            return ['ID']
            
        all_fields = set()
        for req in requirements:
            if isinstance(req, dict):
                for field_name in req.keys():
                    if not field_name.startswith('_') and field_name not in ['content', 'raw_attributes']:
                        all_fields.add(field_name)
                
                attributes = req.get('attributes', {})
                if isinstance(attributes, dict):
                    for attr_name in attributes.keys():
                        all_fields.add(f'attr_{attr_name}')
        
        priority_fields = ['id', 'identifier', 'type']
        selected_columns = []
        
        for field in priority_fields:
            if field in all_fields:
                selected_columns.append(field)
                all_fields.remove(field)
        
        attr_fields = [f for f in all_fields if f.startswith('attr_')]
        selected_columns.extend(attr_fields[:3])
        
        other_fields = [f for f in all_fields if not f.startswith('attr_')]
        remaining_slots = max(0, 6 - len(selected_columns))
        selected_columns.extend(other_fields[:remaining_slots])
        
        return selected_columns if selected_columns else ['id']
        
    def _format_column_name(self, column_name: str) -> str:
        """Format column name for display"""
        if column_name.startswith('attr_'):
            return column_name[5:].replace('_', ' ').title()
        else:
            return column_name.replace('_', ' ').title()
            
    def _populate_tree(self, tree, requirements: List[Dict], columns: List[str], category: str):
        """Populate tree with requirement data"""
        tree_column = columns[0] if columns else 'id'
        other_columns = columns[1:] if len(columns) > 1 else []
        
        for req in requirements:
            if not isinstance(req, dict):
                continue
                
            tree_value = self._get_field_value(req, tree_column)
            
            values = []
            for col in other_columns:
                value = self._get_field_value(req, col)
                if len(str(value)) > 50:
                    value = str(value)[:47] + "..."
                values.append(value)
            
            if category == 'content_modified':
                change_count = req.get('change_count', 0)
                if change_count > 0:
                    tree_value += f" ({change_count} changes)"
            
            tree.insert('', 'end', text=tree_value, values=values)
            
    def _get_field_value(self, req: Dict[str, Any], field_name: str) -> str:
        """Get field value from requirement"""
        try:
            if field_name.startswith('attr_'):
                attr_name = field_name[5:]
                attributes = req.get('attributes', {})
                if isinstance(attributes, dict):
                    return str(attributes.get(attr_name, ''))
                return ''
            else:
                return str(req.get(field_name, ''))
        except Exception:
            return ''
            
    def _show_requirement_details(self, tree, requirements: List[Dict], category: str):
        """Show detailed requirement information"""
        selection = tree.selection()
        if not selection:
            return
            
        try:
            item = selection[0]
            item_index = tree.index(item)
            
            if item_index < len(requirements):
                req = requirements[item_index]
                
                if category == 'content_modified':
                    self._show_content_modified_details(req)
                else:
                    self._show_standard_requirement_details(req, category)
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to show requirement details:\n{str(e)}")
            
    def _show_content_modified_details(self, req: Dict):
        """Show details for content modified requirement with diff view"""
        details_window = tk.Toplevel(self.parent)
        details_window.title(f"Content Modified - {req.get('id', 'Unknown')}")
        details_window.geometry("900x700")
        details_window.transient(self.parent)
        
        main_frame = tk.Frame(details_window, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(main_frame, text=f"Content Changes: {req.get('id', 'Unknown')}", 
                font=('Arial', 16, 'bold')).pack(anchor=tk.W, pady=(0, 20))
        
        changes_summary = req.get('changes_summary', 'Unknown changes')
        change_count = req.get('change_count', 0)
        
        summary_label = tk.Label(main_frame, text=f"Fields Changed: {changes_summary} ({change_count} total)",
                                font=('Arial', 12), fg='darkorange')
        summary_label.pack(anchor=tk.W, pady=(0, 15))
        
        comparison_data = req.get('_comparison_data')
        if comparison_data and comparison_data.get('changes'):
            self._create_diff_view(main_frame, comparison_data['changes'])
        else:
            text_frame = tk.Frame(main_frame)
            text_frame.pack(fill=tk.BOTH, expand=True)
            
            details_text = tk.Text(text_frame, wrap=tk.WORD, font=('Arial', 11))
            details_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=details_text.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            details_text.configure(yscrollcommand=scrollbar.set)
            
            self._populate_basic_details(details_text, req)
            details_text.config(state=tk.DISABLED)
        
        tk.Button(main_frame, text="Close", command=details_window.destroy,
                 font=('Arial', 11), relief='raised', bd=2, padx=20, pady=6,
                 cursor='hand2').pack(pady=(20, 0))
                 
    def _create_diff_view(self, parent, changes: List[Dict]):
        """Create a diff view for content changes"""
        diff_notebook = ttk.Notebook(parent)
        diff_notebook.pack(fill=tk.BOTH, expand=True)
        
        for change in changes:
            field_name = change.get('field', 'Unknown Field')
            old_value = change.get('old_value', '')
            new_value = change.get('new_value', '')
            
            tab_frame = tk.Frame(diff_notebook)
            diff_notebook.add(tab_frame, text=field_name)
            
            paned = ttk.PanedWindow(tab_frame, orient=tk.HORIZONTAL)
            paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            left_frame = tk.LabelFrame(paned, text="Original", font=('Arial', 11, 'bold'))
            paned.add(left_frame, weight=1)
            
            left_text = tk.Text(left_frame, wrap=tk.WORD, font=('Consolas', 10))
            left_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            left_text.insert(1.0, old_value)
            left_text.config(state=tk.DISABLED)
            
            right_frame = tk.LabelFrame(paned, text="Modified", font=('Arial', 11, 'bold'))
            paned.add(right_frame, weight=1)
            
            right_text = tk.Text(right_frame, wrap=tk.WORD, font=('Consolas', 10))
            right_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            right_text.insert(1.0, new_value)
            right_text.config(state=tk.DISABLED)
            
    def _show_standard_requirement_details(self, req: Dict, category: str):
        """Show standard requirement details"""
        details_window = tk.Toplevel(self.parent)
        details_window.title(f"Requirement Details - {category}")
        details_window.geometry("700x600")
        details_window.transient(self.parent)
        
        main_frame = tk.Frame(details_window, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        req_id = req.get('id', 'Unknown')
        tk.Label(main_frame, text=f"Requirement: {req_id}", 
                font=('Arial', 16, 'bold')).pack(anchor=tk.W, pady=(0, 20))
        
        tk.Label(main_frame, text=f"Category: {category.replace('_', ' ').title()}", 
                font=('Arial', 12), fg='darkblue').pack(anchor=tk.W, pady=(0, 15))
        
        text_frame = tk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        details_text = tk.Text(text_frame, wrap=tk.WORD, font=('Arial', 11))
        details_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=details_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        details_text.configure(yscrollcommand=scrollbar.set)
        
        self._populate_basic_details(details_text, req)
        details_text.config(state=tk.DISABLED)
        
        tk.Button(main_frame, text="Close", command=details_window.destroy,
                 font=('Arial', 11), relief='raised', bd=2, padx=20, pady=6,
                 cursor='hand2').pack(pady=(20, 0))
                 
    def _populate_basic_details(self, text_widget, req: Dict):
        """Populate basic requirement details"""
        excluded_fields = {'attributes', 'raw_attributes', 'content', '_comparison_data'}
        
        for field_name, field_value in req.items():
            if field_name not in excluded_fields and not field_name.startswith('_'):
                if field_value:
                    display_name = self._format_column_name(field_name)
                    text_widget.insert(tk.END, f"{display_name}: {field_value}\n\n")
        
        attributes = req.get('attributes', {})
        if isinstance(attributes, dict) and attributes:
            text_widget.insert(tk.END, "Attributes:\n")
            text_widget.insert(tk.END, "-" * 30 + "\n")
            for attr_name, attr_value in attributes.items():
                if attr_value:
                    text_widget.insert(tk.END, f"{attr_name}: {attr_value}\n")
            text_widget.insert(tk.END, "\n")
            
    def _generate_summary_text(self) -> str:
        """Generate summary text for the summary tab"""
        if not self.comparison_result:
            return "No comparison results available."
            
        stats = self.comparison_result.get('statistics', {})
        
        summary_lines = [
            "REQIF FILE COMPARISON SUMMARY",
            "=" * 50,
            "",
            f"Comparison Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Original File: {os.path.basename(self.file1_var.get())}",
            f"Modified File: {os.path.basename(self.file2_var.get())}",
            "",
            "STATISTICS:",
            f"  Requirements in Original: {stats.get('total_file1', 0)}",
            f"  Requirements in Modified: {stats.get('total_file2', 0)}",
            f"  Total Unique Requirements: {stats.get('total_unique', 0)}",
            "",
            "CHANGES DETECTED:",
            f"  Added Requirements: {stats.get('added_count', 0)}",
            f"  Deleted Requirements: {stats.get('deleted_count', 0)}",
            f"  Content Modified: {stats.get('content_modified_count', 0)}",
            f"  Structural Changes Only: {stats.get('structural_only_count', 0)}",
            f"  Unchanged Requirements: {stats.get('unchanged_count', 0)}",
            "",
            f"CHANGE RATES:",
            f"  Content Change Rate: {stats.get('content_change_percentage', 0)}%",
            f"  Overall Change Rate: {stats.get('total_change_percentage', 0)}%",
        ]
        
        added_fields = stats.get('added_fields', [])
        removed_fields = stats.get('removed_fields', [])
        
        if added_fields or removed_fields:
            summary_lines.extend(["", "STRUCTURAL CHANGES:"])
            
            if added_fields:
                summary_lines.append(f"  Fields Added: {', '.join(added_fields[:5])}")
                if len(added_fields) > 5:
                    summary_lines.append(f"    ... and {len(added_fields) - 5} more")
                    
            if removed_fields:
                summary_lines.append(f"  Fields Removed: {', '.join(removed_fields[:5])}")
                if len(removed_fields) > 5:
                    summary_lines.append(f"    ... and {len(removed_fields) - 5} more")