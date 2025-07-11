#!/usr/bin/env python3
"""
Utils Package for Enhanced ReqIF Tool
FIXED: Safe imports and threading initialization
Provides configuration management, compatibility layer, and utility functions
"""

# Safe imports with fallbacks
def safe_import(module_name, fallback=None):
    """Safely import a module with fallback"""
    try:
        import importlib
        return importlib.import_module(module_name)
    except ImportError as e:
        print(f"Warning: Could not import {module_name}: {e}")
        return fallback

# Import main utility components with safe imports
try:
    from .config import (
        Config,
        ThreadingConfig,
        CacheConfig,
        PerformanceConfig,
        CompatibilityConfig,
        ParsingConfig,
        config,
        get_config,
        get_threading_config,
        get_caching_config,
        get_performance_config,
        get_compatibility_config,
        get_parsing_config
    )
    CONFIG_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Config module not available: {e}")
    CONFIG_AVAILABLE = False
    
    # Create fallback config classes
    class DefaultConfig:
        def get_threading_config(self): return DefaultThreadingConfig()
        def get_parsing_config(self): return DefaultParsingConfig()
        def get_compatibility_config(self): return DefaultCompatibilityConfig()
    
    class DefaultThreadingConfig:
        def __init__(self):
            import multiprocessing
            try:
                cpu_count = multiprocessing.cpu_count()
            except:
                cpu_count = 4
            self.enabled = True
            self.parse_threads = min(4, max(2, cpu_count // 2))
            self.compare_threads = min(2, max(1, cpu_count // 4))
            self.io_threads = 2
    
    class DefaultParsingConfig:
        def __init__(self):
            self.preserve_original_structure = True
            self.field_mapping_disabled = True
            self.dynamic_field_detection = True
    
    class DefaultCompatibilityConfig:
        def __init__(self):
            self.maintain_api_compatibility = True
            self.sequential_fallback = True
    
    # Create fallback instances
    config = DefaultConfig()
    get_config = lambda: config
    get_threading_config = lambda: DefaultThreadingConfig()
    get_parsing_config = lambda: DefaultParsingConfig()
    get_compatibility_config = lambda: DefaultCompatibilityConfig()

try:
    from .compatibility_layer import (
        CompatibilityWrapper,
        LegacyProgressCallbackAdapter,
        LegacyResultFormatter,
        FallbackHandler,
        MigrationHelper,
        ensure_compatibility,
        legacy_progress_adapter,
        format_legacy_results,
        register_fallback,
        should_use_fallback,
        get_fallback_stats,
        migrate_config,
        detect_legacy_usage,
        validate_compatibility
    )
    COMPATIBILITY_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Compatibility layer not available: {e}")
    COMPATIBILITY_AVAILABLE = False
    
    # Create fallback compatibility functions
    def ensure_compatibility(func): return func
    def legacy_progress_adapter(callback): return callback
    def format_legacy_results(results, result_type='comparison'): return results
    def register_fallback(reason): print(f"Fallback: {reason}")
    def should_use_fallback(feature): return False
    def get_fallback_stats(): return {'fallback_count': 0, 'failure_reasons': []}
    def migrate_config(old_config): return old_config
    def detect_legacy_usage(*args, **kwargs): return False
    def validate_compatibility(): return {'overall_success': True}

# Version information
__version__ = "1.0.0-phase1a-fixed"
__author__ = "ReqIF Tool Suite Team"

# Public API
__all__ = [
    # Configuration (if available)
    'get_config',
    'get_threading_config', 
    'get_caching_config',
    'get_performance_config',
    'get_compatibility_config',
    'get_parsing_config',
    
    # Compatibility (if available)
    'ensure_compatibility',
    'legacy_progress_adapter',
    'format_legacy_results',
    'register_fallback',
    'should_use_fallback',
    'get_fallback_stats',
    'migrate_config',
    'detect_legacy_usage',
    'validate_compatibility',
    
    # Utility functions
    'initialize_utils_system',
    'get_system_info',
    'validate_utils_system',
    'quick_system_check'
]

# Add available classes to __all__ if imported successfully
if CONFIG_AVAILABLE:
    __all__.extend([
        'Config', 'ThreadingConfig', 'CacheConfig', 'PerformanceConfig', 
        'CompatibilityConfig', 'ParsingConfig', 'config'
    ])

if COMPATIBILITY_AVAILABLE:
    __all__.extend([
        'CompatibilityWrapper', 'LegacyProgressCallbackAdapter', 'LegacyResultFormatter',
        'FallbackHandler', 'MigrationHelper'
    ])


def initialize_utils_system():
    """Initialize the utils system with default configuration"""
    try:
        # Load global configuration
        cfg = get_config()
        
        # Validate configuration
        threading_cfg = get_threading_config()
        compatibility_cfg = get_compatibility_config()
        
        print(f"Utils system initialized:")
        print(f"  Threading enabled: {getattr(threading_cfg, 'enabled', True)}")
        print(f"  Compatibility mode: {getattr(compatibility_cfg, 'maintain_api_compatibility', True)}")
        
        return True
        
    except Exception as e:
        print(f"Utils system initialization error: {e}")
        return False


def get_system_info():
    """Get comprehensive system information"""
    import platform
    import sys
    
    try:
        cfg = get_config()
        threading_cfg = get_threading_config()
        compatibility_cfg = get_compatibility_config()
        
        # Safe attribute access
        threading_enabled = getattr(threading_cfg, 'enabled', True)
        parse_threads = getattr(threading_cfg, 'parse_threads', 4)
        compare_threads = getattr(threading_cfg, 'compare_threads', 2)
        compatibility_mode = getattr(compatibility_cfg, 'maintain_api_compatibility', True)
        
    except Exception as e:
        print(f"Warning: Could not get full configuration: {e}")
        threading_enabled = True
        parse_threads = 4
        compare_threads = 2
        compatibility_mode = True
    
    return {
        'system': {
            'platform': platform.system(),
            'python_version': sys.version,
            'architecture': platform.architecture()[0]
        },
        'configuration': {
            'threading_enabled': threading_enabled,
            'parse_threads': parse_threads,
            'compare_threads': compare_threads,
            'compatibility_mode': compatibility_mode
        },
        'features': {
            'threading_support': threading_enabled,
            'caching_support': False,  # Phase 1B
            'legacy_support': compatibility_mode,
            'config_available': CONFIG_AVAILABLE,
            'compatibility_available': COMPATIBILITY_AVAILABLE
        },
        'version': __version__
    }


def validate_utils_system():
    """Validate that the utils system is working correctly"""
    try:
        validation_results = {
            'config_loading': False,
            'compatibility_layer': False,
            'fallback_system': False
        }
        
        # Test configuration loading
        try:
            cfg = get_config()
            threading_cfg = get_threading_config()
            validation_results['config_loading'] = threading_cfg is not None
        except Exception as e:
            print(f"Config loading test failed: {e}")
        
        # Test compatibility layer
        try:
            if COMPATIBILITY_AVAILABLE:
                compatibility_results = validate_compatibility()
                validation_results['compatibility_layer'] = compatibility_results.get('overall_success', True)
            else:
                validation_results['compatibility_layer'] = True  # Pass if using fallback
        except Exception as e:
            print(f"Compatibility layer test failed: {e}")
        
        # Test fallback system
        try:
            register_fallback("Test fallback")
            stats = get_fallback_stats()
            validation_results['fallback_system'] = 'fallback_count' in stats
        except Exception as e:
            print(f"Fallback system test failed: {e}")
        
        return {
            'overall_success': all(validation_results.values()),
            'individual_tests': validation_results,
            'failed_tests': [test for test, passed in validation_results.items() if not passed]
        }
        
    except Exception as e:
        return {
            'overall_success': False,
            'error': str(e),
            'individual_tests': {},
            'failed_tests': ['validation_error']
        }


def check_system_requirements():
    """Check if system meets requirements for enhanced features"""
    import sys
    
    requirements = {
        'python_version': sys.version_info >= (3, 7),
        'multiprocessing_support': True,
        'threading_support': True,
        'sufficient_cores': True
    }
    
    try:
        # Test multiprocessing
        import multiprocessing
        cpu_count = multiprocessing.cpu_count()
        requirements['sufficient_cores'] = cpu_count >= 2
    except Exception as e:
        print(f"Multiprocessing test failed: {e}")
        requirements['multiprocessing_support'] = False
    
    try:
        # Test threading
        import threading
        threading.current_thread()
    except Exception as e:
        print(f"Threading test failed: {e}")
        requirements['threading_support'] = False
    
    return {
        'meets_requirements': all(requirements.values()),
        'requirements_detail': requirements,
        'recommendations': _get_system_recommendations(requirements)
    }


def _get_system_recommendations(requirements):
    """Get system recommendations based on requirements check"""
    recommendations = []
    
    if not requirements['python_version']:
        recommendations.append("Upgrade to Python 3.7 or higher for full functionality")
    
    if not requirements['multiprocessing_support']:
        recommendations.append("Multiprocessing not available - threading features will be disabled")
    
    if not requirements['threading_support']:
        recommendations.append("Threading not available - will fall back to sequential processing")
    
    if not requirements['sufficient_cores']:
        recommendations.append("Single-core system detected - threading benefits will be minimal")
    
    if not recommendations:
        recommendations.append("System meets all requirements for enhanced features")
    
    return recommendations


# Optional: Auto-initialize on import with safe error handling
import os
if os.getenv('REQIF_UTILS_AUTO_INIT', 'true').lower() == 'true':
    try:
        initialize_utils_system()
    except Exception as e:
        print(f"Utils auto-initialization failed: {e}")


# Convenience function for quick system check
def quick_system_check():
    """Perform a quick system compatibility check"""
    try:
        requirements = check_system_requirements()
        utils_validation = validate_utils_system()
        
        print("=== Enhanced ReqIF Tool - System Check ===")
        print(f"System Requirements: {'✅ PASS' if requirements['meets_requirements'] else '❌ FAIL'}")
        print(f"Utils System: {'✅ PASS' if utils_validation['overall_success'] else '❌ FAIL'}")
        print(f"Config Available: {'✅ YES' if CONFIG_AVAILABLE else '⚠️ FALLBACK'}")
        print(f"Compatibility Available: {'✅ YES' if COMPATIBILITY_AVAILABLE else '⚠️ FALLBACK'}")
        
        if not requirements['meets_requirements']:
            print("\nRecommendations:")
            for rec in requirements['recommendations']:
                print(f"  • {rec}")
        
        if not utils_validation['overall_success']:
            print(f"\nFailed Tests: {', '.join(utils_validation['failed_tests'])}")
        
        return requirements['meets_requirements'] and utils_validation['overall_success']
        
    except Exception as e:
        print(f"System check failed: {e}")
        return False


# Safe initialization that won't fail
def safe_threading_init():
    """Safe threading initialization that won't fail the application"""
    try:
        # Try to import and initialize threading system
        from thread_pools import initialize_threading_system
        success = initialize_threading_system()
        if success:
            print("Threading system initialized successfully")
        else:
            print("Threading system initialization failed - falling back to sequential processing")
            register_fallback("Threading system initialization failed")
        return success
    except ImportError:
        print("Threading system not available - using sequential processing")
        register_fallback("Threading system not available")
        return False
    except Exception as e:
        print(f"Threading initialization error: {e} - using sequential processing")
        register_fallback(f"Threading initialization error: {e}")
        return False


# Auto-run safe threading initialization
if os.getenv('REQIF_THREADING_AUTO_INIT', 'true').lower() == 'true':
    safe_threading_init()