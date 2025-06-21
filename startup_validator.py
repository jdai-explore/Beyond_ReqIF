#!/usr/bin/env python3
"""
Startup Validator for ReqIF Tool Suite
Validates system requirements, module availability, and fixes common issues.
"""

import sys
import os
import tkinter as tk
from pathlib import Path
import importlib.util
from typing import List, Tuple, Dict, Any
import subprocess


class StartupValidator:
    """Validates and fixes common startup issues"""
    
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.fixes_applied = []
        self.project_dir = Path(__file__).parent
        
    def validate_python_version(self) -> bool:
        """Validate Python version compatibility"""
        print("🔍 Checking Python version...")
        
        major, minor = sys.version_info[:2]
        
        if major < 3 or (major == 3 and minor < 7):
            self.issues.append({
                'type': 'critical',
                'message': f"Python {major}.{minor} is not supported. Python 3.7+ required.",
                'fix': "Please upgrade to Python 3.7 or newer"
            })
            return False
        elif major == 3 and minor < 9:
            self.warnings.append({
                'type': 'warning',
                'message': f"Python {major}.{minor} works but Python 3.9+ recommended for best performance.",
                'fix': "Consider upgrading Python for optimal experience"
            })
        
        print(f"✅ Python {major}.{minor} - Compatible")
        return True
    
    def validate_tkinter(self) -> bool:
        """Validate tkinter availability"""
        print("🔍 Checking tkinter availability...")
        
        try:
            import tkinter as tk
            import tkinter.ttk as ttk
            
            # Test basic functionality
            root = tk.Tk()
            root.withdraw()  # Hide window
            
            # Test themed widgets
            frame = ttk.Frame(root)
            button = ttk.Button(frame, text="Test")
            
            root.destroy()
            
            print("✅ tkinter - Available and functional")
            return True
            
        except ImportError as e:
            self.issues.append({
                'type': 'critical',
                'message': "tkinter is not available",
                'fix': "Install tkinter: sudo apt-get install python3-tk (Linux) or reinstall Python with tkinter support",
                'details': str(e)
            })
            return False
        except Exception as e:
            self.warnings.append({
                'type': 'warning',
                'message': f"tkinter available but may have issues: {str(e)}",
                'fix': "GUI may not work correctly"
            })
            return False
    
    def validate_required_modules(self) -> Dict[str, bool]:
        """Validate required Python modules"""
        print("🔍 Checking required modules...")
        
        required_modules = {
            'xml.etree.ElementTree': 'XML parsing (built-in)',
            'zipfile': 'ZIP archive handling (built-in)',
            'tempfile': 'Temporary files (built-in)',
            'shutil': 'File operations (built-in)',
            'csv': 'CSV export (built-in)',
            'difflib': 'Text comparison (built-in)',
            'threading': 'Background operations (built-in)',
            'pathlib': 'Path handling (built-in)',
            'typing': 'Type hints (built-in)',
            'collections': 'Data structures (built-in)',
            'datetime': 'Date/time handling (built-in)',
            'json': 'JSON handling (built-in)',
            'logging': 'Logging (built-in)',
            'traceback': 'Error handling (built-in)'
        }
        
        module_status = {}
        
        for module_name, description in required_modules.items():
            try:
                __import__(module_name)
                print(f"✅ {module_name} - {description}")
                module_status[module_name] = True
            except ImportError as e:
                print(f"❌ {module_name} - Missing")
                self.issues.append({
                    'type': 'critical',
                    'message': f"Required module '{module_name}' not available",
                    'fix': f"This is a built-in module. Python installation may be corrupted.",
                    'details': str(e)
                })
                module_status[module_name] = False
        
        return module_status
    
    def validate_project_files(self) -> Dict[str, bool]:
        """Validate ReqIF Tool Suite project files"""
        print("🔍 Checking project files...")
        
        required_files = {
            'main.py': 'Main application',
            'reqif_parser.py': 'ReqIF file parser',
            'reqif_comparator.py': 'Requirements comparator',
            'theme_manager.py': 'Theme and styling manager'
        }
        
        optional_files = {
            'comparison_gui.py': 'Comparison results GUI',
            'visualizer_gui.py': 'Requirements visualizer GUI',
            'debug_reqif.py': 'Debug utility',
            'requirements.txt': 'Dependencies list'
        }
        
        file_status = {}
        
        # Check required files
        for filename, description in required_files.items():
            file_path = self.project_dir / filename
            if file_path.exists():
                print(f"✅ {filename} - {description}")
                file_status[filename] = True
            else:
                print(f"❌ {filename} - Missing")
                self.issues.append({
                    'type': 'critical',
                    'message': f"Required file '{filename}' not found",
                    'fix': f"Ensure {filename} is in the project directory",
                    'details': f"Expected at: {file_path}"
                })
                file_status[filename] = False
        
        # Check optional files
        for filename, description in optional_files.items():
            file_path = self.project_dir / filename
            if file_path.exists():
                print(f"✅ {filename} - {description}")
                file_status[filename] = True
            else:
                print(f"⚠️ {filename} - Optional file missing")
                self.warnings.append({
                    'type': 'warning',
                    'message': f"Optional file '{filename}' not found",
                    'fix': f"Some features may not be available without {filename}"
                })
                file_status[filename] = False
        
        return file_status
    
    def validate_module_imports(self) -> Dict[str, bool]:
        """Validate that project modules can be imported"""
        print("🔍 Checking module imports...")
        
        modules_to_test = [
            'reqif_parser',
            'reqif_comparator', 
            'theme_manager',
            'comparison_gui',
            'visualizer_gui'
        ]
        
        import_status = {}
        
        # Add project directory to path
        if str(self.project_dir) not in sys.path:
            sys.path.insert(0, str(self.project_dir))
        
        for module_name in modules_to_test:
            try:
                spec = importlib.util.spec_from_file_location(
                    module_name, 
                    self.project_dir / f"{module_name}.py"
                )
                
                if spec is None:
                    print(f"❌ {module_name} - Cannot create module spec")
                    import_status[module_name] = False
                    continue
                
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                print(f"✅ {module_name} - Imports successfully")
                import_status[module_name] = True
                
            except FileNotFoundError:
                print(f"⚠️ {module_name} - File not found (optional)")
                import_status[module_name] = False
                
            except Exception as e:
                print(f"❌ {module_name} - Import error: {str(e)}")
                if module_name in ['reqif_parser', 'reqif_comparator', 'theme_manager']:
                    self.issues.append({
                        'type': 'critical',
                        'message': f"Cannot import critical module '{module_name}'",
                        'fix': f"Check {module_name}.py for syntax errors",
                        'details': str(e)
                    })
                else:
                    self.warnings.append({
                        'type': 'warning',
                        'message': f"Cannot import optional module '{module_name}'",
                        'fix': f"Some features may not be available",
                        'details': str(e)
                    })
                import_status[module_name] = False
        
        return import_status
    
    def validate_file_permissions(self) -> bool:
        """Validate file system permissions"""
        print("🔍 Checking file permissions...")
        
        try:
            # Test read permissions
            test_files = ['main.py', 'reqif_parser.py']
            for filename in test_files:
                file_path = self.project_dir / filename
                if file_path.exists():
                    with open(file_path, 'r') as f:
                        f.read(100)  # Read first 100 chars
            
            # Test write permissions in user directory
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', delete=True) as f:
                f.write("permission test")
            
            print("✅ File permissions - OK")
            return True
            
        except PermissionError as e:
            self.issues.append({
                'type': 'critical',
                'message': "Insufficient file permissions",
                'fix': "Run with appropriate permissions or check file ownership",
                'details': str(e)
            })
            return False
        except Exception as e:
            self.warnings.append({
                'type': 'warning',
                'message': f"Permission check failed: {str(e)}",
                'fix': "May encounter issues with file operations"
            })
            return False
    
    def validate_display(self) -> bool:
        """Validate display/GUI environment"""
        print("🔍 Checking display environment...")
        
        try:
            # Check if we're in a GUI environment
            if sys.platform.startswith('linux'):
                display = os.environ.get('DISPLAY')
                if not display:
                    self.warnings.append({
                        'type': 'warning',
                        'message': "No DISPLAY environment variable found",
                        'fix': "GUI may not work in headless environment. Use 'export DISPLAY=:0' or run in desktop environment."
                    })
                    return False
            
            # Test basic tkinter window creation
            root = tk.Tk()
            root.withdraw()
            
            # Test window positioning and basic operations
            root.geometry("100x100+0+0")
            root.update_idletasks()
            root.destroy()
            
            print("✅ Display environment - OK")
            return True
            
        except tk.TclError as e:
            self.issues.append({
                'type': 'critical',
                'message': "Cannot create GUI windows",
                'fix': "Ensure you're running in a desktop environment with display support",
                'details': str(e)
            })
            return False
        except Exception as e:
            self.warnings.append({
                'type': 'warning',
                'message': f"Display validation failed: {str(e)}",
                'fix': "GUI may not work correctly"
            })
            return False
    
    def auto_fix_common_issues(self) -> bool:
        """Attempt to automatically fix common issues"""
        print("🔧 Attempting to fix common issues...")
        
        fixes_applied = False
        
        # Fix 1: Create missing directories
        try:
            log_dir = Path.home() / ".reqif_tool" / "logs"
            if not log_dir.exists():
                log_dir.mkdir(parents=True, exist_ok=True)
                self.fixes_applied.append("Created log directory")
                fixes_applied = True
                print("✅ Created log directory")
        except Exception as e:
            print(f"❌ Could not create log directory: {e}")
        
        # Fix 2: Fix Python path for imports
        project_dir_str = str(self.project_dir)
        if project_dir_str not in sys.path:
            sys.path.insert(0, project_dir_str)
            self.fixes_applied.append("Added project directory to Python path")
            fixes_applied = True
            print("✅ Fixed Python import path")
        
        # Fix 3: Set basic environment variables if needed
        try:
            if sys.platform.startswith('linux') and not os.environ.get('DISPLAY'):
                # Try to detect available display
                for display_num in [':0', ':1', ':10']:
                    if os.path.exists(f'/tmp/.X11-unix/X{display_num[1:]}'):
                        os.environ['DISPLAY'] = display_num
                        self.fixes_applied.append(f"Set DISPLAY to {display_num}")
                        fixes_applied = True
                        print(f"✅ Set DISPLAY environment variable to {display_num}")
                        break
        except Exception as e:
            print(f"⚠️ Could not auto-fix DISPLAY: {e}")
        
        return fixes_applied
    
    def generate_report(self) -> str:
        """Generate a comprehensive validation report"""
        report = []
        report.append("=" * 60)
        report.append("ReqIF Tool Suite - Startup Validation Report")
        report.append("=" * 60)
        report.append("")
        
        # Summary
        critical_issues = len([i for i in self.issues if i['type'] == 'critical'])
        warnings_count = len(self.warnings)
        
        if critical_issues == 0:
            report.append("🎉 STATUS: READY TO RUN")
        else:
            report.append(f"❌ STATUS: {critical_issues} CRITICAL ISSUES FOUND")
        
        report.append(f"• Critical Issues: {critical_issues}")
        report.append(f"• Warnings: {warnings_count}")
        report.append(f"• Auto-fixes Applied: {len(self.fixes_applied)}")
        report.append("")
        
        # Critical Issues
        if self.issues:
            report.append("CRITICAL ISSUES:")
            report.append("-" * 40)
            for issue in self.issues:
                report.append(f"❌ {issue['message']}")
                report.append(f"   Fix: {issue['fix']}")
                if 'details' in issue:
                    report.append(f"   Details: {issue['details']}")
                report.append("")
        
        # Warnings
        if self.warnings:
            report.append("WARNINGS:")
            report.append("-" * 40)
            for warning in self.warnings:
                report.append(f"⚠️ {warning['message']}")
                report.append(f"   Recommendation: {warning['fix']}")
                if 'details' in warning:
                    report.append(f"   Details: {warning['details']}")
                report.append("")
        
        # Applied Fixes
        if self.fixes_applied:
            report.append("AUTO-FIXES APPLIED:")
            report.append("-" * 40)
            for fix in self.fixes_applied:
                report.append(f"🔧 {fix}")
            report.append("")
        
        # System Info
        report.append("SYSTEM INFORMATION:")
        report.append("-" * 40)
        report.append(f"Python Version: {sys.version}")
        report.append(f"Platform: {sys.platform}")
        report.append(f"Project Directory: {self.project_dir}")
        report.append(f"Current Working Directory: {os.getcwd()}")
        
        return "\n".join(report)
    
    def run_full_validation(self) -> bool:
        """Run complete validation suite"""
        print("🚀 Starting ReqIF Tool Suite validation...")
        print("=" * 60)
        
        # Run all validations
        validations = [
            self.validate_python_version(),
            self.validate_tkinter(),
            self.validate_required_modules(),
            self.validate_project_files(),
            self.validate_file_permissions(),
            self.validate_display()
        ]
        
        # Test module imports
        self.validate_module_imports()
        
        # Attempt auto-fixes
        self.auto_fix_common_issues()
        
        print("\n" + "=" * 60)
        
        # Generate and display report
        report = self.generate_report()
        print(report)
        
        # Save report to file
        try:
            report_file = self.project_dir / "startup_validation_report.txt"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"\n📄 Report saved to: {report_file}")
        except Exception as e:
            print(f"⚠️ Could not save report: {e}")
        
        # Return success status
        critical_issues = len([i for i in self.issues if i['type'] == 'critical'])
        return critical_issues == 0
    
    def show_gui_report(self):
        """Show validation report in a GUI window"""
        try:
            root = tk.Tk()
            root.title("ReqIF Tool Suite - Validation Report")
            root.geometry("800x600")
            
            # Create text widget with scrollbar
            frame = tk.Frame(root)
            frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            text_widget = tk.Text(frame, wrap=tk.WORD, font=('Consolas', 10))
            scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)
            
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Insert report
            report = self.generate_report()
            text_widget.insert(tk.END, report)
            text_widget.configure(state=tk.DISABLED)
            
            # Buttons frame
            button_frame = tk.Frame(root)
            button_frame.pack(fill=tk.X, padx=10, pady=5)
            
            # Close button
            close_btn = tk.Button(button_frame, text="Close", command=root.destroy)
            close_btn.pack(side=tk.RIGHT, padx=5)
            
            # Copy button
            def copy_report():
                root.clipboard_clear()
                root.clipboard_append(report)
                
            copy_btn = tk.Button(button_frame, text="Copy Report", command=copy_report)
            copy_btn.pack(side=tk.RIGHT, padx=5)
            
            # Start main if no critical issues
            critical_issues = len([i for i in self.issues if i['type'] == 'critical'])
            if critical_issues == 0:
                def start_application():
                    root.destroy()
                    # Import and start main application
                    try:
                        from main import ReqIFToolMVP
                        app = ReqIFToolMVP()
                        app.run()
                    except Exception as e:
                        tk.messagebox.showerror("Startup Error", f"Failed to start application:\n{str(e)}")
                
                start_btn = tk.Button(button_frame, text="Start Application", 
                                    command=start_application, bg='green', fg='white')
                start_btn.pack(side=tk.LEFT, padx=5)
            
            root.mainloop()
            
        except Exception as e:
            print(f"Could not show GUI report: {e}")
            print("\nFalling back to console report:")
            print(self.generate_report())


def main():
    """Main validation function"""
    validator = StartupValidator()
    
    # Check if GUI should be shown
    show_gui = len(sys.argv) > 1 and sys.argv[1] == '--gui'
    
    # Run validation
    success = validator.run_full_validation()
    
    if show_gui:
        # Show GUI report
        validator.show_gui_report()
    else:
        # Console mode
        if success:
            print("\n🎉 All validations passed! You can start the application.")
            print("💡 Run 'python main.py' to start the ReqIF Tool Suite")
        else:
            print("\n❌ Validation failed. Please fix the issues above before running.")
            print("💡 Run 'python startup_validator.py --gui' for a detailed GUI report")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())