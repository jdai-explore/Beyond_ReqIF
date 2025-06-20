#!/usr/bin/env python3
"""
ReqIF Tool Suite MVP - Main Application
A comprehensive ReqIF comparison and visualization tool with GUI interface.
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
    print("All modules imported successfully")
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)


class ReqIFToolMVP:
    def __init__(self):
        print("Initializing ReqIF Tool MVP...")
        
        self.root = tk.Tk()
        self.root.title("ReqIF Tool Suite MVP - Compare & Visualize")
        self.root.geometry("900x700")
        self.root.minsize(700, 500)
        
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
        
        print("Variables initialized, setting up GUI...")
        
        # Setup GUI
        try:
            self.setup_gui()
            print("GUI setup completed successfully")
        except Exception as e:
            print(f"Error in GUI setup: {e}")
            import traceback
            traceback.print_exc()
        
    def setup_gui(self):
        """Create the main GUI interface"""
        print("Setting up main GUI...")
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="ReqIF Tool Suite MVP", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, pady=(0, 20))
        
        # Create notebook for different modes
        print("Creating notebook widget...")
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
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
        
        # Menu bar
        print("Creating menu...")
        try:
            self.create_menu()
            print("Menu created successfully")
        except Exception as e:
            print(f"Error creating menu: {e}")
        
        print("GUI setup complete!")
        
    def create_comparison_tab(self):
        """Create the comparison interface tab"""
        compare_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(compare_frame, text="Compare Files")
        
        # Configure grid
        compare_frame.columnconfigure(1, weight=1)
        compare_frame.rowconfigure(4, weight=1)
        
        # Subtitle
        subtitle_label = ttk.Label(compare_frame, text="Compare Two ReqIF Files", 
                                  font=('Arial', 12, 'bold'))
        subtitle_label.grid(row=0, column=0, columnspan=3, pady=(0, 15))
        
        # File 1 selection
        ttk.Label(compare_frame, text="File 1 (Original):").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(compare_frame, textvariable=self.file1_path, width=50).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 5))
        ttk.Button(compare_frame, text="Browse", command=self.browse_file1).grid(row=1, column=2, padx=(5, 0))
        
        # File 2 selection
        ttk.Label(compare_frame, text="File 2 (Modified):").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(compare_frame, textvariable=self.file2_path, width=50).grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(10, 5))
        ttk.Button(compare_frame, text="Browse", command=self.browse_file2).grid(row=2, column=2, padx=(5, 0))
        
        # Compare button
        compare_btn = ttk.Button(compare_frame, text="Compare Files", command=self.compare_files)
        compare_btn.grid(row=3, column=0, columnspan=3, pady=20)
        
        # Status area
        self.status_text = tk.Text(compare_frame, height=15, width=70, wrap=tk.WORD)
        self.status_text.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        # Scrollbar for status area
        scrollbar = ttk.Scrollbar(compare_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        scrollbar.grid(row=4, column=3, sticky=(tk.N, tk.S), pady=(10, 0))
        self.status_text.configure(yscrollcommand=scrollbar.set)
        
        # Initial status message
        self.log_message("ReqIF Comparison Tool initialized. Select two ReqIF files to compare.")
        
    def create_visualizer_tab(self):
        """Create the visualizer interface tab"""
        print("Creating visualizer tab frame...")
        
        viz_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(viz_frame, text="Visualize File")
        
        print("Visualizer tab added to notebook")
        
        # Configure grid
        viz_frame.columnconfigure(1, weight=1)
        viz_frame.rowconfigure(3, weight=1)
        
        # Subtitle
        subtitle_label = ttk.Label(viz_frame, text="Explore a Single ReqIF File", 
                                  font=('Arial', 12, 'bold'))
        subtitle_label.grid(row=0, column=0, columnspan=3, pady=(0, 15))
        
        # File selection for visualizer
        ttk.Label(viz_frame, text="ReqIF File:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(viz_frame, textvariable=self.viz_file_path, width=50).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 5))
        ttk.Button(viz_frame, text="Browse", command=self.browse_viz_file).grid(row=1, column=2, padx=(5, 0))
        
        # Load button
        load_btn = ttk.Button(viz_frame, text="Load & Visualize", command=self.load_visualizer)
        load_btn.grid(row=2, column=0, columnspan=3, pady=20)
        
        # Visualizer container
        self.viz_container = ttk.Frame(viz_frame)
        self.viz_container.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        # Initial message
        initial_label = ttk.Label(self.viz_container, 
                                 text="Select a ReqIF file and click 'Load & Visualize' to explore requirements.",
                                 font=('Arial', 10, 'italic'))
        initial_label.pack(expand=True)
        
        print("Visualizer tab setup complete")
        
    def create_menu(self):
        """Create application menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Clear Comparison Files", command=self.clear_files)
        file_menu.add_command(label="Clear Visualizer File", command=self.clear_viz_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
    def browse_file1(self):
        """Browse for first ReqIF file"""
        filename = filedialog.askopenfilename(
            title="Select First ReqIF File",
            filetypes=[
                ("ReqIF files", "*.reqif"), 
                ("ReqIF Archives", "*.reqifz"), 
                ("All files", "*.*")
            ]
        )
        if filename:
            self.file1_path.set(filename)
            self.log_message(f"File 1 selected: {os.path.basename(filename)}")
            
    def browse_file2(self):
        """Browse for second ReqIF file"""
        filename = filedialog.askopenfilename(
            title="Select Second ReqIF File",
            filetypes=[
                ("ReqIF files", "*.reqif"), 
                ("ReqIF Archives", "*.reqifz"), 
                ("All files", "*.*")
            ]
        )
        if filename:
            self.file2_path.set(filename)
            self.log_message(f"File 2 selected: {os.path.basename(filename)}")
            
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
        """Clear selected files"""
        self.file1_path.set("")
        self.file2_path.set("")
        self.log_message("File selections cleared.")
        
    def clear_viz_file(self):
        """Clear visualizer file selection"""
        self.viz_file_path.set("")
        if self.viz_container:
            # Clear the visualizer container
            for widget in self.viz_container.winfo_children():
                widget.destroy()
            initial_label = ttk.Label(self.viz_container, 
                                     text="Select a ReqIF file and click 'Load & Visualize' to explore requirements.",
                                     font=('Arial', 10, 'italic'))
            initial_label.pack(expand=True)
        
    def log_message(self, message):
        """Add message to status area"""
        if hasattr(self, 'status_text'):
            self.status_text.insert(tk.END, f"{message}\n")
            self.status_text.see(tk.END)
            self.root.update_idletasks()
        
    def load_visualizer(self):
        """Load file and show visualizer"""
        if not self.viz_file_path.get():
            messagebox.showerror("Error", "Please select a ReqIF file to visualize.")
            return
            
        if not os.path.exists(self.viz_file_path.get()):
            messagebox.showerror("Error", f"File does not exist: {self.viz_file_path.get()}")
            return
        
        try:
            # Parse the file
            requirements = self.parser.parse_file(self.viz_file_path.get())
            
            if not requirements:
                messagebox.showwarning("Warning", "No requirements found in the selected file.")
                return
            
            # Clear the container
            for widget in self.viz_container.winfo_children():
                widget.destroy()
            
            # Create visualizer GUI
            visualizer = VisualizerGUI(self.viz_container, requirements, 
                                     os.path.basename(self.viz_file_path.get()))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file:\n{str(e)}")
            
    def compare_files(self):
        """Perform file comparison"""
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
            self.log_message("Starting comparison...")
            
            # Parse both files
            self.log_message("Parsing File 1...")
            file1_reqs = self.parser.parse_file(self.file1_path.get())
            self.log_message(f"File 1: Found {len(file1_reqs)} requirements")
            
            self.log_message("Parsing File 2...")
            file2_reqs = self.parser.parse_file(self.file2_path.get())
            self.log_message(f"File 2: Found {len(file2_reqs)} requirements")
            
            # Perform comparison
            self.log_message("Comparing requirements...")
            comparison_results = self.comparator.compare_requirements(file1_reqs, file2_reqs)
            
            # Log summary
            added_count = len(comparison_results['added'])
            deleted_count = len(comparison_results['deleted'])
            modified_count = len(comparison_results['modified'])
            unchanged_count = len(comparison_results['unchanged'])
            
            self.log_message("\n=== COMPARISON SUMMARY ===")
            self.log_message(f"Added: {added_count}")
            self.log_message(f"Deleted: {deleted_count}")
            self.log_message(f"Modified: {modified_count}")
            self.log_message(f"Unchanged: {unchanged_count}")
            self.log_message("=" * 25)
            
            # Show results window
            self.show_results(comparison_results)
            
        except Exception as e:
            self.log_message(f"Error during comparison: {str(e)}")
            messagebox.showerror("Comparison Error", f"An error occurred during comparison:\n{str(e)}")
            
    def show_results(self, comparison_results):
        """Show comparison results in new window"""
        if self.results_window:
            self.results_window.destroy()
            
        self.results_window = tk.Toplevel(self.root)
        self.results_window.title("Comparison Results")
        self.results_window.geometry("1000x700")
        
        # Create results GUI
        results_gui = ComparisonResultsGUI(self.results_window, comparison_results)
        
    def show_about(self):
        """Show about dialog"""
        about_text = """ReqIF Tool Suite MVP
Version 1.1.0

A comprehensive tool for working with ReqIF (Requirements Interchange Format) files.

Features:
• Parse ReqIF files (.reqif and .reqifz archives)
• Compare two files side-by-side
• Identify added, deleted, and modified requirements
• Visualize and explore single ReqIF files
• Advanced search and filtering
• Statistical analysis and insights
• Export comparison results and requirements data

Built with Python and tkinter."""
        
        messagebox.showinfo("About ReqIF Tool Suite MVP", about_text)
        
    def run(self):
        """Start the application"""
        print("Starting application main loop...")
        self.root.mainloop()


if __name__ == "__main__":
    print("Starting ReqIF Tool Suite MVP...")
    try:
        # Create and run the application
        app = ReqIFToolMVP()
        app.run()
    except Exception as e:
        print(f"Application error: {e}")
        import traceback
        traceback.print_exc()