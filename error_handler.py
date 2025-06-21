#!/usr/bin/env python3
"""
Error Handler Module
Provides enhanced error handling, logging, and recovery mechanisms for the ReqIF Tool Suite.
"""

import sys
import traceback
import logging
import os
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import messagebox
from typing import Any, Callable, Optional


class ErrorHandler:
    """Enhanced error handler with logging and recovery capabilities"""
    
    def __init__(self, app_name="ReqIF Tool Suite", log_dir=None):
        self.app_name = app_name
        self.log_dir = log_dir or Path.home() / ".reqif_tool" / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self.setup_logging()
        
        # Error statistics
        self.error_count = 0
        self.warning_count = 0
        
    def setup_logging(self):
        """Setup comprehensive logging system"""
        log_filename = self.log_dir / f"reqif_tool_{datetime.now().strftime('%Y%m%d')}.log"
        
        # Configure logging format
        log_format = '%(asctime)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s'
        
        # Setup file handler
        file_handler = logging.FileHandler(log_filename, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(log_format))
        
        # Setup console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        
        # Configure root logger
        self.logger = logging.getLogger(self.app_name)
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        self.logger.info(f"=== {self.app_name} Session Started ===")
        self.logger.info(f"Python version: {sys.version}")
        self.logger.info(f"Platform: {sys.platform}")
        
    def handle_exception(self, exc_type, exc_value, exc_traceback):
        """Global exception handler"""
        if issubclass(exc_type, KeyboardInterrupt):
            # Handle Ctrl+C gracefully
            self.logger.info("Application interrupted by user")
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        # Log the exception
        error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        self.logger.error(f"Unhandled exception:\n{error_msg}")
        self.error_count += 1
        
        # Show user-friendly error dialog
        try:
            self.show_error_dialog(exc_type.__name__, str(exc_value), error_msg)
        except:
            # Fallback if GUI is not available
            print(f"FATAL ERROR: {exc_type.__name__}: {exc_value}")
            print("Check logs for details.")
    
    def show_error_dialog(self, error_type: str, error_message: str, full_traceback: str):
        """Show user-friendly error dialog"""
        try:
            # Create temporary root if none exists
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            
            user_message = f"""An unexpected error occurred:

Error Type: {error_type}
Message: {error_message}

The application will continue running, but some features may not work correctly.

Technical details have been logged to:
{self.log_dir}

Would you like to:
• Continue using the application
• View technical details
• Exit the application"""
            
            # Show error dialog with options
            result = messagebox.askyesnocancel(
                "Application Error",
                user_message,
                icon=messagebox.ERROR
            )
            
            if result is True:  # Continue
                pass
            elif result is False:  # View details
                self.show_technical_details(full_traceback)
            else:  # Exit
                sys.exit(1)
                
            root.destroy()
            
        except Exception as e:
            # Ultimate fallback
            print(f"Error showing error dialog: {e}")
            print(f"Original error: {error_type}: {error_message}")
    
    def show_technical_details(self, traceback_text: str):
        """Show technical error details in a separate window"""
        try:
            detail_window = tk.Toplevel()
            detail_window.title("Technical Error Details")
            detail_window.geometry("800x600")
            
            # Create text widget with scrollbar
            frame = tk.Frame(detail_window)
            frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            text_widget = tk.Text(frame, wrap=tk.WORD, font=('Consolas', 10))
            scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)
            
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Insert traceback
            text_widget.insert(tk.END, f"=== Error Details for {self.app_name} ===\n\n")
            text_widget.insert(tk.END, traceback_text)
            text_widget.insert(tk.END, f"\n\n=== System Information ===\n")
            text_widget.insert(tk.END, f"Python: {sys.version}\n")
            text_widget.insert(tk.END, f"Platform: {sys.platform}\n")
            text_widget.insert(tk.END, f"Error Count: {self.error_count}\n")
            
            text_widget.configure(state=tk.DISABLED)
            
            # Copy button
            def copy_to_clipboard():
                detail_window.clipboard_clear()
                detail_window.clipboard_append(text_widget.get(1.0, tk.END))
                messagebox.showinfo("Copied", "Error details copied to clipboard")
            
            copy_btn = tk.Button(detail_window, text="Copy to Clipboard", command=copy_to_clipboard)
            copy_btn.pack(pady=5)
            
        except Exception as e:
            print(f"Failed to show technical details: {e}")
    
    def safe_execute(self, func: Callable, *args, default_return=None, error_message="Operation failed", **kwargs):
        """Safely execute a function with error handling"""
        try:
            return func(*args, **kwargs)
        except Exception as e:
            self.logger.error(f"{error_message}: {str(e)}")
            self.logger.debug(f"Full traceback: {traceback.format_exc()}")
            self.error_count += 1
            
            # Show user-friendly error message
            try:
                messagebox.showerror("Error", f"{error_message}:\n{str(e)}")
            except:
                print(f"ERROR: {error_message}: {str(e)}")
            
            return default_return
    
    def log_warning(self, message: str, show_dialog=False):
        """Log a warning message"""
        self.logger.warning(message)
        self.warning_count += 1
        
        if show_dialog:
            try:
                messagebox.showwarning("Warning", message)
            except:
                print(f"WARNING: {message}")
    
    def log_info(self, message: str):
        """Log an info message"""
        self.logger.info(message)
    
    def log_debug(self, message: str):
        """Log a debug message"""
        self.logger.debug(message)
    
    def get_stats(self) -> dict:
        """Get error handling statistics"""
        return {
            'errors': self.error_count,
            'warnings': self.warning_count,
            'log_dir': str(self.log_dir)
        }
    
    def create_error_report(self) -> str:
        """Create a comprehensive error report"""
        report = f"""
=== {self.app_name} Error Report ===
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

System Information:
- Python: {sys.version}
- Platform: {sys.platform}
- Working Directory: {os.getcwd()}

Session Statistics:
- Errors: {self.error_count}
- Warnings: {self.warning_count}

Log Files Location: {self.log_dir}

Recent Log Entries:
"""
        
        # Add recent log entries if available
        try:
            log_files = sorted(self.log_dir.glob("*.log"), key=os.path.getmtime, reverse=True)
            if log_files:
                with open(log_files[0], 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    report += ''.join(lines[-20:])  # Last 20 lines
        except Exception as e:
            report += f"Could not read log file: {e}"
        
        return report


def install_global_error_handler(app_name="ReqIF Tool Suite"):
    """Install global error handler for the application"""
    error_handler = ErrorHandler(app_name)
    
    # Install as global exception handler
    sys.excepthook = error_handler.handle_exception
    
    return error_handler


# Decorator for safe function execution
def safe_operation(error_message="Operation failed", default_return=None, show_error=True):
    """Decorator to safely execute functions with error handling"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(f"ERROR in {func.__name__}: {error_message}: {str(e)}")
                if show_error:
                    try:
                        messagebox.showerror("Error", f"{error_message}:\n{str(e)}")
                    except:
                        pass
                return default_return
        return wrapper
    return decorator


# Context manager for safe operations
class SafeOperation:
    """Context manager for safe operations with automatic error handling"""
    
    def __init__(self, operation_name: str, error_handler: Optional[ErrorHandler] = None):
        self.operation_name = operation_name
        self.error_handler = error_handler
        
    def __enter__(self):
        if self.error_handler:
            self.error_handler.log_debug(f"Starting operation: {self.operation_name}")
        return self
        
    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            error_msg = f"Error in {self.operation_name}: {str(exc_value)}"
            if self.error_handler:
                self.error_handler.logger.error(error_msg)
                self.error_handler.error_count += 1
            else:
                print(f"ERROR: {error_msg}")
            
            # Show user-friendly error
            try:
                messagebox.showerror("Operation Failed", error_msg)
            except:
                pass
            
            return True  # Suppress the exception
        
        if self.error_handler:
            self.error_handler.log_debug(f"Completed operation: {self.operation_name}")


if __name__ == "__main__":
    # Test the error handler
    print("Testing Error Handler...")
    
    # Install global handler
    error_handler = install_global_error_handler("Test Application")
    
    # Test safe execution
    @safe_operation("Test function failed")
    def test_function():
        raise ValueError("This is a test error")
    
    # Test the function
    result = test_function()
    print(f"Function returned: {result}")
    
    # Test context manager
    with SafeOperation("Test operation", error_handler):
        print("This operation will succeed")
    
    with SafeOperation("Test failing operation", error_handler):
        raise RuntimeError("This operation will fail")
    
    # Show statistics
    stats = error_handler.get_stats()
    print(f"Error handling stats: {stats}")
    
    print("Error handler test completed!")