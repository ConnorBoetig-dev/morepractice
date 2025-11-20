# CONTROLLER LAYER - Business logic and workflow orchestration
#
# What controllers DO:
# - Orchestrate multiple service calls
# - Make business logic decisions (if user exists, throw error, etc.)
# - Call utility functions (password hashing, token creation)
# - Return data to routes
#
# What controllers DON'T DO:
# - Direct database queries (that's what SERVICES do)
# - HTTP request/response handling (that's what ROUTES do)

# FastAPI imports for error handling
from fastapi import HTTPException, status

# SQLAlchemy Session type - passed to services for database access
from sqlalchemy.orm import Session

# SERVICE imports - services are the ONLY layer that queries the database
# Defined in: app/services/auth_service.py
from app.services.auth_service import (
    create_user,        # ← SERVICE: Inserts user into database
    get_user_by_email,  # ← SERVICE: Queries database for user by email
    get_user_by_username,  # ← SERVICE: Queries database for user by username
)

# Import User model for direct queries in password reset/verification
from app.models.user import User

# Defined in: app/services/profile_service.py
from app.services.profile_service import create_profile  # ← SERVICE: Inserts profile into database

# UTILITY imports - helper functions (no database access)
# Defined in: app/utils/auth.py
from app.utils.auth import (
    verify_password,      # ← UTILITY: Compares password with bcrypt hash
    create_access_token,  # ← UTILITY: Generates signed JWT token
    hash_password,        # ← UTILITY: Hashes password with bcrypt
)

# Token utilities
# Defined in: app/utils/tokens.py
from app.utils.tokens import (
    generate_reset_token_with_expiration,
    generate_verification_token_with_expiration,
    generate_refresh_token_with_expiration,
    validate_token,
    is_token_expired,
)

# Email service
# Defined in: app/services/email_service.py
from app.services.email_service import (
    send_password_reset_email,
    send_verification_email,
    send_welcome_email,
)

# Security helpers
# Defined in: app/utils/security_helpers.py
from app.utils.security_helpers import (
    create_audit_log,
    get_user_audit_logs,
    create_session,
    get_session_by_refresh_token,
    revoke_session,
    revoke_all_user_sessions,
    get_user_active_sessions,
    is_account_locked,
    increment_failed_login,
    reset_failed_login_attempts,
    update_last_login,
)

# For datetime operations
from datetime import datetime

# For type hints
from typing import Optional


# SIGNUP CONTROLLER
# Called by: app/api/v1/auth_routes.py → signup_route()
async def signup(
    db: Session,
    email: str,
    password: str,
    username: str,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> dict:
    """
    Orchestrates the signup workflow

    This controller:
    - Checks if email is already taken (calls SERVICE)
    - Creates user in database (calls SERVICE)
    - Creates profile (calls SERVICE)
    - Generates JWT access token and refresh token
    - Creates session
    - Sends welcome email
    - Logs signup event

    This controller does NOT query the database directly!
    """

    # Step 1: Check if user already exists
    # Call SERVICE to query database
    existing = get_user_by_email(db, email)  # ← SERVICE does the database query
    if existing:
        # Business logic decision: reject duplicate email
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered.",
        )

    # Step 1.1: Check if username is already taken
    existing_username = get_user_by_username(db, username)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken.",
        )

    # Step 1.5: Validate password strength (NEW: Enterprise password policy)
    from app.utils.password_policy import validate_password_strength
    is_valid, errors = validate_password_strength(password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Password does not meet security requirements: {'; '.join(errors)}"
        )

    # Step 2: Create user in database
    # Call SERVICE to insert user (SERVICE will hash password)
    user = create_user(db, email=email, password=password, username=username)  # ← SERVICE does the INSERT

    # Step 2.5: Add initial password to history (NEW: Password history tracking)
    from app.services.auth_service import add_password_to_history
    add_password_to_history(
        db, user.id, user.hashed_password,
        ip_address=ip_address,
        user_agent=user_agent,
        reason="signup"
    )

    # Step 3: Create user profile with default stats
    # Call SERVICE to insert profile
    create_profile(db, user_id=user.id)  # ← SERVICE does the INSERT

    # Step 3.5: Unlock default avatars for new user
    # Call SERVICE to unlock all default avatars
    from app.services.avatar_service import unlock_default_avatars
    unlock_default_avatars(db, user.id)

    # Step 3.6: Send welcome email (non-blocking, fire and forget)
    try:
        await send_welcome_email(user.email, user.username)
    except Exception as e:
        # Log error but don't block signup
        print(f"Failed to send welcome email: {str(e)}")

    # Step 4: Generate JWT access token and refresh token
    # Call UTILITY (no database involved)
    access_token = create_access_token({"user_id": user.id})  # ← UTILITY creates token
    refresh_token, refresh_expires = generate_refresh_token_with_expiration()

    # Step 5: Create session for refresh token
    create_session(
        db, user.id, refresh_token,
        ip_address=ip_address,
        user_agent=user_agent,
        expires_in_days=7
    )

    # Step 6: Log signup event
    create_audit_log(
        db, user.id, "signup",
        ip_address=ip_address,
        user_agent=user_agent,
        details="New account created"
    )

    # Return tokens so user is immediately authenticated
    # token_type: "bearer" follows OAuth 2.0 standard (tells client how to use token)
    return {
        "access_token": access_token,
        "token_type": "bearer",  # ← OAuth 2.0 bearer token standard
        "refresh_token": refresh_token,  # ← New: For getting new access tokens
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "is_verified": user.is_verified,
        }
    }


# LOGIN CONTROLLER
# Called by: app/api/v1/auth_routes.py → login_route()
def login(
    db: Session,
    email: str,
    password: str,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> dict:
    """
    Orchestrates the login workflow with security features

    This controller:
    - Looks up user by email (calls SERVICE)
    - Checks for account lockout
    - Verifies password (calls UTILITY)
    - Tracks failed login attempts
    - Generates JWT access token and refresh token
    - Creates session for refresh token management
    - Logs audit events

    This controller does NOT query the database directly!
    """

    # Step 1: Look up user by email or username
    # Try email first, then username if not found
    user = get_user_by_email(db, email)  # ← SERVICE does the database query
    if not user:
        # Try username if email lookup failed
        user = get_user_by_username(db, email)  # email parameter may contain username
    if not user:
        # Business logic: generic error prevents email/username enumeration attacks
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    # Step 1.5: Check if account is disabled (banned/suspended by admin)
    if not user.is_active:
        create_audit_log(
            db, user.id, "login_failed",
            ip_address=ip_address,
            user_agent=user_agent,
            details="Login attempt on disabled account",
            success=False
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account has been disabled. Please contact support for assistance."
        )

    # Step 2: Check if account is locked
    if is_account_locked(user):
        lockout_minutes = int((user.account_locked_until - datetime.utcnow()).total_seconds() / 60)
        create_audit_log(
            db, user.id, "login_failed",
            ip_address=ip_address,
            user_agent=user_agent,
            details="Account locked due to failed login attempts",
            success=False
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account locked due to multiple failed login attempts. Try again in {lockout_minutes} minutes."
        )

    # Step 3: Verify password
    # Call UTILITY to compare password with hash (no database involved)
    if not verify_password(password, user.hashed_password):  # ← UTILITY compares hashes
        # Increment failed login attempts
        increment_failed_login(db, user)

        # Log failed login
        create_audit_log(
            db, user.id, "login_failed",
            ip_address=ip_address,
            user_agent=user_agent,
            details="Incorrect password",
            success=False
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    # Step 4: Reset failed login attempts on successful login
    reset_failed_login_attempts(db, user)

    # Step 5: Generate JWT access token and refresh token
    access_token = create_access_token({"user_id": user.id})  # ← UTILITY creates token
    refresh_token, refresh_expires = generate_refresh_token_with_expiration()

    # Step 6: Create session for refresh token
    create_session(
        db, user.id, refresh_token,
        ip_address=ip_address,
        user_agent=user_agent,
        expires_in_days=7
    )

    # Step 7: Update last login timestamp and IP
    update_last_login(db, user, ip_address)

    # Step 8: Log successful login
    create_audit_log(
        db, user.id, "login",
        ip_address=ip_address,
        user_agent=user_agent,
        details="Successful login"
    )

    # Return tokens with OAuth 2.0 standard format
    return {
        "access_token": access_token,
        "token_type": "bearer",  # ← OAuth 2.0 bearer token standard
        "refresh_token": refresh_token,  # ← New: For getting new access tokens
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "is_verified": user.is_verified,
        }
    }


# PASSWORD RESET REQUEST CONTROLLER
# Called by: app/api/v1/auth_routes.py → request_reset_route()
async def request_password_reset(db: Session, email: str) -> dict:
    """
    Orchestrates password reset request workflow

    This controller:
    - Looks up user by email (calls SERVICE)
    - Generates reset token (calls UTILITY)
    - Saves token to database (calls SERVICE)
    - Sends email with reset link (calls EMAIL SERVICE)

    Security: Returns success even if email not found (prevents email enumeration)
    """

    # Step 1: Look up user by email
    user = get_user_by_email(db, email)

    # Security: Don't reveal if email exists or not
    # Always return success to prevent email enumeration attacks
    if not user:
        return {
            "message": "If that email exists, a password reset link has been sent",
            "detail": "Check your inbox and spam folder"
        }

    # Step 2: Generate secure reset token with expiration
    token, expires_at = generate_reset_token_with_expiration()

    # Step 3: Save token to database
    from app.services.auth_service import update_user
    update_user(db, user.id, {
        "reset_token": token,
        "reset_token_expires": expires_at
    })

    # Step 4: Send password reset email
    try:
        await send_password_reset_email(user.email, token, user.username)
    except Exception as e:
        # Log error but don't expose it to user
        print(f"Failed to send password reset email: {str(e)}")

    return {
        "message": "If that email exists, a password reset link has been sent",
        "detail": "Check your inbox and spam folder"
    }


# PASSWORD RESET CONFIRM CONTROLLER
# Called by: app/api/v1/auth_routes.py → reset_password_route()
def reset_password(db: Session, token: str, new_password: str) -> dict:
    """
    Orchestrates password reset confirmation workflow

    This controller:
    - Queries all users to find matching token
    - Validates token and expiration
    - Updates password
    - Clears reset token
    """

    # Step 1: Find user with this reset token
    user = db.query(User).filter(User.reset_token == token).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )

    # Step 2: Validate token hasn't expired
    if not user.reset_token_expires or is_token_expired(user.reset_token_expires):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token has expired. Please request a new one."
        )

    # Step 3: Validate token matches (constant-time comparison)
    if not validate_token(token, user.reset_token, user.reset_token_expires):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )

    # Step 4: Update password and clear reset token
    from app.services.auth_service import update_user
    update_user(db, user.id, {
        "hashed_password": hash_password(new_password),
        "reset_token": None,
        "reset_token_expires": None
    })

    return {
        "message": "Password reset successful",
        "detail": "You can now login with your new password"
    }


# EMAIL VERIFICATION REQUEST CONTROLLER
# Called by: app/api/v1/auth_routes.py → send_verification_route()
async def send_email_verification(db: Session, email: str) -> dict:
    """
    Orchestrates email verification request workflow

    This controller:
    - Looks up user by email
    - Generates verification token
    - Saves token to database
    - Sends verification email
    """

    # Step 1: Look up user by email
    user = get_user_by_email(db, email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check if already verified
    if user.is_verified:
        return {
            "message": "Email already verified",
            "detail": "No action needed"
        }

    # Step 2: Generate verification token
    token, _ = generate_verification_token_with_expiration()

    # Step 3: Save token to database
    from app.services.auth_service import update_user
    update_user(db, user.id, {
        "email_verification_token": token
    })

    # Step 4: Send verification email
    try:
        await send_verification_email(user.email, token, user.username)
    except Exception as e:
        # Log error but don't expose it to user
        print(f"Failed to send verification email: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send verification email"
        )

    return {
        "message": "Verification email sent",
        "detail": "Check your inbox for the verification link"
    }


# EMAIL VERIFICATION CONFIRM CONTROLLER
# Called by: app/api/v1/auth_routes.py → verify_email_route()
def verify_email(db: Session, token: str) -> dict:
    """
    Orchestrates email verification confirmation workflow

    This controller:
    - Finds user with verification token
    - Validates token
    - Marks email as verified
    - Clears verification token
    """

    # Step 1: Find user with this verification token
    user = db.query(User).filter(User.email_verification_token == token).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token"
        )

    # Check if already verified
    if user.is_verified:
        return {
            "message": "Email already verified",
            "detail": "You're all set!"
        }

    # Step 2: Mark as verified and clear token
    from app.services.auth_service import update_user
    update_user(db, user.id, {
        "is_verified": True,
        "email_verified_at": datetime.utcnow(),
        "email_verification_token": None
    })

    # Step 3: Check for "Welcome Aboard!" achievement
    from app.services.achievement_service import check_and_award_achievements
    newly_unlocked = check_and_award_achievements(db, user.id)

    # Build response message
    message = "Email verified successfully"
    if newly_unlocked:
        achievement_names = [a.name for a in newly_unlocked]
        message += f" - Achievement unlocked: {', '.join(achievement_names)}!"

    return {
        "message": message,
        "detail": "Your account is now verified"
    }


# ============================================
# NEW AUTH CONTROLLERS - Phase 1, 2, 3
# ============================================


# CHANGE PASSWORD CONTROLLER (While Authenticated)
# Called by: app/api/v1/auth_routes.py → change_password_route()
async def change_password(
    db: Session,
    user_id: int,
    old_password: str,
    new_password: str,
    ip_address: Optional[str] = None
) -> dict:
    """
    Orchestrates password change workflow (while authenticated)

    Different from password reset - requires current password
    """

    # Step 1: Get user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Step 2: Verify old password
    if not verify_password(old_password, user.hashed_password):
        # Log failed password change attempt
        create_audit_log(
            db, user_id, "password_change_failed",
            ip_address=ip_address,
            details="Incorrect old password",
            success=False
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect current password"
        )

    # Step 3: Validate password and create hash with history tracking
    from app.services.auth_service import validate_and_create_password, update_user
    is_valid, errors, password_hash = validate_and_create_password(
        db, user.id, new_password,
        ip_address=ip_address,
        reason="user_changed"
    )

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Password validation failed: {'; '.join(errors)}"
        )

    # Step 4: Update password with the validated hash
    update_user(db, user.id, {
        "hashed_password": password_hash
    })

    # Step 5: Log successful password change
    create_audit_log(
        db, user_id, "password_change",
        ip_address=ip_address,
        details="Password changed successfully"
    )

    # Step 6: Send confirmation email
    try:
        from app.services.email_service import send_password_changed_email
        await send_password_changed_email(user.email, user.username)
    except Exception as e:
        print(f"Failed to send password change confirmation email: {str(e)}")

    return {
        "message": "Password changed successfully",
        "detail": "Your password has been updated"
    }


# DELETE ACCOUNT CONTROLLER (Hard Delete)
# Called by: app/api/v1/auth_routes.py → delete_account_route()
def delete_account(
    db: Session,
    user_id: int,
    password: str,
    confirm: bool,
    ip_address: Optional[str] = None
) -> dict:
    """
    Orchestrates account deletion workflow (hard delete)

    Requires password confirmation and explicit confirm flag
    """

    # Step 1: Verify confirm flag
    if not confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account deletion must be confirmed. Set 'confirm' to true."
        )

    # Step 2: Get user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Step 3: Verify password
    if not verify_password(password, user.hashed_password):
        # Log failed deletion attempt
        create_audit_log(
            db, user_id, "account_deletion_failed",
            ip_address=ip_address,
            details="Incorrect password",
            success=False
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password"
        )

    # Step 4: Log account deletion before deleting
    create_audit_log(
        db, user_id, "account_deleted",
        ip_address=ip_address,
        details="Account deleted by user request"
    )

    # Step 5: Manually delete all related data (hard delete)
    # Delete sessions and audit logs
    from app.models.user import Session as SessionModel, AuditLog
    db.query(SessionModel).filter(SessionModel.user_id == user_id).delete()
    db.query(AuditLog).filter(AuditLog.user_id == user_id).delete()  # Must delete for foreign key

    # Delete profile, quiz attempts, achievements, avatars (if they exist)
    from app.models.user import UserProfile
    from app.models.gamification import QuizAttempt, UserAnswer, UserAchievement, UserAvatar

    db.query(UserProfile).filter(UserProfile.user_id == user_id).delete()
    db.query(UserAnswer).filter(UserAnswer.user_id == user_id).delete()
    db.query(QuizAttempt).filter(QuizAttempt.user_id == user_id).delete()
    db.query(UserAchievement).filter(UserAchievement.user_id == user_id).delete()
    db.query(UserAvatar).filter(UserAvatar.user_id == user_id).delete()

    # Finally, delete the user
    db.delete(user)
    db.commit()

    return {
        "message": "Account deleted successfully",
        "detail": "All your data has been permanently removed"
    }


# REFRESH TOKEN CONTROLLER
# Called by: app/api/v1/auth_routes.py → refresh_token_route()
def refresh_access_token(
    db: Session,
    refresh_token: str,
    ip_address: Optional[str] = None
) -> dict:
    """
    Orchestrates refresh token workflow

    Validates refresh token and issues new access token
    """

    # Step 1: Find session with this refresh token
    session = get_session_by_refresh_token(db, refresh_token)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    # Step 2: Check if session has expired
    if datetime.utcnow() > session.expires_at:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired. Please login again."
        )

    # Step 3: Get user
    user = db.query(User).filter(User.id == session.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive"
        )

    # Step 4: Generate new access token
    access_token = create_access_token({"user_id": user.id})

    # Step 5: Update session last_active
    session.last_active = datetime.utcnow()
    db.commit()

    # Step 6: Log token refresh
    create_audit_log(
        db, user.id, "token_refresh",
        ip_address=ip_address,
        details="Access token refreshed"
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# LOGOUT CONTROLLER
# Called by: app/api/v1/auth_routes.py → logout_route()
def logout(
    db: Session,
    user_id: int,
    refresh_token: str,
    ip_address: Optional[str] = None
) -> dict:
    """
    Orchestrates logout workflow

    Revokes the current session
    """

    # Step 1: Find session
    session = get_session_by_refresh_token(db, refresh_token)

    if session and session.user_id == user_id:
        # Step 2: Revoke session
        revoke_session(db, session.id)

        # Step 3: Log logout
        create_audit_log(
            db, user_id, "logout",
            ip_address=ip_address,
            details="User logged out"
        )

    return {
        "message": "Logged out successfully",
        "detail": "Session has been revoked"
    }


# LOGOUT ALL DEVICES CONTROLLER
# Called by: app/api/v1/auth_routes.py → logout_all_route()
def logout_all_devices(
    db: Session,
    user_id: int,
    ip_address: Optional[str] = None
) -> dict:
    """
    Orchestrates logout from all devices workflow

    Revokes all active sessions for the user
    """

    # Step 1: Revoke all sessions
    count = revoke_all_user_sessions(db, user_id)

    # Step 2: Log logout from all devices
    create_audit_log(
        db, user_id, "logout_all",
        ip_address=ip_address,
        details=f"Logged out from all devices ({count} sessions revoked)"
    )

    return {
        "message": f"Logged out from all devices",
        "detail": f"{count} sessions revoked"
    }


# GET ACTIVE SESSIONS CONTROLLER
# Called by: app/api/v1/auth_routes.py → get_sessions_route()
def get_active_sessions(db: Session, user_id: int) -> list:
    """
    Get all active sessions for a user
    """
    sessions = get_user_active_sessions(db, user_id)
    return sessions


# GET AUDIT LOGS CONTROLLER
# Called by: app/api/v1/auth_routes.py → get_audit_logs_route()
def get_audit_logs(
    db: Session,
    user_id: int,
    limit: int = 50,
    action_filter: Optional[str] = None
) -> list:
    """
    Get audit logs for a user
    """
    logs = get_user_audit_logs(db, user_id, limit, action_filter)
    return logs


# UPDATE PROFILE CONTROLLER
# Called by: app/api/v1/auth_routes.py → update_profile_route()
async def update_profile(
    db: Session,
    user_id: int,
    username: Optional[str] = None,
    email: Optional[str] = None,
    ip_address: Optional[str] = None
) -> dict:
    """
    Orchestrates profile update workflow

    Can update username and/or email
    If email is changed, requires re-verification
    """

    # Step 1: Get user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    update_data = {}

    # Step 2: Update username if provided
    if username is not None:
        # Check if username is already taken
        existing = db.query(User).filter(
            User.username == username,
            User.id != user_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        update_data["username"] = username

    # Step 3: Update email if provided
    email_changed = False
    if email is not None:
        # Check if email is already taken
        existing = db.query(User).filter(
            User.email == email,
            User.id != user_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Mark as unverified and generate new verification token
        token, _ = generate_verification_token_with_expiration()
        update_data["email"] = email
        update_data["is_verified"] = False
        update_data["email_verification_token"] = token
        email_changed = True

    # Step 4: Apply updates
    if update_data:
        from app.services.auth_service import update_user
        update_user(db, user_id, update_data)

        # Step 5: Log profile update
        details = f"Updated: {', '.join(update_data.keys())}"
        create_audit_log(
            db, user_id, "profile_update",
            ip_address=ip_address,
            details=details
        )

        # Step 6: Send verification email if email changed
        if email_changed:
            try:
                await send_verification_email(email, token, username or user.username)
            except Exception as e:
                print(f"Failed to send verification email: {str(e)}")

    return {
        "message": "Profile updated successfully",
        "detail": "Verification email sent to new address" if email_changed else "Changes saved"
    }
