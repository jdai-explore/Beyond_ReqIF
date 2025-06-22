#!/usr/bin/env python3
"""
Cleaned VisualizerGUI - Simple Theme Integration
Performance optimized with minimal theme dependencies.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import os
from typing import List, Dict, Any, Optional

# Simple theme import
from theme_manager import apply_theme, get_color


class VisualizerGUI:
    """
    Requirements Visualizer GUI with simple theme integration
    """
    
    def __init__(self, parent: tk.Widget, requirements: List[Dict[str, Any]], filename: str):
        self.parent = parent
        self.requirements = requirements
        self.filename = filename
        self.filtered_requirements = requirements.copy()
        
        # Create independent window
        self.window = tk.Toplevel(parent)
        self.window.title(f"Requirements Analysis - {os.path.basename(filename)}")
        self.window.geometry("1200x800")
        
        # Ensure window independence
        self.window.transient(parent)
        self.window.focus_set()
        
        # Apply simple theme
        apply_theme(widget=self.window)
        
        # Search and filter state
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._on_search_change)
        
        # Column management
        self.visible_columns = []
        
        # Statistics
        self.stats = self._calculate_statistics()
        
        # Setup GUI
        self.setup_gui()
        
        # Populate data
        self.populate_data()
        
        # Handle window closing
        self.window.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def setup_gui(self):
        """Setup GUI using grid geometry manager"""
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
        self._create_control_section()
        self._create_content_section()
        self._create_status_section()
    
    def _create_header_section(self):
        """Create header with file info and search"""
        header_frame = ttk.Frame(self.main_frame)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        header_frame.columnconfigure(1, weight=1)
        
        # File info
        info_frame = ttk.Frame(header_frame)
        info_frame.grid(row=0, column=0, sticky=(tk.W))
        
        title_label = ttk.Label(
            info_frame,
            text="📊 Requirements Analysis",
            font=("Helvetica", 16, "bold")
        )
        title_label.grid(row=0, column=0, sticky=(tk.W))
        
        file_label = ttk.Label(
            info_frame,
            text=f"File: {os.path.basename(self.filename)}",
            font=("Helvetica", 10)
        )
        file_label.grid(row=1, column=0, sticky=(tk.W), pady=(2, 0))
        
        count_label = ttk.Label(
            info_frame,
            text=f"Total Requirements: {len(self.requirements)}",
            font=("Helvetica", 10),
            foreground=get_color("success")
        )
        count_label.grid(row=2, column=0, sticky=(tk.W), pady=(2, 0))
        
        # Search section
        search_frame = ttk.Frame(header_frame)
        search_frame.grid(row=0, column=1, sticky=(tk.E), padx=(20, 0))
        
        ttk.Label(search_frame, text="🔍 Search:", font=("Helvetica", 10, "bold")).grid(
            row=0, column=0, sticky=(tk.W), padx=(0, 8))
        
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.grid(row=0, column=1, sticky=(tk.W))
        
        clear_btn = ttk.Button(search_frame, text="❌", width=3, command=self._clear_search)
        clear_btn.grid(row=0, column=2, padx=(8, 0))
    
    def _create_control_section(self):
        """Create control buttons and options"""
        control_frame = ttk.Frame(self.main_frame)
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        control_frame.columnconfigure(3, weight=1)
        
        # View controls
        view_frame = ttk.LabelFrame(control_frame, text="📋 View", padding="8")
        view_frame.grid(row=0, column=0, sticky=(tk.W), padx=(0, 15))
        
        ttk.Button(view_frame, text="📊 Statistics", command=self._show_statistics).grid(
            row=0, column=0, padx=(0, 8))
        
        ttk.Button(view_frame, text="🔄 Refresh", command=self._refresh_view).grid(
            row=0, column=1)
        
        # Export controls
        export_frame = ttk.LabelFrame(control_frame, text="💾 Export", padding="8")
        export_frame.grid(row=0, column=1, sticky=(tk.W), padx=(0, 15))
        
        ttk.Button(export_frame, text="📄 Export CSV", command=self._export_csv).grid(
            row=0, column=0, padx=(0, 8))
        
        ttk.Button(export_frame, text="📋 Copy Selected", command=self._copy_selected).grid(
            row=0, column=1)
        
        # Filter info
        self.filter_info_label = ttk.Label(
            control_frame,
            text=f"Showing: {len(self.filtered_requirements)} of {len(self.requirements)} requirements"
        )
        self.filter_info_label.grid(row=0, column=4, sticky=(tk.E))
    
    def _create_content_section(self):
        """Create main content area with treeview"""
        content_frame = ttk.Frame(self.main_frame)
        content_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(0, weight=1)
        
        # Create treeview with scrollbars
        tree_frame = ttk.Frame(content_frame)
        tree_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # Treeview
        self.tree = ttk.Treeview(tree_frame, selectmode='extended')
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=v_scrollbar.set)
        
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.tree.configure(xscrollcommand=h_scrollbar.set)
        
        # Bind events
        self.tree.bind('<Double-1>', self._on_double_click)
        self.tree.bind('<Button-1>', self._on_click)
    
    def _create_status_section(self):
        """Create status bar"""
        status_frame = ttk.Frame(self.main_frame)
        status_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(15, 0))
        status_frame.columnconfigure(1, weight=1)
        
        self.status_label = ttk.Label(status_frame, text="✅ Ready")
        self.status_label.grid(row=0, column=0, sticky=(tk.W))
        
        # Selection info
        self.selection_label = ttk.Label(status_frame, text="")
        self.selection_label.grid(row=0, column=2, sticky=(tk.E))
    
    def populate_data(self):
        """Populate treeview with requirements data"""
        try:
            # Determine optimal columns
            self._determine_optimal_columns()
            
            # Configure treeview columns
            self._configure_treeview_columns()
            
            # Insert data
            self._insert_requirements_data()
            
            # Update status
            self.status_label.configure(text="✅ Data loaded successfully")
            
        except Exception as e:
            self.status_label.configure(text=f"❌ Error loading data: {str(e)}")
            messagebox.showerror("Data Loading Error", f"Failed to load requirements data:\n{str(e)}")
    
    def _determine_optimal_columns(self):
        """Determine which columns to show based on data quality"""
        if not self.requirements:
            self.visible_columns = ['id', 'title', 'description']
            return
        
        # Analyze column content quality
        column_scores = {}
        
        # Standard columns
        standard_columns = ['id', 'title', 'description', 'type', 'priority', 'status']
        
        for col in standard_columns:
            filled_count = sum(1 for req in self.requirements if req.get(col, '').strip())
            column_scores[col] = filled_count / len(self.requirements)
        
        # Attribute columns
        attribute_columns = {}
        for req in self.requirements:
            for attr_name, attr_value in req.get('attributes', {}).items():
                if attr_value and str(attr_value).strip():
                    if attr_name not in attribute_columns:
                        attribute_columns[attr_name] = 0
                    attribute_columns[attr_name] += 1
        
        # Convert to scores
        for attr_name, count in attribute_columns.items():
            column_scores[f"attr_{attr_name}"] = count / len(self.requirements)
        
        # Select best columns
        sorted_columns = sorted(column_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Always include ID and title
        self.visible_columns = ['id', 'title']
        
        # Add other high-quality columns
        for col_name, score in sorted_columns:
            if col_name not in self.visible_columns and score > 0.1:
                self.visible_columns.append(col_name)
                if len(self.visible_columns) >= 8:
                    break
        
        # Ensure description is included
        if 'description' not in self.visible_columns:
            self.visible_columns.insert(2, 'description')
    
    def _configure_treeview_columns(self):
        """Configure treeview columns"""
        # Configure columns
        self.tree['columns'] = self.visible_columns[1:]
        self.tree['show'] = 'tree headings'
        
        # Configure tree column
        self.tree.heading('#0', text=self.visible_columns[0].title(), anchor=tk.W)
        self.tree.column('#0', width=100, minwidth=50)
        
        # Configure other columns
        for col in self.visible_columns[1:]:
            display_name = col.replace('attr_', '').replace('_', ' ').title()
            self.tree.heading(col, text=display_name, anchor=tk.W)
            
            # Set column width
            if 'description' in col.lower():
                width = 300
            elif 'id' in col.lower():
                width = 120
            else:
                width = 150
                
            self.tree.column(col, width=width, minwidth=50)
    
    def _insert_requirements_data(self):
        """Insert requirements data into treeview"""
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Insert filtered requirements
        for i, req in enumerate(self.filtered_requirements):
            try:
                # Get values for visible columns
                tree_value = str(req.get(self.visible_columns[0], f"REQ_{i}"))
                values = []
                
                for col in self.visible_columns[1:]:
                    if col.startswith('attr_'):
                        attr_name = col[5:]
                        value = req.get('attributes', {}).get(attr_name, '')
                    else:
                        value = req.get(col, '')
                    
                    # Clean and truncate value
                    value_str = str(value).strip()
                    if len(value_str) > 100:
                        value_str = value_str[:97] + "..."
                    values.append(value_str)
                
                # Insert item with requirement index as tag
                item_id = self.tree.insert('', 'end', text=tree_value, values=values, tags=[f"req_{i}"])
                
            except Exception as e:
                print(f"Error inserting requirement {i}: {e}")
                continue
    
    def _calculate_statistics(self):
        """Calculate statistics about the requirements"""
        if not self.requirements:
            return {}
        
        stats = {
            'total_count': len(self.requirements),
            'with_titles': sum(1 for req in self.requirements if req.get('title', '').strip()),
            'with_descriptions': sum(1 for req in self.requirements if req.get('description', '').strip()),
            'with_types': sum(1 for req in self.requirements if req.get('type', '').strip()),
            'attribute_count': 0,
            'unique_types': set(),
            'avg_attributes_per_req': 0
        }
        
        total_attributes = 0
        for req in self.requirements:
            attrs = req.get('attributes', {})
            total_attributes += len([v for v in attrs.values() if v and str(v).strip()])
            
            req_type = req.get('type', '').strip()
            if req_type:
                stats['unique_types'].add(req_type)
        
        stats['attribute_count'] = total_attributes
        stats['avg_attributes_per_req'] = total_attributes / len(self.requirements) if self.requirements else 0
        stats['unique_types'] = list(stats['unique_types'])
        
        return stats
    
    def _on_search_change(self, *args):
        """Handle search text changes"""
        search_text = self.search_var.get().lower().strip()
        
        if not search_text:
            self.filtered_requirements = self.requirements.copy()
        else:
            self.filtered_requirements = []
            for req in self.requirements:
                # Search in main fields
                searchable_text = ' '.join([
                    str(req.get('id', '')),
                    str(req.get('title', '')),
                    str(req.get('description', '')),
                    str(req.get('type', ''))
                ]).lower()
                
                # Search in attributes
                for attr_value in req.get('attributes', {}).values():
                    searchable_text += ' ' + str(attr_value).lower()
                
                if search_text in searchable_text:
                    self.filtered_requirements.append(req)
        
        # Update display
        self._insert_requirements_data()
        self._update_filter_info()
    
    def _clear_search(self):
        """Clear search filter"""
        self.search_var.set('')
    
    def _update_filter_info(self):
        """Update filter information display"""
        self.filter_info_label.configure(
            text=f"Showing: {len(self.filtered_requirements)} of {len(self.requirements)} requirements"
        )
    
    def _refresh_view(self):
        """Refresh the view"""
        self.populate_data()
        self.status_label.configure(text="🔄 View refreshed")
    
    def _show_statistics(self):
        """Show statistics dialog"""
        stats_window = tk.Toplevel(self.window)
        stats_window.title("Requirements Statistics")
        stats_window.geometry("450x500")
        stats_window.transient(self.window)
        
        # Apply theme
        apply_theme(widget=stats_window)
        
        # Configure grid
        stats_window.columnconfigure(0, weight=1)
        stats_window.rowconfigure(0, weight=1)
        
        main_frame = ttk.Frame(stats_window, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        ttk.Label(main_frame, text="📊 Requirements Statistics", 
                 font=("Helvetica", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 15))
        
        # Statistics
        row = 1
        stats_data = [
            ("Total Requirements", self.stats['total_count']),
            ("With Titles", f"{self.stats['with_titles']} ({self.stats['with_titles']/self.stats['total_count']*100:.1f}%)"),
            ("With Descriptions", f"{self.stats['with_descriptions']} ({self.stats['with_descriptions']/self.stats['total_count']*100:.1f}%)"),
            ("With Types", f"{self.stats['with_types']} ({self.stats['with_types']/self.stats['total_count']*100:.1f}%)"),
            ("Total Attributes", self.stats['attribute_count']),
            ("Avg Attributes/Req", f"{self.stats['avg_attributes_per_req']:.1f}"),
            ("Unique Types", len(self.stats['unique_types']))
        ]
        
        for label, value in stats_data:
            ttk.Label(main_frame, text=f"{label}:", font=("Helvetica", 10, "bold")).grid(
                row=row, column=0, sticky=(tk.W), pady=3)
            ttk.Label(main_frame, text=str(value)).grid(
                row=row, column=1, sticky=(tk.W), padx=(20, 0), pady=3)
            row += 1
        
        # Types list
        if self.stats['unique_types']:
            ttk.Label(main_frame, text="Requirement Types:", 
                     font=("Helvetica", 10, "bold")).grid(row=row, column=0, columnspan=2, sticky=(tk.W), pady=(15, 5))
            row += 1
            
            types_frame = ttk.Frame(main_frame)
            types_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
            
            types_text = tk.Text(types_frame, height=8, width=50)
            types_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            types_scroll = ttk.Scrollbar(types_frame, orient=tk.VERTICAL, command=types_text.yview)
            types_scroll.pack(side=tk.RIGHT, fill=tk.Y)
            types_text.configure(yscrollcommand=types_scroll.set)
            
            for req_type in sorted(self.stats['unique_types']):
                types_text.insert(tk.END, f"• {req_type}\n")
            types_text.configure(state=tk.DISABLED)
        
        # Close button
        ttk.Button(main_frame, text="Close", command=stats_window.destroy).grid(
            row=row+1, column=0, columnspan=2, pady=(15, 0))
    
    def _export_csv(self):
        """Export filtered requirements to CSV"""
        if not self.filtered_requirements:
            messagebox.showwarning("No Data", "No requirements to export.")
            return
        
        try:
            # Use a safer approach for file dialog on macOS
            filename = None
            try:
                filename = filedialog.asksaveasfilename(
                    title="Export Requirements to CSV",
                    defaultextension=".csv",
                    filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                    initialname=f"requirements_export_{len(self.filtered_requirements)}_items.csv"
                )
            except Exception as dialog_error:
                print(f"File dialog error: {dialog_error}")
                # Fallback: create a default filename
                import datetime
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"requirements_export_{timestamp}.csv"
                
                # Ask user to confirm the filename
                response = messagebox.askyesno(
                    "Export with Default Name", 
                    f"File dialog had an issue. Export to:\n{filename}?"
                )
                if not response:
                    return
            
            if not filename:
                return
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                # Determine all columns
                all_columns = set(['id', 'title', 'description', 'type', 'priority', 'status'])
                for req in self.filtered_requirements:
                    all_columns.update(req.keys())
                    all_columns.update(req.get('attributes', {}).keys())
                
                all_columns = sorted(list(all_columns))
                
                writer = csv.DictWriter(csvfile, fieldnames=all_columns)
                writer.writeheader()
                
                for req in self.filtered_requirements:
                    row = {}
                    for col in all_columns:
                        if col in req:
                            row[col] = req[col]
                        elif col in req.get('attributes', {}):
                            row[col] = req['attributes'][col]
                        else:
                            row[col] = ''
                    writer.writerow(row)
            
            messagebox.showinfo("Export Complete", 
                               f"Successfully exported {len(self.filtered_requirements)} requirements to:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export CSV:\n{str(e)}")
    
    def _copy_selected(self):
        """Copy selected requirements to clipboard"""
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select requirements to copy.")
            return
        
        try:
            # Build text representation
            text_lines = []
            text_lines.append('\t'.join(self.visible_columns))
            
            for item_id in selected_items:
                values = [self.tree.item(item_id, 'text')]
                values.extend(self.tree.item(item_id, 'values'))
                text_lines.append('\t'.join(str(v) for v in values))
            
            # Copy to clipboard
            self.window.clipboard_clear()
            self.window.clipboard_append('\n'.join(text_lines))
            
            self.status_label.configure(text=f"✅ Copied {len(selected_items)} requirements to clipboard")
            
        except Exception as e:
            messagebox.showerror("Copy Error", f"Failed to copy to clipboard:\n{str(e)}")
    
    def _on_double_click(self, event):
        """Handle double-click on requirement"""
        item_id = self.tree.selection()[0] if self.tree.selection() else None
        if item_id:
            self._show_requirement_details(item_id)
    
    def _on_click(self, event):
        """Handle single click to update selection info"""
        selected_count = len(self.tree.selection())
        if selected_count == 0:
            self.selection_label.configure(text="")
        elif selected_count == 1:
            self.selection_label.configure(text="1 requirement selected")
        else:
            self.selection_label.configure(text=f"{selected_count} requirements selected")
    
    def _show_requirement_details(self, item_id):
        """Show detailed requirement information"""
        try:
            # Get requirement index from tags
            tags = self.tree.item(item_id, 'tags')
            req_index = None
            for tag in tags:
                if tag.startswith('req_'):
                    req_index = int(tag[4:])
                    break
            
            if req_index is None or req_index >= len(self.filtered_requirements):
                messagebox.showerror("Error", "Could not find requirement data.")
                return
            
            # Get requirement data
            req = self.filtered_requirements[req_index]
            req_text = self.tree.item(item_id, 'text')
            
            # Create details window
            details_window = tk.Toplevel(self.window)
            details_window.title(f"Requirement Details - {req_text}")
            details_window.geometry("600x500")
            details_window.transient(self.window)
            
            # Apply theme
            apply_theme(widget=details_window)
            
            # Configure grid
            details_window.columnconfigure(0, weight=1)
            details_window.rowconfigure(0, weight=1)
            
            main_frame = ttk.Frame(details_window, padding="20")
            main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            main_frame.columnconfigure(0, weight=1)
            main_frame.rowconfigure(1, weight=1)
            
            # Title
            ttk.Label(main_frame, text=f"📋 {req_text}", 
                     font=("Helvetica", 14, "bold")).grid(row=0, column=0, sticky=(tk.W), pady=(0, 15))
            
            # Details in scrollable text
            text_frame = ttk.Frame(main_frame)
            text_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            text_frame.columnconfigure(0, weight=1)
            text_frame.rowconfigure(0, weight=1)
            
            details_text = tk.Text(text_frame, wrap=tk.WORD)
            details_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            
            scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=details_text.yview)
            scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
            details_text.configure(yscrollcommand=scrollbar.set)
            
            # Populate details with actual requirement data
            details_text.insert(tk.END, f"ID: {req.get('id', 'N/A')}\n\n")
            details_text.insert(tk.END, f"Title: {req.get('title', 'N/A')}\n\n")
            details_text.insert(tk.END, f"Description: {req.get('description', 'N/A')}\n\n")
            details_text.insert(tk.END, f"Type: {req.get('type', 'N/A')}\n\n")
            details_text.insert(tk.END, f"Priority: {req.get('priority', 'N/A')}\n\n")
            details_text.insert(tk.END, f"Status: {req.get('status', 'N/A')}\n\n")
            
            # Add attributes
            attributes = req.get('attributes', {})
            if attributes:
                details_text.insert(tk.END, "Attributes:\n")
                for attr_name, attr_value in attributes.items():
                    details_text.insert(tk.END, f"  {attr_name}: {attr_value}\n")
            
            details_text.configure(state=tk.DISABLED)
            
            # Close button
            ttk.Button(main_frame, text="Close", command=details_window.destroy).grid(
                row=2, column=0, pady=(15, 0))
            
        except Exception as e:
            messagebox.showerror("Details Error", f"Failed to show requirement details:\n{str(e)}")
    
    def _on_closing(self):
        """Handle window closing"""
        try:
            self.window.destroy()
        except:
            pass


# Example usage
if __name__ == "__main__":
    print("🔧 Cleaned VisualizerGUI - Performance Optimized")
    print("✅ Key features:")
    print("  - Simple theme integration")
    print("  - Fast, clean interface")
    print("  - Full visualization functionality")
    print("  - Professional appearance")