#!/usr/bin/env python3
"""
Advanced Comparison Settings GUI
Phase 1: Attribute Selection Interface
Phase 2: Comparison Rules Interface
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import os
from typing import Dict, List, Any, Optional, Tuple
from comparison_profile import ComparisonProfile, ProfileManager, AttributeConfig
from attribute_analyzer import AttributeAnalyzer, AttributeStats, analyze_requirements_for_profile


class AdvancedComparisonSettings:
    """
    GUI for advanced comparison settings including attribute selection and rules
    """
    
    def __init__(self, parent: tk.Widget, requirements1: List[Dict] = None, 
                 requirements2: List[Dict] = None, current_profile: ComparisonProfile = None):
        self.parent = parent
        self.requirements1 = requirements1 or []
        self.requirements2 = requirements2 or []
        self.current_profile = current_profile or ComparisonProfile("Custom Profile")
        
        # Analysis results
        self.attribute_stats: Dict[str, AttributeStats] = {}
        self.profile_manager = ProfileManager()
        
        # GUI state
        self.result_profile: Optional[ComparisonProfile] = None
        self.weight_vars: Dict[str, tk.DoubleVar] = {}
        self.enabled_vars: Dict[str, tk.BooleanVar] = {}
        
        # Create window
        self._create_window()
        
        # Load profile manager profiles
        self.profile_manager.load_profiles_from_directory()
        
        # Analyze requirements if provided
        if self.requirements1:
            self._analyze_requirements()
        
        # Setup GUI
        self._setup_gui()
        
        # Load current profile into GUI
        self._load_profile_into_gui()
    
    def _create_window(self):
        """Create the main settings window"""
        self.window = tk.Toplevel(self.parent)
        self.window.title("Advanced Comparison Settings")
        self.window.geometry("900x700")
        self.window.transient(self.parent)
        self.window.grab_set()
        
        # Center window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (self.window.winfo_width() // 2)
        y = (self.window.winfo_screenheight() // 2) - (self.window.winfo_height() // 2)
        self.window.geometry(f"+{x}+{y}")
        
        # Configure grid
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        
        # Handle window closing
        self.window.protocol("WM_DELETE_WINDOW", self._on_cancel)
    
    def _setup_gui(self):
        """Setup the main GUI components"""
        # Main container
        main_frame = ttk.Frame(self.window, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Header
        self._create_header(main_frame)
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        
        # Create tabs
        self._create_attribute_selection_tab()
        self._create_comparison_rules_tab()
        self._create_profile_management_tab()
        
        # Buttons
        self._create_buttons(main_frame)
    
    def _create_header(self, parent):
        """Create header section"""
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        header_frame.columnconfigure(1, weight=1)
        
        # Title and description
        ttk.Label(header_frame, text="Advanced Comparison Settings", 
                 font=("Helvetica", 14, "bold")).grid(row=0, column=0, columnspan=2, sticky=(tk.W))
        
        ttk.Label(header_frame, text="Configure which attributes to compare and how to compare them",
                 foreground="gray").grid(row=1, column=0, columnspan=2, sticky=(tk.W), pady=(5, 0))
        
        # Analysis info
        if self.attribute_stats:
            info_text = f"Found {len(self.attribute_stats)} attributes from {len(self.requirements1 + self.requirements2)} requirements"
            ttk.Label(header_frame, text=info_text, 
                     font=("Helvetica", 9), foreground="blue").grid(row=2, column=0, columnspan=2, sticky=(tk.W), pady=(5, 0))
    
    def _create_attribute_selection_tab(self):
        """Create attribute selection tab (Phase 1)"""
        # Create tab frame
        attr_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(attr_frame, text="Attribute Selection")
        
        # Configure grid
        attr_frame.columnconfigure(0, weight=1)
        attr_frame.rowconfigure(1, weight=1)
        
        # Controls frame
        controls_frame = ttk.Frame(attr_frame)
        controls_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(controls_frame, text="Select All", 
                  command=self._select_all_attributes).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(controls_frame, text="Select None", 
                  command=self._select_no_attributes).grid(row=0, column=1, padx=(0, 5))
        ttk.Button(controls_frame, text="Reset Weights", 
                  command=self._reset_weights).grid(row=0, column=2, padx=(0, 15))
        
        ttk.Button(controls_frame, text="Auto-Select Recommended", 
                  command=self._auto_select_recommended).grid(row=0, column=3, padx=(0, 5))
        
        # Info label
        self.selection_info_label = ttk.Label(controls_frame, text="", foreground="gray")
        self.selection_info_label.grid(row=0, column=4, sticky=(tk.E), padx=(15, 0))
        controls_frame.columnconfigure(4, weight=1)
        
        # Attributes list frame
        list_frame = ttk.Frame(attr_frame)
        list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Create treeview for attributes
        columns = ('enabled', 'weight', 'coverage', 'data_type', 'samples')
        self.attr_tree = ttk.Treeview(list_frame, columns=columns, show='tree headings', height=15)
        self.attr_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure columns
        self.attr_tree.heading('#0', text='Attribute Name', anchor=tk.W)
        self.attr_tree.column('#0', width=200, minwidth=150)
        
        self.attr_tree.heading('enabled', text='✓', anchor=tk.CENTER)
        self.attr_tree.column('enabled', width=30, minwidth=30, stretch=False)
        
        self.attr_tree.heading('weight', text='Weight', anchor=tk.CENTER)
        self.attr_tree.column('weight', width=80, minwidth=60, stretch=False)
        
        self.attr_tree.heading('coverage', text='Coverage', anchor=tk.CENTER)
        self.attr_tree.column('coverage', width=80, minwidth=60, stretch=False)
        
        self.attr_tree.heading('data_type', text='Type', anchor=tk.CENTER)
        self.attr_tree.column('data_type', width=80, minwidth=60, stretch=False)
        
        self.attr_tree.heading('samples', text='Sample Values', anchor=tk.W)
        self.attr_tree.column('samples', width=250, minwidth=150)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.attr_tree.yview)
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.attr_tree.configure(yscrollcommand=v_scrollbar.set)
        
        h_scrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.attr_tree.xview)
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.attr_tree.configure(xscrollcommand=h_scrollbar.set)
        
        # Bind events
        self.attr_tree.bind('<Double-1>', self._on_attribute_double_click)
        self.attr_tree.bind('<Button-1>', self._on_attribute_click)
        
        # Populate attributes
        self._populate_attribute_tree()
    
    def _create_comparison_rules_tab(self):
        """Create comparison rules tab (Phase 2)"""
        rules_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(rules_frame, text="Comparison Rules")
        
        # Configure grid
        rules_frame.columnconfigure(0, weight=1)
        
        row = 0
        
        # Similarity threshold
        threshold_frame = ttk.LabelFrame(rules_frame, text="Similarity Settings", padding="10")
        threshold_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        threshold_frame.columnconfigure(1, weight=1)
        
        ttk.Label(threshold_frame, text="Similarity Threshold:").grid(row=0, column=0, sticky=(tk.W), padx=(0, 10))
        
        self.threshold_var = tk.DoubleVar(value=self.current_profile.similarity_threshold)
        threshold_scale = ttk.Scale(threshold_frame, from_=0.0, to=1.0, 
                                   variable=self.threshold_var, orient=tk.HORIZONTAL)
        threshold_scale.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        self.threshold_label = ttk.Label(threshold_frame, text=f"{self.threshold_var.get():.0%}")
        self.threshold_label.grid(row=0, column=2, sticky=(tk.W))
        
        # Bind threshold change
        self.threshold_var.trace_add("write", self._on_threshold_change)
        
        ttk.Label(threshold_frame, text="Higher values = more strict comparison",
                 font=("Helvetica", 8), foreground="gray").grid(row=1, column=0, columnspan=3, sticky=(tk.W), pady=(5, 0))
        
        row += 1
        
        # Ignore settings
        ignore_frame = ttk.LabelFrame(rules_frame, text="Ignore Settings", padding="10")
        ignore_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        self.ignore_case_var = tk.BooleanVar(value=self.current_profile.ignore_case)
        ttk.Checkbutton(ignore_frame, text="Ignore case differences (ABC = abc)", 
                       variable=self.ignore_case_var).grid(row=0, column=0, sticky=(tk.W), pady=2)
        
        self.ignore_whitespace_var = tk.BooleanVar(value=self.current_profile.ignore_whitespace)
        ttk.Checkbutton(ignore_frame, text="Ignore whitespace changes (spaces, tabs, newlines)", 
                       variable=self.ignore_whitespace_var).grid(row=1, column=0, sticky=(tk.W), pady=2)
        
        self.treat_empty_null_var = tk.BooleanVar(value=self.current_profile.treat_empty_as_null)
        ttk.Checkbutton(ignore_frame, text="Treat empty and null values as same", 
                       variable=self.treat_empty_null_var).grid(row=2, column=0, sticky=(tk.W), pady=2)
        
        self.fuzzy_matching_var = tk.BooleanVar(value=self.current_profile.use_fuzzy_matching)
        ttk.Checkbutton(ignore_frame, text="Use fuzzy string matching (slower but more flexible)", 
                       variable=self.fuzzy_matching_var).grid(row=3, column=0, sticky=(tk.W), pady=2)
        
        row += 1
        
        # Change significance
        significance_frame = ttk.LabelFrame(rules_frame, text="Change Significance", padding="10")
        significance_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        ttk.Label(significance_frame, text="Define what constitutes different levels of changes:",
                 font=("Helvetica", 9)).grid(row=0, column=0, columnspan=2, sticky=(tk.W), pady=(0, 10))
        
        # Significance thresholds (for future use)
        ttk.Label(significance_frame, text="Minor change threshold:").grid(row=1, column=0, sticky=(tk.W))
        self.minor_threshold_var = tk.DoubleVar(value=0.8)
        ttk.Scale(significance_frame, from_=0.5, to=1.0, variable=self.minor_threshold_var, 
                 orient=tk.HORIZONTAL).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0))
        
        ttk.Label(significance_frame, text="Major change threshold:").grid(row=2, column=0, sticky=(tk.W))
        self.major_threshold_var = tk.DoubleVar(value=0.5)
        ttk.Scale(significance_frame, from_=0.0, to=0.8, variable=self.major_threshold_var, 
                 orient=tk.HORIZONTAL).grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(10, 0))
        
        significance_frame.columnconfigure(1, weight=1)
        
        row += 1
        
        # Preview section
        preview_frame = ttk.LabelFrame(rules_frame, text="Settings Preview", padding="10")
        preview_frame.grid(row=row, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)
        rules_frame.rowconfigure(row, weight=1)
        
        self.preview_text = tk.Text(preview_frame, height=8, state=tk.DISABLED, 
                                   wrap=tk.WORD, font=("Consolas", 9))
        self.preview_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        preview_scroll = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=self.preview_text.yview)
        preview_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.preview_text.configure(yscrollcommand=preview_scroll.set)
        
        # Update preview
        self._update_rules_preview()
    
    def _create_profile_management_tab(self):
        """Create profile management tab"""
        profile_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(profile_frame, text="Profile Management")
        
        # Configure grid
        profile_frame.columnconfigure(0, weight=1)
        profile_frame.rowconfigure(1, weight=1)
        
        # Profile selection frame
        selection_frame = ttk.LabelFrame(profile_frame, text="Profile Selection", padding="10")
        selection_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        selection_frame.columnconfigure(1, weight=1)
        
        ttk.Label(selection_frame, text="Current Profile:").grid(row=0, column=0, sticky=(tk.W), padx=(0, 10))
        
        self.profile_var = tk.StringVar(value=self.current_profile.name)
        self.profile_combo = ttk.Combobox(selection_frame, textvariable=self.profile_var, 
                                         state='readonly', width=30)
        self.profile_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        self.profile_combo.bind('<<ComboboxSelected>>', self._on_profile_selected)
        
        # Profile action buttons
        ttk.Button(selection_frame, text="Load", command=self._load_selected_profile).grid(
            row=0, column=2, padx=(0, 5))
        ttk.Button(selection_frame, text="Save As...", command=self._save_profile_as).grid(
            row=0, column=3, padx=(0, 5))
        ttk.Button(selection_frame, text="Delete", command=self._delete_profile).grid(
            row=0, column=4)
        
        # Profile details frame
        details_frame = ttk.LabelFrame(profile_frame, text="Profile Details", padding="10")
        details_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        details_frame.columnconfigure(0, weight=1)
        details_frame.rowconfigure(1, weight=1)
        
        # Profile info
        info_frame = ttk.Frame(details_frame)
        info_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        info_frame.columnconfigure(1, weight=1)
        
        ttk.Label(info_frame, text="Name:").grid(row=0, column=0, sticky=(tk.W), padx=(0, 10))
        self.profile_name_var = tk.StringVar(value=self.current_profile.name)
        ttk.Entry(info_frame, textvariable=self.profile_name_var).grid(
            row=0, column=1, sticky=(tk.W, tk.E), pady=2)
        
        ttk.Label(info_frame, text="Description:").grid(row=1, column=0, sticky=(tk.W), padx=(0, 10))
        self.profile_desc_var = tk.StringVar(value=self.current_profile.description)
        ttk.Entry(info_frame, textvariable=self.profile_desc_var).grid(
            row=1, column=1, sticky=(tk.W, tk.E), pady=2)
        
        # Profile summary
        summary_frame = ttk.Frame(details_frame)
        summary_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        summary_frame.columnconfigure(0, weight=1)
        summary_frame.rowconfigure(0, weight=1)
        
        self.profile_summary_text = tk.Text(summary_frame, height=12, state=tk.DISABLED, 
                                           wrap=tk.WORD, font=("Consolas", 9))
        self.profile_summary_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        summary_scroll = ttk.Scrollbar(summary_frame, orient=tk.VERTICAL, 
                                      command=self.profile_summary_text.yview)
        summary_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.profile_summary_text.configure(yscrollcommand=summary_scroll.set)
        
        # Import/Export buttons
        io_frame = ttk.Frame(details_frame)
        io_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Button(io_frame, text="Export Profile...", command=self._export_profile).grid(
            row=0, column=0, padx=(0, 10))
        ttk.Button(io_frame, text="Import Profile...", command=self._import_profile).grid(
            row=0, column=1)
        
        # Update profile list and summary
        self._update_profile_list()
        self._update_profile_summary()
    
    def _create_buttons(self, parent):
        """Create main action buttons"""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
        # Left side buttons
        ttk.Button(button_frame, text="Reset to Defaults", 
                  command=self._reset_to_defaults).grid(row=0, column=0, padx=(0, 10))
        
        # Right side buttons
        ttk.Button(button_frame, text="Cancel", command=self._on_cancel).grid(
            row=0, column=2, padx=(0, 10))
        ttk.Button(button_frame, text="Apply", command=self._on_apply).grid(
            row=0, column=3, padx=(0, 10))
        ttk.Button(button_frame, text="OK", command=self._on_ok).grid(row=0, column=4)
        
        # Expand middle column
        button_frame.columnconfigure(1, weight=1)
    
    def _analyze_requirements(self):
        """Analyze requirements to discover attributes"""
        try:
            self.attribute_stats = analyze_requirements_for_profile(
                self.requirements1, self.requirements2
            )
            print(f"Analysis complete: {len(self.attribute_stats)} attributes found")
        except Exception as e:
            print(f"Error analyzing requirements: {e}")
            messagebox.showerror("Analysis Error", f"Failed to analyze requirements:\n{str(e)}")
    
    def _populate_attribute_tree(self):
        """Populate the attribute tree with available attributes"""
        # Clear existing items
        for item in self.attr_tree.get_children():
            self.attr_tree.delete(item)
        
        self.weight_vars.clear()
        self.enabled_vars.clear()
        
        if not self.attribute_stats:
            # Show message if no analysis available
            self.attr_tree.insert('', 'end', text='No attribute analysis available', 
                                 values=('', '', '', '', 'Load requirements to see available attributes'))
            return
        
        # Group attributes by type
        standard_attrs = []
        custom_attrs = []
        
        for name, stats in self.attribute_stats.items():
            if stats.field_type == "standard":
                standard_attrs.append((name, stats))
            else:
                custom_attrs.append((name, stats))
        
        # Sort by coverage (highest first)
        standard_attrs.sort(key=lambda x: x[1].coverage, reverse=True)
        custom_attrs.sort(key=lambda x: x[1].coverage, reverse=True)
        
        # Insert standard attributes
        if standard_attrs:
            std_parent = self.attr_tree.insert('', 'end', text='Standard Fields', 
                                              values=('', '', '', '', ''), open=True)
            for name, stats in standard_attrs:
                self._insert_attribute_item(std_parent, name, stats)
        
        # Insert custom attributes
        if custom_attrs:
            custom_parent = self.attr_tree.insert('', 'end', text='Custom Attributes', 
                                                 values=('', '', '', '', ''), open=True)
            for name, stats in custom_attrs:
                self._insert_attribute_item(custom_parent, name, stats)
        
        self._update_selection_info()
    
    def _insert_attribute_item(self, parent, name: str, stats: AttributeStats):
        """Insert a single attribute item into the tree"""
        # Get current profile settings
        attr_config = self.current_profile.attributes.get(name)
        if attr_config:
            enabled = attr_config.enabled
            weight = attr_config.weight
        else:
            enabled = stats.coverage > 0.3  # Auto-enable if good coverage
            weight = stats.suggested_weight
        
        # Create variables
        enabled_var = tk.BooleanVar(value=enabled)
        weight_var = tk.DoubleVar(value=weight)
        
        self.enabled_vars[name] = enabled_var
        self.weight_vars[name] = weight_var
        
        # Format values for display
        enabled_display = "✓" if enabled else ""
        weight_display = f"{weight:.2f}"
        coverage_display = f"{stats.coverage:.1%}"
        samples_display = ", ".join(stats.sample_values[:3])
        if len(stats.sample_values) > 3:
            samples_display += "..."
        
        # Insert item
        item_id = self.attr_tree.insert(parent, 'end', text=stats.display_name,
                                       values=(enabled_display, weight_display, 
                                              coverage_display, stats.data_type, 
                                              samples_display),
                                       tags=[name])
        
        # Bind variable changes
        enabled_var.trace_add("write", lambda *args, n=name: self._on_attribute_changed(n))
        weight_var.trace_add("write", lambda *args, n=name: self._on_attribute_changed(n))
    
    def _on_attribute_click(self, event):
        """Handle single click on attribute"""
        item = self.attr_tree.selection()[0] if self.attr_tree.selection() else None
        if not item:
            return
        
        # Get attribute name from tags
        tags = self.attr_tree.item(item, 'tags')
        if not tags:
            return
        
        attr_name = tags[0]
        
        # Toggle enabled state on click in enabled column
        region = self.attr_tree.identify_region(event.x, event.y)
        column = self.attr_tree.identify_column(event.x, event.y)
        
        if region == "cell" and column == "#1":  # Enabled column
            if attr_name in self.enabled_vars:
                current_value = self.enabled_vars[attr_name].get()
                self.enabled_vars[attr_name].set(not current_value)
    
    def _on_attribute_double_click(self, event):
        """Handle double-click on attribute to edit weight"""
        item = self.attr_tree.selection()[0] if self.attr_tree.selection() else None
        if not item:
            return
        
        tags = self.attr_tree.item(item, 'tags')
        if not tags:
            return
        
        attr_name = tags[0]
        
        # Show weight editor dialog
        self._show_weight_editor(attr_name)
    
    def _show_weight_editor(self, attr_name: str):
        """Show dialog to edit attribute weight"""
        if attr_name not in self.weight_vars:
            return
        
        stats = self.attribute_stats.get(attr_name)
        if not stats:
            return
        
        # Create dialog
        dialog = tk.Toplevel(self.window)
        dialog.title(f"Edit Weight - {stats.display_name}")
        dialog.geometry("400x300")
        dialog.transient(self.window)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = dialog.winfo_screenwidth() // 2 - dialog.winfo_width() // 2
        y = dialog.winfo_screenheight() // 2 - dialog.winfo_height() // 2
        dialog.geometry(f"+{x}+{y}")
        
        main_frame = ttk.Frame(dialog, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        dialog.columnconfigure(0, weight=1)
        dialog.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # Title
        ttk.Label(main_frame, text=f"Attribute: {stats.display_name}", 
                 font=("Helvetica", 12, "bold")).grid(row=0, column=0, sticky=(tk.W), pady=(0, 10))
        
        # Attribute info
        info_frame = ttk.Frame(main_frame)
        info_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        ttk.Label(info_frame, text=f"Coverage: {stats.coverage:.1%}").grid(row=0, column=0, sticky=(tk.W))
        ttk.Label(info_frame, text=f"Data Type: {stats.data_type}").grid(row=1, column=0, sticky=(tk.W))
        ttk.Label(info_frame, text=f"Unique Values: {stats.unique_values}").grid(row=2, column=0, sticky=(tk.W))
        
        # Weight editor
        weight_frame = ttk.LabelFrame(main_frame, text="Weight", padding="10")
        weight_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        weight_frame.columnconfigure(1, weight=1)
        
        weight_var = tk.DoubleVar(value=self.weight_vars[attr_name].get())
        
        ttk.Label(weight_frame, text="Weight:").grid(row=0, column=0, sticky=(tk.W), padx=(0, 10))
        weight_scale = ttk.Scale(weight_frame, from_=0.0, to=1.0, variable=weight_var, 
                               orient=tk.HORIZONTAL)
        weight_scale.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        weight_label = ttk.Label(weight_frame, text=f"{weight_var.get():.2f}")
        weight_label.grid(row=0, column=2, sticky=(tk.W))
        
        def update_weight_label(*args):
            weight_label.configure(text=f"{weight_var.get():.2f}")
        
        weight_var.trace_add("write", update_weight_label)
        
        # Preset buttons
        preset_frame = ttk.Frame(weight_frame)
        preset_frame.grid(row=1, column=0, columnspan=3, pady=(10, 0))
        
        ttk.Button(preset_frame, text="Low (0.2)", 
                  command=lambda: weight_var.set(0.2)).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(preset_frame, text="Medium (0.5)", 
                  command=lambda: weight_var.set(0.5)).grid(row=0, column=1, padx=(0, 5))
        ttk.Button(preset_frame, text="High (0.8)", 
                  command=lambda: weight_var.set(0.8)).grid(row=0, column=2, padx=(0, 5))
        ttk.Button(preset_frame, text="Critical (1.0)", 
                  command=lambda: weight_var.set(1.0)).grid(row=0, column=3)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, sticky=(tk.W, tk.E))
        
        def apply_weight():
            self.weight_vars[attr_name].set(weight_var.get())
            dialog.destroy()
        
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).grid(
            row=0, column=0, padx=(0, 10))
        ttk.Button(button_frame, text="Apply", command=apply_weight).grid(row=0, column=1)
        
        button_frame.columnconfigure(0, weight=1)
    
    def _on_attribute_changed(self, attr_name: str):
        """Handle attribute setting changes"""
        self._update_attribute_display(attr_name)
        self._update_selection_info()
        self._update_profile_summary()
        self._update_rules_preview()
    
    def _update_attribute_display(self, attr_name: str):
        """Update the display of a single attribute in the tree"""
        if attr_name not in self.enabled_vars or attr_name not in self.weight_vars:
            return
        
        enabled = self.enabled_vars[attr_name].get()
        weight = self.weight_vars[attr_name].get()
        
        # Find the item in the tree
        for item in self.attr_tree.get_children():
            for child in self.attr_tree.get_children(item):
                tags = self.attr_tree.item(child, 'tags')
                if tags and tags[0] == attr_name:
                    # Update values
                    current_values = list(self.attr_tree.item(child, 'values'))
                    current_values[0] = "✓" if enabled else ""
                    current_values[1] = f"{weight:.2f}"
                    self.attr_tree.item(child, values=current_values)
                    break
    
    def _update_selection_info(self):
        """Update the selection information label"""
        if not self.enabled_vars:
            self.selection_info_label.configure(text="")
            return
        
        enabled_count = sum(1 for var in self.enabled_vars.values() if var.get())
        total_count = len(self.enabled_vars)
        total_weight = sum(var.get() for name, var in self.weight_vars.items() 
                          if self.enabled_vars[name].get())
        
        info_text = f"Selected: {enabled_count}/{total_count} attributes, Total weight: {total_weight:.2f}"
        self.selection_info_label.configure(text=info_text)
    
    def _select_all_attributes(self):
        """Select all attributes"""
        for var in self.enabled_vars.values():
            var.set(True)
    
    def _select_no_attributes(self):
        """Deselect all attributes"""
        for var in self.enabled_vars.values():
            var.set(False)
    
    def _reset_weights(self):
        """Reset all weights to suggested values"""
        for attr_name, var in self.weight_vars.items():
            stats = self.attribute_stats.get(attr_name)
            if stats:
                var.set(stats.suggested_weight)
            else:
                var.set(1.0)
    
    def _auto_select_recommended(self):
        """Auto-select recommended attributes"""
        if not self.attribute_stats:
            return
        
        analyzer = AttributeAnalyzer()
        recommended = analyzer.get_recommended_attributes(self.attribute_stats)
        
        # Disable all first
        for var in self.enabled_vars.values():
            var.set(False)
        
        # Enable recommended
        for attr_name in recommended:
            if attr_name in self.enabled_vars:
                self.enabled_vars[attr_name].set(True)
        
        messagebox.showinfo("Auto-Selection", 
                           f"Selected {len(recommended)} recommended attributes for comparison.")
    
    def _on_threshold_change(self, *args):
        """Handle similarity threshold change"""
        self.threshold_label.configure(text=f"{self.threshold_var.get():.0%}")
        self._update_rules_preview()
    
    def _update_rules_preview(self):
        """Update the rules preview text"""
        self.preview_text.configure(state=tk.NORMAL)
        self.preview_text.delete(1.0, tk.END)
        
        # Build preview text
        lines = [
            "Comparison Rules Preview",
            "=" * 30,
            "",
            f"Similarity Threshold: {self.threshold_var.get():.1%}",
            f"Ignore Case: {'Yes' if self.ignore_case_var.get() else 'No'}",
            f"Ignore Whitespace: {'Yes' if self.ignore_whitespace_var.get() else 'No'}",
            f"Treat Empty as Null: {'Yes' if self.treat_empty_null_var.get() else 'No'}",
            f"Fuzzy Matching: {'Yes' if self.fuzzy_matching_var.get() else 'No'}",
            "",
            "Enabled Attributes:",
        ]
        
        if self.enabled_vars:
            enabled_attrs = [(name, self.weight_vars[name].get()) 
                           for name, var in self.enabled_vars.items() if var.get()]
            enabled_attrs.sort(key=lambda x: x[1], reverse=True)
            
            for name, weight in enabled_attrs:
                stats = self.attribute_stats.get(name)
                display_name = stats.display_name if stats else name
                lines.append(f"  • {display_name}: weight {weight:.2f}")
            
            if not enabled_attrs:
                lines.append("  (No attributes selected)")
        else:
            lines.append("  (No attributes available)")
        
        self.preview_text.insert(tk.END, "\n".join(lines))
        self.preview_text.configure(state=tk.DISABLED)
    
    def _update_profile_list(self):
        """Update the profile selection dropdown"""
        profiles = self.profile_manager.list_profiles()
        self.profile_combo['values'] = profiles
        
        if self.current_profile.name not in profiles:
            # Add current profile to list
            profiles.append(self.current_profile.name)
            self.profile_combo['values'] = profiles
    
    def _update_profile_summary(self):
        """Update the profile summary display"""
        self.profile_summary_text.configure(state=tk.NORMAL)
        self.profile_summary_text.delete(1.0, tk.END)
        
        # Create current profile from GUI settings
        current_profile = self._create_profile_from_gui()
        summary = current_profile.get_summary()
        
        lines = [
            f"Profile: {current_profile.name}",
            f"Description: {current_profile.description}",
            "",
            f"Total Attributes: {summary['total_attributes']}",
            f"Enabled Attributes: {summary['enabled_attributes']}",
            f"Total Weight: {summary['total_weight']:.2f}",
            f"Similarity Threshold: {summary['similarity_threshold']:.1%}",
            "",
            "Ignore Settings:",
            f"  Case: {'Yes' if summary['ignore_settings']['case'] else 'No'}",
            f"  Whitespace: {'Yes' if summary['ignore_settings']['whitespace'] else 'No'}",
            f"  Empty as Null: {'Yes' if summary['ignore_settings']['empty_as_null'] else 'No'}",
            "",
            f"Fuzzy Matching: {'Yes' if summary['fuzzy_matching'] else 'No'}",
            "",
            "Validation Issues:"
        ]
        
        issues = current_profile.validate()
        if issues:
            for issue in issues:
                lines.append(f"  ⚠ {issue}")
        else:
            lines.append("  ✓ No issues found")
        
        self.profile_summary_text.insert(tk.END, "\n".join(lines))
        self.profile_summary_text.configure(state=tk.DISABLED)
    
    def _create_profile_from_gui(self) -> ComparisonProfile:
        """Create a ComparisonProfile from current GUI settings"""
        profile = ComparisonProfile(self.profile_name_var.get())
        profile.description = self.profile_desc_var.get()
        
        # Clear existing attributes
        profile.attributes.clear()
        
        # Add attributes from GUI
        for attr_name in self.enabled_vars.keys():
            stats = self.attribute_stats.get(attr_name)
            if stats:
                profile.add_attribute(
                    name=attr_name,
                    display_name=stats.display_name,
                    field_type=stats.field_type,
                    data_type=stats.data_type,
                    enabled=self.enabled_vars[attr_name].get(),
                    weight=self.weight_vars[attr_name].get(),
                    coverage=stats.coverage
                )
        
        # Set comparison rules
        profile.similarity_threshold = self.threshold_var.get()
        profile.ignore_case = self.ignore_case_var.get()
        profile.ignore_whitespace = self.ignore_whitespace_var.get()
        profile.treat_empty_as_null = self.treat_empty_null_var.get()
        profile.use_fuzzy_matching = self.fuzzy_matching_var.get()
        
        return profile
    
    def _load_profile_into_gui(self):
        """Load current profile settings into GUI"""
        self.profile_name_var.set(self.current_profile.name)
        self.profile_desc_var.set(self.current_profile.description)
        
        # Update comparison rules
        self.threshold_var.set(self.current_profile.similarity_threshold)
        self.ignore_case_var.set(self.current_profile.ignore_case)
        self.ignore_whitespace_var.set(self.current_profile.ignore_whitespace)
        self.treat_empty_null_var.set(self.current_profile.treat_empty_as_null)
        self.fuzzy_matching_var.set(self.current_profile.use_fuzzy_matching)
        
        # Update attribute settings
        for attr_name, var in self.enabled_vars.items():
            attr_config = self.current_profile.attributes.get(attr_name)
            if attr_config:
                var.set(attr_config.enabled)
                if attr_name in self.weight_vars:
                    self.weight_vars[attr_name].set(attr_config.weight)
    
    def _on_profile_selected(self, event=None):
        """Handle profile selection change"""
        # This is handled by the Load button instead of auto-loading
        pass
    
    def _load_selected_profile(self):
        """Load the selected profile"""
        profile_name = self.profile_var.get()
        profile = self.profile_manager.get_profile(profile_name)
        
        if profile:
            self.current_profile = profile.clone()
            self._load_profile_into_gui()
            self._populate_attribute_tree()  # Refresh tree with new settings
            messagebox.showinfo("Profile Loaded", f"Profile '{profile_name}' loaded successfully.")
        else:
            messagebox.showerror("Load Error", f"Profile '{profile_name}' not found.")
    
    def _save_profile_as(self):
        """Save current settings as a new profile"""
        # Get name from user
        name = simpledialog.askstring("Save Profile", "Enter profile name:", 
                                     initialvalue=self.profile_name_var.get())
        if not name:
            return
        
        # Create profile from GUI
        profile = self._create_profile_from_gui()
        profile.name = name
        
        # Validate
        issues = profile.validate()
        if issues:
            messagebox.showerror("Validation Error", 
                               "Profile validation failed:\n" + "\n".join(issues))
            return
        
        # Save
        try:
            self.profile_manager.save_profile(profile)
            self._update_profile_list()
            self.profile_var.set(name)
            messagebox.showinfo("Profile Saved", f"Profile '{name}' saved successfully.")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save profile:\n{str(e)}")
    
    def _delete_profile(self):
        """Delete the selected profile"""
        profile_name = self.profile_var.get()
        
        if not profile_name:
            return
        
        profile = self.profile_manager.get_profile(profile_name)
        if profile and profile.is_system_profile:
            messagebox.showwarning("Cannot Delete", "Cannot delete system profiles.")
            return
        
        # Confirm deletion
        if messagebox.askyesno("Confirm Delete", 
                              f"Are you sure you want to delete profile '{profile_name}'?"):
            if self.profile_manager.remove_profile(profile_name):
                self._update_profile_list()
                if self.profile_combo['values']:
                    self.profile_var.set(self.profile_combo['values'][0])
                messagebox.showinfo("Profile Deleted", f"Profile '{profile_name}' deleted.")
            else:
                messagebox.showerror("Delete Error", f"Failed to delete profile '{profile_name}'.")
    
    def _export_profile(self):
        """Export current profile to file"""
        profile = self._create_profile_from_gui()
        
        filename = filedialog.asksaveasfilename(
            title="Export Profile",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile=f"{profile.name}.json"
        )
        
        if filename:
            try:
                profile.save_to_file(filename)
                messagebox.showinfo("Export Complete", f"Profile exported to:\n{filename}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export profile:\n{str(e)}")
    
    def _import_profile(self):
        """Import profile from file"""
        filename = filedialog.askopenfilename(
            title="Import Profile",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                imported_profile = self.profile_manager.import_profile(filename)
                if imported_profile:
                    self._update_profile_list()
                    self.profile_var.set(imported_profile.name)
                    messagebox.showinfo("Import Complete", 
                                       f"Profile '{imported_profile.name}' imported successfully.")
                else:
                    messagebox.showerror("Import Error", "Failed to import profile.")
            except Exception as e:
                messagebox.showerror("Import Error", f"Failed to import profile:\n{str(e)}")
    
    def _reset_to_defaults(self):
        """Reset all settings to defaults"""
        if messagebox.askyesno("Reset to Defaults", 
                              "Are you sure you want to reset all settings to defaults?"):
            self.current_profile.reset_to_defaults()
            self._load_profile_into_gui()
            self._populate_attribute_tree()
            messagebox.showinfo("Reset Complete", "Settings reset to defaults.")
    
    def _on_apply(self):
        """Apply current settings"""
        profile = self._create_profile_from_gui()
        issues = profile.validate()
        
        if issues:
            messagebox.showerror("Validation Error", 
                               "Settings validation failed:\n" + "\n".join(issues))
            return
        
        self.result_profile = profile
        messagebox.showinfo("Settings Applied", "Comparison settings applied successfully.")
    
    def _on_ok(self):
        """Apply settings and close window"""
        self._on_apply()
        if self.result_profile:
            self.window.destroy()
    
    def _on_cancel(self):
        """Cancel and close window"""
        self.result_profile = None
        self.window.destroy()
    
    def get_result_profile(self) -> Optional[ComparisonProfile]:
        """Get the result profile after dialog closes"""
        return self.result_profile


# Convenience function for easy integration
def show_advanced_comparison_settings(parent: tk.Widget, 
                                     requirements1: List[Dict] = None,
                                     requirements2: List[Dict] = None,
                                     current_profile: ComparisonProfile = None) -> Optional[ComparisonProfile]:
    """
    Show advanced comparison settings dialog and return selected profile
    
    Args:
        parent: Parent window
        requirements1: First set of requirements for analysis
        requirements2: Second set of requirements for analysis
        current_profile: Current comparison profile
        
    Returns:
        Selected comparison profile or None if cancelled
    """
    dialog = AdvancedComparisonSettings(parent, requirements1, requirements2, current_profile)
    parent.wait_window(dialog.window)
    return dialog.get_result_profile()


# Example usage and testing
if __name__ == "__main__":
    print("Advanced Comparison Settings - Testing")
    
    # Create test requirements for analysis
    test_requirements1 = [
        {
            'id': 'REQ-001',
            'title': 'System shall start',
            'description': 'The system shall start within 5 seconds',
            'type': 'functional',
            'priority': 'high',
            'status': 'approved',
            'attributes': {
                'safety_level': 'SIL-2',
                'verification_method': 'test',
                'source_document': 'SRS-001'
            }
        },
        {
            'id': 'REQ-002',
            'title': 'System shall stop',
            'description': 'The system shall stop safely',
            'type': 'functional', 
            'priority': 'critical',
            'status': 'draft',
            'attributes': {
                'safety_level': 'SIL-3',
                'verification_method': 'inspection'
            }
        }
    ]
    
    test_requirements2 = [
        {
            'id': 'REQ-001',
            'title': 'System shall start quickly',
            'description': 'The system shall start within 3 seconds',
            'type': 'functional',
            'priority': 'critical',
            'status': 'approved',
            'attributes': {
                'safety_level': 'SIL-3',
                'verification_method': 'test',
                'source_document': 'SRS-001'
            }
        },
        {
            'id': 'REQ-003',
            'title': 'Error handling',
            'description': 'System shall handle errors gracefully',
            'type': 'non-functional',
            'priority': 'medium',
            'status': 'draft',
            'attributes': {
                'safety_level': 'SIL-1',
                'verification_method': 'test'
            }
        }
    ]
    
    # Test with tkinter
    try:
        root = tk.Tk()
        root.title("Advanced Comparison Settings Test")
        root.geometry("300x200")
        
        def test_dialog():
            profile = show_advanced_comparison_settings(
                root, test_requirements1, test_requirements2
            )
            
            if profile:
                print(f"\nSelected profile: {profile.name}")
                print(f"Enabled attributes: {len(profile.get_enabled_attributes())}")
                print(f"Total weight: {profile.calculate_total_weight():.2f}")
                
                summary = profile.get_summary()
                print("\nProfile summary:")
                for key, value in summary.items():
                    print(f"  {key}: {value}")
            else:
                print("Dialog cancelled")
        
        ttk.Label(root, text="Advanced Comparison Settings Test", 
                 font=("Helvetica", 12, "bold")).pack(pady=20)
        
        ttk.Button(root, text="Open Advanced Settings", 
                  command=test_dialog).pack(pady=10)
        
        ttk.Button(root, text="Exit", command=root.quit).pack(pady=10)
        
        print("Starting GUI test...")
        print("Click 'Open Advanced Settings' to test the dialog")
        
        root.mainloop()
        
    except Exception as e:
        print(f"GUI test error: {e}")
        print("Testing components individually...")
        
        # Test profile creation
        profile = ComparisonProfile("Test Profile")
        profile.add_attribute("test_attr", "Test Attribute", weight=0.8)
        print(f"Created profile: {profile.name}")
        
        # Test analyzer
        analyzer = AttributeAnalyzer()
        stats = analyzer.analyze_requirements(test_requirements1)
        print(f"Analyzed {len(stats)} attributes")
        
        print("Component testing completed successfully!")
    
    print("\nAdvanced Comparison Settings testing completed!")