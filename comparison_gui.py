#!/usr/bin/env python3
"""
Minimal ComparisonResultsGUI - No Theme Dependencies
Pure functionality with basic Tkinter styling.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import os
from typing import Dict, List, Any


class ComparisonResultsGUI:
    """
    Minimal Comparison Results GUI - No theming
    """
    
    def __init__(self, parent: tk.Widget, results: Dict[str, Any]):
        self.parent = parent
        self.results = results
        
        # Create independent window
        self.window = tk.Toplevel(parent)
        self.window.title("Requirements Comparison Results")
        self.window.geometry("1200x800")
        
        # Ensure window independence
        self.window.transient(parent)
        self.window.focus_set()
        
        # Setup GUI
        self.setup_gui()
        
        # Handle window closing
        self.window.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def setup_gui(self):
        """Setup minimal GUI"""
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
        """Create simple header"""
        header_frame = ttk.Frame(self.main_frame)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Simple title
        title_label = ttk.Label(
            header_frame,
            text="Requirements Comparison Results",
            font=("Helvetica", 16, "bold")
        )
        title_label.grid(row=0, column=0, sticky=(tk.W))
    
    def _create_summary_section(self):
        """Create summary statistics"""
        summary_frame = ttk.LabelFrame(self.main_frame, text="Summary Statistics", padding="10")
        summary_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Configure grid for 4 columns
        for i in range(4):
            summary_frame.columnconfigure(i, weight=1)
        
        # Get statistics
        stats = self.results.get('statistics', {})
        
        # Create simple summary labels
        ttk.Label(summary_frame, text="Added", font=("Helvetica", 10, "bold")).grid(row=0, column=0)
        ttk.Label(summary_frame, text=str(stats.get('added_count', 0)), font=("Helvetica", 14)).grid(row=1, column=0)
        
        ttk.Label(summary_frame, text="Deleted", font=("Helvetica", 10, "bold")).grid(row=0, column=1)
        ttk.Label(summary_frame, text=str(stats.get('deleted_count', 0)), font=("Helvetica", 14)).grid(row=1, column=1)
        
        ttk.Label(summary_frame, text="Modified", font=("Helvetica", 10, "bold")).grid(row=0, column=2)
        ttk.Label(summary_frame, text=str(stats.get('modified_count', 0)), font=("Helvetica", 14)).grid(row=1, column=2)
        
        ttk.Label(summary_frame, text="Unchanged", font=("Helvetica", 10, "bold")).grid(row=0, column=3)
        ttk.Label(summary_frame, text=str(stats.get('unchanged_count', 0)), font=("Helvetica", 14)).grid(row=1, column=3)
    
    def _create_results_section(self):
        """Create results with tabs"""
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create tabs
        self._create_added_tab()
        self._create_deleted_tab()
        self._create_modified_tab()
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
        """Create modified requirements tab"""
        modified_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(modified_frame, text=f"Modified ({len(self.results.get('modified', []))})")
        self._create_requirements_tree(modified_frame, self.results.get('modified', []), "modified")
    
    def _create_unchanged_tab(self):
        """Create unchanged requirements tab"""
        unchanged_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(unchanged_frame, text=f"Unchanged ({len(self.results.get('unchanged', []))})")
        self._create_requirements_tree(unchanged_frame, self.results.get('unchanged', []), "unchanged")
    
    def _create_requirements_tree(self, parent, requirements: List[Dict], category: str):
        """Create treeview for requirements"""
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
        if category == "modified":
            columns.append('changes')
        
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
            elif col == 'changes':
                tree.column(col, width=200, minwidth=150)
            else:
                tree.column(col, width=150, minwidth=100)
        
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
                
                values = [title, description, req_type]
                
                if category == "modified":
                    changes = req.get('changes', {})
                    change_summary = ', '.join(changes.keys()) if changes else 'Unknown changes'
                    values.append(change_summary[:100])
                
                tree.insert('', 'end', text=req_id, values=values)
                
            except Exception as e:
                print(f"Error inserting {category} requirement {i}: {e}")
                continue
    
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
                self._show_requirement_details(req, category)
        except Exception as e:
            print(f"Error handling double-click: {e}")
    
    def _show_requirement_details(self, requirement: Dict, category: str):
        """Show detailed requirement information"""
        details_window = tk.Toplevel(self.window)
        details_window.title(f"Requirement Details - {category.title()}")
        details_window.geometry("600x500")
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
        
        # Populate details
        details_text.insert(tk.END, f"Category: {category.title()}\n\n")
        details_text.insert(tk.END, f"ID: {requirement.get('id', 'N/A')}\n\n")
        details_text.insert(tk.END, f"Title: {requirement.get('title', 'N/A')}\n\n")
        details_text.insert(tk.END, f"Description: {requirement.get('description', 'N/A')}\n\n")
        details_text.insert(tk.END, f"Type: {requirement.get('type', 'N/A')}\n\n")
        
        # Show changes for modified requirements
        if category == "modified" and 'changes' in requirement:
            details_text.insert(tk.END, "Changes:\n")
            for field, change in requirement['changes'].items():
                details_text.insert(tk.END, f"  {field}: {change}\n")
            details_text.insert(tk.END, "\n")
        
        # Show attributes
        attributes = requirement.get('attributes', {})
        if attributes:
            details_text.insert(tk.END, "Attributes:\n")
            for attr_name, attr_value in attributes.items():
                details_text.insert(tk.END, f"  {attr_name}: {attr_value}\n")
        
        details_text.configure(state=tk.DISABLED)
        
        # Close button
        ttk.Button(main_frame, text="Close", command=details_window.destroy).grid(
            row=2, column=0, pady=(15, 0))
    
    def _export_all_results(self):
        """Export all results to CSV"""
        try:
            filename = filedialog.asksaveasfilename(
                title="Export All Results",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialname="comparison_results_all.csv"
            )
            
            if not filename:
                return
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Category', 'ID', 'Title', 'Description', 'Type', 'Changes'])
                
                for category in ['added', 'deleted', 'modified', 'unchanged']:
                    requirements = self.results.get(category, [])
                    for req in requirements:
                        changes = ''
                        if category == 'modified' and 'changes' in req:
                            changes = ', '.join(req['changes'].keys())
                        
                        writer.writerow([
                            category.title(),
                            req.get('id', ''),
                            req.get('title', ''),
                            req.get('description', ''),
                            req.get('type', ''),
                            changes
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