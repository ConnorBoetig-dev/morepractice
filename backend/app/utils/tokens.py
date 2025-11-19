"""
Token Generation and Validation Utilities

Secure token generation for email verification and password reset.
Uses Python's secrets module for cryptographically secure random tokens.

Token Types:
- Password Reset Token: 1 hour expiration
- Email Verification Token: 24 hour expiration
"""

import secrets
from datetime import datetime, timedelta
from typing import Tuple


def generate_secure_token(length: int = 32) -> str:
    """
    Generate a cryptographically secure random token

    Uses secrets.token_urlsafe which generates URL-safe tokens
    using os.urandom (cryptographically secure random source)

    Args:
        length: Number of random bytes (default 32)
                Final token length will be ~43 characters due to base64 encoding

    Returns:
        str: URL-safe random token (e.g., "xj3kD_9mL2vN8pQ1rS4tU6wX...")

    Example:
        >>> token = generate_secure_token()
        >>> len(token)
        43
        >>> token = generate_secure_token(16)
        >>> len(token)
        22
    """
    return secrets.token_urlsafe(length)


def generate_reset_token() -> str:
    """
    Generate password reset token

    Returns:
        str: Secure 32-byte token for password reset
    """
    return generate_secure_token(32)


def generate_verification_token() -> str:
    """
    Generate email verification token

    Returns:
        str: Secure 32-byte token for email verification
    """
    return generate_secure_token(32)


def get_reset_token_expiration() -> datetime:
    """
    Get expiration time for password reset token

    Password reset tokens expire after 1 hour for security

    Returns:
        datetime: Expiration time (current time + 1 hour)
    """
    return datetime.utcnow() + timedelta(hours=1)


def get_verification_token_expiration() -> datetime:
    """
    Get expiration time for email verification token

    Email verification tokens expire after 24 hours

    Returns:
        datetime: Expiration time (current time + 24 hours)
    """
    return datetime.utcnow() + timedelta(hours=24)


def is_token_expired(expires_at: datetime) -> bool:
    """
    Check if a token has expired

    Args:
        expires_at: Expiration datetime to check

    Returns:
        bool: True if token has expired, False if still valid

    Example:
        >>> from datetime import datetime, timedelta
        >>> future_time = datetime.utcnow() + timedelta(hours=1)
        >>> is_token_expired(future_time)
        False
        >>> past_time = datetime.utcnow() - timedelta(hours=1)
        >>> is_token_expired(past_time)
        True
    """
    if not expires_at:
        return True  # Treat None as expired

    return datetime.utcnow() > expires_at


def generate_reset_token_with_expiration() -> Tuple[str, datetime]:
    """
    Generate password reset token with expiration time

    Convenience function that returns both token and expiration

    Returns:
        tuple: (token, expiration_datetime)

    Example:
        >>> token, expires_at = generate_reset_token_with_expiration()
        >>> print(f"Token: {token}")
        >>> print(f"Expires: {expires_at}")
    """
    token = generate_reset_token()
    expires_at = get_reset_token_expiration()
    return token, expires_at


def generate_verification_token_with_expiration() -> Tuple[str, datetime]:
    """
    Generate email verification token with expiration time

    Convenience function that returns both token and expiration

    Returns:
        tuple: (token, expiration_datetime)

    Example:
        >>> token, expires_at = generate_verification_token_with_expiration()
        >>> print(f"Token: {token}")
        >>> print(f"Expires: {expires_at}")
    """
    token = generate_verification_token()
    expires_at = get_verification_token_expiration()
    return token, expires_at


def validate_token(token: str, stored_token: str, expires_at: datetime) -> bool:
    """
    Validate a token against stored token and expiration

    Performs both token match check and expiration check

    Args:
        token: Token provided by user
        stored_token: Token stored in database
        expires_at: Expiration time from database

    Returns:
        bool: True if token is valid and not expired

    Example:
        >>> token = "abc123"
        >>> stored = "abc123"
        >>> future = datetime.utcnow() + timedelta(hours=1)
        >>> validate_token(token, stored, future)
        True
        >>> validate_token("wrong", stored, future)
        False
    """
    # Check if token matches
    if not secrets.compare_digest(token, stored_token):
        return False

    # Check if token has expired
    if is_token_expired(expires_at):
        return False

    return True


# Token expiration constants (in seconds) for reference
RESET_TOKEN_EXPIRATION_SECONDS = 3600  # 1 hour
VERIFICATION_TOKEN_EXPIRATION_SECONDS = 86400  # 24 hours
REFRESH_TOKEN_EXPIRATION_SECONDS = 604800  # 7 days


def generate_refresh_token() -> str:
    """
    Generate refresh token for session management

    Refresh tokens are long-lived (7 days) and used to obtain new access tokens

    Returns:
        str: Secure 32-byte token for refresh
    """
    return generate_secure_token(32)


def get_refresh_token_expiration() -> datetime:
    """
    Get expiration time for refresh token

    Refresh tokens expire after 7 days

    Returns:
        datetime: Expiration time (current time + 7 days)
    """
    return datetime.utcnow() + timedelta(days=7)


def generate_refresh_token_with_expiration() -> Tuple[str, datetime]:
    """
    Generate refresh token with expiration time

    Convenience function that returns both token and expiration

    Returns:
        tuple: (token, expiration_datetime)

    Example:
        >>> token, expires_at = generate_refresh_token_with_expiration()
        >>> print(f"Refresh Token: {token}")
        >>> print(f"Expires: {expires_at}")
    """
    token = generate_refresh_token()
    expires_at = get_refresh_token_expiration()
    return token, expires_at
