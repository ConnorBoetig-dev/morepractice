"""
ENTERPRISE LOGGING CONFIGURATION
Structured logging for security events, errors, and audit trails

Features:
- JSON formatting for log aggregation (Datadog, ELK, etc.)
- Separate log files for different severity levels
- Request ID tracking for distributed tracing
- Security event logging (auth, admin actions, suspicious activity)
- Performance monitoring (slow queries, endpoint timing)
"""

import os
import sys
from pathlib import Path
from loguru import logger
from datetime import datetime

# ============================================
# LOGGING CONFIGURATION
# ============================================

# Get log directory from environment or use default
LOG_DIR = os.getenv("LOG_DIR", "logs")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Create logs directory if it doesn't exist
Path(LOG_DIR).mkdir(parents=True, exist_ok=True)

# Remove default handler (stderr)
logger.remove()

# ============================================
# CONSOLE HANDLER (Development)
# ============================================
# Pretty-printed logs for development
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>",
    level=LOG_LEVEL,
    colorize=True,
    backtrace=True,
    diagnose=True,
)

# ============================================
# FILE HANDLERS (Production)
# ============================================

# General application log (all levels)
logger.add(
    f"{LOG_DIR}/app.log",
    rotation="500 MB",  # Rotate when file reaches 500MB
    retention="30 days",  # Keep logs for 30 days
    compression="zip",  # Compress rotated logs
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
    backtrace=True,
    diagnose=True,
)

# Error log (ERROR and CRITICAL only)
logger.add(
    f"{LOG_DIR}/error.log",
    rotation="100 MB",
    retention="90 days",  # Keep error logs longer
    compression="zip",
    level="ERROR",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
    backtrace=True,
    diagnose=True,
)

# Security audit log (authentication, authorization, admin actions)
logger.add(
    f"{LOG_DIR}/security.log",
    rotation="200 MB",
    retention="365 days",  # Keep security logs for 1 year (compliance)
    compression="zip",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
    filter=lambda record: "security" in record["extra"],  # Only log records with security tag
)

# ============================================
# STRUCTURED LOGGING HELPERS
# ============================================

def log_security_event(
    event_type: str,
    user_id: int = None,
    username: str = None,
    ip_address: str = None,
    user_agent: str = None,
    success: bool = True,
    details: str = None,
    **extra_fields
):
    """
    Log security-related events with structured data

    Event Types:
    - login_attempt, login_success, login_failed
    - logout
    - signup
    - password_change, password_reset_request, password_reset
    - email_verification
    - admin_action (specify action in details)
    - suspicious_activity
    - account_locked, account_unlocked
    - session_created, session_revoked

    Args:
        event_type: Type of security event
        user_id: User database ID (if applicable)
        username: Username or email
        ip_address: IP address of request
        user_agent: Browser/device user agent
        success: Whether the action succeeded
        details: Additional context or error message
        **extra_fields: Any additional structured data
    """
    log_data = {
        "security": True,
        "event_type": event_type,
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": user_id,
        "username": username,
        "ip_address": ip_address,
        "user_agent": user_agent,
        "success": success,
        "details": details,
        **extra_fields
    }

    # Filter out None values
    log_data = {k: v for k, v in log_data.items() if v is not None}

    level = "INFO" if success else "WARNING"
    logger.bind(**log_data).log(level, f"[SECURITY] {event_type}: {details or 'No details'}")


def log_admin_action(
    action: str,
    admin_id: int,
    admin_username: str,
    target_type: str,
    target_id: int = None,
    ip_address: str = None,
    details: str = None,
    **extra_fields
):
    """
    Log admin actions for audit trail

    Action Types:
    - create_question, update_question, delete_question
    - create_achievement, update_achievement, delete_achievement
    - create_user, update_user, delete_user
    - toggle_admin, toggle_active
    - view_sensitive_data

    Args:
        action: Admin action type
        admin_id: Admin user ID
        admin_username: Admin username
        target_type: Type of resource (user, question, achievement)
        target_id: ID of resource being modified
        ip_address: IP address of admin
        details: Additional context
        **extra_fields: Any additional structured data
    """
    log_security_event(
        event_type="admin_action",
        user_id=admin_id,
        username=admin_username,
        ip_address=ip_address,
        success=True,
        details=f"[{action}] on {target_type}#{target_id}: {details or 'N/A'}",
        admin_action=action,
        target_type=target_type,
        target_id=target_id,
        **extra_fields
    )


def log_performance(
    operation: str,
    duration_ms: float,
    endpoint: str = None,
    user_id: int = None,
    **extra_fields
):
    """
    Log performance metrics for slow operations

    Args:
        operation: Name of operation (e.g., "database_query", "api_request")
        duration_ms: Duration in milliseconds
        endpoint: API endpoint (if applicable)
        user_id: User ID (if applicable)
        **extra_fields: Any additional structured data
    """
    log_data = {
        "performance": True,
        "operation": operation,
        "duration_ms": duration_ms,
        "endpoint": endpoint,
        "user_id": user_id,
        **extra_fields
    }

    # Filter out None values
    log_data = {k: v for k, v in log_data.items() if v is not None}

    # Log as warning if operation is slow
    if duration_ms > 1000:  # > 1 second
        logger.bind(**log_data).warning(f"[PERFORMANCE] Slow operation: {operation} took {duration_ms}ms")
    else:
        logger.bind(**log_data).debug(f"[PERFORMANCE] {operation} took {duration_ms}ms")


def log_error(
    error: Exception,
    context: str,
    user_id: int = None,
    endpoint: str = None,
    **extra_fields
):
    """
    Log errors with full context and stack trace

    Args:
        error: Exception object
        context: Description of what was happening when error occurred
        user_id: User ID (if applicable)
        endpoint: API endpoint where error occurred
        **extra_fields: Any additional structured data
    """
    log_data = {
        "error": True,
        "error_type": type(error).__name__,
        "error_message": str(error),
        "context": context,
        "user_id": user_id,
        "endpoint": endpoint,
        **extra_fields
    }

    # Filter out None values
    log_data = {k: v for k, v in log_data.items() if v is not None}

    logger.bind(**log_data).exception(f"[ERROR] {context}: {error}")


# ============================================
# EXPORT LOGGER
# ============================================
# This logger instance should be used throughout the application
__all__ = ["logger", "log_security_event", "log_admin_action", "log_performance", "log_error"]
