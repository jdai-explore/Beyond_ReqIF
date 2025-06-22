#!/usr/bin/env python3
"""
ComparisonResultsGUI - Phase 2: Show Differences Feature
Enhanced with side-by-side diff viewer similar to Beyond Compare.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import os
from typing import Dict, List, Any
import difflib
import re


class ComparisonResultsGUI:
    """
    Comparison Results GUI - Phase 2
    Enhanced with Show Differences feature
    """
    
    def __init__(self, parent: tk.Widget, results: Dict[str, Any]):
        self.parent = parent
        self.results = results
        
        # Create independent window
        self.window = tk.Toplevel(parent)
        self.window.title("Requirements Comparison Results")
        self.window.geometry("1400x800")
        
        # Ensure window independence
        self.window.transient(parent)
        self.window.focus_set()
        
        # Phase 2: Track selected items for diff viewer
        self.selected_modified_items = []
        
        # Setup GUI
        self.setup_gui()
        
        # Handle window closing
        self.window.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def setup_gui(self):
        """Setup GUI with Phase 2 enhancements"""
        # Configure main window grid
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        
        # Create main container
        self.main_frame = ttk.Frame(self.window, padding="15")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure main frame grid
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(2, weight=1)
        
        # Create sections
        self._create_header_section()
        self._create_summary_section()
        self._create_results_section()
        self._create_controls_section()
    
    def _create_header_section(self):
        """Create header with Phase 2 info"""
        header_frame = ttk.Frame(self.main_frame)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Title
        title_label = ttk.Label(
            header_frame,
            text="Requirements Comparison Results",
            font=("Helvetica", 16, "bold")
        )
        title_label.grid(row=0, column=0, sticky=(tk.W))
        
        # Phase 2 subtitle
        subtitle_label = ttk.Label(
            header_frame,
            text="Select modified requirements and click 'Show Differences' for detailed comparison",
            font=("Helvetica", 9, "italic"),
            foreground="gray"
        )
        subtitle_label.grid(row=1, column=0, sticky=(tk.W), pady=(5, 0))
    
    def _create_summary_section(self):
        """Create summary statistics"""
        summary_frame = ttk.LabelFrame(self.main_frame, text="Summary Statistics", padding="10")
        summary_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Configure grid for 4 columns
        for i in range(4):
            summary_frame.columnconfigure(i, weight=1)
        
        # Get statistics
        stats = self.results.get('statistics', {})
        
        # Create summary labels with color coding
        ttk.Label(summary_frame, text="Added", font=("Helvetica", 10, "bold")).grid(row=0, column=0)
        added_label = ttk.Label(summary_frame, text=str(stats.get('added_count', 0)), font=("Helvetica", 14))
        added_label.grid(row=1, column=0)
        
        ttk.Label(summary_frame, text="Deleted", font=("Helvetica", 10, "bold")).grid(row=0, column=1)
        deleted_label = ttk.Label(summary_frame, text=str(stats.get('deleted_count', 0)), font=("Helvetica", 14))
        deleted_label.grid(row=1, column=1)
        
        ttk.Label(summary_frame, text="Modified", font=("Helvetica", 10, "bold")).grid(row=0, column=2)
        modified_label = ttk.Label(summary_frame, text=str(stats.get('modified_count', 0)), font=("Helvetica", 14))
        modified_label.grid(row=1, column=2)
        
        ttk.Label(summary_frame, text="Unchanged", font=("Helvetica", 10, "bold")).grid(row=0, column=3)
        unchanged_label = ttk.Label(summary_frame, text=str(stats.get('unchanged_count', 0)), font=("Helvetica", 14))
        unchanged_label.grid(row=1, column=3)
    
    def _create_results_section(self):
        """Create results with tabs"""
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create tabs
        self._create_added_tab()
        self._create_deleted_tab()
        self._create_modified_tab()  # Enhanced for Phase 2
        self._create_unchanged_tab()
    
    def _create_added_tab(self):
        """Create added requirements tab"""
        added_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(added_frame, text=f"Added ({len(self.results.get('added', []))})")
        self._create_requirements_tree(added_frame, self.results.get('added', []), "added")
    
    def _create_deleted_tab(self):
        """Create deleted requirements tab"""
        deleted_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(deleted_frame, text=f"Deleted ({len(self.results.get('deleted', []))})")
        self._create_requirements_tree(deleted_frame, self.results.get('deleted', []), "deleted")
    
    def _create_modified_tab(self):
        """Create enhanced modified requirements tab for Phase 2"""
        modified_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(modified_frame, text=f"Modified ({len(self.results.get('modified', []))})")
        
        # Phase 2: Enhanced modified tab with Show Differences button
        self._create_enhanced_modified_tree(modified_frame, self.results.get('modified', []))
    
    def _create_unchanged_tab(self):
        """Create unchanged requirements tab"""
        unchanged_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(unchanged_frame, text=f"Unchanged ({len(self.results.get('unchanged', []))})")
        self._create_requirements_tree(unchanged_frame, self.results.get('unchanged', []), "unchanged")
    
    def _create_enhanced_modified_tree(self, parent, requirements: List[Dict]):
        """Phase 2: Create enhanced modified requirements tree with diff functionality"""
        # Configure parent grid
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)
        
        # Phase 2: Controls frame for Show Differences button
        controls_frame = ttk.Frame(parent)
        controls_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.show_diff_btn = ttk.Button(
            controls_frame,
            text="Show Differences",
            command=self._show_differences,
            state=tk.DISABLED
        )
        self.show_diff_btn.grid(row=0, column=0, padx=(0, 10))
        
        self.selection_info_label = ttk.Label(
            controls_frame,
            text="Select a modified requirement to view differences",
            font=("Helvetica", 9),
            foreground="gray"
        )
        self.selection_info_label.grid(row=0, column=1, sticky=(tk.W))
        
        # Tree frame
        tree_frame = ttk.Frame(parent)
        tree_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # Define columns for modified requirements
        columns = ['title', 'description', 'type', 'changes_summary', 'change_count']
        
        # Create treeview
        self.modified_tree = ttk.Treeview(tree_frame, columns=columns, show='tree headings', selectmode='extended')
        self.modified_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure columns
        self.modified_tree.heading('#0', text='ID', anchor=tk.W)
        self.modified_tree.column('#0', width=120, minwidth=80)
        
        for col in columns:
            display_name = col.replace('_', ' ').title()
            self.modified_tree.heading(col, text=display_name, anchor=tk.W)
            
            # Set column widths
            if col == 'description':
                self.modified_tree.column(col, width=300, minwidth=200)
            elif col == 'changes_summary':
                self.modified_tree.column(col, width=200, minwidth=150)
            elif col == 'change_count':
                self.modified_tree.column(col, width=80, minwidth=60)
            elif col == 'title':
                self.modified_tree.column(col, width=200, minwidth=150)
            else:
                self.modified_tree.column(col, width=120, minwidth=100)
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.modified_tree.yview)
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.modified_tree.configure(yscrollcommand=v_scrollbar.set)
        
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.modified_tree.xview)
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.modified_tree.configure(xscrollcommand=h_scrollbar.set)
        
        # Populate tree
        self._populate_tree(self.modified_tree, requirements, "modified")
        
        # Phase 2: Bind events for selection handling
        self.modified_tree.bind('<<TreeviewSelect>>', self._on_modified_selection_change)
        self.modified_tree.bind('<Double-1>', lambda event: self._on_item_double_click(self.modified_tree, requirements, "modified"))
    
    def _create_requirements_tree(self, parent, requirements: List[Dict], category: str):
        """Create standard treeview for non-modified requirements"""
        # Configure parent grid
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        
        # Create frame
        tree_frame = ttk.Frame(parent)
        tree_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # Define columns
        columns = ['title', 'description', 'type']
        
        # Create treeview
        tree = ttk.Treeview(tree_frame, columns=columns, show='tree headings', selectmode='extended')
        tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure columns
        tree.heading('#0', text='ID', anchor=tk.W)
        tree.column('#0', width=120, minwidth=80)
        
        for col in columns:
            tree.heading(col, text=col.title(), anchor=tk.W)
            if col == 'description':
                tree.column(col, width=300, minwidth=200)
            elif col == 'title':
                tree.column(col, width=200, minwidth=150)
            else:
                tree.column(col, width=120, minwidth=100)
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        tree.configure(yscrollcommand=v_scrollbar.set)
        
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=tree.xview)
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        tree.configure(xscrollcommand=h_scrollbar.set)
        
        # Populate tree
        self._populate_tree(tree, requirements, category)
        
        # Bind events
        tree.bind('<Double-1>', lambda event: self._on_item_double_click(tree, requirements, category))
    
    def _populate_tree(self, tree, requirements: List[Dict], category: str):
        """Populate treeview with data"""
        for i, req in enumerate(requirements):
            try:
                req_id = str(req.get('id', f'{category}_{i}'))
                title = str(req.get('title', ''))[:100]
                description = str(req.get('description', ''))[:150]
                req_type = str(req.get('type', ''))
                
                if category == "modified":
                    # For modified requirements, show changes info
                    changes_summary = str(req.get('changes_summary', 'Unknown changes'))[:100]
                    change_count = str(req.get('change_count', 0))
                    values = [title, description, req_type, changes_summary, change_count]
                else:
                    # For other categories, show standard info
                    values = [title, description, req_type]
                
                tree.insert('', 'end', text=req_id, values=values)
                
            except Exception as e:
                print(f"Error inserting {category} requirement {i}: {e}")
                continue
    
    def _on_modified_selection_change(self, event):
        """Phase 2: Handle selection changes in modified requirements tree"""
        try:
            selection = self.modified_tree.selection()
            self.selected_modified_items = list(selection)
            
            if len(selection) == 1:
                self.show_diff_btn.configure(state=tk.NORMAL)
                self.selection_info_label.configure(text="1 requirement selected - click 'Show Differences' to view changes")
            elif len(selection) > 1:
                self.show_diff_btn.configure(state=tk.DISABLED)
                self.selection_info_label.configure(text=f"{len(selection)} requirements selected - select only one to view differences")
            else:
                self.show_diff_btn.configure(state=tk.DISABLED)
                self.selection_info_label.configure(text="Select a modified requirement to view differences")
                
        except Exception as e:
            print(f"Error handling selection change: {e}")
    
    def _show_differences(self):
        """Phase 2: Show side-by-side differences for selected requirement"""
        if not self.selected_modified_items or len(self.selected_modified_items) != 1:
            messagebox.showwarning("Selection Required", "Please select exactly one modified requirement to view differences.")
            return
        
        try:
            # Get the selected item
            item = self.selected_modified_items[0]
            item_index = self.modified_tree.index(item)
            
            # Get the requirement data
            modified_requirements = self.results.get('modified', [])
            if item_index >= len(modified_requirements):
                messagebox.showerror("Error", "Could not find requirement data.")
                return
            
            requirement = modified_requirements[item_index]
            
            # Launch diff viewer
            self._launch_diff_viewer(requirement)
            
        except Exception as e:
            print(f"Error showing differences: {e}")
            messagebox.showerror("Error", f"Failed to show differences:\n{str(e)}")
    
    def _launch_diff_viewer(self, requirement: Dict):
        """Phase 2: Launch the side-by-side diff viewer window"""
        try:
            # Get comparison data
            comparison_data = requirement.get('_comparison_data', {})
            if not comparison_data:
                messagebox.showwarning("No Comparison Data", "No comparison data available for this requirement.")
                return
            
            old_req = comparison_data.get('old', {})
            new_req = comparison_data.get('new', {})
            changes = comparison_data.get('changes', [])
            
            if not old_req or not new_req:
                messagebox.showwarning("Incomplete Data", "Incomplete comparison data for this requirement.")
                return
            
            # Create diff viewer window
            DiffViewerWindow(self.window, requirement['id'], old_req, new_req, changes)
            
        except Exception as e:
            print(f"Error launching diff viewer: {e}")
            messagebox.showerror("Error", f"Failed to launch diff viewer:\n{str(e)}")
    
    def _create_controls_section(self):
        """Create control buttons"""
        controls_frame = ttk.Frame(self.main_frame)
        controls_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(15, 0))
        
        # Export button
        ttk.Button(controls_frame, text="Export All Results", 
                  command=self._export_all_results).grid(row=0, column=0, padx=(0, 10))
        
        # Close button
        ttk.Button(controls_frame, text="Close", 
                  command=self._on_closing).grid(row=0, column=1, sticky=(tk.E))
    
    def _on_item_double_click(self, tree, requirements: List[Dict], category: str):
        """Handle double-click on tree item"""
        selection = tree.selection()
        if not selection:
            return
        
        try:
            item = selection[0]
            item_index = tree.index(item)
            
            if item_index < len(requirements):
                req = requirements[item_index]
                if category == "modified":
                    # For modified requirements, offer choice between details and diff
                    self._show_modified_requirement_options(req)
                else:
                    self._show_requirement_details(req, category)
        except Exception as e:
            print(f"Error handling double-click: {e}")
    
    def _show_modified_requirement_options(self, requirement: Dict):
        """Show options for modified requirements (details or diff)"""
        choice_window = tk.Toplevel(self.window)
        choice_window.title("View Options")
        choice_window.geometry("400x200")
        choice_window.transient(self.window)
        choice_window.grab_set()
        
        # Center the window
        choice_window.update_idletasks()
        x = choice_window.winfo_screenwidth() // 2 - choice_window.winfo_width() // 2
        y = choice_window.winfo_screenheight() // 2 - choice_window.winfo_height() // 2
        choice_window.geometry(f"+{x}+{y}")
        
        main_frame = ttk.Frame(choice_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        req_id = requirement.get('id', 'Unknown')
        ttk.Label(main_frame, text=f"View options for requirement: {req_id}", 
                 font=("Helvetica", 12, "bold")).pack(pady=(0, 15))
        
        ttk.Label(main_frame, text="How would you like to view this modified requirement?").pack(pady=(0, 20))
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        def show_details():
            choice_window.destroy()
            self._show_requirement_details(requirement, "modified")
        
        def show_diff():
            choice_window.destroy()
            self._launch_diff_viewer(requirement)
        
        ttk.Button(button_frame, text="Show Details", command=show_details, width=15).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Show Differences", command=show_diff, width=15).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="Cancel", command=choice_window.destroy, width=15).pack(side=tk.RIGHT)
    
    def _show_requirement_details(self, requirement: Dict, category: str):
        """Show detailed requirement information"""
        details_window = tk.Toplevel(self.window)
        details_window.title(f"Requirement Details - {category.title()}")
        details_window.geometry("700x600")
        details_window.transient(self.window)
        
        # Configure grid
        details_window.columnconfigure(0, weight=1)
        details_window.rowconfigure(0, weight=1)
        
        main_frame = ttk.Frame(details_window, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title = requirement.get('title', requirement.get('id', 'Unknown'))
        ttk.Label(main_frame, text=f"Requirement: {title}", 
                 font=("Helvetica", 14, "bold")).grid(row=0, column=0, sticky=(tk.W), pady=(0, 15))
        
        # Details in scrollable text
        text_frame = ttk.Frame(main_frame)
        text_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        details_text = tk.Text(text_frame, wrap=tk.WORD, state=tk.NORMAL)
        details_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=details_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        details_text.configure(yscrollcommand=scrollbar.set)
        
        # Populate details based on category
        if category == "modified":
            self._populate_modified_details(details_text, requirement)
        else:
            self._populate_standard_details(details_text, requirement, category)
        
        details_text.configure(state=tk.DISABLED)
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=2, column=0, pady=(15, 0))
        
        if category == "modified":
            # Add Show Differences button for modified requirements
            ttk.Button(buttons_frame, text="Show Differences", 
                      command=lambda: [details_window.destroy(), self._launch_diff_viewer(requirement)]).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(buttons_frame, text="Close", command=details_window.destroy).pack(side=tk.RIGHT)
    
    def _populate_standard_details(self, text_widget, requirement: Dict, category: str):
        """Populate details for non-modified requirements"""
        text_widget.insert(tk.END, f"Category: {category.title()}\n\n")
        text_widget.insert(tk.END, f"ID: {requirement.get('id', 'N/A')}\n\n")
        text_widget.insert(tk.END, f"Title: {requirement.get('title', 'N/A')}\n\n")
        text_widget.insert(tk.END, f"Description: {requirement.get('description', 'N/A')}\n\n")
        text_widget.insert(tk.END, f"Type: {requirement.get('type', 'N/A')}\n\n")
        text_widget.insert(tk.END, f"Priority: {requirement.get('priority', 'N/A')}\n\n")
        text_widget.insert(tk.END, f"Status: {requirement.get('status', 'N/A')}\n\n")
        
        # Show attributes
        attributes = requirement.get('attributes', {})
        if attributes:
            text_widget.insert(tk.END, "Attributes:\n")
            for attr_name, attr_value in attributes.items():
                text_widget.insert(tk.END, f"  {attr_name}: {attr_value}\n")
    
    def _populate_modified_details(self, text_widget, requirement: Dict):
        """Populate details for modified requirements with change information"""
        text_widget.insert(tk.END, "Category: Modified\n\n")
        text_widget.insert(tk.END, f"ID: {requirement.get('id', 'N/A')}\n\n")
        
        # Show current (new) values
        text_widget.insert(tk.END, "=== CURRENT VALUES (After Changes) ===\n\n")
        text_widget.insert(tk.END, f"Title: {requirement.get('title', 'N/A')}\n\n")
        text_widget.insert(tk.END, f"Description: {requirement.get('description', 'N/A')}\n\n")
        text_widget.insert(tk.END, f"Type: {requirement.get('type', 'N/A')}\n\n")
        text_widget.insert(tk.END, f"Priority: {requirement.get('priority', 'N/A')}\n\n")
        text_widget.insert(tk.END, f"Status: {requirement.get('status', 'N/A')}\n\n")
        
        # Show change summary
        changes_summary = requirement.get('changes_summary', 'Unknown changes')
        change_count = requirement.get('change_count', 0)
        text_widget.insert(tk.END, f"=== CHANGE SUMMARY ===\n")
        text_widget.insert(tk.END, f"Fields Changed: {changes_summary}\n")
        text_widget.insert(tk.END, f"Total Changes: {change_count}\n\n")
        
        # Show detailed changes if available
        comparison_data = requirement.get('_comparison_data', {})
        if comparison_data:
            changes = comparison_data.get('changes', [])
            old_req = comparison_data.get('old', {})
            
            if changes:
                text_widget.insert(tk.END, "=== DETAILED CHANGES ===\n\n")
                
                for change in changes:
                    field = change.get('field', 'Unknown')
                    change_type = change.get('change_type', 'modified')
                    old_value = change.get('old_value', '')
                    new_value = change.get('new_value', '')
                    
                    text_widget.insert(tk.END, f"Field: {field}\n")
                    text_widget.insert(tk.END, f"Change Type: {change_type.title()}\n")
                    
                    if change_type == 'added':
                        text_widget.insert(tk.END, f"Added Value: {new_value}\n")
                    elif change_type == 'deleted':
                        text_widget.insert(tk.END, f"Deleted Value: {old_value}\n")
                    else:  # modified
                        text_widget.insert(tk.END, f"Old Value: {old_value}\n")
                        text_widget.insert(tk.END, f"New Value: {new_value}\n")
                    
                    text_widget.insert(tk.END, "\n" + "-"*50 + "\n\n")
            
            # Show original values for reference
            if old_req:
                text_widget.insert(tk.END, "=== ORIGINAL VALUES (Before Changes) ===\n\n")
                text_widget.insert(tk.END, f"Title: {old_req.get('title', 'N/A')}\n\n")
                text_widget.insert(tk.END, f"Description: {old_req.get('description', 'N/A')}\n\n")
                text_widget.insert(tk.END, f"Type: {old_req.get('type', 'N/A')}\n\n")
                text_widget.insert(tk.END, f"Priority: {old_req.get('priority', 'N/A')}\n\n")
                text_widget.insert(tk.END, f"Status: {old_req.get('status', 'N/A')}\n\n")
        
        # Show current attributes
        attributes = requirement.get('attributes', {})
        if attributes:
            text_widget.insert(tk.END, "=== CURRENT ATTRIBUTES ===\n")
            for attr_name, attr_value in attributes.items():
                text_widget.insert(tk.END, f"  {attr_name}: {attr_value}\n")
    
    def _export_all_results(self):
        """Export all results to CSV"""
        try:
            filename = filedialog.asksaveasfilename(
                title="Export All Results",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile="comparison_results_all.csv"
            )
            
            if not filename:
                return
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Enhanced header for Phase 2
                writer.writerow(['Category', 'ID', 'Title', 'Description', 'Type', 'Priority', 'Status', 'Changes_Summary', 'Change_Count'])
                
                for category in ['added', 'deleted', 'modified', 'unchanged']:
                    requirements = self.results.get(category, [])
                    for req in requirements:
                        # Handle modified requirements differently
                        if category == 'modified':
                            changes_summary = req.get('changes_summary', '')
                            change_count = req.get('change_count', 0)
                        else:
                            changes_summary = ''
                            change_count = 0
                        
                        writer.writerow([
                            category.title(),
                            req.get('id', ''),
                            req.get('title', ''),
                            req.get('description', ''),
                            req.get('type', ''),
                            req.get('priority', ''),
                            req.get('status', ''),
                            changes_summary,
                            change_count
                        ])
            
            messagebox.showinfo("Export Complete", f"Results exported to:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export results:\n{str(e)}")
    
    def _on_closing(self):
        """Handle window closing"""
        try:
            self.window.destroy()
        except:
            pass


class DiffViewerWindow:
    """
    Phase 2: Side-by-side diff viewer window similar to Beyond Compare
    """
    
    def __init__(self, parent: tk.Widget, req_id: str, old_req: Dict, new_req: Dict, changes: List[Dict]):
        self.parent = parent
        self.req_id = req_id
        self.old_req = old_req
        self.new_req = new_req
        self.changes = changes
        
        # Create diff viewer window
        self.window = tk.Toplevel(parent)
        self.window.title(f"Show Differences - {req_id}")
        self.window.geometry("1200x800")
        self.window.transient(parent)
        
        # Track current field being viewed
        self.current_field = None
        self.field_data = {}
        
        # Build field data
        self._build_field_data()
        
        # Create UI
        self._create_diff_viewer_ui()
        
        # Show first field with changes
        self._show_first_changed_field()
    
    def _build_field_data(self):
        """Build comprehensive field data for diff viewing"""
        # Standard fields
        standard_fields = ['title', 'description', 'type', 'priority', 'status']
        
        for field in standard_fields:
            old_value = str(self.old_req.get(field, '') or '')
            new_value = str(self.new_req.get(field, '') or '')
            
            self.field_data[field] = {
                'display_name': field.title(),
                'old_value': old_value,
                'new_value': new_value,
                'has_changes': old_value != new_value,
                'field_type': 'standard'
            }
        
        # Attribute fields
        old_attrs = self.old_req.get('attributes', {})
        new_attrs = self.new_req.get('attributes', {})
        all_attr_keys = set(old_attrs.keys()) | set(new_attrs.keys())
        
        for attr_key in all_attr_keys:
            old_value = str(old_attrs.get(attr_key, '') or '')
            new_value = str(new_attrs.get(attr_key, '') or '')
            
            self.field_data[f'attribute.{attr_key}'] = {
                'display_name': f'Attribute: {attr_key}',
                'old_value': old_value,
                'new_value': new_value,
                'has_changes': old_value != new_value,
                'field_type': 'attribute'
            }
    
    def _create_diff_viewer_ui(self):
        """Create the side-by-side diff viewer UI"""
        # Configure main window grid
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        
        # Main container
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Header
        self._create_diff_header(main_frame)
        
        # Field selector
        self._create_field_selector(main_frame)
        
        # Side-by-side diff panes
        self._create_diff_panes(main_frame)
        
        # Controls
        self._create_diff_controls(main_frame)
    
    def _create_diff_header(self, parent):
        """Create diff viewer header"""
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        header_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(
            header_frame,
            text=f"Differences for Requirement: {self.req_id}",
            font=("Helvetica", 14, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=3, sticky=(tk.W), pady=(0, 10))
        
        # Column headers
        ttk.Label(header_frame, text="Original", font=("Helvetica", 12, "bold")).grid(
            row=1, column=0, sticky=(tk.W), padx=(0, 10))
        
        ttk.Label(header_frame, text="Modified", font=("Helvetica", 12, "bold")).grid(
            row=1, column=2, sticky=(tk.W), padx=(10, 0))
        
        # Separator
        separator = ttk.Separator(header_frame, orient='vertical')
        separator.grid(row=1, column=1, sticky=(tk.N, tk.S), padx=5)
    
    def _create_field_selector(self, parent):
        """Create field selector dropdown"""
        selector_frame = ttk.Frame(parent)
        selector_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        ttk.Label(selector_frame, text="Field:", font=("Helvetica", 10, "bold")).grid(
            row=0, column=0, sticky=(tk.W), padx=(0, 10))
        
        # Create field options
        self.field_options = []
        self.field_var = tk.StringVar()
        
        for field_key, field_info in self.field_data.items():
            display_text = field_info['display_name']
            if field_info['has_changes']:
                display_text += " (Modified)"
            self.field_options.append((field_key, display_text))
        
        # Sort so changed fields appear first
        self.field_options.sort(key=lambda x: (not self.field_data[x[0]]['has_changes'], x[1]))
        
        self.field_combo = ttk.Combobox(
            selector_frame,
            textvariable=self.field_var,
            values=[option[1] for option in self.field_options],
            state='readonly',
            width=50
        )
        self.field_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        self.field_combo.bind('<<ComboboxSelected>>', self._on_field_change)
        
        # Navigation buttons
        self.prev_btn = ttk.Button(selector_frame, text="← Previous", command=self._show_previous_field)
        self.prev_btn.grid(row=0, column=2, padx=(0, 5))
        
        self.next_btn = ttk.Button(selector_frame, text="Next →", command=self._show_next_field)
        self.next_btn.grid(row=0, column=3, padx=(0, 10))
        
        # Change indicator
        self.change_indicator = ttk.Label(selector_frame, text="", font=("Helvetica", 9))
        self.change_indicator.grid(row=0, column=4, sticky=(tk.W))
    
    def _create_diff_panes(self, parent):
        """Create side-by-side diff panes"""
        panes_frame = ttk.Frame(parent)
        panes_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        panes_frame.columnconfigure(0, weight=1)
        panes_frame.columnconfigure(2, weight=1)
        panes_frame.rowconfigure(0, weight=1)
        
        # Left pane (Original)
        left_frame = ttk.LabelFrame(panes_frame, text="Original", padding="10")
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(0, weight=1)
        
        self.left_text = tk.Text(
            left_frame,
            wrap=tk.WORD,
            font=("Consolas", 10),
            state=tk.DISABLED,
            bg="#f8f8f8"
        )
        self.left_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        left_scroll = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.left_text.yview)
        left_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.left_text.configure(yscrollcommand=left_scroll.set)
        
        # Separator
        separator = ttk.Separator(panes_frame, orient='vertical')
        separator.grid(row=0, column=1, sticky=(tk.N, tk.S), padx=5)
        
        # Right pane (Modified)
        right_frame = ttk.LabelFrame(panes_frame, text="Modified", padding="10")
        right_frame.grid(row=0, column=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(0, weight=1)
        
        self.right_text = tk.Text(
            right_frame,
            wrap=tk.WORD,
            font=("Consolas", 10),
            state=tk.DISABLED,
            bg="#f8f8f8"
        )
        self.right_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        right_scroll = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.right_text.yview)
        right_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.right_text.configure(yscrollcommand=right_scroll.set)
        
        # Configure text highlighting tags
        self._configure_text_tags()
        
        # Bind synchronized scrolling
        self._bind_synchronized_scrolling()
    
    def _configure_text_tags(self):
        """Configure text highlighting tags for diff visualization"""
        # Deletion highlighting (red background)
        self.left_text.tag_configure("deleted", background="#ffdddd", foreground="#cc0000")
        
        # Addition highlighting (green background)
        self.right_text.tag_configure("added", background="#ddffdd", foreground="#006600")
        
        # Modification highlighting (yellow background)
        self.left_text.tag_configure("modified_old", background="#ffffdd", foreground="#666600")
        self.right_text.tag_configure("modified_new", background="#ffffdd", foreground="#666600")
        
        # Line number highlighting
        self.left_text.tag_configure("line_num", foreground="#888888", font=("Consolas", 8))
        self.right_text.tag_configure("line_num", foreground="#888888", font=("Consolas", 8))
    
    def _bind_synchronized_scrolling(self):
        """Bind synchronized scrolling between left and right panes"""
        def sync_scroll(*args):
            self.left_text.yview_moveto(args[0])
            self.right_text.yview_moveto(args[0])
        
        def on_left_scroll(*args):
            self.right_text.yview(*args)
            return 'break'
        
        def on_right_scroll(*args):
            self.left_text.yview(*args)
            return 'break'
        
        self.left_text.bind('<MouseWheel>', lambda e: on_left_scroll('scroll', -1 * (e.delta // 120), 'units'))
        self.right_text.bind('<MouseWheel>', lambda e: on_right_scroll('scroll', -1 * (e.delta // 120), 'units'))
    
    def _create_diff_controls(self, parent):
        """Create diff viewer controls"""
        controls_frame = ttk.Frame(parent)
        controls_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(15, 0))
        
        # Export diff button
        ttk.Button(controls_frame, text="Export Diff Report", 
                  command=self._export_diff_report).grid(row=0, column=0, padx=(0, 10))
        
        # Copy buttons
        ttk.Button(controls_frame, text="Copy Original", 
                  command=self._copy_original).grid(row=0, column=1, padx=(0, 10))
        
        ttk.Button(controls_frame, text="Copy Modified", 
                  command=self._copy_modified).grid(row=0, column=2, padx=(0, 20))
        
        # Close button
        ttk.Button(controls_frame, text="Close", 
                  command=self.window.destroy).grid(row=0, column=3, sticky=(tk.E))
    
    def _show_first_changed_field(self):
        """Show the first field that has changes"""
        for field_key, field_info in self.field_data.items():
            if field_info['has_changes']:
                self._show_field(field_key)
                break
        else:
            # If no changes, show first field
            if self.field_options:
                self._show_field(self.field_options[0][0])
    
    def _show_field(self, field_key: str):
        """Show the specified field in the diff viewer"""
        if field_key not in self.field_data:
            return
        
        self.current_field = field_key
        field_info = self.field_data[field_key]
        
        # Update field selector
        for i, (key, display_text) in enumerate(self.field_options):
            if key == field_key:
                self.field_combo.current(i)
                break
        
        # Update change indicator
        if field_info['has_changes']:
            self.change_indicator.configure(text="✓ Modified", foreground="orange")
        else:
            self.change_indicator.configure(text="= Unchanged", foreground="green")
        
        # Show field content
        self._display_field_content(field_info)
        
        # Update navigation buttons
        self._update_navigation_buttons()
    
    def _display_field_content(self, field_info: Dict):
        """Display field content with diff highlighting"""
        old_value = field_info['old_value']
        new_value = field_info['new_value']
        
        # Clear text widgets
        self.left_text.configure(state=tk.NORMAL)
        self.right_text.configure(state=tk.NORMAL)
        self.left_text.delete(1.0, tk.END)
        self.right_text.delete(1.0, tk.END)
        
        if field_info['has_changes']:
            # Show diff highlighting
            self._display_diff_content(old_value, new_value)
        else:
            # Show identical content
            self.left_text.insert(tk.END, old_value if old_value else "(empty)")
            self.right_text.insert(tk.END, new_value if new_value else "(empty)")
        
        # Disable editing
        self.left_text.configure(state=tk.DISABLED)
        self.right_text.configure(state=tk.DISABLED)
    
    def _display_diff_content(self, old_value: str, new_value: str):
        """Display content with diff highlighting"""
        if not old_value and not new_value:
            self.left_text.insert(tk.END, "(empty)")
            self.right_text.insert(tk.END, "(empty)")
            return
        
        if not old_value:
            # Addition only
            self.left_text.insert(tk.END, "(empty)")
            self.right_text.insert(tk.END, new_value, "added")
            return
        
        if not new_value:
            # Deletion only
            self.left_text.insert(tk.END, old_value, "deleted")
            self.right_text.insert(tk.END, "(empty)")
            return
        
        # Generate word-level diff
        old_words = re.split(r'(\s+)', old_value)
        new_words = re.split(r'(\s+)', new_value)
        
        differ = difflib.SequenceMatcher(None, old_words, new_words)
        
        left_pos = 1.0
        right_pos = 1.0
        
        for tag, i1, i2, j1, j2 in differ.get_opcodes():
            old_text = ''.join(old_words[i1:i2])
            new_text = ''.join(new_words[j1:j2])
            
            if tag == 'equal':
                # Unchanged text
                self.left_text.insert(tk.END, old_text)
                self.right_text.insert(tk.END, new_text)
            elif tag == 'delete':
                # Deleted text (only in left)
                self.left_text.insert(tk.END, old_text, "deleted")
            elif tag == 'insert':
                # Inserted text (only in right)
                self.right_text.insert(tk.END, new_text, "added")
            elif tag == 'replace':
                # Modified text
                self.left_text.insert(tk.END, old_text, "modified_old")
                self.right_text.insert(tk.END, new_text, "modified_new")
    
    def _on_field_change(self, event=None):
        """Handle field selection change"""
        try:
            selected_index = self.field_combo.current()
            if 0 <= selected_index < len(self.field_options):
                field_key = self.field_options[selected_index][0]
                self._show_field(field_key)
        except Exception as e:
            print(f"Error changing field: {e}")
    
    def _show_previous_field(self):
        """Show previous field"""
        try:
            current_index = self.field_combo.current()
            if current_index > 0:
                self.field_combo.current(current_index - 1)
                self._on_field_change()
        except Exception as e:
            print(f"Error showing previous field: {e}")
    
    def _show_next_field(self):
        """Show next field"""
        try:
            current_index = self.field_combo.current()
            if current_index < len(self.field_options) - 1:
                self.field_combo.current(current_index + 1)
                self._on_field_change()
        except Exception as e:
            print(f"Error showing next field: {e}")
    
    def _update_navigation_buttons(self):
        """Update navigation button states"""
        current_index = self.field_combo.current()
        
        # Previous button
        if current_index <= 0:
            self.prev_btn.configure(state=tk.DISABLED)
        else:
            self.prev_btn.configure(state=tk.NORMAL)
        
        # Next button
        if current_index >= len(self.field_options) - 1:
            self.next_btn.configure(state=tk.DISABLED)
        else:
            self.next_btn.configure(state=tk.NORMAL)
    
    def _copy_original(self):
        """Copy original content to clipboard"""
        try:
            content = self.left_text.get(1.0, tk.END).strip()
            self.window.clipboard_clear()
            self.window.clipboard_append(content)
            messagebox.showinfo("Copied", "Original content copied to clipboard")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy content:\n{str(e)}")
    
    def _copy_modified(self):
        """Copy modified content to clipboard"""
        try:
            content = self.right_text.get(1.0, tk.END).strip()
            self.window.clipboard_clear()
            self.window.clipboard_append(content)
            messagebox.showinfo("Copied", "Modified content copied to clipboard")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy content:\n{str(e)}")
    
    def _export_diff_report(self):
        """Export detailed diff report"""
        try:
            filename = filedialog.asksaveasfilename(
                title="Export Diff Report",
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                initialfile=f"diff_report_{self.req_id}.txt"
            )
            
            if not filename:
                return
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"Difference Report for Requirement: {self.req_id}\n")
                f.write("=" * 60 + "\n\n")
                
                for field_key, field_info in self.field_data.items():
                    f.write(f"Field: {field_info['display_name']}\n")
                    f.write("-" * 30 + "\n")
                    
                    if field_info['has_changes']:
                        f.write("Status: MODIFIED\n\n")
                        f.write(f"Original:\n{field_info['old_value']}\n\n")
                        f.write(f"Modified:\n{field_info['new_value']}\n\n")
                    else:
                        f.write("Status: UNCHANGED\n\n")
                        f.write(f"Content:\n{field_info['old_value']}\n\n")
                    
                    f.write("\n" + "="*60 + "\n\n")
            
            messagebox.showinfo("Export Complete", f"Diff report exported to:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export diff report:\n{str(e)}")