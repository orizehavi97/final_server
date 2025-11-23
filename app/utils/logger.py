"""Logging configuration and utilities."""
import logging
import sys
from pathlib import Path

# Create logs directory if it doesn't exist
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Configure logging format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Create logger
logger = logging.getLogger("finalserver")
logger.setLevel(logging.INFO)

# Remove any existing handlers
logger.handlers = []

# File handler - write to server.log
file_handler = logging.FileHandler("logs/server.log", encoding="utf-8")
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
file_handler.setFormatter(file_formatter)

# Console handler - write to stdout
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
console_handler.setFormatter(console_formatter)

# Add handlers to logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)


def log_info(message: str, **kwargs):
    """Log info message with optional context."""
    if kwargs:
        message = f"{message} | {kwargs}"
    logger.info(message)


def log_warning(message: str, **kwargs):
    """Log warning message with optional context."""
    if kwargs:
        message = f"{message} | {kwargs}"
    logger.warning(message)


def log_error(message: str, **kwargs):
    """Log error message with optional context."""
    if kwargs:
        message = f"{message} | {kwargs}"
    logger.error(message)


def log_debug(message: str, **kwargs):
    """Log debug message with optional context."""
    if kwargs:
        message = f"{message} | {kwargs}"
    logger.debug(message)
