"""
Error Response Schemas

Standardized error responses for the entire API.
All errors follow the same structure for consistent frontend handling.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List


class ErrorDetail(BaseModel):
    """
    Single error detail with message and code.

    Example:
        {
            "message": "Question with id 123 not found",
            "code": "RESOURCE_NOT_FOUND"
        }
    """
    message: str = Field(..., description="Human-readable error message")
    code: str = Field(..., description="Machine-readable error code (e.g., RESOURCE_NOT_FOUND)")

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "message": "Bookmark not found",
                    "code": "RESOURCE_NOT_FOUND"
                },
                {
                    "message": "Invalid email or password",
                    "code": "INVALID_CREDENTIALS"
                },
                {
                    "message": "Insufficient permissions to access this resource",
                    "code": "FORBIDDEN"
                }
            ]
        }
    )


class ErrorResponse(BaseModel):
    """
    Standard error response for all non-validation errors.

    Used for: 400, 401, 403, 404, 409, 500, etc.

    Example:
        {
            "success": false,
            "error": {
                "message": "Question with id 123 not found",
                "code": "RESOURCE_NOT_FOUND"
            },
            "status_code": 404,
            "timestamp": "2024-01-15T10:30:00Z",
            "path": "/api/v1/questions/123"
        }
    """
    success: bool = Field(False, description="Always false for errors")
    error: ErrorDetail = Field(..., description="Error details")
    status_code: int = Field(..., description="HTTP status code")
    timestamp: str = Field(..., description="ISO 8601 timestamp when error occurred")
    path: str = Field(..., description="Request path that caused the error")

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "success": False,
                    "error": {
                        "message": "Bookmark not found",
                        "code": "RESOURCE_NOT_FOUND"
                    },
                    "status_code": 404,
                    "timestamp": "2025-01-20T14:30:00Z",
                    "path": "/api/v1/bookmarks/questions/999"
                },
                {
                    "success": False,
                    "error": {
                        "message": "Invalid email or password",
                        "code": "INVALID_CREDENTIALS"
                    },
                    "status_code": 401,
                    "timestamp": "2025-01-20T14:30:00Z",
                    "path": "/api/v1/auth/login"
                },
                {
                    "success": False,
                    "error": {
                        "message": "Admin access required",
                        "code": "ADMIN_REQUIRED"
                    },
                    "status_code": 403,
                    "timestamp": "2025-01-20T14:30:00Z",
                    "path": "/api/v1/admin/users"
                }
            ]
        }
    )


class ValidationErrorDetail(BaseModel):
    """
    Single validation error (e.g., missing field, invalid format).

    Example:
        {
            "field": "body.email",
            "message": "field required",
            "code": "VALIDATION_ERROR"
        }
    """
    field: str = Field(..., description="Field that failed validation (e.g., 'body.email')")
    message: str = Field(..., description="What went wrong")
    code: str = Field(default="VALIDATION_ERROR", description="Error code")

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "field": "body.email",
                    "message": "field required",
                    "code": "VALIDATION_ERROR"
                },
                {
                    "field": "body.password",
                    "message": "ensure this value has at least 8 characters",
                    "code": "VALIDATION_ERROR"
                },
                {
                    "field": "query.page",
                    "message": "ensure this value is greater than or equal to 1",
                    "code": "VALIDATION_ERROR"
                }
            ]
        }
    )


class ValidationErrorResponse(BaseModel):
    """
    Validation error response (422 Unprocessable Entity).

    Used for: Pydantic validation errors (missing fields, wrong types, etc.)

    Example:
        {
            "success": false,
            "errors": [
                {
                    "field": "body.email",
                    "message": "field required",
                    "code": "VALIDATION_ERROR"
                }
            ],
            "status_code": 422,
            "timestamp": "2024-01-15T10:30:00Z",
            "path": "/api/v1/auth/signup"
        }
    """
    success: bool = Field(False, description="Always false for errors")
    errors: List[ValidationErrorDetail] = Field(..., description="List of validation errors")
    status_code: int = Field(422, description="HTTP status code (always 422 for validation)")
    timestamp: str = Field(..., description="ISO 8601 timestamp when error occurred")
    path: str = Field(..., description="Request path that caused the error")

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "success": False,
                    "errors": [
                        {
                            "field": "body.email",
                            "message": "field required",
                            "code": "VALIDATION_ERROR"
                        },
                        {
                            "field": "body.password",
                            "message": "field required",
                            "code": "VALIDATION_ERROR"
                        }
                    ],
                    "status_code": 422,
                    "timestamp": "2025-01-20T14:30:00Z",
                    "path": "/api/v1/auth/signup"
                },
                {
                    "success": False,
                    "errors": [
                        {
                            "field": "query.page",
                            "message": "ensure this value is greater than or equal to 1",
                            "code": "VALIDATION_ERROR"
                        }
                    ],
                    "status_code": 422,
                    "timestamp": "2025-01-20T14:30:00Z",
                    "path": "/api/v1/bookmarks"
                }
            ]
        }
    )
