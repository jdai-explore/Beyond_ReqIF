#!/usr/bin/env python3
"""
ReqIF Tool Suite - Native GUI Version with Enhanced Folder Comparison
FIXED: Added missing typing imports and corrected threading initialization
Completely native tkinter with individual file statistics support
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading as thread_module
from typing import Optional, Dict, Any, List  # FIXED: Added missing typing imports

# Import core modules
from reqif_parser import ReqIFParser
from reqif_comparator import ReqIFComparator
from comparison_gui import ComparisonResultsGUI
from visualizer_gui import VisualizerGUI
from error_handler import ErrorHandler
from folder_comparator import FolderComparator
from folder_comparison_gui import FolderComparisonResultsGUI
from progress_dialog import ProgressDialog


class ReqIFToolNative:
    """
    ReqIF Tool Suite - Native GUI Version with Enhanced Folder Comparison
    UPDATED for Phase 3: Dynamic field support without hardcoded field assumptions
    Pure tkinter with individual file statistics support
    """
    
    def __init__(self):
        # Initialize error handling
        self.error_handler = ErrorHandler()
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("Beyond ReqIF v1.3.0 - Enhanced Edition (Phase 3) with Dynamic Field Support")
        self.root.geometry("1150x750")
        
        # Initialize components
        self.parser = ReqIFParser()
        self.comparator = ReqIFComparator()
        self.folder_comparator = FolderComparator()
        
        # File tracking
        self.file1_path = tk.StringVar()
        self.file2_path = tk.StringVar()
        self.visualize_file_path = tk.StringVar()
        
        # Folder tracking
        self.folder1_path = tk.StringVar()
        self.folder2_path = tk.StringVar()
        
        # UI state
        self.comparison_window = None
        self.visualizer_window = None
        self.folder_comparison_window = None
        self.progress_dialog = None
        
        # Create UI
        self._create_main_ui()
        
        # Setup monitoring
        self._setup_monitoring()
    
    def _create_main_ui(self):
        """Create native UI"""
        # Create main container
        self.main_frame = tk.Frame(self.root, padx=20, pady=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create sections
        self._create_header()
        self._create_main_content()
        self._create_status_bar()
    
    def _create_header(self):
        """Create enhanced header"""
        header_frame = tk.Frame(self.main_frame, relief='ridge', bd=2)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Enhanced title
        title_label = tk.Label(header_frame, text="Beyond ReqIF Enhanced (Phase 3)", 
                              font=('Arial', 18, 'bold'))
        title_label.pack(side=tk.LEFT, padx=15, pady=15)
        
        # Enhanced version with dynamic field support
        version_label = tk.Label(header_frame, text="Dynamic Field Edition v1.3.0 + Phase 3", 
                                font=('Arial', 11))
        version_label.pack(side=tk.RIGHT, padx=15, pady=15)
    
    def _create_main_content(self):
        """Create main content with notebook"""
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self._create_compare_tab()
        self._create_enhanced_compare_folders_tab()
        self._create_visualize_tab()
    
    def _create_compare_tab(self):
        """Create comparison tab"""
        compare_frame = tk.Frame(self.notebook)
        self.notebook.add(compare_frame, text="📊 Compare Files")
        
        # Main content frame
        content_frame = tk.Frame(compare_frame, padx=25, pady=25)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Section header
        header_label = tk.Label(content_frame, text="File Comparison", 
                               font=('Arial', 16, 'bold'))
        header_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Description
        desc_label = tk.Label(content_frame, 
                             text="Compare two ReqIF files to identify changes using dynamic field detection", 
                             font=('Arial', 11), wraplength=600, justify=tk.LEFT)
        desc_label.pack(anchor=tk.W, pady=(0, 25))
        
        # File selection frame
        files_frame = tk.LabelFrame(content_frame, text="Select Files", 
                                   font=('Arial', 11, 'bold'), padx=15, pady=15)
        files_frame.pack(fill=tk.X, pady=(0, 25))
        
        # File 1
        file1_frame = tk.Frame(files_frame)
        file1_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(file1_frame, text="Original File:", font=('Arial', 11, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        
        file1_input_frame = tk.Frame(file1_frame)
        file1_input_frame.pack(fill=tk.X)
        
        file1_entry = tk.Entry(file1_input_frame, textvariable=self.file1_path, 
                              font=('Arial', 10), relief='sunken', bd=2)
        file1_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        file1_btn = tk.Button(file1_input_frame, text="Browse...", command=self._browse_file1,
                             font=('Arial', 10), relief='raised', bd=2, padx=15)
        file1_btn.pack(side=tk.RIGHT)
        
        # File 2
        file2_frame = tk.Frame(files_frame)
        file2_frame.pack(fill=tk.X)
        
        tk.Label(file2_frame, text="Modified File:", font=('Arial', 11, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        
        file2_input_frame = tk.Frame(file2_frame)
        file2_input_frame.pack(fill=tk.X)
        
        file2_entry = tk.Entry(file2_input_frame, textvariable=self.file2_path, 
                              font=('Arial', 10), relief='sunken', bd=2)
        file2_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        file2_btn = tk.Button(file2_input_frame, text="Browse...", command=self._browse_file2,
                             font=('Arial', 10), relief='raised', bd=2, padx=15)
        file2_btn.pack(side=tk.RIGHT)
        
        # Controls
        controls_frame = tk.Frame(content_frame)
        controls_frame.pack(fill=tk.X, pady=(15, 0))
        
        self.compare_btn = tk.Button(controls_frame, text="🔍 Compare Files", 
                                    command=self._compare_files,
                                    font=('Arial', 12, 'bold'), relief='raised', bd=3,
                                    padx=25, pady=8, cursor='hand2')
        self.compare_btn.pack(side=tk.LEFT)
        
        self.compare_status_label = tk.Label(controls_frame, 
                                           text="Select two ReqIF files to begin dynamic field comparison",
                                           font=('Arial', 11))
        self.compare_status_label.pack(side=tk.LEFT, padx=(25, 0))
    
    def _create_enhanced_compare_folders_tab(self):
        """Create enhanced folder comparison tab with individual file statistics"""
        compare_folders_frame = tk.Frame(self.notebook)
        self.notebook.add(compare_folders_frame, text="📁 Enhanced Folders")
        
        # Main content frame
        content_frame = tk.Frame(compare_folders_frame, padx=25, pady=25)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Section header
        header_label = tk.Label(content_frame, text="Enhanced Folder Comparison (Phase 3)", 
                               font=('Arial', 16, 'bold'))
        header_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Enhanced description
        desc_label = tk.Label(content_frame, 
                             text="Compare two folders containing ReqIF files with dynamic field detection and detailed individual file statistics", 
                             font=('Arial', 11), wraplength=600, justify=tk.LEFT)
        desc_label.pack(anchor=tk.W, pady=(0, 25))
        
        # Enhanced info box with Phase 3 features
        info_frame = tk.Frame(content_frame, relief='solid', bd=1, bg='lightcyan')
        info_frame.pack(fill=tk.X, pady=(0, 25))
        
        info_text = """✨ Phase 3 enhanced folder comparison features:
• Dynamic field detection - no hardcoded field assumptions
• Individual file statistics with adaptive field analysis
• Detailed change tracking per file with any field structure
• Parsing success/failure monitoring per file
• File size and requirement count analysis
• Enhanced export capabilities with discovered field data
• Analysis insights and recommendations based on actual content
• Maximum 200 files per comparison
• Progress tracking with cancellation"""
        
        tk.Label(info_frame, text=info_text, font=('Arial', 10), 
                justify=tk.LEFT, bg='lightcyan', padx=15, pady=10).pack(anchor=tk.W)
        
        # Folder selection frame
        folders_frame = tk.LabelFrame(content_frame, text="Select Folders", 
                                     font=('Arial', 11, 'bold'), padx=15, pady=15)
        folders_frame.pack(fill=tk.X, pady=(0, 25))
        
        # Folder 1
        folder1_frame = tk.Frame(folders_frame)
        folder1_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(folder1_frame, text="Original Folder:", font=('Arial', 11, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        
        folder1_input_frame = tk.Frame(folder1_frame)
        folder1_input_frame.pack(fill=tk.X)
        
        folder1_entry = tk.Entry(folder1_input_frame, textvariable=self.folder1_path, 
                                font=('Arial', 10), relief='sunken', bd=2)
        folder1_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        folder1_btn = tk.Button(folder1_input_frame, text="Browse...", command=self._browse_folder1,
                               font=('Arial', 10), relief='raised', bd=2, padx=15)
        folder1_btn.pack(side=tk.RIGHT)
        
        # Folder 2
        folder2_frame = tk.Frame(folders_frame)
        folder2_frame.pack(fill=tk.X)
        
        tk.Label(folder2_frame, text="Modified Folder:", font=('Arial', 11, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        
        folder2_input_frame = tk.Frame(folder2_frame)
        folder2_input_frame.pack(fill=tk.X)
        
        folder2_entry = tk.Entry(folder2_input_frame, textvariable=self.folder2_path, 
                                font=('Arial', 10), relief='sunken', bd=2)
        folder2_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        folder2_btn = tk.Button(folder2_input_frame, text="Browse...", command=self._browse_folder2,
                               font=('Arial', 10), relief='raised', bd=2, padx=15)
        folder2_btn.pack(side=tk.RIGHT)
        
        # Enhanced controls
        controls_frame = tk.Frame(content_frame)
        controls_frame.pack(fill=tk.X, pady=(15, 0))
        
        self.compare_folders_btn = tk.Button(controls_frame, text="🔍 Dynamic Compare", 
                                            command=self._compare_folders,
                                            font=('Arial', 12, 'bold'), relief='raised', bd=3,
                                            padx=25, pady=8, cursor='hand2')
        self.compare_folders_btn.pack(side=tk.LEFT)
        
        self.compare_folders_status_label = tk.Label(controls_frame, 
                                                    text="Select two folders for dynamic field comparison with individual file analysis",
                                                    font=('Arial', 11))
        self.compare_folders_status_label.pack(side=tk.LEFT, padx=(25, 0))
    
    def _create_visualize_tab(self):
        """Create visualization tab"""
        visualize_frame = tk.Frame(self.notebook)
        self.notebook.add(visualize_frame, text="📈 Analyze File")
        
        # Main content frame
        content_frame = tk.Frame(visualize_frame, padx=25, pady=25)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Section header
        header_label = tk.Label(content_frame, text="Dynamic Field Analysis", 
                               font=('Arial', 16, 'bold'))
        header_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Description
        desc_label = tk.Label(content_frame, 
                             text="Analyze and explore the structure and content of a single ReqIF file using dynamic field detection", 
                             font=('Arial', 11), wraplength=600, justify=tk.LEFT)
        desc_label.pack(anchor=tk.W, pady=(0, 25))
        
        # File selection frame
        file_frame = tk.LabelFrame(content_frame, text="Select File", 
                                  font=('Arial', 11, 'bold'), padx=15, pady=15)
        file_frame.pack(fill=tk.X, pady=(0, 25))
        
        tk.Label(file_frame, text="ReqIF File:", font=('Arial', 11, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        
        file_select_frame = tk.Frame(file_frame)
        file_select_frame.pack(fill=tk.X)
        
        file_entry = tk.Entry(file_select_frame, textvariable=self.visualize_file_path, 
                             font=('Arial', 10), relief='sunken', bd=2)
        file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        file_btn = tk.Button(file_select_frame, text="Browse...", command=self._browse_visualize_file,
                            font=('Arial', 10), relief='raised', bd=2, padx=15)
        file_btn.pack(side=tk.RIGHT)
        
        # Controls
        controls_frame = tk.Frame(content_frame)
        controls_frame.pack(fill=tk.X, pady=(15, 0))
        
        self.visualize_btn = tk.Button(controls_frame, text="📊 Analyze Fields", 
                                      command=self._visualize_file,
                                      font=('Arial', 12, 'bold'), relief='raised', bd=3,
                                      padx=25, pady=8, cursor='hand2')
        self.visualize_btn.pack(side=tk.LEFT)
        
        self.visualize_status_label = tk.Label(controls_frame, 
                                             text="Select a ReqIF file to explore and analyze with dynamic field detection",
                                             font=('Arial', 11))
        self.visualize_status_label.pack(side=tk.LEFT, padx=(25, 0))
    
    def _create_status_bar(self):
        """Create enhanced status bar"""
        status_frame = tk.Frame(self.main_frame, relief='sunken', bd=2)
        status_frame.pack(fill=tk.X, pady=(20, 0))
        
        self.status_label = tk.Label(status_frame, text="Ready - Phase 3: Dynamic field detection enabled", 
                                    font=('Arial', 10), anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, padx=10, pady=8)
        
        version_label = tk.Label(status_frame, text="Phase 3 v1.3.0", 
                                font=('Arial', 10))
        version_label.pack(side=tk.RIGHT, padx=10, pady=8)
    
    def _setup_monitoring(self):
        """Setup file path monitoring"""
        def update_button_states(*args):
            self._update_button_states()
        
        self.file1_path.trace_add("write", update_button_states)
        self.file2_path.trace_add("write", update_button_states)
        self.folder1_path.trace_add("write", update_button_states)
        self.folder2_path.trace_add("write", update_button_states)
        self.visualize_file_path.trace_add("write", update_button_states)
        
        self._update_button_states()
    
    def _update_button_states(self):
        """UPDATED Phase 3: Enhanced button states without hardcoded field references"""
        # Compare button state
        has_both_files = bool(self.file1_path.get() and self.file2_path.get())
        
        if has_both_files:
            self.compare_btn.configure(state=tk.NORMAL, bg='lightgreen')
            self.compare_status_label.configure(text="✓ Ready for dynamic field comparison", fg='darkgreen')
        else:
            self.compare_btn.configure(state=tk.DISABLED, bg='lightgray')
            self.compare_status_label.configure(text="Select two ReqIF files to begin dynamic field comparison", fg='black')
        
        # Enhanced compare folders button state
        has_both_folders = bool(self.folder1_path.get() and self.folder2_path.get())
        
        if has_both_folders:
            self.compare_folders_btn.configure(state=tk.NORMAL, bg='lightblue')
            self.compare_folders_status_label.configure(text="✓ Ready for dynamic comparison with adaptive field analysis", fg='darkblue')
        else:
            self.compare_folders_btn.configure(state=tk.DISABLED, bg='lightgray')
            self.compare_folders_status_label.configure(text="Select two folders for dynamic field comparison with individual file analysis", fg='black')
        
        # Visualize button state
        has_visualize_file = bool(self.visualize_file_path.get())
        
        if has_visualize_file:
            self.visualize_btn.configure(state=tk.NORMAL, bg='lightblue')
            self.visualize_status_label.configure(text="✓ Ready for dynamic field analysis", fg='darkblue')
        else:
            self.visualize_btn.configure(state=tk.DISABLED, bg='lightgray')
            self.visualize_status_label.configure(text="Select a ReqIF file to explore and analyze with dynamic field detection", fg='black')
    
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
                self.status_label.configure(text=f"Original file selected: {basename}", fg='blue')
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
                self.status_label.configure(text=f"Modified file selected: {basename}", fg='blue')
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
                self.status_label.configure(text=f"Analysis file selected: {basename}", fg='blue')
        except Exception as e:
            self._show_error("File Selection Error", f"Failed to select analysis file:\n{str(e)}")
    
    def _browse_folder1(self):
        """Browse for first folder"""
        try:
            foldername = filedialog.askdirectory(
                title="Select Original Folder"
            )
            if foldername:
                self.folder1_path.set(foldername)
                basename = os.path.basename(foldername)
                self.status_label.configure(text=f"Original folder selected: {basename}", fg='blue')
        except Exception as e:
            self._show_error("Folder Selection Error", f"Failed to select original folder:\n{str(e)}")
    
    def _browse_folder2(self):
        """Browse for second folder"""
        try:
            foldername = filedialog.askdirectory(
                title="Select Modified Folder"
            )
            if foldername:
                self.folder2_path.set(foldername)
                basename = os.path.basename(foldername)
                self.status_label.configure(text=f"Modified folder selected: {basename}", fg='blue')
        except Exception as e:
            self._show_error("Folder Selection Error", f"Failed to select modified folder:\n{str(e)}")
    
    def _compare_files(self):
        """UPDATED Phase 3: Compare files with dynamic field detection"""
        if not (self.file1_path.get() and self.file2_path.get()):
            self._show_warning("Missing Files", "Please select both files to compare.")
            return
        
        self._show_progress("Initializing dynamic field comparison...")
        self.compare_btn.configure(state=tk.DISABLED, text="Comparing...", bg='yellow')
        self.root.update()
        
        def compare_in_thread():
            try:
                self.root.after_idle(lambda: self._show_progress("Parsing original file with dynamic field detection..."))
                file1_reqs = self.parser.parse_file(self.file1_path.get())
                
                self.root.after_idle(lambda: self._show_progress("Parsing modified file with dynamic field detection..."))
                file2_reqs = self.parser.parse_file(self.file2_path.get())
                
                self.root.after_idle(lambda: self._show_progress("Analyzing differences using adaptive field comparison..."))
                results = self.comparator.compare_requirements(file1_reqs, file2_reqs)
                
                def show_results():
                    try:
                        self.comparison_window = ComparisonResultsGUI(self.root, results)
                        stats = results.get('statistics', {})
                        
                        # UPDATED Phase 3: Dynamic change counting without hardcoded fields
                        change_count = self._count_dynamic_changes(stats)
                        field_count = self._count_available_fields(file1_reqs + file2_reqs)
                        
                        self._show_success(f"Dynamic comparison complete - {change_count} changes found across {field_count} detected fields")
                        self.compare_btn.configure(state=tk.NORMAL, text="🔍 Compare Files")
                        self._update_button_states()
                    except Exception as e:
                        self._show_error("Results Error", f"Failed to display results:\n{str(e)}")
                        self.compare_btn.configure(state=tk.NORMAL, text="🔍 Compare Files")
                        self._update_button_states()
                
                self.root.after_idle(show_results)
                
            except Exception as e:
                error_message = str(e)
                def show_error():
                    self._show_error("Comparison Failed", f"File comparison failed:\n{error_message}")
                    self.compare_btn.configure(state=tk.NORMAL, text="🔍 Compare Files")
                    self._update_button_states()
                
                self.root.after_idle(show_error)
        
        thread_module.Thread(target=compare_in_thread, daemon=True).start()
    
    def _compare_folders(self):
        """UPDATED Phase 3: Enhanced folder comparison with dynamic field analysis"""
        if not (self.folder1_path.get() and self.folder2_path.get()):
            self._show_warning("Missing Folders", "Please select both folders to compare.")
            return
        
        # Show progress dialog
        self.progress_dialog = ProgressDialog(self.root, "Dynamic Folder Comparison", 
                                             "Initializing dynamic folder comparison with adaptive field detection...", True)
        self.progress_dialog.show()
        
        # Setup cancellation
        cancel_flag = thread_module.Event()
        self.progress_dialog.set_cancel_callback(lambda: cancel_flag.set())
        
        self._show_progress("Initializing dynamic folder comparison...")
        self.compare_folders_btn.configure(state=tk.DISABLED, text="Comparing...", bg='yellow')
        self.root.update()
        
        def compare_folders_in_thread():
            try:
                # Setup folder comparator (now enhanced with individual stats)
                self.folder_comparator.set_cancel_flag(cancel_flag)
                self.folder_comparator.set_progress_callback(self.progress_dialog.update_progress)
                
                # Perform comparison (automatically collects individual file statistics)
                results = self.folder_comparator.compare_folders(
                    self.folder1_path.get(), 
                    self.folder2_path.get()
                )
                
                if cancel_flag.is_set():
                    self.root.after_idle(lambda: self._show_comparison_cancelled())
                    return
                
                def show_enhanced_folder_results():
                    try:
                        # Create enhanced comparison window (automatically displays individual stats)
                        self.folder_comparison_window = FolderComparisonResultsGUI(self.root, results)
                        
                        # Get statistics for enhanced success message
                        folder_stats = results.get('folder_statistics', {})
                        req_stats = results.get('aggregated_statistics', {})
                        individual_stats = results.get('individual_file_statistics', {})
                        
                        # UPDATED Phase 3: Calculate enhanced metrics dynamically
                        total_file_changes = (folder_stats.get('files_added', 0) + 
                                            folder_stats.get('files_deleted', 0) + 
                                            folder_stats.get('files_with_changes', 0))
                        
                        total_req_changes = self._count_dynamic_changes(req_stats)
                        
                        # NEW: Get individual file insights
                        total_files_analyzed = (len(individual_stats.get('matched_files', {})) +
                                              len(individual_stats.get('added_files', {})) +
                                              len(individual_stats.get('deleted_files', {})))
                        
                        # Count total fields detected across all files
                        total_fields_detected = self._count_total_fields_in_results(results)
                        
                        # Enhanced success message with dynamic field insights
                        success_msg = (f"Dynamic folder comparison complete!\n"
                                     f"📁 Files: {total_file_changes} changes across {total_files_analyzed} analyzed\n"
                                     f"📄 Requirements: {total_req_changes} changes detected\n"
                                     f"🔍 Fields: {total_fields_detected} unique fields discovered\n"
                                     f"💡 View 'Individual Files' tab for detailed field analysis")
                        
                        self._show_success(success_msg)
                        self.compare_folders_btn.configure(state=tk.NORMAL, text="🔍 Dynamic Compare")
                        self._update_button_states()
                        
                        # Close progress dialog
                        if self.progress_dialog:
                            self.progress_dialog.complete("Dynamic comparison completed successfully!")
                        
                    except Exception as e:
                        self._show_error("Results Error", f"Failed to display enhanced folder comparison results:\n{str(e)}")
                        self.compare_folders_btn.configure(state=tk.NORMAL, text="🔍 Dynamic Compare")
                        self._update_button_states()
                        
                        if self.progress_dialog:
                            self.progress_dialog.close()
                
                self.root.after_idle(show_enhanced_folder_results)
                
            except Exception as e:
                error_message = str(e)
                def show_error():
                    self._show_error("Enhanced Folder Comparison Failed", f"Enhanced folder comparison failed:\n{error_message}")
                    self.compare_folders_btn.configure(state=tk.NORMAL, text="🔍 Dynamic Compare")
                    self._update_button_states()
                    
                    if self.progress_dialog:
                        self.progress_dialog.close()
                
                self.root.after_idle(show_error)
        
        thread_module.Thread(target=compare_folders_in_thread, daemon=True).start()
    
    def _visualize_file(self):
        """UPDATED Phase 3: Visualize file with dynamic field detection"""
        if not self.visualize_file_path.get():
            self._show_warning("Missing File", "Please select a file to analyze.")
            return
        
        self._show_progress("Initializing dynamic field analysis...")
        self.visualize_btn.configure(state=tk.DISABLED, text="Analyzing...", bg='yellow')
        self.root.update()
        
        def visualize_in_thread():
            try:
                self.root.after_idle(lambda: self._show_progress("Parsing ReqIF file with dynamic field detection..."))
                requirements = self.parser.parse_file(self.visualize_file_path.get())
                
                def show_visualizer():
                    try:
                        self.visualizer_window = VisualizerGUI(
                            self.root, 
                            requirements, 
                            self.visualize_file_path.get()
                        )
                        
                        # UPDATED Phase 3: Dynamic field counting
                        req_count = len(requirements)
                        field_count = self._count_available_fields(requirements)
                        
                        self._show_success(f"Dynamic analysis complete - {req_count} requirements with {field_count} detected fields")
                        self.visualize_btn.configure(state=tk.NORMAL, text="📊 Analyze Fields")
                        self._update_button_states()
                    except Exception as e:
                        self._show_error("Analysis Error", f"Failed to display analysis:\n{str(e)}")
                        self.visualize_btn.configure(state=tk.NORMAL, text="📊 Analyze Fields")
                        self._update_button_states()
                
                self.root.after_idle(show_visualizer)
                
            except Exception as e:
                error_message = str(e)
                def show_error():
                    self._show_error("Analysis Failed", f"File analysis failed:\n{error_message}")
                    self.visualize_btn.configure(state=tk.NORMAL, text="📊 Analyze Fields")
                    self._update_button_states()
                
                self.root.after_idle(show_error)
        
        thread_module.Thread(target=visualize_in_thread, daemon=True).start()
    
    def _count_dynamic_changes(self, stats: Dict[str, Any]) -> int:
        """
        NEW Phase 3: Count changes dynamically without hardcoded field assumptions
        """
        try:
            total_changes = 0
            
            # Look for standard change count fields
            standard_change_fields = ['added_count', 'deleted_count', 'modified_count']
            for field in standard_change_fields:
                if field in stats:
                    try:
                        total_changes += int(stats[field])
                    except (ValueError, TypeError):
                        continue
            
            # If no standard fields found, look for alternative patterns
            if total_changes == 0:
                change_patterns = ['total_changes', 'changes_detected', 'modifications']
                for pattern in change_patterns:
                    if pattern in stats:
                        try:
                            total_changes += int(stats[pattern])
                        except (ValueError, TypeError):
                            continue
            
            # Last resort: count any field with 'count' in name (except unchanged)
            if total_changes == 0:
                for key, value in stats.items():
                    if 'count' in key.lower() and 'unchanged' not in key.lower():
                        try:
                            total_changes += int(value)
                        except (ValueError, TypeError):
                            continue
            
            return total_changes
            
        except Exception as e:
            print(f"Error counting dynamic changes: {e}")
            return 0
    
    def _count_available_fields(self, requirements: List[Dict[str, Any]]) -> int:
        """
        NEW Phase 3: Count available fields dynamically
        """
        try:
            all_fields = set()
            
            for req in requirements:
                if isinstance(req, dict):
                    # Add main fields (excluding internal ones)
                    for field_name in req.keys():
                        if not field_name.startswith('_') and field_name not in ['content', 'raw_attributes']:
                            all_fields.add(field_name)
                    
                    # Add attribute fields
                    attributes = req.get('attributes', {})
                    if isinstance(attributes, dict):
                        for attr_name in attributes.keys():
                            all_fields.add(f'attr_{attr_name}')
            
            return len(all_fields)
            
        except Exception as e:
            print(f"Error counting available fields: {e}")
            return 0
    
    def _count_total_fields_in_results(self, results: Dict[str, Any]) -> int:
        """
        NEW Phase 3: Count total unique fields discovered in comparison results
        """
        try:
            all_fields = set()
            
            # Check individual file statistics for field diversity
            individual_stats = results.get('individual_file_statistics', {})
            
            for category in ['matched_files', 'added_files', 'deleted_files']:
                files_data = individual_stats.get(category, {})
                for file_data in files_data.values():
                    # Extract fields from comparison stats
                    stats = file_data.get('comparison_stats', {})
                    if isinstance(stats, dict):
                        all_fields.update(stats.keys())
                    
                    # Extract fields from file info
                    for info_key in ['file1_info', 'file2_info', 'file_info']:
                        info = file_data.get(info_key, {})
                        if isinstance(info, dict):
                            all_fields.update(info.keys())
            
            # Filter out internal/meta fields
            meaningful_fields = {f for f in all_fields 
                               if not f.startswith('_') and f not in ['full_path', 'relative_path']}
            
            return len(meaningful_fields)
            
        except Exception as e:
            print(f"Error counting total fields: {e}")
            return 0
    
    def _show_comparison_cancelled(self):
        """Handle cancelled comparison"""
        self._show_progress("Dynamic comparison cancelled by user")
        self.compare_folders_btn.configure(state=tk.NORMAL, text="🔍 Dynamic Compare")
        self._update_button_states()
        
        if self.progress_dialog:
            self.progress_dialog.close()
    
    def _show_progress(self, message):
        """Show progress message"""
        self.status_label.configure(text=message, fg='blue')
    
    def _show_success(self, message):
        """Show success message"""
        self.status_label.configure(text=message, fg='darkgreen')
    
    def _show_error(self, title, message):
        """Show error"""
        self.status_label.configure(text="Error occurred - Check details", fg='red')
        messagebox.showerror(title, message)
    
    def _show_warning(self, title, message):
        """Show warning"""
        self.status_label.configure(text="Warning - Check requirements", fg='orange')
        messagebox.showwarning(title, message)
    
    def run(self):
        """Run the application"""
        try:
            self._show_success("Beyond ReqIF Enhanced (Phase 3) ready - Dynamic field detection and comparison available")
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
            if self.folder_comparison_window:
                try:
                    self.folder_comparison_window.window.destroy()
                except:
                    pass
            if self.progress_dialog:
                try:
                    self.progress_dialog.close()
                except:
                    pass
        except:
            pass


def main():
    """Main function"""
    try:
        print("Starting Beyond ReqIF v1.3.0 - Enhanced Edition (Phase 3) with Dynamic Field Support...")
        app = ReqIFToolNative()
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
                f"Failed to start Beyond ReqIF Enhanced (Phase 3):\n\n{str(e)}"
            )
            root.destroy()
        except Exception:
            print("Failed to show error dialog - check console output")


if __name__ == "__main__":
    main()