#!/usr/bin/env python3
"""
Progress Dialog Module
Lightweight progress dialog for long-running operations
"""

import tkinter as tk
from tkinter import ttk
import threading as thread_module  # FIXED: Renamed to avoid circular import
from typing import Optional, Callable


class ProgressDialog:
    """
    Non-blocking progress dialog for long-running operations
    """
    
    def __init__(self, parent: tk.Widget, title: str = "Processing", 
                 message: str = "Please wait...", cancelable: bool = True):
        self.parent = parent
        self.title = title
        self.message = message
        self.cancelable = cancelable
        
        # State tracking
        self.cancelled = False
        self.completed = False
        self.current_progress = 0
        self.max_progress = 100
        
        # Create dialog
        self.dialog = None
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar(value=message)
        
        # Callbacks
        self.cancel_callback = None
        
    def show(self):
        """Show the progress dialog"""
        try:
            if self.dialog is not None:
                return
            
            # Create dialog window
            self.dialog = tk.Toplevel(self.parent)
            self.dialog.title(self.title)
            self.dialog.geometry("450x180")
            self.dialog.resizable(False, False)
            
            # Center the dialog
            self.dialog.transient(self.parent)
            self.dialog.grab_set()
            
            # Center on parent
            self.dialog.update_idletasks()
            x = (self.dialog.winfo_screenwidth() // 2) - (450 // 2)
            y = (self.dialog.winfo_screenheight() // 2) - (180 // 2)
            self.dialog.geometry(f"450x180+{x}+{y}")
            
            # Create UI
            self._create_progress_ui()
            
            # Handle window close
            self.dialog.protocol("WM_DELETE_WINDOW", self._on_window_close)
            
        except Exception as e:
            print(f"Error showing progress dialog: {e}")
    
    def _create_progress_ui(self):
        """Create the progress dialog UI"""
        main_frame = tk.Frame(self.dialog, padx=30, pady=25)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(main_frame, text=self.title, 
                              font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 15))
        
        # Status message
        self.status_label = tk.Label(main_frame, textvariable=self.status_var,
                                    font=('Arial', 11), wraplength=350)
        self.status_label.pack(pady=(0, 20))
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(main_frame, 
                                           variable=self.progress_var,
                                           maximum=100,
                                           length=350,
                                           mode='determinate')
        self.progress_bar.pack(pady=(0, 20))
        
        # Buttons frame
        if self.cancelable:
            buttons_frame = tk.Frame(main_frame)
            buttons_frame.pack()
            
            self.cancel_btn = tk.Button(buttons_frame, text="Cancel", 
                                       command=self._on_cancel,
                                       font=('Arial', 11), relief='raised', bd=2,
                                       padx=20, pady=6, cursor='hand2')
            self.cancel_btn.pack()
    
    def update_progress(self, current: int, maximum: int = None, 
                       status: str = None):
        """
        Update progress safely from any thread
        
        Args:
            current: Current progress value
            maximum: Maximum progress value (optional)
            status: Status message (optional)
        """
        if self.dialog is None or self.completed:
            return
        
        try:
            def _update():
                if self.dialog is None:
                    return
                
                # Update maximum if provided
                if maximum is not None:
                    self.max_progress = maximum
                    self.progress_bar.configure(maximum=maximum)
                
                # Update current progress
                self.current_progress = current
                progress_percentage = (current / max(self.max_progress, 1)) * 100
                self.progress_var.set(progress_percentage)
                
                # Update status if provided
                if status is not None:
                    self.status_var.set(status)
                
                # Update display
                self.dialog.update_idletasks()
            
            # Schedule update on main thread
            if thread_module.current_thread() == thread_module.main_thread():
                _update()
            else:
                self.dialog.after_idle(_update)
                
        except Exception as e:
            print(f"Error updating progress: {e}")
    
    def set_indeterminate(self, active: bool = True):
        """Set progress bar to indeterminate mode"""
        try:
            if self.dialog is None:
                return
            
            def _set_mode():
                if self.dialog is None:
                    return
                
                if active:
                    self.progress_bar.configure(mode='indeterminate')
                    self.progress_bar.start(10)  # Animation speed
                else:
                    self.progress_bar.stop()
                    self.progress_bar.configure(mode='determinate')
            
            if thread_module.current_thread() == thread_module.main_thread():
                _set_mode()
            else:
                self.dialog.after_idle(_set_mode)
                
        except Exception as e:
            print(f"Error setting indeterminate mode: {e}")
    
    def complete(self, success_message: str = None):
        """Mark operation as completed"""
        try:
            self.completed = True
            
            if success_message and self.dialog is not None:
                def _complete():
                    if self.dialog is None:
                        return
                    
                    self.status_var.set(success_message)
                    self.progress_var.set(100)
                    
                    if self.cancelable:
                        self.cancel_btn.configure(text="Close")
                    
                    # Auto-close after 1 second
                    self.dialog.after(1000, self.close)
                
                if thread_module.current_thread() == thread_module.main_thread():
                    _complete()
                else:
                    self.dialog.after_idle(_complete)
            else:
                self.close()
                
        except Exception as e:
            print(f"Error completing progress dialog: {e}")
    
    def close(self):
        """Close the progress dialog"""
        try:
            if self.dialog is not None:
                def _close():
                    try:
                        if self.dialog is not None:
                            self.dialog.grab_release()
                            self.dialog.destroy()
                            self.dialog = None
                    except:
                        pass
                
                if thread_module.current_thread() == thread_module.main_thread():
                    _close()
                else:
                    self.dialog.after_idle(_close)
                    
        except Exception as e:
            print(f"Error closing progress dialog: {e}")
    
    def set_cancel_callback(self, callback: Callable):
        """Set callback function for cancel button"""
        self.cancel_callback = callback
    
    def _on_cancel(self):
        """Handle cancel button click"""
        self.cancelled = True
        
        if self.cancel_callback:
            try:
                self.cancel_callback()
            except Exception as e:
                print(f"Error in cancel callback: {e}")
        
        self.close()
    
    def _on_window_close(self):
        """Handle window close button"""
        if self.cancelable:
            self._on_cancel()
        else:
            # Don't allow closing if not cancelable
            pass
    
    def is_cancelled(self) -> bool:
        """Check if operation was cancelled"""
        return self.cancelled
    
    def is_completed(self) -> bool:
        """Check if operation was completed"""
        return self.completed


class ProgressManager:
    """
    Context manager for progress dialogs
    """
    
    def __init__(self, parent: tk.Widget, title: str = "Processing",
                 message: str = "Please wait...", cancelable: bool = True):
        self.progress_dialog = ProgressDialog(parent, title, message, cancelable)
        
    def __enter__(self):
        self.progress_dialog.show()
        return self.progress_dialog
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.progress_dialog.complete("Operation completed successfully")
        else:
            self.progress_dialog.close()


# Example usage and testing
if __name__ == "__main__":
    import time
    
    def test_progress_dialog():
        """Test the progress dialog"""
        root = tk.Tk()
        root.title("Progress Dialog Test")
        root.geometry("300x200")
        
        def run_test():
            # Test with context manager
            with ProgressManager(root, "Test Operation", "Testing progress dialog...") as progress:
                for i in range(11):
                    if progress.is_cancelled():
                        print("Operation cancelled")
                        break
                    
                    progress.update_progress(i, 10, f"Step {i} of 10")
                    time.sleep(0.5)
        
        def run_indeterminate_test():
            # Test indeterminate mode
            progress = ProgressDialog(root, "Processing", "Analyzing data...", True)
            progress.show()
            progress.set_indeterminate(True)
            
            def finish_after_delay():
                progress.set_indeterminate(False)
                progress.complete("Analysis complete!")
            
            root.after(3000, finish_after_delay)
        
        # Test buttons
        tk.Button(root, text="Test Determinate Progress", 
                 command=lambda: thread_module.Thread(target=run_test, daemon=True).start(),
                 padx=10, pady=5).pack(pady=10)
        
        tk.Button(root, text="Test Indeterminate Progress", 
                 command=run_indeterminate_test,
                 padx=10, pady=5).pack(pady=10)
        
        tk.Button(root, text="Exit", command=root.quit,
                 padx=10, pady=5).pack(pady=10)
        
        root.mainloop()
    
    print("Testing Progress Dialog...")
    test_progress_dialog()
    print("Progress dialog test completed!")