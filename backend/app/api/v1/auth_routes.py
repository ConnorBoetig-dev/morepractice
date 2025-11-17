# ROUTES LAYER - HTTP endpoints that receive requests and call controllers
# Routes do NOT have business logic or database access

# FastAPI imports - for creating API routes
from fastapi import APIRouter, Depends, HTTPException, status

# SQLAlchemy Session type - represents a database connection
from sqlalchemy.orm import Session

# SessionLocal - database connection factory
# Defined in: app/db/session.py
from app.db.session import SessionLocal

# Controller functions - routes call these (controllers have the business logic)
# Defined in: app/controllers/auth_controller.py
from app.controllers.auth_controller import (
    signup,  # ← Handles signup workflow
    login,   # ← Handles login workflow
)

# Pydantic schemas - FastAPI uses these to validate requests/responses
# Defined in: app/schemas/auth.py
from app.schemas.auth import SignupRequest, LoginRequest, TokenResponse, UserResponse

# Auth utility - for JWT validation and user extraction
# Defined in: app/utils/auth.py
from app.utils.auth import get_current_user

# User model - needed for type annotation on protected routes
# Defined in: app/models/user.py
from app.models.user import User

# Create a router specifically for auth endpoints
router = APIRouter(prefix="/auth", tags=["Auth"])

# ----------------------------------------------------
# Dependency: Create a DB session for each request
# ----------------------------------------------------
def get_db():
    """
    This function is a DEPENDENCY.
    FastAPI will call this BEFORE running the route.

    - It creates a fresh Postgres DB session.
    - `yield` gives the session to the route.
    - After the route finishes, the session is closed.
    """
    db = SessionLocal()   # open DB connection
    try:
        yield db          # give connection to route handler
    finally:
        db.close()        # close connection automatically

# POST /api/v1/auth/signup - User registration endpoint
@router.post("/signup", response_model=TokenResponse)
def signup_route(payload: SignupRequest, db: Session = Depends(get_db)):
    """
    Register a new user

    What happens:
    1. FastAPI validates request body against SignupRequest schema
    2. FastAPI runs get_db() to create database session
    3. This route calls signup() CONTROLLER (does NOT do logic itself)
    4. Controller handles the workflow and returns token
    """
    # Call controller - controller will orchestrate services
    # Calls: app/controllers/auth_controller.py → signup()
    return signup(
        db=db,
        email=payload.email,
        password=payload.password,
        username=payload.username,
    )


# POST /api/v1/auth/login - User authentication endpoint
@router.post("/login", response_model=TokenResponse)
def login_route(payload: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate user and return JWT token

    What happens:
    1. FastAPI validates request body against LoginRequest schema
    2. FastAPI runs get_db() to create database session
    3. This route calls login() CONTROLLER (does NOT do logic itself)
    4. Controller validates credentials and returns token
    """
    # Call controller - controller will verify password and generate token
    # Calls: app/controllers/auth_controller.py → login()
    return login(
        db=db,
        email=payload.email,
        password=payload.password,
    )


# GET /api/v1/auth/me - Get current authenticated user
@router.get("/me", response_model=UserResponse)
def get_me_route(
    current_user: User = Depends(get_current_user),  # ← FastAPI injects authenticated user
):
    """
    Get current user information from JWT token

    What happens:
    1. FastAPI runs get_current_user() dependency (which internally uses get_db())
    2. get_current_user() validates token and queries database for user
    3. If token is invalid/expired, raises 401 HTTPException
    4. If valid, returns User model
    5. response_model=UserResponse ensures password hash is NOT included in response

    Protected Route: Requires "Authorization: Bearer <token>" header
    """
    # Depends(get_current_user) already fetched the user from database
    # get_current_user() handles DB connection internally
    # Calls: app/utils/auth.py → get_current_user() (validates token and queries DB)

    # FastAPI auto-converts User model to UserResponse JSON (excludes password)
    return current_user  # ← User model from app/models/user.py


# POST /api/v1/auth/logout - Logout user (client-side token removal)
@router.post("/logout")
def logout_route(current_user: User = Depends(get_current_user)):
    """
    Logout endpoint - informs client to remove token

    How JWT logout works:
    - JWTs are STATELESS (server doesn't track active tokens)
    - Server cannot "revoke" a token (it's valid until expiration)
    - Client is responsible for deleting the token from storage

    This endpoint:
    1. Validates the user is authenticated (via get_current_user dependency)
    2. Returns success message
    3. Client must delete token from localStorage/cookies

    For true server-side logout, you'd need:
    - Token blacklist (store invalidated tokens in Redis/database)
    - Check blacklist on every protected request
    - More complex but provides immediate revocation
    """
    # Token validation already done by get_current_user dependency
    # No server-side state to change (JWT is stateless)

    # Return success - client should delete token
    return {
        "message": "Logout successful",
        "detail": "Please remove the access token from client storage"
    }
