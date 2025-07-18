#!/usr/bin/env python3
"""
ComparisonResultsGUI - Updated Version for Content/Structural Separation
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


class ComparisonResultsGUI:
    """
    Comparison Results GUI with Content/Structural Change Separation
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
        
        # Track selected items for diff viewer
        self.selected_content_items = []
        self.selected_structural_items = []
        
        # Dynamic field detection
        self.available_fields = self._detect_available_fields()
        self.display_fields = self._select_display_fields()
        
        # Setup GUI
        self.setup_gui()
        
        # Handle window closing
        self.window.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _detect_available_fields(self) -> Dict[str, Set[str]]:
        """Detect which fields are actually available in each category"""
        available_fields = {
            'added': set(),
            'deleted': set(),
            'content_modified': set(),
            'structural_only': set(),
            'unchanged': set()
        }
        
        for category in available_fields.keys():
            requirements = self.results.get(category, [])
            if not requirements:
                continue
                
            for req in requirements:
                if isinstance(req, dict):
                    # Add main fields (excluding internal ones)
                    for field_name in req.keys():
                        if not field_name.startswith('_') and field_name not in ['content', 'raw_attributes']:
                            available_fields[category].add(field_name)
                    
                    # Add attribute fields with prefix
                    attributes = req.get('attributes', {})
                    if isinstance(attributes, dict):
                        for attr_name in attributes.keys():
                            available_fields[category].add(f'attr_{attr_name}')
        
        return available_fields
    
    def _select_display_fields(self) -> Dict[str, List[str]]:
        """Select optimal fields for display in each category"""
        display_fields = {}
        
        for category, fields in self.available_fields.items():
            if not fields:
                display_fields[category] = ['id']
                continue
            
            # Always include id first
            selected = ['id']
            
            # Priority fields (if they exist)
            priority_fields = ['identifier', 'type']
            for field in priority_fields:
                if field in fields and field not in selected:
                    selected.append(field)
            
            # Add most common attribute fields (limit to reasonable number)
            attr_fields = [f for f in fields if f.startswith('attr_')]
            attr_fields = sorted(attr_fields)[:4]  # Limit to 4 attributes
            selected.extend(attr_fields)
            
            # Add other fields (limit total columns)
            other_fields = [f for f in fields if not f.startswith('attr_') and f not in selected]
            remaining_slots = max(0, 8 - len(selected))  # Max 8 columns total
            selected.extend(sorted(other_fields)[:remaining_slots])
            
            display_fields[category] = selected
        
        return display_fields
    
    def setup_gui(self):
        """Setup native GUI with content/structural separation"""
        # Create main container
        self.main_frame = tk.Frame(self.window, padx=20, pady=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create sections
        self._create_header_section()
        self._create_summary_section()
        self._create_results_section()
        self._create_controls_section()
    
    def _create_header_section(self):
        """Create header"""
        header_frame = tk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Title
        title_label = tk.Label(header_frame, text="Requirements Comparison Results", 
                              font=('Arial', 18, 'bold'))
        title_label.pack(anchor=tk.W)
        
        # Subtitle
        subtitle_label = tk.Label(header_frame,
                                 text="Content changes show actual value modifications. Structural changes show field additions/removals.",
                                 font=('Arial', 11))
        subtitle_label.pack(anchor=tk.W, pady=(8, 0))
    
    def _create_summary_section(self):
        """Create summary statistics with content/structural breakdown"""
        summary_frame = tk.LabelFrame(self.main_frame, text="Summary Statistics", 
                                     font=('Arial', 12, 'bold'), padx=15, pady=15)
        summary_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Get statistics
        stats = self.results.get('statistics', {})
        
        # Create grid for statistics
        stats_container = tk.Frame(summary_frame)
        stats_container.pack(fill=tk.X)
        
        # Create summary labels with colors
        summary_data = [
            ("Added", stats.get('added_count', 0), 'darkgreen'),
            ("Deleted", stats.get('deleted_count', 0), 'darkred'),
            ("Content Modified", stats.get('content_modified_count', 0), 'darkorange'),
            ("Structure Only", stats.get('structural_only_count', 0), 'purple'),
            ("Unchanged", stats.get('unchanged_count', 0), 'darkblue')
        ]
        
        for col, (label, count, color) in enumerate(summary_data):
            frame = tk.Frame(stats_container)
            frame.grid(row=0, column=col, padx=20, pady=10, sticky='n')
            
            tk.Label(frame, text=label, font=('Arial', 12, 'bold')).pack()
            tk.Label(frame, text=str(count), font=('Arial', 16, 'bold'), 
                    fg=color).pack()
        
        # Add percentage info
        percentage_frame = tk.Frame(summary_frame)
        percentage_frame.pack(fill=tk.X, pady=(15, 0))
        
        content_pct = stats.get('content_change_percentage', 0)
        total_pct = stats.get('total_change_percentage', 0)
        
        tk.Label(percentage_frame, text=f"Content Change Rate: {content_pct}%", 
                font=('Arial', 11, 'bold'), fg='darkorange').pack(side=tk.LEFT, padx=(0, 30))
        tk.Label(percentage_frame, text=f"Total Change Rate: {total_pct}%", 
                font=('Arial', 11, 'bold'), fg='darkred').pack(side=tk.LEFT)
        
        # Structural changes info
        if stats.get('added_fields') or stats.get('removed_fields'):
            struct_frame = tk.Frame(summary_frame)
            struct_frame.pack(fill=tk.X, pady=(15, 0))
            
            tk.Label(struct_frame, text="Common Structural Changes:", 
                    font=('Arial', 11, 'bold')).pack(anchor=tk.W)
            
            if stats.get('added_fields'):
                added_fields = stats['added_fields'][:5]  # Show first 5
                tk.Label(struct_frame, text=f"  Added fields: {', '.join(added_fields)}", 
                        font=('Arial', 10), fg='darkgreen').pack(anchor=tk.W)
            
            if stats.get('removed_fields'):
                removed_fields = stats['removed_fields'][:5]  # Show first 5
                tk.Label(struct_frame, text=f"  Removed fields: {', '.join(removed_fields)}", 
                        font=('Arial', 10), fg='darkred').pack(anchor=tk.W)
    
    def _create_results_section(self):
        """Create results with tabs for different change types"""
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self._create_added_tab()
        self._create_deleted_tab()
        self._create_content_modified_tab()
        self._create_structural_only_tab()
        self._create_unchanged_tab()
    
    def _create_added_tab(self):
        """Create added requirements tab"""
        added_frame = tk.Frame(self.notebook)
        self.notebook.add(added_frame, text=f"➕ Added ({len(self.results.get('added', []))})")
        self._create_requirements_tree(added_frame, self.results.get('added', []), "added")
    
    def _create_deleted_tab(self):
        """Create deleted requirements tab"""
        deleted_frame = tk.Frame(self.notebook)
        self.notebook.add(deleted_frame, text=f"➖ Deleted ({len(self.results.get('deleted', []))})")
        self._create_requirements_tree(deleted_frame, self.results.get('deleted', []), "deleted")
    
    def _create_content_modified_tab(self):
        """Create content-modified requirements tab with diff functionality"""
        modified_frame = tk.Frame(self.notebook)
        self.notebook.add(modified_frame, text=f"📝 Content Modified ({len(self.results.get('content_modified', []))})")
        
        self._create_enhanced_modified_tree(modified_frame, self.results.get('content_modified', []), 'content')
    
    def _create_structural_only_tab(self):
        """Create structural-only changes tab"""
        structural_frame = tk.Frame(self.notebook)
        self.notebook.add(structural_frame, text=f"📋 Structure Only ({len(self.results.get('structural_only', []))})")
        
        self._create_structural_tree(structural_frame, self.results.get('structural_only', []))
    
    def _create_unchanged_tab(self):
        """Create unchanged requirements tab"""
        unchanged_frame = tk.Frame(self.notebook)
        self.notebook.add(unchanged_frame, text=f"✓ Unchanged ({len(self.results.get('unchanged', []))})")
        self._create_requirements_tree(unchanged_frame, self.results.get('unchanged', []), "unchanged")
    
    def _create_enhanced_modified_tree(self, parent, requirements: List[Dict], change_type: str):
        """Create enhanced modified requirements tree with diff functionality"""
        # Controls frame for Show Differences button
        controls_frame = tk.Frame(parent)
        controls_frame.pack(fill=tk.X, padx=15, pady=15)
        
        self.show_diff_btn = tk.Button(controls_frame, text="👁️ Show Differences",
                                      command=lambda: self._show_differences(change_type), 
                                      state=tk.DISABLED,
                                      font=('Arial', 11, 'bold'), relief='raised', bd=2,
                                      padx=15, pady=5, cursor='hand2')
        self.show_diff_btn.pack(side=tk.LEFT, padx=(0, 15))
        
        self.selection_info_label = tk.Label(controls_frame,
                                           text="Select a requirement to view content differences",
                                           font=('Arial', 10))
        self.selection_info_label.pack(side=tk.LEFT)
        
        # Tree frame
        tree_frame = tk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        # Get display fields for content modified category
        display_fields = self.display_fields.get('content_modified', ['id'])
        
        # Add special columns for modified view
        columns = display_fields[1:] + ['changes_summary', 'change_count']
        
        # Create treeview
        self.content_tree = ttk.Treeview(tree_frame, columns=columns, show='tree headings', selectmode='extended')
        self.content_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure tree column
        tree_field = display_fields[0] if display_fields else 'id'
        self.content_tree.heading('#0', text=self._format_field_name(tree_field), anchor=tk.W)
        self.content_tree.column('#0', width=120, minwidth=80)
        
        # Configure other columns
        for col in columns:
            display_name = self._format_field_name(col)
            self.content_tree.heading(col, text=display_name, anchor=tk.W)
            
            if col in ['changes_summary']:
                width = 300
            elif col in ['change_count']:
                width = 80
            elif col.startswith('attr_'):
                width = 180
            else:
                width = 150
                
            self.content_tree.column(col, width=width, minwidth=60)
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.content_tree.yview)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.content_tree.configure(yscrollcommand=v_scrollbar.set)
        
        # Populate tree
        self._populate_tree(self.content_tree, requirements, "content_modified")
        
        # Bind events
        self.content_tree.bind('<<TreeviewSelect>>', lambda e: self._on_modified_selection_change('content'))
        self.content_tree.bind('<Double-1>', lambda event: self._on_item_double_click(self.content_tree, requirements, "content_modified"))
    
    def _create_structural_tree(self, parent, requirements: List[Dict]):
        """Create tree for structural-only changes"""
        # Info frame
        info_frame = tk.Frame(parent)
        info_frame.pack(fill=tk.X, padx=15, pady=15)
        
        tk.Label(info_frame, text="These requirements have the same content but different fields/attributes",
                font=('Arial', 11), fg='purple').pack(anchor=tk.W)
        
        # Tree frame
        tree_frame = tk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        # Define columns for structural view
        columns = ['added_fields', 'removed_fields']
        
        # Create treeview
        self.structural_tree = ttk.Treeview(tree_frame, columns=columns, show='tree headings', selectmode='extended')
        self.structural_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure columns
        self.structural_tree.heading('#0', text='ID', anchor=tk.W)
        self.structural_tree.column('#0', width=150, minwidth=100)
        
        self.structural_tree.heading('added_fields', text='Added Fields', anchor=tk.W)
        self.structural_tree.column('added_fields', width=300, minwidth=150)
        
        self.structural_tree.heading('removed_fields', text='Removed Fields', anchor=tk.W)
        self.structural_tree.column('removed_fields', width=300, minwidth=150)
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.structural_tree.yview)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.structural_tree.configure(yscrollcommand=v_scrollbar.set)
        
        # Populate tree
        for req in requirements:
            if isinstance(req, dict):
                req_id = req.get('id', 'Unknown')
                added_fields = req.get('added_fields', [])
                removed_fields = req.get('removed_fields', [])
                
                # Format field lists
                added_text = ', '.join(added_fields[:5])
                if len(added_fields) > 5:
                    added_text += f' (+{len(added_fields)-5} more)'
                
                removed_text = ', '.join(removed_fields[:5])
                if len(removed_fields) > 5:
                    removed_text += f' (+{len(removed_fields)-5} more)'
                
                values = [added_text or 'None', removed_text or 'None']
                self.structural_tree.insert('', 'end', text=req_id, values=values)
        
        # Bind double-click
        self.structural_tree.bind('<Double-1>', lambda event: self._on_structural_double_click(event, requirements))
    
    def _create_requirements_tree(self, parent, requirements: List[Dict], category: str):
        """Create standard treeview for non-modified requirements with dynamic fields"""
        # Create frame
        tree_frame = tk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Get display fields for this category
        display_fields = self.display_fields.get(category, ['id'])
        
        # Define columns (exclude first field which goes in tree column)
        columns = display_fields[1:] if len(display_fields) > 1 else []
        
        # Create treeview
        tree = ttk.Treeview(tree_frame, columns=columns, show='tree headings', selectmode='extended')
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure tree column (first field)
        tree_field = display_fields[0] if display_fields else 'id'
        tree.heading('#0', text=self._format_field_name(tree_field), anchor=tk.W)
        tree.column('#0', width=120, minwidth=80)
        
        # Configure other columns
        for col in columns:
            display_name = self._format_field_name(col)
            tree.heading(col, text=display_name, anchor=tk.W)
            
            # Set column width based on field type
            if col.startswith('attr_'):
                width = 200
            elif col in ['type']:
                width = 120
            else:
                width = 150
                
            tree.column(col, width=width, minwidth=80)
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.configure(yscrollcommand=v_scrollbar.set)
        
        # Populate tree
        self._populate_tree(tree, requirements, category)
        
        # Bind events
        tree.bind('<Double-1>', lambda event: self._on_item_double_click(tree, requirements, category))
    
    def _format_field_name(self, field_name: str) -> str:
        """Format field name for display"""
        if field_name.startswith('attr_'):
            # Remove 'attr_' prefix and format attribute name
            attr_name = field_name[5:]
            return attr_name.replace('_', ' ').title()
        else:
            # Format regular field names
            formatted = field_name.replace('_', ' ').title()
            # Special cases
            if formatted == 'Id':
                return 'ID'
            elif formatted == 'Changes Summary':
                return 'Changes'
            elif formatted == 'Change Count':
                return 'Count'
            return formatted
    
    def _populate_tree(self, tree, requirements: List[Dict], category: str):
        """Populate treeview with data using dynamic fields"""
        display_fields = self.display_fields.get(category, ['id'])
        tree_field = display_fields[0] if display_fields else 'id'
        column_fields = display_fields[1:] if len(display_fields) > 1 else []
        
        # Add special fields for content modified category
        if category == "content_modified":
            column_fields = column_fields + ['changes_summary', 'change_count']
        
        for i, req in enumerate(requirements):
            try:
                if not isinstance(req, dict):
                    continue
                
                # Get tree column value
                tree_value = self._get_field_value(req, tree_field)
                
                # Get column values
                values = []
                for field in column_fields:
                    value = self._get_field_value(req, field)
                    # Truncate long values
                    if len(str(value)) > 100:
                        value = str(value)[:97] + "..."
                    values.append(value)
                
                tree.insert('', 'end', text=tree_value, values=values)
                
            except Exception as e:
                print(f"Error inserting {category} requirement {i}: {e}")
                continue
    
    def _get_field_value(self, req: Dict[str, Any], field_name: str) -> str:
        """Get field value from requirement with proper handling"""
        try:
            if field_name.startswith('attr_'):
                # Attribute field
                attr_name = field_name[5:]
                attributes = req.get('attributes', {})
                if isinstance(attributes, dict):
                    return str(attributes.get(attr_name, ''))
                return ''
            else:
                # Regular field
                return str(req.get(field_name, ''))
        except Exception as e:
            print(f"Error getting field value for {field_name}: {e}")
            return ''
    
    def _on_modified_selection_change(self, change_type: str):
        """Handle selection changes in modified requirements tree"""
        try:
            if change_type == 'content':
                tree = self.content_tree
                selection = tree.selection()
                self.selected_content_items = list(selection)
                
                if len(selection) == 1:
                    self.show_diff_btn.configure(state=tk.NORMAL, bg='lightgreen')
                    self.selection_info_label.configure(text="1 requirement selected - click 'Show Differences' to view changes")
                elif len(selection) > 1:
                    self.show_diff_btn.configure(state=tk.DISABLED, bg='lightgray')
                    self.selection_info_label.configure(text=f"{len(selection)} requirements selected - select only one to view differences")
                else:
                    self.show_diff_btn.configure(state=tk.DISABLED, bg='lightgray')
                    self.selection_info_label.configure(text="Select a requirement to view content differences")
                
        except Exception as e:
            print(f"Error handling selection change: {e}")
    
    def _show_differences(self, change_type: str):
        """Show side-by-side differences for selected requirement"""
        if change_type == 'content' and not self.selected_content_items:
            messagebox.showwarning("Selection Required", "Please select exactly one requirement to view differences.")
            return
        
        try:
            if change_type == 'content':
                item = self.selected_content_items[0]
                tree = self.content_tree
                requirements = self.results.get('content_modified', [])
            
            item_index = tree.index(item)
            
            if item_index >= len(requirements):
                messagebox.showerror("Error", "Could not find requirement data.")
                return
            
            requirement = requirements[item_index]
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
    
    def _on_structural_double_click(self, event, requirements: List[Dict]):
        """Handle double-click on structural changes"""
        selection = self.structural_tree.selection()
        if not selection:
            return
        
        try:
            item = selection[0]
            item_index = self.structural_tree.index(item)
            
            if item_index < len(requirements):
                req = requirements[item_index]
                self._show_structural_details(req)
        except Exception as e:
            print(f"Error handling structural double-click: {e}")
    
    def _show_structural_details(self, requirement: Dict):
        """Show detailed structural changes"""
        details_window = tk.Toplevel(self.window)
        details_window.title(f"Structural Changes - {requirement.get('id', 'Unknown')}")
        details_window.geometry("700x600")
        details_window.transient(self.window)
        
        main_frame = tk.Frame(details_window, padx=25, pady=25)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        tk.Label(main_frame, text=f"Structural Changes for: {requirement.get('id', 'Unknown')}", 
                font=('Arial', 16, 'bold')).pack(anchor=tk.W, pady=(0, 20))
        
        # Info
        tk.Label(main_frame, text="This requirement has identical content but different fields/attributes",
                font=('Arial', 11), fg='purple').pack(anchor=tk.W, pady=(0, 15))
        
        # Details in scrollable text
        text_frame = tk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        details_text = tk.Text(text_frame, wrap=tk.WORD, font=('Arial', 11))
        details_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=details_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        details_text.configure(yscrollcommand=scrollbar.set)
        
        # Populate details
        comparison_data = requirement.get('_comparison_data', {})
        added_fields = comparison_data.get('added_fields', set())
        removed_fields = comparison_data.get('removed_fields', set())
        
        details_text.insert(tk.END, "=== ADDED FIELDS ===\n\n")
        if added_fields:
            for field in sorted(added_fields):
                field_display = field.replace('attribute.', 'Attribute: ')
                new_req = comparison_data.get('new', {})
                value = self._get_field_value_from_comparison(new_req, field)
                details_text.insert(tk.END, f"{field_display}:\n  {value}\n\n")
        else:
            details_text.insert(tk.END, "No fields added\n\n")
        
        details_text.insert(tk.END, "\n=== REMOVED FIELDS ===\n\n")
        if removed_fields:
            for field in sorted(removed_fields):
                field_display = field.replace('attribute.', 'Attribute: ')
                old_req = comparison_data.get('old', {})
                value = self._get_field_value_from_comparison(old_req, field)
                details_text.insert(tk.END, f"{field_display}:\n  {value}\n\n")
        else:
            details_text.insert(tk.END, "No fields removed\n\n")
        
        details_text.configure(state=tk.DISABLED)
        
        # Close button
        tk.Button(main_frame, text="Close", command=details_window.destroy,
                 font=('Arial', 11), relief='raised', bd=2, padx=20, pady=6,
                 cursor='hand2').pack(pady=(20, 0))
    
    def _get_field_value_from_comparison(self, req: Dict[str, Any], field: str) -> str:
        """Get field value handling attribute fields"""
        if field.startswith('attribute.'):
            attr_name = field[10:]
            attributes = req.get('attributes', {})
            if isinstance(attributes, dict):
                return str(attributes.get(attr_name, ''))
        else:
            return str(req.get(field, ''))
    
    def _create_controls_section(self):
        """Create control buttons"""
        controls_frame = tk.Frame(self.main_frame)
        controls_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Export button
        export_btn = tk.Button(controls_frame, text="📄 Export All Results", 
                              command=self._export_all_results,
                              font=('Arial', 11, 'bold'), relief='raised', bd=2,
                              padx=20, pady=6, cursor='hand2', bg='lightblue')
        export_btn.pack(side=tk.LEFT, padx=(0, 15))
        
        # Close button
        close_btn = tk.Button(controls_frame, text="✖️ Close", 
                             command=self._on_closing,
                             font=('Arial', 11), relief='raised', bd=2,
                             padx=20, pady=6, cursor='hand2')
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
                if category == "content_modified":
                    self._show_modified_requirement_options(req)
                else:
                    self._show_requirement_details(req, category)
        except Exception as e:
            print(f"Error handling double-click: {e}")
    
    def _show_modified_requirement_options(self, requirement: Dict):
       """Show options for content-modified requirements (details or diff)"""
       choice_window = tk.Toplevel(self.window)
       choice_window.title("View Options")
       choice_window.geometry("450x250")
       choice_window.transient(self.window)
       choice_window.grab_set()
       
       main_frame = tk.Frame(choice_window, padx=25, pady=25)
       main_frame.pack(fill=tk.BOTH, expand=True)
       
       req_id = requirement.get('id', 'Unknown')
       tk.Label(main_frame, text=f"View options for requirement: {req_id}", 
               font=('Arial', 14, 'bold')).pack(pady=(0, 20))
       
       tk.Label(main_frame, text="How would you like to view this content-modified requirement?",
               font=('Arial', 11)).pack(pady=(0, 25))
       
       button_frame = tk.Frame(main_frame)
       button_frame.pack(fill=tk.X)
       
       def show_details():
           choice_window.destroy()
           self._show_requirement_details(requirement, "content_modified")
       
       def show_diff():
           choice_window.destroy()
           self._launch_diff_viewer(requirement)
       
       tk.Button(button_frame, text="📋 Show Details", command=show_details, 
                font=('Arial', 11), relief='raised', bd=2, padx=15, pady=6,
                cursor='hand2').pack(side=tk.LEFT, padx=(0, 15))
       tk.Button(button_frame, text="🔍 Show Differences", command=show_diff,
                font=('Arial', 11), relief='raised', bd=2, padx=15, pady=6,
                cursor='hand2').pack(side=tk.LEFT)
       tk.Button(button_frame, text="Cancel", command=choice_window.destroy,
                font=('Arial', 11), relief='raised', bd=2, padx=15, pady=6,
                cursor='hand2').pack(side=tk.RIGHT)
   
   def _show_requirement_details(self, requirement: Dict, category: str):
       """Show detailed requirement information with dynamic fields"""
       details_window = tk.Toplevel(self.window)
       details_window.title(f"Requirement Details - {category.replace('_', ' ').title()}")
       details_window.geometry("750x650")
       details_window.transient(self.window)
       
       main_frame = tk.Frame(details_window, padx=25, pady=25)
       main_frame.pack(fill=tk.BOTH, expand=True)
       
       # Title - use best available display text
       display_text = self._get_requirement_display_text(requirement)
       tk.Label(main_frame, text=f"Requirement: {display_text}", 
               font=('Arial', 16, 'bold')).pack(anchor=tk.W, pady=(0, 20))
       
       # Details in scrollable text
       text_frame = tk.Frame(main_frame)
       text_frame.pack(fill=tk.BOTH, expand=True)
       
       details_text = tk.Text(text_frame, wrap=tk.WORD, font=('Arial', 11))
       details_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
       
       scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=details_text.yview)
       scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
       details_text.configure(yscrollcommand=scrollbar.set)
       
       # Populate details with dynamic fields
       if category == "content_modified":
           self._populate_content_modified_details(details_text, requirement)
       else:
           self._populate_standard_details(details_text, requirement, category)
       
       details_text.configure(state=tk.DISABLED)
       
       # Buttons frame
       buttons_frame = tk.Frame(main_frame)
       buttons_frame.pack(fill=tk.X, pady=(20, 0))
       
       if category == "content_modified":
           tk.Button(buttons_frame, text="🔍 Show Differences", 
                    command=lambda: [details_window.destroy(), self._launch_diff_viewer(requirement)],
                    font=('Arial', 11), relief='raised', bd=2, padx=15, pady=6,
                    cursor='hand2').pack(side=tk.LEFT, padx=(0, 15))
       
       tk.Button(buttons_frame, text="Close", command=details_window.destroy,
                font=('Arial', 11), relief='raised', bd=2, padx=15, pady=6,
                cursor='hand2').pack(side=tk.RIGHT)
   
   def _get_requirement_display_text(self, req: Dict[str, Any]) -> str:
       """Get best display text for requirement using dynamic fields"""
       try:
           if not isinstance(req, dict):
               return "Invalid requirement"
           
           # Try different fields in priority order
           candidates = []
           
           # Check for identifier if different from id
           if req.get('identifier') and req.get('identifier') != req.get('id'):
               candidates.append(req['identifier'])
           
           # Check for type
           if req.get('type'):
               candidates.append(req['type'])
           
           # Check attributes for display-worthy content
           attributes = req.get('attributes', {})
           if isinstance(attributes, dict):
               # Look for text-like attributes
               for attr_name, attr_value in attributes.items():
                   if attr_value and len(str(attr_value).strip()) > 0:
                       display_value = str(attr_value)
                       if len(display_value) > 50:
                           display_value = display_value[:50] + "..."
                       candidates.append(display_value)
                       break  # Use first meaningful attribute
           
           # Return best candidate or fallback to ID
           return candidates[0] if candidates else req.get('id', 'Unknown')
           
       except Exception as e:
           print(f"Error getting display text: {e}")
           return req.get('id', 'Unknown')
   
   def _populate_standard_details(self, text_widget, requirement: Dict, category: str):
       """Populate details for non-modified requirements with dynamic fields"""
       text_widget.insert(tk.END, f"Category: {category.replace('_', ' ').title()}\n\n")
       
       # Display all available fields dynamically
       excluded_fields = {'attributes', 'raw_attributes', 'content', '_comparison_data', 
                         'changes_summary', 'changed_fields', 'change_count',
                         'added_fields', 'removed_fields', 'structural_changes_only'}
       
       for field_name, field_value in requirement.items():
           if field_name not in excluded_fields and field_value:
               display_name = self._format_field_name(field_name)
               text_widget.insert(tk.END, f"{display_name}: {field_value}\n\n")
       
       # Display attributes
       attributes = requirement.get('attributes', {})
       if isinstance(attributes, dict) and attributes:
           text_widget.insert(tk.END, "Attributes:\n")
           text_widget.insert(tk.END, "-" * 30 + "\n")
           for attr_name, attr_value in attributes.items():
               if attr_value:
                   text_widget.insert(tk.END, f"  {attr_name}: {attr_value}\n")
           text_widget.insert(tk.END, "\n")
       
       # Display raw attributes if different
       raw_attributes = requirement.get('raw_attributes', {})
       if isinstance(raw_attributes, dict) and raw_attributes and raw_attributes != attributes:
           text_widget.insert(tk.END, "Raw Attribute References:\n")
           text_widget.insert(tk.END, "-" * 30 + "\n")
           for attr_ref, attr_value in raw_attributes.items():
               if attr_value:
                   text_widget.insert(tk.END, f"  {attr_ref}: {attr_value}\n")
   
   def _populate_content_modified_details(self, text_widget, requirement: Dict):
       """Populate details for content-modified requirements with change information"""
       text_widget.insert(tk.END, "Category: Content Modified\n\n")
       
       # Display current values (excluding change metadata)
       excluded_fields = {'attributes', 'raw_attributes', 'content', '_comparison_data', 
                         'changes_summary', 'changed_fields', 'change_count'}
       
       text_widget.insert(tk.END, "=== CURRENT VALUES (After Changes) ===\n\n")
       for field_name, field_value in requirement.items():
           if field_name not in excluded_fields and field_value:
               display_name = self._format_field_name(field_name)
               text_widget.insert(tk.END, f"{display_name}: {field_value}\n\n")
       
       # Display current attributes
       attributes = requirement.get('attributes', {})
       if isinstance(attributes, dict) and attributes:
           text_widget.insert(tk.END, "Current Attributes:\n")
           text_widget.insert(tk.END, "-" * 30 + "\n")
           for attr_name, attr_value in attributes.items():
               if attr_value:
                   text_widget.insert(tk.END, f"  {attr_name}: {attr_value}\n")
           text_widget.insert(tk.END, "\n")
       
       # Display change summary
       changes_summary = requirement.get('changes_summary', 'Unknown changes')
       change_count = requirement.get('change_count', 0)
       text_widget.insert(tk.END, f"=== CHANGE SUMMARY ===\n")
       text_widget.insert(tk.END, f"Fields Changed: {changes_summary}\n")
       text_widget.insert(tk.END, f"Total Changes: {change_count}\n\n")
       
       # Display detailed changes
       comparison_data = requirement.get('_comparison_data', {})
       if comparison_data:
           changes = comparison_data.get('changes', [])
           old_req = comparison_data.get('old', {})
           
           if changes:
               text_widget.insert(tk.END, "=== DETAILED CONTENT CHANGES ===\n\n")
               
               for change in changes:
                   field = change.get('field', 'Unknown')
                   old_value = change.get('old_value', '')
                   new_value = change.get('new_value', '')
                   
                   display_field = field.replace('attribute.', 'Attribute: ')
                   text_widget.insert(tk.END, f"Field: {display_field}\n")
                   text_widget.insert(tk.END, f"Old Value: {old_value}\n")
                   text_widget.insert(tk.END, f"New Value: {new_value}\n")
                   
                   text_widget.insert(tk.END, "\n" + "-"*50 + "\n\n")
   
   def _export_all_results(self):
       """Export all results to CSV with dynamic fields and new categorization"""
       try:
           filename = filedialog.asksaveasfilename(
               title="Export All Results",
               defaultextension=".csv",
               filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
               initialfile="comparison_results_all.csv"
           )
           
           if not filename:
               return
           
           # Collect all possible fields from all requirements
           all_fields = set()
           for category in ['added', 'deleted', 'content_modified', 'structural_only', 'unchanged']:
               requirements = self.results.get(category, [])
               for req in requirements:
                   if isinstance(req, dict):
                       # Add main fields
                       for field_name in req.keys():
                           if not field_name.startswith('_') and field_name not in ['content', 'raw_attributes']:
                               all_fields.add(field_name)
                       
                       # Add attribute fields
                       attributes = req.get('attributes', {})
                       if isinstance(attributes, dict):
                           for attr_name in attributes.keys():
                               all_fields.add(f'attr_{attr_name}')
           
           # Add change-specific fields
           all_fields.update(['category', 'changes_summary', 'change_count', 'added_fields', 'removed_fields'])
           
           # Sort fields for consistent column order
           sorted_fields = sorted(all_fields)
           
           with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
               writer = csv.writer(csvfile)
               
               # Write header
               header = [self._format_field_name(field) for field in sorted_fields]
               writer.writerow(header)
               
               # Write data for each category
               for category in ['added', 'deleted', 'content_modified', 'structural_only', 'unchanged']:
                   requirements = self.results.get(category, [])
                   for req in requirements:
                       if isinstance(req, dict):
                           row = []
                           for field in sorted_fields:
                               if field == 'category':
                                   row.append(category.replace('_', ' ').title())
                               elif field == 'added_fields':
                                   added = req.get('added_fields', [])
                                   row.append(', '.join(added) if added else '')
                               elif field == 'removed_fields':
                                   removed = req.get('removed_fields', [])
                                   row.append(', '.join(removed) if removed else '')
                               else:
                                   value = self._get_field_value(req, field)
                                   row.append(value)
                           writer.writerow(row)
           
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
   Side-by-side diff viewer window for content changes only
   """
   
   def __init__(self, parent: tk.Widget, req_id: str, old_req: Dict, new_req: Dict, changes: List[Dict]):
       self.parent = parent
       self.req_id = req_id
       self.old_req = old_req
       self.new_req = new_req
       self.changes = changes
       
       # Create diff viewer window
       self.window = tk.Toplevel(parent)
       self.window.title(f"Content Differences - {req_id}")
       self.window.geometry("1200x800")
       self.window.transient(parent)
       
       # Track current field being viewed
       self.current_field = None
       self.field_data = {}
       
       # Build field data (only changed fields)
       self._build_field_data()
       
       # Create UI
       self._create_diff_viewer_ui()
       
       # Show first field with changes
       self._show_first_changed_field()
   
   def _build_field_data(self):
       """Build field data for diff viewing - only content changes"""
       # Process only the changes provided
       for change in self.changes:
           field = change.get('field', '')
           if field:
               self.field_data[field] = {
                   'display_name': field.replace('attribute.', 'Attribute: '),
                   'old_value': str(change.get('old_value', '')),
                   'new_value': str(change.get('new_value', '')),
                   'has_changes': True,
                   'field_type': 'attribute' if field.startswith('attribute.') else 'regular'
               }
   
   def _create_diff_viewer_ui(self):
       """Create the side-by-side diff viewer UI"""
       main_frame = tk.Frame(self.window, padx=15, pady=15)
       main_frame.pack(fill=tk.BOTH, expand=True)
       
       # Header
       self._create_diff_header(main_frame)
       
       # Field selector
       self._create_field_selector(main_frame)
       
       # Side-by-side diff panes
       self._create_diff_panes(main_frame)
       
       # Controls
       self._create_diff_controls(main_frame)
   
   def _create_diff_header(self, parent):
       """Create diff header"""
       header_frame = tk.Frame(parent)
       header_frame.pack(fill=tk.X, pady=(0, 20))
       
       tk.Label(header_frame, text=f"Content Differences: {self.req_id}", 
               font=('Arial', 16, 'bold')).pack(anchor=tk.W)
       
       tk.Label(header_frame, text="Showing only fields with content changes", 
               font=('Arial', 11), fg='darkorange').pack(anchor=tk.W)
   
   def _create_field_selector(self, parent):
       """Create field selector dropdown"""
       selector_frame = tk.Frame(parent)
       selector_frame.pack(fill=tk.X, pady=(0, 20))
       
       tk.Label(selector_frame, text="Field:", font=('Arial', 12, 'bold')).pack(side=tk.LEFT, padx=(0, 15))
       
       # Create field options (only changed fields)
       self.field_options = []
       self.field_var = tk.StringVar()
       
       for field_key, field_info in self.field_data.items():
           display_text = field_info['display_name'] + " (Modified)"
           self.field_options.append((field_key, display_text))
       
       # Sort fields
       self.field_options.sort(key=lambda x: x[1])
       
       self.field_combo = ttk.Combobox(selector_frame, textvariable=self.field_var,
                                      values=[option[1] for option in self.field_options],
                                      state='readonly', width=50, font=('Arial', 10))
       self.field_combo.pack(side=tk.LEFT, padx=(0, 15))
       self.field_combo.bind('<<ComboboxSelected>>', self._on_field_change)
       
       # Navigation buttons
       self.prev_btn = tk.Button(selector_frame, text="← Previous", command=self._show_previous_field,
                                font=('Arial', 10), relief='raised', bd=2, padx=10, pady=3)
       self.prev_btn.pack(side=tk.LEFT, padx=(0, 8))
       
       self.next_btn = tk.Button(selector_frame, text="Next →", command=self._show_next_field,
                                font=('Arial', 10), relief='raised', bd=2, padx=10, pady=3)
       self.next_btn.pack(side=tk.LEFT, padx=(0, 15))
       
       # Change indicator
       self.change_indicator = tk.Label(selector_frame, text="Content Modified", 
                                      font=('Arial', 10), fg='darkorange')
       self.change_indicator.pack(side=tk.LEFT)
   
   def _create_diff_panes(self, parent):
       """Create side-by-side diff panes"""
       panes_frame = tk.Frame(parent)
       panes_frame.pack(fill=tk.BOTH, expand=True)
       
       # Left pane (Original)
       left_frame = tk.LabelFrame(panes_frame, text="Original", font=('Arial', 12, 'bold'))
       left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))
       
       self.left_text = tk.Text(left_frame, wrap=tk.WORD, font=('Consolas', 11),
                               state=tk.DISABLED)
       self.left_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
       
       left_scroll = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.left_text.yview)
       left_scroll.pack(side=tk.RIGHT, fill=tk.Y)
       self.left_text.configure(yscrollcommand=left_scroll.set)
       
       # Right pane (Modified)
       right_frame = tk.LabelFrame(panes_frame, text="Modified", font=('Arial', 12, 'bold'))
       right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(8, 0))
       
       self.right_text = tk.Text(right_frame, wrap=tk.WORD, font=('Consolas', 11),
                                state=tk.DISABLED)
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
       controls_frame = tk.Frame(parent)
       controls_frame.pack(fill=tk.X, pady=(20, 0))
       
       # Export diff button
       tk.Button(controls_frame, text="📄 Export Diff Report", command=self._export_diff_report,
                font=('Arial', 11), relief='raised', bd=2, padx=15, pady=6,
                cursor='hand2').pack(side=tk.LEFT, padx=(0, 15))
       
       # Copy buttons
       tk.Button(controls_frame, text="📋 Copy Original", command=self._copy_original,
                font=('Arial', 11), relief='raised', bd=2, padx=15, pady=6,
                cursor='hand2').pack(side=tk.LEFT, padx=(0, 15))
       
       tk.Button(controls_frame, text="📋 Copy Modified", command=self._copy_modified,
                font=('Arial', 11), relief='raised', bd=2, padx=15, pady=6,
                cursor='hand2').pack(side=tk.LEFT, padx=(0, 25))
       
       # Close button
       tk.Button(controls_frame, text="✖️ Close", command=self.window.destroy,
                font=('Arial', 11), relief='raised', bd=2, padx=15, pady=6,
                cursor='hand2').pack(side=tk.RIGHT)
   
   def _show_first_changed_field(self):
       """Show the first field that has changes"""
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
       
       # Show diff highlighting
       self._display_diff_content(old_value, new_value)
       
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
        """Export detailed difference report with new categories"""
        if not self.comparison_result:
            messagebox.showwarning("Export", "No comparison results to export")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[
                ("Text files", "*.txt"),
                ("JSON files", "*.json"),
                ("All files", "*.*")
            ],
            title="Export Difference Report"
        )
        
        if not filename:
            return
            
        try:
            if filename.endswith('.json'):
                self._export_json_report(filename)
            else:
                self._export_text_report(filename)
                
            messagebox.showinfo("Export", f"Report exported successfully to:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export report:\n{str(e)}")
            
    def _export_json_report(self, filename: str):
        """Export comparison results as JSON"""
        import json
        from datetime import datetime
        
        export_data = {
            'metadata': {
                'export_time': datetime.now().isoformat(),
                'original_file': self.file1_var.get(),
                'modified_file': self.file2_var.get(),
                'comparison_version': '2.0'
            },
            'statistics': self.comparison_result.get('statistics', {}),
            'results': {
                'added': self.comparison_result.get('added', []),
                'deleted': self.comparison_result.get('deleted', []),
                'content_modified': self.comparison_result.get('content_modified', []),
                'structural_only': self.comparison_result.get('structural_only', []),
                'unchanged': self.comparison_result.get('unchanged', [])
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, default=str)
            
    def _export_text_report(self, filename: str):
        """Export comparison results as formatted text"""
        from datetime import datetime
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("REQIF FILE COMPARISON REPORT - V2.0\n")
            f.write("=" * 50 + "\n\n")
            
            f.write(f"Export Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Original File: {self.file1_var.get()}\n")
            f.write(f"Modified File: {self.file2_var.get()}\n\n")
            
            # Write statistics
            stats = self.comparison_result.get('statistics', {})
            f.write("SUMMARY STATISTICS:\n")
            f.write("-" * 30 + "\n")
            f.write(f"Requirements Added: {len(self.comparison_result.get('added', []))}\n")
            f.write(f"Requirements Deleted: {len(self.comparison_result.get('deleted', []))}\n")
            f.write(f"Content Modified: {len(self.comparison_result.get('content_modified', []))}\n")
            f.write(f"Structural Changes: {len(self.comparison_result.get('structural_only', []))}\n")
            f.write(f"Unchanged: {len(self.comparison_result.get('unchanged', []))}\n\n")
            
            # Write detailed sections
            self._write_section_to_file(f, "ADDED REQUIREMENTS", self.comparison_result.get('added', []))
            self._write_section_to_file(f, "DELETED REQUIREMENTS", self.comparison_result.get('deleted', []))
            self._write_section_to_file(f, "CONTENT MODIFIED REQUIREMENTS", self.comparison_result.get('content_modified', []))
            self._write_section_to_file(f, "STRUCTURAL CHANGES ONLY", self.comparison_result.get('structural_only', []))
            
    def _write_section_to_file(self, file_handle, section_title: str, requirements: List[Dict]):
        """Write a section of requirements to file"""
        file_handle.write(f"{section_title}:\n")
        file_handle.write("-" * len(section_title) + "\n")
        
        if not requirements:
            file_handle.write("None\n\n")
            return
            
        for i, req in enumerate(requirements, 1):
            file_handle.write(f"{i}. ID: {req.get('identifier', 'Unknown')}\n")
            
            if section_title == "CONTENT MODIFIED REQUIREMENTS":
                # Show changes for content modified
                if 'changes' in req:
                    file_handle.write("   Changes:\n")
                    for field, change_info in req['changes'].items():
                        if isinstance(change_info, dict) and 'old' in change_info and 'new' in change_info:
                            file_handle.write(f"     {field}:\n")
                            file_handle.write(f"       Old: {change_info['old']}\n")
                            file_handle.write(f"       New: {change_info['new']}\n")
                        else:
                            file_handle.write(f"     {field}: {change_info}\n")
            elif section_title == "STRUCTURAL CHANGES ONLY":
                # Show structural changes
                if 'structural_changes' in req:
                    struct_changes = req['structural_changes']
                    if 'added_attributes' in struct_changes:
                        added_attrs = struct_changes['added_attributes']
                        if added_attrs:
                            file_handle.write("   Added attributes:\n")
                            for attr, value in added_attrs.items():
                                file_handle.write(f"     + {attr}: {value}\n")
                    
                    if 'removed_attributes' in struct_changes:
                        removed_attrs = struct_changes['removed_attributes']
                        if removed_attrs:
                            file_handle.write("   Removed attributes:\n")
                            for attr, value in removed_attrs.items():
                                file_handle.write(f"     - {attr}: {value}\n")
            else:
                # For added/deleted/unchanged, show basic info
                if 'the_value' in req:
                    value = req['the_value']
                    if len(value) > 100:
                        value = value[:100] + "..."
                    file_handle.write(f"   Content: {value}\n")
                    
            file_handle.write("\n")
            
        file_handle.write("\n")
        
    def _clear_results(self):
        """Clear all comparison results and reset UI"""
        self.comparison_result = None
        
        # Clear all text widgets
        for tab_type in ['added', 'deleted', 'content_modified', 'structural_only', 'unchanged']:
            text_widget = getattr(self, f"{tab_type}_text", None)
            if text_widget:
                text_widget.delete(1.0, tk.END)
                
        # Clear summary
        if hasattr(self, 'summary_text'):
            self.summary_text.delete(1.0, tk.END)
            
        # Reset statistics
        for label in self.stats_labels.values():
            label.configure(text="0")
            
        # Reset progress
        self.progress_var.set(0)
        self.progress_label.configure(text="Ready to compare")
        
        # Enable compare button
        self.compare_btn.configure(state=tk.NORMAL)
        
        self._update_status("Results cleared")
        
    def _update_status(self, message: str):
        """Update status bar message"""
        self.status_var.set(message)
        self.root.update_idletasks()
        
    def _show_detailed_comparison(self, req1: Dict, req2: Dict):
        """Show detailed side-by-side comparison of two requirements"""
        detail_window = tk.Toplevel(self.root)
        detail_window.title("Detailed Requirement Comparison")
        detail_window.geometry("1000x700")
        
        # Create main frame
        main_frame = ttk.Frame(detail_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(main_frame, 
                               text=f"Comparing Requirement: {req1.get('identifier', 'Unknown')}",
                               font=('TkDefaultFont', 12, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # Create paned window for side-by-side view
        paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # Original version (left)
        left_frame = ttk.LabelFrame(paned, text="Original Version", padding=10)
        paned.add(left_frame, weight=1)
        
        left_text = tk.Text(left_frame, wrap=tk.WORD, font=('Consolas', 10))
        left_scroll = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=left_text.yview)
        left_text.configure(yscrollcommand=left_scroll.set)
        
        left_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        left_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Modified version (right)
        right_frame = ttk.LabelFrame(paned, text="Modified Version", padding=10)
        paned.add(right_frame, weight=1)
        
        right_text = tk.Text(right_frame, wrap=tk.WORD, font=('Consolas', 10))
        right_scroll = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=right_text.yview)
        right_text.configure(yscrollcommand=right_scroll.set)
        
        right_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        right_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Populate content
        self._populate_comparison_text(left_text, req1, "Original")
        self._populate_comparison_text(right_text, req2, "Modified")
        
        # Make read-only
        left_text.configure(state=tk.DISABLED)
        right_text.configure(state=tk.DISABLED)
        
        # Close button
        ttk.Button(detail_window, text="Close", command=detail_window.destroy).pack(pady=10)
        
    def _populate_comparison_text(self, text_widget: tk.Text, req_data: Dict, version_label: str):
        """Populate text widget with requirement data"""
        if not req_data:
            text_widget.insert(1.0, f"No {version_label.lower()} version available")
            return
            
        content_lines = []
        
        # Basic information
        content_lines.append(f"REQUIREMENT DETAILS ({version_label}):")
        content_lines.append("=" * 40)
        content_lines.append("")
        
        # Key fields
        key_fields = ['identifier', 'the_value', 'req_type', 'last_change', 'spec_hierarchy']
        for field in key_fields:
            if field in req_data:
                value = req_data[field]
                if field == 'the_value' and len(str(value)) > 200:
                    value = str(value)[:200] + "..."
                content_lines.append(f"{field.replace('_', ' ').title()}: {value}")
                
        content_lines.append("")
        content_lines.append("ALL ATTRIBUTES:")
        content_lines.append("-" * 20)
        
        # All attributes
        for key, value in sorted(req_data.items()):
            if key not in key_fields:  # Don't repeat key fields
                if len(str(value)) > 100:
                    value = str(value)[:100] + "..."
                content_lines.append(f"{key}: {value}")
                
        text_widget.insert(1.0, "\n".join(content_lines))
        
    def _get_change_summary(self) -> str:
        """Get a summary of changes for status display"""
        if not self.comparison_result:
            return "No comparison performed"
            
        added = len(self.comparison_result.get('added', []))
        deleted = len(self.comparison_result.get('deleted', []))
        content_modified = len(self.comparison_result.get('content_modified', []))
        structural_only = len(self.comparison_result.get('structural_only', []))
        unchanged = len(self.comparison_result.get('unchanged', []))
        
        total_changes = added + deleted + content_modified + structural_only
        
        if total_changes == 0:
            return f"Files identical ({unchanged} requirements)"
        else:
            change_parts = []
            if added > 0:
                change_parts.append(f"+{added}")
            if deleted > 0:
                change_parts.append(f"-{deleted}")
            if content_modified > 0:
                change_parts.append(f"~{content_modified}")
            if structural_only > 0:
                change_parts.append(f"#{structural_only}")
                
            return f"Changes: {' '.join(change_parts)} | Unchanged: {unchanged}"
            
    def _validate_files(self) -> bool:
        """Validate selected files before comparison"""
        file1 = self.file1_var.get().strip()
        file2 = self.file2_var.get().strip()
        
        if not file1 or not file2:
            messagebox.showerror("Error", "Please select both files for comparison")
            return False
            
        if not os.path.exists(file1):
            messagebox.showerror("Error", f"Original file not found:\n{file1}")
            return False
            
        if not os.path.exists(file2):
            messagebox.showerror("Error", f"Modified file not found:\n{file2}")
            return False
            
        # Check file extensions
        if not (file1.lower().endswith('.reqif') or file1.lower().endswith('.xml')):
            result = messagebox.askyesno("Warning", 
                f"Original file may not be a ReqIF file:\n{file1}\n\nContinue anyway?")
            if not result:
                return False
                
        if not (file2.lower().endswith('.reqif') or file2.lower().endswith('.xml')):
            result = messagebox.askyesno("Warning", 
                f"Modified file may not be a ReqIF file:\n{file2}\n\nContinue anyway?")
            if not result:
                return False
                
        return True


def main():
    """Main function to run the comparison GUI"""
    root = tk.Tk()
    app = ComparisonGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()