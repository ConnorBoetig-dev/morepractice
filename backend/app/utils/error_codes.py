"""
Error Code Definitions

Machine-readable error codes for programmatic error handling.
Frontend can use these codes to display appropriate messages or take specific actions.
"""

from enum import Enum


class ErrorCode(str, Enum):
    """
    Standard error codes used throughout the API.

    Usage in frontend:
        if (error.code === 'UNAUTHORIZED') {
            redirectToLogin();
        }
    """

    # ============================================
    # 400 BAD REQUEST
    # ============================================
    INVALID_INPUT = "INVALID_INPUT"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    INVALID_TOKEN = "INVALID_TOKEN"
    WEAK_PASSWORD = "WEAK_PASSWORD"

    # ============================================
    # 401 UNAUTHORIZED
    # ============================================
    UNAUTHORIZED = "UNAUTHORIZED"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    TOKEN_INVALID = "TOKEN_INVALID"
    AUTHENTICATION_REQUIRED = "AUTHENTICATION_REQUIRED"

    # ============================================
    # 403 FORBIDDEN
    # ============================================
    FORBIDDEN = "FORBIDDEN"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"
    ADMIN_REQUIRED = "ADMIN_REQUIRED"
    ACCOUNT_INACTIVE = "ACCOUNT_INACTIVE"
    ACCOUNT_UNVERIFIED = "ACCOUNT_UNVERIFIED"
    ACCOUNT_LOCKED = "ACCOUNT_LOCKED"

    # ============================================
    # 404 NOT FOUND
    # ============================================
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    USER_NOT_FOUND = "USER_NOT_FOUND"
    QUESTION_NOT_FOUND = "QUESTION_NOT_FOUND"
    BOOKMARK_NOT_FOUND = "BOOKMARK_NOT_FOUND"
    ENDPOINT_NOT_FOUND = "ENDPOINT_NOT_FOUND"

    # ============================================
    # 409 CONFLICT
    # ============================================
    RESOURCE_ALREADY_EXISTS = "RESOURCE_ALREADY_EXISTS"
    EMAIL_ALREADY_REGISTERED = "EMAIL_ALREADY_REGISTERED"
    USERNAME_ALREADY_TAKEN = "USERNAME_ALREADY_TAKEN"
    DUPLICATE_ENTRY = "DUPLICATE_ENTRY"

    # ============================================
    # 422 UNPROCESSABLE ENTITY
    # ============================================
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_FORMAT = "INVALID_FORMAT"

    # ============================================
    # 429 TOO MANY REQUESTS
    # ============================================
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"

    # ============================================
    # 500 INTERNAL SERVER ERROR
    # ============================================
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"


def map_status_to_code(status_code: int) -> str:
    """
    Map HTTP status code to a default error code.

    Used when HTTPException doesn't specify an error code.

    Args:
        status_code: HTTP status code (e.g., 404, 500)

    Returns:
        Error code string (e.g., "RESOURCE_NOT_FOUND")
    """
    mapping = {
        400: ErrorCode.INVALID_INPUT,
        401: ErrorCode.UNAUTHORIZED,
        403: ErrorCode.FORBIDDEN,
        404: ErrorCode.RESOURCE_NOT_FOUND,
        409: ErrorCode.RESOURCE_ALREADY_EXISTS,
        422: ErrorCode.VALIDATION_ERROR,
        429: ErrorCode.RATE_LIMIT_EXCEEDED,
        500: ErrorCode.INTERNAL_SERVER_ERROR,
    }

    return mapping.get(status_code, ErrorCode.INTERNAL_SERVER_ERROR)
