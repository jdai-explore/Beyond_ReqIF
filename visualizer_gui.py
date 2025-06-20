#!/usr/bin/env python3
"""
Visualizer GUI Module
Handles the display and exploration of requirements from a single ReqIF file.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv
from typing import Dict, Any, List
from collections import Counter

# Import tooltip functionality
try:
    from theme_manager import add_tooltip
except ImportError:
    # Fallback if theme_manager not available
    def add_tooltip(widget, text, delay=500):
        pass


class VisualizerGUI:
    """GUI for visualizing and exploring requirements from a single ReqIF file"""
    
    def __init__(self, parent_container, requirements: List[Dict[str, Any]], filename: str):
        self.parent = parent_container
        self.requirements = requirements
        self.filename = filename
        self.filtered_requirements = requirements.copy()
        
        # Search/filter state
        self.search_var = tk.StringVar()
        # Use try/except for trace method compatibility
        try:
            self.search_var.trace_add('write', self.on_search_change)
        except AttributeError:
            # Fallback for older tkinter versions
            self.search_var.trace('w', self.on_search_change)
        
        self.setup_gui()
        self.populate_requirements()
        self.update_statistics()
        
    def setup_gui(self):
        """Create the modern visualizer GUI"""
        # Main frame with professional styling
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header with file info and controls
        header_frame = ttk.Frame(main_frame, padding="10")
        header_frame.pack(fill=tk.X)
        header_frame.columnconfigure(1, weight=1)
        
        # File info with icon
        info_text = f"📄 {self.filename} | 📊 {len(self.requirements)} Requirements"
        info_label = ttk.Label(header_frame, text=info_text, font=('Arial', 11, 'bold'))
        info_label.grid(row=0, column=0, sticky=tk.W)
        
        # Control buttons
        controls_frame = ttk.Frame(header_frame)
        controls_frame.grid(row=0, column=2, sticky=tk.E)
        
        # Export button with icon
        export_btn = ttk.Button(controls_frame, text="📤 Export CSV", 
                               command=self.export_to_csv, style='Accent.TButton')
        export_btn.pack(side=tk.RIGHT, padx=(5, 0))
        add_tooltip(export_btn, "Export current view to CSV file")
        
        # Refresh button
        refresh_btn = ttk.Button(controls_frame, text="🔄", width=3,
                                command=self.refresh_view)
        refresh_btn.pack(side=tk.RIGHT, padx=(5, 0))
        add_tooltip(refresh_btn, "Refresh visualization")
        
        # Search section with enhanced styling
        search_frame = ttk.LabelFrame(main_frame, text="🔍 Search & Filter", padding="10")
        search_frame.pack(fill=tk.X, padx=10, pady=(5, 10))
        search_frame.columnconfigure(1, weight=1)
        
        ttk.Label(search_frame, text="Search:").grid(row=0, column=0, sticky=tk.W)
        
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=40, font=('Arial', 10))
        search_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 5))
        search_entry.focus()  # Focus on search by default
        add_tooltip(search_entry, "Search across all requirement fields (Ctrl+F)")
        
        # Search controls
        search_controls = ttk.Frame(search_frame)
        search_controls.grid(row=0, column=2, padx=(5, 0))
        
        clear_btn = ttk.Button(search_controls, text="❌", width=3, command=self.clear_search)
        clear_btn.pack(side=tk.LEFT, padx=(0, 5))
        add_tooltip(clear_btn, "Clear search (Esc)")
        
        # Search info label
        self.search_info_label = ttk.Label(search_frame, text="", font=('Arial', 9, 'italic'))
        self.search_info_label.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(5, 0))
        
        # Create enhanced notebook for different views
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Create tabs with icons
        self.create_table_tab()
        self.create_statistics_tab()
        
        # Bind search shortcut
        try:
            # Get root window for binding
            root = self.parent.winfo_toplevel()
            search_entry.bind('<Control-f>', lambda e: search_entry.focus())
            search_entry.bind('<Escape>', lambda e: self.clear_search())
        except:
            pass
            
    def create_table_tab(self):
        """Create the enhanced requirements table view"""
        table_frame = ttk.Frame(self.notebook)
        self.notebook.add(table_frame, text="📋 Requirements Table")
        
        # Determine columns based on actual data
        base_columns = ['ID', 'Title', 'Type', 'Description']
        
        # Find common attributes across requirements
        all_attributes = set()
        for req in self.requirements:
            all_attributes.update(req.get('attributes', {}).keys())
        
        # Add most common attributes as columns (limit to avoid too many columns)
        common_attrs = sorted(list(all_attributes))[:3]  # Show top 3 additional attributes
        columns = base_columns + common_attrs
        
        # Create treeview with enhanced styling
        tree_frame = ttk.Frame(table_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=20)
        
        # Configure base columns with icons
        self.tree.heading('ID', text='🆔 Requirement ID')
        self.tree.heading('Title', text='📝 Title')
        self.tree.heading('Type', text='🏷️ Type')
        self.tree.heading('Description', text='📄 Description')
        
        self.tree.column('ID', width=150, minwidth=100)
        self.tree.column('Title', width=250, minwidth=150)
        self.tree.column('Type', width=120, minwidth=80)
        self.tree.column('Description', width=300, minwidth=200)
        
        # Configure additional attribute columns
        for attr in common_attrs:
            self.tree.heading(attr, text=f'⚙️ {attr}')
            self.tree.column(attr, width=150, minwidth=100)
        
        # Add professional scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Bind events
        self.tree.bind('<Double-1>', self.show_requirement_details)
        self.tree.bind('<Button-3>', self.show_context_menu)  # Right-click
        
        # Status label for filtered results with enhanced styling
        status_frame = ttk.Frame(table_frame)
        status_frame.pack(fill=tk.X, padx=10, pady=(5, 10))
        
        self.status_label = ttk.Label(status_frame, text="", font=('Arial', 9, 'italic'))
        self.status_label.pack(side=tk.LEFT)
        
        # Quick stats in status area
        self.quick_stats_label = ttk.Label(status_frame, text="", font=('Arial', 9))
        self.quick_stats_label.pack(side=tk.RIGHT)
        
        # Store column info for population
        self.table_columns = columns
        self.common_attrs = common_attrs
        
    def show_context_menu(self, event):
        """Show context menu on right-click"""
        try:
            context_menu = tk.Menu(self.tree, tearoff=0)
            context_menu.add_command(label="📋 View Details", command=lambda: self.show_requirement_details(event))
            context_menu.add_separator()
            context_menu.add_command(label="📤 Export Selected", command=self.export_selected)
            context_menu.add_command(label="🔍 Search Similar", command=self.search_similar)
            
            # Show menu at cursor position
            context_menu.post(event.x_root, event.y_root)
        except Exception:
            pass  # Fail silently if context menu creation fails
            
    def export_selected(self):
        """Export selected requirement"""
        selection = self.tree.selection()
        if selection:
            messagebox.showinfo("Export", "Selected requirement export feature coming soon!")
            
    def search_similar(self):
        """Search for similar requirements"""
        selection = self.tree.selection()
        if selection:
            messagebox.showinfo("Search", "Similar requirements search feature coming soon!")
        
    def create_statistics_tab(self):
        """Create the statistics and analytics view"""
        stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(stats_frame, text="📊 Statistics")
        
        # Create scrollable frame for statistics
        canvas = tk.Canvas(stats_frame)
        scrollbar = ttk.Scrollbar(stats_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.stats_container = scrollable_frame
        
    def refresh_view(self):
        """Refresh the visualization"""
        self.populate_requirements()
        self.update_statistics()
        
    def populate_requirements(self):
        """Populate the requirements table with enhanced information"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add filtered requirements with enhanced data
        for req in self.filtered_requirements:
            # Build row values for all columns
            row_values = []
            
            # Base columns
            row_values.append(req.get('id', ''))
            
            # Title
            title = req.get('title', '')
            if len(title) > 50:
                title = title[:47] + "..."
            row_values.append(title)
            
            # Type
            req_type = req.get('type', req.get('type_ref', ''))
            if len(req_type) > 20:
                req_type = req_type[:17] + "..."
            row_values.append(req_type)
            
            # Description
            description = req.get('description', '')
            if len(description) > 100:
                description = description[:97] + "..."
            row_values.append(description)
            
            # Additional attribute columns
            if hasattr(self, 'common_attrs'):
                for attr in self.common_attrs:
                    attr_value = req.get('attributes', {}).get(attr, '')
                    if len(str(attr_value)) > 30:
                        attr_value = str(attr_value)[:27] + "..."
                    row_values.append(str(attr_value))
            
            # Insert with alternating row colors (if supported)
            item_id = self.tree.insert('', tk.END, values=row_values)
        
        # Update status with enhanced information
        total = len(self.requirements)
        showing = len(self.filtered_requirements)
        
        if total == showing:
            status_text = f"📊 Showing all {total} requirements"
        else:
            status_text = f"🔍 Showing {showing} of {total} requirements"
        self.status_label.config(text=status_text)
        
        # Update quick stats
        if hasattr(self, 'quick_stats_label'):
            with_desc = len([r for r in self.filtered_requirements if r.get('description')])
            with_type = len([r for r in self.filtered_requirements if r.get('type')])
            quick_stats = f"📝 {with_desc} with descriptions | 🏷️ {with_type} with types"
            self.quick_stats_label.config(text=quick_stats)
        
    def update_statistics(self):
        """Update the statistics display"""
        # Clear existing statistics
        for widget in self.stats_container.winfo_children():
            widget.destroy()
        
        # General statistics
        general_frame = ttk.LabelFrame(self.stats_container, text="📊 General Statistics", padding="10")
        general_frame.pack(fill=tk.X, pady=(0, 10))
        
        total_reqs = len(self.requirements)
        
        # Basic counts
        stats_text = f"Total Requirements: {total_reqs}\nCurrently Displayed: {len(self.filtered_requirements)}\n"
        
        # Count requirements with different attributes
        with_title = len([r for r in self.requirements if r.get('title')])
        with_description = len([r for r in self.requirements if r.get('description')])
        with_type = len([r for r in self.requirements if r.get('type')])
        
        stats_text += f"""
Completeness:
- With Title: {with_title} ({with_title/total_reqs*100:.1f}%)
- With Description: {with_description} ({with_description/total_reqs*100:.1f}%)
- With Type: {with_type} ({with_type/total_reqs*100:.1f}%)
"""
        
        ttk.Label(general_frame, text=stats_text, justify=tk.LEFT).pack(anchor=tk.W)
        
        # Type distribution
        if with_type > 0:
            type_frame = ttk.LabelFrame(self.stats_container, text="🏷️ Type Distribution", padding="10")
            type_frame.pack(fill=tk.X, pady=(0, 10))
            
            types = [r.get('type', 'Unknown') for r in self.requirements if r.get('type')]
            type_counts = Counter(types)
            
            type_text = "Requirement Types:\n"
            for req_type, count in type_counts.most_common():
                percentage = (count / total_reqs) * 100
                type_text += f"- {req_type}: {count} ({percentage:.1f}%)\n"
            
            ttk.Label(type_frame, text=type_text, justify=tk.LEFT).pack(anchor=tk.W)
        
        # Text analysis
        text_frame = ttk.LabelFrame(self.stats_container, text="📝 Text Analysis", padding="10")
        text_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Analyze description lengths
        descriptions = [r.get('description', '') for r in self.requirements if r.get('description')]
        if descriptions:
            desc_lengths = [len(desc) for desc in descriptions]
            avg_length = sum(desc_lengths) / len(desc_lengths)
            min_length = min(desc_lengths)
            max_length = max(desc_lengths)
            
            text_analysis = f"""Description Analysis:
- Average length: {avg_length:.1f} characters
- Shortest: {min_length} characters
- Longest: {max_length} characters
- Empty descriptions: {total_reqs - len(descriptions)}
"""
        else:
            text_analysis = "No descriptions found in requirements."
        
        ttk.Label(text_frame, text=text_analysis, justify=tk.LEFT).pack(anchor=tk.W)
        
        # Attribute analysis
        attr_frame = ttk.LabelFrame(self.stats_container, text="⚙️ Attribute Analysis", padding="10")
        attr_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Collect all unique attributes
        all_attributes = set()
        for req in self.requirements:
            all_attributes.update(req.get('attributes', {}).keys())
        
        if all_attributes:
            attr_text = f"Found {len(all_attributes)} unique attribute types:\n"
            for attr in sorted(all_attributes):
                # Count how many requirements have this attribute
                count = len([r for r in self.requirements 
                           if attr in r.get('attributes', {}) and r['attributes'][attr]])
                percentage = (count / total_reqs) * 100
                attr_text += f"- {attr}: {count} ({percentage:.1f}%)\n"
        else:
            attr_text = "No additional attributes found."
        
        ttk.Label(attr_frame, text=attr_text, justify=tk.LEFT).pack(anchor=tk.W)
        
    def on_search_change(self, *args):
        """Handle search text changes - compatible with both trace formats"""
        search_term = self.search_var.get().lower()
        
        if not search_term:
            self.filtered_requirements = self.requirements.copy()
            self.search_info_label.config(text="")
        else:
            # Filter requirements based on search term
            self.filtered_requirements = []
            for req in self.requirements:
                # Search in ID, title, description, type, and all attributes
                searchable_text = ' '.join([
                    req.get('id', ''),
                    req.get('title', ''),
                    req.get('description', ''),
                    req.get('type', ''),
                    ' '.join(str(v) for v in req.get('attributes', {}).values())
                ]).lower()
                
                if search_term in searchable_text:
                    self.filtered_requirements.append(req)
            
            # Update search info
            total = len(self.requirements)
            found = len(self.filtered_requirements)
            self.search_info_label.config(text=f"🔍 Found {found} of {total} requirements")
        
        self.populate_requirements()
        
    def clear_search(self):
        """Clear the search filter"""
        self.search_var.set("")
        
    def show_requirement_details(self, event):
        """Show detailed view of selected requirement"""
        selection = self.tree.selection()
        if not selection:
            return
            
        item = self.tree.item(selection[0])
        req_id = item['values'][0]
        
        # Find the requirement
        requirement = None
        for req in self.filtered_requirements:
            if req.get('id') == req_id:
                requirement = req
                break
                
        if not requirement:
            return
            
        # Create details window
        details_window = tk.Toplevel(self.parent)
        details_window.title(f"Requirement Details - {req_id}")
        details_window.geometry("700x600")
        
        # Create scrollable text widget
        main_frame = ttk.Frame(details_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create notebook for organized display
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Basic info tab
        basic_frame = ttk.Frame(notebook)
        notebook.add(basic_frame, text="Basic Information")
        
        basic_text = tk.Text(basic_frame, wrap=tk.WORD, font=('Consolas', 10))
        basic_scrollbar = ttk.Scrollbar(basic_frame, orient=tk.VERTICAL, command=basic_text.yview)
        basic_text.configure(yscrollcommand=basic_scrollbar.set)
        
        basic_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        basic_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Format basic information
        basic_info = f"""Requirement ID: {requirement.get('id', 'N/A')}
Title: {requirement.get('title', 'N/A')}
Type: {requirement.get('type', requirement.get('type_ref', 'N/A'))}

Description:
{requirement.get('description', 'No description available')}
"""
        
        if requirement.get('source_file'):
            basic_info += f"\nSource File: {requirement['source_file']}"
        
        # Add other mapped fields
        for field_name in ['priority', 'status']:
            if requirement.get(field_name):
                basic_info += f"\n{field_name.title()}: {requirement[field_name]}"
        
        basic_text.insert(tk.END, basic_info)
        basic_text.configure(state=tk.DISABLED)
        
        # All Attributes tab - show everything
        all_attr_frame = ttk.Frame(notebook)
        notebook.add(all_attr_frame, text="All Attributes")
        
        all_attr_text = tk.Text(all_attr_frame, wrap=tk.WORD, font=('Consolas', 10))
        all_attr_scrollbar = ttk.Scrollbar(all_attr_frame, orient=tk.VERTICAL, command=all_attr_text.yview)
        all_attr_text.configure(yscrollcommand=all_attr_scrollbar.set)
        
        all_attr_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        all_attr_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Show all parsed attributes
        all_attr_info = "All Parsed Attributes:\n" + "=" * 40 + "\n\n"
        
        # Show mapped attributes first
        mapped_attrs = requirement.get('attributes', {})
        if mapped_attrs:
            all_attr_info += "Mapped Attributes (Human Readable Names):\n" + "-" * 35 + "\n"
            for attr_name, attr_value in mapped_attrs.items():
                all_attr_info += f"{attr_name}:\n{attr_value}\n\n"
        
        # Show raw attributes
        raw_attrs = requirement.get('raw_attributes', {})
        if raw_attrs:
            all_attr_info += "\nRaw Attributes (Original References):\n" + "-" * 35 + "\n"
            for attr_ref, attr_value in raw_attrs.items():
                all_attr_info += f"{attr_ref}:\n{attr_value}\n\n"
        
        if not mapped_attrs and not raw_attrs:
            all_attr_info += "No additional attributes found."
        
        all_attr_text.insert(tk.END, all_attr_info)
        all_attr_text.configure(state=tk.DISABLED)
        
        # Technical Details tab
        tech_frame = ttk.Frame(notebook)
        notebook.add(tech_frame, text="Technical Details")
        
        tech_text = tk.Text(tech_frame, wrap=tk.WORD, font=('Consolas', 10))
        tech_scrollbar = ttk.Scrollbar(tech_frame, orient=tk.VERTICAL, command=tech_text.yview)
        tech_text.configure(yscrollcommand=tech_scrollbar.set)
        
        tech_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tech_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Technical information
        tech_info = f"""Technical Information:
{'=' * 30}

Identifier: {requirement.get('identifier', 'N/A')}
Type Reference: {requirement.get('type_ref', 'N/A')}
Content Hash: {requirement.get('content', 'N/A')[:100]}...

Raw Data Structure:
{'-' * 20}
"""
        
        # Show the raw requirement dictionary (excluding large content)
        req_copy = requirement.copy()
        if 'content' in req_copy and len(req_copy['content']) > 200:
            req_copy['content'] = req_copy['content'][:200] + "... (truncated)"
        
        import json
        try:
            tech_info += json.dumps(req_copy, indent=2, ensure_ascii=False)
        except:
            tech_info += str(req_copy)
        
        tech_text.insert(tk.END, tech_info)
        tech_text.configure(state=tk.DISABLED)
        
    def export_to_csv(self):
        """Export current requirements view to CSV"""
        if not self.filtered_requirements:
            messagebox.showwarning("Warning", "No requirements to export.")
            return
            
        filename = filedialog.asksaveasfilename(
            title="Export Requirements to CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialname=f"{self.filename.replace('.reqif', '').replace('.reqifz', '')}_requirements.csv"
        )
        
        if not filename:
            return
            
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                headers = ['ID', 'Title', 'Description', 'Type']
                
                # Add attribute columns if any requirements have attributes
                all_attributes = set()
                for req in self.filtered_requirements:
                    all_attributes.update(req.get('attributes', {}).keys())
                
                headers.extend(sorted(all_attributes))
                if any(req.get('source_file') for req in self.filtered_requirements):
                    headers.append('Source_File')
                
                writer.writerow(headers)
                
                # Write requirements
                for req in self.filtered_requirements:
                    row = [
                        req.get('id', ''),
                        req.get('title', ''),
                        req.get('description', ''),
                        req.get('type', '')
                    ]
                    
                    # Add attribute values
                    for attr in sorted(all_attributes):
                        row.append(req.get('attributes', {}).get(attr, ''))
                    
                    # Add source file if present
                    if 'Source_File' in headers:
                        row.append(req.get('source_file', ''))
                    
                    writer.writerow(row)
            
            count = len(self.filtered_requirements)
            messagebox.showinfo("Export Complete", 
                              f"Successfully exported {count} requirements to {filename}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export requirements:\n{str(e)}")
    
    def get_summary(self):
        """Get a text summary of the visualized requirements"""
        total = len(self.requirements)
        displayed = len(self.filtered_requirements)
        
        # Type distribution
        types = [r.get('type', 'Unknown') for r in self.requirements if r.get('type')]
        type_counts = Counter(types)
        
        summary = f"""ReqIF File Visualization Summary
================================

File: {self.filename}
Total Requirements: {total}
Currently Displayed: {displayed}

Completeness Analysis:
- With Title: {len([r for r in self.requirements if r.get('title')])} ({len([r for r in self.requirements if r.get('title')])/total*100:.1f}%)
- With Description: {len([r for r in self.requirements if r.get('description')])} ({len([r for r in self.requirements if r.get('description')])/total*100:.1f}%)
- With Type: {len([r for r in self.requirements if r.get('type')])} ({len([r for r in self.requirements if r.get('type')])/total*100:.1f}%)

"""
        
        if type_counts:
            summary += "Type Distribution:\n"
            for req_type, count in type_counts.most_common():
                percentage = (count / total) * 100
                summary += f"- {req_type}: {count} ({percentage:.1f}%)\n"
        
        return summary


# Example usage
if __name__ == "__main__":
    # This would normally be called from the main application
    print("Visualizer GUI module loaded successfully.")