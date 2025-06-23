#!/usr/bin/env python3
"""
ReqIF Tool Suite - Simplified Version
Removed all Apple design theme dependencies
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


class ReqIFToolMVP:
    """
    ReqIF Tool Suite - Simplified Version
    """
    
    def __init__(self):
        # Initialize error handling
        self.error_handler = ErrorHandler()
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("Beyond ReqIF v1.2.0 - Professional Edition")
        self.root.geometry("1100x750")
        self.root.configure(bg='#FFFFFF')
        
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
        """Create simplified UI"""
        # Create main container
        self.main_frame = tk.Frame(self.root, bg='#FFFFFF', padx=20, pady=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create sections
        self._create_header()
        self._create_main_content()
        self._create_status_bar()
    
    def _create_header(self):
        """Create simple header"""
        header_frame = tk.Frame(self.main_frame, bg='#F0F0F0', relief='ridge', bd=1)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Title
        title_label = tk.Label(header_frame, text="Beyond ReqIF", 
                              font=('Arial', 16, 'bold'), bg='#F0F0F0', fg='#000000')
        title_label.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Version
        version_label = tk.Label(header_frame, text="Professional Edition v1.2.0", 
                                font=('Arial', 10), bg='#F0F0F0', fg='#666666')
        version_label.pack(side=tk.RIGHT, padx=10, pady=10)
    
    def _create_main_content(self):
        """Create main content with notebook"""
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self._create_compare_tab()
        self._create_visualize_tab()
    
    def _create_compare_tab(self):
        """Create comparison tab"""
        compare_frame = tk.Frame(self.notebook, bg='#FFFFFF')
        self.notebook.add(compare_frame, text="Compare Files")
        
        # Main content frame
        content_frame = tk.Frame(compare_frame, bg='#FFFFFF', padx=20, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Section header
        header_label = tk.Label(content_frame, text="File Comparison", 
                               font=('Arial', 14, 'bold'), bg='#FFFFFF', fg='#000000')
        header_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Description
        desc_label = tk.Label(content_frame, 
                             text="Compare two ReqIF files to identify added, deleted, and modified requirements", 
                             font=('Arial', 10), bg='#FFFFFF', fg='#666666', wraplength=600)
        desc_label.pack(anchor=tk.W, pady=(0, 20))
        
        # File selection frame
        files_frame = tk.LabelFrame(content_frame, text="Select Files", 
                                   font=('Arial', 10, 'bold'), bg='#FFFFFF', fg='#000000')
        files_frame.pack(fill=tk.X, pady=(0, 20))
        
        # File 1
        file1_frame = tk.Frame(files_frame, bg='#FFFFFF')
        file1_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(file1_frame, text="Original File:", font=('Arial', 10), 
                bg='#FFFFFF', fg='#000000').pack(side=tk.LEFT)
        
        file1_entry = tk.Entry(file1_frame, textvariable=self.file1_path, 
                              font=('Arial', 10), width=50)
        file1_entry.pack(side=tk.LEFT, padx=(10, 10), fill=tk.X, expand=True)
        
        file1_btn = tk.Button(file1_frame, text="Browse", command=self._browse_file1,
                             bg='#F0F0F0', fg='#000000', font=('Arial', 10))
        file1_btn.pack(side=tk.RIGHT)
        
        # File 2
        file2_frame = tk.Frame(files_frame, bg='#FFFFFF')
        file2_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(file2_frame, text="Modified File:", font=('Arial', 10), 
                bg='#FFFFFF', fg='#000000').pack(side=tk.LEFT)
        
        file2_entry = tk.Entry(file2_frame, textvariable=self.file2_path, 
                              font=('Arial', 10), width=50)
        file2_entry.pack(side=tk.LEFT, padx=(10, 10), fill=tk.X, expand=True)
        
        file2_btn = tk.Button(file2_frame, text="Browse", command=self._browse_file2,
                             bg='#F0F0F0', fg='#000000', font=('Arial', 10))
        file2_btn.pack(side=tk.RIGHT)
        
        # Controls
        controls_frame = tk.Frame(content_frame, bg='#FFFFFF')
        controls_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.compare_btn = tk.Button(controls_frame, text="Compare Files", 
                                    command=self._compare_files,
                                    bg='#0078D4', fg='white', font=('Arial', 10, 'bold'),
                                    padx=20, pady=5)
        self.compare_btn.pack(side=tk.LEFT)
        
        self.compare_status_label = tk.Label(controls_frame, 
                                           text="Select two ReqIF files to begin comparison",
                                           font=('Arial', 10), bg='#FFFFFF', fg='#666666')
        self.compare_status_label.pack(side=tk.LEFT, padx=(20, 0))
    
    def _create_visualize_tab(self):
        """Create visualization tab"""
        visualize_frame = tk.Frame(self.notebook, bg='#FFFFFF')
        self.notebook.add(visualize_frame, text="Analyze File")
        
        # Main content frame
        content_frame = tk.Frame(visualize_frame, bg='#FFFFFF', padx=20, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Section header
        header_label = tk.Label(content_frame, text="File Analysis", 
                               font=('Arial', 14, 'bold'), bg='#FFFFFF', fg='#000000')
        header_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Description
        desc_label = tk.Label(content_frame, 
                             text="Analyze and explore the structure and content of a single ReqIF file", 
                             font=('Arial', 10), bg='#FFFFFF', fg='#666666', wraplength=600)
        desc_label.pack(anchor=tk.W, pady=(0, 20))
        
        # File selection frame
        file_frame = tk.LabelFrame(content_frame, text="Select File", 
                                  font=('Arial', 10, 'bold'), bg='#FFFFFF', fg='#000000')
        file_frame.pack(fill=tk.X, pady=(0, 20))
        
        file_select_frame = tk.Frame(file_frame, bg='#FFFFFF')
        file_select_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(file_select_frame, text="ReqIF File:", font=('Arial', 10), 
                bg='#FFFFFF', fg='#000000').pack(side=tk.LEFT)
        
        file_entry = tk.Entry(file_select_frame, textvariable=self.visualize_file_path, 
                             font=('Arial', 10), width=50)
        file_entry.pack(side=tk.LEFT, padx=(10, 10), fill=tk.X, expand=True)
        
        file_btn = tk.Button(file_select_frame, text="Browse", command=self._browse_visualize_file,
                            bg='#F0F0F0', fg='#000000', font=('Arial', 10))
        file_btn.pack(side=tk.RIGHT)
        
        # Controls
        controls_frame = tk.Frame(content_frame, bg='#FFFFFF')
        controls_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.visualize_btn = tk.Button(controls_frame, text="Analyze File", 
                                      command=self._visualize_file,
                                      bg='#0078D4', fg='white', font=('Arial', 10, 'bold'),
                                      padx=20, pady=5)
        self.visualize_btn.pack(side=tk.LEFT)
        
        self.visualize_status_label = tk.Label(controls_frame, 
                                             text="Select a ReqIF file to explore and analyze",
                                             font=('Arial', 10), bg='#FFFFFF', fg='#666666')
        self.visualize_status_label.pack(side=tk.LEFT, padx=(20, 0))
    
    def _create_status_bar(self):
        """Create simple status bar"""
        status_frame = tk.Frame(self.main_frame, bg='#F0F0F0', relief='sunken', bd=1)
        status_frame.pack(fill=tk.X, pady=(20, 0))
        
        self.status_label = tk.Label(status_frame, text="Ready", 
                                    font=('Arial', 10), bg='#F0F0F0', fg='#000000')
        self.status_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        version_label = tk.Label(status_frame, text="v1.2.0", 
                                font=('Arial', 10), bg='#F0F0F0', fg='#666666')
        version_label.pack(side=tk.RIGHT, padx=10, pady=5)
    
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
        # Compare button state
        has_both_files = bool(self.file1_path.get() and self.file2_path.get())
        state = tk.NORMAL if has_both_files else tk.DISABLED
        self.compare_btn.configure(state=state)
        
        if has_both_files:
            self.compare_status_label.configure(text="✓ Ready to compare files", fg='#107C10')
        else:
            self.compare_status_label.configure(text="Select two ReqIF files to begin comparison", fg='#666666')
        
        # Visualize button state
        has_visualize_file = bool(self.visualize_file_path.get())
        state = tk.NORMAL if has_visualize_file else tk.DISABLED
        self.visualize_btn.configure(state=state)
        
        if has_visualize_file:
            self.visualize_status_label.configure(text="✓ Ready to analyze file", fg='#107C10')
        else:
            self.visualize_status_label.configure(text="Select a ReqIF file to explore and analyze", fg='#666666')
    
    def _browse_file1(self):
        """Browse for first file"""
        try:
            filename = filedialog.askopenfilename(
                title="Select Original ReqIF File",
                filetypes=[
                    ("ReqIF files", "*.reqif"),
                    ("ReqIF archives", "*.reqifz"),
                    ("All files", "*.*")
                ]
            )
            if filename:
                self.file1_path.set(filename)
                basename = os.path.basename(filename)
                self.status_label.configure(text=f"Original file selected: {basename}", fg='#0078D4')
        except Exception as e:
            self._show_error("File Selection Error", f"Failed to select original file:\n{str(e)}")
    
    def _browse_file2(self):
        """Browse for second file"""
        try:
            filename = filedialog.askopenfilename(
                title="Select Modified ReqIF File",
                filetypes=[
                    ("ReqIF files", "*.reqif"),
                    ("ReqIF archives", "*.reqifz"),
                    ("All files", "*.*")
                ]
            )
            if filename:
                self.file2_path.set(filename)
                basename = os.path.basename(filename)
                self.status_label.configure(text=f"Modified file selected: {basename}", fg='#0078D4')
        except Exception as e:
            self._show_error("File Selection Error", f"Failed to select modified file:\n{str(e)}")
    
    def _browse_visualize_file(self):
        """Browse for visualization file"""
        try:
            filename = filedialog.askopenfilename(
                title="Select ReqIF File to Analyze",
                filetypes=[
                    ("ReqIF files", "*.reqif"),
                    ("ReqIF archives", "*.reqifz"),
                    ("All files", "*.*")
                ]
            )
            if filename:
                self.visualize_file_path.set(filename)
                basename = os.path.basename(filename)
                self.status_label.configure(text=f"Analysis file selected: {basename}", fg='#0078D4')
        except Exception as e:
            self._show_error("File Selection Error", f"Failed to select analysis file:\n{str(e)}")
    
    def _compare_files(self):
        """Compare files"""
        if not (self.file1_path.get() and self.file2_path.get()):
            self._show_warning("Missing Files", "Please select both files to compare.")
            return
        
        self._show_progress("Initializing comparison...")
        self.compare_btn.configure(state=tk.DISABLED, text="Comparing...")
        self.root.update()
        
        def compare_in_thread():
            try:
                self.root.after_idle(lambda: self._show_progress("Parsing original file..."))
                file1_reqs = self.parser.parse_file(self.file1_path.get())
                
                self.root.after_idle(lambda: self._show_progress("Parsing modified file..."))
                file2_reqs = self.parser.parse_file(self.file2_path.get())
                
                self.root.after_idle(lambda: self._show_progress("Analyzing differences..."))
                results = self.comparator.compare_requirements(file1_reqs, file2_reqs)
                
                def show_results():
                    try:
                        self.comparison_window = ComparisonResultsGUI(self.root, results)
                        stats = results.get('statistics', {})
                        changes = stats.get('added_count', 0) + stats.get('deleted_count', 0) + stats.get('modified_count', 0)
                        self._show_success(f"Comparison complete - {changes} changes found")
                        self.compare_btn.configure(state=tk.NORMAL, text="Compare Files")
                    except Exception as e:
                        self._show_error("Results Error", f"Failed to display results:\n{str(e)}")
                        self.compare_btn.configure(state=tk.NORMAL, text="Compare Files")
                
                self.root.after_idle(show_results)
                
            except Exception as e:
                error_message = str(e)
                def show_error():
                    self._show_error("Comparison Failed", f"File comparison failed:\n{error_message}")
                    self.compare_btn.configure(state=tk.NORMAL, text="Compare Files")
                
                self.root.after_idle(show_error)
        
        threading.Thread(target=compare_in_thread, daemon=True).start()
    
    def _visualize_file(self):
        """Visualize file"""
        if not self.visualize_file_path.get():
            self._show_warning("Missing File", "Please select a file to analyze.")
            return
        
        self._show_progress("Initializing analysis...")
        self.visualize_btn.configure(state=tk.DISABLED, text="Analyzing...")
        self.root.update()
        
        def visualize_in_thread():
            try:
                self.root.after_idle(lambda: self._show_progress("Parsing ReqIF file..."))
                requirements = self.parser.parse_file(self.visualize_file_path.get())
                
                def show_visualizer():
                    try:
                        self.visualizer_window = VisualizerGUI(
                            self.root, 
                            requirements, 
                            self.visualize_file_path.get()
                        )
                        self._show_success(f"Analysis complete - {len(requirements)} requirements loaded")
                        self.visualize_btn.configure(state=tk.NORMAL, text="Analyze File")
                    except Exception as e:
                        self._show_error("Analysis Error", f"Failed to display analysis:\n{str(e)}")
                        self.visualize_btn.configure(state=tk.NORMAL, text="Analyze File")
                
                self.root.after_idle(show_visualizer)
                
            except Exception as e:
                error_message = str(e)
                def show_error():
                    self._show_error("Analysis Failed", f"File analysis failed:\n{error_message}")
                    self.visualize_btn.configure(state=tk.NORMAL, text="Analyze File")
                
                self.root.after_idle(show_error)
        
        threading.Thread(target=visualize_in_thread, daemon=True).start()
    
    def _show_progress(self, message):
        """Show progress message"""
        self.status_label.configure(text=message, fg='#0078D4')
    
    def _show_success(self, message):
        """Show success message"""
        self.status_label.configure(text=message, fg='#107C10')
    
    def _show_error(self, title, message):
        """Show error"""
        self.status_label.configure(text="Error occurred - Check details", fg='#D13438')
        messagebox.showerror(title, message)
    
    def _show_warning(self, title, message):
        """Show warning"""
        self.status_label.configure(text="Warning - Check requirements", fg='#FF8C00')
        messagebox.showwarning(title, message)
    
    def run(self):
        """Run the application"""
        try:
            self._show_success("Beyond ReqIF ready - File comparison and analysis available")
            self.notebook.select(0)
            self.root.mainloop()
        except Exception as e:
            self._show_error("Runtime Error", f"Application runtime error:\n{str(e)}")
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
        print("Starting Beyond ReqIF v1.2.0 - Simplified Version...")
        app = ReqIFToolMVP()
        app.run()
    except Exception as e:
        print(f"Critical startup error: {e}")
        try:
            import traceback
            traceback.print_exc()
            
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "Startup Error", 
                f"Failed to start Beyond ReqIF:\n\n{str(e)}"
            )
            root.destroy()
        except Exception:
            print("Failed to show error dialog - check console output")


if __name__ == "__main__":
    main()