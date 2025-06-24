#!/usr/bin/env python3
"""
Compatibility Layer for Enhanced ReqIF Tool
Ensures 100% backward compatibility while adding new enhanced functionality
"""

import functools
import warnings
import threading
import time
from typing import Dict, Any, List, Callable, Optional, Union
from utils.config import get_compatibility_config, get_threading_config


class CompatibilityWrapper:
    """
    Main compatibility wrapper to ensure existing functionality works unchanged
    """
    
    def __init__(self):
        self.compatibility_config = get_compatibility_config()
        self.threading_config = get_threading_config()
        self._legacy_callbacks = {}
        self._result_formatters = {}
    
    def ensure_backward_compatibility(self, func):
        """Decorator to ensure backward compatibility for enhanced functions"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Try enhanced version first
                if self.compatibility_config.maintain_api_compatibility:
                    return self._safe_enhanced_execution(func, *args, **kwargs)
                else:
                    return func(*args, **kwargs)
            except Exception as e:
                if self.compatibility_config.sequential_fallback:
                    if self.compatibility_config.verbose_logging:
                        print(f"Enhanced version failed, falling back: {e}")
                    return self._fallback_execution(func, *args, **kwargs)
                else:
                    raise
        return wrapper
    
    def _safe_enhanced_execution(self, func, *args, **kwargs):
        """Execute enhanced version with safety checks"""
        # Check if threading should be disabled for this call
        if 'use_threading' in kwargs:
            if not kwargs['use_threading'] and self.threading_config.enabled:
                # Temporarily disable threading for this call
                kwargs['_force_sequential'] = True
        
        # Check for cache bypass
        if self.compatibility_config.cache_bypass_option:
            if kwargs.get('bypass_cache', False):
                kwargs['_bypass_cache'] = True
        
        return func(*args, **kwargs)
    
    def _fallback_execution(self, func, *args, **kwargs):
        """Fallback execution with legacy behavior"""
        # Remove enhanced-specific kwargs
        legacy_kwargs = {k: v for k, v in kwargs.items() 
                        if not k.startswith('_') and k not in ['use_threading', 'bypass_cache']}
        
        # Execute with original behavior
        return func(*args, **legacy_kwargs)


class LegacyProgressCallbackAdapter:
    """
    Adapter to convert new multi-threaded progress callbacks to legacy format
    """
    
    def __init__(self, legacy_callback: Optional[Callable]):
        self.legacy_callback = legacy_callback
        self.last_update_time = 0
        self.update_interval = 0.1  # Minimum interval between updates
    
    def __call__(self, current: int, maximum: int, status: str, **kwargs):
        """Convert enhanced progress format to legacy format"""
        if not self.legacy_callback:
            return
        
        # Throttle updates to avoid overwhelming legacy callbacks
        current_time = time.time()
        if current_time - self.last_update_time < self.update_interval:
            return
        
        self.last_update_time = current_time
        
        try:
            # Call legacy callback with expected signature
            if callable(self.legacy_callback):
                # Detect callback signature and adapt accordingly
                import inspect
                sig = inspect.signature(self.legacy_callback)
                params = list(sig.parameters.keys())
                
                if len(params) == 3:
                    # Standard format: (current, maximum, status)
                    self.legacy_callback(current, maximum, status)
                elif len(params) == 2:
                    # Simplified format: (current, maximum)
                    self.legacy_callback(current, maximum)
                else:
                    # Generic format: pass all as kwargs
                    self.legacy_callback(current=current, maximum=maximum, status=status)
        except Exception as e:
            if get_compatibility_config().verbose_logging:
                print(f"Legacy callback error: {e}")


class LegacyResultFormatter:
    """
    Formats enhanced results to match legacy result structure
    """
    
    @staticmethod
    def format_comparison_results(enhanced_results: Dict[str, Any]) -> Dict[str, Any]:
        """Format enhanced comparison results to legacy format"""
        if not get_compatibility_config().legacy_result_format:
            return enhanced_results
        
        # Ensure all legacy fields are present
        legacy_results = {
            'added': enhanced_results.get('added', []),
            'deleted': enhanced_results.get('deleted', []),
            'modified': enhanced_results.get('modified', []),
            'unchanged': enhanced_results.get('unchanged', []),
            'statistics': enhanced_results.get('statistics', {}),
        }
        
        # Remove enhanced-only fields that might confuse legacy code
        legacy_statistics = legacy_results['statistics'].copy()
        enhanced_only_fields = ['cache_hits', 'processing_time', 'thread_count', 'memory_usage']
        for field in enhanced_only_fields:
            legacy_statistics.pop(field, None)
        
        legacy_results['statistics'] = legacy_statistics
        return legacy_results
    
    @staticmethod
    def format_folder_results(enhanced_results: Dict[str, Any]) -> Dict[str, Any]:
        """Format enhanced folder results to legacy format"""
        if not get_compatibility_config().legacy_result_format:
            return enhanced_results
        
        # Keep legacy structure while hiding enhanced fields
        legacy_results = enhanced_results.copy()
        
        # Remove enhanced-only sections
        enhanced_only_sections = ['individual_file_statistics', 'performance_metrics', 'cache_statistics']
        for section in enhanced_only_sections:
            legacy_results.pop(section, None)
        
        return legacy_results


class FallbackHandler:
    """
    Handles graceful degradation when enhanced features fail
    """
    
    def __init__(self):
        self.fallback_count = 0
        self.failure_reasons = []
    
    def register_fallback(self, reason: str):
        """Register a fallback event"""
        self.fallback_count += 1
        self.failure_reasons.append(reason)
        
        if get_compatibility_config().verbose_logging:
            print(f"Fallback #{self.fallback_count}: {reason}")
    
    def should_use_fallback(self, feature: str) -> bool:
        """Determine if a feature should use fallback"""
        config = get_compatibility_config()
        
        if feature == 'threading':
            return not get_threading_config().enabled or config.sequential_fallback
        elif feature == 'caching':
            return config.cache_bypass_option
        else:
            return config.sequential_fallback
    
    def get_fallback_stats(self) -> Dict[str, Any]:
        """Get fallback statistics"""
        return {
            'fallback_count': self.fallback_count,
            'failure_reasons': self.failure_reasons,
            'most_common_reason': max(set(self.failure_reasons), key=self.failure_reasons.count) if self.failure_reasons else None
        }


class MigrationHelper:
    """
    Helps migrate from old configurations to new enhanced configurations
    """
    
    @staticmethod
    def migrate_old_config(old_config: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate old configuration format to new format"""
        new_config = {}
        
        # Map old settings to new structure
        if 'max_files' in old_config:
            new_config.setdefault('threading', {})['max_files_per_thread'] = old_config['max_files'] // 4
        
        if 'progress_callback' in old_config:
            new_config.setdefault('compatibility', {})['legacy_progress_callbacks'] = True
        
        if 'timeout' in old_config:
            new_config.setdefault('threading', {})['thread_timeout'] = old_config['timeout']
        
        return new_config
    
    @staticmethod
    def detect_legacy_usage(args, kwargs) -> bool:
        """Detect if legacy usage patterns are being used"""
        legacy_indicators = [
            'single_threaded' in kwargs,
            'no_cache' in kwargs,
            'old_format' in kwargs,
            len(args) > 5,  # Old function signatures often had more positional args
        ]
        
        return any(legacy_indicators)


# Global instances
compatibility_wrapper = CompatibilityWrapper()
fallback_handler = FallbackHandler()
migration_helper = MigrationHelper()


def ensure_compatibility(func):
    """Main compatibility decorator"""
    return compatibility_wrapper.ensure_backward_compatibility(func)


def legacy_progress_adapter(callback):
    """Create legacy progress adapter"""
    return LegacyProgressCallbackAdapter(callback)


def format_legacy_results(results, result_type='comparison'):
    """Format results for legacy compatibility"""
    if result_type == 'comparison':
        return LegacyResultFormatter.format_comparison_results(results)
    elif result_type == 'folder':
        return LegacyResultFormatter.format_folder_results(results)
    else:
        return results


def register_fallback(reason: str):
    """Register a fallback event"""
    fallback_handler.register_fallback(reason)


def should_use_fallback(feature: str) -> bool:
    """Check if should use fallback for a feature"""
    return fallback_handler.should_use_fallback(feature)


def get_fallback_stats() -> Dict[str, Any]:
    """Get fallback statistics"""
    return fallback_handler.get_fallback_stats()


def migrate_config(old_config: Dict[str, Any]) -> Dict[str, Any]:
    """Migrate old configuration"""
    return migration_helper.migrate_old_config(old_config)


def detect_legacy_usage(*args, **kwargs) -> bool:
    """Detect legacy usage patterns"""
    return migration_helper.detect_legacy_usage(args, kwargs)


# Testing and validation functions
def validate_compatibility():
    """Validate that compatibility layer is working correctly"""
    test_results = {
        'progress_adapter': False,
        'result_formatter': False,
        'fallback_handler': False,
        'config_migration': False
    }
    
    try:
        # Test progress adapter
        def dummy_callback(current, maximum, status):
            pass
        adapter = LegacyProgressCallbackAdapter(dummy_callback)
        adapter(50, 100, "Test")
        test_results['progress_adapter'] = True
    except Exception as e:
        print(f"Progress adapter test failed: {e}")
    
    try:
        # Test result formatter
        test_results_data = {
            'added': [],
            'deleted': [],
            'modified': [],
            'unchanged': [],
            'statistics': {'cache_hits': 10}
        }
        formatted = LegacyResultFormatter.format_comparison_results(test_results_data)
        test_results['result_formatter'] = 'cache_hits' not in formatted['statistics']
    except Exception as e:
        print(f"Result formatter test failed: {e}")
    
    try:
        # Test fallback handler
        fallback_handler.register_fallback("Test fallback")
        test_results['fallback_handler'] = fallback_handler.fallback_count > 0
    except Exception as e:
        print(f"Fallback handler test failed: {e}")
    
    try:
        # Test config migration
        old_config = {'max_files': 100, 'timeout': 300}
        migrated = migration_helper.migrate_old_config(old_config)
        test_results['config_migration'] = 'threading' in migrated
    except Exception as e:
        print(f"Config migration test failed: {e}")
    
    return test_results


# Example usage and testing
if __name__ == "__main__":
    print("Testing Compatibility Layer...")
    
    # Run validation tests
    results = validate_compatibility()
    print("Validation Results:")
    for test, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {test}: {status}")
    
    # Test compatibility wrapper
    @ensure_compatibility
    def test_enhanced_function(value, use_threading=True, bypass_cache=False):
        """Test function with enhanced parameters"""
        return f"Enhanced: {value}, threading: {use_threading}, cache: {not bypass_cache}"
    
    # Test normal usage
    result1 = test_enhanced_function("test1")
    print(f"Normal usage: {result1}")
    
    # Test with legacy parameters
    result2 = test_enhanced_function("test2", use_threading=False)
    print(f"Legacy usage: {result2}")
    
    print("Compatibility layer ready!")