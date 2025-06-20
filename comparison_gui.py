#!/usr/bin/env python3
"""
Comparison GUI Module
Handles the display of comparison results in a tabbed interface.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv
from typing import Dict, Any, List


class ComparisonResultsGUI:
    """GUI for displaying comparison results in a tabbed interface"""
    
    def __init__(self, parent_window, comparison_results: Dict[str, Any]):
        self.parent = parent_window
        self.results = comparison_results
        self.setup_gui()
        
    def setup_gui(self):
        """Create the comparison results GUI"""
        # Main frame
        main_frame = ttk.Frame(self.parent, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Comparison Results", 
                               font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # Statistics frame
        self.create_statistics_panel(main_frame)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Create tabs for each category
        self.create_added_tab()
        self.create_deleted_tab()
        self.create_modified_tab()
        self.create_unchanged_tab()
        
        # Export button frame
        export_frame = ttk.Frame(main_frame)
        export_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(export_frame, text="Export Results to CSV", 
                  command=self.export_to_csv).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(export_frame, text="Export Summary", 
                  command=self.export_summary).pack(side=tk.LEFT)
        
    def create_statistics_panel(self, parent):
        """Create the statistics summary panel"""
        stats_frame = ttk.LabelFrame(parent, text="Summary Statistics", padding="5")
        stats_frame.pack(fill=tk.X, pady=(0, 5))
        
        stats = self.results['statistics']
        
        # Create grid of statistics
        row = 0
        col = 0
        
        stat_items = [
            ("Original File:", f"{stats['total_file1']} requirements"),
            ("Modified File:", f"{stats['total_file2']} requirements"),
            ("Added:", f"{stats['added_count']} requirements"),
            ("Deleted:", f"{stats['deleted_count']} requirements"),
            ("Modified:", f"{stats['modified_count']} requirements"),
            ("Unchanged:", f"{stats['unchanged_count']} requirements"),
            ("Change Rate:", f"{stats['change_percentage']}%"),
        ]
        
        for label_text, value_text in stat_items:
            # Label
            ttk.Label(stats_frame, text=label_text, font=('Arial', 9, 'bold')).grid(
                row=row, column=col*2, sticky=tk.W, padx=(0, 5))
            # Value
            ttk.Label(stats_frame, text=value_text).grid(
                row=row, column=col*2+1, sticky=tk.W, padx=(0, 20))
            
            col += 1
            if col >= 3:  # 3 columns
                col = 0
                row += 1
    
    def create_added_tab(self):
        """Create tab for added requirements"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=f"Added ({len(self.results['added'])})")
        
        # Create treeview
        columns = ('ID', 'Title', 'Description', 'Type')
        tree = ttk.Treeview(frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        tree.heading('ID', text='Requirement ID')
        tree.heading('Title', text='Title')
        tree.heading('Description', text='Description')
        tree.heading('Type', text='Type')
        
        tree.column('ID', width=120)
        tree.column('Title', width=200)
        tree.column('Description', width=300)
        tree.column('Type', width=100)
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        h_scrollbar = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)
        
        # Populate with data
        for req in self.results['added']:
            tree.insert('', tk.END, values=(
                req.get('id', ''),
                req.get('title', '')[:50] + ('...' if len(req.get('title', '')) > 50 else ''),
                req.get('description', '')[:100] + ('...' if len(req.get('description', '')) > 100 else ''),
                req.get('type', '')
            ), tags=('added',))
        
        # Configure colors
        tree.tag_configure('added', background='#e8f5e8')
        
        # Bind double-click
        tree.bind('<Double-1>', lambda e: self.show_requirement_details(tree, self.results['added']))
        
    def create_deleted_tab(self):
        """Create tab for deleted requirements"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=f"Deleted ({len(self.results['deleted'])})")
        
        # Create treeview
        columns = ('ID', 'Title', 'Description', 'Type')
        tree = ttk.Treeview(frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        tree.heading('ID', text='Requirement ID')
        tree.heading('Title', text='Title')
        tree.heading('Description', text='Description')
        tree.heading('Type', text='Type')
        
        tree.column('ID', width=120)
        tree.column('Title', width=200)
        tree.column('Description', width=300)
        tree.column('Type', width=100)
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        h_scrollbar = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)
        
        # Populate with data
        for req in self.results['deleted']:
            tree.insert('', tk.END, values=(
                req.get('id', ''),
                req.get('title', '')[:50] + ('...' if len(req.get('title', '')) > 50 else ''),
                req.get('description', '')[:100] + ('...' if len(req.get('description', '')) > 100 else ''),
                req.get('type', '')
            ), tags=('deleted',))
        
        # Configure colors
        tree.tag_configure('deleted', background='#ffe8e8')
        
        # Bind double-click
        tree.bind('<Double-1>', lambda e: self.show_requirement_details(tree, self.results['deleted']))
        
    def create_modified_tab(self):
        """Create tab for modified requirements"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=f"Modified ({len(self.results['modified'])})")
        
        # Create treeview
        columns = ('ID', 'Title', 'Changes', 'Old_Title', 'New_Title')
        tree = ttk.Treeview(frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        tree.heading('ID', text='Requirement ID')
        tree.heading('Title', text='New Title')
        tree.heading('Changes', text='# Changes')
        tree.heading('Old_Title', text='Original Title')
        tree.heading('New_Title', text='Modified Title')
        
        tree.column('ID', width=120)
        tree.column('Title', width=200)
        tree.column('Changes', width=80)
        tree.column('Old_Title', width=200)
        tree.column('New_Title', width=200)
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        h_scrollbar = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)
        
        # Populate with data
        for mod in self.results['modified']:
            old_req = mod['old']
            new_req = mod['new']
            changes = mod['changes']
            
            tree.insert('', tk.END, values=(
                mod['id'],
                new_req.get('title', '')[:50] + ('...' if len(new_req.get('title', '')) > 50 else ''),
                len(changes),
                old_req.get('title', '')[:40] + ('...' if len(old_req.get('title', '')) > 40 else ''),
                new_req.get('title', '')[:40] + ('...' if len(new_req.get('title', '')) > 40 else '')
            ), tags=('modified',))
        
        # Configure colors
        tree.tag_configure('modified', background='#fff8e1')
        
        # Bind double-click
        tree.bind('<Double-1>', lambda e: self.show_modified_details(tree))
        
    def create_unchanged_tab(self):
        """Create tab for unchanged requirements"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=f"Unchanged ({len(self.results['unchanged'])})")
        
        # Create treeview
        columns = ('ID', 'Title', 'Description', 'Type')
        tree = ttk.Treeview(frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        tree.heading('ID', text='Requirement ID')
        tree.heading('Title', text='Title')
        tree.heading('Description', text='Description')
        tree.heading('Type', text='Type')
        
        tree.column('ID', width=120)
        tree.column('Title', width=200)
        tree.column('Description', width=300)
        tree.column('Type', width=100)
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        h_scrollbar = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)
        
        # Populate with data
        for req in self.results['unchanged']:
            tree.insert('', tk.END, values=(
                req.get('id', ''),
                req.get('title', '')[:50] + ('...' if len(req.get('title', '')) > 50 else ''),
                req.get('description', '')[:100] + ('...' if len(req.get('description', '')) > 100 else ''),
                req.get('type', '')
            ), tags=('unchanged',))
        
        # Configure colors
        tree.tag_configure('unchanged', background='white')
        
        # Bind double-click
        tree.bind('<Double-1>', lambda e: self.show_requirement_details(tree, self.results['unchanged']))
        
    def show_requirement_details(self, tree, requirements_list):
        """Show detailed view of a selected requirement"""
        selection = tree.selection()
        if not selection:
            return
            
        item = tree.item(selection[0])
        req_id = item['values'][0]
        
        # Find the requirement
        requirement = None
        for req in requirements_list:
            if req.get('id') == req_id:
                requirement = req
                break
                
        if not requirement:
            return
            
        # Create details window
        details_window = tk.Toplevel(self.parent)
        details_window.title(f"Requirement Details - {req_id}")
        details_window.geometry("600x500")
        
        # Create text widget with scrollbar
        text_frame = ttk.Frame(details_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget = tk.Text(text_frame, wrap=tk.WORD, font=('Consolas', 10))
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Format requirement details
        details = f"""Requirement ID: {requirement.get('id', 'N/A')}
Title: {requirement.get('title', 'N/A')}
Type: {requirement.get('type', 'N/A')}

Description:
{requirement.get('description', 'No description available')}

Attributes:
"""
        
        for attr_name, attr_value in requirement.get('attributes', {}).items():
            details += f"  {attr_name}: {attr_value}\n"
            
        text_widget.insert(tk.END, details)
        text_widget.configure(state=tk.DISABLED)
        
    def show_modified_details(self, tree):
        """Show detailed view of a modified requirement with changes"""
        selection = tree.selection()
        if not selection:
            return
            
        item = tree.item(selection[0])
        req_id = item['values'][0]
        
        # Find the modified requirement
        modified_req = None
        for mod in self.results['modified']:
            if mod['id'] == req_id:
                modified_req = mod
                break
                
        if not modified_req:
            return
            
        # Create details window
        details_window = tk.Toplevel(self.parent)
        details_window.title(f"Modified Requirement - {req_id}")
        details_window.geometry("800x600")
        
        # Create notebook for old/new comparison
        notebook = ttk.Notebook(details_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Original version tab
        old_frame = ttk.Frame(notebook)
        notebook.add(old_frame, text="Original Version")
        
        old_text = tk.Text(old_frame, wrap=tk.WORD, font=('Consolas', 10))
        old_scrollbar = ttk.Scrollbar(old_frame, orient=tk.VERTICAL, command=old_text.yview)
        old_text.configure(yscrollcommand=old_scrollbar.set)
        old_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        old_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Modified version tab
        new_frame = ttk.Frame(notebook)
        notebook.add(new_frame, text="Modified Version")
        
        new_text = tk.Text(new_frame, wrap=tk.WORD, font=('Consolas', 10))
        new_scrollbar = ttk.Scrollbar(new_frame, orient=tk.VERTICAL, command=new_text.yview)
        new_text.configure(yscrollcommand=new_scrollbar.set)
        new_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        new_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Changes summary tab
        changes_frame = ttk.Frame(notebook)
        notebook.add(changes_frame, text="Changes Summary")
        
        changes_text = tk.Text(changes_frame, wrap=tk.WORD, font=('Consolas', 10))
        changes_scrollbar = ttk.Scrollbar(changes_frame, orient=tk.VERTICAL, command=changes_text.yview)
        changes_text.configure(yscrollcommand=changes_scrollbar.set)
        changes_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        changes_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Populate old version
        old_req = modified_req['old']
        old_details = self._format_requirement_details(old_req)
        old_text.insert(tk.END, old_details)
        old_text.configure(state=tk.DISABLED)
        
        # Populate new version
        new_req = modified_req['new']
        new_details = self._format_requirement_details(new_req)
        new_text.insert(tk.END, new_details)
        new_text.configure(state=tk.DISABLED)
        
        # Populate changes
        changes_details = f"Changes Summary for {req_id}\n{'='*50}\n\n"
        for change in modified_req['changes']:
            changes_details += f"Field: {change['field']}\n"
            changes_details += f"Change Type: {change['change_type']}\n"
            changes_details += f"Old Value: {change['old_value']}\n"
            changes_details += f"New Value: {change['new_value']}\n"
            changes_details += "-" * 30 + "\n\n"
            
        changes_text.insert(tk.END, changes_details)
        changes_text.configure(state=tk.DISABLED)
        
    def _format_requirement_details(self, req):
        """Format requirement details for display"""
        details = f"""Requirement ID: {req.get('id', 'N/A')}
Title: {req.get('title', 'N/A')}
Type: {req.get('type', 'N/A')}

Description:
{req.get('description', 'No description available')}

Attributes:
"""
        
        for attr_name, attr_value in req.get('attributes', {}).items():
            details += f"  {attr_name}: {attr_value}\n"
            
        return details
        
    def export_to_csv(self):
        """Export comparison results to CSV file"""
        filename = filedialog.asksaveasfilename(
            title="Export Comparison Results",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if not filename:
            return
            
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                writer.writerow(['Category', 'ID', 'Title', 'Description', 'Type', 'Changes'])
                
                # Write added requirements
                for req in self.results['added']:
                    writer.writerow([
                        'ADDED',
                        req.get('id', ''),
                        req.get('title', ''),
                        req.get('description', ''),
                        req.get('type', ''),
                        ''
                    ])
                
                # Write deleted requirements
                for req in self.results['deleted']:
                    writer.writerow([
                        'DELETED',
                        req.get('id', ''),
                        req.get('title', ''),
                        req.get('description', ''),
                        req.get('type', ''),
                        ''
                    ])
                
                # Write modified requirements
                for mod in self.results['modified']:
                    changes_summary = f"{len(mod['changes'])} changes: " + \
                                    ", ".join([f"{c['field']}({c['change_type']})" for c in mod['changes']])
                    writer.writerow([
                        'MODIFIED',
                        mod['id'],
                        mod['new'].get('title', ''),
                        mod['new'].get('description', ''),
                        mod['new'].get('type', ''),
                        changes_summary
                    ])
                
                # Write unchanged requirements
                for req in self.results['unchanged']:
                    writer.writerow([
                        'UNCHANGED',
                        req.get('id', ''),
                        req.get('title', ''),
                        req.get('description', ''),
                        req.get('type', ''),
                        ''
                    ])
            
            messagebox.showinfo("Export Complete", f"Results exported to {filename}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export results:\n{str(e)}")
            
    def export_summary(self):
        """Export summary statistics to text file"""
        filename = filedialog.asksaveasfilename(
            title="Export Summary",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if not filename:
            return
            
        try:
            # Import comparator to use summary generation
            from reqif_comparator import ReqIFComparator
            comparator = ReqIFComparator()
            summary = comparator.export_comparison_summary(self.results)
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(summary)
            
            messagebox.showinfo("Export Complete", f"Summary exported to {filename}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export summary:\n{str(e)}")


# Example usage
if __name__ == "__main__":
    # This would normally be called from the main application
    print("Comparison GUI module loaded successfully.")