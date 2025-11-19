"""
Rate Limiting Utilities

Centralized rate limiting configuration for all API routes.
Uses slowapi with custom key functions for:
- Per-user rate limiting (authenticated requests)
- IP-based rate limiting (unauthenticated requests)

Usage in routes:
    from app.utils.rate_limit import limiter, user_limiter

    # IP-based rate limiting (for public endpoints):
    @router.get("/endpoint")
    @limiter.limit("10/minute")
    async def my_endpoint(request: Request):
        ...

    # User-based rate limiting (for authenticated endpoints):
    @router.get("/authenticated-endpoint")
    @user_limiter.limit("100/minute")
    async def my_endpoint(request: Request, user_id: int = Depends(get_current_user_id)):
        ...
"""

from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.requests import Request
from typing import Optional
import jwt
import os


def get_user_or_ip(request: Request) -> str:
    """
    Custom key function that prioritizes user_id over IP address.

    For authenticated requests: Returns "user:{user_id}"
    For unauthenticated requests: Returns "ip:{ip_address}"

    This allows different rate limits for authenticated vs unauthenticated users.
    """
    # Try to extract user_id from JWT token
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "")
        try:
            # Decode JWT token to get user_id
            # Note: We don't verify the token here (just extract user_id)
            # Token verification happens in the auth dependency
            secret = os.getenv("JWT_SECRET", "")
            if secret:
                payload = jwt.decode(token, secret, algorithms=["HS256"])
                user_id = payload.get("user_id")
                if user_id:
                    return f"user:{user_id}"
        except (jwt.DecodeError, jwt.ExpiredSignatureError, KeyError):
            # If token is invalid/expired, fall back to IP
            pass

    # Fall back to IP address for unauthenticated requests
    ip_address = get_remote_address(request)
    return f"ip:{ip_address}"


def get_user_id_only(request: Request) -> str:
    """
    Strict user-based rate limiting.

    Only extracts user_id from JWT token.
    Returns None for unauthenticated requests (no rate limit applied).

    Use this for endpoints that should only be rate-limited for authenticated users.
    """
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "")
        try:
            secret = os.getenv("JWT_SECRET", "")
            if secret:
                payload = jwt.decode(token, secret, algorithms=["HS256"])
                user_id = payload.get("user_id")
                if user_id:
                    return f"user:{user_id}"
        except (jwt.DecodeError, jwt.ExpiredSignatureError, KeyError):
            pass

    # Return a constant key for unauthenticated requests
    # This effectively disables rate limiting for non-authenticated users
    return "anonymous"


# Initialize the rate limiters

# IP-based rate limiter (for public endpoints like signup, login)
limiter = Limiter(key_func=get_remote_address)

# User-based rate limiter (for authenticated endpoints)
# Uses user_id when available, falls back to IP
user_limiter = Limiter(key_func=get_user_or_ip)

# Strict user-only rate limiter (only limits authenticated users)
user_only_limiter = Limiter(key_func=get_user_id_only)


# Common rate limit presets
# These can be used directly in routes for consistency
RATE_LIMITS = {
    # Public endpoints (IP-based rate limits - stricter)
    "auth_signup": "3/hour",          # Signup rate limit (prevent spam accounts)
    "auth_login": "5/minute",         # Login rate limit (prevent brute force)

    # Authenticated endpoints (User-based rate limits - more lenient)
    "quiz_submit": "100/minute",      # Quiz submission rate limit (per user)
    "standard": "300/minute",         # Standard API endpoint rate limit (per user)
    "leaderboard": "60/minute",       # Leaderboard query rate limit (per user)
    "admin": "1000/minute",           # Admin endpoints (per admin user)

    # Mixed endpoints (could be used by both authenticated and unauthenticated users)
    "questions_view": "30/minute",    # View questions (IP-based for anonymous, user-based for authenticated)
}
