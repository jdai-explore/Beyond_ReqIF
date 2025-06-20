# Error icon and message
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Error icon (using emoji as fallback)
        icon_label = ttk.Label(header_frame, text="❌", font=('Segoe UI', 24))
        icon_label.pack(side=tk.LEFT, padx=(0, 15))
        
        # Message
        message_label = ttk.Label(header_frame, text=message, wraplength=400, justify=tk.LEFT)
        message_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Details section (if provided)
        if details:
            # Separator
            separator = ttk.Separator(main_frame, orient=tk.HORIZONTAL)
            separator.pack(fill=tk.X, pady=(0, 10))
            
            # Details label
            details_label = ttk.Label(main_frame, text="Error Details:", font=('Segoe UI', 10, 'bold'))
            details_label.pack(anchor=tk.W)
            
            # Details text area
            details_frame = ttk.Frame(main_frame)
            details_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 20))
            
            details_text = scrolledtext.ScrolledText(details_frame, wrap=tk.WORD, height=10, width=60)
            details_text.pack(fill=tk.BOTH, expand=True)
            details_text.insert(tk.END, details)
            details_text.config(state=tk.DISABLED)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Copy to clipboard button (if details exist)
        if details:
            def copy_details():
                dialog.clipboard_clear()
                dialog.clipboard_append(f"{message}\n\nDetails:\n{details}")
                messagebox.showinfo("Copied", "Error details copied to clipboard.")
            
            ttk.Button(button_frame, text="Copy Details", command=copy_details).pack(side=tk.LEFT)
        
        # OK button
        ttk.Button(button_frame, text="OK", command=dialog.destroy).pack(side=tk.RIGHT)
        
        # Center dialog on parent
        ErrorDialog._center_dialog(dialog, parent)
    
    @staticmethod
    def _center_dialog(dialog, parent):
        """Center dialog on parent window"""
        dialog.update_idletasks()
        
        # Get parent geometry
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        # Get dialog size
        dialog_width = dialog.winfo_width()
        dialog_height = dialog.winfo_height()
        
        # Calculate centered position
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        dialog.geometry(f"+{x}+{y}")


class AboutDialog:
    """
    About dialog with application information
    """
    
    def __init__(self, parent):
        """Initialize about dialog"""
        self.parent = parent
        self.create_dialog()
    
    def create_dialog(self):
        """Create the about dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("About ReqIF Tool Suite")
        self.dialog.geometry("500x600")
        self.dialog.resizable(False, False)
        
        # Center and configure
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Main frame with padding
        main_frame = ttk.Frame(self.dialog, padding="30")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Application icon and title
        self.create_header(main_frame)
        
        # Information sections
        self.create_info_sections(main_frame)
        
        # Buttons
        self.create_buttons(main_frame)
        
        # Center dialog
        self._center_dialog()
    
    def create_header(self, parent):
        """Create header with icon and title"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 30))
        
        # Application icon
        icon_label = ttk.Label(header_frame, text="📋", font=('Segoe UI', 48))
        icon_label.pack(pady=(0, 10))
        
        # Application title
        title_label = ttk.Label(header_frame, text="ReqIF Tool Suite", 
                               font=('Segoe UI', 18, 'bold'))
        title_label.pack()
        
        # Version
        version_label = ttk.Label(header_frame, text=f"Version {APP_CONFIG.VERSION}", 
                                 font=('Segoe UI', 12))
        version_label.pack(pady=(5, 0))
        
        # Subtitle
        subtitle_label = ttk.Label(header_frame, 
                                  text="Professional ReqIF Analysis and Comparison Tool",
                                  font=('Segoe UI', 10), foreground='gray')
        subtitle_label.pack(pady=(5, 0))
    
    def create_info_sections(self, parent):
        """Create information sections"""
        # Description
        desc_frame = ttk.LabelFrame(parent, text="Description", padding="10")
        desc_frame.pack(fill=tk.X, pady=(0, 15))
        
        description = (
            "ReqIF Tool Suite is a comprehensive application for working with "
            "Requirements Interchange Format (ReqIF) files. It provides powerful "
            "comparison, visualization, and analysis capabilities for requirements "
            "engineering workflows."
        )
        
        desc_label = ttk.Label(desc_frame, text=description, wraplength=420, justify=tk.LEFT)
        desc_label.pack()
        
        # Features
        features_frame = ttk.LabelFrame(parent, text="Key Features", padding="10")
        features_frame.pack(fill=tk.X, pady=(0, 15))
        
        features = [
            "• Side-by-side ReqIF file comparison",
            "• Excel-like requirement visualization",
            "• Comprehensive statistical analysis",
            "• Multiple export formats (CSV, Excel, PDF, JSON)",
            "• Advanced search and filtering",
            "• File validation and integrity checking",
            "• Backup and recovery capabilities"
        ]
        
        for feature in features:
            feature_label = ttk.Label(features_frame, text=feature)
            feature_label.pack(anchor=tk.W)
        
        # System info
        system_frame = ttk.LabelFrame(parent, text="System Information", padding="10")
        system_frame.pack(fill=tk.X, pady=(0, 15))
        
        import sys
        import platform
        
        system_info = [
            f"Python Version: {sys.version.split()[0]}",
            f"Platform: {platform.system()} {platform.release()}",
            f"Architecture: {platform.machine()}",
            f"Supported Formats: {', '.join([fmt['extension'] for fmt in SUPPORTED_FORMATS])}"
        ]
        
        for info in system_info:
            info_label = ttk.Label(system_frame, text=info)
            info_label.pack(anchor=tk.W)
        
        # Copyright
        copyright_frame = ttk.Frame(parent)
        copyright_frame.pack(fill=tk.X, pady=(15, 0))
        
        copyright_text = f"© 2024 ReqIF Tool Suite Team. All rights reserved."
        copyright_label = ttk.Label(copyright_frame, text=copyright_text, 
                                   font=('Segoe UI', 9), foreground='gray')
        copyright_label.pack()
    
    def create_buttons(self, parent):
        """Create dialog buttons"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Documentation button
        def open_docs():
            try:
                webbrowser.open("https://github.com/your-org/reqif-tool-suite/docs")
            except Exception as e:
                logger.error("Failed to open documentation: %s", str(e))
                messagebox.showerror("Error", "Failed to open documentation in browser.")
        
        ttk.Button(button_frame, text="Documentation", command=open_docs).pack(side=tk.LEFT)
        
        # License button
        def show_license():
            license_text = """MIT License

Copyright (c) 2024 ReqIF Tool Suite Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE."""
            
            # Show license in a new dialog
            license_dialog = tk.Toplevel(self.dialog)
            license_dialog.title("License")
            license_dialog.geometry("600x500")
            license_dialog.resizable(True, True)
            
            license_text_widget = scrolledtext.ScrolledText(license_dialog, wrap=tk.WORD)
            license_text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            license_text_widget.insert(tk.END, license_text)
            license_text_widget.config(state=tk.DISABLED)
            
            ttk.Button(license_dialog, text="Close", 
                      command=license_dialog.destroy).pack(pady=(0, 10))
        
        ttk.Button(button_frame, text="License", command=show_license).pack(side=tk.LEFT, padx=(10, 0))
        
        # Close button
        ttk.Button(button_frame, text="Close", command=self.dialog.destroy).pack(side=tk.RIGHT)
    
    def _center_dialog(self):
        """Center dialog on parent"""
        self.dialog.update_idletasks()
        
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        dialog_width = self.dialog.winfo_width()
        dialog_height = self.dialog.winfo_height()
        
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.dialog.geometry(f"+{x}+{y}")


class SettingsDialog:
    """
    Settings configuration dialog
    """
    
    def __init__(self, parent, config: ConfigManager):
        """Initialize settings dialog"""
        self.parent = parent
        self.config = config
        self.settings_changed = False
        
        # Load current settings
        self.current_settings = self.config.get_all_settings()
        
        self.create_dialog()
    
    def create_dialog(self):
        """Create the settings dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Settings")
        self.dialog.geometry("600x500")
        self.dialog.resizable(True, True)
        
        # Configure dialog
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Handle window close
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_cancel)
        
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook for different settings categories
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Create settings tabs
        self.create_general_tab()
        self.create_comparison_tab()
        self.create_interface_tab()
        self.create_advanced_tab()
        
        # Button frame
        self.create_buttons(main_frame)
        
        # Center dialog
        self._center_dialog()
    
    def create_general_tab(self):
        """Create general settings tab"""
        general_frame = ttk.Frame(self.notebook)
        self.notebook.add(general_frame, text="General")
        
        # Create scrollable frame
        canvas = tk.Canvas(general_frame)
        scrollbar = ttk.Scrollbar(general_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Default file locations
        locations_group = ttk.LabelFrame(scrollable_frame, text="Default Locations", padding="10")
        locations_group.pack(fill=tk.X, pady=(0, 15))
        
        # Default export directory
        export_frame = ttk.Frame(locations_group)
        export_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(export_frame, text="Default Export Directory:").pack(anchor=tk.W)
        
        export_path_frame = ttk.Frame(export_frame)
        export_path_frame.pack(fill=tk.X, pady=(2, 0))
        
        self.export_dir_var = tk.StringVar(value=self.current_settings.get('export_directory', ''))
        export_entry = ttk.Entry(export_path_frame, textvariable=self.export_dir_var)
        export_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        def browse_export_dir():
            directory = filedialog.askdirectory(title="Select Export Directory")
            if directory:
                self.export_dir_var.set(directory)
        
        ttk.Button(export_path_frame, text="Browse", command=browse_export_dir).pack(side=tk.RIGHT, padx=(5, 0))
        
        # File handling options
        file_handling_group = ttk.LabelFrame(scrollable_frame, text="File Handling", padding="10")
        file_handling_group.pack(fill=tk.X, pady=(0, 15))
        
        self.create_backup_var = tk.BooleanVar(value=self.current_settings.get('create_backups', True))
        ttk.Checkbutton(file_handling_group, text="Create backups before modifying files", 
                       variable=self.create_backup_var).pack(anchor=tk.W)
        
        self.validate_files_var = tk.BooleanVar(value=self.current_settings.get('validate_files', True))
        ttk.Checkbutton(file_handling_group, text="Validate files before processing", 
                       variable=self.validate_files_var).pack(anchor=tk.W)
        
        self.remember_recent_var = tk.BooleanVar(value=self.current_settings.get('remember_recent_files', True))
        ttk.Checkbutton(file_handling_group, text="Remember recent files", 
                       variable=self.remember_recent_var).pack(anchor=tk.W)
        
        # Recent files limit
        recent_limit_frame = ttk.Frame(file_handling_group)
        recent_limit_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(recent_limit_frame, text="Maximum recent files:").pack(side=tk.LEFT)
        
        self.recent_limit_var = tk.StringVar(value=str(self.current_settings.get('recent_files_limit', 10)))
        recent_spinbox = ttk.Spinbox(recent_limit_frame, from_=1, to=50, width=10, 
                                    textvariable=self.recent_limit_var)
        recent_spinbox.pack(side=tk.LEFT, padx=(5, 0))
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_comparison_tab(self):
        """Create comparison settings tab"""
        comparison_frame = ttk.Frame(self.notebook)
        self.notebook.add(comparison_frame, text="Comparison")
        
        # Default comparison options
        defaults_group = ttk.LabelFrame(comparison_frame, text="Default Comparison Options", padding="10")
        defaults_group.pack(fill=tk.X, pady=(0, 15))
        
        # Comparison mode
        mode_frame = ttk.Frame(defaults_group)
        mode_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(mode_frame, text="Default Comparison Mode:").pack(side=tk.LEFT)
        
        self.comparison_mode_var = tk.StringVar(value=self.current_settings.get('comparison_mode', 'detailed'))
        mode_combo = ttk.Combobox(mode_frame, textvariable=self.comparison_mode_var,
                                 values=['basic', 'detailed', 'fuzzy', 'structural'],
                                 state="readonly", width=15)
        mode_combo.pack(side=tk.LEFT, padx=(5, 0))
        
        # Matching strategy
        matching_frame = ttk.Frame(defaults_group)
        matching_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(matching_frame, text="Default Matching Strategy:").pack(side=tk.LEFT)
        
        self.matching_strategy_var = tk.StringVar(value=self.current_settings.get('matching_strategy', 'id_only'))
        matching_combo = ttk.Combobox(matching_frame, textvariable=self.matching_strategy_var,
                                     values=['id_only', 'id_and_text', 'fuzzy_matching', 'content_based'],
                                     state="readonly", width=15)
        matching_combo.pack(side=tk.LEFT, padx=(5, 0))
        
        # Comparison options
        options_group = ttk.LabelFrame(comparison_frame, text="Default Options", padding="10")
        options_group.pack(fill=tk.X, pady=(0, 15))
        
        self.ignore_whitespace_var = tk.BooleanVar(value=self.current_settings.get('ignore_whitespace', False))
        ttk.Checkbutton(options_group, text="Ignore whitespace differences", 
                       variable=self.ignore_whitespace_var).pack(anchor=tk.W)
        
        self.case_sensitive_var = tk.BooleanVar(value=self.current_settings.get('case_sensitive', True))
        ttk.Checkbutton(options_group, text="Case sensitive comparison", 
                       variable=self.case_sensitive_var).pack(anchor=tk.W)
        
        self.include_attributes_var = tk.BooleanVar(value=self.current_settings.get('include_attributes', True))
        ttk.Checkbutton(options_group, text="Include attributes in comparison", 
                       variable=self.include_attributes_var).pack(anchor=tk.W)
        
        # Performance settings
        performance_group = ttk.LabelFrame(comparison_frame, text="Performance", padding="10")
        performance_group.pack(fill=tk.X)
        
        # Similarity threshold
        similarity_frame = ttk.Frame(performance_group)
        similarity_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(similarity_frame, text="Similarity Threshold:").pack(side=tk.LEFT)
        
        self.similarity_threshold_var = tk.StringVar(value=str(self.current_settings.get('similarity_threshold', 0.8)))
        similarity_scale = ttk.Scale(similarity_frame, from_=0.1, to=1.0, orient=tk.HORIZONTAL,
                                    variable=self.similarity_threshold_var, length=200)
        similarity_scale.pack(side=tk.LEFT, padx=(5, 5))
        
        similarity_value_label = ttk.Label(similarity_frame, textvariable=self.similarity_threshold_var)
        similarity_value_label.pack(side=tk.LEFT)
        
        # Update label when scale changes
        def update_similarity_label(value):
            self.similarity_threshold_var.set(f"{float(value):.2f}")
        
        similarity_scale.config(command=update_similarity_label)
    
    def create_interface_tab(self):
        """Create interface settings tab"""
        interface_frame = ttk.Frame(self.notebook)
        self.notebook.add(interface_frame, text="Interface")
        
        # Theme settings
        theme_group = ttk.LabelFrame(interface_frame, text="Appearance", padding="10")
        theme_group.pack(fill=tk.X, pady=(0, 15))
        
        # Theme selection
        theme_frame = ttk.Frame(theme_group)
        theme_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(theme_frame, text="Theme:").pack(side=tk.LEFT)
        
        self.theme_var = tk.StringVar(value=self.current_settings.get('theme', 'default'))
        theme_combo = ttk.Combobox(theme_frame, textvariable=self.theme_var,
                                  values=['default', 'dark', 'light', 'blue'],
                                  state="readonly", width=15)
        theme_combo.pack(side=tk.LEFT, padx=(5, 0))
        
        # Font settings
        font_frame = ttk.Frame(theme_group)
        font_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(font_frame, text="Font Size:").pack(side=tk.LEFT)
        
        self.font_size_var = tk.StringVar(value=str(self.current_settings.get('font_size', 9)))
        font_spinbox = ttk.Spinbox(font_frame, from_=8, to=16, width=10, 
                                  textvariable=self.font_size_var)
        font_spinbox.pack(side=tk.LEFT, padx=(5, 0))
        
        # Window settings
        window_group = ttk.LabelFrame(interface_frame, text="Window Behavior", padding="10")
        window_group.pack(fill=tk.X, pady=(0, 15))
        
        self.remember_window_var = tk.BooleanVar(value=self.current_settings.get('remember_window_state', True))
        ttk.Checkbutton(window_group, text="Remember window size and position", 
                       variable=self.remember_window_var).pack(anchor=tk.W)
        
        self.confirm_exit_var = tk.BooleanVar(value=self.current_settings.get('confirm_exit', False))
        ttk.Checkbutton(window_group, text="Confirm before exiting application", 
                       variable=self.confirm_exit_var).pack(anchor=tk.W)
        
        # Display settings
        display_group = ttk.LabelFrame(interface_frame, text="Display Options", padding="10")
        display_group.pack(fill=tk.X)
        
        self.show_tooltips_var = tk.BooleanVar(value=self.current_settings.get('show_tooltips', True))
        ttk.Checkbutton(display_group, text="Show tooltips", 
                       variable=self.show_tooltips_var).pack(anchor=tk.W)
        
        self.show_status_bar_var = tk.BooleanVar(value=self.current_settings.get('show_status_bar', True))
        ttk.Checkbutton(display_group, text="Show status bar", 
                       variable=self.show_status_bar_var).pack(anchor=tk.W)
        
        self.animate_ui_var = tk.BooleanVar(value=self.current_settings.get('animate_ui', True))
        ttk.Checkbutton(display_group, text="Enable UI animations", 
                       variable=self.animate_ui_var).pack(anchor=tk.W)
    
    def create_advanced_tab(self):
        """Create advanced settings tab"""
        advanced_frame = ttk.Frame(self.notebook)
        self.notebook.add(advanced_frame, text="Advanced")
        
        # Logging settings
        logging_group = ttk.LabelFrame(advanced_frame, text="Logging", padding="10")
        logging_group.pack(fill=tk.X, pady=(0, 15))
        
        # Log level
        level_frame = ttk.Frame(logging_group)
        level_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(level_frame, text="Log Level:").pack(side=tk.LEFT)
        
        self.log_level_var = tk.StringVar(value=self.current_settings.get('log_level', 'INFO'))
        level_combo = ttk.Combobox(level_frame, textvariable=self.log_level_var,
                                  values=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                                  state="readonly", width=15)
        level_combo.pack(side=tk.LEFT, padx=(5, 0))
        
        self.enable_file_logging_var = tk.BooleanVar(value=self.current_settings.get('enable_file_logging', True))
        ttk.Checkbutton(logging_group, text="Enable file logging", 
                       variable=self.enable_file_logging_var).pack(anchor=tk.W)
        
        # Performance settings
        performance_group = ttk.LabelFrame(advanced_frame, text="Performance", padding="10")
        performance_group.pack(fill=tk.X, pady=(0, 15))
        
        # Memory settings
        memory_frame = ttk.Frame(performance_group)
        memory_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(memory_frame, text="Memory Cache Size (MB):").pack(side=tk.LEFT)
        
        self.cache_size_var = tk.StringVar(value=str(self.current_settings.get('cache_size_mb', 100)))
        cache_spinbox = ttk.Spinbox(memory_frame, from_=50, to=1000, width=10, 
                                   textvariable=self.cache_size_var)
        cache_spinbox.pack(side=tk.LEFT, padx=(5, 0))
        
        # Thread settings
        thread_frame = ttk.Frame(performance_group)
        thread_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(thread_frame, text="Max Worker Threads:").pack(side=tk.LEFT)
        
        self.max_threads_var = tk.StringVar(value=str(self.current_settings.get('max_threads', 4)))
        thread_spinbox = ttk.Spinbox(thread_frame, from_=1, to=16, width=10, 
                                    textvariable=self.max_threads_var)
        thread_spinbox.pack(side=tk.LEFT, padx=(5, 0))
        
        # Debug options
        debug_group = ttk.LabelFrame(advanced_frame, text="Debug Options", padding="10")
        debug_group.pack(fill=tk.X)
        
        self.debug_mode_var = tk.BooleanVar(value=self.current_settings.get('debug_mode', False))
        ttk.Checkbutton(debug_group, text="Enable debug mode", 
                       variable=self.debug_mode_var).pack(anchor=tk.W)
        
        self.verbose_logging_var = tk.BooleanVar(value=self.current_settings.get('verbose_logging', False))
        ttk.Checkbutton(debug_group, text="Verbose logging", 
                       variable=self.verbose_logging_var).pack(anchor=tk.W)
        
        # Reset button
        def reset_to_defaults():
            if messagebox.askyesno("Reset Settings", "Reset all settings to default values?"):
                self.config.reset_to_defaults()
                self.dialog.destroy()
                messagebox.showinfo("Reset Complete", "Settings have been reset to defaults. Please restart the application.")
        
        ttk.Button(debug_group, text="Reset to Defaults", command=reset_to_defaults).pack(anchor=tk.W, pady=(10, 0))
    
    def create_buttons(self, parent):
        """Create dialog buttons"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X)
        
        # Cancel button
        ttk.Button(button_frame, text="Cancel", command=self.on_cancel).pack(side=tk.RIGHT)
        
        # Apply button
        ttk.Button(button_frame, text="Apply", command=self.on_apply).pack(side=tk.RIGHT, padx=(0, 10))
        
        # OK button
        ttk.Button(button_frame, text="OK", command=self.on_ok).pack(side=tk.RIGHT, padx=(0, 10))
    
    def collect_settings(self) -> Dict[str, Any]:
        """Collect all settings from the dialog"""
        settings = {}
        
        # General settings
        settings['export_directory'] = self.export_dir_var.get()
        settings['create_backups'] = self.create_backup_var.get()
        settings['validate_files'] = self.validate_files_var.get()
        settings['remember_recent_files'] = self.remember_recent_var.get()
        settings['recent_files_limit'] = int(self.recent_limit_var.get())
        
        # Comparison settings
        settings['comparison_mode'] = self.comparison_mode_var.get()
        settings['matching_strategy'] = self.matching_strategy_var.get()
        settings['ignore_whitespace'] = self.ignore_whitespace_var.get()
        settings['case_sensitive'] = self.case_sensitive_var.get()
        settings['include_attributes'] = self.include_attributes_var.get()
        """
Dialogs Module
=============

This module provides custom dialog windows for the ReqIF Tool Suite.
Includes settings dialogs, error dialogs, about dialogs, and other
specialized modal windows.

Classes:
    SettingsDialog: Application settings configuration dialog
    AboutDialog: About the application dialog
    ErrorDialog: Error message dialog with details
    FileInfoDialog: File information display dialog
    ProgressDialog: Progress indication dialog (imported from common_widgets)
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, colorchooser, filedialog
from pathlib import Path
from typing import Optional, Dict, Any, Callable
import webbrowser
import logging

from utils.config import ConfigManager
from utils.logger import get_logger
from utils.constants import APP_CONFIG, SUPPORTED_FORMATS
from utils.helpers import format_file_size, format_timestamp
from models.file_info import FileInfo

logger = get_logger(__name__)


class ErrorDialog:
    """
    Error dialog with detailed error information and logging
    """
    
    @staticmethod
    def show_error(parent, title: str, message: str, details: str = None, 
                   log_error: bool = True):
        """
        Show error dialog
        
        Args:
            parent: Parent window
            title: Error dialog title
            message: Main error message
            details: Optional detailed error information
            log_error: Whether to log the error
        """
        if log_error:
            logger.error("%s: %s", title, message)
            if details:
                logger.error("Error details: %s", details)
        
        # Create error dialog
        dialog = tk.Toplevel(parent)
        dialog.title(title)
        dialog.geometry("500x400" if details else "400x200")
        dialog.resizable(True, True)
        
        # Center and configure dialog
        dialog.transient(parent)
        dialog.grab_set()
        
        # Icon (if available)
        try:
            dialog.iconbitmap(str(Path(__file__).parent.parent / "resources" / "icons" / "error.ico"))
        except:
            pass
        
        # Main frame
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Error icon and message
        header_frame = ttk.Frame(main_frame)
        header_frame.