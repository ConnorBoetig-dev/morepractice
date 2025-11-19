# SCHEMAS LAYER - Data validation models
#
# What schemas DO:
# - Validate incoming request data (FastAPI does this automatically)
# - Define response structure (what fields to return in JSON)
# - Convert between database models and JSON
#
# What schemas DON'T DO:
# - Database queries (that's what SERVICES do)
# - Business logic (that's what CONTROLLERS do)

# Pydantic - data validation library using Python type hints
# BaseModel is the parent class for all Pydantic models
# EmailStr is a special type that validates email format
from pydantic import BaseModel, EmailStr, field_validator, Field

# For timestamp types
from datetime import datetime

# For optional types
from typing import Optional

# For password strength validation
import re


# ============================================
# INPUT VALIDATION HELPERS
# ============================================

def validate_username(username: str) -> str:
    """
    Validates username meets security and format requirements

    Requirements:
    - 3-50 characters
    - Alphanumeric, underscore, hyphen only (no special chars to prevent XSS)
    - Cannot start/end with underscore or hyphen
    - No consecutive underscores or hyphens

    Raises ValueError if username doesn't meet requirements
    """
    # Length check (prevent DoS and database issues)
    if len(username) < 3:
        raise ValueError('Username must be at least 3 characters long')
    if len(username) > 50:
        raise ValueError('Username must be at most 50 characters long')

    # Format check (alphanumeric, underscore, hyphen only)
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        raise ValueError('Username can only contain letters, numbers, underscores, and hyphens')

    # Cannot start or end with special characters
    if username[0] in ('_', '-') or username[-1] in ('_', '-'):
        raise ValueError('Username cannot start or end with underscore or hyphen')

    # No consecutive special characters
    if '__' in username or '--' in username or '_-' in username or '-_' in username:
        raise ValueError('Username cannot contain consecutive underscores or hyphens')

    # Reserved usernames (prevent impersonation)
    reserved = {'admin', 'root', 'system', 'support', 'moderator', 'staff'}
    if username.lower() in reserved:
        raise ValueError('This username is reserved and cannot be used')

    return username


def validate_string_length(value: str, min_len: int = 1, max_len: int = 1000, field_name: str = "Field") -> str:
    """
    Validates string length to prevent DoS attacks and database issues

    Args:
        value: String to validate
        min_len: Minimum allowed length
        max_len: Maximum allowed length
        field_name: Name of field for error messages

    Raises ValueError if string doesn't meet length requirements
    """
    if len(value) < min_len:
        raise ValueError(f'{field_name} must be at least {min_len} characters long')
    if len(value) > max_len:
        raise ValueError(f'{field_name} must be at most {max_len} characters long')
    return value


# ============================================
# SIGNUP REQUEST SCHEMA
# ============================================
# Used by: app/api/v1/auth_routes.py → signup_route()
# FastAPI validates incoming JSON against this schema BEFORE the route runs
class SignupRequest(BaseModel):
    """Request body for POST /auth/signup"""

    email: EmailStr  # ← Pydantic validates email format (raises HTTP 422 if invalid)
    password: str    # ← Raw password (comprehensive validation in controller layer)
    username: str    # ← Display name (alphanumeric, underscore, hyphen only)

    @field_validator('username')
    @classmethod
    def validate_username_format(cls, v: str) -> str:
        """Validate username format and prevent XSS"""
        return validate_username(v)

    @field_validator('password')
    @classmethod
    def validate_password_length(cls, v: str) -> str:
        """Basic password length check (full validation in controller)"""
        # Note: Full password policy validation (complexity, history, etc.)
        # is done in app/controllers/auth_controller.py using password_policy.py
        # This is just a basic sanity check to fail fast
        return validate_string_length(v, min_len=12, max_len=128, field_name="Password")

    # Example valid request body:
    # {"email": "user@example.com", "password": "SecurePass123!", "username": "john_doe"}


# ============================================
# LOGIN REQUEST SCHEMA
# ============================================
# Used by: app/api/v1/auth_routes.py → login_route()
class LoginRequest(BaseModel):
    """Request body for POST /auth/login"""

    email: EmailStr  # ← Must be valid email format
    password: str    # ← Plain text password (compared with bcrypt hash in database)

    # Example valid request body:
    # {"email": "user@example.com", "password": "SecurePass123"}


# ============================================
# TOKEN RESPONSE SCHEMA
# ============================================
# Used by: app/api/v1/auth_routes.py → signup_route(), login_route()
# Returned after successful signup or login
class TokenResponse(BaseModel):
    """Response after successful authentication - contains JWT tokens"""

    access_token: str              # ← Signed JWT token (valid for 15 minutes)
    token_type: str = "bearer"     # ← OAuth 2.0 standard bearer token format
    refresh_token: str             # ← Long-lived refresh token (valid for 7 days)

    user_id: int                   # ← User's database ID
    username: str                  # ← User's display name

    # Example response:
    # {
    #   "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    #   "token_type": "bearer",
    #   "refresh_token": "abc123def456...",
    #   "user_id": 1,
    #   "username": "john_doe"
    # }


# ============================================
# USER RESPONSE SCHEMA
# ============================================
# Used by: app/api/v1/auth_routes.py → get_me_route()
# Returns current user info (without password hash for security)
class UserResponse(BaseModel):
    """Response containing user information - password hash excluded for security"""

    id: int                        # ← User's database ID
    email: EmailStr                # ← User's email (used for login)
    username: str                  # ← Display name
    is_active: bool                # ← Whether account is active
    is_verified: bool              # ← Whether email is verified
    is_admin: bool = False         # ← Whether user has admin privileges
    created_at: datetime           # ← When account was created

    class Config:
        # Allows Pydantic to work with SQLAlchemy models
        # Without this, Pydantic can't convert User model to UserResponse
        from_attributes = True  # (was orm_mode in Pydantic v1)

    # Example response:
    # {
    #   "id": 1,
    #   "email": "user@example.com",
    #   "username": "john_doe",
    #   "is_active": true,
    #   "is_verified": false,
    #   "created_at": "2024-01-15T10:30:00"
    # }


# ============================================
# PASSWORD RESET REQUEST SCHEMA
# ============================================
class PasswordResetRequest(BaseModel):
    """Request body for POST /auth/request-reset"""
    email: EmailStr  # Email to send password reset link to

    # Example valid request body:
    # {"email": "user@example.com"}


# ============================================
# PASSWORD RESET CONFIRM SCHEMA
# ============================================
class PasswordResetConfirm(BaseModel):
    """Request body for POST /auth/reset-password"""
    token: str        # Password reset token from email
    new_password: str # New password to set

    @field_validator('token')
    @classmethod
    def validate_token_length(cls, v: str) -> str:
        """Validate token is not empty and not too long"""
        return validate_string_length(v, min_len=1, max_len=500, field_name="Token")

    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Basic password length check (full validation in controller)"""
        return validate_string_length(v, min_len=12, max_len=128, field_name="Password")

    # Example valid request body:
    # {"token": "abc123...", "new_password": "NewSecurePass123!"}


# ============================================
# EMAIL VERIFICATION REQUEST SCHEMA
# ============================================
class EmailVerificationRequest(BaseModel):
    """Request body for POST /auth/send-verification"""
    email: EmailStr  # Email to send verification link to

    # Example valid request body:
    # {"email": "user@example.com"}


# ============================================
# EMAIL VERIFICATION CONFIRM SCHEMA
# ============================================
class EmailVerificationConfirm(BaseModel):
    """Request body for POST /auth/verify-email"""
    token: str  # Email verification token from email

    # Example valid request body:
    # {"token": "xyz789..."}


# ============================================
# GENERIC MESSAGE RESPONSE SCHEMA
# ============================================
class MessageResponse(BaseModel):
    """Generic success message response"""
    message: str
    detail: str = None

    # Example response:
    # {"message": "Password reset email sent", "detail": "Check your inbox"}


# ============================================
# CHANGE PASSWORD REQUEST SCHEMA (While Authenticated)
# ============================================
class ChangePasswordRequest(BaseModel):
    """Request body for POST /auth/change-password"""
    old_password: str  # Current password for verification
    new_password: str  # New password to set

    @field_validator('old_password')
    @classmethod
    def validate_old_password_length(cls, v: str) -> str:
        """Validate old password is not empty and not too long"""
        return validate_string_length(v, min_len=1, max_len=128, field_name="Old password")

    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Basic password length check (full validation in controller)"""
        return validate_string_length(v, min_len=12, max_len=128, field_name="New password")

    # Example valid request body:
    # {"old_password": "OldPass123!", "new_password": "NewSecurePass456!"}


# ============================================
# DELETE ACCOUNT REQUEST SCHEMA
# ============================================
class DeleteAccountRequest(BaseModel):
    """Request body for DELETE /auth/delete-account"""
    password: str  # Password confirmation required for security
    confirm: bool = Field(default=False, description="Must be true to confirm deletion")

    # Example valid request body:
    # {"password": "MyPassword123!", "confirm": true}


# ============================================
# REFRESH TOKEN REQUEST SCHEMA
# ============================================
class RefreshTokenRequest(BaseModel):
    """Request body for POST /auth/refresh"""
    refresh_token: str  # Long-lived refresh token

    # Example valid request body:
    # {"refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}


# ============================================
# REFRESH TOKEN RESPONSE SCHEMA
# ============================================
class RefreshTokenResponse(BaseModel):
    """Response after refreshing access token"""
    access_token: str              # New short-lived access token
    token_type: str = "bearer"     # OAuth 2.0 standard

    # Example response:
    # {"access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...", "token_type": "bearer"}


# ============================================
# UPDATE PROFILE REQUEST SCHEMA
# ============================================
class UpdateProfileRequest(BaseModel):
    """Request body for PATCH /auth/profile"""
    username: Optional[str] = None      # New username (optional)
    email: Optional[EmailStr] = None    # New email (optional, requires re-verification)

    @field_validator('username')
    @classmethod
    def validate_username_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate username format if provided"""
        if v is not None:
            return validate_username(v)
        return v

    # Example valid request body:
    # {"username": "new_username"}
    # or {"email": "newemail@example.com"}
    # or {"username": "new_username", "email": "newemail@example.com"}


# ============================================
# SESSION RESPONSE SCHEMA
# ============================================
class SessionResponse(BaseModel):
    """Response containing active session information"""
    id: int                      # Session ID
    user_id: int                # User ID
    created_at: datetime        # When session was created
    last_active: datetime       # Last activity timestamp
    expires_at: datetime        # When session expires
    ip_address: Optional[str] = None    # IP address (optional)
    user_agent: Optional[str] = None    # Browser/device info (optional)

    class Config:
        from_attributes = True

    # Example response:
    # {
    #   "id": 1,
    #   "user_id": 42,
    #   "created_at": "2024-01-15T10:30:00",
    #   "last_active": "2024-01-15T11:00:00",
    #   "ip_address": "192.168.1.1",
    #   "user_agent": "Mozilla/5.0..."
    # }


# ============================================
# AUDIT LOG RESPONSE SCHEMA
# ============================================
class AuditLogResponse(BaseModel):
    """Response containing audit log entry"""
    id: int                      # Log entry ID
    user_id: int                # User ID
    action: str                  # Action performed (login, logout, password_change, etc.)
    timestamp: datetime          # When action occurred
    ip_address: Optional[str] = None     # IP address (optional)
    user_agent: Optional[str] = None     # Browser/device info (optional)
    details: Optional[str] = None        # Additional details (optional)

    class Config:
        from_attributes = True

    # Example response:
    # {
    #   "id": 1,
    #   "user_id": 42,
    #   "action": "login",
    #   "timestamp": "2024-01-15T10:30:00",
    #   "ip_address": "192.168.1.1",
    #   "user_agent": "Mozilla/5.0...",
    #   "details": "Successful login"
    # }
