#!/usr/bin/env python3
"""
Basic Thread Manager for Enhanced ReqIF Tool
FIXED: Threading initialization and import issues
Manages thread pools for parsing and comparison operations with safety and monitoring
"""

import threading
import queue
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, Future, as_completed
from typing import Dict, Any, List, Callable, Optional, Union

# FIXED: Safe imports with fallbacks
try:
    from utils.config import get_threading_config, get_performance_config
except ImportError:
    print("Warning: Utils not available, using default threading configuration")
    
    # Fallback configuration classes
    class DefaultThreadingConfig:
        def __init__(self):
            import multiprocessing
            cpu_count = multiprocessing.cpu_count()
            self.enabled = True
            self.parse_threads = min(4, max(2, cpu_count // 2))
            self.compare_threads = min(2, max(1, cpu_count // 4))
            self.io_threads = 2
            self.thread_timeout = 300
            self.fallback_to_sequential = True
    
    class DefaultPerformanceConfig:
        def __init__(self):
            self.memory_monitoring = True
            self.performance_logging = False
    
    def get_threading_config():
        return DefaultThreadingConfig()
    
    def get_performance_config():
        return DefaultPerformanceConfig()

try:
    from utils.compatibility_layer import register_fallback, should_use_fallback
except ImportError:
    print("Warning: Compatibility layer not available, using fallbacks")
    
    # Simple fallback tracking
    _fallbacks = []
    
    def register_fallback(reason: str):
        _fallbacks.append(reason)
        print(f"Fallback registered: {reason}")
    
    def should_use_fallback(feature: str) -> bool:
        return False  # Default to not using fallbacks


class ThreadSafeCounter:
    """Thread-safe counter for progress tracking"""
    
    def __init__(self, initial_value: int = 0):
        self._value = initial_value
        self._lock = threading.Lock()
    
    def increment(self, delta: int = 1) -> int:
        """Increment counter and return new value"""
        with self._lock:
            self._value += delta
            return self._value
    
    def get_value(self) -> int:
        """Get current value"""
        with self._lock:
            return self._value
    
    def set_value(self, value: int):
        """Set counter value"""
        with self._lock:
            self._value = value


class ThreadMonitor:
    """Monitor thread health and performance"""
    
    def __init__(self):
        self.thread_stats = {}
        self.lock = threading.Lock()
        self.start_time = time.time()
    
    def register_thread(self, thread_id: str, thread_type: str):
        """Register a new thread"""
        with self.lock:
            self.thread_stats[thread_id] = {
                'type': thread_type,
                'start_time': time.time(),
                'tasks_completed': 0,
                'errors': 0,
                'status': 'starting'
            }
    
    def update_thread_status(self, thread_id: str, status: str, tasks_completed: int = None):
        """Update thread status"""
        with self.lock:
            if thread_id in self.thread_stats:
                self.thread_stats[thread_id]['status'] = status
                if tasks_completed is not None:
                    self.thread_stats[thread_id]['tasks_completed'] = tasks_completed
    
    def record_error(self, thread_id: str, error: Exception):
        """Record an error for a thread"""
        with self.lock:
            if thread_id in self.thread_stats:
                self.thread_stats[thread_id]['errors'] += 1
    
    def get_overall_stats(self) -> Dict[str, Any]:
        """Get overall statistics"""
        with self.lock:
            total_threads = len(self.thread_stats)
            active_threads = sum(1 for stats in self.thread_stats.values() 
                               if stats['status'] in ['running', 'working'])
            total_tasks = sum(stats['tasks_completed'] for stats in self.thread_stats.values())
            total_errors = sum(stats['errors'] for stats in self.thread_stats.values())
            
            return {
                'total_threads': total_threads,
                'active_threads': active_threads,
                'total_tasks_completed': total_tasks,
                'total_errors': total_errors,
                'elapsed_time': time.time() - self.start_time
            }


class WorkerThread:
    """Individual worker thread wrapper with monitoring"""
    
    def __init__(self, thread_id: str, thread_type: str, monitor: ThreadMonitor):
        self.thread_id = thread_id
        self.thread_type = thread_type
        self.monitor = monitor
        self.tasks_completed = 0
        
        # Register with monitor
        self.monitor.register_thread(thread_id, thread_type)
    
    def execute_task(self, task_func: Callable, *args, **kwargs) -> Any:
        """Execute a task with monitoring"""
        try:
            self.monitor.update_thread_status(self.thread_id, 'working')
            result = task_func(*args, **kwargs)
            self.tasks_completed += 1
            self.monitor.update_thread_status(self.thread_id, 'completed', self.tasks_completed)
            return result
        except Exception as e:
            self.monitor.record_error(self.thread_id, e)
            self.monitor.update_thread_status(self.thread_id, 'error')
            raise


class ThreadPoolManager:
    """
    Main thread pool manager that orchestrates all threading operations
    FIXED: Improved initialization and error handling
    """
    
    def __init__(self):
        try:
            self.threading_config = get_threading_config()
            self.performance_config = get_performance_config()
        except Exception as e:
            print(f"Warning: Configuration loading failed, using defaults: {e}")
            self.threading_config = DefaultThreadingConfig()
            self.performance_config = DefaultPerformanceConfig()
        
        # Thread pools
        self.parse_pool = None
        self.compare_pool = None
        self.io_pool = None
        
        # Monitoring
        self.monitor = ThreadMonitor()
        self.active = False
        
        # Thread safety
        self.lock = threading.Lock()
        self.shutdown_event = threading.Event()
        
        # Progress tracking
        self.progress_counter = ThreadSafeCounter()
        self.total_tasks = ThreadSafeCounter()
        
        # Initialization flag
        self._initialization_attempted = False
    
    def initialize_pools(self):
        """Initialize thread pools based on configuration with improved error handling"""
        with self.lock:
            if self.active:
                return True
            
            if self._initialization_attempted:
                # Don't keep trying if we've already failed
                return False
            
            self._initialization_attempted = True
            
            try:
                # Check if threading should be disabled
                if not self.threading_config.enabled or should_use_fallback('threading'):
                    register_fallback("Threading disabled by configuration")
                    return False
                
                # Test basic threading functionality first
                if not self._test_threading_capability():
                    register_fallback("Threading capability test failed")
                    return False
                
                # Create thread pools with error handling
                try:
                    self.parse_pool = ThreadPoolExecutor(
                        max_workers=self.threading_config.parse_threads,
                        thread_name_prefix="ReqIF-Parser"
                    )
                    print(f"Created parse pool with {self.threading_config.parse_threads} threads")
                except Exception as e:
                    print(f"Failed to create parse pool: {e}")
                    register_fallback(f"Parse pool creation failed: {e}")
                    return False
                
                try:
                    self.compare_pool = ThreadPoolExecutor(
                        max_workers=self.threading_config.compare_threads,
                        thread_name_prefix="ReqIF-Comparator"
                    )
                    print(f"Created compare pool with {self.threading_config.compare_threads} threads")
                except Exception as e:
                    print(f"Failed to create compare pool: {e}")
                    if self.parse_pool:
                        self.parse_pool.shutdown(wait=False)
                    register_fallback(f"Compare pool creation failed: {e}")
                    return False
                
                try:
                    self.io_pool = ThreadPoolExecutor(
                        max_workers=self.threading_config.io_threads,
                        thread_name_prefix="ReqIF-IO"
                    )
                    print(f"Created IO pool with {self.threading_config.io_threads} threads")
                except Exception as e:
                    print(f"Failed to create IO pool: {e}")
                    if self.parse_pool:
                        self.parse_pool.shutdown(wait=False)
                    if self.compare_pool:
                        self.compare_pool.shutdown(wait=False)
                    register_fallback(f"IO pool creation failed: {e}")
                    return False
                
                self.active = True
                print("Threading system initialized successfully")
                return True
                
            except Exception as e:
                print(f"Threading initialization failed: {e}")
                register_fallback(f"Thread pool initialization failed: {e}")
                self._cleanup_failed_initialization()
                return False
    
    def _test_threading_capability(self) -> bool:
        """Test basic threading capability"""
        try:
            # Simple test to see if we can create and run a thread
            import concurrent.futures
            
            def test_task():
                return "test_success"
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(test_task)
                result = future.result(timeout=5.0)
                return result == "test_success"
                
        except Exception as e:
            print(f"Threading capability test failed: {e}")
            return False
    
    def _cleanup_failed_initialization(self):
        """Cleanup after failed initialization"""
        try:
            if self.parse_pool:
                self.parse_pool.shutdown(wait=False)
                self.parse_pool = None
            if self.compare_pool:
                self.compare_pool.shutdown(wait=False)
                self.compare_pool = None
            if self.io_pool:
                self.io_pool.shutdown(wait=False)
                self.io_pool = None
            self.active = False
        except Exception as e:
            print(f"Cleanup failed: {e}")
    
    def shutdown_pools(self):
        """Shutdown all thread pools gracefully"""
        with self.lock:
            if not self.active:
                return
            
            self.shutdown_event.set()
            
            # Shutdown pools in order
            pools = [
                ("parse_pool", self.parse_pool),
                ("compare_pool", self.compare_pool), 
                ("io_pool", self.io_pool)
            ]
            
            for pool_name, pool in pools:
                if pool:
                    try:
                        print(f"Shutting down {pool_name}...")
                        pool.shutdown(wait=True, timeout=30)
                        print(f"{pool_name} shutdown complete")
                    except Exception as e:
                        print(f"Warning: {pool_name} shutdown error: {e}")
            
            self.parse_pool = None
            self.compare_pool = None
            self.io_pool = None
            self.active = False
            print("All thread pools shut down")
    
    def submit_parse_task(self, task_func: Callable, *args, **kwargs) -> Future:
        """Submit a parsing task to the parse thread pool"""
        if not self.active:
            if not self.initialize_pools():
                raise RuntimeError("Thread pools not available - initialization failed")
        
        if not self.parse_pool:
            raise RuntimeError("Parse thread pool not available")
        
        # Wrap task with monitoring
        thread_id = f"parse-{threading.get_ident()}-{time.time()}"
        worker = WorkerThread(thread_id, "parse", self.monitor)
        
        def monitored_task():
            return worker.execute_task(task_func, *args, **kwargs)
        
        return self.parse_pool.submit(monitored_task)
    
    def submit_compare_task(self, task_func: Callable, *args, **kwargs) -> Future:
        """Submit a comparison task to the compare thread pool"""
        if not self.active:
            if not self.initialize_pools():
                raise RuntimeError("Thread pools not available - initialization failed")
        
        if not self.compare_pool:
            raise RuntimeError("Compare thread pool not available")
        
        # Wrap task with monitoring
        thread_id = f"compare-{threading.get_ident()}-{time.time()}"
        worker = WorkerThread(thread_id, "compare", self.monitor)
        
        def monitored_task():
            return worker.execute_task(task_func, *args, **kwargs)
        
        return self.compare_pool.submit(monitored_task)
    
    def submit_io_task(self, task_func: Callable, *args, **kwargs) -> Future:
        """Submit an I/O task to the I/O thread pool"""
        if not self.active:
            if not self.initialize_pools():
                raise RuntimeError("Thread pools not available - initialization failed")
        
        if not self.io_pool:
            raise RuntimeError("IO thread pool not available")
        
        # Wrap task with monitoring
        thread_id = f"io-{threading.get_ident()}-{time.time()}"
        worker = WorkerThread(thread_id, "io", self.monitor)
        
        def monitored_task():
            return worker.execute_task(task_func, *args, **kwargs)
        
        return self.io_pool.submit(monitored_task)
    
    def execute_batch_parse(self, parse_tasks: List[tuple], progress_callback: Optional[Callable] = None) -> List[Any]:
        """Execute a batch of parsing tasks in parallel with improved error handling"""
        if not parse_tasks:
            return []
        
        if not self.initialize_pools():
            # Fallback to sequential execution
            print("Threading not available, falling back to sequential execution")
            return self._execute_sequential_parse(parse_tasks, progress_callback)
        
        results = []
        futures = []
        
        try:
            # Submit all tasks
            for task_func, args, kwargs in parse_tasks:
                try:
                    future = self.submit_parse_task(task_func, *args, **kwargs)
                    futures.append(future)
                except Exception as e:
                    print(f"Failed to submit parse task: {e}")
                    futures.append(None)  # Placeholder for failed submission
            
            # Collect results with progress tracking
            completed_count = 0
            for i, future in enumerate(futures):
                try:
                    if future is None:
                        # Failed submission
                        results.append(None)
                        completed_count += 1
                        continue
                    
                    result = future.result(timeout=self.threading_config.thread_timeout)
                    results.append(result)
                    completed_count += 1
                    
                    # Update progress
                    if progress_callback:
                        try:
                            progress_callback(completed_count, len(futures), f"Parsed {completed_count}/{len(futures)} files")
                        except Exception as e:
                            print(f"Progress callback error: {e}")
                
                except Exception as e:
                    print(f"Parse task failed: {e}")
                    results.append(None)  # Placeholder for failed task
                    completed_count += 1
            
            return results
            
        except Exception as e:
            print(f"Batch parse execution failed: {e}")
            register_fallback(f"Batch parse execution failed: {e}")
            
            # Cancel remaining futures
            for future in futures:
                if future:
                    try:
                        future.cancel()
                    except:
                        pass
            
            # Fallback to sequential
            return self._execute_sequential_parse(parse_tasks, progress_callback)
    
    def execute_batch_compare(self, compare_tasks: List[tuple], progress_callback: Optional[Callable] = None) -> List[Any]:
        """Execute a batch of comparison tasks in parallel with improved error handling"""
        if not compare_tasks:
            return []
        
        if not self.initialize_pools():
            # Fallback to sequential execution
            print("Threading not available, falling back to sequential execution")
            return self._execute_sequential_compare(compare_tasks, progress_callback)
        
        results = []
        futures = []
        
        try:
            # Submit all tasks
            for task_func, args, kwargs in compare_tasks:
                try:
                    future = self.submit_compare_task(task_func, *args, **kwargs)
                    futures.append(future)
                except Exception as e:
                    print(f"Failed to submit compare task: {e}")
                    futures.append(None)  # Placeholder for failed submission
            
            # Collect results with progress tracking
            completed_count = 0
            for i, future in enumerate(futures):
                try:
                    if future is None:
                        # Failed submission
                        results.append(None)
                        completed_count += 1
                        continue
                    
                    result = future.result(timeout=self.threading_config.thread_timeout)
                    results.append(result)
                    completed_count += 1
                    
                    # Update progress
                    if progress_callback:
                        try:
                            progress_callback(completed_count, len(futures), f"Compared {completed_count}/{len(futures)} pairs")
                        except Exception as e:
                            print(f"Progress callback error: {e}")
                
                except Exception as e:
                    print(f"Compare task failed: {e}")
                    results.append(None)  # Placeholder for failed task
                    completed_count += 1
            
            return results
            
        except Exception as e:
            print(f"Batch compare execution failed: {e}")
            register_fallback(f"Batch compare execution failed: {e}")
            
            # Cancel remaining futures
            for future in futures:
                if future:
                    try:
                        future.cancel()
                    except:
                        pass
            
            # Fallback to sequential
            return self._execute_sequential_compare(compare_tasks, progress_callback)
    
    def _execute_sequential_parse(self, parse_tasks: List[tuple], progress_callback: Optional[Callable] = None) -> List[Any]:
        """Fallback sequential parsing execution"""
        results = []
        
        for i, (task_func, args, kwargs) in enumerate(parse_tasks):
            try:
                result = task_func(*args, **kwargs)
                results.append(result)
                
                if progress_callback:
                    try:
                        progress_callback(i + 1, len(parse_tasks), f"Parsed {i + 1}/{len(parse_tasks)} files (sequential)")
                    except Exception as e:
                        print(f"Progress callback error: {e}")
            
            except Exception as e:
                print(f"Sequential parse task failed: {e}")
                results.append(None)
        
        return results
    
    def _execute_sequential_compare(self, compare_tasks: List[tuple], progress_callback: Optional[Callable] = None) -> List[Any]:
        """Fallback sequential comparison execution"""
        results = []
        
        for i, (task_func, args, kwargs) in enumerate(compare_tasks):
            try:
                result = task_func(*args, **kwargs)
                results.append(result)
                
                if progress_callback:
                    try:
                        progress_callback(i + 1, len(compare_tasks), f"Compared {i + 1}/{len(compare_tasks)} pairs (sequential)")
                    except Exception as e:
                        print(f"Progress callback error: {e}")
            
            except Exception as e:
                print(f"Sequential compare task failed: {e}")
                results.append(None)
        
        return results
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        monitor_stats = self.monitor.get_overall_stats()
        
        return {
            'threading_enabled': self.active,
            'pools_initialized': bool(self.parse_pool and self.compare_pool and self.io_pool),
            'initialization_attempted': self._initialization_attempted,
            'configuration': {
                'parse_threads': getattr(self.threading_config, 'parse_threads', 0),
                'compare_threads': getattr(self.threading_config, 'compare_threads', 0),
                'io_threads': getattr(self.threading_config, 'io_threads', 0),
            },
            'monitor_stats': monitor_stats,
            'progress': {
                'completed_tasks': self.progress_counter.get_value(),
                'total_tasks': self.total_tasks.get_value()
            }
        }
    
    def is_healthy(self) -> bool:
        """Check if thread manager is in healthy state"""
        if not self.active:
            return True  # Not active is considered healthy (sequential mode)
        
        # Check if pools exist
        if not (self.parse_pool and self.compare_pool and self.io_pool):
            return False
        
        try:
            stats = self.monitor.get_overall_stats()
            
            # Check for excessive errors
            if stats['total_errors'] > 0 and stats['total_tasks_completed'] > 0:
                error_rate = stats['total_errors'] / stats['total_tasks_completed']
                if error_rate > 0.1:  # More than 10% error rate
                    return False
            
            # Check if pools are responsive with a simple test
            def simple_test():
                return True
            
            if self.parse_pool:
                test_future = self.parse_pool.submit(simple_test)
                test_future.result(timeout=1.0)
            
            return True
            
        except Exception as e:
            print(f"Health check failed: {e}")
            return False


# Global thread manager instance
_thread_manager = None
_thread_manager_lock = threading.Lock()


def get_thread_manager() -> ThreadPoolManager:
    """Get global thread manager instance (singleton)"""
    global _thread_manager
    
    with _thread_manager_lock:
        if _thread_manager is None:
            _thread_manager = ThreadPoolManager()
        return _thread_manager


def shutdown_threading():
    """Shutdown global thread manager"""
    global _thread_manager
    
    with _thread_manager_lock:
        if _thread_manager:
            _thread_manager.shutdown_pools()
            _thread_manager = None


# Convenience functions for easy access
def submit_parse_task(task_func: Callable, *args, **kwargs) -> Future:
    """Submit parsing task to global thread manager"""
    try:
        return get_thread_manager().submit_parse_task(task_func, *args, **kwargs)
    except Exception as e:
        print(f"Failed to submit parse task: {e}")
        raise


def submit_compare_task(task_func: Callable, *args, **kwargs) -> Future:
    """Submit comparison task to global thread manager"""
    try:
        return get_thread_manager().submit_compare_task(task_func, *args, **kwargs)
    except Exception as e:
        print(f"Failed to submit compare task: {e}")
        raise


def execute_parallel_parse(parse_tasks: List[tuple], progress_callback: Optional[Callable] = None) -> List[Any]:
    """Execute parsing tasks in parallel"""
    try:
        return get_thread_manager().execute_batch_parse(parse_tasks, progress_callback)
    except Exception as e:
        print(f"Parallel parse execution failed: {e}")
        # Return empty list as fallback
        return [None] * len(parse_tasks) if parse_tasks else []


def execute_parallel_compare(compare_tasks: List[tuple], progress_callback: Optional[Callable] = None) -> List[Any]:
    """Execute comparison tasks in parallel"""
    try:
        return get_thread_manager().execute_batch_compare(compare_tasks, progress_callback)
    except Exception as e:
        print(f"Parallel compare execution failed: {e}")
        # Return empty list as fallback
        return [None] * len(compare_tasks) if compare_tasks else []


def get_threading_stats() -> Dict[str, Any]:
    """Get threading performance statistics"""
    try:
        return get_thread_manager().get_performance_stats()
    except Exception as e:
        print(f"Failed to get threading stats: {e}")
        return {
            'threading_enabled': False,
            'pools_initialized': False,
            'error': str(e)
        }


def is_threading_healthy() -> bool:
    """Check if threading system is healthy"""
    try:
        return get_thread_manager().is_healthy()
    except Exception as e:
        print(f"Threading health check failed: {e}")
        return False


# Context manager for thread safety
class ThreadingContext:
    """Context manager for threading operations"""
    
    def __init__(self):
        self.manager = None
    
    def __enter__(self):
        try:
            self.manager = get_thread_manager()
            if not self.manager.initialize_pools():
                print("Warning: Threading initialization failed, will use sequential processing")
            return self.manager
        except Exception as e:
            print(f"Threading context setup failed: {e}")
            raise RuntimeError("Failed to initialize threading context")
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Don't shutdown pools here - let them persist for reuse
        # Only shutdown on application exit
        pass


# Testing and validation functions
def validate_threading():
    """Validate that threading system is working correctly"""
    test_results = {
        'manager_creation': False,
        'initialization': False,
        'parse_submission': False,
        'compare_submission': False,
        'batch_execution': False,
        'monitoring': False,
        'health_check': False
    }
    
    try:
        # Test manager creation
        manager = get_thread_manager()
        test_results['manager_creation'] = manager is not None
    except Exception as e:
        print(f"Manager creation test failed: {e}")
        return test_results
    
    try:
        # Test initialization
        test_results['initialization'] = manager.initialize_pools()
        if not test_results['initialization']:
            print("Threading initialization failed, but this may be expected in some environments")
            # Continue with other tests even if initialization fails
    except Exception as e:
        print(f"Threading initialization test failed: {e}")
    
    # Only run remaining tests if initialization succeeded
    if test_results['initialization']:
        try:
            # Test task submission
            def dummy_parse_task():
                return "parse_result"
            
            future = manager.submit_parse_task(dummy_parse_task)
            result = future.result(timeout=5.0)
            test_results['parse_submission'] = result == "parse_result"
        except Exception as e:
            print(f"Parse task submission test failed: {e}")
        
        try:
            # Test compare task submission
            def dummy_compare_task():
                return "compare_result"
            
            future = manager.submit_compare_task(dummy_compare_task)
            result = future.result(timeout=5.0)
            test_results['compare_submission'] = result == "compare_result"
        except Exception as e:
            print(f"Compare task submission test failed: {e}")
        
        try:
            # Test batch execution
            def dummy_task(value):
                return f"result_{value}"
            
            tasks = [(dummy_task, (i,), {}) for i in range(3)]
            results = manager.execute_batch_parse(tasks)
            test_results['batch_execution'] = len(results) == 3 and all(r is not None for r in results)
        except Exception as e:
            print(f"Batch execution test failed: {e}")
        
        try:
            # Test health check
            test_results['health_check'] = manager.is_healthy()
        except Exception as e:
            print(f"Health check test failed: {e}")
    
    try:
        # Test monitoring (should work even without active pools)
        stats = manager.get_performance_stats()
        test_results['monitoring'] = 'threading_enabled' in stats
    except Exception as e:
        print(f"Monitoring test failed: {e}")
    
    return test_results


# Example usage and testing
if __name__ == "__main__":
    print("Testing Fixed Thread Manager...")
    
    # Run validation tests
    results = validate_threading()
    print("Validation Results:")
    for test, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {test}: {status}")
    
    # Test threading context
    try:
        with ThreadingContext() as manager:
            print(f"Threading context active: {manager.active}")
            
            # Test performance stats
            stats = get_threading_stats()
            print(f"Threading stats: {stats}")
    except Exception as e:
        print(f"Threading context test failed: {e}")
    
    # Show final status
    overall_success = sum(results.values()) >= len(results) * 0.6  # 60% pass rate
    print(f"\nOverall threading system status: {'✅ READY' if overall_success else '⚠️ LIMITED'}")
    
    if not overall_success:
        print("Note: Limited threading functionality detected. Application will use sequential processing.")
    
    print("Fixed thread manager ready!")