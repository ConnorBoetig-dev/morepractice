"""
Centralized Logging Configuration

Provides structured logging for production observability.

Features:
- JSON formatted logs for log aggregators (DataDog, Splunk, ELK)
- Contextual logging (user_id, request_id, operation)
- Different log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Performance: Non-blocking, async-safe
"""

import logging
import sys
import json
from datetime import datetime
from typing import Dict, Any, Optional
import os


class JSONFormatter(logging.Formatter):
    """
    Custom formatter that outputs logs as JSON

    Makes logs easy to parse by log aggregation systems.
    Each log line is valid JSON with structured fields.
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON

        Args:
            record: Python logging record

        Returns:
            JSON string with log data
        """
        # Build base log entry
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add source location (file, line number, function)
        if record.pathname:
            log_data["source"] = {
                "file": record.pathname,
                "line": record.lineno,
                "function": record.funcName,
            }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add custom fields from extra parameter
        # Example: logger.info("User login", extra={"user_id": 123})
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        if hasattr(record, "operation"):
            log_data["operation"] = record.operation
        if hasattr(record, "duration_ms"):
            log_data["duration_ms"] = record.duration_ms
        if hasattr(record, "exam_type"):
            log_data["exam_type"] = record.exam_type
        if hasattr(record, "ip_address"):
            log_data["ip_address"] = record.ip_address

        # Return as compact JSON (one line per log)
        return json.dumps(log_data, default=str)


class SimpleFormatter(logging.Formatter):
    """
    Simple human-readable formatter for development

    Format: [TIMESTAMP] LEVEL - MESSAGE
    Example: [2025-11-20 10:30:00] INFO - User 123 logged in
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as simple text"""
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        # Build message
        message = f"[{timestamp}] {record.levelname:8s} - {record.getMessage()}"

        # Add context if available
        if hasattr(record, "user_id"):
            message += f" [user_id={record.user_id}]"
        if hasattr(record, "operation"):
            message += f" [operation={record.operation}]"

        # Add exception if present
        if record.exc_info:
            message += "\n" + self.formatException(record.exc_info)

        return message


def get_logger(name: str = "billings") -> logging.Logger:
    """
    Get configured logger instance

    Args:
        name: Logger name (typically module name)

    Returns:
        Configured logger instance

    Usage:
        from app.utils.logger import get_logger
        logger = get_logger(__name__)
        logger.info("User logged in", extra={"user_id": 123})
    """
    logger = logging.getLogger(name)

    # Only configure if not already configured (avoid duplicate handlers)
    if not logger.handlers:
        # Set log level from environment or default to INFO
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        logger.setLevel(getattr(logging, log_level, logging.INFO))

        # Create console handler (writes to stdout)
        handler = logging.StreamHandler(sys.stdout)

        # Use JSON format in production, simple format in development
        environment = os.getenv("ENVIRONMENT", "development")
        if environment == "production":
            handler.setFormatter(JSONFormatter())
        else:
            handler.setFormatter(SimpleFormatter())

        logger.addHandler(handler)

        # Don't propagate to root logger (avoid duplicate logs)
        logger.propagate = False

    return logger


# Create default logger instance
logger = get_logger()


# Convenience functions for common operations
def log_auth_event(
    event: str,
    user_id: Optional[int] = None,
    email: Optional[str] = None,
    success: bool = True,
    ip_address: Optional[str] = None,
    details: Optional[str] = None
):
    """
    Log authentication event

    Args:
        event: Event type (login, logout, signup, password_reset, etc.)
        user_id: User ID if available
        email: User email (masked for privacy)
        success: Whether operation succeeded
        ip_address: Client IP address
        details: Additional details
    """
    level = logging.INFO if success else logging.WARNING

    # Mask email for privacy (show first 2 chars and domain)
    masked_email = None
    if email and "@" in email:
        parts = email.split("@")
        masked_email = f"{parts[0][:2]}***@{parts[1]}"

    extra = {
        "operation": f"auth_{event}",
        "user_id": user_id,
        "ip_address": ip_address,
    }

    message = f"Auth: {event} - {'success' if success else 'failed'}"
    if masked_email:
        message += f" ({masked_email})"
    if details:
        message += f" - {details}"

    logger.log(level, message, extra=extra)


def log_quiz_event(
    event: str,
    user_id: int,
    exam_type: str,
    score: Optional[float] = None,
    question_count: Optional[int] = None,
    duration_ms: Optional[int] = None
):
    """
    Log quiz-related event

    Args:
        event: Event type (submit, review, start, etc.)
        user_id: User ID
        exam_type: Exam type (security, network, etc.)
        score: Quiz score percentage
        question_count: Number of questions
        duration_ms: Time taken in milliseconds
    """
    extra = {
        "operation": f"quiz_{event}",
        "user_id": user_id,
        "exam_type": exam_type,
    }

    if duration_ms:
        extra["duration_ms"] = duration_ms

    message = f"Quiz: {event} - {exam_type}"
    if score is not None:
        message += f" - {score:.1f}%"
    if question_count:
        message += f" ({question_count} questions)"

    logger.info(message, extra=extra)


def log_error(
    error: Exception,
    context: str,
    user_id: Optional[int] = None,
    **kwargs
):
    """
    Log error with full context

    Args:
        error: Exception that occurred
        context: What was happening when error occurred
        user_id: User ID if available
        **kwargs: Additional context fields
    """
    extra = {
        "operation": "error",
        "user_id": user_id,
        **kwargs
    }

    logger.error(
        f"{context}: {type(error).__name__} - {str(error)}",
        extra=extra,
        exc_info=True  # Include stack trace
    )


def log_performance(
    operation: str,
    duration_ms: int,
    threshold_ms: int = 1000,
    **kwargs
):
    """
    Log performance metrics

    Args:
        operation: Operation name
        duration_ms: Duration in milliseconds
        threshold_ms: Log as warning if exceeds this
        **kwargs: Additional context
    """
    extra = {
        "operation": operation,
        "duration_ms": duration_ms,
        **kwargs
    }

    if duration_ms > threshold_ms:
        logger.warning(
            f"Slow operation: {operation} took {duration_ms}ms",
            extra=extra
        )
    else:
        logger.debug(
            f"Performance: {operation} took {duration_ms}ms",
            extra=extra
        )
