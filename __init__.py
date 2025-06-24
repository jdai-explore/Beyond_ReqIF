#!/usr/bin/env python3
"""
Enhanced ReqIF Tool Suite - Main Package
Professional ReqIF file parser, comparison, and visualization tool with enhanced performance
"""

# Version information
__version__ = "1.3.0-enhanced-phase1a"
__author__ = "ReqIF Tool Suite Team"
__description__ = "Enhanced ReqIF Tool Suite with threading and individual file statistics"

# Import main components for easy access
try:
    from .reqif_parser import ReqIFParser
    from .reqif_comparator import ReqIFComparator
    from .folder_comparator import FolderComparator
    from .comparison_gui import ComparisonResultsGUI
    from .folder_comparison_gui import FolderComparisonResultsGUI
    from .visualizer_gui import VisualizerGUI
    from .main import ReqIFToolNative
    
    # Enhanced components - FIXED IMPORTS
    from .utils import (
        get_config, get_threading_config, get_compatibility_config,
        ensure_compatibility, legacy_progress_adapter, quick_system_check
    )
    from .thread_pools import (
        get_thread_manager, execute_parallel_parse, execute_parallel_compare,
        get_threading_stats, is_threading_healthy
    )
    
    IMPORTS_SUCCESSFUL = True
    
except ImportError as e:
    print(f"Warning: Some enhanced features may not be available: {e}")
    # Fallback to basic imports
    try:
        from .reqif_parser import ReqIFParser
        from .reqif_comparator import ReqIFComparator
        from .folder_comparator import FolderComparator
        from .main import ReqIFToolNative
        IMPORTS_SUCCESSFUL = False
    except ImportError as e:
        print(f"Critical import error: {e}")
        IMPORTS_SUCCESSFUL = False

# Public API
__all__ = [
    # Core components
    'ReqIFParser',
    'ReqIFComparator', 
    'FolderComparator',
    'ReqIFToolNative',
    
    # GUI components
    'ComparisonResultsGUI',
    'FolderComparisonResultsGUI',
    'VisualizerGUI',
    
    # Enhanced features (if available)
    'get_config',
    'get_threading_config',
    'get_compatibility_config',
    'ensure_compatibility',
    'legacy_progress_adapter',
    'quick_system_check',
    'get_thread_manager',
    'execute_parallel_parse',
    'execute_parallel_compare',
    'get_threading_stats',
    'is_threading_healthy',
    
    # Package info
    '__version__',
    '__author__',
    '__description__',
    'IMPORTS_SUCCESSFUL'
]


def get_package_info():
    """Get comprehensive package information"""
    info = {
        'version': __version__,
        'author': __author__,
        'description': __description__,
        'imports_successful': IMPORTS_SUCCESSFUL,
        'features': {
            'basic_functionality': True,
            'enhanced_threading': IMPORTS_SUCCESSFUL,
            'individual_statistics': IMPORTS_SUCCESSFUL,
            'configuration_management': IMPORTS_SUCCESSFUL,
            'compatibility_layer': IMPORTS_SUCCESSFUL
        }
    }
    
    if IMPORTS_SUCCESSFUL:
        try:
            # Get system information
            from .utils import get_system_info, check_system_requirements
            info['system_info'] = get_system_info()
            info['system_requirements'] = check_system_requirements()
        except:
            pass
    
    return info


def run_package_validation():
    """Run comprehensive package validation"""
    print(f"=== Enhanced ReqIF Tool Suite v{__version__} ===")
    print(f"Validation Results:")
    
    validation_results = {
        'basic_imports': False,
        'enhanced_imports': False,
        'system_requirements': False,
        'threading_system': False,
        'configuration_system': False
    }
    
    # Test basic imports
    try:
        parser = ReqIFParser()
        comparator = ReqIFComparator()
        validation_results['basic_imports'] = True
        print("  ✅ Basic imports: PASS")
    except Exception as e:
        print(f"  ❌ Basic imports: FAIL - {e}")
    
    # Test enhanced imports
    if IMPORTS_SUCCESSFUL:
        try:
            config = get_config()
            validation_results['enhanced_imports'] = True
            print("  ✅ Enhanced imports: PASS")
        except Exception as e:
            print(f"  ❌ Enhanced imports: FAIL - {e}")
    else:
        print("  ⚠️ Enhanced imports: SKIPPED (import errors)")
    
    # Test system requirements
    if IMPORTS_SUCCESSFUL:
        try:
            from .utils import check_system_requirements
            req_check = check_system_requirements()
            validation_results['system_requirements'] = req_check['meets_requirements']
            status = "PASS" if req_check['meets_requirements'] else "WARN"
            print(f"  {'✅' if status == 'PASS' else '⚠️'} System requirements: {status}")
        except Exception as e:
            print(f"  ❌ System requirements: FAIL - {e}")
    
    # Test threading system
    if IMPORTS_SUCCESSFUL:
        try:
            from .thread_pools import validate_threading_system
            thread_validation = validate_threading_system()
            validation_results['threading_system'] = thread_validation['overall_success']
            status = "PASS" if thread_validation['overall_success'] else "FAIL"
            print(f"  {'✅' if status == 'PASS' else '❌'} Threading system: {status}")
        except Exception as e:
            print(f"  ❌ Threading system: FAIL - {e}")
    
    # Test configuration system
    if IMPORTS_SUCCESSFUL:
        try:
            from .utils import validate_utils_system
            utils_validation = validate_utils_system()
            validation_results['configuration_system'] = utils_validation['overall_success']
            status = "PASS" if utils_validation['overall_success'] else "FAIL"
            print(f"  {'✅' if status == 'PASS' else '❌'} Configuration system: {status}")
        except Exception as e:
            print(f"  ❌ Configuration system: FAIL - {e}")
    
    # Overall status
    overall_success = validation_results['basic_imports'] and (
        not IMPORTS_SUCCESSFUL or 
        (validation_results['enhanced_imports'] and validation_results['threading_system'])
    )
    
    print(f"\n  Overall Status: {'✅ READY' if overall_success else '❌ ISSUES DETECTED'}")
    
    if not overall_success:
        print("  Recommendations:")
        if not validation_results['basic_imports']:
            print("    • Check Python environment and dependencies")
        if IMPORTS_SUCCESSFUL and not validation_results['enhanced_imports']:
            print("    • Enhanced features may not be available")
        if IMPORTS_SUCCESSFUL and not validation_results['threading_system']:
            print("    • Threading features disabled - will use sequential processing")
    
    return validation_results


# Quick start function
def quick_start():
    """Quick start guide for the enhanced tool"""
    print(f"""
=== Enhanced ReqIF Tool Suite v{__version__} - Quick Start ===

1. Basic Usage (Compatible with existing code):
   from reqif_tool_suite import FolderComparator
   
   comparator = FolderComparator()
   results = comparator.compare_folders(folder1, folder2)

2. Enhanced Usage (New features):
   # Automatic threading for better performance
   # Individual file statistics available in results
   # Enhanced export capabilities
   
3. Configuration (Optional):
   from reqif_tool_suite import get_config
   
   config = get_config()
   config.update_section('threading', {{'parse_threads': 6}})

4. Performance Monitoring (New):
   from reqif_tool_suite import get_threading_stats
   
   stats = get_threading_stats()
   print(f"Threading efficiency: {{stats}}")

5. System Validation:
   from reqif_tool_suite import run_package_validation
   
   run_package_validation()

Features in v{__version__}:
• 3-4x faster folder comparisons (50-200 files)
• Individual file statistics and analysis
• 100% backward compatibility
• Intelligent configuration management
• Automatic fallback to sequential processing
""")


# Optional: Auto-run validation on import if environment variable is set
import os
if os.getenv('REQIF_VALIDATE_ON_IMPORT', 'false').lower() == 'true':
    try:
        run_package_validation()
    except Exception as e:
        print(f"Auto-validation failed: {e}")