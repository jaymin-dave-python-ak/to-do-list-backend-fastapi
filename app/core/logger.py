import logging
import functools
import asyncio
from pathlib import Path
from app.utils.mask_sensitive_data import mask_sensitive_data

log_file = Path("app/logs/application_logs.txt")
log_file.parent.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(log_file)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def log_func(func):
    """Decorator to automatically log function entry, exit, and errors."""

    @functools.wraps(func)  # Preserves original function metadata (name, docstrings)
    async def async_wrapper(*args, **kwargs):
        """Asynchronous wrapper for async functions"""
        m_args = mask_sensitive_data(args)
        m_kwargs = mask_sensitive_data(kwargs)

        logger.info(
            f"Function Start: {func.__name__} | Args: {m_args} Kwargs: {m_kwargs}"
        )
        try:
            result = await func(*args, **kwargs)
            m_result = mask_sensitive_data(result)
            logger.info(f"Function Success: {func.__name__} | Result: {m_result}")
            return result
        except Exception as e:
            logger.error(f"Function Error: {func.__name__} | Exception: {str(e)}")
            raise e

    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        """Synchronous wrapper for sync functions"""
        m_args = mask_sensitive_data(args)
        m_kwargs = mask_sensitive_data(kwargs)
        logger.info(
            f"Function Start: {func.__name__} | Args: {m_args} Kwargs: {m_kwargs}"
        )
        try:
            result = func(*args, **kwargs)
            m_result = mask_sensitive_data(result)
            logger.info(f"Function Success: {func.__name__} | Result: {m_result}")
            return result
        except Exception as e:
            logger.error(f"Function Error: {func.__name__} | Exception: {str(e)}")
            raise e

    return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
