"""
Security Helper Functions
Utilities for audit logging, session management, and security features
"""

from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
from app.models.user import AuditLog, Session as SessionModel, User


# ============================================
# AUDIT LOGGING HELPERS
# ============================================

def create_audit_log(
    db: Session,
    user_id: int,
    action: str,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    details: Optional[str] = None,
    success: bool = True
) -> AuditLog:
    """
    Create an audit log entry for security tracking

    Args:
        db: Database session
        user_id: ID of user performing action
        action: Action performed (login, logout, password_change, etc.)
        ip_address: IP address where action occurred
        user_agent: Browser/device information
        details: Additional details about the action
        success: Whether the action was successful

    Returns:
        AuditLog: Created audit log entry
    """
    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        ip_address=ip_address,
        user_agent=user_agent,
        details=details,
        success=success,
        timestamp=datetime.utcnow()
    )
    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)
    return audit_log


def get_user_audit_logs(
    db: Session,
    user_id: int,
    limit: int = 50,
    action_filter: Optional[str] = None
) -> list[AuditLog]:
    """
    Get audit logs for a specific user

    Args:
        db: Database session
        user_id: ID of user
        limit: Maximum number of logs to return
        action_filter: Optional filter by action type

    Returns:
        List of audit log entries
    """
    query = db.query(AuditLog).filter(AuditLog.user_id == user_id)

    if action_filter:
        query = query.filter(AuditLog.action == action_filter)

    return query.order_by(AuditLog.timestamp.desc()).limit(limit).all()


# ============================================
# SESSION MANAGEMENT HELPERS
# ============================================

def create_session(
    db: Session,
    user_id: int,
    refresh_token: str,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    expires_in_days: int = 7
) -> SessionModel:
    """
    Create a new user session

    Args:
        db: Database session
        user_id: ID of user
        refresh_token: Refresh token for this session
        ip_address: IP address of session
        user_agent: Browser/device information
        expires_in_days: Number of days until session expires

    Returns:
        SessionModel: Created session
    """
    session = SessionModel(
        user_id=user_id,
        refresh_token=refresh_token,
        ip_address=ip_address,
        user_agent=user_agent,
        is_active=True,
        expires_at=datetime.utcnow() + timedelta(days=expires_in_days),
        created_at=datetime.utcnow(),
        last_active=datetime.utcnow()
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_session_by_refresh_token(db: Session, refresh_token: str) -> Optional[SessionModel]:
    """
    Get session by refresh token

    Args:
        db: Database session
        refresh_token: Refresh token to look up

    Returns:
        SessionModel if found, None otherwise
    """
    return db.query(SessionModel).filter(
        SessionModel.refresh_token == refresh_token,
        SessionModel.is_active == True
    ).first()


def revoke_session(db: Session, session_id: int) -> bool:
    """
    Revoke a session (logout)

    Args:
        db: Database session
        session_id: ID of session to revoke

    Returns:
        True if session was revoked, False if not found
    """
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if session:
        session.is_active = False
        db.commit()
        return True
    return False


def revoke_all_user_sessions(db: Session, user_id: int) -> int:
    """
    Revoke all sessions for a user (logout from all devices)

    Args:
        db: Database session
        user_id: ID of user

    Returns:
        Number of sessions revoked
    """
    count = db.query(SessionModel).filter(
        SessionModel.user_id == user_id,
        SessionModel.is_active == True
    ).update({"is_active": False})
    db.commit()
    return count


def get_user_active_sessions(db: Session, user_id: int) -> list[SessionModel]:
    """
    Get all active sessions for a user

    Args:
        db: Database session
        user_id: ID of user

    Returns:
        List of active sessions
    """
    return db.query(SessionModel).filter(
        SessionModel.user_id == user_id,
        SessionModel.is_active == True,
        SessionModel.expires_at > datetime.utcnow()
    ).order_by(SessionModel.last_active.desc()).all()


def cleanup_expired_sessions(db: Session) -> int:
    """
    Clean up expired sessions (should be run periodically)

    Args:
        db: Database session

    Returns:
        Number of sessions cleaned up
    """
    count = db.query(SessionModel).filter(
        SessionModel.expires_at < datetime.utcnow(),
        SessionModel.is_active == True
    ).update({"is_active": False})
    db.commit()
    return count


# ============================================
# FAILED LOGIN PROTECTION HELPERS
# ============================================

def is_account_locked(user: User) -> bool:
    """
    Check if account is currently locked due to failed login attempts

    Args:
        user: User model instance

    Returns:
        True if account is locked, False otherwise
    """
    if user.account_locked_until is None:
        return False

    # Check if lockout period has expired
    if datetime.utcnow() >= user.account_locked_until:
        return False

    return True


def increment_failed_login(db: Session, user: User) -> None:
    """
    Increment failed login attempts and lock account if threshold reached

    Args:
        db: Database session
        user: User model instance
    """
    user.failed_login_attempts += 1

    # Lock account after 5 failed attempts for 15 minutes
    if user.failed_login_attempts >= 5:
        user.account_locked_until = datetime.utcnow() + timedelta(minutes=15)

    db.commit()


def reset_failed_login_attempts(db: Session, user: User) -> None:
    """
    Reset failed login attempts after successful login

    Args:
        db: Database session
        user: User model instance
    """
    user.failed_login_attempts = 0
    user.account_locked_until = None
    db.commit()


def update_last_login(db: Session, user: User, ip_address: Optional[str] = None) -> None:
    """
    Update user's last login timestamp and IP address

    Args:
        db: Database session
        user: User model instance
        ip_address: IP address of login
    """
    user.last_login_at = datetime.utcnow()
    if ip_address:
        user.last_login_ip = ip_address
    db.commit()
