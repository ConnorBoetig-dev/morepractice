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
)

# Defined in: app/services/profile_service.py
from app.services.profile_service import create_profile  # ← SERVICE: Inserts profile into database

# UTILITY imports - helper functions (no database access)
# Defined in: app/utils/auth.py
from app.utils.auth import (
    verify_password,      # ← UTILITY: Compares password with bcrypt hash
    create_access_token,  # ← UTILITY: Generates signed JWT token
)


# SIGNUP CONTROLLER
# Called by: app/api/v1/auth_routes.py → signup_route()
def signup(db: Session, email: str, password: str, username: str) -> dict:
    """
    Orchestrates the signup workflow

    This controller:
    - Checks if email is already taken (calls SERVICE)
    - Creates user in database (calls SERVICE)
    - Creates profile (calls SERVICE)
    - Generates JWT token (calls UTILITY)

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

    # Step 2: Create user in database
    # Call SERVICE to insert user (SERVICE will hash password)
    user = create_user(db, email=email, password=password, username=username)  # ← SERVICE does the INSERT

    # Step 3: Create user profile with default stats
    # Call SERVICE to insert profile
    create_profile(db, user_id=user.id)  # ← SERVICE does the INSERT

    # Step 3.5: Unlock default avatars for new user
    # Call SERVICE to unlock all default avatars
    from app.services.avatar_service import unlock_default_avatars
    unlock_default_avatars(db, user.id)

    # Step 4: Generate JWT token
    # Call UTILITY (no database involved)
    token = create_access_token({"user_id": user.id})  # ← UTILITY creates token

    # Return token so user is immediately authenticated
    # token_type: "bearer" follows OAuth 2.0 standard (tells client how to use token)
    return {
        "access_token": token,
        "token_type": "bearer",  # ← OAuth 2.0 bearer token standard
        "user_id": user.id,
        "username": user.username,
    }


# LOGIN CONTROLLER
# Called by: app/api/v1/auth_routes.py → login_route()
def login(db: Session, email: str, password: str) -> dict:
    """
    Orchestrates the login workflow

    This controller:
    - Looks up user by email (calls SERVICE)
    - Verifies password (calls UTILITY)
    - Generates JWT token (calls UTILITY)

    This controller does NOT query the database directly!
    """

    # Step 1: Look up user by email
    # Call SERVICE to query database
    user = get_user_by_email(db, email)  # ← SERVICE does the database query
    if not user:
        # Business logic: generic error prevents email enumeration attacks
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    # Step 2: Verify password
    # Call UTILITY to compare password with hash (no database involved)
    if not verify_password(password, user.hashed_password):  # ← UTILITY compares hashes
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    # Step 3: Generate JWT token
    # Call UTILITY (no database involved)
    token = create_access_token({"user_id": user.id})  # ← UTILITY creates token

    # Return token with OAuth 2.0 standard format
    return {
        "access_token": token,
        "token_type": "bearer",  # ← OAuth 2.0 bearer token standard
        "user_id": user.id,
        "username": user.username,
    }
