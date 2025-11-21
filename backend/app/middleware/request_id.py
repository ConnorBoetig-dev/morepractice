"""
Request ID Middleware

Adds unique request ID to each HTTP request for tracing.

Features:
- Generates UUID for each request
- Adds X-Request-ID header to response
- Makes request ID available to all logging
"""

import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from typing import Callable
import contextvars


# Context variable to store request ID (thread-safe)
request_id_contextvar = contextvars.ContextVar("request_id", default=None)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware that adds unique request ID to each request

    Benefits:
    - Trace single request through logs
    - Correlate errors with specific requests
    - Debug production issues
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and add request ID

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/route handler

        Returns:
            Response with X-Request-ID header
        """
        # Check if client provided request ID (for distributed tracing)
        request_id = request.headers.get("X-Request-ID")

        # Generate new UUID if not provided
        if not request_id:
            request_id = str(uuid.uuid4())

        # Store in context variable (accessible to all code in this request)
        request_id_contextvar.set(request_id)

        # Add to request state (accessible via request.state.request_id)
        request.state.request_id = request_id

        # Process request
        response = await call_next(request)

        # Add request ID to response headers (useful for debugging)
        response.headers["X-Request-ID"] = request_id

        return response


def get_request_id() -> str:
    """
    Get current request ID

    Returns:
        Request ID string or "unknown" if not in request context

    Usage:
        from app.middleware.request_id import get_request_id
        request_id = get_request_id()
        logger.info("Processing request", extra={"request_id": request_id})
    """
    return request_id_contextvar.get() or "unknown"
