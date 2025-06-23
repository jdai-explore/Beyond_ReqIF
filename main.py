#!/usr/bin/env python3
"""
ReqIF Tool Suite - Apple Design Guidelines Version with 60-30-10 Color Principle
Fixed: Updated to use new color system from theme_manager
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
from theme_manager import (
    configure_main_window, apply_theme, get_color, get_semantic_color,
    create_title_label, create_body_label, create_primary_button, 
    create_secondary_button, create_section_separator, Spacing,
    AppleColors, AppleFonts, style_text_widget
)


class ReqIFToolMVP:
    """
    ReqIF Tool Suite with Apple Design Guidelines and 60-30-10 Color Principle
    Fixed: Updated to use new color system
    """
    
    def __init__(self):
        # Initialize error handling
        self.error_handler = ErrorHandler()
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("Beyond ReqIF v1.2.0 - Professional Edition")
        self.root.geometry("1100x750")
        
        # Apply 60-30-10 Apple Design Guidelines
        configure_main_window(self.root)
        
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
        """Create Apple-styled UI with 60-30-10 colors"""
        # Create main container with proper padding
        self.main_frame = ttk.Frame(self.root, padding="24")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for responsive design
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(2, weight=1)
        
        # Create sections
        self._create_header()
        self._create_main_content()
        self._create_status_bar()
    
    def _create_header(self):
        """Create Apple-style header with 60-30-10 colors"""
        # Use 30% secondary background for header area
        header_frame = ttk.Frame(self.main_frame, style='Header.TFrame', padding="15")
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, Spacing.XXL))
        header_frame.columnconfigure(1, weight=1)
        
        # Left side - Title and description
        title_frame = ttk.Frame(header_frame)
        title_frame.grid(row=0, column=0, sticky=(tk.W))
        
        title_label = create_title_label(title_frame, "Beyond ReqIF", "title_1")
        title_label.grid(row=0, column=0, sticky=(tk.W))
        
        version_label = create_body_label(title_frame, "Professional Edition v1.2.0", secondary=True)
        version_label.grid(row=1, column=0, sticky=(tk.W), pady=(2, 0))
        
        subtitle_label = create_body_label(title_frame, "Advanced Requirements Analysis and Comparison", secondary=True)
        subtitle_label.grid(row=2, column=0, sticky=(tk.W), pady=(4, 0))
        
        # Right side - File format support info
        info_frame = ttk.Frame(header_frame)
        info_frame.grid(row=0, column=1, sticky=(tk.E))
        
        support_label = create_body_label(info_frame, "Supports: ReqIF • ReqIFZ", secondary=True)
        support_label.grid(row=0, column=0, sticky=(tk.E))
        
        # Add subtle separator
        separator = create_section_separator(self.main_frame)
        separator.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, Spacing.XL))
    
    def _create_main_content(self):
        """Create main content with Apple-styled tabs using 60-30-10 colors"""
        # Create notebook with 30% secondary background for tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create tabs
        self._create_compare_tab()
        self._create_visualize_tab()
    
    def _create_compare_tab(self):
        """Create Apple-styled comparison tab with 60-30-10 colors"""
        # Main content uses 60% dominant background
        compare_frame = ttk.Frame(self.notebook, padding="30")
        self.notebook.add(compare_frame, text="Compare Files")
        
        # Configure grid
        compare_frame.columnconfigure(0, weight=1)
        compare_frame.rowconfigure(4, weight=1)
        
        # Section header
        section_header = create_title_label(compare_frame, "File Comparison", "headline")
        section_header.grid(row=0, column=0, sticky=(tk.W), pady=(0, Spacing.L))
        
        description = create_body_label(compare_frame, 
                                       "Compare two ReqIF files to identify added, deleted, and modified requirements", 
                                       secondary=True)
        description.grid(row=1, column=0, sticky=(tk.W), pady=(0, Spacing.XXL))
        
        # File selection area with 30% secondary background
        files_frame = ttk.LabelFrame(compare_frame, text="Select Files", padding="20")
        files_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, Spacing.L))
        files_frame.columnconfigure(1, weight=1)
        
        # File 1 selection
        file1_label = create_body_label(files_frame, "Original File:")
        file1_label.grid(row=0, column=0, sticky=(tk.W), pady=(0, 8), padx=(0, Spacing.M))
        
        # Entry fields use 60% dominant background
        file1_entry = ttk.Entry(files_frame, textvariable=self.file1_path, width=50,
                               font=AppleFonts.get("body"))
        file1_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 8), padx=(0, Spacing.M))
        
        # Secondary buttons use 30% secondary background
        file1_btn = create_secondary_button(files_frame, "Browse", self._browse_file1)
        file1_btn.grid(row=0, column=2, pady=(0, 8))
        
        # File 2 selection
        file2_label = create_body_label(files_frame, "Modified File:")
        file2_label.grid(row=1, column=0, sticky=(tk.W), pady=(8, 0), padx=(0, Spacing.M))
        
        file2_entry = ttk.Entry(files_frame, textvariable=self.file2_path, width=50,
                               font=AppleFonts.get("body"))
        file2_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(8, 0), padx=(0, Spacing.M))
        
        file2_btn = create_secondary_button(files_frame, "Browse", self._browse_file2)
        file2_btn.grid(row=1, column=2, pady=(8, 0))
        
        # Controls section
        controls_frame = ttk.Frame(compare_frame)
        controls_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(Spacing.L, Spacing.L))
        controls_frame.columnconfigure(1, weight=1)
        
        # Primary action button uses 10% accent color
        self.compare_btn = create_primary_button(controls_frame, "Compare Files", self._compare_files)
        self.compare_btn.grid(row=0, column=0, sticky=(tk.W))
        
        # Status information
        self.compare_status_label = create_body_label(controls_frame, 
                                                     "Select two ReqIF files to begin comparison", 
                                                     secondary=True)
        self.compare_status_label.grid(row=0, column=1, sticky=(tk.W), padx=(Spacing.L, 0))
        
        # Help text
        help_frame = ttk.Frame(compare_frame)
        help_frame.grid(row=4, column=0, sticky=(tk.W, tk.E))
        
        help_text = create_body_label(help_frame, 
                                     "💡 Tip: Compare ReqIF files to track changes between versions",
                                     secondary=True)
        help_text.grid(row=0, column=0, sticky=(tk.W))
    
    def _create_visualize_tab(self):
        """Create Apple-styled visualization tab with 60-30-10 colors"""
        # Main content uses 60% dominant background
        visualize_frame = ttk.Frame(self.notebook, padding="30")
        self.notebook.add(visualize_frame, text="Analyze File")
        
        # Configure grid
        visualize_frame.columnconfigure(0, weight=1)
        visualize_frame.rowconfigure(3, weight=1)
        
        # Section header
        section_header = create_title_label(visualize_frame, "File Analysis", "headline")
        section_header.grid(row=0, column=0, sticky=(tk.W), pady=(0, Spacing.L))
        
        description = create_body_label(visualize_frame,
                                       "Analyze and explore the structure and content of a single ReqIF file",
                                       secondary=True)
        description.grid(row=1, column=0, sticky=(tk.W), pady=(0, Spacing.XXL))
        
        # File selection with 30% secondary background
        file_frame = ttk.LabelFrame(visualize_frame, text="Select File", padding="20")
        file_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, Spacing.XL))
        file_frame.columnconfigure(1, weight=1)
        
        file_label = create_body_label(file_frame, "ReqIF File:")
        file_label.grid(row=0, column=0, sticky=(tk.W), padx=(0, Spacing.M))
        
        # Entry field uses 60% dominant background
        file_entry = ttk.Entry(file_frame, textvariable=self.visualize_file_path, width=50,
                              font=AppleFonts.get("body"))
        file_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, Spacing.M))
        
        # Secondary button uses 30% secondary background
        file_btn = create_secondary_button(file_frame, "Browse", self._browse_visualize_file)
        file_btn.grid(row=0, column=2)
        
        # Controls section
        controls_frame = ttk.Frame(visualize_frame)
        controls_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, Spacing.L))
        controls_frame.columnconfigure(1, weight=1)
        
        # Primary action button uses 10% accent color
        self.visualize_btn = create_primary_button(controls_frame, "Analyze File", self._visualize_file)
        self.visualize_btn.grid(row=0, column=0, sticky=(tk.W))
        
        # Status information
        self.visualize_status_label = create_body_label(controls_frame,
                                                       "Select a ReqIF file to explore and analyze",
                                                       secondary=True)
        self.visualize_status_label.grid(row=0, column=1, sticky=(tk.W), padx=(Spacing.L, 0))
        
        # Features list
        features_frame = ttk.Frame(visualize_frame)
        features_frame.grid(row=4, column=0, sticky=(tk.W, tk.E))
        
        features_text = create_body_label(features_frame,
                                         "📊 Features: Statistics • Search & Filter • Data Export • Requirement Details",
                                         secondary=True)
        features_text.grid(row=0, column=0, sticky=(tk.W))
    
    def _create_status_bar(self):
        """Create Apple-styled status bar with 60-30-10 colors"""
        # Status bar uses 30% secondary background
        status_frame = ttk.Frame(self.main_frame, style='Header.TFrame', padding="10")
        status_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(Spacing.L, 0))
        status_frame.columnconfigure(0, weight=1)
        
        # Add subtle separator above status bar using 30% secondary color
        separator = ttk.Separator(status_frame, orient='horizontal')
        separator.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, Spacing.S))
        
        # Status content
        status_content = ttk.Frame(status_frame)
        status_content.grid(row=1, column=0, sticky=(tk.W, tk.E))
        status_content.columnconfigure(1, weight=1)
        
        self.status_label = create_body_label(status_content, "Ready", secondary=True)
        self.status_label.grid(row=0, column=0, sticky=(tk.W))
        
        # Right side status info
        right_status = ttk.Frame(status_content)
        right_status.grid(row=0, column=2, sticky=(tk.E))
        
        # Version indicator
        version_indicator = create_body_label(right_status, "v1.2.0", secondary=True)
        version_indicator.grid(row=0, column=1, sticky=(tk.E))
    
    def _setup_monitoring(self):
        """Setup file path monitoring with enhanced feedback"""
        def update_button_states(*args):
            self._update_button_states()
        
        self.file1_path.trace_add("write", update_button_states)
        self.file2_path.trace_add("write", update_button_states)
        self.visualize_file_path.trace_add("write", update_button_states)
        
        self._update_button_states()
    
    def _update_button_states(self):
        """Update button states with enhanced visual feedback using 60-30-10 colors"""
        # Compare button state
        has_both_files = bool(self.file1_path.get() and self.file2_path.get())
        self.compare_btn.configure(state=tk.NORMAL if has_both_files else tk.DISABLED)
        
        if has_both_files:
            self.compare_status_label.configure(text="✓ Ready to compare files")
            # Use 10% accent color for success state
            self.compare_status_label.configure(foreground=get_semantic_color("success"))
        else:
            self.compare_status_label.configure(text="Select two ReqIF files to begin comparison")
            # Use secondary text color
            self.compare_status_label.configure(foreground=get_color("fg_secondary"))
        
        # Visualize button state
        has_visualize_file = bool(self.visualize_file_path.get())
        self.visualize_btn.configure(state=tk.NORMAL if has_visualize_file else tk.DISABLED)
        
        if has_visualize_file:
            self.visualize_status_label.configure(text="✓ Ready to analyze file")
            # Use 10% accent color for success state
            self.visualize_status_label.configure(foreground=get_semantic_color("success"))
        else:
            self.visualize_status_label.configure(text="Select a ReqIF file to explore and analyze")
            # Use secondary text color
            self.visualize_status_label.configure(foreground=get_color("fg_secondary"))
    
    # =============================================================================
    # FILE OPERATIONS WITH ENHANCED USER FEEDBACK
    # =============================================================================
    
    def _browse_file1(self):
        """Browse for first file with enhanced feedback"""
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
                # Enhanced status feedback with 10% accent color
                basename = os.path.basename(filename)
                self.status_label.configure(text=f"Original file selected: {basename}")
                self.status_label.configure(foreground=get_semantic_color("info"))
        except Exception as e:
            self._show_error("File Selection Error", f"Failed to select original file:\n{str(e)}")
    
    def _browse_file2(self):
        """Browse for second file with enhanced feedback"""
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
                # Enhanced status feedback with 10% accent color
                basename = os.path.basename(filename)
                self.status_label.configure(text=f"Modified file selected: {basename}")
                self.status_label.configure(foreground=get_semantic_color("info"))
        except Exception as e:
            self._show_error("File Selection Error", f"Failed to select modified file:\n{str(e)}")
    
    def _browse_visualize_file(self):
        """Browse for visualization file with enhanced feedback"""
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
                # Enhanced status feedback with 10% accent color
                basename = os.path.basename(filename)
                self.status_label.configure(text=f"Analysis file selected: {basename}")
                self.status_label.configure(foreground=get_semantic_color("info"))
        except Exception as e:
            self._show_error("File Selection Error", f"Failed to select analysis file:\n{str(e)}")
    
    def _compare_files(self):
        """Compare files with enhanced progress feedback using 60-30-10 colors"""
        if not (self.file1_path.get() and self.file2_path.get()):
            self._show_warning("Missing Files", "Please select both files to compare.")
            return
        
        # Enhanced progress feedback with 10% accent color
        self._show_progress("Initializing comparison...")
        self.compare_btn.configure(state=tk.DISABLED, text="Comparing...")
        self.root.update()
        
        def compare_in_thread():
            try:
                # Parse files with progress updates
                self.root.after_idle(lambda: self._show_progress("Parsing original file..."))
                file1_reqs = self.parser.parse_file(self.file1_path.get())
                
                self.root.after_idle(lambda: self._show_progress("Parsing modified file..."))
                file2_reqs = self.parser.parse_file(self.file2_path.get())
                
                # Compare with progress
                self.root.after_idle(lambda: self._show_progress("Analyzing differences..."))
                results = self.comparator.compare_requirements(file1_reqs, file2_reqs)
                
                # Show results
                def show_results():
                    try:
                        self.comparison_window = ComparisonResultsGUI(self.root, results)
                        # Enhanced success feedback with 10% accent color
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
        """Visualize file with enhanced progress feedback using 60-30-10 colors"""
        if not self.visualize_file_path.get():
            self._show_warning("Missing File", "Please select a file to analyze.")
            return
        
        # Enhanced progress feedback with 10% accent color
        self._show_progress("Initializing analysis...")
        self.visualize_btn.configure(state=tk.DISABLED, text="Analyzing...")
        self.root.update()
        
        def visualize_in_thread():
            try:
                # Parse file with progress
                self.root.after_idle(lambda: self._show_progress("Parsing ReqIF file..."))
                requirements = self.parser.parse_file(self.visualize_file_path.get())
                
                # Show visualizer
                def show_visualizer():
                    try:
                        self.visualizer_window = VisualizerGUI(
                            self.root, 
                            requirements, 
                            self.visualize_file_path.get()
                        )
                        # Enhanced success feedback with 10% accent color
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
    
    # =============================================================================
    # ENHANCED FEEDBACK METHODS USING 60-30-10 COLORS
    # =============================================================================
    
    def _show_progress(self, message):
        """Show progress message with 10% accent color"""
        self.status_label.configure(text=message, foreground=get_semantic_color("info"))
    
    def _show_success(self, message):
        """Show success message with 10% accent color"""
        self.status_label.configure(text=message, foreground=get_semantic_color("success"))
    
    def _show_error(self, title, message):
        """Show error with 10% accent color"""
        self.status_label.configure(text="Error occurred - Check details", 
                                   foreground=get_semantic_color("error"))
        messagebox.showerror(title, message)
    
    def _show_warning(self, title, message):
        """Show warning with 10% accent color"""
        self.status_label.configure(text="Warning - Check requirements", 
                                   foreground=get_semantic_color("warning"))
        messagebox.showwarning(title, message)
    
    def _show_info(self, title, message):
        """Show info with 10% accent color"""
        self.status_label.configure(text="Information displayed", 
                                   foreground=get_semantic_color("info"))
        messagebox.showinfo(title, message)
    
    def run(self):
        """Run the application with enhanced startup"""
        try:
            # Enhanced startup feedback with 10% accent color
            self._show_success("Beyond ReqIF ready - File comparison and analysis available")
            
            # Set focus to first tab
            self.notebook.select(0)
            
            self.root.mainloop()
        except Exception as e:
            self._show_error("Runtime Error", f"Application runtime error:\n{str(e)}")
        finally:
            self._cleanup()
    
    def _cleanup(self):
        """Enhanced cleanup on exit"""
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
    """Main function with enhanced error handling"""
    try:
        print("Starting Beyond ReqIF v1.2.0 with 60-30-10 Color Principle...")
        app = ReqIFToolMVP()
        app.run()
    except Exception as e:
        print(f"Critical startup error: {e}")
        try:
            import traceback
            traceback.print_exc()
            
            # Try to show error dialog with Apple styling
            root = tk.Tk()
            root.withdraw()
            
            # Apply basic Apple styling
            configure_main_window(root)
            
            messagebox.showerror(
                "Startup Error", 
                f"Failed to start Beyond ReqIF:\n\n{str(e)}\n\n"
                "Please check the console for detailed error information."
            )
            root.destroy()
        except Exception:
            print("Failed to show error dialog - check console output")


if __name__ == "__main__":
    main()