"""
REQUEST HELPER UTILITIES
Utilities for extracting information from FastAPI Request objects
"""

from fastapi import Request
from typing import Optional


def get_client_ip(request: Request) -> Optional[str]:
    """
    Extract client IP address from request

    Checks headers in order:
    1. X-Forwarded-For (for proxied requests)
    2. X-Real-IP (for nginx proxied requests)
    3. request.client.host (direct connection)

    Args:
        request: FastAPI Request object

    Returns:
        IP address string or None
    """
    # Check X-Forwarded-For header (used by load balancers/proxies)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # X-Forwarded-For can contain multiple IPs, first one is the client
        return forwarded_for.split(",")[0].strip()

    # Check X-Real-IP header (used by nginx)
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()

    # Fallback to direct client host
    if request.client:
        return request.client.host

    return None


def get_user_agent(request: Request) -> Optional[str]:
    """
    Extract user agent string from request

    Args:
        request: FastAPI Request object

    Returns:
        User agent string or None
    """
    return request.headers.get("User-Agent")


__all__ = ["get_client_ip", "get_user_agent"]
