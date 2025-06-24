#!/usr/bin/env python3
"""
Task Queue System for Enhanced ReqIF Tool
Manages task distribution, scheduling, and result collection with priority support
"""

import threading
import queue
import time
import uuid
from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, List, Callable, Optional, Union, Tuple
from concurrent.futures import Future
from utils.config import get_threading_config


class TaskPriority(Enum):
    """Task priority levels"""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    RUNNING = "running" 
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class TaskResult:
    """Standardized task result container"""
    task_id: str
    status: TaskStatus
    result: Any = None
    error: Optional[Exception] = None
    execution_time: float = 0.0
    thread_id: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def is_successful(self) -> bool:
        """Check if task completed successfully"""
        return self.status == TaskStatus.COMPLETED and self.error is None
    
    def get_result_or_raise(self) -> Any:
        """Get result or raise the error if task failed"""
        if self.error:
            raise self.error
        return self.result


class BaseTask:
    """Base class for all tasks"""
    
    def __init__(self, task_id: str = None, priority: TaskPriority = TaskPriority.NORMAL):
        self.task_id = task_id or str(uuid.uuid4())
        self.priority = priority
        self.created_time = time.time()
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.status = TaskStatus.PENDING
        self.metadata: Dict[str, Any] = {}
    
    def execute(self) -> Any:
        """Execute the task - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement execute method")
    
    def get_execution_time(self) -> float:
        """Get task execution time"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0
    
    def get_wait_time(self) -> float:
        """Get time spent waiting in queue"""
        if self.start_time:
            return self.start_time - self.created_time
        return time.time() - self.created_time
    
    def __lt__(self, other):
        """For priority queue ordering"""
        if isinstance(other, BaseTask):
            return self.priority.value > other.priority.value  # Higher priority first
        return False


class ParseTask(BaseTask):
    """File parsing task"""
    
    def __init__(self, file_path: str, parser_func: Callable, 
                 task_id: str = None, priority: TaskPriority = TaskPriority.NORMAL,
                 parser_args: tuple = None, parser_kwargs: dict = None):
        super().__init__(task_id, priority)
        self.file_path = file_path
        self.parser_func = parser_func
        self.parser_args = parser_args or ()
        self.parser_kwargs = parser_kwargs or {}
        self.metadata['task_type'] = 'parse'
        self.metadata['file_path'] = file_path
    
    def execute(self) -> Any:
        """Execute the parsing task"""
        self.start_time = time.time()
        self.status = TaskStatus.RUNNING
        
        try:
            result = self.parser_func(self.file_path, *self.parser_args, **self.parser_kwargs)
            self.status = TaskStatus.COMPLETED
            self.end_time = time.time()
            return result
        except Exception as e:
            self.status = TaskStatus.FAILED
            self.end_time = time.time()
            raise e


class CompareTask(BaseTask):
    """File comparison task"""
    
    def __init__(self, file1_data: Any, file2_data: Any, comparator_func: Callable,
                 task_id: str = None, priority: TaskPriority = TaskPriority.NORMAL,
                 comparator_args: tuple = None, comparator_kwargs: dict = None):
        super().__init__(task_id, priority)
        self.file1_data = file1_data
        self.file2_data = file2_data
        self.comparator_func = comparator_func
        self.comparator_args = comparator_args or ()
        self.comparator_kwargs = comparator_kwargs or {}
        self.metadata['task_type'] = 'compare'
    
    def execute(self) -> Any:
        """Execute the comparison task"""
        self.start_time = time.time()
        self.status = TaskStatus.RUNNING
        
        try:
            result = self.comparator_func(self.file1_data, self.file2_data, 
                                        *self.comparator_args, **self.comparator_kwargs)
            self.status = TaskStatus.COMPLETED
            self.end_time = time.time()
            return result
        except Exception as e:
            self.status = TaskStatus.FAILED
            self.end_time = time.time()
            raise e


class IOTask(BaseTask):
    """I/O operation task (caching, file operations)"""
    
    def __init__(self, io_func: Callable, operation_type: str,
                 task_id: str = None, priority: TaskPriority = TaskPriority.NORMAL,
                 io_args: tuple = None, io_kwargs: dict = None):
        super().__init__(task_id, priority)
        self.io_func = io_func
        self.operation_type = operation_type
        self.io_args = io_args or ()
        self.io_kwargs = io_kwargs or {}
        self.metadata['task_type'] = 'io'
        self.metadata['operation_type'] = operation_type
    
    def execute(self) -> Any:
        """Execute the I/O task"""
        self.start_time = time.time()
        self.status = TaskStatus.RUNNING
        
        try:
            result = self.io_func(*self.io_args, **self.io_kwargs)
            self.status = TaskStatus.COMPLETED
            self.end_time = time.time()
            return result
        except Exception as e:
            self.status = TaskStatus.FAILED
            self.end_time = time.time()
            raise e


class TaskQueue:
    """Priority-based task queue with thread-safe operations"""
    
    def __init__(self, maxsize: int = 0):
        self._queue = queue.PriorityQueue(maxsize)
        self._task_registry: Dict[str, BaseTask] = {}
        self._lock = threading.Lock()
        self._stats = {
            'tasks_queued': 0,
            'tasks_completed': 0,
            'tasks_failed': 0,
            'total_wait_time': 0.0,
            'total_execution_time': 0.0
        }
    
    def put_task(self, task: BaseTask, block: bool = True, timeout: Optional[float] = None):
        """Add a task to the queue"""
        with self._lock:
            self._task_registry[task.task_id] = task
            self._stats['tasks_queued'] += 1
        
        self._queue.put(task, block, timeout)
    
    def get_task(self, block: bool = True, timeout: Optional[float] = None) -> Optional[BaseTask]:
        """Get next task from the queue"""
        try:
            task = self._queue.get(block, timeout)
            return task
        except queue.Empty:
            return None
    
    def task_done(self, task: BaseTask, result: TaskResult):
        """Mark task as completed and update statistics"""
        with self._lock:
            if task.task_id in self._task_registry:
                self._task_registry[task.task_id] = task
                
                # Update statistics
                if result.is_successful():
                    self._stats['tasks_completed'] += 1
                else:
                    self._stats['tasks_failed'] += 1
                
                self._stats['total_wait_time'] += task.get_wait_time()
                self._stats['total_execution_time'] += task.get_execution_time()
        
        self._queue.task_done()
    
    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """Get status of a specific task"""
        with self._lock:
            task = self._task_registry.get(task_id)
            return task.status if task else None
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get queue statistics"""
        with self._lock:
            stats = self._stats.copy()
            stats['queue_size'] = self._queue.qsize()
            stats['tasks_in_registry'] = len(self._task_registry)
            
            # Calculate averages
            if stats['tasks_completed'] > 0:
                stats['avg_wait_time'] = stats['total_wait_time'] / stats['tasks_completed']
                stats['avg_execution_time'] = stats['total_execution_time'] / stats['tasks_completed']
            else:
                stats['avg_wait_time'] = 0.0
                stats['avg_execution_time'] = 0.0
            
            return stats
    
    def clear(self):
        """Clear the queue and registry"""
        with self._lock:
            # Clear the queue
            while not self._queue.empty():
                try:
                    self._queue.get_nowait()
                    self._queue.task_done()
                except queue.Empty:
                    break
            
            # Clear registry
            self._task_registry.clear()
            
            # Reset statistics
            self._stats = {
                'tasks_queued': 0,
                'tasks_completed': 0,
                'tasks_failed': 0,
                'total_wait_time': 0.0,
                'total_execution_time': 0.0
            }


class TaskScheduler:
    """Intelligent task distribution and scheduling"""
    
    def __init__(self):
        self.threading_config = get_threading_config()
        
        # Separate queues for different task types
        self.parse_queue = TaskQueue()
        self.compare_queue = TaskQueue()
        self.io_queue = TaskQueue()
        
        # Scheduling statistics
        self.scheduling_stats = {
            'tasks_scheduled': 0,
            'batches_created': 0,
            'load_balancing_adjustments': 0
        }
        
        self._lock = threading.Lock()
    
    def schedule_parse_tasks(self, file_paths: List[str], parser_func: Callable,
                           parser_args: tuple = None, parser_kwargs: dict = None) -> List[str]:
        """Schedule multiple parsing tasks and return task IDs"""
        task_ids = []
        
        for file_path in file_paths:
            task = ParseTask(
                file_path=file_path,
                parser_func=parser_func,
                parser_args=parser_args,
                parser_kwargs=parser_kwargs,
                priority=self._determine_parse_priority(file_path)
            )
            
            self.parse_queue.put_task(task)
            task_ids.append(task.task_id)
        
        with self._lock:
            self.scheduling_stats['tasks_scheduled'] += len(file_paths)
        
        return task_ids
    
    def schedule_compare_tasks(self, comparison_pairs: List[Tuple[Any, Any]], 
                             comparator_func: Callable,
                             comparator_args: tuple = None, 
                             comparator_kwargs: dict = None) -> List[str]:
        """Schedule multiple comparison tasks and return task IDs"""
        task_ids = []
        
        for file1_data, file2_data in comparison_pairs:
            task = CompareTask(
                file1_data=file1_data,
                file2_data=file2_data,
                comparator_func=comparator_func,
                comparator_args=comparator_args,
                comparator_kwargs=comparator_kwargs,
                priority=self._determine_compare_priority(file1_data, file2_data)
            )
            
            self.compare_queue.put_task(task)
            task_ids.append(task.task_id)
        
        with self._lock:
            self.scheduling_stats['tasks_scheduled'] += len(comparison_pairs)
        
        return task_ids
    
    def create_parse_batches(self, file_paths: List[str], batch_size: int = None) -> List[List[str]]:
        """Create optimized batches for parsing tasks"""
        if batch_size is None:
            batch_size = self.threading_config.max_files_per_thread
        
        batches = []
        for i in range(0, len(file_paths), batch_size):
            batch = file_paths[i:i + batch_size]
            batches.append(batch)
        
        with self._lock:
            self.scheduling_stats['batches_created'] += len(batches)
        
        return batches
    
    def create_comparison_batches(self, comparison_pairs: List[Tuple[Any, Any]], 
                                 batch_size: int = None) -> List[List[Tuple[Any, Any]]]:
        """Create optimized batches for comparison tasks"""
        if batch_size is None:
            batch_size = self.threading_config.max_files_per_thread // 2  # Comparisons are more memory intensive
        
        batches = []
        for i in range(0, len(comparison_pairs), batch_size):
            batch = comparison_pairs[i:i + batch_size]
            batches.append(batch)
        
        with self._lock:
            self.scheduling_stats['batches_created'] += len(batches)
        
        return batches
    
    def _determine_parse_priority(self, file_path: str) -> TaskPriority:
        """Determine priority for parsing task based on file characteristics"""
        # Simple heuristics - can be enhanced based on file size, type, etc.
        import os
        
        try:
            file_size = os.path.getsize(file_path)
            
            # Prioritize smaller files first (faster processing)
            if file_size < 1024 * 1024:  # < 1MB
                return TaskPriority.HIGH
            elif file_size < 10 * 1024 * 1024:  # < 10MB
                return TaskPriority.NORMAL
            else:
                return TaskPriority.LOW
        except:
            return TaskPriority.NORMAL
    
    def _determine_compare_priority(self, file1_data: Any, file2_data: Any) -> TaskPriority:
        """Determine priority for comparison task"""
        # Simple heuristics - can be enhanced based on data size, complexity, etc.
        try:
            # Prioritize based on data size (smaller comparisons first)
            if hasattr(file1_data, '__len__') and hasattr(file2_data, '__len__'):
                total_size = len(file1_data) + len(file2_data)
                
                if total_size < 100:  # Small datasets
                    return TaskPriority.HIGH
                elif total_size < 1000:  # Medium datasets
                    return TaskPriority.NORMAL
                else:  # Large datasets
                    return TaskPriority.LOW
        except:
            pass
        
        return TaskPriority.NORMAL
    
    def get_queue_statistics(self) -> Dict[str, Any]:
        """Get comprehensive queue statistics"""
        return {
            'parse_queue': self.parse_queue.get_statistics(),
            'compare_queue': self.compare_queue.get_statistics(),
            'io_queue': self.io_queue.get_statistics(),
            'scheduling_stats': self.scheduling_stats.copy()
        }
    
    def clear_all_queues(self):
        """Clear all task queues"""
        self.parse_queue.clear()
        self.compare_queue.clear()
        self.io_queue.clear()
        
        with self._lock:
            self.scheduling_stats = {
                'tasks_scheduled': 0,
                'batches_created': 0,
                'load_balancing_adjustments': 0
            }


class ResultCollector:
    """Thread-safe result collection and aggregation"""
    
    def __init__(self):
        self._results: Dict[str, TaskResult] = {}
        self._lock = threading.Lock()
        self._completion_callbacks: List[Callable] = []
    
    def add_result(self, task_result: TaskResult):
        """Add a task result"""
        with self._lock:
            self._results[task_result.task_id] = task_result
            
            # Trigger completion callbacks
            for callback in self._completion_callbacks:
                try:
                    callback(task_result)
                except Exception as e:
                    print(f"Completion callback error: {e}")
    
    def get_result(self, task_id: str) -> Optional[TaskResult]:
        """Get result for a specific task"""
        with self._lock:
            return self._results.get(task_id)
    
    def get_all_results(self) -> Dict[str, TaskResult]:
        """Get all results"""
        with self._lock:
            return self._results.copy()
    
    def get_successful_results(self) -> Dict[str, TaskResult]:
        """Get only successful results"""
        with self._lock:
            return {task_id: result for task_id, result in self._results.items() 
                   if result.is_successful()}
    
    def get_failed_results(self) -> Dict[str, TaskResult]:
        """Get only failed results"""
        with self._lock:
            return {task_id: result for task_id, result in self._results.items() 
                   if not result.is_successful()}
    
    def wait_for_results(self, task_ids: List[str], timeout: float = None) -> Dict[str, TaskResult]:
        """Wait for specific task results"""
        start_time = time.time()
        collected_results = {}
        
        while len(collected_results) < len(task_ids):
            with self._lock:
                for task_id in task_ids:
                    if task_id in self._results and task_id not in collected_results:
                        collected_results[task_id] = self._results[task_id]
            
            # Check timeout
            if timeout and (time.time() - start_time) > timeout:
                break
            
            # Short sleep to avoid busy waiting
            time.sleep(0.01)
        
        return collected_results
    
    def add_completion_callback(self, callback: Callable[[TaskResult], None]):
        """Add callback to be called when any task completes"""
        with self._lock:
            self._completion_callbacks.append(callback)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get collection statistics"""
        with self._lock:
            total_results = len(self._results)
            successful_results = sum(1 for r in self._results.values() if r.is_successful())
            failed_results = total_results - successful_results
            
            total_execution_time = sum(r.execution_time for r in self._results.values())
            avg_execution_time = total_execution_time / total_results if total_results > 0 else 0
            
            return {
                'total_results': total_results,
                'successful_results': successful_results,
                'failed_results': failed_results,
                'success_rate': successful_results / total_results if total_results > 0 else 0,
                'total_execution_time': total_execution_time,
                'avg_execution_time': avg_execution_time
            }
    
    def clear(self):
        """Clear all results"""
        with self._lock:
            self._results.clear()
            self._completion_callbacks.clear()


# Convenience functions for task creation
def create_parse_task(file_path: str, parser_func: Callable, 
                     priority: TaskPriority = TaskPriority.NORMAL,
                     **kwargs) -> ParseTask:
    """Create a parsing task"""
    return ParseTask(
        file_path=file_path,
        parser_func=parser_func,
        priority=priority,
        parser_args=kwargs.get('parser_args', ()),
        parser_kwargs=kwargs.get('parser_kwargs', {})
    )


def create_compare_task(file1_data: Any, file2_data: Any, comparator_func: Callable,
                       priority: TaskPriority = TaskPriority.NORMAL,
                       **kwargs) -> CompareTask:
    """Create a comparison task"""
    return CompareTask(
        file1_data=file1_data,
        file2_data=file2_data,
        comparator_func=comparator_func,
        priority=priority,
        comparator_args=kwargs.get('comparator_args', ()),
        comparator_kwargs=kwargs.get('comparator_kwargs', {})
    )


def create_io_task(io_func: Callable, operation_type: str,
                  priority: TaskPriority = TaskPriority.NORMAL,
                  **kwargs) -> IOTask:
    """Create an I/O task"""
    return IOTask(
        io_func=io_func,
        operation_type=operation_type,
        priority=priority,
        io_args=kwargs.get('io_args', ()),
        io_kwargs=kwargs.get('io_kwargs', {})
    )


# Global instances
_task_scheduler = None
_result_collector = None
_scheduler_lock = threading.Lock()


def get_task_scheduler() -> TaskScheduler:
    """Get global task scheduler instance"""
    global _task_scheduler
    
    with _scheduler_lock:
        if _task_scheduler is None:
            _task_scheduler = TaskScheduler()
        return _task_scheduler


def get_result_collector() -> ResultCollector:
    """Get global result collector instance"""
    global _result_collector
    
    with _scheduler_lock:
        if _result_collector is None:
            _result_collector = ResultCollector()
        return _result_collector


def clear_task_system():
    """Clear global task system"""
    global _task_scheduler, _result_collector
    
    with _scheduler_lock:
        if _task_scheduler:
            _task_scheduler.clear_all_queues()
        if _result_collector:
            _result_collector.clear()


# Testing and validation functions
def validate_task_system():
    """Validate that task system is working correctly"""
    test_results = {
        'task_creation': False,
        'task_execution': False,
        'priority_ordering': False,
        'result_collection': False,
        'statistics': False
    }
    
    try:
        # Test task creation
        def dummy_parser(file_path):
            return f"parsed_{file_path}"
        
        task = create_parse_task("/test/file.reqif", dummy_parser)
        test_results['task_creation'] = isinstance(task, ParseTask)
    except Exception as e:
        print(f"Task creation test failed: {e}")
    
    try:
        # Test task execution
        result = task.execute()
        test_results['task_execution'] = result == "parsed_/test/file.reqif"
    except Exception as e:
        print(f"Task execution test failed: {e}")
    
    try:
        # Test priority ordering
        high_task = create_parse_task("/high.reqif", dummy_parser, TaskPriority.HIGH)
        low_task = create_parse_task("/low.reqif", dummy_parser, TaskPriority.LOW)
        
        # High priority should be "less than" low priority (for min-heap)
        test_results['priority_ordering'] = high_task < low_task
    except Exception as e:
        print(f"Priority ordering test failed: {e}")
    
    try:
        # Test result collection
        collector = get_result_collector()
        task_result = TaskResult(
            task_id="test_task",
            status=TaskStatus.COMPLETED,
            result="test_result"
        )
        
        collector.add_result(task_result)
        retrieved = collector.get_result("test_task")
        test_results['result_collection'] = retrieved is not None and retrieved.result == "test_result"
    except Exception as e:
        print(f"Result collection test failed: {e}")
    
    try:
        # Test statistics
        stats = collector.get_statistics()
        test_results['statistics'] = 'total_results' in stats
    except Exception as e:
        print(f"Statistics test failed: {e}")
    
    return test_results


# Example usage and testing
if __name__ == "__main__":
    print("Testing Task Queue System...")
    
    # Run validation tests
    results = validate_task_system()
    print("Validation Results:")
    for test, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {test}: {status}")
    
    # Test task scheduler
    try:
        scheduler = get_task_scheduler()
        
        def dummy_parser(file_path):
            time.sleep(0.1)  # Simulate work
            return f"parsed_{file_path}"
        
        # Schedule some parse tasks
        file_paths = [f"/test/file_{i}.reqif" for i in range(5)]
        task_ids = scheduler.schedule_parse_tasks(file_paths, dummy_parser)
        
        print(f"Scheduled {len(task_ids)} parse tasks")
        
        # Get statistics
        queue_stats = scheduler.get_queue_statistics()
        print(f"Queue statistics: {queue_stats}")
        
    except Exception as e:
        print(f"Task scheduler test failed: {e}")
    
    print("Task queue system ready!")