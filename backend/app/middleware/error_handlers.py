"""
Global Exception Handlers

Catches all exceptions and transforms them into consistent error responses.
Ensures every error follows the same format for frontend consumption.
"""

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from datetime import datetime
from app.utils.error_codes import map_status_to_code, ErrorCode
from app.utils.logger import get_logger, log_error

logger = get_logger(__name__)


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """
    Handle HTTP exceptions (raised by FastAPI routes).

    Examples:
        - HTTPException(status_code=404, detail="Not found")
        - HTTPException(status_code=401, detail="Unauthorized")

    Returns consistent error format with error codes.
    """
    # Determine error code
    # If detail is a dict with 'code', use it; otherwise map from status code
    if isinstance(exc.detail, dict) and "code" in exc.detail:
        error_code = exc.detail["code"]
        error_message = exc.detail.get("message", str(exc.detail))
    else:
        error_code = map_status_to_code(exc.status_code)
        error_message = str(exc.detail)

    # Log the error (for monitoring/debugging)
    if exc.status_code >= 500:
        logger.error(
            f"HTTP {exc.status_code}: {error_message}",
            extra={
                "status_code": exc.status_code,
                "path": str(request.url.path),
                "error_code": error_code
            }
        )
    else:
        logger.warning(
            f"HTTP {exc.status_code}: {error_message}",
            extra={
                "status_code": exc.status_code,
                "path": str(request.url.path),
                "error_code": error_code
            }
        )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "message": error_message,
                "code": error_code
            },
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "path": str(request.url.path)
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handle Pydantic validation errors (422 Unprocessable Entity).

    Examples:
        - Missing required field
        - Wrong data type
        - Value doesn't match pattern

    Returns list of validation errors with field names.
    """
    # Transform Pydantic errors into our format
    errors = []
    for error in exc.errors():
        # Build field path (e.g., "body.email" or "query.page")
        field_path = ".".join(str(loc) for loc in error["loc"])

        errors.append({
            "field": field_path,
            "message": error["msg"],
            "code": "VALIDATION_ERROR"
        })

    # Log validation errors (debug level - these are expected)
    logger.debug(
        f"Validation error: {len(errors)} field(s) failed",
        extra={
            "path": str(request.url.path),
            "error_count": len(errors)
        }
    )

    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "errors": errors,
            "status_code": 422,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "path": str(request.url.path)
        }
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle unexpected exceptions (500 Internal Server Error).

    This is the catch-all handler for bugs and unexpected errors.
    Logs full stack trace for debugging.

    IMPORTANT: Never expose internal error details to clients in production!
    """
    # Log full exception with stack trace
    logger.error(
        f"Unexpected error: {type(exc).__name__}: {str(exc)}",
        exc_info=True,  # Include full stack trace
        extra={
            "path": str(request.url.path),
            "exception_type": type(exc).__name__
        }
    )

    # Return generic error message (don't expose internal details!)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "message": "An unexpected error occurred. Please try again later.",
                "code": ErrorCode.INTERNAL_SERVER_ERROR
            },
            "status_code": 500,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "path": str(request.url.path)
        }
    )
