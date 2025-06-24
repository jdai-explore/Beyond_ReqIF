#!/usr/bin/env python3
"""
Threading Package for Enhanced ReqIF Tool
Provides thread pool management, task queuing, and progress aggregation
"""

# Import main threading components
from .thread_manager import (
    ThreadPoolManager,
    get_thread_manager,
    submit_parse_task,
    submit_compare_task,
    execute_parallel_parse,
    execute_parallel_compare,
    get_threading_stats,
    is_threading_healthy,
    shutdown_threading,
    ThreadingContext
)

from .task_queue import (
    TaskPriority,
    TaskStatus,
    TaskResult,
    ParseTask,
    CompareTask,
    IOTask,
    TaskQueue,
    TaskScheduler,
    ResultCollector,
    get_task_scheduler,
    get_result_collector,
    create_parse_task,
    create_compare_task,
    create_io_task,
    clear_task_system
)

# Version information
__version__ = "1.0.0-phase1a"
__author__ = "ReqIF Tool Suite Team"

# Package-level configuration
DEFAULT_PARSE_THREADS = 4
DEFAULT_COMPARE_THREADS = 2
DEFAULT_IO_THREADS = 2

# Public API
__all__ = [
    # Thread Manager
    'ThreadPoolManager',
    'get_thread_manager',
    'submit_parse_task',
    'submit_compare_task',
    'execute_parallel_parse',
    'execute_parallel_compare',
    'get_threading_stats',
    'is_threading_healthy',
    'shutdown_threading',
    'ThreadingContext',
    
    # Task System
    'TaskPriority',
    'TaskStatus',
    'TaskResult',
    'ParseTask',
    'CompareTask',
    'IOTask',
    'TaskQueue',
    'TaskScheduler',
    'ResultCollector',
    'get_task_scheduler',
    'get_result_collector',
    'create_parse_task',
    'create_compare_task',
    'create_io_task',
    'clear_task_system',
    
    # Constants
    'DEFAULT_PARSE_THREADS',
    'DEFAULT_COMPARE_THREADS',
    'DEFAULT_IO_THREADS'
]


def initialize_threading_system():
    """Initialize the threading system with default configuration"""
    try:
        manager = get_thread_manager()
        success = manager.initialize_pools()
        
        if success:
            print("Threading system initialized successfully")
            return True
        else:
            print("Threading system initialization failed - falling back to sequential processing")
            return False
    except Exception as e:
        print(f"Threading system initialization error: {e}")
        return False


def get_threading_info():
    """Get information about the current threading configuration"""
    from utils.config import get_threading_config
    
    config = get_threading_config()
    manager = get_thread_manager()
    
    return {
        'threading_enabled': config.enabled,
        'parse_threads': config.parse_threads,
        'compare_threads': config.compare_threads,
        'io_threads': config.io_threads,
        'thread_pools_active': manager.active,
        'threading_healthy': is_threading_healthy(),
        'version': __version__
    }


def validate_threading_system():
    """Validate that the threading system is working correctly"""
    try:
        # Import validation functions
        from .thread_manager import validate_threading
        from .task_queue import validate_task_system
        
        # Run validations
        threading_results = validate_threading()
        task_results = validate_task_system()
        
        # Combine results
        all_results = {**threading_results, **task_results}
        
        # Check overall success
        all_passed = all(all_results.values())
        
        return {
            'overall_success': all_passed,
            'individual_tests': all_results,
            'failed_tests': [test for test, passed in all_results.items() if not passed]
        }
        
    except Exception as e:
        return {
            'overall_success': False,
            'error': str(e),
            'individual_tests': {},
            'failed_tests': ['validation_error']
        }


# Optional: Auto-initialize on import (can be disabled by setting environment variable)
import os
if os.getenv('REQIF_THREADING_AUTO_INIT', 'true').lower() == 'true':
    try:
        initialize_threading_system()
    except Exception as e:
        print(f"Auto-initialization failed: {e}")