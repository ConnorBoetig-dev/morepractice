"""
Rate Limiting Utilities

Centralized rate limiting configuration for all API routes.
Uses slowapi for IP-based rate limiting.

Usage in routes:
    from app.utils.rate_limit import limiter

    @router.get("/endpoint")
    @limiter.limit("10/minute")
    async def my_endpoint(request: Request):
        ...
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

# Initialize the rate limiter
# Key function: get_remote_address extracts client IP from request
limiter = Limiter(key_func=get_remote_address)

# Common rate limit presets
# These can be used directly in routes for consistency
RATE_LIMITS = {
    "auth_signup": "3/hour",          # Signup rate limit
    "auth_login": "5/minute",         # Login rate limit
    "quiz_submit": "10/minute",       # Quiz submission rate limit
    "standard": "30/minute",          # Standard API endpoint rate limit
    "leaderboard": "20/minute",       # Leaderboard query rate limit
}
