# ROUTES LAYER - HTTP endpoints that receive requests and call controllers
# Routes do NOT have business logic or database access

# FastAPI imports - for creating API routes
from fastapi import APIRouter, Depends, HTTPException, status, Request

# SQLAlchemy Session type - represents a database connection
from sqlalchemy.orm import Session

# Import centralized rate limiter
from app.utils.rate_limit import limiter, RATE_LIMITS

# Import database session dependency
# Defined in: app/db/session.py
# This provides a database connection for each request
from app.db.session import get_db

# Controller functions - routes call these (controllers have the business logic)
# Defined in: app/controllers/auth_controller.py
from app.controllers.auth_controller import (
    signup,  # ← Handles signup workflow
    login,   # ← Handles login workflow
    request_password_reset,  # ← Handles password reset request
    reset_password,  # ← Handles password reset confirmation
    send_email_verification,  # ← Handles email verification request
    verify_email,  # ← Handles email verification confirmation
    change_password,  # ← Handles password change (while authenticated)
    delete_account,  # ← Handles account deletion
    refresh_access_token,  # ← Handles refresh token exchange
    logout,  # ← Handles logout (session revocation)
    logout_all_devices,  # ← Handles logout from all devices
    get_active_sessions,  # ← Get user's active sessions
    get_audit_logs,  # ← Get user's audit logs
    update_profile,  # ← Update user profile
)

# Pydantic schemas - FastAPI uses these to validate requests/responses
# Defined in: app/schemas/auth.py
from app.schemas.auth import (
    SignupRequest,
    LoginRequest,
    TokenResponse,
    UserResponse,
    ProfileResponse,
    PublicProfileResponse,
    PasswordResetRequest,
    PasswordResetConfirm,
    EmailVerificationRequest,
    EmailVerificationConfirm,
    MessageResponse,
    ChangePasswordRequest,
    DeleteAccountRequest,
    RefreshTokenRequest,
    RefreshTokenResponse,
    UpdateProfileRequest,
    SessionResponse,
    AuditLogResponse,
)

# Auth utility - for JWT validation and user extraction
# Defined in: app/utils/auth.py
from app.utils.auth import get_current_user

# User model - needed for type annotation on protected routes
# Defined in: app/models/user.py
from app.models.user import User

# Profile service - for accessing user profile data
# Defined in: app/services/profile_service.py
from app.services import profile_service

# For typing
from typing import Optional, List

# Create a router specifically for auth endpoints
router = APIRouter(prefix="/auth", tags=["Auth"])


# ============================================
# HELPER FUNCTIONS
# ============================================

def get_client_ip(request: Request) -> Optional[str]:
    """Extract client IP address from request"""
    # Check for forwarded IP (behind proxy/load balancer)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    # Otherwise use direct client IP
    return request.client.host if request.client else None


def get_user_agent(request: Request) -> Optional[str]:
    """Extract user agent from request"""
    return request.headers.get("User-Agent")

# POST /api/v1/auth/signup - User registration endpoint
@router.post("/signup", response_model=TokenResponse)
@limiter.limit(RATE_LIMITS["auth_signup"])  # 3/hour rate limit
async def signup_route(
    request: Request,
    payload: SignupRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new user (Enterprise Flow)

    Rate limit: 3 requests per hour per IP (prevents mass account creation)

    What happens:
    1. FastAPI validates request body against SignupRequest schema
    2. Rate limiter checks if IP has exceeded signup limit
    3. FastAPI runs get_db() to create database session
    4. Controller creates user + profile + unlocks default avatars
    5. Sends verification email (not welcome email - enterprise pattern)
    6. Returns JWT token (user can access platform but should verify)

    User Flow:
    - Signup → Verification email sent
    - User verifies → Welcome email + Achievement unlocked + Avatar unlocked
    """
    # Call controller - controller will orchestrate services
    # Calls: app/controllers/auth_controller.py → signup()
    return await signup(
        db=db,
        email=payload.email,
        password=payload.password,
        username=payload.username,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
    )


# POST /api/v1/auth/login - User authentication endpoint
@router.post("/login", response_model=TokenResponse)
@limiter.limit(RATE_LIMITS["auth_login"])  # 5/minute rate limit
async def login_route(
    request: Request,
    payload: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return JWT token

    Rate limit: 5 requests per minute per IP (prevents credential stuffing)

    What happens:
    1. FastAPI validates request body against LoginRequest schema
    2. Rate limiter checks if IP has exceeded login attempts
    3. FastAPI runs get_db() to create database session
    4. This route calls login() CONTROLLER (does NOT do logic itself)
    5. Controller validates credentials and returns token
    """
    # Call controller - controller will verify password and generate tokens
    # Calls: app/controllers/auth_controller.py → login()
    return login(
        db=db,
        email=payload.email,
        password=payload.password,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
    )


# GET /api/v1/auth/me - Get current authenticated user with profile data
@router.get("/me", response_model=ProfileResponse)
@limiter.limit(RATE_LIMITS["standard"])  # 300/minute rate limit
async def get_me_route(
    request: Request,
    current_user: User = Depends(get_current_user),  # ← FastAPI injects authenticated user
    db: Session = Depends(get_db),  # ← Database session for profile query
):
    """
    Get current user information with full profile data (bio, avatar, stats, etc.)

    What happens:
    1. FastAPI runs get_current_user() dependency (validates token and gets user)
    2. We fetch the user's profile from database (bio, xp, level, streaks, etc.)
    3. Combine user + profile data into ProfileResponse
    4. response_model=ProfileResponse ensures password hash is NOT included

    Protected Route: Requires "Authorization: Bearer <token>" header
    """
    # Get user's profile (bio, avatar, stats, etc.)
    profile = profile_service.get_profile(db, current_user.id)

    # If no profile exists (shouldn't happen but defensive coding)
    if not profile:
        # Return user data with default profile values
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found"
        )

    # Combine user and profile data
    # ProfileResponse expects all fields from both User and UserProfile
    response_data = {
        # User data
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "is_active": current_user.is_active,
        "is_verified": current_user.is_verified,
        "is_admin": current_user.is_admin,
        "created_at": current_user.created_at,

        # Profile data
        "bio": profile.bio,
        "avatar_url": profile.avatar_url,
        "selected_avatar_id": profile.selected_avatar_id,
        "xp": profile.xp,
        "level": profile.level,
        "study_streak_current": profile.study_streak_current,
        "study_streak_longest": profile.study_streak_longest,
        "total_exams_taken": profile.total_exams_taken,
        "total_questions_answered": profile.total_questions_answered,
        "last_activity_date": profile.last_activity_date,
    }

    return ProfileResponse(**response_data)


# ============================================
# NEW AUTH ROUTES - PHASE 1, 2, 3
# ============================================


# POST /api/v1/auth/change-password - Change password while authenticated
@router.post("/change-password", response_model=MessageResponse)
@limiter.limit(RATE_LIMITS["auth_login"])
async def change_password_route(
    request: Request,
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change password (requires old password for verification)

    Protected Route: Requires authentication
    Rate limit: 5 requests per minute

    Different from password reset - requires current password
    """
    return await change_password(
        db=db,
        user_id=current_user.id,
        old_password=payload.old_password,
        new_password=payload.new_password,
        ip_address=get_client_ip(request)
    )


# DELETE /api/v1/auth/delete-account - Delete user account
@router.delete("/delete-account", response_model=MessageResponse)
@limiter.limit(RATE_LIMITS["auth_login"])
def delete_account_route(
    request: Request,
    payload: DeleteAccountRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete user account (hard delete)

    Protected Route: Requires authentication
    Rate limit: 5 requests per minute

    Requires password confirmation and explicit confirm flag
    Permanently deletes all user data
    """
    return delete_account(
        db=db,
        user_id=current_user.id,
        password=payload.password,
        confirm=payload.confirm,
        ip_address=get_client_ip(request)
    )


# POST /api/v1/auth/refresh - Refresh access token
@router.post("/refresh", response_model=RefreshTokenResponse)
@limiter.limit(RATE_LIMITS["auth_login"])
def refresh_token_route(
    request: Request,
    payload: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token

    Rate limit: 5 requests per minute

    Exchanges valid refresh token for new access token
    Does not require authentication (uses refresh token)
    """
    return refresh_access_token(
        db=db,
        refresh_token=payload.refresh_token,
        ip_address=get_client_ip(request)
    )


# POST /api/v1/auth/logout - Logout user (revoke session)
@router.post("/logout", response_model=MessageResponse)
def logout_route(
    request: Request,
    payload: RefreshTokenRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Logout user (revoke current session)

    Protected Route: Requires authentication

    Revokes the refresh token session
    Client should delete both access and refresh tokens
    """
    return logout(
        db=db,
        user_id=current_user.id,
        refresh_token=payload.refresh_token,
        ip_address=get_client_ip(request)
    )


# POST /api/v1/auth/logout-all - Logout from all devices
@router.post("/logout-all", response_model=MessageResponse)
def logout_all_route(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Logout from all devices (revoke all sessions)

    Protected Route: Requires authentication

    Revokes all active sessions for the user
    Useful if account is compromised
    """
    return logout_all_devices(
        db=db,
        user_id=current_user.id,
        ip_address=get_client_ip(request)
    )


# GET /api/v1/auth/sessions - Get active sessions
@router.get("/sessions", response_model=List[SessionResponse])
@limiter.limit(RATE_LIMITS["standard"])  # 300/minute rate limit
async def get_sessions_route(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all active sessions for current user

    Protected Route: Requires authentication
    Rate limit: 300 requests per minute

    Returns list of active sessions with device info
    """
    return get_active_sessions(db=db, user_id=current_user.id)


# GET /api/v1/auth/audit-logs - Get audit logs
@router.get("/audit-logs", response_model=List[AuditLogResponse])
@limiter.limit(RATE_LIMITS["standard"])  # 300/minute rate limit
async def get_audit_logs_route(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 50,
    action: Optional[str] = None
):
    """
    Get audit logs for current user

    Protected Route: Requires authentication
    Rate limit: 300 requests per minute

    Query parameters:
    - limit: Number of logs to return (default: 50)
    - action: Filter by action type (optional)

    Returns list of security events (login, logout, password changes, etc.)
    """
    return get_audit_logs(
        db=db,
        user_id=current_user.id,
        limit=limit,
        action_filter=action
    )


# PATCH /api/v1/auth/profile - Update user profile
@router.patch("/profile", response_model=MessageResponse)
@limiter.limit(RATE_LIMITS["auth_login"])
async def update_profile_route(
    request: Request,
    payload: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user profile (username, email, and/or bio)

    Protected Route: Requires authentication
    Rate limit: 5 requests per minute

    Can update username, email, and/or bio
    Email changes require re-verification
    """
    return await update_profile(
        db=db,
        user_id=current_user.id,
        username=payload.username,
        email=payload.email,
        bio=payload.bio,
        ip_address=get_client_ip(request)
    )


# POST /api/v1/auth/request-reset - Request password reset email
@router.post("/request-reset", response_model=MessageResponse)
@limiter.limit(RATE_LIMITS["auth_login"])  # 5/minute rate limit
async def request_reset_route(
    request: Request,
    payload: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """
    Request password reset email

    Rate limit: 5 requests per minute per IP (prevents abuse)

    What happens:
    1. Validates email format (Pydantic schema)
    2. Rate limiter checks request frequency
    3. Controller generates token and sends email
    4. Returns generic success message (security: no email enumeration)
    """
    return await request_password_reset(db=db, email=payload.email)


# POST /api/v1/auth/reset-password - Confirm password reset with token
@router.post("/reset-password", response_model=MessageResponse)
@limiter.limit(RATE_LIMITS["auth_login"])  # 5/minute rate limit
async def reset_password_route(
    request: Request,
    payload: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """
    Reset password using token from email

    Rate limit: 5 requests per minute per IP (prevents brute force)

    What happens:
    1. Validates token and new password
    2. Controller verifies token hasn't expired
    3. Updates password in database
    4. Clears reset token
    """
    return reset_password(db=db, token=payload.token, new_password=payload.new_password)


# POST /api/v1/auth/send-verification - Send email verification
@router.post("/send-verification", response_model=MessageResponse)
@limiter.limit(RATE_LIMITS["auth_login"])  # 5/minute rate limit
async def send_verification_route(
    request: Request,
    payload: EmailVerificationRequest,
    db: Session = Depends(get_db)
):
    """
    Send email verification link

    Rate limit: 5 requests per minute per IP (prevents abuse)

    What happens:
    1. Validates email format
    2. Controller generates verification token
    3. Sends verification email
    """
    return await send_email_verification(db=db, email=payload.email)


# POST /api/v1/auth/verify-email - Verify email with token
@router.post("/verify-email", response_model=MessageResponse)
@limiter.limit(RATE_LIMITS["auth_login"])  # 5/minute rate limit
async def verify_email_route(
    request: Request,
    payload: EmailVerificationConfirm,
    db: Session = Depends(get_db)
):
    """
    Verify email using token from email

    Rate limit: 5 requests per minute per IP (prevents brute force)

    What happens:
    1. Validates token
    2. Controller marks email as verified
    3. Sends welcome email (enterprise flow)
    4. Unlocks "Welcome Aboard" achievement + Verified Scholar avatar
    """
    return await verify_email(db=db, token=payload.token)


# ============================================
# PUBLIC USER PROFILE
# ============================================

# GET /api/v1/users/{user_id} - View public profile
@router.get("/users/{user_id}", response_model=PublicProfileResponse)
@limiter.limit(RATE_LIMITS["standard"])  # 300/minute rate limit
async def get_public_profile_route(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get public profile for any user by ID

    Public endpoint - no authentication required
    Rate limit: 300 requests per minute

    Returns public profile data (excludes sensitive info like email)

    Use cases:
    - Click on username in leaderboard to view profile
    - Profile sharing/viewing
    - Social features

    Errors:
    - 404 NOT_FOUND - User does not exist
    """
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Get user's profile
    profile = profile_service.get_profile(db, user_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found"
        )

    # Build public profile response (excludes sensitive data)
    response_data = {
        # Public user data
        "id": user.id,
        "username": user.username,
        "created_at": user.created_at,

        # Profile customization
        "bio": profile.bio,
        "avatar_url": profile.avatar_url,
        "selected_avatar_id": profile.selected_avatar_id,

        # Gamification
        "xp": profile.xp,
        "level": profile.level,
        "study_streak_current": profile.study_streak_current,
        "study_streak_longest": profile.study_streak_longest,

        # Stats
        "total_exams_taken": profile.total_exams_taken,
        "total_questions_answered": profile.total_questions_answered,
    }

    return PublicProfileResponse(**response_data)
