#!/usr/bin/env python3
"""
ReqIF Tool Suite - Main Entry Point
===================================

A comprehensive tool suite for ReqIF (Requirements Interchange Format) files
providing comparison, visualization, and analysis capabilities.

Features:
- ReqIF file comparison with side-by-side diff view
- Excel-like visualization of requirements
- Statistical analysis and reporting
- Multiple export formats (CSV, Excel, PDF, JSON)
- Extensible plugin architecture

Author: ReqIF Tool Suite Team
Version: 2.0.0
License: MIT
"""

import sys
import os
import traceback
import tkinter as tk
from tkinter import messagebox
from pathlib import Path

# Add the project root to Python path
PROJECT_ROOT = Path(__file__).parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

# Import application modules
try:
    from gui.main_menu import MainMenuGUI
    from utils.config import ConfigManager
    from utils.logger import setup_logging, get_logger
    from utils.constants import APP_CONFIG
    from utils.helpers import check_dependencies, setup_environment
except ImportError as e:
    # Handle missing dependencies gracefully
    print(f"Error importing modules: {e}")
    print("Please ensure all required dependencies are installed.")
    print("Run: pip install -r requirements.txt")
    sys.exit(1)


class ReqIFToolSuite:
    """Main application class for the ReqIF Tool Suite"""
    
    def __init__(self):
        """Initialize the application"""
        self.logger = None
        self.config = None
        self.root = None
        self.main_gui = None
        
        # Setup application environment
        self._setup_application()
    
    def _setup_application(self):
        """Setup the application environment"""
        try:
            # Setup logging first
            setup_logging()
            self.logger = get_logger(__name__)
            self.logger.info("Starting ReqIF Tool Suite v%s", APP_CONFIG.VERSION)
            
            # Check dependencies
            missing_deps = check_dependencies()
            if missing_deps:
                self._handle_missing_dependencies(missing_deps)
            
            # Setup environment
            setup_environment()
            
            # Load configuration
            self.config = ConfigManager()
            self.logger.info("Configuration loaded successfully")
            
            # Setup GUI
            self._setup_gui()
            
        except Exception as e:
            self._handle_startup_error(e)
    
    def _setup_gui(self):
        """Setup the main GUI"""
        try:
            # Create root window
            self.root = tk.Tk()
            
            # Configure root window
            self._configure_root_window()
            
            # Create main menu GUI
            self.main_gui = MainMenuGUI(self.root, self.config)
            
            # Setup global exception handler
            self._setup_exception_handler()
            
            self.logger.info("GUI initialized successfully")
            
        except Exception as e:
            self.logger.error("Failed to setup GUI: %s", str(e))
            raise
    
    def _configure_root_window(self):
        """Configure the root window properties"""
        # Set window properties
        self.root.title(f"{APP_CONFIG.APP_NAME} v{APP_CONFIG.VERSION}")
        
        # Set window size and position
        window_config = self.config.get_window_config()
        width = window_config.get('width', APP_CONFIG.DEFAULT_WINDOW_WIDTH)
        height = window_config.get('height', APP_CONFIG.DEFAULT_WINDOW_HEIGHT)
        
        # Center window on screen
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
        # Set minimum window size
        self.root.minsize(APP_CONFIG.MIN_WINDOW_WIDTH, APP_CONFIG.MIN_WINDOW_HEIGHT)
        
        # Set window icon if available
        icon_path = PROJECT_ROOT / "resources" / "icons" / "app_icon.ico"
        if icon_path.exists():
            try:
                self.root.iconbitmap(str(icon_path))
            except Exception as e:
                self.logger.warning("Could not set window icon: %s", str(e))
        
        # Configure window close behavior
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Apply theme if configured
        theme = self.config.get_theme()
        if theme != 'default':
            self._apply_theme(theme)
    
    def _apply_theme(self, theme_name):
        """Apply a theme to the application"""
        try:
            from gui.themes import ThemeManager
            theme_manager = ThemeManager()
            theme_manager.apply_theme(self.root, theme_name)
            self.logger.info("Applied theme: %s", theme_name)
        except Exception as e:
            self.logger.warning("Could not apply theme '%s': %s", theme_name, str(e))
    
    def _setup_exception_handler(self):
        """Setup global exception handler for GUI"""
        def handle_exception(exc_type, exc_value, exc_traceback):
            """Handle uncaught exceptions"""
            if issubclass(exc_type, KeyboardInterrupt):
                # Handle Ctrl+C gracefully
                self.logger.info("Application interrupted by user")
                self.shutdown()
                return
            
            # Log the exception
            error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            self.logger.error("Uncaught exception: %s", error_msg)
            
            # Show error dialog to user
            if self.root and self.root.winfo_exists():
                messagebox.showerror(
                    "Unexpected Error",
                    f"An unexpected error occurred:\n\n{exc_value}\n\n"
                    f"Please check the log file for details.\n"
                    f"Log location: {self.config.get_log_file_path() if self.config else 'logs/'}"
                )
        
        # Set the exception handler
        sys.excepthook = handle_exception
    
    def _handle_missing_dependencies(self, missing_deps):
        """Handle missing dependencies"""
        deps_str = ", ".join(missing_deps)
        error_msg = (
            f"Missing required dependencies: {deps_str}\n\n"
            f"Please install them using:\n"
            f"pip install {' '.join(missing_deps)}\n\n"
            f"Or install all dependencies with:\n"
            f"pip install -r requirements.txt"
        )
        
        print(error_msg)
        
        # Try to show GUI error if possible
        try:
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            messagebox.showerror("Missing Dependencies", error_msg)
            root.destroy()
        except:
            pass  # If GUI fails, error message was already printed
        
        sys.exit(1)
    
    def _handle_startup_error(self, error):
        """Handle startup errors"""
        error_msg = f"Failed to start application: {str(error)}"
        print(error_msg)
        print("\nFull traceback:")
        traceback.print_exc()
        
        # Try to show GUI error if possible
        try:
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            messagebox.showerror("Startup Error", error_msg)
            root.destroy()
        except:
            pass  # If GUI fails, error message was already printed
        
        sys.exit(1)
    
    def _on_closing(self):
        """Handle application closing"""
        try:
            self.logger.info("Application closing...")
            
            # Save window state
            if self.root:
                self.config.save_window_state(
                    width=self.root.winfo_width(),
                    height=self.root.winfo_height(),
                    x=self.root.winfo_x(),
                    y=self.root.winfo_y()
                )
            
            # Save configuration
            self.config.save()
            
            # Close application
            self.shutdown()
            
        except Exception as e:
            self.logger.error("Error during shutdown: %s", str(e))
            self.root.destroy()
    
    def run(self):
        """Run the application"""
        try:
            self.logger.info("Starting application main loop")
            
            # Start the GUI main loop
            self.root.mainloop()
            
        except Exception as e:
            self.logger.error("Error in main loop: %s", str(e))
            raise
        finally:
            self.logger.info("Application main loop ended")
    
    def shutdown(self):
        """Shutdown the application gracefully"""
        try:
            # Cleanup resources
            if self.main_gui:
                self.main_gui.cleanup()
            
            # Destroy GUI
            if self.root:
                self.root.quit()
                self.root.destroy()
            
            self.logger.info("Application shutdown complete")
            
        except Exception as e:
            self.logger.error("Error during shutdown: %s", str(e))


def check_python_version():
    """Check if Python version is supported"""
    min_version = (3, 8)
    current_version = sys.version_info[:2]
    
    if current_version < min_version:
        print(f"Error: Python {'.'.join(map(str, min_version))}+ is required.")
        print(f"Current version: {'.'.join(map(str, current_version))}")
        print("Please upgrade Python to continue.")
        sys.exit(1)


def main():
    """Main entry point"""
    try:
        # Check Python version compatibility
        check_python_version()
        
        # Create and run the application
        app = ReqIFToolSuite()
        app.run()
        
    except KeyboardInterrupt:
        print("\nApplication interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()