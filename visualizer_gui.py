#!/usr/bin/env python3
"""
VisualizerGUI - Native Version
Pure tkinter without any theme dependencies
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import os
from typing import List, Dict, Any, Optional


class VisualizerGUI:
    """
    Native Requirements Visualizer GUI
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
        """Setup native GUI"""
        # Create main container
        self.main_frame = tk.Frame(self.window, padx=20, pady=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create sections
        self._create_header_section()
        self._create_control_section()
        self._create_content_section()
        self._create_status_section()
    
    def _create_header_section(self):
        """Create header with file info and search"""
        header_frame = tk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # File info
        info_frame = tk.Frame(header_frame)
        info_frame.pack(side=tk.LEFT)
        
        title_label = tk.Label(info_frame, text="Requirements Analysis", 
                              font=('Arial', 18, 'bold'))
        title_label.pack(anchor=tk.W)
        
        file_label = tk.Label(info_frame, text=f"File: {os.path.basename(self.filename)}",
                             font=('Arial', 11))
        file_label.pack(anchor=tk.W, pady=(5, 0))
        
        count_label = tk.Label(info_frame, text=f"Total Requirements: {len(self.requirements)}",
                              font=('Arial', 11), fg='darkblue')
        count_label.pack(anchor=tk.W, pady=(3, 0))
        
        # Search section
        search_frame = tk.Frame(header_frame)
        search_frame.pack(side=tk.RIGHT, padx=(25, 0))
        
        tk.Label(search_frame, text="Search:", font=('Arial', 12, 'bold')).pack(side=tk.LEFT, padx=(0, 10))
        
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, width=35, 
                               font=('Arial', 11), relief='sunken', bd=2)
        search_entry.pack(side=tk.LEFT)
        
        clear_btn = tk.Button(search_frame, text="Clear", width=8, command=self._clear_search,
                             font=('Arial', 10), relief='raised', bd=2, padx=12, pady=4,
                             cursor='hand2')
        clear_btn.pack(side=tk.LEFT, padx=(10, 0))
    
    def _create_control_section(self):
        """Create control buttons"""
        control_frame = tk.Frame(self.main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Left side buttons
        left_buttons = tk.Frame(control_frame)
        left_buttons.pack(side=tk.LEFT)
        
        tk.Button(left_buttons, text="📊 Statistics", command=self._show_statistics,
                 font=('Arial', 11, 'bold'), relief='raised', bd=2,
                 padx=20, pady=6, cursor='hand2', bg='lightcyan').pack(side=tk.LEFT, padx=(0, 15))
        
        tk.Button(left_buttons, text="📄 Export CSV", command=self._export_csv,
                 font=('Arial', 11, 'bold'), relief='raised', bd=2,
                 padx=20, pady=6, cursor='hand2', bg='lightgreen').pack(side=tk.LEFT, padx=(0, 15))
        
        tk.Button(left_buttons, text="🔄 Refresh", command=self._refresh_view,
                 font=('Arial', 11), relief='raised', bd=2,
                 padx=20, pady=6, cursor='hand2').pack(side=tk.LEFT, padx=(0, 25))
        
        # Filter info on the right
        self.filter_info_label = tk.Label(control_frame,
                                         text=f"Showing: {len(self.filtered_requirements)} of {len(self.requirements)} requirements",
                                         font=('Arial', 11))
        self.filter_info_label.pack(side=tk.RIGHT)
    
    def _create_content_section(self):
        """Create main content area with treeview"""
        content_frame = tk.Frame(self.main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview with scrollbars
        tree_frame = tk.Frame(content_frame)
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
        status_frame = tk.Frame(self.main_frame, relief='sunken', bd=2)
        status_frame.pack(fill=tk.X, pady=(20, 0))
        
        self.status_label = tk.Label(status_frame, text="Ready", font=('Arial', 10), 
                                    anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, padx=12, pady=8)
        
        # Selection info
        self.selection_label = tk.Label(status_frame, text="", font=('Arial', 10))
        self.selection_label.pack(side=tk.RIGHT, padx=12, pady=8)
    
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
            self.status_label.configure(text="Data loaded successfully", fg='darkgreen')
            
        except Exception as e:
            self.status_label.configure(text=f"Error loading data: {str(e)}", fg='red')
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
        total = len(self.requirements)
        showing = len(self.filtered_requirements)
        
        if showing == total:
            self.filter_info_label.configure(
                text=f"Showing: {showing} requirements", fg='black'
            )
        else:
            self.filter_info_label.configure(
                text=f"Showing: {showing} of {total} requirements (filtered)", fg='darkorange'
            )
    
    def _refresh_view(self):
        """Refresh the view"""
        self.populate_data()
        self.status_label.configure(text="View refreshed", fg='darkgreen')
    
    def _show_statistics(self):
        """Show statistics dialog"""
        stats_window = tk.Toplevel(self.window)
        stats_window.title("Requirements Statistics")
        stats_window.geometry("500x450")
        stats_window.transient(self.window)
        
        main_frame = tk.Frame(stats_window, padx=25, pady=25)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        tk.Label(main_frame, text="Requirements Statistics", 
                font=('Arial', 16, 'bold')).pack(pady=(0, 20))
        
        # Statistics frame
        stats_frame = tk.Frame(main_frame)
        stats_frame.pack(fill=tk.BOTH, expand=True)
        
        # Statistics data
        stats_data = [
            ("Total Requirements", self.stats['total_count'], 'darkblue'),
            ("With Titles", f"{self.stats['with_titles']} ({self.stats['with_titles']/self.stats['total_count']*100:.1f}%)", 'darkgreen'),
            ("With Descriptions", f"{self.stats['with_descriptions']} ({self.stats['with_descriptions']/self.stats['total_count']*100:.1f}%)", 'darkgreen'),
            ("With Types", f"{self.stats['with_types']} ({self.stats['with_types']/self.stats['total_count']*100:.1f}%)", 'darkgreen'),
            ("Total Attributes", self.stats['attribute_count'], 'darkorange'),
            ("Avg Attributes/Req", f"{self.stats['avg_attributes_per_req']:.1f}", 'darkorange'),
            ("Unique Types", len(self.stats['unique_types']), 'purple')
        ]
        
        for i, (label, value, color) in enumerate(stats_data):
            frame = tk.Frame(stats_frame)
            frame.pack(fill=tk.X, pady=6)
            
            tk.Label(frame, text=f"{label}:", font=('Arial', 12, 'bold')).pack(side=tk.LEFT)
            tk.Label(frame, text=str(value), font=('Arial', 12), fg=color).pack(side=tk.RIGHT)
        
        # Types list if available
        if self.stats['unique_types']:
            types_frame = tk.LabelFrame(main_frame, text="Requirement Types", 
                                       font=('Arial', 11, 'bold'), padx=10, pady=10)
            types_frame.pack(fill=tk.X, pady=(20, 0))
            
            types_text = ', '.join(self.stats['unique_types'][:10])
            if len(self.stats['unique_types']) > 10:
                types_text += f"... and {len(self.stats['unique_types']) - 10} more"
            
            tk.Label(types_frame, text=types_text, font=('Arial', 10), 
                    wraplength=400, justify=tk.LEFT).pack()
        
        # Close button
        tk.Button(main_frame, text="Close", command=stats_window.destroy,
                 font=('Arial', 11), relief='raised', bd=2, padx=20, pady=6,
                 cursor='hand2').pack(pady=(20, 0))
    
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
            details_window.geometry("700x600")
            details_window.transient(self.window)
            
            main_frame = tk.Frame(details_window, padx=25, pady=25)
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Title
            tk.Label(main_frame, text=f"Requirement: {req_text}", 
                    font=('Arial', 16, 'bold')).pack(anchor=tk.W, pady=(0, 20))
            
            # Details in scrollable text
            text_frame = tk.Frame(main_frame)
            text_frame.pack(fill=tk.BOTH, expand=True)
            
            details_text = tk.Text(text_frame, wrap=tk.WORD, font=('Arial', 11))
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
                details_text.insert(tk.END, "-" * 20 + "\n")
                for attr_name, attr_value in attributes.items():
                    details_text.insert(tk.END, f"{attr_name}: {attr_value}\n")
                details_text.insert(tk.END, "\n")
            
            # Add raw attributes if different
            raw_attributes = req.get('raw_attributes', {})
            if raw_attributes and raw_attributes != attributes:
                details_text.insert(tk.END, "Raw Attributes:\n")
                details_text.insert(tk.END, "-" * 20 + "\n")
                for attr_ref, attr_value in raw_attributes.items():
                    details_text.insert(tk.END, f"{attr_ref}: {attr_value}\n")
            
            details_text.configure(state=tk.DISABLED)
            
            # Close button
            tk.Button(main_frame, text="Close", command=details_window.destroy,
                     font=('Arial', 11), relief='raised', bd=2, padx=20, pady=6,
                     cursor='hand2').pack(pady=(20, 0))
            
        except Exception as e:
            messagebox.showerror("Details Error", f"Failed to show requirement details:\n{str(e)}")
    
    def _on_closing(self):
        """Handle window closing"""
        try:
            self.window.destroy()
        except:
            pass