import logging
import functools
from pathlib import Path

log_file = Path("app/logs/application_logs.txt")
log_file.parent.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(log_file)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def log_func(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"Function Start: {func.__name__} | Args: {args} Kwargs: {kwargs}")
        try:
            result = func(*args, **kwargs)
            logger.info(f"Function Success: {func.__name__} | Result: {result}")
            return result
        except Exception as e:
            logger.error(f"Function Error: {func.__name__} | Exception: {str(e)}")
            raise e

    return wrapper
