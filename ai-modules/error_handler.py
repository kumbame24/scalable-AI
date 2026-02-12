import logging
from functools import wraps
from typing import Callable, Any, Optional
import traceback

logger = logging.getLogger(__name__)


def safe_detector(detector_name: str):
    """
    Decorator for detector functions to handle errors gracefully.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Optional[Any]:
            try:
                logger.debug(f"{detector_name}: Processing input")
                result = func(*args, **kwargs)
                if result:
                    logger.info(f"{detector_name}: Detected event - {result.get('type', 'UNKNOWN')}")
                return result
            except Exception as e:
                logger.error(f"{detector_name} Error: {str(e)}")
                logger.debug(traceback.format_exc())
                return None
        return wrapper
    return decorator


def safe_capture(capture_name: str):
    """
    Decorator for capture functions to handle errors gracefully.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Optional[Any]:
            try:
                logger.debug(f"{capture_name}: Starting capture")
                result = func(*args, **kwargs)
                logger.debug(f"{capture_name}: Capture successful")
                return result
            except Exception as e:
                logger.error(f"{capture_name} Error: {str(e)}")
                logger.debug(traceback.format_exc())
                return None
        return wrapper
    return decorator


class DetectionError(Exception):
    """Exception for detection module errors"""
    pass


class CaptureError(Exception):
    """Exception for capture module errors"""
    pass


def retry_on_error(max_retries: int = 3, delay: float = 1.0):
    """
    Decorator to retry function on error.
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Delay between retries in seconds
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            import time
            
            last_error = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    if attempt < max_retries - 1:
                        logger.warning(
                            f"{func.__name__} attempt {attempt + 1} failed, "
                            f"retrying in {delay}s: {str(e)}"
                        )
                        time.sleep(delay)
                    else:
                        logger.error(
                            f"{func.__name__} failed after {max_retries} attempts"
                        )
            
            raise last_error or Exception(f"Failed to execute {func.__name__}")
        return wrapper
    return decorator
