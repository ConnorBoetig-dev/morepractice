# SERVICE LAYER - Database operations for User model
#
# What services DO:
# - Execute SQL queries (SELECT, INSERT, UPDATE, DELETE)
# - Return database models or None
# - Simple, focused functions (one query per function)
#
# What services DON'T DO:
# - Business logic decisions (that's what CONTROLLERS do)
# - HTTP error handling (that's what CONTROLLERS do)
# - Complex workflows (that's what CONTROLLERS do)

# SQLAlchemy Session type - represents database connection
from sqlalchemy.orm import Session

# User model - maps to "users" table in PostgreSQL
# Defined in: app/models/user.py
from app.models.user import User

# Password hashing utility - called before storing passwords
# Defined in: app/utils/auth.py
from app.utils.auth import hash_password

# For timestamps
from datetime import datetime

# Centralized logging
from app.utils.logger import get_logger

logger = get_logger(__name__)


# CREATE USER SERVICE
# Called by: app/controllers/auth_controller.py → signup()
def create_user(db: Session, email: str, password: str, username: str) -> User:
    """
    DATABASE OPERATION: Insert new user into database

    This service function:
    - Hashes the password
    - Inserts user into "users" table
    - Returns User model with auto-generated ID
    """

    # Hash password before storing (call utility function)
    # NEVER store plain text passwords in database!
    hashed = hash_password(password)  # ← Calls app/utils/auth.py

    # Create User model instance (from app/models/user.py)
    user = User(
        email=email,
        username=username,
        hashed_password=hashed,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    # Execute database INSERT
    db.add(user)       # Add to SQLAlchemy session (staged for insert)
    db.commit()        # ← EXECUTE: SQL INSERT INTO users (...) VALUES (...)
    db.refresh(user)   # Reload from database to get auto-generated id

    # Log user creation
    logger.info(
        f"User created: {username}",
        extra={"user_id": user.id, "operation": "create_user"}
    )

    return user        # ← Returns User model with id field populated

# GET USER BY EMAIL SERVICE
# Called by: app/controllers/auth_controller.py → signup(), login()
def get_user_by_email(db: Session, email: str) -> User | None:
    """
    DATABASE OPERATION: Query user by email

    SQL executed: SELECT * FROM users WHERE email = 'xxx' LIMIT 1
    Returns: User model if found, None if not found
    """
    # Execute database SELECT query
    return db.query(User).filter(User.email == email).first()  # ← Returns User or None

# GET USER BY ID SERVICE
# Called by: app/services/auth_service.py → update_user()
# Called by: app/utils/auth.py → get_current_user() (for JWT token validation)
def get_user_by_id(db: Session, user_id: int) -> User | None:
    """
    DATABASE OPERATION: Query user by ID (primary key)

    SQL executed: SELECT * FROM users WHERE id = 123 LIMIT 1
    Returns: User model if found, None if not found
    """
    # Execute database SELECT query
    return db.query(User).filter(User.id == user_id).first()  # ← Returns User or None

# GET USER BY USERNAME SERVICE
# Called by: app/controllers/auth_controller.py → signup(), login()
def get_user_by_username(db: Session, username: str) -> User | None:
    """
    DATABASE OPERATION: Query user by username

    SQL executed: SELECT * FROM users WHERE username = 'xxx' LIMIT 1
    Returns: User model if found, None if not found
    """
    # Execute database SELECT query
    return db.query(User).filter(User.username == username).first()  # ← Returns User or None

# UPDATE USER SERVICE
# Called by: (not currently used - placeholder for future features)
def update_user(db: Session, user_id: int, updates: dict) -> User:
    """
    DATABASE OPERATION: Update user fields

    This service function:
    - Queries for user by ID
    - Updates specified fields
    - Saves changes to database
    """

    # Get user from database (call service in this same file)
    user = get_user_by_id(db, user_id)
    if not user:
        return None

    # Dynamically update fields from updates dict
    # Example: updates = {"is_verified": True, "username": "new_name"}
    for key, value in updates.items():
        setattr(user, key, value)  # Set user.key = value

    user.updated_at = datetime.utcnow()  # Update timestamp
    db.commit()                          # ← EXECUTE: SQL UPDATE users SET ... WHERE id = ...
    db.refresh(user)                     # Reload from database
    return user                          # ← Returns updated User model


# ============================================
# PASSWORD HISTORY & POLICY SERVICES
# ============================================

from app.models.user import PasswordHistory
from app.utils.auth import verify_password
from app.utils.password_policy import (
    validate_password_strength,
    PASSWORD_HISTORY_COUNT
)
from typing import Optional


def check_password_in_history(
    db: Session,
    user_id: int,
    plain_password: str,
    history_count: int = PASSWORD_HISTORY_COUNT
) -> bool:
    """
    Check if password has been used before (prevent reuse)

    Args:
        db: Database session
        user_id: User ID
        plain_password: Plain text password to check
        history_count: Number of previous passwords to check (default: 5)

    Returns:
        True if password was used before, False if it's new
    """
    # Get last N password hashes for this user
    password_history = db.query(PasswordHistory)\
        .filter(PasswordHistory.user_id == user_id)\
        .order_by(PasswordHistory.changed_at.desc())\
        .limit(history_count)\
        .all()

    # Check if new password matches any previous password
    for history_entry in password_history:
        if verify_password(plain_password, history_entry.password_hash):
            return True  # Password was used before

    return False  # Password is new


def add_password_to_history(
    db: Session,
    user_id: int,
    password_hash: str,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    reason: str = "user_changed"
):
    """
    Add password to history and clean up old entries

    Args:
        db: Database session
        user_id: User ID
        password_hash: Bcrypt hash of the password
        ip_address: IP address where change occurred
        user_agent: Browser/device user agent
        reason: Reason for change ("signup", "user_changed", "password_reset", "admin_forced")
    """
    # Create new password history entry
    history_entry = PasswordHistory(
        user_id=user_id,
        password_hash=password_hash,
        changed_at=datetime.utcnow(),
        changed_from_ip=ip_address,
        user_agent=user_agent,
        change_reason=reason
    )

    db.add(history_entry)

    # Clean up old password history (keep only last N passwords)
    # Get all history entries for this user
    all_history = db.query(PasswordHistory)\
        .filter(PasswordHistory.user_id == user_id)\
        .order_by(PasswordHistory.changed_at.desc())\
        .all()

    # Delete entries beyond the retention limit
    if len(all_history) >= PASSWORD_HISTORY_COUNT:
        entries_to_delete = all_history[PASSWORD_HISTORY_COUNT:]
        for entry in entries_to_delete:
            db.delete(entry)

    db.commit()


def validate_and_create_password(
    db: Session,
    user_id: int,
    plain_password: str,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    reason: str = "user_changed"
) -> tuple[bool, list[str], Optional[str]]:
    """
    Validate password policy and create hash (all-in-one function)

    This function:
    1. Validates password strength (complexity requirements)
    2. Checks password history (prevents reuse)
    3. Creates password hash
    4. Adds to password history

    Args:
        db: Database session
        user_id: User ID (0 for new users during signup)
        plain_password: Plain text password
        ip_address: IP address where change occurred
        user_agent: Browser/device user agent
        reason: Reason for change

    Returns:
        Tuple of (is_valid, errors, password_hash)
        - is_valid: True if password meets all requirements
        - errors: List of validation errors (empty if valid)
        - password_hash: Bcrypt hash if valid, None if invalid
    """
    # Step 1: Validate password strength
    is_strong, strength_errors = validate_password_strength(plain_password)
    if not is_strong:
        return (False, strength_errors, None)

    # Step 2: Check password history (skip for new users)
    if user_id > 0:
        was_used_before = check_password_in_history(db, user_id, plain_password)
        if was_used_before:
            return (False, [f"Password was recently used. Please choose a different password (last {PASSWORD_HISTORY_COUNT} passwords cannot be reused)"], None)

    # Step 3: Create password hash
    password_hash = hash_password(plain_password)

    # Step 4: Add to password history (skip for new users - will be added after user creation)
    if user_id > 0:
        add_password_to_history(db, user_id, password_hash, ip_address, user_agent, reason)

    return (True, [], password_hash)
