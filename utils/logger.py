"""
Logging System
==============

This module provides comprehensive logging capabilities for the ReqIF Tool Suite.
Includes file logging, console logging, log rotation, and performance monitoring.

Functions:
    setup_logging: Initialize the logging system
    get_logger: Get a logger instance for a module
    log_performance: Performance logging decorator
    log_exception: Exception logging utility
    
Classes:
    ColoredConsoleHandler: Console handler with color support
    PerformanceLogger: Performance monitoring logger
    LogFilter: Custom log filtering
"""

import logging
import logging.handlers
import sys
import os
import time
import functools
import traceback
from datetime import datetime
from pathlib import Path
from typing import Optional, Any, Callable, Dict
import threading

# Import constants (will be available after constants.py is created)
try:
    from .constants import (
        APP_CONFIG, LoggingConstants, get_logs_dir, 
        is_development_mode, get_environment_settings
    )
except ImportError:
    # Fallback values if constants not available yet
    class FallbackConfig:
        APP_NAME = "ReqIF Tool Suite"
        VERSION = "2.0.0"
    
    APP_CONFIG = FallbackConfig()
    
    class LoggingConstants:
        DEBUG = "DEBUG"
        INFO = "INFO"
        WARNING = "WARNING"
        ERROR = "ERROR"
        CRITICAL = "CRITICAL"
        DETAILED_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
        SIMPLE_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
        CONSOLE_FORMAT = "%(levelname)s: %(message)s"
        APP_LOG_FILE = "app.log"
        ERROR_LOG_FILE = "error.log"
        DEBUG_LOG_FILE = "debug.log"
        MAX_LOG_SIZE = 10 * 1024 * 1024
        MAX_LOG_FILES = 5
    
    def get_logs_dir():
        return Path.home() / ".reqif_tool_suite" / "logs"
    
    def is_development_mode():
        return os.getenv('REQIF_ENV', 'production').lower() == 'development'


class ColoredConsoleHandler(logging.StreamHandler):
    """Console handler with color support for different log levels"""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def __init__(self, stream=None, use_colors=None):
        """
        Initialize colored console handler
        
        Args:
            stream: Output stream (default: sys.stderr)
            use_colors: Enable colors (auto-detect if None)
        """
        super().__init__(stream)
        
        if use_colors is None:
            # Auto-detect color support
            self.use_colors = (
                hasattr(self.stream, 'isatty') and 
                self.stream.isatty() and 
                os.getenv('TERM') != 'dumb'
            )
        else:
            self.use_colors = use_colors
    
    def format(self, record):
        """Format log record with colors"""
        formatted = super().format(record)
        
        if self.use_colors and record.levelname in self.COLORS:
            color = self.COLORS[record.levelname]
            reset = self.COLORS['RESET']
            return f"{color}{formatted}{reset}"
        
        return formatted


class PerformanceLogger:
    """Logger for performance monitoring and profiling"""
    
    def __init__(self, logger_name: str = "performance"):
        """Initialize performance logger"""
        self.logger = logging.getLogger(logger_name)
        self.timers = {}
        self.lock = threading.Lock()
    
    def start_timer(self, operation_name: str) -> str:
        """
        Start a performance timer
        
        Args:
            operation_name: Name of the operation being timed
            
        Returns:
            Timer ID for stopping the timer
        """
        timer_id = f"{operation_name}_{int(time.time() * 1000000)}"
        
        with self.lock:
            self.timers[timer_id] = {
                'operation': operation_name,
                'start_time': time.perf_counter(),
                'thread_id': threading.get_ident()
            }
        
        self.logger.debug("Started timer for operation: %s (ID: %s)", operation_name, timer_id)
        return timer_id
    
    def stop_timer(self, timer_id: str) -> Optional[float]:
        """
        Stop a performance timer and log the result
        
        Args:
            timer_id: Timer ID returned by start_timer
            
        Returns:
            Elapsed time in seconds, or None if timer not found
        """
        with self.lock:
            timer_info = self.timers.pop(timer_id, None)
        
        if not timer_info:
            self.logger.warning("Timer not found: %s", timer_id)
            return None
        
        elapsed_time = time.perf_counter() - timer_info['start_time']
        operation_name = timer_info['operation']
        
        # Log performance with appropriate level based on duration
        if elapsed_time > 10.0:  # > 10 seconds
            self.logger.warning("SLOW OPERATION: %s took %.3f seconds", operation_name, elapsed_time)
        elif elapsed_time > 1.0:  # > 1 second
            self.logger.info("Operation %s took %.3f seconds", operation_name, elapsed_time)
        else:
            self.logger.debug("Operation %s took %.3f seconds", operation_name, elapsed_time)
        
        return elapsed_time
    
    def log_memory_usage(self, operation_name: str):
        """Log current memory usage"""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            
            self.logger.info(
                "Memory usage for %s: RSS=%.1f MB, VMS=%.1f MB",
                operation_name,
                memory_info.rss / 1024 / 1024,
                memory_info.vms / 1024 / 1024
            )
        except ImportError:
            self.logger.debug("psutil not available for memory monitoring")
        except Exception as e:
            self.logger.debug("Failed to get memory usage: %s", str(e))


class LogFilter:
    """Custom log filter for advanced filtering capabilities"""
    
    def __init__(self, 
                 min_level: int = logging.DEBUG,
                 max_level: int = logging.CRITICAL,
                 include_modules: Optional[list] = None,
                 exclude_modules: Optional[list] = None):
        """
        Initialize log filter
        
        Args:
            min_level: Minimum log level to accept
            max_level: Maximum log level to accept
            include_modules: List of module names to include (None = all)
            exclude_modules: List of module names to exclude
        """
        self.min_level = min_level
        self.max_level = max_level
        self.include_modules = set(include_modules) if include_modules else None
        self.exclude_modules = set(exclude_modules) if exclude_modules else set()
    
    def filter(self, record):
        """
        Filter log records
        
        Args:
            record: Log record to filter
            
        Returns:
            True if record should be logged, False otherwise
        """
        # Check log level
        if not (self.min_level <= record.levelno <= self.max_level):
            return False
        
        # Check module inclusion/exclusion
        module_name = record.name
        
        if self.exclude_modules and any(excluded in module_name for excluded in self.exclude_modules):
            return False
        
        if self.include_modules and not any(included in module_name for included in self.include_modules):
            return False
        
        return True


class StructuredFormatter(logging.Formatter):
    """Formatter that can output structured logs (JSON)"""
    
    def __init__(self, format_type: str = "text", include_extra: bool = True):
        """
        Initialize structured formatter
        
        Args:
            format_type: "text" or "json"
            include_extra: Include extra fields in log records
        """
        super().__init__()
        self.format_type = format_type
        self.include_extra = include_extra
    
    def format(self, record):
        """Format log record"""
        if self.format_type == "json":
            return self._format_json(record)
        else:
            return self._format_text(record)
    
    def _format_text(self, record):
        """Format as text"""
        timestamp = datetime.fromtimestamp(record.created).isoformat()
        
        base_format = (
            f"{timestamp} - {record.name} - {record.levelname} - "
            f"{record.filename}:{record.lineno} - {record.getMessage()}"
        )
        
        if record.exc_info:
            base_format += "\n" + self.formatException(record.exc_info)
        
        return base_format
    
    def _format_json(self, record):
        """Format as JSON"""
        import json
        
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'message': record.getMessage(),
            'thread': record.thread,
            'thread_name': record.threadName
        }
        
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        if self.include_extra:
            # Add any extra fields
            for key, value in record.__dict__.items():
                if key not in log_entry and not key.startswith('_'):
                    try:
                        json.dumps(value)  # Test if value is JSON serializable
                        log_entry[key] = value
                    except (TypeError, ValueError):
                        log_entry[key] = str(value)
        
        return json.dumps(log_entry, ensure_ascii=False)


# Global performance logger instance
_performance_logger = None

def get_performance_logger() -> PerformanceLogger:
    """Get the global performance logger instance"""
    global _performance_logger
    if _performance_logger is None:
        _performance_logger = PerformanceLogger()
    return _performance_logger


def setup_logging(
    log_level: str = None,
    enable_file_logging: bool = True,
    enable_console_logging: bool = True,
    log_format: str = "detailed",
    log_to_json: bool = False
) -> None:
    """
    Setup the logging system for the application
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        enable_file_logging: Enable logging to files
        enable_console_logging: Enable logging to console
        log_format: Log format ("detailed", "simple", "console")
        log_to_json: Enable JSON structured logging
    """
    # Get settings
    try:
        settings = get_environment_settings()
        if log_level is None:
            log_level = settings.get('log_level', LoggingConstants.INFO)
    except:
        log_level = log_level or LoggingConstants.INFO
    
    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Clear any existing handlers
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    
    # Set root logger level
    root_logger.setLevel(logging.DEBUG)  # Capture all levels, filter in handlers
    
    # Create formatters
    formatters = {
        'detailed': logging.Formatter(LoggingConstants.DETAILED_FORMAT),
        'simple': logging.Formatter(LoggingConstants.SIMPLE_FORMAT),
        'console': logging.Formatter(LoggingConstants.CONSOLE_FORMAT),
        'structured': StructuredFormatter('json' if log_to_json else 'text')
    }
    
    handlers = []
    
    # Console handler
    if enable_console_logging:
        console_handler = ColoredConsoleHandler()
        console_handler.setLevel(numeric_level)
        
        # Use simpler format for console
        formatter_name = 'console' if not log_to_json else 'structured'
        console_handler.setFormatter(formatters[formatter_name])
        
        # Add filter to reduce noise in console
        if not is_development_mode():
            console_filter = LogFilter(
                min_level=logging.INFO,
                exclude_modules=['urllib3', 'requests', 'PIL']
            )
            console_handler.addFilter(console_filter)
        
        handlers.append(console_handler)
        root_logger.addHandler(console_handler)
    
    # File handlers
    if enable_file_logging:
        try:
            # Ensure log directory exists
            log_dir = get_logs_dir()
            log_dir.mkdir(parents=True, exist_ok=True)
            
            # Main application log
            app_log_path = log_dir / LoggingConstants.APP_LOG_FILE
            app_handler = logging.handlers.RotatingFileHandler(
                app_log_path,
                maxBytes=LoggingConstants.MAX_LOG_SIZE,
                backupCount=LoggingConstants.MAX_LOG_FILES,
                encoding='utf-8'
            )
            app_handler.setLevel(numeric_level)
            app_handler.setFormatter(formatters.get(log_format, formatters['detailed']))
            handlers.append(app_handler)
            root_logger.addHandler(app_handler)
            
            # Error log (only errors and above)
            error_log_path = log_dir / LoggingConstants.ERROR_LOG_FILE
            error_handler = logging.handlers.RotatingFileHandler(
                error_log_path,
                maxBytes=LoggingConstants.MAX_LOG_SIZE,
                backupCount=LoggingConstants.MAX_LOG_FILES,
                encoding='utf-8'
            )
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(formatters['detailed'])
            handlers.append(error_handler)
            root_logger.addHandler(error_handler)
            
            # Debug log (only in development mode)
            if is_development_mode():
                debug_log_path = log_dir / LoggingConstants.DEBUG_LOG_FILE
                debug_handler = logging.handlers.RotatingFileHandler(
                    debug_log_path,
                    maxBytes=LoggingConstants.MAX_LOG_SIZE,
                    backupCount=LoggingConstants.MAX_LOG_FILES,
                    encoding='utf-8'
                )
                debug_handler.setLevel(logging.DEBUG)
                debug_handler.setFormatter(formatters['detailed'])
                handlers.append(debug_handler)
                root_logger.addHandler(debug_handler)
        
        except Exception as e:
            # If file logging fails, log to console
            if enable_console_logging:
                logging.error("Failed to setup file logging: %s", str(e))
            else:
                print(f"Failed to setup logging: {e}", file=sys.stderr)
    
    # Set library log levels to reduce noise
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('PIL').setLevel(logging.WARNING)
    
    # Log startup information
    logger = logging.getLogger(__name__)
    logger.info("Logging system initialized")
    logger.info("Application: %s v%s", getattr(APP_CONFIG, 'APP_NAME', 'ReqIF Tool Suite'), 
               getattr(APP_CONFIG, 'VERSION', '2.0.0'))
    logger.info("Log level: %s", log_level)
    logger.info("Development mode: %s", is_development_mode())
    logger.debug("Handlers configured: %d", len(handlers))


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module
    
    Args:
        name: Logger name (typically __name__ of the calling module)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


def log_performance(operation_name: str = None):
    """
    Decorator for logging function performance
    
    Args:
        operation_name: Custom operation name (defaults to function name)
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            perf_logger = get_performance_logger()
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            
            timer_id = perf_logger.start_timer(op_name)
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                logger = get_logger(func.__module__)
                logger.error("Exception in %s: %s", op_name, str(e))
                raise
            finally:
                perf_logger.stop_timer(timer_id)
        
        return wrapper
    return decorator


def log_exception(logger: logging.Logger, message: str = "Exception occurred", 
                 exc_info: bool = True, level: int = logging.ERROR):
    """
    Log an exception with full traceback
    
    Args:
        logger: Logger instance to use
        message: Custom error message
        exc_info: Include exception info in log
        level: Log level to use
    """
    if exc_info and sys.exc_info()[0] is not None:
        logger.log(level, message, exc_info=True)
    else:
        logger.log(level, message)


def log_function_call(logger: logging.Logger, level: int = logging.DEBUG):
    """
    Decorator to log function calls with arguments
    
    Args:
        logger: Logger to use
        level: Log level
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Log function entry
            args_str = ', '.join([repr(arg) for arg in args[:3]])  # Limit to first 3 args
            if len(args) > 3:
                args_str += ', ...'
            
            kwargs_str = ', '.join([f"{k}={repr(v)}" for k, v in list(kwargs.items())[:3]])
            if len(kwargs) > 3:
                kwargs_str += ', ...'
            
            logger.log(level, "Entering %s(%s%s%s)", 
                      func.__name__, 
                      args_str,
                      ', ' if args_str and kwargs_str else '',
                      kwargs_str)
            
            try:
                result = func(*args, **kwargs)
                logger.log(level, "Exiting %s", func.__name__)
                return result
            except Exception as e:
                logger.error("Exception in %s: %s", func.__name__, str(e))
                raise
        
        return wrapper
    return decorator


def create_child_logger(parent_logger: logging.Logger, child_name: str) -> logging.Logger:
    """
    Create a child logger with the same configuration as parent
    
    Args:
        parent_logger: Parent logger
        child_name: Name for child logger
        
    Returns:
        Child logger instance
    """
    child_logger_name = f"{parent_logger.name}.{child_name}"
    return logging.getLogger(child_logger_name)


def set_module_log_level(module_name: str, level: str):
    """
    Set log level for a specific module
    
    Args:
        module_name: Module name
        level: Log level string
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logger = logging.getLogger(module_name)
    logger.setLevel(numeric_level)


def flush_logs():
    """Flush all log handlers"""
    for handler in logging.getLogger().handlers:
        if hasattr(handler, 'flush'):
            handler.flush()


def close_logs():
    """Close all log handlers"""
    for handler in logging.getLogger().handlers[:]:
        if hasattr(handler, 'close'):
            handler.close()
        logging.getLogger().removeHandler(handler)


# Context manager for temporary log level changes
class TemporaryLogLevel:
    """Context manager for temporarily changing log level"""
    
    def __init__(self, logger: logging.Logger, level: str):
        """
        Initialize temporary log level context
        
        Args:
            logger: Logger to modify
            level: Temporary log level
        """
        self.logger = logger
        self.new_level = getattr(logging, level.upper(), logging.INFO)
        self.old_level = None
    
    def __enter__(self):
        """Enter context - set new log level"""
        self.old_level = self.logger.level
        self.logger.setLevel(self.new_level)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context - restore old log level"""
        if self.old_level is not None:
            self.logger.setLevel(self.old_level)


# Initialize logging on module import if not already done
if not logging.getLogger().handlers:
    setup_logging()