#!/usr/bin/env python3
"""
ReqIF Tool Suite - Native Launcher
Fixed: Removed startup dialog, launches directly
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


def run_validation():
    """Run system validation"""
    print("🔍 Running system validation...")
    
    missing_deps = check_dependencies()
    if missing_deps:
        print(f"❌ Missing dependencies: {', '.join(missing_deps)}")
        return False
    else:
        print("✅ All dependencies available")
    
    missing_files = check_files()
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False
    else:
        print("✅ All required files present")
    
    if sys.version_info < (3, 7):
        print(f"❌ Python 3.7+ required, found {sys.version}")
        return False
    else:
        print(f"✅ Python version: {sys.version}")
    
    print("✅ System validation completed successfully")
    return True


def main():
    """Main launcher function - directly starts application"""
    print("ReqIF Tool Suite - Starting...")
    
    # Handle command line arguments
    if len(sys.argv) > 1:
        if '--validate' in sys.argv:
            if not run_validation():
                print("❌ Validation failed. Please check your installation.")
                input("Press Enter to exit...")
                return
            print("Proceeding with normal startup...")
        elif '--help' in sys.argv or '-h' in sys.argv:
            print("Usage: python run_reqif_tool.py [options]")
            print("Options:")
            print("  --validate           Run validation first")
            print("  --help, -h           Show this help")
            return
    
    # Import and run the main application directly
    try:
        print("🚀 Starting ReqIF Tool Suite...")
        from main import ReqIFToolNative
        
        app = ReqIFToolNative()
        app.run()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Missing required modules. Please check your installation.")
        
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
        
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "Startup Error",
                f"An unexpected error occurred:\n\n{str(e)}\n\n"
                "Please check the console for details."
            )
            root.destroy()
        except:
            pass
    
    print("ReqIF Tool Suite session ended.")


if __name__ == "__main__":
    main()