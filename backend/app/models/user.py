# MODEL LAYER: User and UserProfile database schema definitions

# SQLAlchemy column types for defining table structure
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Date

# For default timestamps
from datetime import datetime

# Declarative base - all models inherit from this
# Defined in: app/db/base.py
from app.db.base import Base

# USER MODEL
# Used by: app/services/auth_service.py
# This class maps to the "users" table in PostgreSQL
class User(Base):
    """User account model - authentication and account info"""
    __tablename__ = "users"  # PostgreSQL table name

    # ============================================
    # PRIMARY KEY
    # ============================================
    id = Column(Integer, primary_key=True, index=True)  # Auto-increments: 1, 2, 3...

    # ============================================
    # AUTHENTICATION FIELDS
    # ============================================
    # unique=True prevents duplicate emails/usernames
    # index=True makes lookups fast (used in WHERE clauses)
    email = Column(String, unique=True, index=True, nullable=False)  # ← Used for login
    username = Column(String, unique=True, index=True, nullable=False)  # ← Display name
    hashed_password = Column(String, nullable=False)  # ← Bcrypt hash (NEVER plain text!)

    # ============================================
    # ACCOUNT STATUS FLAGS
    # ============================================
    is_active = Column(Boolean, default=True)  # False = account disabled (without deleting)
    is_verified = Column(Boolean, default=False)  # Email verification status
    is_admin = Column(Boolean, default=False)  # True = admin user with management privileges

    # ============================================
    # EMAIL VERIFICATION & PASSWORD RESET
    # ============================================
    email_verification_token = Column(String, nullable=True)  # Token sent via email for verification
    email_verified_at = Column(DateTime, nullable=True)  # Timestamp when email was verified
    reset_token = Column(String, nullable=True)  # Password reset token
    reset_token_expires = Column(DateTime, nullable=True)  # When reset token expires (1 hour)

    # ============================================
    # REFRESH TOKEN SYSTEM
    # ============================================
    refresh_token = Column(String, nullable=True)  # Long-lived refresh token (7 days)
    refresh_token_expires = Column(DateTime, nullable=True)  # When refresh token expires

    # ============================================
    # SECURITY: FAILED LOGIN PROTECTION
    # ============================================
    failed_login_attempts = Column(Integer, default=0)  # Count of consecutive failed logins
    account_locked_until = Column(DateTime, nullable=True)  # When account lockout expires (15 min)
    last_login_at = Column(DateTime, nullable=True)  # Timestamp of last successful login
    last_login_ip = Column(String, nullable=True)  # IP address of last login (for audit)

    # ============================================
    # SECURITY: PASSWORD POLICY
    # ============================================
    password_changed_at = Column(DateTime, default=datetime.utcnow)  # When password was last changed

    # ============================================
    # TIMESTAMPS
    # ============================================
    created_at = Column(DateTime, default=datetime.utcnow)  # When account was created
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Auto-updates on changes


# USER PROFILE MODEL
# Used by: app/services/profile_service.py
# This class maps to the "user_profiles" table in PostgreSQL
# One-to-one relationship with User (each user has exactly one profile)
class UserProfile(Base):
    """User profile with gamification stats and customization"""
    __tablename__ = "user_profiles"  # PostgreSQL table name

    # ============================================
    # PRIMARY KEY & RELATIONSHIP
    # ============================================
    # ForeignKey links to users.id - this is BOTH primary key AND foreign key
    # This creates a one-to-one relationship (one user = one profile)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)

    # ============================================
    # PROFILE CUSTOMIZATION
    # ============================================
    bio = Column(Text, nullable=True)  # User biography/description (optional)
    avatar_url = Column(String, nullable=True)  # Profile picture URL (optional)
    selected_avatar_id = Column(Integer, ForeignKey("avatars.id"), nullable=True)  # Currently equipped avatar

    # ============================================
    # GAMIFICATION: XP & LEVEL SYSTEM
    # ============================================
    xp = Column(Integer, default=0, nullable=False)  # Total experience points
    level = Column(Integer, default=1, nullable=False)  # Current level (calculated from XP)

    # ============================================
    # GAMIFICATION: STREAKS
    # ============================================
    study_streak_current = Column(Integer, default=0)  # Current consecutive study days
    study_streak_longest = Column(Integer, default=0)  # Personal record (highest streak)

    # ============================================
    # GAMIFICATION: ACTIVITY COUNTERS
    # ============================================
    total_exams_taken = Column(Integer, default=0)  # Lifetime exam count
    total_questions_answered = Column(Integer, default=0)  # Lifetime question count

    # ============================================
    # STREAK TRACKING DATA
    # ============================================
    # Used to calculate if streak continues or resets
    # Date (not DateTime) - we only care about the day, not the time
    last_activity_date = Column(Date, nullable=True)

    # ============================================
    # TIMESTAMPS
    # ============================================
    created_at = Column(DateTime, default=datetime.utcnow)  # When profile was created


# SESSION MODEL
# Tracks active user sessions for security and logout functionality
class Session(Base):
    """User session model - for tracking active logins and enabling logout"""
    __tablename__ = "sessions"

    # ============================================
    # PRIMARY KEY
    # ============================================
    id = Column(Integer, primary_key=True, index=True)

    # ============================================
    # FOREIGN KEY
    # ============================================
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # ============================================
    # SESSION DATA
    # ============================================
    refresh_token = Column(String, unique=True, nullable=False, index=True)  # Unique session identifier
    ip_address = Column(String, nullable=True)  # IP address of session
    user_agent = Column(String, nullable=True)  # Browser/device information

    # ============================================
    # SESSION STATUS
    # ============================================
    is_active = Column(Boolean, default=True)  # False = session revoked/logged out
    expires_at = Column(DateTime, nullable=False)  # When session expires (7 days)

    # ============================================
    # TIMESTAMPS
    # ============================================
    created_at = Column(DateTime, default=datetime.utcnow)  # When session was created
    last_active = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Last activity


# AUDIT LOG MODEL
# Tracks all authentication events for security monitoring
class AuditLog(Base):
    """Audit log model - tracks all auth events for security"""
    __tablename__ = "audit_logs"

    # ============================================
    # PRIMARY KEY
    # ============================================
    id = Column(Integer, primary_key=True, index=True)

    # ============================================
    # FOREIGN KEY
    # ============================================
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # ============================================
    # AUDIT DATA
    # ============================================
    action = Column(String, nullable=False, index=True)  # Action: login, logout, password_change, etc.
    ip_address = Column(String, nullable=True)  # IP address where action occurred
    user_agent = Column(String, nullable=True)  # Browser/device information
    details = Column(Text, nullable=True)  # Additional details about the action
    success = Column(Boolean, default=True)  # Whether action was successful

    # ============================================
    # TIMESTAMP
    # ============================================
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)  # When action occurred


# PASSWORD HISTORY MODEL
# Tracks password changes for security policy enforcement
class PasswordHistory(Base):
    """Password history model - prevents password reuse and tracks changes"""
    __tablename__ = "password_history"

    # ============================================
    # PRIMARY KEY
    # ============================================
    id = Column(Integer, primary_key=True, index=True)

    # ============================================
    # FOREIGN KEY
    # ============================================
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # ============================================
    # PASSWORD DATA
    # ============================================
    password_hash = Column(String, nullable=False)  # Bcrypt hash of previous password

    # ============================================
    # CHANGE METADATA
    # ============================================
    changed_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)  # When password was changed
    changed_from_ip = Column(String, nullable=True)  # IP address where change occurred
    user_agent = Column(String, nullable=True)  # Browser/device used for change
    change_reason = Column(String, nullable=True)  # Reason: "signup", "user_changed", "password_reset", "admin_forced"