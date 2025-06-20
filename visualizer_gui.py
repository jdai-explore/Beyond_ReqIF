#!/usr/bin/env python3
"""
Visualizer GUI Module
Handles the display and exploration of requirements from a single ReqIF file.
Enhanced with intelligent content prioritization and quality analysis.
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
        """Create the enhanced requirements table view with intelligent column selection"""
        table_frame = ttk.Frame(self.notebook)
        self.notebook.add(table_frame, text="📋 Requirements Table")
        
        # Intelligently determine columns based on content quality
        base_columns = ['ID', 'Title', 'Type', 'Description']
        
        # Analyze all requirements to find meaningful attributes
        meaningful_attrs = self._analyze_meaningful_attributes()
        
        # Add top meaningful attributes as columns (limit for readability)
        additional_columns = meaningful_attrs[:2]  # Show top 2 meaningful attributes
        columns = base_columns + additional_columns
        
        # Create treeview with enhanced styling
        tree_frame = ttk.Frame(table_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=20)
        
        # Configure base columns with icons and smart widths
        self.tree.heading('ID', text='🆔 Requirement ID')
        self.tree.heading('Title', text='📝 Title')
        self.tree.heading('Type', text='🏷️ Type')
        self.tree.heading('Description', text='📄 Description')
        
        # Smart column widths based on content
        self.tree.column('ID', width=120, minwidth=80)
        self.tree.column('Title', width=300, minwidth=200)  # Larger for titles
        self.tree.column('Type', width=140, minwidth=100)
        self.tree.column('Description', width=350, minwidth=250)  # Larger for descriptions
        
        # Configure meaningful attribute columns
        for attr in additional_columns:
            self.tree.heading(attr, text=f'⚙️ {attr}')
            self.tree.column(attr, width=180, minwidth=120)
        
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
        
        # Enhanced status section
        status_frame = ttk.Frame(table_frame)
        status_frame.pack(fill=tk.X, padx=10, pady=(5, 10))
        
        # Content quality indicator
        self.content_quality_label = ttk.Label(status_frame, text="", font=('Arial', 9, 'bold'))
        self.content_quality_label.pack(side=tk.LEFT)
        
        # Main status label
        self.status_label = ttk.Label(status_frame, text="", font=('Arial', 9, 'italic'))
        self.status_label.pack(side=tk.LEFT, padx=(20, 0))
        
        # Quick stats in status area
        self.quick_stats_label = ttk.Label(status_frame, text="", font=('Arial', 9))
        self.quick_stats_label.pack(side=tk.RIGHT)
        
        # Store column info for population
        self.table_columns = columns
        self.meaningful_attrs = additional_columns
        
    def _analyze_meaningful_attributes(self) -> List[str]:
        """Analyze requirements to identify most meaningful attributes for display"""
        if not self.requirements:
            return []
        
        # Score all attributes by meaningfulness
        attr_scores = {}
        
        for req in self.requirements:
            for attr_name, attr_value in req.get('attributes', {}).items():
                if not attr_value or attr_name in ['Title', 'Description', 'Type']:
                    continue  # Skip empty or already displayed attributes
                
                if attr_name not in attr_scores:
                    attr_scores[attr_name] = {
                        'count': 0,
                        'total_length': 0,
                        'unique_values': set(),
                        'looks_meaningful': 0
                    }
                
                attr_scores[attr_name]['count'] += 1
                attr_scores[attr_name]['total_length'] += len(str(attr_value))
                attr_scores[attr_name]['unique_values'].add(str(attr_value)[:50])  # Limit for set size
                
                # Check if content looks meaningful (not just references)
                if self._looks_like_meaningful_content(str(attr_value)):
                    attr_scores[attr_name]['looks_meaningful'] += 1
        
        # Calculate meaningfulness score for each attribute
        scored_attributes = []
        total_reqs = len(self.requirements)
        
        for attr_name, scores in attr_scores.items():
            if scores['count'] < total_reqs * 0.1:  # Skip if less than 10% have this attribute
                continue
            
            # Calculate composite score
            coverage = scores['count'] / total_reqs  # How many requirements have this
            avg_length = scores['total_length'] / scores['count']  # Average content length
            uniqueness = len(scores['unique_values']) / scores['count']  # Value diversity
            meaningfulness = scores['looks_meaningful'] / scores['count']  # Content quality
            
            # Weighted composite score
            composite_score = (
                coverage * 0.3 +           # 30% weight for coverage
                min(avg_length / 50, 1) * 0.2 +  # 20% weight for length (capped)
                uniqueness * 0.2 +         # 20% weight for uniqueness
                meaningfulness * 0.3       # 30% weight for meaningfulness
            )
            
            scored_attributes.append((attr_name, composite_score))
        
        # Sort by score and return top attributes
        scored_attributes.sort(key=lambda x: x[1], reverse=True)
        return [attr[0] for attr in scored_attributes]
    
    def _looks_like_meaningful_content(self, content: str) -> bool:
        """Determine if content looks like meaningful human-readable text"""
        if not content or len(content) < 3:
            return False
        
        # Content is likely meaningful if:
        # - Has spaces (not just an ID)
        # - Doesn't have too many underscores or technical patterns
        # - Has reasonable length
        # - Contains some letters
        
        has_spaces = ' ' in content
        not_too_technical = content.count('_') < len(content) * 0.3
        reasonable_length = 3 <= len(content) <= 500
        has_letters = any(c.isalpha() for c in content)
        not_just_numbers = not content.replace('.', '').replace('-', '').isdigit()
        
        return has_spaces and not_too_technical and reasonable_length and has_letters and not_just_numbers
        
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
        """Populate the requirements table with enhanced content validation"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Track content quality for user feedback
        content_issues = 0
        
        # Add filtered requirements with enhanced data validation
        for req in self.filtered_requirements:
            # Build row values for all columns
            row_values = []
            
            # ID column
            req_id = req.get('id', '')
            row_values.append(req_id)
            
            # Title column with content validation
            title = req.get('title', '')
            if not title or title == req_id:
                # Try to find better title from attributes
                title = self._find_better_title(req) or req_id or 'Untitled'
                if title == req_id:
                    content_issues += 1
            
            # Truncate long titles but keep them readable
            if len(title) > 60:
                title = title[:57] + "..."
            row_values.append(title)
            
            # Type column with fallback
            req_type = req.get('type', '')
            if not req_type:
                req_type = req.get('type_ref', 'Unknown')
            if len(req_type) > 25:
                req_type = req_type[:22] + "..."
            row_values.append(req_type)
            
            # Description column with content validation
            description = req.get('description', '')
            if not description:
                # Try to find description-like content
                description = self._find_description_content(req) or 'No description available'
                if description == 'No description available':
                    content_issues += 1
            
            # Smart truncation for descriptions
            if len(description) > 120:
                description = description[:117] + "..."
            row_values.append(description)
            
            # Additional meaningful attribute columns
            if hasattr(self, 'meaningful_attrs'):
                for attr in self.meaningful_attrs:
                    attr_value = req.get('attributes', {}).get(attr, '')
                    if len(str(attr_value)) > 35:
                        attr_value = str(attr_value)[:32] + "..."
                    row_values.append(str(attr_value))
            
            # Insert row
            item_id = self.tree.insert('', tk.END, values=row_values)
        
        # Update status with enhanced information
        total = len(self.requirements)
        showing = len(self.filtered_requirements)
        
        if total == showing:
            status_text = f"📊 Showing all {total} requirements"
        else:
            status_text = f"🔍 Showing {showing} of {total} requirements"
        self.status_label.config(text=status_text)
        
        # Update content quality indicator
        if hasattr(self, 'content_quality_label'):
            if content_issues == 0:
                quality_text = "✅ Good content quality"
            elif content_issues < showing * 0.1:
                quality_text = f"⚠️ Minor content issues ({content_issues})"
            else:
                quality_text = f"❌ Content quality issues ({content_issues})"
            
            self.content_quality_label.config(text=quality_text)
        
        # Update quick stats with meaningful metrics
        if hasattr(self, 'quick_stats_label'):
            with_good_titles = len([r for r in self.filtered_requirements 
                                  if r.get('title') and r.get('title') != r.get('id')])
            with_descriptions = len([r for r in self.filtered_requirements 
                                   if r.get('description') and r.get('description') != 'No description available'])
            with_types = len([r for r in self.filtered_requirements if r.get('type')])
            
            quick_stats = f"📝 {with_good_titles} meaningful titles | 📄 {with_descriptions} descriptions | 🏷️ {with_types} types"
            self.quick_stats_label.config(text=quick_stats)
    
    def _find_better_title(self, req: Dict[str, Any]) -> str:
        """Try to find a better title from attributes if main title is poor"""
        attributes = req.get('attributes', {})
        
        # Look for attributes that might contain better titles
        title_candidates = []
        for attr_name, attr_value in attributes.items():
            if not attr_value:
                continue
                
            attr_lower = attr_name.lower()
            # Look for title-like attributes
            if any(keyword in attr_lower for keyword in ['name', 'summary', 'caption', 'label', 'heading']):
                if self._looks_like_meaningful_content(str(attr_value)):
                    title_candidates.append(str(attr_value))
        
        # Return the shortest meaningful candidate (likely to be a good title)
        if title_candidates:
            return min(title_candidates, key=len)
        
        return ''
    
    def _find_description_content(self, req: Dict[str, Any]) -> str:
        """Try to find description-like content from attributes"""
        attributes = req.get('attributes', {})
        
        # Look for attributes that might contain description content
        description_candidates = []
        for attr_name, attr_value in attributes.items():
            if not attr_value:
                continue
                
            attr_lower = attr_name.lower()
            # Look for description-like attributes
            if any(keyword in attr_lower for keyword in ['text', 'detail', 'content', 'specification', 'rationale']):
                if self._looks_like_meaningful_content(str(attr_value)) and len(str(attr_value)) > 10:
                    description_candidates.append(str(attr_value))
        
        # Return the longest meaningful candidate (likely to be a good description)
        if description_candidates:
            return max(description_candidates, key=len)
        
        return ''
        
    def update_statistics(self):
        """Update the statistics display with enhanced content analysis"""
        # Clear existing statistics
        for widget in self.stats_container.winfo_children():
            widget.destroy()
        
        # Content Quality Analysis
        quality_frame = ttk.LabelFrame(self.stats_container, text="📊 Content Quality Analysis", padding="10")
        quality_frame.pack(fill=tk.X, pady=(0, 10))
        
        total_reqs = len(self.requirements)
        
        # Analyze content quality
        meaningful_titles = len([r for r in self.requirements 
                               if r.get('title') and r.get('title') != r.get('id') 
                               and self._looks_like_meaningful_content(r.get('title', ''))])
        
        good_descriptions = len([r for r in self.requirements 
                               if r.get('description') and len(r.get('description', '')) > 20
                               and self._looks_like_meaningful_content(r.get('description', ''))])
        
        resolved_types = len([r for r in self.requirements 
                            if r.get('type') and not r.get('type', '').startswith('_')])
        
        quality_text = f"""Content Quality Assessment:
✅ Meaningful Titles: {meaningful_titles} ({meaningful_titles/total_reqs*100:.1f}%)
✅ Rich Descriptions: {good_descriptions} ({good_descriptions/total_reqs*100:.1f}%)
✅ Resolved Types: {resolved_types} ({resolved_types/total_reqs*100:.1f}%)

Total Requirements: {total_reqs}
Currently Displayed: {len(self.filtered_requirements)}
"""
        
        ttk.Label(quality_frame, text=quality_text, justify=tk.LEFT).pack(anchor=tk.W)
        
        # Basic statistics for backward compatibility
        stats_frame = ttk.LabelFrame(self.stats_container, text="📋 Basic Statistics", padding="10")
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        with_title = len([r for r in self.requirements if r.get('title')])
        with_description = len([r for r in self.requirements if r.get('description')])
        with_type = len([r for r in self.requirements if r.get('type')])
        
        basic_stats = f"""Field Presence:
📝 Title: {with_title} ({with_title/total_reqs*100:.1f}%)
📄 Description: {with_description} ({with_description/total_reqs*100:.1f}%)
🏷️ Type: {with_type} ({with_type/total_reqs*100:.1f}%)
"""
        
        ttk.Label(stats_frame, text=basic_stats, justify=tk.LEFT).pack(anchor=tk.W)
        
    def on_search_change(self, *args):
        """Handle search text changes with enhanced search across resolved content"""
        search_term = self.search_var.get().lower()
        
        if not search_term:
            self.filtered_requirements = self.requirements.copy()
            self.search_info_label.config(text="")
        else:
            # Enhanced search across all meaningful content
            self.filtered_requirements = []
            for req in self.requirements:
                # Search in all meaningful fields including resolved content
                searchable_content = []
                
                # Basic fields
                searchable_content.extend([
                    req.get('id', ''),
                    req.get('title', ''),
                    req.get('description', ''),
                    req.get('type', ''),
                    req.get('priority', ''),
                    req.get('status', '')
                ])
                
                # All resolved attributes
                for attr_value in req.get('attributes', {}).values():
                    if attr_value:
                        searchable_content.append(str(attr_value))
                
                # Create searchable text
                searchable_text = ' '.join(searchable_content).lower()
                
                if search_term in searchable_text:
                    self.filtered_requirements.append(req)
            
            # Update search info with enhanced feedback
            total = len(self.requirements)
            found = len(self.filtered_requirements)
            if found == 0:
                self.search_info_label.config(text=f"🔍 No matches found for '{search_term}'")
            elif found == total:
                self.search_info_label.config(text=f"🔍 All requirements match '{search_term}'")
            else:
                self.search_info_label.config(text=f"🔍 Found {found} of {total} requirements matching '{search_term}'")
        
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
    print("Enhanced Visualizer GUI module loaded successfully.")
    print("Features: Intelligent content prioritization, quality analysis, enhanced search")