#!/usr/bin/env python3
"""
ComparisonGUI - Fixed Version with proper ComparisonGUI class
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

# Import the required modules
from reqif_parser import ReqIFParser
from reqif_comparator import ReqIFComparator


class ComparisonGUI:
    """
    Single File Comparison GUI - FIXED CLASS NAME
    """
    
    def __init__(self, parent):
        self.parent = parent
        self.root = parent  # For compatibility
        
        # Initialize components
        self.reqif_parser = ReqIFParser()
        self.reqif_comparator = ReqIFComparator()
        
        # State variables
        self.file1_var = tk.StringVar()
        self.file2_var = tk.StringVar()
        self.comparison_result = None
        self.is_comparing = False
        
        # Progress tracking
        self.progress_var = tk.DoubleVar()
        self.progress_label = tk.StringVar()
        self.progress_label.set("Ready to compare")
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        
        # Setup GUI
        self.setup_gui()
        
    def setup_gui(self):
        """Setup the comparison GUI"""
        # Main container
        main_frame = tk.Frame(self.parent, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create sections
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
                                   padx=20, pady=6, cursor='hand2', state=tk.DISABLED)
        self.export_btn.pack(side=tk.LEFT)
        
    def _create_progress_section(self, parent):
        """Create progress section"""
        progress_frame = tk.LabelFrame(parent, text="Progress", 
                                      font=('Arial', 12, 'bold'), padx=15, pady=15)
        progress_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var,
                                           length=400, mode='determinate')
        self.progress_bar.pack(pady=(0, 10))
        
        # Progress label
        self.progress_status_label = tk.Label(progress_frame, textvariable=self.progress_label,
                                             font=('Arial', 10))
        self.progress_status_label.pack()
        
    def _create_results_section(self, parent):
        """Create results section"""
        results_frame = tk.LabelFrame(parent, text="Comparison Results", 
                                     font=('Arial', 12, 'bold'), padx=15, pady=15)
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook for results
        self.results_notebook = ttk.Notebook(results_frame)
        self.results_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Initially disabled
        self.results_notebook.configure(state='disabled')
        
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
            
        # Disable compare button during comparison
        self.compare_btn.configure(state=tk.DISABLED, text="Comparing...")
        self.is_comparing = True
        self.progress_var.set(0)
        self.progress_label.set("Starting comparison...")
        
        # Start comparison in background thread
        comparison_thread = threading.Thread(target=self._run_comparison, args=(file1, file2))
        comparison_thread.daemon = True
        comparison_thread.start()
        
    def _run_comparison(self, file1: str, file2: str):
        """Run comparison in background thread"""
        try:
            # Parse first file
            self._update_progress(10, "Parsing original file...")
            file1_reqs = self.reqif_parser.parse_file(file1)
            
            # Parse second file
            self._update_progress(30, "Parsing modified file...")
            file2_reqs = self.reqif_parser.parse_file(file2)
            
            # Compare requirements
            self._update_progress(60, "Comparing requirements...")
            comparison_result = self.reqif_comparator.compare_requirements(file1_reqs, file2_reqs)
            
            # Store results and update UI
            self._update_progress(90, "Preparing results...")
            self.comparison_result = comparison_result
            
            # Update UI on main thread
            self.parent.after(0, self._comparison_complete)
            
        except Exception as e:
            # Handle errors on main thread
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
        self.compare_btn.configure(state=tk.NORMAL, text="🔍 Compare Files")
        self.export_btn.configure(state=tk.NORMAL)
        self.progress_var.set(100)
        self.progress_label.set("Comparison completed successfully!")
        
        # Display results
        self._display_results()
        
        # Show summary
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
        self.compare_btn.configure(state=tk.NORMAL, text="🔍 Compare Files")
        self.progress_label.set("Comparison failed")
        self._update_status(f"Comparison failed: {error_msg}")
        
        messagebox.showerror("Comparison Error", 
                           f"An error occurred during comparison:\n\n{error_msg}")
        
    def _display_results(self):
        """Display comparison results in notebook tabs"""
        if not self.comparison_result:
            return
            
        # Clear existing tabs
        for tab in self.results_notebook.tabs():
            self.results_notebook.forget(tab)
            
        # Enable notebook
        self.results_notebook.configure(state='normal')
        
        # Create summary tab
        self._create_summary_tab()
        
        # Create results tabs for each category
        categories = [
            ('added', 'Added', 'Requirements only in modified file'),
            ('deleted', 'Deleted', 'Requirements only in original file'),
            ('content_modified', 'Content Modified', 'Requirements with content changes'),
            ('structural_only', 'Structural Only', 'Requirements with structural changes only'),
            ('unchanged', 'Unchanged', 'Identical requirements')
        ]
        
        for category, title, description in categories:
            requirements = self.comparison_result.get(category, [])
            if requirements:  # Only create tab if there are items
                self._create_results_tab(category, f"{title} ({len(requirements)})", 
                                       requirements, description)
        
    def _create_summary_tab(self):
        """Create summary tab"""
        summary_frame = tk.Frame(self.results_notebook)
        self.results_notebook.add(summary_frame, text="📊 Summary")
        
        # Create scrollable text area
        text_frame = tk.Frame(summary_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        summary_text = tk.Text(text_frame, wrap=tk.WORD, font=('Consolas', 10), state=tk.DISABLED)
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=summary_text.yview)
        summary_text.configure(yscrollcommand=scrollbar.set)
        
        summary_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Generate summary content
        summary_content = self._generate_summary_text()
        
        summary_text.configure(state=tk.NORMAL)
        summary_text.insert(1.0, summary_content)
        summary_text.configure(state=tk.DISABLED)
        
    def _create_results_tab(self, category: str, title: str, requirements: List[Dict], description: str):
        """Create a results tab for a specific category"""
        tab_frame = tk.Frame(self.results_notebook)
        self.results_notebook.add(tab_frame, text=title)
        
        # Description label
        desc_label = tk.Label(tab_frame, text=description, font=('Arial', 11), fg='darkblue')
        desc_label.pack(anchor=tk.W, padx=15, pady=(15, 10))
        
        # Create treeview for requirements
        tree_frame = tk.Frame(tab_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        # Determine columns based on available data
        columns = self._determine_columns(requirements)
        
        tree = ttk.Treeview(tree_frame, columns=columns[1:], show='tree headings', selectmode='extended')
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure columns
        tree.heading('#0', text=columns[0], anchor=tk.W)
        tree.column('#0', width=120, minwidth=80)
        
        for col in columns[1:]:
            tree.heading(col, text=self._format_column_name(col), anchor=tk.W)
            tree.column(col, width=150, minwidth=80)
        
        # Add scrollbar
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.configure(yscrollcommand=v_scrollbar.set)
        
        # Populate tree
        self._populate_tree(tree, requirements, columns, category)
        
        # Bind double-click for details
        tree.bind('<Double-1>', lambda event: self._show_requirement_details(tree, requirements, category))
        
    def _determine_columns(self, requirements: List[Dict]) -> List[str]:
        """Determine optimal columns for display based on actual data"""
        if not requirements:
            return ['ID']
            
        # Collect all possible fields
        all_fields = set()
        for req in requirements:
            if isinstance(req, dict):
                for field_name in req.keys():
                    if not field_name.startswith('_') and field_name not in ['content', 'raw_attributes']:
                        all_fields.add(field_name)
                
                # Add attribute fields
                attributes = req.get('attributes', {})
                if isinstance(attributes, dict):
                    for attr_name in attributes.keys():
                        all_fields.add(f'attr_{attr_name}')
        
        # Prioritize important fields
        priority_fields = ['id', 'identifier', 'type']
        selected_columns = []
        
        # Add priority fields that exist
        for field in priority_fields:
            if field in all_fields:
                selected_columns.append(field)
                all_fields.remove(field)
        
        # Add some attribute fields (limit to keep UI manageable)
        attr_fields = [f for f in all_fields if f.startswith('attr_')]
        selected_columns.extend(attr_fields[:3])  # Add up to 3 attribute fields
        
        # Add other fields up to reasonable limit
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
                
            # Get tree column value
            tree_value = self._get_field_value(req, tree_column)
            
            # Get values for other columns
            values = []
            for col in other_columns:
                value = self._get_field_value(req, col)
                # Truncate long values
                if len(str(value)) > 50:
                    value = str(value)[:47] + "..."
                values.append(value)
            
            # Add special formatting for modified requirements
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
        
        # Title
        tk.Label(main_frame, text=f"Content Changes: {req.get('id', 'Unknown')}", 
                font=('Arial', 16, 'bold')).pack(anchor=tk.W, pady=(0, 20))
        
        # Changes summary
        changes_summary = req.get('changes_summary', 'Unknown changes')
        change_count = req.get('change_count', 0)
        
        summary_label = tk.Label(main_frame, text=f"Fields Changed: {changes_summary} ({change_count} total)",
                                font=('Arial', 12), fg='darkorange')
        summary_label.pack(anchor=tk.W, pady=(0, 15))
        
        # Show comparison data if available
        comparison_data = req.get('_comparison_data')
        if comparison_data and comparison_data.get('changes'):
            self._create_diff_view(main_frame, comparison_data['changes'])
        else:
            # Fallback to basic display
            text_frame = tk.Frame(main_frame)
            text_frame.pack(fill=tk.BOTH, expand=True)
            
            details_text = tk.Text(text_frame, wrap=tk.WORD, font=('Arial', 11))
            details_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=details_text.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            details_text.configure(yscrollcommand=scrollbar.set)
            
            # Show basic requirement info
            self._populate_basic_details(details_text, req)
            details_text.configure(state=tk.DISABLED)
        
        # Close button
        tk.Button(main_frame, text="Close", command=details_window.destroy,
                 font=('Arial', 11), relief='raised', bd=2, padx=20, pady=6,
                 cursor='hand2').pack(pady=(20, 0))
                 
    def _create_diff_view(self, parent, changes: List[Dict]):
        """Create a diff view for content changes"""
        # Create notebook for different changed fields
        diff_notebook = ttk.Notebook(parent)
        diff_notebook.pack(fill=tk.BOTH, expand=True)
        
        for change in changes:
            field_name = change.get('field', 'Unknown Field')
            old_value = change.get('old_value', '')
            new_value = change.get('new_value', '')
            
            # Create tab for this field
            tab_frame = tk.Frame(diff_notebook)
            diff_notebook.add(tab_frame, text=field_name)
            
            # Create side-by-side diff
            paned = ttk.PanedWindow(tab_frame, orient=tk.HORIZONTAL)
            paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Old value (left)
            left_frame = tk.LabelFrame(paned, text="Original", font=('Arial', 11, 'bold'))
            paned.add(left_frame, weight=1)
            
            left_text = tk.Text(left_frame, wrap=tk.WORD, font=('Consolas', 10))
            left_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            left_text.insert(1.0, old_value)
            left_text.configure(state=tk.DISABLED)
            
            # New value (right)
            right_frame = tk.LabelFrame(paned, text="Modified", font=('Arial', 11, 'bold'))
            paned.add(right_frame, weight=1)
            
            right_text = tk.Text(right_frame, wrap=tk.WORD, font=('Consolas', 10))
            right_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            right_text.insert(1.0, new_value)
            right_text.configure(state=tk.DISABLED)
            
    def _show_standard_requirement_details(self, req: Dict, category: str):
        """Show standard requirement details"""
        details_window = tk.Toplevel(self.parent)
        details_window.title(f"Requirement Details - {category}")
        details_window.geometry("700x600")
        details_window.transient(self.parent)
        
        main_frame = tk.Frame(details_window, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        req_id = req.get('id', 'Unknown')
        tk.Label(main_frame, text=f"Requirement: {req_id}", 
                font=('Arial', 16, 'bold')).pack(anchor=tk.W, pady=(0, 20))
        
        # Category info
        tk.Label(main_frame, text=f"Category: {category.replace('_', ' ').title()}", 
                font=('Arial', 12), fg='darkblue').pack(anchor=tk.W, pady=(0, 15))
        
        # Details
        text_frame = tk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        details_text = tk.Text(text_frame, wrap=tk.WORD, font=('Arial', 11))
        details_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=details_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        details_text.configure(yscrollcommand=scrollbar.set)
        
        self._populate_basic_details(details_text, req)
        details_text.configure(state=tk.DISABLED)
        
        # Close button
        tk.Button(main_frame, text="Close", command=details_window.destroy,
                 font=('Arial', 11), relief='raised', bd=2, padx=20, pady=6,
                 cursor='hand2').pack(pady=(20, 0))
                 
    def _populate_basic_details(self, text_widget, req: Dict):
        """Populate basic requirement details"""
        # Show main fields
        excluded_fields = {'attributes', 'raw_attributes', 'content', '_comparison_data'}
        
        for field_name, field_value in req.items():
            if field_name not in excluded_fields and not field_name.startswith('_'):
                if field_value:
                    display_name = self._format_column_name(field_name)
                    text_widget.insert(tk.END, f"{display_name}: {field_value}\n\n")
        
        # Show attributes
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
        
        # Add field changes if available
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
        
        return "\n".join(summary_lines)
        
    def _export_results(self):
        """Export comparison results"""
        if not self.comparison_result:
            messagebox.showwarning("No Results", "No comparison results to export.")
            return
            
        filename = filedialog.asksaveasfilename(
            title="Export Comparison Results",
            defaultextension=".csv",
            filetypes=[
                ("CSV files", "*.csv"),
                ("JSON files", "*.json"),
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )
        
        if not filename:
            return
            
        try:
            if filename.lower().endswith('.json'):
                self._export_json(filename)
            elif filename.lower().endswith('.txt'):
                self._export_text(filename)
            else:
                self._export_csv(filename)
                
            messagebox.showinfo("Export Complete", f"Results exported to:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export results:\n{str(e)}")
            
    def _export_csv(self, filename: str):
        """Export results as CSV"""
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow(['Category', 'ID', 'Type', 'Changes', 'Details'])
            
            # Write data for each category
            categories = ['added', 'deleted', 'content_modified', 'structural_only', 'unchanged']
            
            for category in categories:
                requirements = self.comparison_result.get(category, [])
                for req in requirements:
                    if isinstance(req, dict):
                        req_id = req.get('id', 'Unknown')
                        req_type = req.get('type', '')
                        
                        if category == 'content_modified':
                            changes = req.get('changes_summary', '')
                            details = f"{req.get('change_count', 0)} fields changed"
                        elif category == 'structural_only':
                            added_fields = len(req.get('added_fields', []))
                            removed_fields = len(req.get('removed_fields', []))
                            changes = 'Structural'
                            details = f"+{added_fields} fields, -{removed_fields} fields"
                        else:
                            changes = category.replace('_', ' ').title()
                            details = ''
                        
                        writer.writerow([category, req_id, req_type, changes, details])
                        
    def _export_json(self, filename: str):
        """Export results as JSON"""
        import json
        
        export_data = {
            'metadata': {
                'export_time': datetime.now().isoformat(),
                'original_file': self.file1_var.get(),
                'modified_file': self.file2_var.get(),
                'tool_version': '2.0'
            },
            'results': self.comparison_result
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, default=str)
            
    def _export_text(self, filename: str):
        """Export results as text"""
        summary_content = self._generate_summary_text()
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(summary_content)
            f.write("\n\n")
            f.write("=" * 50 + "\n")
            f.write("DETAILED RESULTS\n")
            f.write("=" * 50 + "\n\n")
            
            # Write detailed results for each category
            categories = [
                ('added', 'ADDED REQUIREMENTS'),
                ('deleted', 'DELETED REQUIREMENTS'),
                ('content_modified', 'CONTENT MODIFIED REQUIREMENTS'),
                ('structural_only', 'STRUCTURAL CHANGES ONLY'),
                ('unchanged', 'UNCHANGED REQUIREMENTS')
            ]
            
            for category, title in categories:
                requirements = self.comparison_result.get(category, [])
                if requirements:
                    f.write(f"{title} ({len(requirements)}):\n")
                    f.write("-" * (len(title) + 10) + "\n")
                    
                    for i, req in enumerate(requirements, 1):
                        if isinstance(req, dict):
                            req_id = req.get('id', 'Unknown')
                            f.write(f"{i}. {req_id}\n")
                            
                            if category == 'content_modified':
                                changes = req.get('changes_summary', 'Unknown changes')
                                change_count = req.get('change_count', 0)
                                f.write(f"   Changes: {changes} ({change_count} fields)\n")
                            elif category == 'structural_only':
                                added_fields = req.get('added_fields', [])
                                removed_fields = req.get('removed_fields', [])
                                f.write(f"   Added fields: {', '.join(added_fields) if added_fields else 'None'}\n")
                                f.write(f"   Removed fields: {', '.join(removed_fields) if removed_fields else 'None'}\n")
                            
                            # Show some basic info
                            req_type = req.get('type', '')
                            if req_type:
                                f.write(f"   Type: {req_type}\n")
                                
                            f.write("\n")
                    
                    f.write("\n")
                    
    def _clear_results(self):
        """Clear comparison results"""
        # Clear existing tabs
        for tab in self.results_notebook.tabs():
            self.results_notebook.forget(tab)
            
        # Disable notebook
        self.results_notebook.configure(state='disabled')
        self.export_btn.configure(state=tk.DISABLED)
        self.progress_var.set(0)
        self.progress_label.set("Ready to compare")
        
    def _update_status(self, message: str):
        """Update status message"""
        self.status_var.set(message)
        self.parent.update_idletasks()


# For backward compatibility, also create ComparisonResultsGUI class
# that delegates to the main ComparisonGUI functionality
class ComparisonResultsGUI:
    """
    Compatibility class that wraps ComparisonGUI for showing results
    """
    
    def __init__(self, parent: tk.Widget, results: Dict[str, Any]):
        self.parent = parent
        self.results = results
        
        # Create window
        self.window = tk.Toplevel(parent)
        self.window.title("Comparison Results")
        self.window.geometry("1200x800")
        self.window.transient(parent)
        
        # Create a simplified results viewer
        self._create_results_viewer()
        
    def _create_results_viewer(self):
        """Create a simplified results viewer"""
        main_frame = tk.Frame(self.window, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        tk.Label(main_frame, text="Comparison Results", 
                font=('Arial', 18, 'bold')).pack(anchor=tk.W, pady=(0, 20))
        
        # Summary
        self._create_summary_section(main_frame)
        
        # Results tabs
        self._create_results_tabs(main_frame)
        
        # Close button
        tk.Button(main_frame, text="Close", command=self.window.destroy,
                 font=('Arial', 11), relief='raised', bd=2, padx=20, pady=6,
                 cursor='hand2').pack(pady=(20, 0))
        
    def _create_summary_section(self, parent):
        """Create summary section"""
        summary_frame = tk.LabelFrame(parent, text="Summary", font=('Arial', 12, 'bold'), 
                                     padx=15, pady=15)
        summary_frame.pack(fill=tk.X, pady=(0, 20))
        
        stats = self.results.get('statistics', {})
        
        # Create summary labels
        summary_data = [
            ("Added", stats.get('added_count', 0), 'darkgreen'),
            ("Deleted", stats.get('deleted_count', 0), 'darkred'),
            ("Content Modified", stats.get('content_modified_count', 0), 'darkorange'),
            ("Structural Only", stats.get('structural_only_count', 0), 'purple'),
            ("Unchanged", stats.get('unchanged_count', 0), 'darkblue')
        ]
        
        stats_container = tk.Frame(summary_frame)
        stats_container.pack()
        
        for col, (label, count, color) in enumerate(summary_data):
            frame = tk.Frame(stats_container)
            frame.grid(row=0, column=col, padx=20, pady=10)
            
            tk.Label(frame, text=label, font=('Arial', 12, 'bold')).pack()
            tk.Label(frame, text=str(count), font=('Arial', 16, 'bold'), 
                    fg=color).pack()
                    
    def _create_results_tabs(self, parent):
        """Create results tabs"""
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        categories = [
            ('added', 'Added'),
            ('deleted', 'Deleted'),
            ('content_modified', 'Content Modified'),
            ('structural_only', 'Structural Only'),
            ('unchanged', 'Unchanged')
        ]
        
        for category, title in categories:
            requirements = self.results.get(category, [])
            if requirements:
                tab_frame = tk.Frame(notebook)
                notebook.add(tab_frame, text=f"{title} ({len(requirements)})")
                
                # Create simple list
                listbox = tk.Listbox(tab_frame, font=('Arial', 10))
                listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                
                for req in requirements:
                    if isinstance(req, dict):
                        req_id = req.get('id', 'Unknown')
                        if category == 'content_modified':
                            change_count = req.get('change_count', 0)
                            listbox.insert(tk.END, f"{req_id} ({change_count} changes)")
                        else:
                            listbox.insert(tk.END, req_id)


def main():
    """Main function for testing"""
    root = tk.Tk()
    app = ComparisonGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()