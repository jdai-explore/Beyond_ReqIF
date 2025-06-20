#!/usr/bin/env python3
"""
ReqIF Tool Suite MVP - Main Application
A comprehensive ReqIF comparison and visualization tool with modern professional interface.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
from pathlib import Path

# Add the current directory to path for imports
sys.path.append(str(Path(__file__).parent))

try:
    from reqif_parser import ReqIFParser
    from reqif_comparator import ReqIFComparator
    from comparison_gui import ComparisonResultsGUI
    from visualizer_gui import VisualizerGUI
    from theme_manager import ThemeManager, add_tooltip
    print("All modules imported successfully")
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)


class ReqIFToolMVP:
    def __init__(self):
        print("Initializing ReqIF Tool MVP...")
        
        self.root = tk.Tk()
        self.root.title("ReqIF Tool Suite MVP - Professional Edition")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Initialize theme manager first
        self.theme_manager = ThemeManager(self.root)
        self.root.theme_manager = self.theme_manager  # Store reference for tooltips
        
        # Initialize components
        self.parser = ReqIFParser()
        self.comparator = ReqIFComparator()
        
        # File paths - Initialize ALL variables first
        self.file1_path = tk.StringVar()
        self.file2_path = tk.StringVar()
        self.viz_file_path = tk.StringVar()
        
        # Results window reference
        self.results_window = None
        self.viz_container = None
        
        # Progress tracking
        self.progress_var = tk.DoubleVar()
        
        print("Variables initialized, setting up GUI...")
        
        # Setup GUI
        try:
            self.setup_gui()
            self.setup_keyboard_shortcuts()
            
            # Apply theme after GUI setup
            self.theme_manager.apply_theme()
            
            print("GUI setup completed successfully")
        except Exception as e:
            print(f"Error in GUI setup: {e}")
            import traceback
            traceback.print_exc()
        
    def setup_gui(self):
        """Create the modern professional GUI interface"""
        print("Setting up main GUI...")
        
        # Main container with professional styling
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_container.columnconfigure(0, weight=1)
        self.main_container.rowconfigure(1, weight=1)
        
        # Create header with title and controls
        self.create_header()
        
        # Create main content area with notebook
        self.create_main_content()
        
        # Create status bar
        self.create_status_bar()
        
        # Menu bar
        print("Creating menu...")
        try:
            self.create_menu()
            print("Menu created successfully")
        except Exception as e:
            print(f"Error creating menu: {e}")
        
        print("GUI setup complete!")
        
    def create_header(self):
        """Create professional header with title and controls"""
        header_frame = ttk.Frame(self.main_container, padding="15")
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=10, pady=(10, 0))
        header_frame.columnconfigure(1, weight=1)
        
        # App title and logo area
        title_frame = ttk.Frame(header_frame)
        title_frame.grid(row=0, column=0, sticky=tk.W)
        
        title_label = ttk.Label(title_frame, text="⚙️ ReqIF Tool Suite", 
                               style='Title.TLabel')
        title_label.pack(side=tk.LEFT)
        
        subtitle_label = ttk.Label(title_frame, text="Professional Edition", 
                                  font=('Arial', 10, 'italic'))
        subtitle_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Control buttons
        controls_frame = ttk.Frame(header_frame)
        controls_frame.grid(row=0, column=2, sticky=tk.E)
        
        # Theme toggle button
        theme_btn = ttk.Button(controls_frame, text="🌓", width=3,
                              command=self.theme_manager.toggle_theme)
        theme_btn.pack(side=tk.RIGHT, padx=(5, 0))
        add_tooltip(theme_btn, "Toggle Dark/Light Theme (Ctrl+T)")
        
        # Help button
        help_btn = ttk.Button(controls_frame, text="❓", width=3,
                             command=self.show_about)
        help_btn.pack(side=tk.RIGHT, padx=(5, 0))
        add_tooltip(help_btn, "About ReqIF Tool Suite (F1)")
        
    def create_main_content(self):
        """Create main content area with enhanced notebook"""
        content_frame = ttk.Frame(self.main_container, padding="10")
        content_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(0, weight=1)
        
        # Create enhanced notebook for different modes
        print("Creating notebook widget...")
        self.notebook = ttk.Notebook(content_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create comparison tab
        print("Creating comparison tab...")
        try:
            self.create_comparison_tab()
            print("Comparison tab created successfully")
        except Exception as e:
            print(f"Error creating comparison tab: {e}")
            import traceback
            traceback.print_exc()
        
        # Create visualizer tab
        print("Creating visualizer tab...")
        try:
            self.create_visualizer_tab()
            print("Visualizer tab created successfully")
        except Exception as e:
            print(f"Error creating visualizer tab: {e}")
            import traceback
            traceback.print_exc()
        
    def create_status_bar(self):
        """Create professional status bar with progress indicator"""
        status_frame = ttk.Frame(self.main_container, relief='sunken', padding="5")
        status_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), padx=10, pady=(0, 10))
        status_frame.columnconfigure(1, weight=1)
        
        # Status label
        self.status_label = ttk.Label(status_frame, text="Ready")
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        # Progress bar (hidden by default)
        self.progress_bar = ttk.Progressbar(status_frame, variable=self.progress_var,
                                           length=200, mode='determinate')
        # Don't grid it initially - will be shown when needed
        
        # Current theme indicator
        self.theme_indicator = ttk.Label(status_frame, text="Light Theme")
        self.theme_indicator.grid(row=0, column=2, sticky=tk.E, padx=(10, 0))
        
    def create_comparison_tab(self):
        """Create the enhanced comparison interface tab"""
        compare_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(compare_frame, text="🔄 Compare Files")
        
        # Configure grid
        compare_frame.columnconfigure(1, weight=1)
        compare_frame.rowconfigure(5, weight=1)
        
        # Section header
        header_label = ttk.Label(compare_frame, text="Compare Two ReqIF Files", 
                                style='Header.TLabel')
        header_label.grid(row=0, column=0, columnspan=3, pady=(0, 20), sticky=tk.W)
        
        # File selection section with drag-drop indication
        file_section = ttk.LabelFrame(compare_frame, text="File Selection", padding="15")
        file_section.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        file_section.columnconfigure(1, weight=1)
        
        # File 1 selection
        ttk.Label(file_section, text="File 1 (Original):").grid(row=0, column=0, sticky=tk.W, pady=5)
        file1_entry = ttk.Entry(file_section, textvariable=self.file1_path, width=60)
        file1_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 5))
        browse1_btn = ttk.Button(file_section, text="📁 Browse", command=self.browse_file1)
        browse1_btn.grid(row=0, column=2, padx=(5, 0))
        add_tooltip(browse1_btn, "Browse for original ReqIF file (Ctrl+O)")
        
        # File 2 selection
        ttk.Label(file_section, text="File 2 (Modified):").grid(row=1, column=0, sticky=tk.W, pady=5)
        file2_entry = ttk.Entry(file_section, textvariable=self.file2_path, width=60)
        file2_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 5))
        browse2_btn = ttk.Button(file_section, text="📁 Browse", command=self.browse_file2)
        browse2_btn.grid(row=1, column=2, padx=(5, 0))
        add_tooltip(browse2_btn, "Browse for modified ReqIF file (Ctrl+Shift+O)")
        
        # Action buttons
        action_frame = ttk.Frame(compare_frame)
        action_frame.grid(row=2, column=0, columnspan=3, pady=20)
        
        compare_btn = ttk.Button(action_frame, text="🔍 Compare Files", 
                                command=self.compare_files, style='Accent.TButton')
        compare_btn.pack(side=tk.LEFT, padx=(0, 10))
        add_tooltip(compare_btn, "Start comparison analysis (F5)")
        
        clear_btn = ttk.Button(action_frame, text="🗑️ Clear", command=self.clear_files)
        clear_btn.pack(side=tk.LEFT)
        add_tooltip(clear_btn, "Clear file selections (Ctrl+R)")
        
        # Results area with better styling
        results_section = ttk.LabelFrame(compare_frame, text="Analysis Log", padding="10")
        results_section.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(15, 0))
        results_section.columnconfigure(0, weight=1)
        results_section.rowconfigure(0, weight=1)
        
        # Text widget with scrollbar
        text_frame = ttk.Frame(results_section)
        text_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        self.status_text = tk.Text(text_frame, height=12, width=80, wrap=tk.WORD,
                                  font=('Consolas', 9))
        self.status_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar for status area
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.status_text.configure(yscrollcommand=scrollbar.set)
        
        # Initial status message
        self.log_message("🚀 ReqIF Comparison Tool initialized and ready.")
        self.log_message("💡 Tip: You can drag and drop .reqif/.reqifz files directly onto the file entry fields.")
        
    def create_visualizer_tab(self):
        """Create the enhanced visualizer interface tab"""
        viz_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(viz_frame, text="📊 Visualize File")
        
        # Configure grid
        viz_frame.columnconfigure(1, weight=1)
        viz_frame.rowconfigure(4, weight=1)
        
        # Section header
        header_label = ttk.Label(viz_frame, text="Explore a Single ReqIF File", 
                                style='Header.TLabel')
        header_label.grid(row=0, column=0, columnspan=3, pady=(0, 20), sticky=tk.W)
        
        # File selection section
        file_section = ttk.LabelFrame(viz_frame, text="File Selection", padding="15")
        file_section.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        file_section.columnconfigure(1, weight=1)
        
        ttk.Label(file_section, text="ReqIF File:").grid(row=0, column=0, sticky=tk.W, pady=5)
        viz_entry = ttk.Entry(file_section, textvariable=self.viz_file_path, width=60)
        viz_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 5))
        browse_viz_btn = ttk.Button(file_section, text="📁 Browse", command=self.browse_viz_file)
        browse_viz_btn.grid(row=0, column=2, padx=(5, 0))
        add_tooltip(browse_viz_btn, "Browse for ReqIF file to visualize")
        
        # Action buttons
        action_frame = ttk.Frame(viz_frame)
        action_frame.grid(row=2, column=0, columnspan=3, pady=20)
        
        load_btn = ttk.Button(action_frame, text="📈 Load & Visualize", 
                             command=self.load_visualizer, style='Accent.TButton')
        load_btn.pack(side=tk.LEFT, padx=(0, 10))
        add_tooltip(load_btn, "Load file and start visualization (F6)")
        
        clear_viz_btn = ttk.Button(action_frame, text="🗑️ Clear", command=self.clear_viz_file)
        clear_viz_btn.pack(side=tk.LEFT)
        add_tooltip(clear_viz_btn, "Clear visualization")
        
        # Visualizer container with better styling
        viz_section = ttk.LabelFrame(viz_frame, text="Visualization", padding="10")
        viz_section.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(15, 0))
        viz_section.columnconfigure(0, weight=1)
        viz_section.rowconfigure(0, weight=1)
        
        self.viz_container = ttk.Frame(viz_section)
        self.viz_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Initial message with better styling
        initial_frame = ttk.Frame(self.viz_container)
        initial_frame.pack(expand=True, fill=tk.BOTH)
        
        initial_label = ttk.Label(initial_frame, 
                                 text="📁 Select a ReqIF file and click 'Load & Visualize' to explore requirements.",
                                 font=('Arial', 11, 'italic'),
                                 justify=tk.CENTER)
        initial_label.pack(expand=True)
        
        print("Visualizer tab setup complete")
        
    def setup_keyboard_shortcuts(self):
        """Setup professional keyboard shortcuts"""
        # File operations
        self.root.bind('<Control-o>', lambda e: self.browse_file1())
        self.root.bind('<Control-O>', lambda e: self.browse_file2())  # Shift+Ctrl+O
        self.root.bind('<Control-r>', lambda e: self.clear_files())
        
        # Actions
        self.root.bind('<F5>', lambda e: self.compare_files())
        self.root.bind('<F6>', lambda e: self.load_visualizer())
        
        # Interface
        self.root.bind('<Control-t>', lambda e: self.theme_manager.toggle_theme())
        self.root.bind('<F1>', lambda e: self.show_about())
        self.root.bind('<Escape>', lambda e: self.root.quit())
        
        # Tab switching
        self.root.bind('<Control-1>', lambda e: self.notebook.select(0))
        self.root.bind('<Control-2>', lambda e: self.notebook.select(1))
        
    def show_progress(self, message, progress=0):
        """Show progress bar and update status"""
        self.status_label.config(text=message)
        self.progress_var.set(progress)
        
        if progress > 0:
            self.progress_bar.grid(row=0, column=1, sticky=tk.E, padx=(10, 10))
        else:
            self.progress_bar.grid_remove()
            
        self.root.update_idletasks()
        
    def hide_progress(self):
        """Hide progress bar"""
        self.progress_bar.grid_remove()
        self.status_label.config(text="Ready")
        
    def update_theme_indicator(self):
        """Update theme indicator in status bar"""
        theme_name = self.theme_manager.themes[self.theme_manager.current_theme]["name"]
        self.theme_indicator.config(text=theme_name)
        
    def create_menu(self):
        """Create enhanced application menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open File 1...", command=self.browse_file1, accelerator="Ctrl+O")
        file_menu.add_command(label="Open File 2...", command=self.browse_file2, accelerator="Ctrl+Shift+O")
        file_menu.add_separator()
        file_menu.add_command(label="Clear Comparison Files", command=self.clear_files, accelerator="Ctrl+R")
        file_menu.add_command(label="Clear Visualizer File", command=self.clear_viz_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit, accelerator="Esc")
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Compare Files", command=self.compare_files, accelerator="F5")
        tools_menu.add_command(label="Load Visualizer", command=self.load_visualizer, accelerator="F6")
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        
        # Theme submenu
        theme_submenu = tk.Menu(view_menu, tearoff=0)
        view_menu.add_cascade(label="Themes", menu=theme_submenu)
        
        for theme_id, theme_name in self.theme_manager.get_available_themes():
            theme_submenu.add_command(label=theme_name, 
                                    command=lambda t=theme_id: self.set_theme(t))
        
        theme_submenu.add_separator()
        theme_submenu.add_command(label="Toggle Dark/Light", 
                                command=self.theme_manager.toggle_theme, 
                                accelerator="Ctrl+T")
        
        # Tabs submenu
        view_menu.add_separator()
        view_menu.add_command(label="Compare Tab", command=lambda: self.notebook.select(0), accelerator="Ctrl+1")
        view_menu.add_command(label="Visualize Tab", command=lambda: self.notebook.select(1), accelerator="Ctrl+2")
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Keyboard Shortcuts", command=self.show_shortcuts)
        help_menu.add_command(label="About", command=self.show_about, accelerator="F1")
        
    def set_theme(self, theme_name):
        """Set theme and update indicator"""
        self.theme_manager.set_theme(theme_name)
        self.update_theme_indicator()
        
    def browse_file1(self):
        """Browse for first ReqIF file with enhanced dialog"""
        filename = filedialog.askopenfilename(
            title="Select Original ReqIF File",
            filetypes=[
                ("ReqIF files", "*.reqif"), 
                ("ReqIF Archives", "*.reqifz"), 
                ("All files", "*.*")
            ]
        )
        if filename:
            self.file1_path.set(filename)
            self.log_message(f"📁 File 1 selected: {os.path.basename(filename)}")
            
    def browse_file2(self):
        """Browse for second ReqIF file with enhanced dialog"""
        filename = filedialog.askopenfilename(
            title="Select Modified ReqIF File",
            filetypes=[
                ("ReqIF files", "*.reqif"), 
                ("ReqIF Archives", "*.reqifz"), 
                ("All files", "*.*")
            ]
        )
        if filename:
            self.file2_path.set(filename)
            self.log_message(f"📁 File 2 selected: {os.path.basename(filename)}")
            
    def browse_viz_file(self):
        """Browse for ReqIF file to visualize"""
        filename = filedialog.askopenfilename(
            title="Select ReqIF File to Visualize",
            filetypes=[
                ("ReqIF files", "*.reqif"), 
                ("ReqIF Archives", "*.reqifz"), 
                ("All files", "*.*")
            ]
        )
        if filename:
            self.viz_file_path.set(filename)
            
    def clear_files(self):
        """Clear selected files with enhanced feedback"""
        self.file1_path.set("")
        self.file2_path.set("")
        self.log_message("🗑️ File selections cleared.")
        
    def clear_viz_file(self):
        """Clear visualizer file selection"""
        self.viz_file_path.set("")
        if self.viz_container:
            # Clear the visualizer container
            for widget in self.viz_container.winfo_children():
                widget.destroy()
            
            # Recreate initial message
            initial_frame = ttk.Frame(self.viz_container)
            initial_frame.pack(expand=True, fill=tk.BOTH)
            
            initial_label = ttk.Label(initial_frame, 
                                     text="📁 Select a ReqIF file and click 'Load & Visualize' to explore requirements.",
                                     font=('Arial', 11, 'italic'),
                                     justify=tk.CENTER)
            initial_label.pack(expand=True)
        
    def log_message(self, message):
        """Add message to status area with timestamp"""
        if hasattr(self, 'status_text'):
            import datetime
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            formatted_message = f"[{timestamp}] {message}\n"
            self.status_text.insert(tk.END, formatted_message)
            self.status_text.see(tk.END)
            self.root.update_idletasks()
        
    def load_visualizer(self):
        """Load file and show visualizer with progress tracking"""
        if not self.viz_file_path.get():
            messagebox.showerror("Error", "Please select a ReqIF file to visualize.")
            return
            
        if not os.path.exists(self.viz_file_path.get()):
            messagebox.showerror("Error", f"File does not exist: {self.viz_file_path.get()}")
            return
        
        try:
            # Show progress
            self.show_progress("Loading and parsing ReqIF file...", 10)
            
            # Parse the file
            requirements = self.parser.parse_file(self.viz_file_path.get())
            self.show_progress("Processing requirements...", 60)
            
            if not requirements:
                self.hide_progress()
                messagebox.showwarning("Warning", "No requirements found in the selected file.")
                return
            
            self.show_progress("Creating visualization...", 80)
            
            # Clear the container
            for widget in self.viz_container.winfo_children():
                widget.destroy()
            
            # Create visualizer GUI
            visualizer = VisualizerGUI(self.viz_container, requirements, 
                                     os.path.basename(self.viz_file_path.get()))
            
            self.show_progress("Visualization complete!", 100)
            self.root.after(1000, self.hide_progress)  # Hide after 1 second
            
        except Exception as e:
            self.hide_progress()
            messagebox.showerror("Error", f"Failed to load file:\n{str(e)}")
            
    def compare_files(self):
        """Perform file comparison with enhanced progress tracking"""
        # Validate file selection
        if not self.file1_path.get() or not self.file2_path.get():
            messagebox.showerror("Error", "Please select both files to compare.")
            return
            
        if not os.path.exists(self.file1_path.get()):
            messagebox.showerror("Error", f"File 1 does not exist: {self.file1_path.get()}")
            return
            
        if not os.path.exists(self.file2_path.get()):
            messagebox.showerror("Error", f"File 2 does not exist: {self.file2_path.get()}")
            return
        
        try:
            self.log_message("🚀 Starting comparison analysis...")
            self.show_progress("Initializing comparison...", 5)
            
            # Parse both files
            self.log_message("📖 Parsing File 1...")
            self.show_progress("Parsing original file...", 20)
            file1_reqs = self.parser.parse_file(self.file1_path.get())
            self.log_message(f"✅ File 1: Found {len(file1_reqs)} requirements")
            
            self.log_message("📖 Parsing File 2...")
            self.show_progress("Parsing modified file...", 40)
            file2_reqs = self.parser.parse_file(self.file2_path.get())
            self.log_message(f"✅ File 2: Found {len(file2_reqs)} requirements")
            
            # Perform comparison
            self.log_message("🔍 Analyzing differences...")
            self.show_progress("Comparing requirements...", 70)
            comparison_results = self.comparator.compare_requirements(file1_reqs, file2_reqs)
            
            # Log summary
            added_count = len(comparison_results['added'])
            deleted_count = len(comparison_results['deleted'])
            modified_count = len(comparison_results['modified'])
            unchanged_count = len(comparison_results['unchanged'])
            
            self.log_message("\n" + "="*50)
            self.log_message("📊 COMPARISON SUMMARY")
            self.log_message("="*50)
            self.log_message(f"➕ Added: {added_count}")
            self.log_message(f"➖ Deleted: {deleted_count}")
            self.log_message(f"📝 Modified: {modified_count}")
            self.log_message(f"⚪ Unchanged: {unchanged_count}")
            self.log_message("="*50)
            
            self.show_progress("Opening results window...", 90)
            
            # Show results window
            self.show_results(comparison_results)
            
            self.show_progress("Comparison complete!", 100)
            self.root.after(1500, self.hide_progress)  # Hide after 1.5 seconds
            
        except Exception as e:
            self.hide_progress()
            self.log_message(f"❌ Error during comparison: {str(e)}")
            messagebox.showerror("Comparison Error", f"An error occurred during comparison:\n{str(e)}")
            
    def show_results(self, comparison_results):
        """Show comparison results in new window"""
        if self.results_window:
            self.results_window.destroy()
            
        self.results_window = tk.Toplevel(self.root)
        self.results_window.title("Comparison Results - ReqIF Tool Suite")
        self.results_window.geometry("1200x800")
        self.results_window.minsize(1000, 600)
        
        # Apply theme to results window
        self.results_window.configure(bg=self.theme_manager.get_color('bg'))
        
        # Create results GUI
        results_gui = ComparisonResultsGUI(self.results_window, comparison_results)
        
    def show_shortcuts(self):
        """Show keyboard shortcuts help"""
        shortcuts_text = """Keyboard Shortcuts:

File Operations:
• Ctrl+O          Open File 1
• Ctrl+Shift+O    Open File 2  
• Ctrl+R          Clear Files

Actions:
• F5              Compare Files
• F6              Load Visualizer

Navigation:
• Ctrl+1          Compare Tab
• Ctrl+2          Visualize Tab

Interface:
• Ctrl+T          Toggle Theme
• F1              About Dialog
• Esc             Exit Application

Tips:
• Use drag & drop to quickly load files
• Double-click requirements for details
• Right-click for context menus"""
        
        messagebox.showinfo("Keyboard Shortcuts", shortcuts_text)
        
    def show_about(self):
        """Show enhanced about dialog"""
        about_text = """ReqIF Tool Suite MVP
Professional Edition v1.1.0

A comprehensive tool for working with ReqIF (Requirements Interchange Format) files.

🔥 Features:
• Parse ReqIF files (.reqif and .reqifz archives)
• Compare two files side-by-side with detailed analysis
• Visualize and explore single ReqIF files
• Advanced search and filtering capabilities
• Professional themes (Light/Dark/Blue)
• Statistical analysis and insights
• Export comparison results and requirements data
• Keyboard shortcuts for power users

🛠️ Built with Python and tkinter
🎨 Professional UI with modern theming
⚡ Optimized for performance and usability

© 2024 ReqIF Tool Suite Team"""
        
        messagebox.showinfo("About ReqIF Tool Suite MVP", about_text)
        
    def run(self):
        """Start the application"""
        print("Starting application main loop...")
        
        # Update theme indicator
        self.update_theme_indicator()
        
        # Center window on screen
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
        self.root.mainloop()


if __name__ == "__main__":
    print("Starting ReqIF Tool Suite MVP - Professional Edition...")
    try:
        # Create and run the application
        app = ReqIFToolMVP()
        app.run()
    except Exception as e:
        print(f"Application error: {e}")
        import traceback
        traceback.print_exc()