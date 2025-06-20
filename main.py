#!/usr/bin/env python3
"""
ReqIF Tool Suite MVP - Main Application
A simple ReqIF comparison tool with GUI interface.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
from pathlib import Path

# Add the current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from reqif_parser import ReqIFParser
from reqif_comparator import ReqIFComparator
from comparison_gui import ComparisonResultsGUI


class ReqIFToolMVP:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ReqIF Tool Suite MVP - Comparison Tool")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # Initialize components
        self.parser = ReqIFParser()
        self.comparator = ReqIFComparator()
        
        # File paths
        self.file1_path = tk.StringVar()
        self.file2_path = tk.StringVar()
        
        # Setup GUI
        self.setup_gui()
        
        # Results window reference
        self.results_window = None
        
    def setup_gui(self):
        """Create the main GUI interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="ReqIF Comparison Tool", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # File 1 selection
        ttk.Label(main_frame, text="File 1 (Original):").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.file1_path, width=50).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 5))
        ttk.Button(main_frame, text="Browse", command=self.browse_file1).grid(row=1, column=2, padx=(5, 0))
        
        # File 2 selection
        ttk.Label(main_frame, text="File 2 (Modified):").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.file2_path, width=50).grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(10, 5))
        ttk.Button(main_frame, text="Browse", command=self.browse_file2).grid(row=2, column=2, padx=(5, 0))
        
        # Compare button
        compare_btn = ttk.Button(main_frame, text="Compare Files", 
                                command=self.compare_files, style='Accent.TButton')
        compare_btn.grid(row=3, column=0, columnspan=3, pady=20)
        
        # Status area
        self.status_text = tk.Text(main_frame, height=15, width=70, wrap=tk.WORD)
        self.status_text.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        main_frame.rowconfigure(4, weight=1)
        
        # Scrollbar for status area
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        scrollbar.grid(row=4, column=3, sticky=(tk.N, tk.S), pady=(10, 0))
        self.status_text.configure(yscrollcommand=scrollbar.set)
        
        # Initial status message
        self.log_message("ReqIF Comparison Tool initialized. Select two ReqIF files to compare.")
        
        # Menu bar
        self.create_menu()
        
    def create_menu(self):
        """Create application menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Clear Files", command=self.clear_files)
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
            filetypes=[("ReqIF files", "*.reqif*"), ("All files", "*.*")]
        )
        if filename:
            self.file1_path.set(filename)
            self.log_message(f"File 1 selected: {os.path.basename(filename)}")
            
    def browse_file2(self):
        """Browse for second ReqIF file"""
        filename = filedialog.askopenfilename(
            title="Select Second ReqIF File",
            filetypes=[("ReqIF files", "*.reqif*"), ("All files", "*.*")]
        )
        if filename:
            self.file2_path.set(filename)
            self.log_message(f"File 2 selected: {os.path.basename(filename)}")
            
    def clear_files(self):
        """Clear selected files"""
        self.file1_path.set("")
        self.file2_path.set("")
        self.log_message("File selections cleared.")
        
    def log_message(self, message):
        """Add message to status area"""
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.see(tk.END)
        self.root.update_idletasks()
        
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
Version 1.0.0

A simple tool for comparing ReqIF (Requirements Interchange Format) files.

Features:
• Parse ReqIF files
• Compare two files side-by-side
• Identify added, deleted, and modified requirements
• Export comparison results

Built with Python and tkinter."""
        
        messagebox.showinfo("About ReqIF Tool Suite MVP", about_text)
        
    def run(self):
        """Start the application"""
        self.root.mainloop()


if __name__ == "__main__":
    # Create and run the application
    app = ReqIFToolMVP()
    app.run()