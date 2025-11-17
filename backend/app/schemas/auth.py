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
from pydantic import BaseModel, EmailStr

# For timestamp types
from datetime import datetime


# ============================================
# SIGNUP REQUEST SCHEMA
# ============================================
# Used by: app/api/v1/auth_routes.py → signup_route()
# FastAPI validates incoming JSON against this schema BEFORE the route runs
class SignupRequest(BaseModel):
    """Request body for POST /auth/signup"""

    email: EmailStr  # ← Pydantic validates email format (raises HTTP 422 if invalid)
    password: str    # ← Raw password (will be hashed by app/services/auth_service.py)
    username: str    # ← Display name

    # Example valid request body:
    # {"email": "user@example.com", "password": "SecurePass123", "username": "john_doe"}


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
    """Response after successful authentication - contains JWT token"""

    access_token: str              # ← Signed JWT token (valid for 15 minutes)
    token_type: str = "bearer"     # ← OAuth 2.0 standard bearer token format

    user_id: int                   # ← User's database ID
    username: str                  # ← User's display name

    # Example response:
    # {
    #   "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    #   "token_type": "bearer",
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
