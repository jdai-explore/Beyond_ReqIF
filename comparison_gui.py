#!/usr/bin/env python3
"""
ComparisonResultsGUI - Simplified Version
Removed all Apple theme dependencies
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
    Comparison Results GUI - Simplified Version
    """
    
    def __init__(self, parent: tk.Widget, results: Dict[str, Any]):
        self.parent = parent
        self.results = results
        
        # Create independent window
        self.window = tk.Toplevel(parent)
        self.window.title("Requirements Comparison Results")
        self.window.geometry("1400x800")
        self.window.configure(bg='#FFFFFF')
        
        # Ensure window independence
        self.window.transient(parent)
        self.window.focus_set()
        
        # Track selected items for diff viewer
        self.selected_modified_items = []
        
        # Setup GUI
        self.setup_gui()
        
        # Handle window closing
        self.window.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def setup_gui(self):
        """Setup simplified GUI"""
        # Create main container
        self.main_frame = tk.Frame(self.window, bg='#FFFFFF', padx=15, pady=15)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create sections
        self._create_header_section()
        self._create_summary_section()
        self._create_results_section()
        self._create_controls_section()
    
    def _create_header_section(self):
        """Create header"""
        header_frame = tk.Frame(self.main_frame, bg='#FFFFFF')
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Title
        title_label = tk.Label(header_frame, text="Requirements Comparison Results", 
                              font=('Arial', 16, 'bold'), bg='#FFFFFF', fg='#000000')
        title_label.pack(anchor=tk.W)
        
        # Subtitle
        subtitle_label = tk.Label(header_frame,
                                 text="Select modified requirements and click 'Show Differences' for detailed comparison",
                                 font=('Arial', 10), bg='#FFFFFF', fg='#666666')
        subtitle_label.pack(anchor=tk.W, pady=(5, 0))
    
    def _create_summary_section(self):
        """Create summary statistics"""
        summary_frame = tk.LabelFrame(self.main_frame, text="Summary Statistics", 
                                     font=('Arial', 10, 'bold'), bg='#FFFFFF', fg='#000000')
        summary_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Get statistics
        stats = self.results.get('statistics', {})
        
        # Create grid for statistics
        stats_container = tk.Frame(summary_frame, bg='#FFFFFF')
        stats_container.pack(fill=tk.X, padx=10, pady=10)
        
        # Create summary labels
        col = 0
        for label, count in [("Added", stats.get('added_count', 0)),
                            ("Deleted", stats.get('deleted_count', 0)),
                            ("Modified", stats.get('modified_count', 0)),
                            ("Unchanged", stats.get('unchanged_count', 0))]:
            
            frame = tk.Frame(stats_container, bg='#FFFFFF')
            frame.grid(row=0, column=col, padx=20, pady=5)
            
            tk.Label(frame, text=label, font=('Arial', 10, 'bold'), 
                    bg='#FFFFFF', fg='#000000').pack()
            tk.Label(frame, text=str(count), font=('Arial', 14), 
                    bg='#FFFFFF', fg='#0078D4').pack()
            
            col += 1
    
    def _create_results_section(self):
        """Create results with tabs"""
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self._create_added_tab()
        self._create_deleted_tab()
        self._create_modified_tab()
        self._create_unchanged_tab()
    
    def _create_added_tab(self):
        """Create added requirements tab"""
        added_frame = tk.Frame(self.notebook, bg='#FFFFFF')
        self.notebook.add(added_frame, text=f"Added ({len(self.results.get('added', []))})")
        self._create_requirements_tree(added_frame, self.results.get('added', []), "added")
    
    def _create_deleted_tab(self):
        """Create deleted requirements tab"""
        deleted_frame = tk.Frame(self.notebook, bg='#FFFFFF')
        self.notebook.add(deleted_frame, text=f"Deleted ({len(self.results.get('deleted', []))})")
        self._create_requirements_tree(deleted_frame, self.results.get('deleted', []), "deleted")
    
    def _create_modified_tab(self):
        """Create modified requirements tab with diff functionality"""
        modified_frame = tk.Frame(self.notebook, bg='#FFFFFF')
        self.notebook.add(modified_frame, text=f"Modified ({len(self.results.get('modified', []))})")
        
        self._create_enhanced_modified_tree(modified_frame, self.results.get('modified', []))
    
    def _create_unchanged_tab(self):
        """Create unchanged requirements tab"""
        unchanged_frame = tk.Frame(self.notebook, bg='#FFFFFF')
        self.notebook.add(unchanged_frame, text=f"Unchanged ({len(self.results.get('unchanged', []))})")
        self._create_requirements_tree(unchanged_frame, self.results.get('unchanged', []), "unchanged")
    
    def _create_enhanced_modified_tree(self, parent, requirements: List[Dict]):
        """Create enhanced modified requirements tree with diff functionality"""
        # Configure parent
        parent.configure(bg='#FFFFFF')
        
        # Controls frame for Show Differences button
        controls_frame = tk.Frame(parent, bg='#FFFFFF')
        controls_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.show_diff_btn = tk.Button(controls_frame, text="Show Differences",
                                      command=self._show_differences, state=tk.DISABLED,
                                      bg='#0078D4', fg='white', font=('Arial', 10))
        self.show_diff_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.selection_info_label = tk.Label(controls_frame,
                                           text="Select a modified requirement to view differences",
                                           font=('Arial', 9), bg='#FFFFFF', fg='#666666')
        self.selection_info_label.pack(side=tk.LEFT)
        
        # Tree frame
        tree_frame = tk.Frame(parent, bg='#FFFFFF')
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Define columns for modified requirements
        columns = ['title', 'description', 'type', 'changes_summary', 'change_count']
        
        # Create treeview
        self.modified_tree = ttk.Treeview(tree_frame, columns=columns, show='tree headings', selectmode='extended')
        self.modified_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure columns
        self.modified_tree.heading('#0', text='ID', anchor=tk.W)
        self.modified_tree.column('#0', width=120, minwidth=80)
        
        for col in columns:
            display_name = col.replace('_', ' ').title()
            self.modified_tree.heading(col, text=display_name, anchor=tk.W)
            
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
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.modified_tree.configure(yscrollcommand=v_scrollbar.set)
        
        # Populate tree
        self._populate_tree(self.modified_tree, requirements, "modified")
        
        # Bind events for selection handling
        self.modified_tree.bind('<<TreeviewSelect>>', self._on_modified_selection_change)
        self.modified_tree.bind('<Double-1>', lambda event: self._on_item_double_click(self.modified_tree, requirements, "modified"))
    
    def _create_requirements_tree(self, parent, requirements: List[Dict], category: str):
        """Create standard treeview for non-modified requirements"""
        parent.configure(bg='#FFFFFF')
        
        # Create frame
        tree_frame = tk.Frame(parent, bg='#FFFFFF')
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Define columns
        columns = ['title', 'description', 'type']
        
        # Create treeview
        tree = ttk.Treeview(tree_frame, columns=columns, show='tree headings', selectmode='extended')
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
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
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.configure(yscrollcommand=v_scrollbar.set)
        
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
                    changes_summary = str(req.get('changes_summary', 'Unknown changes'))[:100]
                    change_count = str(req.get('change_count', 0))
                    values = [title, description, req_type, changes_summary, change_count]
                else:
                    values = [title, description, req_type]
                
                tree.insert('', 'end', text=req_id, values=values)
                
            except Exception as e:
                print(f"Error inserting {category} requirement {i}: {e}")
                continue
    
    def _on_modified_selection_change(self, event):
        """Handle selection changes in modified requirements tree"""
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
        """Show side-by-side differences for selected requirement"""
        if not self.selected_modified_items or len(self.selected_modified_items) != 1:
            messagebox.showwarning("Selection Required", "Please select exactly one modified requirement to view differences.")
            return
        
        try:
            item = self.selected_modified_items[0]
            item_index = self.modified_tree.index(item)
            
            modified_requirements = self.results.get('modified', [])
            if item_index >= len(modified_requirements):
                messagebox.showerror("Error", "Could not find requirement data.")
                return
            
            requirement = modified_requirements[item_index]
            self._launch_diff_viewer(requirement)
            
        except Exception as e:
            print(f"Error showing differences: {e}")
            messagebox.showerror("Error", f"Failed to show differences:\n{str(e)}")
    
    def _launch_diff_viewer(self, requirement: Dict):
        """Launch the side-by-side diff viewer window"""
        try:
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
            
            DiffViewerWindow(self.window, requirement['id'], old_req, new_req, changes)
            
        except Exception as e:
            print(f"Error launching diff viewer: {e}")
            messagebox.showerror("Error", f"Failed to launch diff viewer:\n{str(e)}")
    
    def _create_controls_section(self):
        """Create control buttons"""
        controls_frame = tk.Frame(self.main_frame, bg='#FFFFFF')
        controls_frame.pack(fill=tk.X, pady=(15, 0))
        
        # Export button
        export_btn = tk.Button(controls_frame, text="Export All Results", 
                              command=self._export_all_results,
                              bg='#0078D4', fg='white', font=('Arial', 10))
        export_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Close button
        close_btn = tk.Button(controls_frame, text="Close", 
                             command=self._on_closing,
                             bg='#F0F0F0', fg='#000000', font=('Arial', 10))
        close_btn.pack(side=tk.RIGHT)
    
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
        choice_window.configure(bg='#FFFFFF')
        choice_window.transient(self.window)
        choice_window.grab_set()
        
        main_frame = tk.Frame(choice_window, bg='#FFFFFF', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        req_id = requirement.get('id', 'Unknown')
        tk.Label(main_frame, text=f"View options for requirement: {req_id}", 
                font=('Arial', 12, 'bold'), bg='#FFFFFF', fg='#000000').pack(pady=(0, 15))
        
        tk.Label(main_frame, text="How would you like to view this modified requirement?",
                bg='#FFFFFF', fg='#000000').pack(pady=(0, 20))
        
        button_frame = tk.Frame(main_frame, bg='#FFFFFF')
        button_frame.pack(fill=tk.X)
        
        def show_details():
            choice_window.destroy()
            self._show_requirement_details(requirement, "modified")
        
        def show_diff():
            choice_window.destroy()
            self._launch_diff_viewer(requirement)
        
        tk.Button(button_frame, text="Show Details", command=show_details, 
                 bg='#0078D4', fg='white', font=('Arial', 10)).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(button_frame, text="Show Differences", command=show_diff,
                 bg='#0078D4', fg='white', font=('Arial', 10)).pack(side=tk.LEFT)
        tk.Button(button_frame, text="Cancel", command=choice_window.destroy,
                 bg='#F0F0F0', fg='#000000', font=('Arial', 10)).pack(side=tk.RIGHT)
    
    def _show_requirement_details(self, requirement: Dict, category: str):
        """Show detailed requirement information"""
        details_window = tk.Toplevel(self.window)
        details_window.title(f"Requirement Details - {category.title()}")
        details_window.geometry("700x600")
        details_window.configure(bg='#FFFFFF')
        details_window.transient(self.window)
        
        main_frame = tk.Frame(details_window, bg='#FFFFFF', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = requirement.get('title', requirement.get('id', 'Unknown'))
        tk.Label(main_frame, text=f"Requirement: {title}", 
                font=('Arial', 14, 'bold'), bg='#FFFFFF', fg='#000000').pack(anchor=tk.W, pady=(0, 15))
        
        # Details in scrollable text
        text_frame = tk.Frame(main_frame, bg='#FFFFFF')
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        details_text = tk.Text(text_frame, wrap=tk.WORD, bg='#FFFFFF', fg='#000000', font=('Arial', 10))
        details_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=details_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        details_text.configure(yscrollcommand=scrollbar.set)
        
        # Populate details
        if category == "modified":
            self._populate_modified_details(details_text, requirement)
        else:
            self._populate_standard_details(details_text, requirement, category)
        
        details_text.configure(state=tk.DISABLED)
        
        # Buttons frame
        buttons_frame = tk.Frame(main_frame, bg='#FFFFFF')
        buttons_frame.pack(fill=tk.X, pady=(15, 0))
        
        if category == "modified":
            tk.Button(buttons_frame, text="Show Differences", 
                     command=lambda: [details_window.destroy(), self._launch_diff_viewer(requirement)],
                     bg='#0078D4', fg='white', font=('Arial', 10)).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(buttons_frame, text="Close", command=details_window.destroy,
                 bg='#F0F0F0', fg='#000000', font=('Arial', 10)).pack(side=tk.RIGHT)
    
    def _populate_standard_details(self, text_widget, requirement: Dict, category: str):
        """Populate details for non-modified requirements"""
        text_widget.insert(tk.END, f"Category: {category.title()}\n\n")
        text_widget.insert(tk.END, f"ID: {requirement.get('id', 'N/A')}\n\n")
        text_widget.insert(tk.END, f"Title: {requirement.get('title', 'N/A')}\n\n")
        text_widget.insert(tk.END, f"Description: {requirement.get('description', 'N/A')}\n\n")
        text_widget.insert(tk.END, f"Type: {requirement.get('type', 'N/A')}\n\n")
        text_widget.insert(tk.END, f"Priority: {requirement.get('priority', 'N/A')}\n\n")
        text_widget.insert(tk.END, f"Status: {requirement.get('status', 'N/A')}\n\n")
        
        attributes = requirement.get('attributes', {})
        if attributes:
            text_widget.insert(tk.END, "Attributes:\n")
            for attr_name, attr_value in attributes.items():
                text_widget.insert(tk.END, f"  {attr_name}: {attr_value}\n")
    
    def _populate_modified_details(self, text_widget, requirement: Dict):
        """Populate details for modified requirements with change information"""
        text_widget.insert(tk.END, "Category: Modified\n\n")
        text_widget.insert(tk.END, f"ID: {requirement.get('id', 'N/A')}\n\n")
        
        text_widget.insert(tk.END, "=== CURRENT VALUES (After Changes) ===\n\n")
        text_widget.insert(tk.END, f"Title: {requirement.get('title', 'N/A')}\n\n")
        text_widget.insert(tk.END, f"Description: {requirement.get('description', 'N/A')}\n\n")
        text_widget.insert(tk.END, f"Type: {requirement.get('type', 'N/A')}\n\n")
        text_widget.insert(tk.END, f"Priority: {requirement.get('priority', 'N/A')}\n\n")
        text_widget.insert(tk.END, f"Status: {requirement.get('status', 'N/A')}\n\n")
        
        changes_summary = requirement.get('changes_summary', 'Unknown changes')
        change_count = requirement.get('change_count', 0)
        text_widget.insert(tk.END, f"=== CHANGE SUMMARY ===\n")
        text_widget.insert(tk.END, f"Fields Changed: {changes_summary}\n")
        text_widget.insert(tk.END, f"Total Changes: {change_count}\n\n")
        
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
                    else:
                        text_widget.insert(tk.END, f"Old Value: {old_value}\n")
                        text_widget.insert(tk.END, f"New Value: {new_value}\n")
                    
                    text_widget.insert(tk.END, "\n" + "-"*50 + "\n\n")
            
            if old_req:
                text_widget.insert(tk.END, "=== ORIGINAL VALUES (Before Changes) ===\n\n")
                text_widget.insert(tk.END, f"Title: {old_req.get('title', 'N/A')}\n\n")
                text_widget.insert(tk.END, f"Description: {old_req.get('description', 'N/A')}\n\n")
                text_widget.insert(tk.END, f"Type: {old_req.get('type', 'N/A')}\n\n")
                text_widget.insert(tk.END, f"Priority: {old_req.get('priority', 'N/A')}\n\n")
                text_widget.insert(tk.END, f"Status: {old_req.get('status', 'N/A')}\n\n")
        
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
                
                writer.writerow(['Category', 'ID', 'Title', 'Description', 'Type', 'Priority', 'Status', 'Changes_Summary', 'Change_Count'])
                
                for category in ['added', 'deleted', 'modified', 'unchanged']:
                    requirements = self.results.get(category, [])
                    for req in requirements:
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
    Side-by-side diff viewer window - simplified version
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
        self.window.configure(bg='#FFFFFF')
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
        main_frame = tk.Frame(self.window, bg='#FFFFFF', padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        self._create_diff_header(main_frame)
        
        # Field selector
        self._create_field_selector(main_frame)
        
        # Side-by-side diff panes
        self._create_diff_panes(main_frame)
        
        # Controls
        self._create_diff_controls(main_frame)
    
    def _create_field_selector(self, parent):
        """Create field selector dropdown"""
        selector_frame = tk.Frame(parent, bg='#FFFFFF')
        selector_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(selector_frame, text="Field:", font=('Arial', 10, 'bold'), 
                bg='#FFFFFF', fg='#000000').pack(side=tk.LEFT, padx=(0, 10))
        
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
        
        self.field_combo = ttk.Combobox(selector_frame, textvariable=self.field_var,
                                       values=[option[1] for option in self.field_options],
                                       state='readonly', width=50)
        self.field_combo.pack(side=tk.LEFT, padx=(0, 10))
        self.field_combo.bind('<<ComboboxSelected>>', self._on_field_change)
        
        # Navigation buttons
        self.prev_btn = tk.Button(selector_frame, text="← Previous", command=self._show_previous_field,
                                 bg='#F0F0F0', fg='#000000', font=('Arial', 9))
        self.prev_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.next_btn = tk.Button(selector_frame, text="Next →", command=self._show_next_field,
                                 bg='#F0F0F0', fg='#000000', font=('Arial', 9))
        self.next_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Change indicator
        self.change_indicator = tk.Label(selector_frame, text="", font=('Arial', 9), 
                                        bg='#FFFFFF', fg='#666666')
        self.change_indicator.pack(side=tk.LEFT)
    
    def _create_diff_panes(self, parent):
        """Create side-by-side diff panes"""
        panes_frame = tk.Frame(parent, bg='#FFFFFF')
        panes_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left pane (Original)
        left_frame = tk.LabelFrame(panes_frame, text="Original", bg='#FFFFFF', fg='#000000')
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.left_text = tk.Text(left_frame, wrap=tk.WORD, font=('Consolas', 10),
                                bg='#F8F8F8', fg='#000000', state=tk.DISABLED)
        self.left_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        left_scroll = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.left_text.yview)
        left_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.left_text.configure(yscrollcommand=left_scroll.set)
        
        # Right pane (Modified)
        right_frame = tk.LabelFrame(panes_frame, text="Modified", bg='#FFFFFF', fg='#000000')
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        self.right_text = tk.Text(right_frame, wrap=tk.WORD, font=('Consolas', 10),
                                 bg='#F8F8F8', fg='#000000', state=tk.DISABLED)
        self.right_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        right_scroll = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.right_text.yview)
        right_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.right_text.configure(yscrollcommand=right_scroll.set)
        
        # Configure text highlighting tags
        self._configure_text_tags()
    
    def _configure_text_tags(self):
        """Configure text highlighting tags for diff visualization"""
        # Deletion highlighting (red background)
        self.left_text.tag_configure("deleted", background="#ffdddd", foreground="#cc0000")
        
        # Addition highlighting (green background)
        self.right_text.tag_configure("added", background="#ddffdd", foreground="#006600")
        
        # Modification highlighting (yellow background)
        self.left_text.tag_configure("modified_old", background="#ffffdd", foreground="#666600")
        self.right_text.tag_configure("modified_new", background="#ffffdd", foreground="#666600")
    
    def _create_diff_controls(self, parent):
        """Create diff viewer controls"""
        controls_frame = tk.Frame(parent, bg='#FFFFFF')
        controls_frame.pack(fill=tk.X, pady=(15, 0))
        
        # Export diff button
        tk.Button(controls_frame, text="Export Diff Report", command=self._export_diff_report,
                 bg='#0078D4', fg='white', font=('Arial', 10)).pack(side=tk.LEFT, padx=(0, 10))
        
        # Copy buttons
        tk.Button(controls_frame, text="Copy Original", command=self._copy_original,
                 bg='#F0F0F0', fg='#000000', font=('Arial', 10)).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(controls_frame, text="Copy Modified", command=self._copy_modified,
                 bg='#F0F0F0', fg='#000000', font=('Arial', 10)).pack(side=tk.LEFT, padx=(0, 20))
        
        # Close button
        tk.Button(controls_frame, text="Close", command=self.window.destroy,
                 bg='#F0F0F0', fg='#000000', font=('Arial', 10)).pack(side=tk.RIGHT)
    
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
            self.change_indicator.configure(text="✓ Modified", fg="#FF8C00")
        else:
            self.change_indicator.configure(text="= Unchanged", fg="#107C10")
        
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