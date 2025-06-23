#!/usr/bin/env python3
"""
VisualizerGUI - Simplified Version
Removed all Apple theme dependencies, basic styling only
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import os
from typing import List, Dict, Any, Optional


class VisualizerGUI:
    """
    Simplified Requirements Visualizer GUI
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
        self.window.configure(bg='#FFFFFF')
        
        # Ensure window independence
        self.window.transient(parent)
        self.window.focus_set()
        
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
        """Setup simplified GUI"""
        # Create main container
        self.main_frame = tk.Frame(self.window, bg='#FFFFFF', padx=15, pady=15)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create sections
        self._create_header_section()
        self._create_control_section()
        self._create_content_section()
        self._create_status_section()
    
    def _create_header_section(self):
        """Create header with file info and search"""
        header_frame = tk.Frame(self.main_frame, bg='#FFFFFF')
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        # File info
        info_frame = tk.Frame(header_frame, bg='#FFFFFF')
        info_frame.pack(side=tk.LEFT)
        
        title_label = tk.Label(info_frame, text="Requirements Analysis", 
                              font=('Arial', 16, 'bold'), bg='#FFFFFF', fg='#000000')
        title_label.pack(anchor=tk.W)
        
        file_label = tk.Label(info_frame, text=f"File: {os.path.basename(self.filename)}",
                             font=('Arial', 10), bg='#FFFFFF', fg='#666666')
        file_label.pack(anchor=tk.W, pady=(2, 0))
        
        count_label = tk.Label(info_frame, text=f"Total Requirements: {len(self.requirements)}",
                              font=('Arial', 10), bg='#FFFFFF', fg='#666666')
        count_label.pack(anchor=tk.W, pady=(2, 0))
        
        # Search section
        search_frame = tk.Frame(header_frame, bg='#FFFFFF')
        search_frame.pack(side=tk.RIGHT, padx=(20, 0))
        
        tk.Label(search_frame, text="Search:", font=('Arial', 10, 'bold'), 
                bg='#FFFFFF', fg='#000000').pack(side=tk.LEFT, padx=(0, 8))
        
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, width=30, font=('Arial', 10))
        search_entry.pack(side=tk.LEFT)
        
        clear_btn = tk.Button(search_frame, text="Clear", width=8, command=self._clear_search,
                             bg='#F0F0F0', fg='#000000', font=('Arial', 10),
                             relief='solid', borderwidth=1, padx=10, pady=2,
                             activebackground='#E0E0E0', activeforeground='#000000')
        clear_btn.pack(side=tk.LEFT, padx=(8, 0))
    
    def _create_control_section(self):
        """Create control buttons"""
        control_frame = tk.Frame(self.main_frame, bg='#FFFFFF')
        control_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Buttons
        tk.Button(control_frame, text="Statistics", command=self._show_statistics,
                 bg='#0078D4', fg='white', font=('Arial', 10),
                 relief='flat', borderwidth=0, padx=15, pady=5,
                 activebackground='#005A9E', activeforeground='white').pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(control_frame, text="Export CSV", command=self._export_csv,
                 bg='#0078D4', fg='white', font=('Arial', 10),
                 relief='flat', borderwidth=0, padx=15, pady=5,
                 activebackground='#005A9E', activeforeground='white').pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(control_frame, text="Refresh", command=self._refresh_view,
                 bg='#F0F0F0', fg='#000000', font=('Arial', 10),
                 relief='solid', borderwidth=1, padx=15, pady=5,
                 activebackground='#E0E0E0', activeforeground='#000000').pack(side=tk.LEFT, padx=(0, 20))
        
        # Filter info
        self.filter_info_label = tk.Label(control_frame,
                                         text=f"Showing: {len(self.filtered_requirements)} of {len(self.requirements)} requirements",
                                         font=('Arial', 10), bg='#FFFFFF', fg='#666666')
        self.filter_info_label.pack(side=tk.RIGHT)
    
    def _create_content_section(self):
        """Create main content area with treeview"""
        content_frame = tk.Frame(self.main_frame, bg='#FFFFFF')
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview with scrollbars
        tree_frame = tk.Frame(content_frame, bg='#FFFFFF')
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview
        self.tree = ttk.Treeview(tree_frame, selectmode='extended')
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=v_scrollbar.set)
        
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.configure(xscrollcommand=h_scrollbar.set)
        
        # Bind events
        self.tree.bind('<Double-1>', self._on_double_click)
        self.tree.bind('<Button-1>', self._on_click)
    
    def _create_status_section(self):
        """Create status bar"""
        status_frame = tk.Frame(self.main_frame, bg='#F0F0F0', relief='sunken', bd=1)
        status_frame.pack(fill=tk.X, pady=(15, 0))
        
        self.status_label = tk.Label(status_frame, text="Ready", font=('Arial', 10), 
                                    bg='#F0F0F0', fg='#000000')
        self.status_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Selection info
        self.selection_label = tk.Label(status_frame, text="", font=('Arial', 10), 
                                       bg='#F0F0F0', fg='#666666')
        self.selection_label.pack(side=tk.RIGHT, padx=10, pady=5)
    
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
            self.status_label.configure(text="Data loaded successfully")
            
        except Exception as e:
            self.status_label.configure(text=f"Error loading data: {str(e)}")
            messagebox.showerror("Data Loading Error", f"Failed to load requirements data:\n{str(e)}")
    
    def _determine_optimal_columns(self):
        """Determine which columns to show"""
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
        self.status_label.configure(text="View refreshed")
    
    def _show_statistics(self):
        """Show statistics dialog"""
        stats_window = tk.Toplevel(self.window)
        stats_window.title("Requirements Statistics")
        stats_window.geometry("450x400")
        stats_window.configure(bg='#FFFFFF')
        stats_window.transient(self.window)
        
        main_frame = tk.Frame(stats_window, bg='#FFFFFF', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        tk.Label(main_frame, text="Requirements Statistics", 
                font=('Arial', 14, 'bold'), bg='#FFFFFF', fg='#000000').pack(pady=(0, 15))
        
        # Statistics
        stats_data = [
            ("Total Requirements", self.stats['total_count']),
            ("With Titles", f"{self.stats['with_titles']} ({self.stats['with_titles']/self.stats['total_count']*100:.1f}%)"),
            ("With Descriptions", f"{self.stats['with_descriptions']} ({self.stats['with_descriptions']/self.stats['total_count']*100:.1f}%)"),
            ("With Types", f"{self.stats['with_types']} ({self.stats['with_types']/self.stats['total_count']*100:.1f}%)"),
            ("Total Attributes", self.stats['attribute_count']),
            ("Avg Attributes/Req", f"{self.stats['avg_attributes_per_req']:.1f}"),
            ("Unique Types", len(self.stats['unique_types']))
        ]
        
        for i, (label, value) in enumerate(stats_data):
            frame = tk.Frame(main_frame, bg='#FFFFFF')
            frame.pack(fill=tk.X, pady=3)
            
            tk.Label(frame, text=f"{label}:", font=('Arial', 10, 'bold'), 
                    bg='#FFFFFF', fg='#000000').pack(side=tk.LEFT)
            tk.Label(frame, text=str(value), font=('Arial', 10), 
                    bg='#FFFFFF', fg='#0078D4').pack(side=tk.RIGHT)
        
        # Close button
        tk.Button(main_frame, text="Close", command=stats_window.destroy,
                 bg='#F0F0F0', fg='#000000', font=('Arial', 10),
                 relief='solid', borderwidth=1, padx=15, pady=5,
                 activebackground='#E0E0E0', activeforeground='#000000').pack(pady=(15, 0))
    
    def _export_csv(self):
        """Export filtered requirements to CSV"""
        if not self.filtered_requirements:
            messagebox.showwarning("No Data", "No requirements to export.")
            return
        
        try:
            filename = filedialog.asksaveasfilename(
                title="Export Requirements to CSV",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile=f"requirements_export_{len(self.filtered_requirements)}_items.csv"
            )
            
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
            details_window.configure(bg='#FFFFFF')
            details_window.transient(self.window)
            
            main_frame = tk.Frame(details_window, bg='#FFFFFF', padx=20, pady=20)
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Title
            tk.Label(main_frame, text=f"Requirement: {req_text}", 
                    font=('Arial', 14, 'bold'), bg='#FFFFFF', fg='#000000').pack(anchor=tk.W, pady=(0, 15))
            
            # Details in scrollable text
            text_frame = tk.Frame(main_frame, bg='#FFFFFF')
            text_frame.pack(fill=tk.BOTH, expand=True)
            
            details_text = tk.Text(text_frame, wrap=tk.WORD, bg='#F8F8F8', fg='#000000', font=('Arial', 10))
            details_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=details_text.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            details_text.configure(yscrollcommand=scrollbar.set)
            
            # Populate details
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
            tk.Button(main_frame, text="Close", command=details_window.destroy,
                     bg='#F0F0F0', fg='#000000', font=('Arial', 10),
                     relief='solid', borderwidth=1, padx=15, pady=5,
                     activebackground='#E0E0E0', activeforeground='#000000').pack(pady=(15, 0))
            
        except Exception as e:
            messagebox.showerror("Details Error", f"Failed to show requirement details:\n{str(e)}")
    
    def _on_closing(self):
        """Handle window closing"""
        try:
            self.window.destroy()
        except:
            pass