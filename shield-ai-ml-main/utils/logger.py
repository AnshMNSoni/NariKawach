"""
SHIELD AI - Logger Utility
Provides consistent logging across all modules
"""

import logging
import sys
from datetime import datetime
from typing import Optional
from pathlib import Path

# Try to import loguru, fall back to standard logging
try:
    from loguru import logger as loguru_logger
    HAS_LOGURU = True
except ImportError:
    HAS_LOGURU = False


def setup_logger(
    name: str,
    level: str = "INFO",
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Setup and return a configured logger.
    
    Args:
        name: Logger name (usually __name__)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for logging
        
    Returns:
        Configured logger instance
    """
    if HAS_LOGURU:
        return _setup_loguru_logger(name, level, log_file)
    else:
        return _setup_standard_logger(name, level, log_file)


def _setup_loguru_logger(
    name: str,
    level: str = "INFO",
    log_file: Optional[str] = None
):
    """Setup loguru-based logger"""
    from loguru import logger
    
    # Remove default handler
    logger.remove()
    
    # Add console handler with custom format
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    
    logger.add(
        sys.stderr,
        format=log_format,
        level=level,
        colorize=True
    )
    
    # Add file handler if specified
    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        logger.add(
            log_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            level=level,
            rotation="10 MB",
            retention="7 days",
            compression="zip"
        )
    
    return logger.bind(name=name)


def _setup_standard_logger(
    name: str,
    level: str = "INFO",
    log_file: Optional[str] = None
) -> logging.Logger:
    """Setup standard library logger"""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    
    # Format
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, level.upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


# Create default logger instance
default_logger = setup_logger("shield_ai")


def get_logger(name: str = "shield_ai") -> logging.Logger:
    """Get or create a logger with the given name"""
    return setup_logger(name)


class LoggerMixin:
    """Mixin class to add logging capability to any class"""
    
    @property
    def logger(self):
        if not hasattr(self, '_logger'):
            self._logger = setup_logger(self.__class__.__name__)
        return self._logger
