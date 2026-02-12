import logging
from functools import wraps
from typing import Callable, Any
from fastapi import Request, status
from fastapi.responses import JSONResponse
import traceback
import time

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backend.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def log_request(app):
    """Middleware to log all requests"""
    @app.middleware("http")
    async def log_middleware(request: Request, call_next):
        start_time = time.time()
        
        # Log request
        logger.info(f"Request: {request.method} {request.url.path}")
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Log response
            logger.info(
                f"Response: {request.method} {request.url.path} - "
                f"Status: {response.status_code} - Duration: {process_time:.3f}s"
            )
            
            response.headers["X-Process-Time"] = str(process_time)
            return response
        except Exception as e:
            logger.error(f"Request error: {request.method} {request.url.path} - {str(e)}")
            logger.error(traceback.format_exc())
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Internal server error"}
            )


def safe_execute(func: Callable) -> Callable:
    """
    Decorator to safely execute functions with error handling and logging.
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        try:
            logger.debug(f"Executing: {func.__name__}")
            result = func(*args, **kwargs)
            logger.debug(f"Completed: {func.__name__}")
            return result
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    return wrapper


def validate_event_data(event_dict: dict) -> tuple[bool, str]:
    """
    Validate event data completeness and format.
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    required_fields = ['source', 'session_id', 'sensor_id', 'event_type', 'confidence']
    
    for field in required_fields:
        if field not in event_dict:
            return False, f"Missing required field: {field}"
    
    # Validate confidence range
    confidence = event_dict.get('confidence')
    if not isinstance(confidence, (int, float)) or not (0 <= confidence <= 1):
        return False, "Confidence must be a number between 0 and 1"
    
    # Validate session_id and sensor_id are integers
    if not isinstance(event_dict.get('session_id'), int):
        return False, "session_id must be an integer"
    
    if not isinstance(event_dict.get('sensor_id'), int):
        return False, "sensor_id must be an integer"
    
    return True, ""


def validate_source_field(source: str) -> tuple[bool, str]:
    """
    Validate event source is from known modules.
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    valid_sources = ['video', 'audio', 'unknown']
    
    if source not in valid_sources:
        return False, f"Source must be one of: {', '.join(valid_sources)}"
    
    return True, ""


class EventError(Exception):
    """Custom exception for event processing errors"""
    pass


class DatabaseError(Exception):
    """Custom exception for database errors"""
    pass


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass
