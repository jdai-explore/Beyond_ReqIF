#!/usr/bin/env python3
"""
Enhanced Launcher for Beyond ReqIF
Provides comprehensive startup validation, error handling, and recovery.
"""

import sys
import os
import traceback
from pathlib import Path
import argparse
import tkinter as tk
from tkinter import messagebox

# Add project directory to Python path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

# Try to import our modules
try:
    from startup_validator import StartupValidator
    from error_handler import install_global_error_handler
    startup_available = True
except ImportError as e:
    print(f"⚠️ Warning: Could not import startup modules: {e}")
    startup_available = False


class ReqIFLauncher:
    """Enhanced launcher with validation and error handling"""
    
    def __init__(self):
        self.validator = None
        self.error_handler = None
        self.args = None
        
    def parse_arguments(self):
        """Parse command line arguments"""
        parser = argparse.ArgumentParser(
            description="ReqIF Tool Suite - Professional Edition",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  python run_reqif_tool.py                    # Normal startup with validation
  python run_reqif_tool.py --no-validation    # Skip validation (faster startup)
  python run_reqif_tool.py --validate-only    # Run validation only
  python run_reqif_tool.py --debug           # Enable debug mode
  python run_reqif_tool.py --safe-mode       # Safe mode with basic GUI only
            """
        )
        
        parser.add_argument('--no-validation', action='store_true',
                          help='Skip startup validation (faster but may miss issues)')
        parser.add_argument('--validate-only', action='store_true',
                          help='Run validation only, do not start application')
        parser.add_argument('--debug', action='store_true',
                          help='Enable debug mode with verbose logging')
        parser.add_argument('--safe-mode', action='store_true',
                          help='Start in safe mode with minimal features')
        parser.add_argument('--version', action='version', version='ReqIF Tool Suite v1.1.0')
        
        self.args = parser.parse_args()
        
    def setup_error_handling(self):
        """Setup global error handling"""
        if startup_available:
            try:
                self.error_handler = install_global_error_handler("ReqIF Tool Suite")
                if self.args.debug:
                    self.error_handler.logger.setLevel('DEBUG')
                print("✅ Error handling initialized")
            except Exception as e:
                print(f"⚠️ Could not setup error handling: {e}")
        else:
            print("⚠️ Using basic error handling")
            sys.excepthook = self.basic_exception_handler
    
    def basic_exception_handler(self, exc_type, exc_value, exc_traceback):
        """Basic fallback exception handler"""
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        error_msg = f"Unhandled exception: {exc_type.__name__}: {exc_value}"
        print(f"❌ {error_msg}")
        
        # Try to show GUI error if possible
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Application Error", error_msg)
            root.destroy()
        except:
            pass
        
        traceback.print_exception(exc_type, exc_value, exc_traceback)
    
    def run_validation(self) -> bool:
        """Run startup validation"""
        if not startup_available:
            print("⚠️ Startup validation not available, proceeding anyway...")
            return True
        
        print("🔍 Running startup validation...")
        try:
            self.validator = StartupValidator()
            success = self.validator.run_full_validation()
            
            if not success:
                print("\n❌ Validation failed!")
                
                # Ask user if they want to continue anyway
                try:
                    root = tk.Tk()
                    root.withdraw()
                    
                    result = messagebox.askyesno(
                        "Validation Failed",
                        "Startup validation found issues that may prevent the application from working correctly.\n\n"
                        "Do you want to continue anyway?\n\n"
                        "Click 'No' to view the detailed validation report.",
                        icon=messagebox.WARNING
                    )
                    
                    root.destroy()
                    
                    if not result:
                        # Show detailed report
                        self.validator.show_gui_report()
                        return False
                    else:
                        print("⚠️ Continuing despite validation issues...")
                        return True
                        
                except Exception as e:
                    print(f"Could not show validation dialog: {e}")
                    return False
            
            return success
            
        except Exception as e:
            print(f"❌ Validation error: {e}")
            return False
    
    def start_application(self):
        """Start the main application"""
        print("🚀 Starting ReqIF Tool Suite...")
        
        try:
            # Import main application
            if self.args.safe_mode:
                # Safe mode - basic functionality only
                self.start_safe_mode()
            else:
                # Normal mode
                from main import ReqIFToolMVP
                app = ReqIFToolMVP()
                
                # Apply debug settings if requested
                if self.args.debug and hasattr(app, 'error_handler'):
                    app.error_handler.logger.setLevel('DEBUG')
                
                app.run()
                
        except ImportError as e:
            print(f"❌ Could not import main application: {e}")
            self.show_import_error_help(e)
            return False
        except Exception as e:
            print(f"❌ Application startup failed: {e}")
            traceback.print_exc()
            
            # Try to show error dialog
            try:
                root = tk.Tk()
                root.withdraw()
                messagebox.showerror(
                    "Startup Error", 
                    f"Failed to start ReqIF Tool Suite:\n\n{str(e)}\n\n"
                    "Check the console for detailed error information."
                )
                root.destroy()
            except:
                pass
            
            return False
        
        return True
    
    def start_safe_mode(self):
        """Start application in safe mode with basic functionality"""
        print("🛡️ Starting in Safe Mode...")
        
        try:
            # Create basic GUI
            root = tk.Tk()
            root.title("ReqIF Tool Suite - Safe Mode")
            root.geometry("600x400")
            
            # Main frame
            main_frame = tk.Frame(root, padx=20, pady=20)
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Title
            title_label = tk.Label(main_frame, text="Beyond ReqIF - Safe Mode", 
                                 font=('Arial', 16, 'bold'))
            title_label.pack(pady=(0, 20))
            
            # Status
            status_text = """Safe Mode is active due to startup issues.
            
Available features:
• Basic file validation
• Simple ReqIF parsing
• Text-based comparison output

Some advanced features may not be available."""
            
            status_label = tk.Label(main_frame, text=status_text, justify=tk.LEFT)
            status_label.pack(pady=(0, 20))
            
            # Buttons
            button_frame = tk.Frame(main_frame)
            button_frame.pack(fill=tk.X)
            
            def try_normal_mode():
                root.destroy()
                self.args.safe_mode = False
                self.start_application()
            
            def run_validation():
                if self.validator:
                    self.validator.show_gui_report()
                else:
                    messagebox.showinfo("Validation", "Validation tools not available")
            
            tk.Button(button_frame, text="Try Normal Mode", 
                     command=try_normal_mode).pack(side=tk.LEFT, padx=5)
            tk.Button(button_frame, text="Run Validation", 
                     command=run_validation).pack(side=tk.LEFT, padx=5)
            tk.Button(button_frame, text="Exit", 
                     command=root.quit).pack(side=tk.RIGHT, padx=5)
            
            root.mainloop()
            
        except Exception as e:
            print(f"❌ Safe mode failed: {e}")
            print("💡 Try running individual modules directly")
    
    def show_import_error_help(self, error):
        """Show helpful information for import errors"""
        help_text = f"""
Import Error: {error}

Possible solutions:
1. Ensure all required files are in the project directory:
   - main.py
   - reqif_parser.py  
   - reqif_comparator.py
   - theme_manager.py

2. Check file permissions and ensure files are readable

3. Verify Python path includes the project directory

4. Run the startup validator:
   python startup_validator.py --gui

5. Try safe mode:
   python run_reqif_tool.py --safe-mode
"""
        
        print(help_text)
        
        # Show GUI help if possible
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Import Error", help_text)
            root.destroy()
        except:
            pass
    
    def run(self):
        """Main launcher execution"""
        print("=" * 60)
        print("🚀 Beyond ReqIF - Professional Edition")
        print("=" * 60)
        
        # Parse command line arguments
        self.parse_arguments()
        
        # Setup error handling
        self.setup_error_handling()
        
        # Validation-only mode
        if self.args.validate_only:
            if startup_available:
                validator = StartupValidator()
                success = validator.run_full_validation()
                validator.show_gui_report()
                return 0 if success else 1
            else:
                print("❌ Validation tools not available")
                return 1
        
        # Run validation unless disabled
        if not self.args.no_validation:
            validation_success = self.run_validation()
            if not validation_success and not self.args.safe_mode:
                print("❌ Startup aborted due to validation failures")
                return 1
        else:
            print("⚠️ Skipping validation (--no-validation flag)")
        
        # Start the application
        success = self.start_application()
        
        if success:
            print("👋 Beyond ReqIF session ended")
            return 0
        else:
            print("❌ Application failed to start")
            return 1


def show_welcome_screen():
    """Show a welcome screen with options"""
    try:
        root = tk.Tk()
        root.title("Beyond ReqIF - Welcome")
        root.geometry("500x400")
        root.resizable(False, False)
        
        # Center the window
        root.update_idletasks()
        x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
        y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
        root.geometry(f"+{x}+{y}")
        
        # Main frame
        main_frame = tk.Frame(root, padx=30, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Logo/Title
        title_label = tk.Label(main_frame, text="⚙️ Beyond ReqIF", 
                             font=('Arial', 20, 'bold'), fg='#2196F3')
        title_label.pack(pady=(0, 5))
        
        subtitle_label = tk.Label(main_frame, text="Professional Edition v1.1.0", 
                                font=('Arial', 12, 'italic'))
        subtitle_label.pack(pady=(0, 20))
        
        # Description
        desc_text = """A comprehensive tool for working with ReqIF 
(Requirements Interchange Format) files.

Features:
• Parse and compare ReqIF files
• Visualize requirements data
• Export analysis results
• Professional themes and UI"""
        
        desc_label = tk.Label(main_frame, text=desc_text, 
                            justify=tk.CENTER, font=('Arial', 10))
        desc_label.pack(pady=(0, 30))
        
        # Options frame
        options_frame = tk.Frame(main_frame)
        options_frame.pack(fill=tk.X, pady=(0, 20))
        
        selected_option = tk.StringVar(value="normal")
        
        tk.Radiobutton(options_frame, text="Normal startup (recommended)", 
                      variable=selected_option, value="normal").pack(anchor=tk.W)
        tk.Radiobutton(options_frame, text="Run validation first", 
                      variable=selected_option, value="validate").pack(anchor=tk.W)
        tk.Radiobutton(options_frame, text="Safe mode (basic features only)", 
                      variable=selected_option, value="safe").pack(anchor=tk.W)
        tk.Radiobutton(options_frame, text="Skip validation (faster startup)", 
                      variable=selected_option, value="no-validation").pack(anchor=tk.W)
        
        # Buttons frame
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        def start_selected():
            option = selected_option.get()
            root.destroy()
            
            # Build command line arguments based on selection
            args = []
            if option == "validate":
                args.append("--validate-only")
            elif option == "safe":
                args.append("--safe-mode")
            elif option == "no-validation":
                args.append("--no-validation")
            
            # Update sys.argv and run launcher
            sys.argv = [sys.argv[0]] + args
            launcher = ReqIFLauncher()
            launcher.run()
        
        def exit_app():
            root.destroy()
            sys.exit(0)
        
        start_btn = tk.Button(button_frame, text="Start Application", 
                            command=start_selected, bg='#2196F3', fg='white',
                            font=('Arial', 11, 'bold'), padx=20)
        start_btn.pack(side=tk.LEFT)
        
        exit_btn = tk.Button(button_frame, text="Exit", command=exit_app)
        exit_btn.pack(side=tk.RIGHT)
        
        # Status bar
        status_frame = tk.Frame(root)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        status_label = tk.Label(status_frame, text="Ready to start", 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_label.pack(fill=tk.X, padx=5, pady=2)
        
        root.mainloop()
        
    except Exception as e:
        print(f"Could not show welcome screen: {e}")
        # Fallback to direct launch
        launcher = ReqIFLauncher()
        return launcher.run()


def quick_system_check():
    """Perform a quick system compatibility check"""
    print("🔍 Quick system check...")
    
    issues = []
    
    # Check Python version
    if sys.version_info < (3, 7):
        issues.append("Python 3.7+ required")
    
    # Check tkinter
    try:
        import tkinter
        # Test basic window creation
        root = tkinter.Tk()
        root.withdraw()
        root.destroy()
    except ImportError:
        issues.append("tkinter not available")
    except Exception as e:
        issues.append(f"GUI issues detected: {e}")
    
    # Check required files
    required_files = ['main.py', 'reqif_parser.py', 'reqif_comparator.py']
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        issues.append(f"Missing files: {', '.join(missing_files)}")
    
    if issues:
        print("❌ System check failed:")
        for issue in issues:
            print(f"  • {issue}")
        return False
    else:
        print("✅ System check passed")
        return True


def emergency_mode():
    """Emergency mode for when everything else fails"""
    print("🚨 Starting emergency mode...")
    
    try:
        # Try to import and run just the parser
        sys.path.insert(0, str(Path(__file__).parent))
        from reqif_parser import ReqIFParser
        
        parser = ReqIFParser()
        print("✅ ReqIF Parser available")
        
        # Simple command-line interface
        print("\nEmergency Mode - Basic ReqIF Parser")
        print("Enter ReqIF file path (or 'quit' to exit):")
        
        while True:
            try:
                file_path = input("> ").strip()
                if file_path.lower() in ['quit', 'exit', 'q']:
                    break
                
                if not file_path:
                    continue
                
                if not Path(file_path).exists():
                    print(f"❌ File not found: {file_path}")
                    continue
                
                print(f"📖 Parsing {file_path}...")
                requirements = parser.parse_file(file_path)
                
                print(f"✅ Found {len(requirements)} requirements")
                
                # Show first few requirements
                for i, req in enumerate(requirements[:3]):
                    print(f"\nRequirement {i+1}:")
                    print(f"  ID: {req.get('id', 'N/A')}")
                    print(f"  Title: {req.get('title', 'N/A')}")
                    print(f"  Type: {req.get('type', 'N/A')}")
                
                if len(requirements) > 3:
                    print(f"... and {len(requirements) - 3} more")
                
            except KeyboardInterrupt:
                print("\n👋 Emergency mode exited")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                
    except ImportError:
        print("❌ Cannot import parser - check installation")
    except Exception as e:
        print(f"❌ Emergency mode failed: {e}")


def main():
    """Main entry point with multiple fallback options"""
    try:
        # Quick system check first
        if not quick_system_check():
            print("\n💡 You can still try:")
            print("  python run_reqif_tool.py --safe-mode")
            print("  python startup_validator.py --gui")
            
            # Ask if user wants to continue anyway
            try:
                response = input("\nContinue anyway? (y/N): ").strip().lower()
                if response not in ['y', 'yes']:
                    return 1
            except (KeyboardInterrupt, EOFError):
                return 1
        
        # Check if we should show welcome screen
        if len(sys.argv) == 1:  # No command line arguments
            try:
                show_welcome_screen()
                return 0
            except Exception as e:
                print(f"Welcome screen failed: {e}")
                print("Falling back to direct launcher...")
        
        # Run launcher
        launcher = ReqIFLauncher()
        return launcher.run()
        
    except KeyboardInterrupt:
        print("\n👋 Startup cancelled by user")
        return 1
    except Exception as e:
        print(f"❌ Launcher failed: {e}")
        print("\n🚨 Trying emergency mode...")
        emergency_mode()
        return 1


if __name__ == "__main__":
    sys.exit(main())