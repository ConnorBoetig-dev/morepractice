# UTILITIES LAYER - Helper functions (no database access, no business logic)
#
# What utilities DO:
# - Pure functions (same input = same output)
# - Security operations (password hashing, JWT creation)
# - No side effects (don't modify database or global state)
#
# What utilities DON'T DO:
# - Database queries (that's what SERVICES do)
# - Business logic decisions (that's what CONTROLLERS do)

# Passlib - password hashing library (supports bcrypt, argon2, etc.)
from passlib.context import CryptContext

# Configure password hashing using bcrypt algorithm
# bcrypt is intentionally slow to resist brute-force attacks
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# HASH PASSWORD UTILITY
# Called by: app/services/auth_service.py → create_user()
def hash_password(password: str) -> str:
    """
    Pure function: Hash raw password using bcrypt

    Input: Plain text password (e.g., "mypassword")
    Output: 60-character bcrypt hash (e.g., "$2b$12$KIXvZ9Q2r8Y.../aBcD...")

    Important: Bcrypt hash is ONE-WAY - cannot be reversed to get original password
    """
    return pwd_context.hash(password)  # ← Returns bcrypt hash string


# VERIFY PASSWORD UTILITY
# Called by: app/controllers/auth_controller.py → login()
def verify_password(raw_password: str, hashed_password: str) -> bool:
    """
    Pure function: Compare plain password with bcrypt hash

    Input: Raw password + stored hash
    Output: True if password matches, False if not

    How it works: Bcrypt re-hashes the raw password and compares with stored hash
    """
    return pwd_context.verify(raw_password, hashed_password)  # ← Returns True or False

# PyJWT - library for creating and validating JSON Web Tokens
import jwt

# For timestamps and time deltas
from datetime import datetime, timedelta
from typing import Optional

# For reading environment variables
import os

# JWT Configuration - loaded from environment variables (.env file)
# Environment variables are loaded in app/main.py via load_dotenv()
SECRET_KEY = os.getenv("JWT_SECRET", "fallback_dev_secret_key")  # ← Loaded from .env
ALGORITHM = "HS256"  # HMAC with SHA-256 signing algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRATION_MINUTES", "15"))  # ← Loaded from .env


# CREATE JWT TOKEN UTILITY
# Called by: app/controllers/auth_controller.py → signup(), login()
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Pure function: Generate signed JWT token

    Input: Data to encode (e.g., {"user_id": 123})
    Output: Signed JWT string (e.g., "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")

    Token structure:
    - Header: {"alg": "HS256", "typ": "JWT"}
    - Payload: {"user_id": 123, "exp": 1699999999}
    - Signature: HMAC-SHA256(header + payload, SECRET_KEY)
    """

    to_encode = data.copy()  # Copy to avoid mutating original dict

    # Set expiration time (default 15 minutes from now)
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})  # Add expiration to payload

    # Sign the payload with SECRET_KEY
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt  # ← Returns JWT string (3 base64 parts separated by dots)

# DECODE JWT TOKEN UTILITY
# Called by: app/controllers/auth_controller.py → get_current_user_from_token()
def decode_access_token(token: str):
    """
    Pure function: Validate JWT and extract payload

    Input: JWT string (e.g., "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    Output: Payload dict if valid (e.g., {"user_id": 123, "exp": 1699999999})
            OR None if invalid/expired

    Validation checks:
    1. Signature is valid (token wasn't tampered with)
    2. Token hasn't expired (checks exp field)
    3. Token format is correct
    """

    try:
        # Decode and validate JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload  # ← Returns payload dict

    except jwt.ExpiredSignatureError:
        # Token's exp (expiration) time has passed
        return None

    except jwt.InvalidTokenError:
        # Token signature is invalid or token is malformed
        return None


# ============================================
# DEPENDENCY: Get Current User from JWT Token
# ============================================
# This is a FastAPI DEPENDENCY - used with Depends() to protect routes
# FastAPI imports
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# SQLAlchemy Session - represents database connection
from sqlalchemy.orm import Session

# Bearer token security scheme - extracts "Authorization: Bearer <token>" from headers
security = HTTPBearer()

# GET CURRENT USER DEPENDENCY
# Used by: Protected routes that require authentication (e.g., GET /auth/me)
# Note: Routes must inject both get_db() and this function via Depends()
def get_current_user(
    db: Session,  # ← Database session from route's Depends(get_db)
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """
    FastAPI DEPENDENCY: Extracts user from JWT token in Authorization header

    What this does:
    1. HTTPBearer extracts token from "Authorization: Bearer <token>" header
    2. Decodes JWT and validates signature/expiration
    3. Queries database for user by ID from token payload
    4. Returns User model if valid, raises 401 HTTPException if not

    Usage in routes:
    @router.get("/me")
    def protected_route(current_user: User = Depends(get_current_user)):
        return current_user  # ← FastAPI calls get_current_user() automatically
    """

    # Step 1: Extract token from Authorization header
    # HTTPBearer dependency already validated format "Bearer <token>"
    token = credentials.credentials  # ← Just the token string (without "Bearer ")

    # Step 2: Decode and validate JWT token
    # Calls: decode_access_token() above (validates signature and expiration)
    payload = decode_access_token(token)

    # If token is invalid or expired, return None
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},  # Tell client to use Bearer auth
        )

    # Step 3: Extract user_id from JWT payload
    user_id: int = payload.get("user_id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Step 4: Query database for user
    # Import User model here to avoid circular imports
    from app.models.user import User

    # Call service layer to get user (SERVICE LAYER handles all database queries)
    # Defined in: app/services/auth_service.py
    from app.services.auth_service import get_user_by_id

    user = get_user_by_id(db, user_id)  # ← Calls service layer (not direct query)

    # If user not found in database (maybe deleted after token was issued)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Return User model - FastAPI will inject this into route parameter
    return user  # ← Returns User from app/models/user.py
