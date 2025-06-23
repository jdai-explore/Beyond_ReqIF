#!/usr/bin/env python3
"""
ReqIF Tool Suite - Native Launcher
Pure tkinter launcher without theme dependencies
"""

import tkinter as tk
from tkinter import messagebox
import sys
import os


def check_dependencies():
    """Check if all required dependencies are available"""
    missing_modules = []
    
    try:
        import xml.etree.ElementTree as ET
    except ImportError:
        missing_modules.append("xml.etree.ElementTree")
    
    try:
        import csv
    except ImportError:
        missing_modules.append("csv")
    
    try:
        import tempfile
    except ImportError:
        missing_modules.append("tempfile")
    
    try:
        import zipfile
    except ImportError:
        missing_modules.append("zipfile")
    
    return missing_modules


def check_files():
    """Check if all required files are present"""
    required_files = [
        'main.py',
        'reqif_parser.py',
        'reqif_comparator.py',
        'comparison_gui.py',
        'visualizer_gui.py',
        'error_handler.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    return missing_files


def show_startup_dialog():
    """Show startup options dialog"""
    startup_window = tk.Tk()
    startup_window.title("Beyond ReqIF - Startup Options")
    startup_window.geometry("500x400")
    startup_window.resizable(False, False)
    
    # Center the window
    startup_window.update_idletasks()
    x = (startup_window.winfo_screenwidth() // 2) - (500 // 2)
    y = (startup_window.winfo_screenheight() // 2) - (400 // 2)
    startup_window.geometry(f"500x400+{x}+{y}")
    
    choice = {'value': None}
    
    main_frame = tk.Frame(startup_window, padx=30, pady=30)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Title
    title_label = tk.Label(main_frame, text="Beyond ReqIF", 
                          font=('Arial', 20, 'bold'))
    title_label.pack(pady=(0, 10))
    
    subtitle_label = tk.Label(main_frame, text="Native Edition v1.2.0", 
                             font=('Arial', 12))
    subtitle_label.pack(pady=(0, 30))
    
    # Description
    desc_text = """Professional ReqIF file parser, comparison, and visualization tool.

Pure native tkinter interface - no external theme dependencies.

Choose your startup option:"""
    
    desc_label = tk.Label(main_frame, text=desc_text, 
                         font=('Arial', 11), justify=tk.LEFT)
    desc_label.pack(pady=(0, 25))
    
    # Buttons frame
    buttons_frame = tk.Frame(main_frame)
    buttons_frame.pack(fill=tk.X, pady=(10, 0))
    
    def normal_startup():
        choice['value'] = 'normal'
        startup_window.destroy()
    
    def validation_startup():
        choice['value'] = 'validate'
        startup_window.destroy()
    
    def safe_startup():
        choice['value'] = 'safe'
        startup_window.destroy()
    
    def exit_app():
        choice['value'] = 'exit'
        startup_window.destroy()
    
    # Normal startup button
    normal_btn = tk.Button(buttons_frame, text="🚀 Normal Startup", 
                          command=normal_startup,
                          font=('Arial', 12, 'bold'), relief='raised', bd=3,
                          padx=20, pady=8, cursor='hand2', bg='lightgreen')
    normal_btn.pack(fill=tk.X, pady=(0, 10))
    
    # Validation startup button
    validate_btn = tk.Button(buttons_frame, text="🔍 Run Validation First", 
                            command=validation_startup,
                            font=('Arial', 11), relief='raised', bd=2,
                            padx=20, pady=6, cursor='hand2', bg='lightyellow')
    validate_btn.pack(fill=tk.X, pady=(0, 10))
    
    # Safe mode button
    safe_btn = tk.Button(buttons_frame, text="🛡️ Safe Mode", 
                        command=safe_startup,
                        font=('Arial', 11), relief='raised', bd=2,
                        padx=20, pady=6, cursor='hand2', bg='lightcyan')
    safe_btn.pack(fill=tk.X, pady=(0, 15))
    
    # Exit button
    exit_btn = tk.Button(buttons_frame, text="Exit", 
                        command=exit_app,
                        font=('Arial', 11), relief='raised', bd=2,
                        padx=20, pady=6, cursor='hand2')
    exit_btn.pack(fill=tk.X)
    
    # Status label
    status_label = tk.Label(main_frame, text="Ready to start", 
                           font=('Arial', 10))
    status_label.pack(pady=(15, 0))
    
    # Make normal startup the default
    normal_btn.focus_set()
    
    # Handle window close
    def on_closing():
        choice['value'] = 'exit'
        startup_window.destroy()
    
    startup_window.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Handle Enter key
    def on_enter(event):
        normal_startup()
    
    startup_window.bind('<Return>', on_enter)
    
    startup_window.mainloop()
    return choice['value']


def run_validation():
    """Run system validation"""
    print("🔍 Running system validation...")
    
    # Check dependencies
    missing_deps = check_dependencies()
    if missing_deps:
        print(f"❌ Missing dependencies: {', '.join(missing_deps)}")
        return False
    else:
        print("✅ All dependencies available")
    
    # Check files
    missing_files = check_files()
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False
    else:
        print("✅ All required files present")
    
    # Check Python version
    if sys.version_info < (3, 7):
        print(f"❌ Python 3.7+ required, found {sys.version}")
        return False
    else:
        print(f"✅ Python version: {sys.version}")
    
    print("✅ System validation completed successfully")
    return True


def main():
    """Main launcher function"""
    print("Beyond ReqIF - Native Edition")
    print("=" * 40)
    
    # Handle command line arguments
    if len(sys.argv) > 1:
        if '--safe-mode' in sys.argv or '--safe' in sys.argv:
            startup_choice = 'safe'
        elif '--validate' in sys.argv:
            startup_choice = 'validate'
        elif '--help' in sys.argv or '-h' in sys.argv:
            print("Usage: python run_reqif_tool.py [options]")
            print("Options:")
            print("  --safe-mode, --safe   Start in safe mode")
            print("  --validate           Run validation first")
            print("  --help, -h           Show this help")
            return
        else:
            startup_choice = 'normal'
    else:
        # Show startup dialog
        startup_choice = show_startup_dialog()
    
    if startup_choice == 'exit' or startup_choice is None:
        print("Startup cancelled.")
        return
    
    # Run validation if requested
    if startup_choice == 'validate':
        if not run_validation():
            print("❌ Validation failed. Please check your installation.")
            input("Press Enter to exit...")
            return
        print("Proceeding with normal startup...")
        startup_choice = 'normal'
    
    # Import and run the main application
    try:
        if startup_choice == 'safe':
            print("🛡️ Starting in safe mode...")
            # Import with error handling
            from main import ReqIFToolNative
            print("✅ Modules imported successfully")
            
            app = ReqIFToolNative()
            print("✅ Application initialized")
            
            print("🚀 Launching Beyond ReqIF...")
            app.run()
            
        else:  # normal startup
            print("🚀 Starting Beyond ReqIF...")
            from main import ReqIFToolNative
            
            app = ReqIFToolNative()
            app.run()
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Missing required modules. Please check your installation.")
        
        # Show error dialog
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "Import Error",
                f"Failed to import required modules:\n\n{str(e)}\n\n"
                "Please ensure all required files are present in the same directory."
            )
            root.destroy()
        except:
            pass
            
    except Exception as e:
        print(f"❌ Startup error: {e}")
        print("An unexpected error occurred during startup.")
        
        # Show error dialog
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "Startup Error",
                f"An unexpected error occurred:\n\n{str(e)}\n\n"
                "Please try running in safe mode or check the console for details."
            )
            root.destroy()
        except:
            pass
    
    print("Beyond ReqIF session ended.")


if __name__ == "__main__":
    main()