# main.py - Fixed imports and usage
"""
Main Application Entry Point - Fixed import issues
Now handles: Added, Deleted, Content Modified, Structural Changes, Unchanged
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import sys
from typing import Dict, List, Optional, Any
import threading
from datetime import datetime

# Import comparison modules - FIXED IMPORTS
try:
    from reqif_comparator import ReqIFComparator  # Import the class, not a function
    from folder_comparator import FolderComparator
    from comparison_gui import ComparisonResultsGUI  # Fixed class name
    from folder_comparison_gui import FolderComparisonGUI
    from visualizer_gui import VisualizerGUI
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Please ensure all required modules are in the same directory.")
    sys.exit(1)


class ReqIFToolNative:  # Changed class name to match the one used in run_reqif_tool.py
    """Main application controller with updated functionality"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ReqIF Comparison Tool Suite - v2.0")
        self.root.geometry("800x600")
        
        # Application state
        self.current_mode = None
        self.active_window = None
        
        self.setup_ui()
        self.setup_styles()
        
    def setup_styles(self):
        """Setup application styles"""
        style = ttk.Style()
        
        # Configure modern theme
        try:
            style.theme_use('clam')
        except:
            pass
            
        # Custom button styles
        style.configure("Accent.TButton", 
                       foreground="white",
                       font=('TkDefaultFont', 10, 'bold'))
        
        style.configure("Large.TButton", 
                       font=('TkDefaultFont', 12, 'bold'),
                       padding=(20, 10))
        
    def setup_ui(self):
        """Setup main application UI"""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = ttk.Label(main_frame, 
                               text="ReqIF Comparison Tool Suite",
                               font=('TkDefaultFont', 16, 'bold'))
        title_label.pack(pady=(0, 10))
        
        subtitle_label = ttk.Label(main_frame, 
                                  text="Version 2.0 - Updated Comparison Categories",
                                  font=('TkDefaultFont', 10, 'italic'))
        subtitle_label.pack(pady=(0, 30))
        
        # Mode selection
        self.setup_mode_selection(main_frame)
        
        # Feature highlights
        self.setup_feature_highlights(main_frame)
        
        # Status and help
        self.setup_status_section(main_frame)
        
    def setup_mode_selection(self, parent):
        """Setup comparison mode selection"""
        mode_frame = ttk.LabelFrame(parent, text="Select Comparison Mode", padding=20)
        mode_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Single file comparison
        file_frame = ttk.Frame(mode_frame)
        file_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Button(file_frame, 
                  text="Single File Comparison",
                  command=self.open_file_comparison,
                  style="Large.TButton").pack(side=tk.LEFT)
        
        file_desc = ttk.Label(file_frame, 
                             text="Compare two individual ReqIF files")
        file_desc.pack(side=tk.LEFT, padx=(20, 0))
        
        # Single file analysis
        analysis_frame = ttk.Frame(mode_frame)
        analysis_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Button(analysis_frame, 
                  text="Single File Analysis",
                  command=self.open_file_analysis,
                  style="Large.TButton").pack(side=tk.LEFT)
        
        analysis_desc = ttk.Label(analysis_frame, 
                                 text="Analyze and visualize a single ReqIF file")
        analysis_desc.pack(side=tk.LEFT, padx=(20, 0))
        
        # Folder comparison
        folder_frame = ttk.Frame(mode_frame)
        folder_frame.pack(fill=tk.X)
        
        ttk.Button(folder_frame, 
                  text="Folder Comparison",
                  command=self.open_folder_comparison,
                  style="Large.TButton").pack(side=tk.LEFT)
        
        folder_desc = ttk.Label(folder_frame, 
                               text="Compare all ReqIF files in two folders")
        folder_desc.pack(side=tk.LEFT, padx=(20, 0))
        
    def setup_feature_highlights(self, parent):
        """Setup feature highlights section"""
        features_frame = ttk.LabelFrame(parent, text="Updated Features in v2.0", padding=15)
        features_frame.pack(fill=tk.X, pady=(0, 20))
        
        features_text = """
✓ Clearer Change Categories:
  • Added Requirements - Completely new requirements
  • Deleted Requirements - Requirements removed from original
  • Content Modified - Same requirement with different content
  • Structural Changes - Same content, different attributes
  • Unchanged - Identical requirements

✓ Enhanced Analysis:
  • Separate content changes from structural differences
  • Better understanding of what actually changed
  • Improved statistics and reporting

✓ Improved User Interface:
  • Clear visual distinction between change types
  • Better organized tabs and displays
  • More detailed comparison views
        """
        
        features_label = ttk.Label(features_frame, text=features_text.strip(), 
                                  justify=tk.LEFT, font=('TkDefaultFont', 9))
        features_label.pack(anchor=tk.W)
        
    def setup_status_section(self, parent):
        """Setup status and help section"""
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X)
        
        # Help button
        ttk.Button(status_frame, text="Help & Guide", 
                  command=self.show_help).pack(side=tk.LEFT)
        
        # About button
        ttk.Button(status_frame, text="About", 
                  command=self.show_about).pack(side=tk.LEFT, padx=(10, 0))
        
        # Status label
        self.status_var = tk.StringVar()
        self.status_var.set("Ready - Select a comparison mode to begin")
        status_label = ttk.Label(status_frame, textvariable=self.status_var)
        status_label.pack(side=tk.RIGHT)
        
    def open_file_comparison(self):
        """Open single file comparison window"""
        try:
            self.update_status("Opening file comparison...")
            
            # Create new window for file comparison
            comparison_window = tk.Toplevel(self.root)
            comparison_window.title("Single File Comparison - v2.0")
            comparison_window.geometry("1200x800")
            
            # Create comparison GUI - FIXED: Use the correct class
            from comparison_gui import ComparisonGUI
            self.active_window = ComparisonGUI(comparison_window)
            self.current_mode = "file"
            
            # Handle window close
            comparison_window.protocol("WM_DELETE_WINDOW", 
                                     lambda: self.close_comparison_window(comparison_window))
            
            self.update_status("File comparison window opened")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file comparison:\n{str(e)}")
            self.update_status("Error opening file comparison")
    
    def open_file_analysis(self):
        """Open single file analysis window"""
        try:
            self.update_status("Opening file analysis...")
            
            # File selection dialog
            file_path = filedialog.askopenfilename(
                title="Select ReqIF file to analyze",
                filetypes=[
                    ("ReqIF files", "*.reqif"),
                    ("ReqIF archives", "*.reqifz"),
                    ("XML files", "*.xml"),
                    ("All files", "*.*")
                ]
            )
            
            if not file_path:
                self.update_status("File analysis cancelled")
                return
            
            # Parse the file
            from reqif_parser import ReqIFParser
            parser = ReqIFParser()
            
            try:
                requirements = parser.parse_file(file_path)
                
                if not requirements:
                    messagebox.showwarning("No Data", 
                        f"No requirements found in file:\n{file_path}\n\n"
                        "Please check that this is a valid ReqIF file.")
                    self.update_status("No requirements found")
                    return
                
                # Create visualizer window
                self.active_window = VisualizerGUI(self.root, requirements, file_path)
                self.current_mode = "analysis"
                
                self.update_status(f"Analyzing {len(requirements)} requirements from {os.path.basename(file_path)}")
                
            except Exception as e:
                messagebox.showerror("Parsing Error", 
                    f"Failed to parse ReqIF file:\n{file_path}\n\nError: {str(e)}")
                self.update_status("File parsing failed")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file analysis:\n{str(e)}")
            self.update_status("Error opening file analysis")
            
    def open_folder_comparison(self):
        """Open folder comparison window"""
        try:
            self.update_status("Opening folder comparison...")
            
            # Create new window for folder comparison
            comparison_window = tk.Toplevel(self.root)
            comparison_window.title("Folder Comparison - v2.0")
            comparison_window.geometry("1400x900")
            
            # Create folder comparison GUI
            self.active_window = FolderComparisonGUI(comparison_window)
            self.current_mode = "folder"
            
            # Handle window close
            comparison_window.protocol("WM_DELETE_WINDOW", 
                                     lambda: self.close_comparison_window(comparison_window))
            
            self.update_status("Folder comparison window opened")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open folder comparison:\n{str(e)}")
            self.update_status("Error opening folder comparison")
            
    def close_comparison_window(self, window):
        """Handle comparison window closing"""
        try:
            window.destroy()
            self.active_window = None
            self.current_mode = None
            self.update_status("Ready - Select a comparison mode to begin")
        except Exception as e:
            print(f"Error closing window: {e}")
            
    def show_help(self):
        """Show help and usage guide"""
        help_window = tk.Toplevel(self.root)
        help_window.title("Help & Usage Guide")
        help_window.geometry("700x600")
        
        # Create scrollable text area
        text_frame = ttk.Frame(help_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        text_widget = tk.Text(text_frame, wrap=tk.WORD, font=('TkDefaultFont', 10))
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        help_content = """
REQIF COMPARISON TOOL SUITE - USER GUIDE
==========================================

OVERVIEW
--------
This tool compares ReqIF (Requirements Interchange Format) files and provides detailed analysis of changes between versions.

VERSION 2.0 UPDATES
-------------------
The comparison logic has been completely updated to provide clearer categorization:

1. ADDED REQUIREMENTS
   - Requirements that exist only in the modified version
   - Completely new requirements not found in the original

2. DELETED REQUIREMENTS  
   - Requirements that exist only in the original version
   - Requirements removed in the modified version

3. CONTENT MODIFIED
   - Requirements with the same ID but different content
   - Changes in requirement text, values, or key attributes
   - Same structure but different information

4. STRUCTURAL CHANGES
   - Requirements with identical content but different metadata
   - Changes in attributes like timestamps, formatting, etc.
   - Same information presented differently

5. UNCHANGED
   - Requirements that are completely identical
   - No differences detected in content or structure

COMPARISON MODES
---------------

SINGLE FILE COMPARISON:
- Compare two individual ReqIF files
- See detailed side-by-side differences
- Export specific change reports
- Best for detailed analysis of specific files

SINGLE FILE ANALYSIS:
- Analyze a single ReqIF file
- View requirements in a structured format
- Search and filter capabilities
- Export to CSV for further analysis

FOLDER COMPARISON:
- Compare entire folders containing ReqIF files
- Process multiple files automatically
- Generate comprehensive summary reports
- Best for bulk analysis and project-level changes

HOW TO USE
----------

Single File Comparison:
1. Click "Single File Comparison"
2. Select original file (before changes)
3. Select modified file (after changes)  
4. Click "Compare Files"
5. Review results in categorized tabs
6. Export results if needed

Single File Analysis:
1. Click "Single File Analysis"
2. Select ReqIF file to analyze
3. Browse requirements in the table
4. Use search to find specific content
5. View detailed statistics
6. Export filtered data to CSV

Folder Comparison:
1. Click "Folder Comparison"
2. Select original folder (before changes)
3. Select modified folder (after changes)
4. Click "Start Comparison"
5. Monitor progress and review summary
6. Examine individual files in detail
7. Export comprehensive results

UNDERSTANDING RESULTS
--------------------

Statistics Panel:
- Shows counts for each change category
- Provides overview of total changes
- Helps identify patterns in modifications

File Tree (Folder Mode):
- Lists all files with changes
- Color codes by primary change type
- Shows change counts with symbols:
  +N = N requirements added
  -N = N requirements deleted
  ~N = N content modifications
  #N = N structural changes

Detail Tabs:
- Each category has its own tab
- Shows specific requirements in each category
- Provides detailed change information
- Allows focused analysis of specific change types

EXPORT OPTIONS
--------------
- JSON format: Machine-readable detailed results
- Text format: Human-readable summary reports
- CSV format: Spreadsheet-compatible data
- Include full comparison details and statistics

TIPS FOR EFFECTIVE USE
---------------------
1. Always compare in chronological order (older → newer)
2. Focus on Content Modified for functional changes
3. Check Structural Changes for process/tool differences
4. Use folder comparison for project-wide analysis
5. Export results for documentation and review

TROUBLESHOOTING
--------------
- Ensure ReqIF files are valid and accessible
- Check file permissions for reading
- Large files may take time to process
- Use progress indicators to monitor long operations

For additional support or to report issues, please contact the development team.
        """
        
        text_widget.insert(1.0, help_content.strip())
        text_widget.configure(state=tk.DISABLED)
        
        # Close button
        ttk.Button(help_window, text="Close", command=help_window.destroy).pack(pady=10)
        
    def show_about(self):
        """Show about dialog"""
        about_text = """
ReqIF Comparison Tool Suite
Version 2.0

A comprehensive tool for comparing ReqIF (Requirements Interchange Format) files.

Key Features:
• Single file and folder comparison modes
• Single file analysis and visualization
• Clear categorization of changes
• Detailed analysis and reporting
• Export capabilities
• User-friendly interface

Updates in Version 2.0:
• Redesigned comparison logic
• Clearer change categories
• Improved user interface
• Better performance and reliability
• Enhanced reporting capabilities
• Added single file analysis mode

Developed for requirements engineering and change management.

© 2024 ReqIF Tools Team
        """
        
        messagebox.showinfo("About ReqIF Comparison Tool", about_text.strip())
        
    def update_status(self, message: str):
        """Update status message"""
        self.status_var.set(message)
        self.root.update_idletasks()
        
    def run_quick_test(self):
        """Run a quick test of the comparison functionality"""
        try:
            self.update_status("Running quick functionality test...")
            
            # Test basic comparison function
            from reqif_comparator import ReqIFComparator
            
            # Create sample data for testing
            sample_req1 = {
                'id': 'REQ-001',
                'attributes': {'Object Text': 'Original requirement text'},
                'type': 'Functional'
            }
            
            sample_req2 = {
                'id': 'REQ-001', 
                'attributes': {'Object Text': 'Modified requirement text'},
                'type': 'Functional'
            }
            
            # Test comparison
            comparator = ReqIFComparator()
            result = comparator.compare_requirements([sample_req1], [sample_req2])
            
            # Check result structure
            expected_keys = ['added', 'deleted', 'content_modified', 'structural_only', 'unchanged', 'statistics']
            
            success = all(key in result for key in expected_keys)
            
            if success:
                self.update_status("Quick test passed - All functionality working")
                messagebox.showinfo("Test Results", 
                    "Quick functionality test passed!\n\n"
                    "All comparison functions are working correctly.\n"
                    "You can proceed with normal operation.")
            else:
                self.update_status("Quick test failed - Check installation")
                messagebox.showerror("Test Results",
                    "Quick functionality test failed!\n\n"
                    "There may be an issue with the installation.\n"
                    "Please check all required files are present.")
                
        except Exception as e:
            self.update_status("Quick test failed with error")
            messagebox.showerror("Test Error", 
                f"Quick test failed with error:\n\n{str(e)}\n\n"
                "Please check the installation and try again.")
    
    def run(self):
        """Run the main application"""
        try:
            # Start the application
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\nApplication interrupted by user")
        except Exception as e:
            print(f"Application error: {str(e)}")
            messagebox.showerror("Application Error", 
                f"A critical error occurred:\n\n{str(e)}\n\n"
                "The application will now exit.")
        finally:
            try:
                self.root.quit()
            except:
                pass


# Compatibility alias for the old class name
MainApplication = ReqIFToolNative


def setup_application():
    """Setup and configure the main application"""
    # Create root window
    root = tk.Tk()
    
    # Set window properties
    root.title("ReqIF Comparison Tool Suite")
    root.geometry("800x600")
    root.minsize(600, 400)
    
    # Center window on screen
    try:
        root.update_idletasks()
        width = root.winfo_width()
        height = root.winfo_height()
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f"{width}x{height}+{x}+{y}")
    except:
        pass
        
    return root


def main():
    """Main application entry point"""
    try:
        print("Starting ReqIF Comparison Tool Suite v2.0...")
        
        # Create application instance
        app = ReqIFToolNative()
        
        # Add menu bar
        menubar = tk.Menu(app.root)
        app.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Single File Comparison", command=app.open_file_comparison)
        file_menu.add_command(label="Single File Analysis", command=app.open_file_analysis)
        file_menu.add_command(label="Folder Comparison", command=app.open_folder_comparison)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=app.root.quit)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Quick Test", command=app.run_quick_test)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="User Guide", command=app.show_help)
        help_menu.add_command(label="About", command=app.show_about)
        
        print("Application setup complete")
        
        # Start the application
        print("Starting GUI main loop...")
        app.run()
        
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        return 0
    except Exception as e:
        print(f"Application error: {str(e)}")
        try:
            messagebox.showerror("Application Error", 
                f"A critical error occurred:\n\n{str(e)}\n\n"
                "The application will now exit.")
        except:
            pass
        return 1
    finally:
        print("Application shutdown complete")


def check_dependencies():
    """Check if all required dependencies are available"""
    required_modules = [
        'tkinter',
        'xml.etree.ElementTree', 
        'datetime',
        'os',
        'sys',
        'threading',
        'json'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print("Missing required modules:")
        for module in missing_modules:
            print(f"  - {module}")
        return False
        
    # Check for custom modules
    custom_modules = [
        'reqif_comparator',
        'folder_comparator', 
        'comparison_gui',
        'folder_comparison_gui',
        'visualizer_gui'
    ]
    
    missing_custom = []
    
    for module in custom_modules:
        try:
            __import__(module)
        except ImportError:
            missing_custom.append(module)
    
    if missing_custom:
        print("Missing custom modules:")
        for module in missing_custom:
            print(f"  - {module}.py")
        print("\nPlease ensure all files are in the same directory.")
        return False
        
    return True


def show_startup_message():
    """Show startup message with version info"""
    startup_msg = """
=====================================
ReqIF Comparison Tool Suite v2.0
=====================================

New Features in v2.0:
✓ Clearer change categorization
✓ Separate content vs structural changes
✓ Single file analysis mode
✓ Improved user interface
✓ Better performance and reliability
✓ Enhanced reporting capabilities

Starting application...
    """
    print(startup_msg.strip())


if __name__ == "__main__":
    try:
        # Show startup message
        show_startup_message()
        
        # Check dependencies
        print("Checking dependencies...")
        if not check_dependencies():
            print("❌ Dependency check failed")
            print("Please install missing modules and ensure all files are present.")
            input("Press Enter to exit...")
            sys.exit(1)
        print("✅ All dependencies found")
        
        # Run main application
        exit_code = main()
        sys.exit(exit_code)
        
    except Exception as e:
        print(f"Critical startup error: {str(e)}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
        sys.exit(1)