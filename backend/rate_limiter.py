import time
import logging
from typing import Dict, Tuple
from collections import defaultdict
from fastapi import Request, status
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Simple in-memory rate limiter for API endpoints.
    """
    
    def __init__(self, requests_per_second: float = 100):
        self.requests_per_second = requests_per_second
        self.client_requests: Dict[str, list] = defaultdict(list)
    
    def is_allowed(self, client_id: str) -> Tuple[bool, Dict]:
        """
        Check if a request from a client is allowed.
        
        Returns:
            Tuple of (is_allowed, info_dict)
        """
        current_time = time.time()
        window_start = current_time - 1.0  # 1 second window
        
        # Remove old requests outside the window
        self.client_requests[client_id] = [
            req_time for req_time in self.client_requests[client_id]
            if req_time > window_start
        ]
        
        requests_in_window = len(self.client_requests[client_id])
        
        if requests_in_window < self.requests_per_second:
            self.client_requests[client_id].append(current_time)
            return True, {
                "requests_used": requests_in_window + 1,
                "requests_limit": int(self.requests_per_second),
                "reset_time": window_start + 1.0
            }
        else:
            return False, {
                "requests_used": requests_in_window,
                "requests_limit": int(self.requests_per_second),
                "reset_time": window_start + 1.0
            }
    
    def cleanup(self, max_age: int = 3600):
        """
        Remove old client records to prevent memory bloat.
        
        Args:
            max_age: Maximum age of a client record in seconds
        """
        current_time = time.time()
        clients_to_remove = []
        
        for client_id, requests in self.client_requests.items():
            # If no recent requests, mark for removal
            if not requests or (current_time - requests[-1]) > max_age:
                clients_to_remove.append(client_id)
        
        for client_id in clients_to_remove:
            del self.client_requests[client_id]
            logger.debug(f"Cleaned up rate limiter for client: {client_id}")


# Global rate limiter instance
rate_limiter = RateLimiter(requests_per_second=100)


async def rate_limit_middleware(app):
    """
    Middleware to apply rate limiting to all incoming requests.
    """
    @app.middleware("http")
    async def rate_limit_check(request: Request, call_next):
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Check rate limit
        is_allowed, info = rate_limiter.is_allowed(client_ip)
        
        if not is_allowed:
            logger.warning(
                f"Rate limit exceeded for client {client_ip} - "
                f"{info['requests_used']} requests in window"
            )
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Rate limit exceeded",
                    "requests_limit": info["requests_limit"],
                    "reset_time": info["reset_time"]
                }
            )
        
        # Add rate limit headers to response
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(int(info["requests_limit"]))
        response.headers["X-RateLimit-Used"] = str(int(info["requests_used"]))
        response.headers["X-RateLimit-Reset"] = str(int(info["reset_time"]))
        
        return response
    
    return app


def get_rate_limiter_stats() -> Dict:
    """
    Get current rate limiter statistics.
    """
    total_clients = len(rate_limiter.client_requests)
    total_requests = sum(
        len(requests) for requests in rate_limiter.client_requests.values()
    )
    
    return {
        "total_clients": total_clients,
        "total_requests_tracked": total_requests,
        "requests_per_second_limit": rate_limiter.requests_per_second
    }
