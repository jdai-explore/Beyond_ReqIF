#!/usr/bin/env python3
"""
Utils Package for Enhanced ReqIF Tool
Provides configuration management, compatibility layer, and utility functions
"""

# Import main utility components
from .config import (
    Config,
    ThreadingConfig,
    CacheConfig,
    PerformanceConfig,
    CompatibilityConfig,
    config,
    get_config,
    get_threading_config,
    get_caching_config,
    get_performance_config,
    get_compatibility_config
)

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

# Version information
__version__ = "1.0.0-phase1a"
__author__ = "ReqIF Tool Suite Team"

# Public API
__all__ = [
    # Configuration
    'Config',
    'ThreadingConfig',
    'CacheConfig',
    'PerformanceConfig',
    'CompatibilityConfig',
    'config',
    'get_config',
    'get_threading_config',
    'get_caching_config',
    'get_performance_config',
    'get_compatibility_config',
    
    # Compatibility
    'CompatibilityWrapper',
    'LegacyProgressCallbackAdapter',
    'LegacyResultFormatter',
    'FallbackHandler',
    'MigrationHelper',
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
    'validate_utils_system'
]


def initialize_utils_system():
    """Initialize the utils system with default configuration"""
    try:
        # Load global configuration
        cfg = get_config()
        
        # Validate configuration
        threading_cfg = get_threading_config()
        compatibility_cfg = get_compatibility_config()
        
        print(f"Utils system initialized:")
        print(f"  Threading enabled: {threading_cfg.enabled}")
        print(f"  Compatibility mode: {compatibility_cfg.maintain_api_compatibility}")
        
        return True
        
    except Exception as e:
        print(f"Utils system initialization error: {e}")
        return False


def get_system_info():
    """Get comprehensive system information"""
    import platform
    import sys
    
    cfg = get_config()
    threading_cfg = get_threading_config()
    performance_cfg = get_performance_config()
    compatibility_cfg = get_compatibility_config()
    
    return {
        'system': {
            'platform': platform.system(),
            'python_version': sys.version,
            'architecture': platform.architecture()[0]
        },
        'configuration': {
            'threading_enabled': threading_cfg.enabled,
            'parse_threads': threading_cfg.parse_threads,
            'compare_threads': threading_cfg.compare_threads,
            'memory_monitoring': performance_cfg.memory_monitoring,
            'compatibility_mode': compatibility_cfg.maintain_api_compatibility
        },
        'features': {
            'threading_support': threading_cfg.enabled,
            'caching_support': False,  # Phase 1B
            'performance_monitoring': performance_cfg.memory_monitoring,
            'legacy_support': compatibility_cfg.legacy_progress_callbacks
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
            validation_results['config_loading'] = isinstance(threading_cfg, ThreadingConfig)
        except Exception as e:
            print(f"Config loading test failed: {e}")
        
        # Test compatibility layer
        try:
            compatibility_results = validate_compatibility()
            validation_results['compatibility_layer'] = all(compatibility_results.values())
        except Exception as e:
            print(f"Compatibility layer test failed: {e}")
        
        # Test fallback system
        try:
            register_fallback("Test fallback")
            stats = get_fallback_stats()
            validation_results['fallback_system'] = stats['fallback_count'] > 0
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
    import multiprocessing
    
    requirements = {
        'python_version': sys.version_info >= (3, 7),
        'multiprocessing_support': True,
        'threading_support': True,
        'sufficient_cores': multiprocessing.cpu_count() >= 2
    }
    
    try:
        # Test multiprocessing
        multiprocessing.cpu_count()
    except:
        requirements['multiprocessing_support'] = False
    
    try:
        # Test threading
        import threading
        threading.current_thread()
    except:
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


# Optional: Auto-initialize on import
import os
if os.getenv('REQIF_UTILS_AUTO_INIT', 'true').lower() == 'true':
    try:
        initialize_utils_system()
    except Exception as e:
        print(f"Utils auto-initialization failed: {e}")


# Convenience function for quick system check
def quick_system_check():
    """Perform a quick system compatibility check"""
    requirements = check_system_requirements()
    utils_validation = validate_utils_system()
    
    print("=== Enhanced ReqIF Tool - System Check ===")
    print(f"System Requirements: {'✅ PASS' if requirements['meets_requirements'] else '❌ FAIL'}")
    print(f"Utils System: {'✅ PASS' if utils_validation['overall_success'] else '❌ FAIL'}")
    
    if not requirements['meets_requirements']:
        print("\nRecommendations:")
        for rec in requirements['recommendations']:
            print(f"  • {rec}")
    
    if not utils_validation['overall_success']:
        print(f"\nFailed Tests: {', '.join(utils_validation['failed_tests'])}")
    
    return requirements['meets_requirements'] and utils_validation['overall_success']