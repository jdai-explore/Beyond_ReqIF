#!/usr/bin/env python3
"""
Error Handler Module - UPDATED for Phase 3
UPDATED: Removes hardcoded field references and adds validation for dynamic field structures
Provides enhanced error handling, logging, and recovery mechanisms for the Beyond ReqIF.
"""

import sys
import traceback
import logging
import os
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import messagebox
from typing import Any, Callable, Optional, Dict, List, Set


class ErrorHandler:
    """UPDATED: Enhanced error handler without hardcoded field assumptions"""
    
    def __init__(self, app_name="ReqIF Tool Suite", log_dir=None):
        self.app_name = app_name
        self.log_dir = log_dir or Path.home() / ".reqif_tool" / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self.setup_logging()
        
        # Error statistics - UPDATED with field validation tracking
        self.error_count = 0
        self.warning_count = 0
        self.field_validation_errors = 0  # NEW: Track field validation errors
        
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
        self.logger.info("Phase 3: Dynamic field validation enabled")  # NEW
        
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
    
    def validate_dynamic_field_structure(self, requirements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        NEW: Validate dynamic field structures without hardcoded assumptions
        """
        validation_results = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'field_analysis': {},
            'recommendations': []
        }
        
        if not requirements:
            validation_results['warnings'].append("No requirements to validate")
            return validation_results
        
        try:
            # Analyze actual field usage
            field_usage = {}
            total_reqs = len(requirements)
            
            for i, req in enumerate(requirements):
                if not isinstance(req, dict):
                    validation_results['errors'].append(f"Requirement {i} is not a dictionary: {type(req)}")
                    validation_results['is_valid'] = False
                    continue
                
                # Track field usage
                for field_name, field_value in req.items():
                    if not field_name.startswith('_'):  # Exclude internal fields
                        if field_name not in field_usage:
                            field_usage[field_name] = {
                                'count': 0,
                                'non_empty_count': 0,
                                'data_types': set(),
                                'sample_values': []
                            }
                        
                        field_usage[field_name]['count'] += 1
                        
                        if field_value and str(field_value).strip():
                            field_usage[field_name]['non_empty_count'] += 1
                            field_usage[field_name]['data_types'].add(type(field_value).__name__)
                            
                            # Store sample values (first 3)
                            if len(field_usage[field_name]['sample_values']) < 3:
                                sample_value = str(field_value)
                                if len(sample_value) > 50:
                                    sample_value = sample_value[:47] + "..."
                                field_usage[field_name]['sample_values'].append(sample_value)
                
                # Validate required structure
                if 'id' not in req:
                    validation_results['errors'].append(f"Requirement {i} missing required 'id' field")
                    validation_results['is_valid'] = False
            
            # Analyze field patterns
            validation_results['field_analysis'] = self._analyze_field_patterns(field_usage, total_reqs)
            
            # Generate recommendations
            validation_results['recommendations'] = self._generate_field_recommendations(
                field_usage, total_reqs, validation_results['field_analysis']
            )
            
            return validation_results
            
        except Exception as e:
            validation_results['errors'].append(f"Validation error: {str(e)}")
            validation_results['is_valid'] = False
            self.field_validation_errors += 1
            return validation_results
    
    def _analyze_field_patterns(self, field_usage: Dict, total_reqs: int) -> Dict[str, Any]:
        """Analyze field usage patterns"""
        analysis = {
            'total_fields': len(field_usage),
            'universal_fields': [],  # Present in all requirements
            'common_fields': [],     # Present in >50% of requirements
            'sparse_fields': [],     # Present in <25% of requirements
            'attribute_fields': 0,
            'regular_fields': 0
        }
        
        for field_name, usage in field_usage.items():
            fill_rate = usage['non_empty_count'] / total_reqs
            
            if fill_rate == 1.0:
                analysis['universal_fields'].append(field_name)
            elif fill_rate >= 0.5:
                analysis['common_fields'].append(field_name)
            elif fill_rate < 0.25:
                analysis['sparse_fields'].append(field_name)
            
            # Count field types
            if field_name == 'attributes':
                analysis['attribute_fields'] += 1
            else:
                analysis['regular_fields'] += 1
        
        return analysis
    
    def _generate_field_recommendations(self, field_usage: Dict, total_reqs: int, 
                                      analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on field analysis"""
        recommendations = []
        
        if analysis['total_fields'] == 0:
            recommendations.append("No fields detected - check parsing configuration")
            return recommendations
        
        # Check for essential fields
        if 'id' not in field_usage:
            recommendations.append("CRITICAL: No 'id' field found - requirements may not be properly parsed")
        
        # Check field diversity
        if analysis['total_fields'] < 3:
            recommendations.append("Low field diversity detected - check if parsing is extracting all available data")
        
        # Check for sparse fields
        if len(analysis['sparse_fields']) > analysis['total_fields'] * 0.5:
            recommendations.append("Many sparse fields detected - consider data quality review")
        
        # Check for attributes
        if 'attributes' not in field_usage:
            recommendations.append("No 'attributes' field found - this may be normal for some ReqIF files")
        
        # Performance recommendations
        if analysis['total_fields'] > 20:
            recommendations.append("High field count detected - consider optimizing display columns for performance")
        
        return recommendations
    
    def validate_ui_field_handling(self, available_fields: Set[str], display_fields: List[str]) -> Dict[str, Any]:
        """
        NEW: Validate that UI components handle missing expected fields gracefully
        """
        validation_results = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'field_coverage': {}
        }
        
        try:
            # Check if display fields are available
            missing_display_fields = []
            for field in display_fields:
                if field not in available_fields:
                    missing_display_fields.append(field)
            
            if missing_display_fields:
                validation_results['warnings'].append(
                    f"Display fields not available: {missing_display_fields}"
                )
            
            # Calculate field coverage
            if available_fields:
                coverage_rate = len([f for f in display_fields if f in available_fields]) / len(display_fields)
                validation_results['field_coverage']['rate'] = coverage_rate
                validation_results['field_coverage']['available_count'] = len(available_fields)
                validation_results['field_coverage']['display_count'] = len(display_fields)
                validation_results['field_coverage']['missing_count'] = len(missing_display_fields)
                
                if coverage_rate < 0.5:
                    validation_results['warnings'].append(
                        f"Low field coverage: {coverage_rate:.1%} of display fields are available"
                    )
            
            return validation_results
            
        except Exception as e:
            validation_results['errors'].append(f"UI validation error: {str(e)}")
            validation_results['is_valid'] = False
            return validation_results
    
    def log_field_mapping_warning(self, message: str, show_dialog=False):
        """
        NEW: Log warnings related to field mapping removal
        """
        warning_msg = f"FIELD MAPPING: {message}"
        self.logger.warning(warning_msg)
        self.warning_count += 1
        
        if show_dialog:
            try:
                messagebox.showwarning("Field Mapping Warning", warning_msg)
            except:
                print(f"WARNING: {warning_msg}")
    
    def handle_dynamic_field_error(self, operation: str, field_name: str, error: Exception):
        """
        NEW: Handle errors related to dynamic field processing
        """
        error_msg = f"Dynamic field error in {operation} for field '{field_name}': {str(error)}"
        self.logger.error(error_msg)
        self.error_count += 1
        
        # Don't show dialog for field errors by default - they should be handled gracefully
        print(f"ERROR: {error_msg}")
    
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
            text_widget.insert(tk.END, f"Field Validation Errors: {self.field_validation_errors}\n")  # NEW
            
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
        """UPDATED: Get error handling statistics"""
        return {
            'errors': self.error_count,
            'warnings': self.warning_count,
            'field_validation_errors': self.field_validation_errors,  # NEW
            'log_dir': str(self.log_dir)
        }
    
    def get_enhanced_stats(self) -> dict:
        """NEW: Get enhanced error handling statistics"""
        base_stats = self.get_stats()
        base_stats.update({
            'dynamic_field_support': True,
            'hardcoded_field_mapping': False,  # Indicates removal is complete
            'phase3_features_enabled': True
        })
        return base_stats
    
    def create_error_report(self) -> str:
        """UPDATED: Create a comprehensive error report"""
        report = f"""
=== {self.app_name} Error Report (Phase 3) ===
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

System Information:
- Python: {sys.version}
- Platform: {sys.platform}
- Working Directory: {os.getcwd()}

Session Statistics:
- Errors: {self.error_count}
- Warnings: {self.warning_count}
- Field Validation Errors: {self.field_validation_errors}

Phase 3 Features:
- Dynamic Field Detection: Enabled
- Hardcoded Field Mapping: Disabled
- Field Structure Validation: Enabled

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
    
    def create_field_validation_report(self, validation_results: Dict[str, Any]) -> str:
        """
        NEW: Create a comprehensive field validation report
        """
        report_lines = [
            "=== FIELD VALIDATION REPORT ===",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            f"Overall Status: {'✅ VALID' if validation_results['is_valid'] else '❌ INVALID'}",
            ""
        ]
        
        # Field analysis
        if 'field_analysis' in validation_results:
            analysis = validation_results['field_analysis']
            report_lines.extend([
                "FIELD ANALYSIS:",
                f"- Total Fields: {analysis.get('total_fields', 0)}",
                f"- Universal Fields: {len(analysis.get('universal_fields', []))}",
                f"- Common Fields: {len(analysis.get('common_fields', []))}",
                f"- Sparse Fields: {len(analysis.get('sparse_fields', []))}",
                ""
            ])
            
            if analysis.get('universal_fields'):
                report_lines.append(f"Universal Fields: {', '.join(analysis['universal_fields'])}")
            if analysis.get('sparse_fields'):
                report_lines.append(f"Sparse Fields: {', '.join(analysis['sparse_fields'])}")
            report_lines.append("")
        
        # Errors
        if validation_results.get('errors'):
            report_lines.extend([
                "ERRORS:",
                *[f"  ❌ {error}" for error in validation_results['errors']],
                ""
            ])
        
        # Warnings
        if validation_results.get('warnings'):
            report_lines.extend([
                "WARNINGS:",
                *[f"  ⚠️ {warning}" for warning in validation_results['warnings']],
                ""
            ])
        
        # Recommendations
        if validation_results.get('recommendations'):
            report_lines.extend([
                "RECOMMENDATIONS:",
                *[f"  💡 {rec}" for rec in validation_results['recommendations']],
                ""
            ])
        


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
    # Test the enhanced error handler (Phase 3)
    print("Testing Enhanced Error Handler (Phase 3)...")
    
    # Install global handler
    error_handler = install_global_error_handler("Test Application")
    
    # Test field validation
    test_requirements = [
        {'id': 'REQ-001', 'attributes': {'Object Text': 'Test requirement 1'}},
        {'id': 'REQ-002', 'type': 'Functional', 'attributes': {'Object Text': 'Test requirement 2'}},
        {'id': 'REQ-003'}  # Minimal requirement
    ]
    
    validation_results = error_handler.validate_dynamic_field_structure(test_requirements)
    print(f"Field validation passed: {validation_results['is_valid']}")
    print(f"Field analysis: {validation_results['field_analysis']}")
    
    # Test UI field handling validation
    available_fields = {'id', 'type', 'attributes', 'attr_Object Text'}
    display_fields = ['id', 'type', 'attr_Object Text', 'title']  # 'title' should trigger warning
    
    ui_validation = error_handler.validate_ui_field_handling(available_fields, display_fields)
    print(f"UI validation warnings: {ui_validation['warnings']}")
    
    # Test field mapping warning
    error_handler.log_field_mapping_warning("Artificial field 'title' detected and ignored")
    
    # Test dynamic field error handling
    try:
        raise ValueError("Test field processing error")
    except Exception as e:
        error_handler.handle_dynamic_field_error("test_operation", "test_field", e)
    
    # Show enhanced statistics
    stats = error_handler.get_enhanced_stats()
    print(f"Enhanced error handling stats: {stats}")
    
    # Generate validation report
    report = error_handler.create_field_validation_report(validation_results)
    print("\nField Validation Report:")
    print(report)
    
    print("Enhanced error handler (Phase 3) test completed!")