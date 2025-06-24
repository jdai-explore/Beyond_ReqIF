#!/usr/bin/env python3
"""
Configuration Management for Enhanced ReqIF Tool
Handles threading, caching, and performance settings with backward compatibility
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
import threading


class Config:
    """
    Main configuration manager with thread-safe access and automatic defaults
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Singleton pattern for global configuration access"""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(Config, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self):
        """Initialize configuration with safe defaults"""
        if self._initialized:
            return
        
        self._config_data = {}
        self._config_file = None
        self._load_defaults()
        self._load_user_config()
        self._initialized = True
    
    def _load_defaults(self):
        """Load safe default configuration"""
        self._config_data = {
            'threading': ThreadingConfig().to_dict(),
            'caching': CacheConfig().to_dict(),
            'performance': PerformanceConfig().to_dict(),
            'compatibility': CompatibilityConfig().to_dict(),
            'version': '1.3.0-enhanced',
            'config_version': 1
        }
    
    def _load_user_config(self):
        """Load user configuration from file if it exists"""
        try:
            config_dir = Path.home() / '.reqif_tool'
            config_dir.mkdir(exist_ok=True)
            self._config_file = config_dir / 'config.json'
            
            if self._config_file.exists():
                with open(self._config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    self._merge_config(user_config)
        except Exception as e:
            print(f"Warning: Could not load user config: {e}")
            # Continue with defaults
    
    def _merge_config(self, user_config: Dict[str, Any]):
        """Safely merge user configuration with defaults"""
        for section, values in user_config.items():
            if section in self._config_data and isinstance(values, dict):
                self._config_data[section].update(values)
    
    def save_config(self):
        """Save current configuration to file"""
        try:
            if self._config_file:
                with open(self._config_file, 'w', encoding='utf-8') as f:
                    json.dump(self._config_data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save config: {e}")
    
    def get_threading_config(self) -> 'ThreadingConfig':
        """Get threading configuration"""
        return ThreadingConfig.from_dict(self._config_data.get('threading', {}))
    
    def get_caching_config(self) -> 'CacheConfig':
        """Get caching configuration"""
        return CacheConfig.from_dict(self._config_data.get('caching', {}))
    
    def get_performance_config(self) -> 'PerformanceConfig':
        """Get performance configuration"""
        return PerformanceConfig.from_dict(self._config_data.get('performance', {}))
    
    def get_compatibility_config(self) -> 'CompatibilityConfig':
        """Get compatibility configuration"""
        return CompatibilityConfig.from_dict(self._config_data.get('compatibility', {}))
    
    def update_section(self, section: str, updates: Dict[str, Any]):
        """Update a configuration section"""
        if section in self._config_data:
            self._config_data[section].update(updates)
            self.save_config()


class ThreadingConfig:
    """Threading-specific configuration"""
    
    def __init__(self):
        # Detect optimal thread counts based on system
        import multiprocessing
        cpu_count = multiprocessing.cpu_count()
        
        self.enabled = True
        self.parse_threads = min(4, max(2, cpu_count // 2))  # Conservative parsing threads
        self.compare_threads = min(2, max(1, cpu_count // 4))  # Comparison threads
        self.io_threads = 2  # Fixed I/O threads
        self.max_files_per_thread = 10  # Batch size per thread
        self.thread_timeout = 300  # 5 minutes timeout per thread
        self.fallback_to_sequential = True  # Auto-fallback on threading issues
        self.memory_limit_mb = 1024  # Memory limit per thread
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ThreadingConfig':
        """Create from dictionary"""
        config = cls()
        for key, value in data.items():
            if hasattr(config, key):
                setattr(config, key, value)
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'enabled': self.enabled,
            'parse_threads': self.parse_threads,
            'compare_threads': self.compare_threads,
            'io_threads': self.io_threads,
            'max_files_per_thread': self.max_files_per_thread,
            'thread_timeout': self.thread_timeout,
            'fallback_to_sequential': self.fallback_to_sequential,
            'memory_limit_mb': self.memory_limit_mb
        }


class CacheConfig:
    """Caching-specific configuration"""
    
    def __init__(self):
        self.enabled = True
        self.cache_dir = str(Path.home() / '.reqif_tool_cache')
        self.max_size_mb = 2048  # 2GB default cache size
        self.max_age_days = 30  # Keep cache for 30 days
        self.compression_level = 6  # Balanced compression
        self.hash_algorithm = 'md5'  # Fast hashing for change detection
        self.cleanup_on_startup = True  # Clean old entries on startup
        self.cache_parsing_results = True  # Cache parsing results
        self.cache_comparison_results = True  # Cache comparison results
        self.cache_file_hashes = True  # Cache file hashes
        self.integrity_check = True  # Verify cache integrity
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CacheConfig':
        """Create from dictionary"""
        config = cls()
        for key, value in data.items():
            if hasattr(config, key):
                setattr(config, key, value)
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'enabled': self.enabled,
            'cache_dir': self.cache_dir,
            'max_size_mb': self.max_size_mb,
            'max_age_days': self.max_age_days,
            'compression_level': self.compression_level,
            'hash_algorithm': self.hash_algorithm,
            'cleanup_on_startup': self.cleanup_on_startup,
            'cache_parsing_results': self.cache_parsing_results,
            'cache_comparison_results': self.cache_comparison_results,
            'cache_file_hashes': self.cache_file_hashes,
            'integrity_check': self.integrity_check
        }


class PerformanceConfig:
    """Performance tuning configuration"""
    
    def __init__(self):
        self.memory_monitoring = True  # Monitor memory usage
        self.performance_logging = False  # Log performance metrics
        self.auto_optimization = True  # Auto-adjust based on system performance
        self.max_memory_usage_mb = 4096  # Maximum memory usage (4GB)
        self.gc_frequency = 50  # Garbage collection frequency (files processed)
        self.progress_update_interval = 0.5  # Progress update interval (seconds)
        self.benchmark_mode = False  # Enable detailed benchmarking
        self.memory_profiling = False  # Enable memory profiling
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PerformanceConfig':
        """Create from dictionary"""
        config = cls()
        for key, value in data.items():
            if hasattr(config, key):
                setattr(config, key, value)
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'memory_monitoring': self.memory_monitoring,
            'performance_logging': self.performance_logging,
            'auto_optimization': self.auto_optimization,
            'max_memory_usage_mb': self.max_memory_usage_mb,
            'gc_frequency': self.gc_frequency,
            'progress_update_interval': self.progress_update_interval,
            'benchmark_mode': self.benchmark_mode,
            'memory_profiling': self.memory_profiling
        }


class CompatibilityConfig:
    """Backward compatibility configuration"""
    
    def __init__(self):
        self.maintain_api_compatibility = True  # Keep existing API signatures
        self.legacy_progress_callbacks = True  # Support old progress callback format
        self.legacy_result_format = True  # Support old result format
        self.sequential_fallback = True  # Fall back to sequential processing if needed
        self.cache_bypass_option = True  # Allow cache bypass for troubleshooting
        self.debug_mode = False  # Enable debug mode for troubleshooting
        self.verbose_logging = False  # Enable verbose logging
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CompatibilityConfig':
        """Create from dictionary"""
        config = cls()
        for key, value in data.items():
            if hasattr(config, key):
                setattr(config, key, value)
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'maintain_api_compatibility': self.maintain_api_compatibility,
            'legacy_progress_callbacks': self.legacy_progress_callbacks,
            'legacy_result_format': self.legacy_result_format,
            'sequential_fallback': self.sequential_fallback,
            'cache_bypass_option': self.cache_bypass_option,
            'debug_mode': self.debug_mode,
            'verbose_logging': self.verbose_logging
        }


# Global configuration instance
config = Config()


def get_config() -> Config:
    """Get global configuration instance"""
    return config


def get_threading_config() -> ThreadingConfig:
    """Get threading configuration"""
    return config.get_threading_config()


def get_caching_config() -> CacheConfig:
    """Get caching configuration"""
    return config.get_caching_config()


def get_performance_config() -> PerformanceConfig:
    """Get performance configuration"""
    return config.get_performance_config()


def get_compatibility_config() -> CompatibilityConfig:
    """Get compatibility configuration"""
    return config.get_compatibility_config()


# Example usage and testing
if __name__ == "__main__":
    print("Testing Configuration Management...")
    
    # Test configuration loading
    cfg = get_config()
    threading_cfg = get_threading_config()
    caching_cfg = get_caching_config()
    
    print(f"Threading enabled: {threading_cfg.enabled}")
    print(f"Parse threads: {threading_cfg.parse_threads}")
    print(f"Caching enabled: {caching_cfg.enabled}")
    print(f"Cache directory: {caching_cfg.cache_dir}")
    
    # Test configuration updates
    cfg.update_section('threading', {'enabled': False})
    updated_threading = get_threading_config()
    print(f"Threading after update: {updated_threading.enabled}")
    
    print("Configuration management ready!")