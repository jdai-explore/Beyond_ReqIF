#!/usr/bin/env python3
"""
Minimal ReqIF Tool Suite - No Theme System
Pure functionality focus with basic Tkinter styling.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
from typing import Optional, Dict, Any

# Import core modules
from reqif_parser import ReqIFParser
from reqif_comparator import ReqIFComparator
from comparison_gui import ComparisonResultsGUI
from visualizer_gui import VisualizerGUI
from error_handler import ErrorHandler


class ReqIFToolMinimal:
    """
    Minimal ReqIF Tool - Pure functionality, no theming
    """
    
    def __init__(self):
        # Initialize error handling
        self.error_handler = ErrorHandler()
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("Beyond ReqIF v1.2.0")
        self.root.geometry("1000x700")
        
        # Initialize components
        self.parser = ReqIFParser()
        self.comparator = ReqIFComparator()
        
        # File tracking
        self.file1_path = tk.StringVar()
        self.file2_path = tk.StringVar()
        self.visualize_file_path = tk.StringVar()
        
        # UI state
        self.comparison_window = None
        self.visualizer_window = None
        
        # Create UI
        self._create_main_ui()
        
        # Setup monitoring
        self._setup_monitoring()
    
    def _create_main_ui(self):
        """Create minimal UI"""
        # Create main container
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(2, weight=1)
        
        # Create sections
        self._create_header()
        self._create_main_content()
        self._create_status_bar()
    
    def _create_header(self):
        """Create simple header"""
        header_frame = ttk.Frame(self.main_frame)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Simple title
        title_label = ttk.Label(
            header_frame,
            text="ReqIF Tool Suite v1.2.0",
            font=("Helvetica", 18, "bold")
        )
        title_label.grid(row=0, column=0, sticky=(tk.W))
        
        subtitle_label = ttk.Label(
            header_frame,
            text="Requirements Analysis and Comparison"
        )
        subtitle_label.grid(row=1, column=0, sticky=(tk.W), pady=(5, 0))
    
    def _create_main_content(self):
        """Create main content with tabs"""
        # Create notebook
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(20, 0))
        
        # Create tabs
        self._create_compare_tab()
        self._create_visualize_tab()
    
    def _create_compare_tab(self):
        """Create comparison tab"""
        compare_frame = ttk.Frame(self.notebook, padding="25")
        self.notebook.add(compare_frame, text="Compare Files")
        
        # Configure grid
        compare_frame.columnconfigure(1, weight=1)
        
        # File 1 selection
        ttk.Label(compare_frame, text="File 1 (Original):", font=("Helvetica", 11, "bold")).grid(
            row=0, column=0, sticky=(tk.W), pady=(10, 10), padx=(0, 20))
        
        ttk.Entry(compare_frame, textvariable=self.file1_path, width=50).grid(
            row=0, column=1, sticky=(tk.W, tk.E), pady=(10, 10), padx=(0, 15))
        
        ttk.Button(compare_frame, text="Browse", command=self._browse_file1, width=12).grid(
            row=0, column=2, pady=(10, 10))
        
        # File 2 selection
        ttk.Label(compare_frame, text="File 2 (Modified):", font=("Helvetica", 11, "bold")).grid(
            row=1, column=0, sticky=(tk.W), pady=(10, 10), padx=(0, 20))
        
        ttk.Entry(compare_frame, textvariable=self.file2_path, width=50).grid(
            row=1, column=1, sticky=(tk.W, tk.E), pady=(10, 10), padx=(0, 15))
        
        ttk.Button(compare_frame, text="Browse", command=self._browse_file2, width=12).grid(
            row=1, column=2, pady=(10, 10))
        
        # Controls
        controls_frame = ttk.Frame(compare_frame)
        controls_frame.grid(row=2, column=0, columnspan=3, pady=(30, 0))
        
        self.compare_btn = ttk.Button(
            controls_frame,
            text="Compare Files",
            command=self._compare_files
        )
        self.compare_btn.grid(row=0, column=0, padx=(0, 20))
        
        self.compare_status_label = ttk.Label(
            controls_frame,
            text="Select two ReqIF files to begin comparison"
        )
        self.compare_status_label.grid(row=0, column=1, sticky=(tk.W))
    
    def _create_visualize_tab(self):
        """Create visualization tab"""
        visualize_frame = ttk.Frame(self.notebook, padding="25")
        self.notebook.add(visualize_frame, text="Visualize File")
        
        # Configure grid
        visualize_frame.columnconfigure(1, weight=1)
        
        # File selection
        ttk.Label(visualize_frame, text="ReqIF File:", font=("Helvetica", 11, "bold")).grid(
            row=0, column=0, sticky=(tk.W), pady=(10, 10), padx=(0, 20))
        
        ttk.Entry(visualize_frame, textvariable=self.visualize_file_path, width=50).grid(
            row=0, column=1, sticky=(tk.W, tk.E), pady=(10, 10), padx=(0, 15))
        
        ttk.Button(visualize_frame, text="Browse", command=self._browse_visualize_file, width=12).grid(
            row=0, column=2, pady=(10, 10))
        
        # Controls
        controls_frame = ttk.Frame(visualize_frame)
        controls_frame.grid(row=1, column=0, columnspan=3, pady=(30, 0))
        
        self.visualize_btn = ttk.Button(
            controls_frame,
            text="Load & Analyze",
            command=self._visualize_file
        )
        self.visualize_btn.grid(row=0, column=0, padx=(0, 20))
        
        self.visualize_status_label = ttk.Label(
            controls_frame,
            text="Select a ReqIF file to explore and analyze"
        )
        self.visualize_status_label.grid(row=0, column=1, sticky=(tk.W))
    
    def _create_status_bar(self):
        """Create simple status bar"""
        status_frame = ttk.Frame(self.main_frame)
        status_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(20, 0))
        
        self.status_label = ttk.Label(status_frame, text="Ready")
        self.status_label.grid(row=0, column=0, sticky=(tk.W))
    
    def _setup_monitoring(self):
        """Setup file path monitoring"""
        def update_button_states(*args):
            self._update_button_states()
        
        self.file1_path.trace_add("write", update_button_states)
        self.file2_path.trace_add("write", update_button_states)
        self.visualize_file_path.trace_add("write", update_button_states)
        
        self._update_button_states()
    
    def _update_button_states(self):
        """Update button states"""
        # Compare button
        has_both_files = bool(self.file1_path.get() and self.file2_path.get())
        self.compare_btn.configure(state=tk.NORMAL if has_both_files else tk.DISABLED)
        
        if has_both_files:
            self.compare_status_label.configure(text="Ready to compare files")
        else:
            self.compare_status_label.configure(text="Select two ReqIF files to begin comparison")
        
        # Visualize button
        has_visualize_file = bool(self.visualize_file_path.get())
        self.visualize_btn.configure(state=tk.NORMAL if has_visualize_file else tk.DISABLED)
        
        if has_visualize_file:
            self.visualize_status_label.configure(text="Ready to load and analyze")
        else:
            self.visualize_status_label.configure(text="Select a ReqIF file to explore and analyze")
    
    # =============================================================================
    # FILE OPERATIONS
    # =============================================================================
    
    def _browse_file1(self):
        """Browse for first file"""
        try:
            filename = filedialog.askopenfilename(
                title="Select First ReqIF File (Original)",
                filetypes=[("ReqIF files", "*.reqif"), ("ReqIF archives", "*.reqifz"), ("All files", "*.*")]
            )
            if filename:
                self.file1_path.set(filename)
                self.status_label.configure(text=f"File 1 selected: {os.path.basename(filename)}")
        except Exception as e:
            self.error_handler.safe_execute(
                lambda: messagebox.showerror("Error", f"Failed to select file 1:\n{str(e)}"),
                error_message="Failed to select file 1"
            )
    
    def _browse_file2(self):
        """Browse for second file"""
        try:
            filename = filedialog.askopenfilename(
                title="Select Second ReqIF File (Modified)",
                filetypes=[("ReqIF files", "*.reqif"), ("ReqIF archives", "*.reqifz"), ("All files", "*.*")]
            )
            if filename:
                self.file2_path.set(filename)
                self.status_label.configure(text=f"File 2 selected: {os.path.basename(filename)}")
        except Exception as e:
            self.error_handler.safe_execute(
                lambda: messagebox.showerror("Error", f"Failed to select file 2:\n{str(e)}"),
                error_message="Failed to select file 2"
            )
    
    def _browse_visualize_file(self):
        """Browse for visualization file"""
        try:
            filename = filedialog.askopenfilename(
                title="Select ReqIF File to Analyze",
                filetypes=[("ReqIF files", "*.reqif"), ("ReqIF archives", "*.reqifz"), ("All files", "*.*")]
            )
            if filename:
                self.visualize_file_path.set(filename)
                self.status_label.configure(text=f"File selected for analysis: {os.path.basename(filename)}")
        except Exception as e:
            self.error_handler.safe_execute(
                lambda: messagebox.showerror("Error", f"Failed to select analysis file:\n{str(e)}"),
                error_message="Failed to select analysis file"
            )
    
    def _compare_files(self):
        """Compare files"""
        if not (self.file1_path.get() and self.file2_path.get()):
            messagebox.showwarning("Missing Files", "Please select both files to compare.")
            return
        
        # Show progress
        self.status_label.configure(text="Comparing files...")
        self.compare_btn.configure(state=tk.DISABLED, text="Comparing...")
        self.root.update()
        
        def compare_in_thread():
            try:
                # Parse files
                self.root.after_idle(lambda: self.status_label.configure(text="Parsing first file..."))
                file1_reqs = self.parser.parse_file(self.file1_path.get())
                
                self.root.after_idle(lambda: self.status_label.configure(text="Parsing second file..."))
                file2_reqs = self.parser.parse_file(self.file2_path.get())
                
                # Compare
                self.root.after_idle(lambda: self.status_label.configure(text="Analyzing differences..."))
                results = self.comparator.compare_requirements(file1_reqs, file2_reqs)
                
                # Show results
                def show_results():
                    self.comparison_window = ComparisonResultsGUI(self.root, results)
                    self.status_label.configure(text="Comparison complete - Results window opened")
                    self.compare_btn.configure(state=tk.NORMAL, text="Compare Files")
                
                self.root.after_idle(show_results)
                
            except Exception as e:
                error_message = str(e)  # Capture the error message
                def show_error():
                    error_msg = f"File comparison failed:\n{error_message}"
                    messagebox.showerror("Comparison Error", error_msg)
                    self.status_label.configure(text="Comparison failed - Check error details")
                    self.compare_btn.configure(state=tk.NORMAL, text="Compare Files")
                
                self.root.after_idle(show_error)
        
        threading.Thread(target=compare_in_thread, daemon=True).start()
    
    def _visualize_file(self):
        """Visualize file"""
        if not self.visualize_file_path.get():
            messagebox.showwarning("Missing File", "Please select a file to analyze.")
            return
        
        # Show progress
        self.status_label.configure(text="Loading file for analysis...")
        self.visualize_btn.configure(state=tk.DISABLED, text="Loading...")
        self.root.update()
        
        def visualize_in_thread():
            try:
                # Parse file
                self.root.after_idle(lambda: self.status_label.configure(text="Parsing ReqIF file..."))
                requirements = self.parser.parse_file(self.visualize_file_path.get())
                
                # Show visualizer
                def show_visualizer():
                    self.visualizer_window = VisualizerGUI(
                        self.root, 
                        requirements, 
                        self.visualize_file_path.get()
                    )
                    self.status_label.configure(text="File loaded - Analysis window opened")
                    self.visualize_btn.configure(state=tk.NORMAL, text="Load & Analyze")
                
                self.root.after_idle(show_visualizer)
                
            except Exception as e:
                error_message = str(e)  # Capture the error message
                def show_error():
                    error_msg = f"File analysis failed:\n{error_message}"
                    messagebox.showerror("Analysis Error", error_msg)
                    self.status_label.configure(text="Analysis failed - Check error details")
                    self.visualize_btn.configure(state=tk.NORMAL, text="Load & Analyze")
                
                self.root.after_idle(show_error)
        
        threading.Thread(target=visualize_in_thread, daemon=True).start()
    
    def run(self):
        """Run the application"""
        try:
            self.status_label.configure(text="Ready - ReqIF Tool Suite")
            self.root.mainloop()
        except Exception as e:
            error_msg = f"Application runtime error:\n{str(e)}"
            messagebox.showerror("Runtime Error", error_msg)
        finally:
            self._cleanup()
    
    def _cleanup(self):
        """Cleanup on exit"""
        try:
            if self.comparison_window:
                try:
                    self.comparison_window.window.destroy()
                except:
                    pass
            if self.visualizer_window:
                try:
                    self.visualizer_window.window.destroy()
                except:
                    pass
        except:
            pass


def main():
    """Main function"""
    try:
        print("Starting Minimal ReqIF Tool Suite v1.2.0...")
        app = ReqIFToolMinimal()
        app.run()
    except Exception as e:
        print(f"Critical startup error: {e}")
        try:
            import traceback
            traceback.print_exc()
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Startup Error", f"Failed to start ReqIF Tool Suite:\n\n{str(e)}")
        except Exception:
            print("Failed to show error dialog - check console output")


if __name__ == "__main__":
    main()