"""
SHIELD AI - API Middleware
Security, rate limiting, and request processing middleware
"""

import time
import uuid
from datetime import datetime
from typing import Callable, Dict, Optional
from collections import defaultdict
import asyncio

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from ...utils.logger import setup_logger
from ...config.settings import settings

logger = setup_logger(__name__)


class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Security middleware for request validation and headers
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Log request
        logger.debug(
            f"Request {request_id}: {request.method} {request.url.path}"
        )
        
        # Add security headers
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
        
        # Log response
        logger.debug(
            f"Response {request_id}: {response.status_code} in {request.state.process_time:.2f}ms"
            if hasattr(request.state, 'process_time') else
            f"Response {request_id}: {response.status_code}"
        )
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware with sliding window
    """
    
    def __init__(self, app, requests_per_minute: int = None):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute or settings.RATE_LIMIT_DEFAULT_RPM
        self.window_size = 60  # seconds
        
        # Request tracking: {client_key: [(timestamp, count), ...]}
        self.request_log: Dict[str, list] = defaultdict(list)
        
        # Cleanup interval
        self._cleanup_task = None
    
    def _get_client_key(self, request: Request) -> str:
        """Get unique client identifier"""
        # Try to get API key first
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return f"api:{api_key[:16]}"
        
        # Fall back to IP address
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            ip = forwarded.split(",")[0].strip()
        else:
            ip = request.client.host if request.client else "unknown"
        
        return f"ip:{ip}"
    
    def _is_rate_limited(self, client_key: str) -> bool:
        """Check if client is rate limited"""
        if not settings.RATE_LIMIT_ENABLED:
            return False
        
        current_time = time.time()
        window_start = current_time - self.window_size
        
        # Get requests in current window
        client_requests = self.request_log[client_key]
        
        # Remove old requests
        client_requests[:] = [
            (ts, count) for ts, count in client_requests 
            if ts > window_start
        ]
        
        # Count requests in window
        request_count = sum(count for _, count in client_requests)
        
        return request_count >= self.requests_per_minute
    
    def _record_request(self, client_key: str):
        """Record a request"""
        current_time = time.time()
        self.request_log[client_key].append((current_time, 1))
    
    def _get_retry_after(self, client_key: str) -> int:
        """Calculate retry-after time in seconds"""
        if not self.request_log[client_key]:
            return 0
        
        oldest_request = min(ts for ts, _ in self.request_log[client_key])
        return max(1, int(self.window_size - (time.time() - oldest_request)))
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        client_key = self._get_client_key(request)
        
        # Check rate limit
        if self._is_rate_limited(client_key):
            retry_after = self._get_retry_after(client_key)
            
            logger.warning(f"Rate limit exceeded for {client_key}")
            
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests. Please retry after {retry_after} seconds.",
                    "retry_after": retry_after,
                    "timestamp": datetime.now().isoformat()
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(self.requests_per_minute),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time()) + retry_after)
                }
            )
        
        # Record request
        self._record_request(client_key)
        
        # Calculate remaining requests
        client_requests = self.request_log[client_key]
        request_count = sum(count for _, count in client_requests)
        remaining = max(0, self.requests_per_minute - request_count)
        
        # Process request
        start_time = time.time()
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        
        # Store process time for logging
        request.state.process_time = process_time
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(time.time()) + self.window_size)
        response.headers["X-Process-Time-Ms"] = f"{process_time:.2f}"
        
        return response


class RequestTimingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to track request timing
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        response = await call_next(request)
        
        process_time = (time.time() - start_time) * 1000
        response.headers["X-Process-Time-Ms"] = f"{process_time:.2f}"
        
        # Log slow requests
        if process_time > 1000:  # > 1 second
            logger.warning(
                f"Slow request: {request.method} {request.url.path} - {process_time:.2f}ms"
            )
        
        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """
    Global error handling middleware
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)
        except Exception as e:
            request_id = getattr(request.state, 'request_id', 'unknown')
            
            logger.error(
                f"Unhandled error in request {request_id}: {str(e)}",
                exc_info=True
            )
            
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "message": "An unexpected error occurred",
                    "request_id": request_id,
                    "timestamp": datetime.now().isoformat()
                }
            )


class CORSDebugMiddleware(BaseHTTPMiddleware):
    """
    Debug middleware to log CORS issues (development only)
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if settings.DEBUG:
            origin = request.headers.get("origin")
            if origin:
                logger.debug(f"CORS request from origin: {origin}")
        
        return await call_next(request)
