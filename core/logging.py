"""
Logging configuration using loguru.
Provides structured logging with file rotation and console output.
"""

import sys
import os
from pathlib import Path
from loguru import logger

# Remove default handler
logger.remove()

# Log directory
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)


def setup_logging(
    level: str = "INFO",
    log_to_file: bool = True,
    log_to_console: bool = True,
    json_logs: bool = False,
):
    """
    Configure logging for the application.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Whether to write logs to files
        log_to_console: Whether to output logs to console
        json_logs: Whether to use JSON format for file logs
    """
    # Clear existing handlers
    logger.remove()

    # Console format - colorful and readable
    console_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    # File format - more detailed
    file_format = (
        "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
        "{level: <8} | "
        "{name}:{function}:{line} | "
        "{message}"
    )

    # Console handler
    if log_to_console:
        logger.add(
            sys.stderr,
            format=console_format,
            level=level,
            colorize=True,
            backtrace=True,
            diagnose=True,
        )

    # File handlers - 3 fixed log files
    if log_to_file:
        # General app log
        logger.add(
            LOG_DIR / "app.log",
            format=file_format if not json_logs else None,
            serialize=json_logs,
            level=level,
            rotation="10 MB",
            retention=1,
            backtrace=True,
            diagnose=True,
        )

        # Error log
        logger.add(
            LOG_DIR / "error.log",
            format=file_format if not json_logs else None,
            serialize=json_logs,
            level="ERROR",
            rotation="10 MB",
            retention=1,
            backtrace=True,
            diagnose=True,
        )

        # API log
        logger.add(
            LOG_DIR / "api.log",
            format=file_format,
            level="DEBUG",
            rotation="10 MB",
            retention=1,
            filter=lambda record: "api" in record["extra"].get("category", ""),
        )

    logger.info("Logging initialized", level=level, log_dir=str(LOG_DIR))
    return logger


def get_logger(name: str):
    """
    Get a logger with a specific name/module context.

    Args:
        name: Module or component name

    Returns:
        Logger instance with bound context
    """
    return logger.bind(name=name)


# Context managers for structured logging
class LogContext:
    """Context manager for adding context to log messages."""

    def __init__(self, **kwargs):
        self.context = kwargs
        self._token = None

    def __enter__(self):
        self._token = logger.contextualize(**self.context)
        return logger

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._token:
            self._token.__exit__(exc_type, exc_val, exc_tb)


# Decorators for common logging patterns
def log_function_call(func):
    """Decorator to log function entry and exit."""
    from functools import wraps

    @wraps(func)
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        logger.debug(f"Entering {func_name}", args=str(args)[:100], kwargs=str(kwargs)[:100])
        try:
            result = func(*args, **kwargs)
            logger.debug(f"Exiting {func_name}", result_type=type(result).__name__)
            return result
        except Exception as e:
            logger.exception(f"Exception in {func_name}: {e}")
            raise

    return wrapper


def log_api_call(func):
    """Decorator to log API calls with timing."""
    from functools import wraps
    import time

    @wraps(func)
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        start_time = time.time()

        logger.info(
            f"API call: {func_name}",
            category="api",
        )

        try:
            result = func(*args, **kwargs)
            elapsed = time.time() - start_time
            logger.info(
                f"API call completed: {func_name}",
                category="api",
                elapsed_ms=round(elapsed * 1000, 2),
            )
            return result
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(
                f"API call failed: {func_name}",
                category="api",
                elapsed_ms=round(elapsed * 1000, 2),
                error=str(e),
            )
            raise

    return wrapper


# Initialize with default settings on import
# Can be reconfigured by calling setup_logging()
_env_level = os.getenv("LOG_LEVEL", "INFO").upper()
setup_logging(level=_env_level)
