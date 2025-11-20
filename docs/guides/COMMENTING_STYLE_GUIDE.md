# Code Commenting Style Guide

This document outlines the teaching-focused commenting style used in the Billings backend codebase. Use this guide when asking Claude (or other developers) to add comments to new code in future conversations.

## Philosophy

**Purpose:** Comments should teach new developers how the system works, explain the flow between architectural layers, and highlight framework "magic" that isn't obvious from code alone.

**Key Principles:**
- **Layer awareness** - Always identify which architectural layer the file belongs to
- **Breadcrumb navigation** - Show exactly where imports come from and where functions are called
- **Flow documentation** - Highlight when crossing layers (route→controller→service→database)
- **Framework transparency** - Explain what FastAPI, SQLAlchemy, Pydantic do automatically
- **Conciseness** - Mostly single-line comments; 2-3 lines max for complex concepts
- **No over-commenting** - Don't restate obvious code; add context instead

---

## Breadcrumb Comments

**Purpose:** Help developers quickly navigate between files by showing where imports come from and where functions get called.

### Import Breadcrumbs

Always show where imports are defined:

```python
# User model - defined in app/models/user.py
from app.models.user import User

# Password hashing utility - defined in app/utils/auth.py
from app.utils.auth import hash_password
```

For grouped imports with multiple functions:

```python
# Service functions - these interact with the database
# Defined in: app/services/auth_service.py
from app.services.auth_service import (
    create_user,           # ← Creates new user in database
    get_user_by_email,     # ← Queries user by email
    get_user_by_id,        # ← Queries user by ID
)
```

### Function Call Breadcrumbs

Show where each function is called from and what it calls:

```python
# CREATE USER
# Called by: app/controllers/auth_controller.py → signup()
def create_user(db: Session, email: str, password: str, username: str) -> User:
    """Create new user in database - password is hashed before storing"""

    # Hash password using bcrypt (from app/utils/auth.py)
    hashed = hash_password(password)

    # Calls: app/utils/auth.py → hash_password()
    user = create_user(db, email=email, password=password, username=username)
```

### Return Type Breadcrumbs

Show what type is returned and where it's defined:

```python
    return user  # ← Returns User model (from app/models/user.py)
```

---

## Layer Identification

Every file should start with a header comment identifying its architectural layer:

### Routes Layer
```python
# ROUTES LAYER: HTTP entry point - receives requests, validates data, calls controllers
```

### Controller Layer
```python
# CONTROLLER LAYER: Business logic orchestration - coordinates services, handles workflows
```

### Service Layer
```python
# SERVICE LAYER: Data access - handles database CRUD operations
```

### Model Layer
```python
# MODEL LAYER: Database schema definitions - SQLAlchemy ORM models map to PostgreSQL tables
```

### Schema Layer
```python
# SCHEMAS: Pydantic models for request/response validation - FastAPI uses these automatically
```

### Utilities
```python
# UTILITIES: Password hashing and JWT token management - called by controllers/services
```

### Application Entry
```python
# APPLICATION ENTRY POINT: FastAPI app initialization - run with: uvicorn app.main:app --reload
```

---

## Import Comments (with Breadcrumbs)

Highlight important imports, explain their purpose, AND show where they're defined:

### Routes
```python
# SQLAlchemy Session type - represents database connection
from sqlalchemy.orm import Session

# SessionLocal = our connection factory for Postgres
# Every time we call SessionLocal(), we get a fresh DB session
# Defined in: app/db/session.py
from app.db.session import SessionLocal

# These are controller functions.
# Our route will call these instead of putting logic in routes.
# Defined in: app/controllers/auth_controller.py
from app.controllers.auth_controller import (
    signup,                        # ← Handles signup workflow
    login,                         # ← Handles login workflow
    get_current_user_from_token,  # ← Validates JWT and gets user
)

# These are Pydantic models for validating request/response bodies.
# Defined in: app/schemas/auth.py
from app.schemas.auth import SignupRequest, LoginRequest, TokenResponse, UserResponse
```

### Controllers
```python
# FastAPI's HTTPException for throwing errors (404, 401, etc.)
# status gives us HTTP status codes (status.HTTP_400_BAD_REQUEST, etc.)
from fastapi import HTTPException, status

# Service functions - these interact with the database
# Defined in: app/services/auth_service.py
from app.services.auth_service import (
    create_user,           # ← Creates new user in database
    get_user_by_email,     # ← Queries user by email
    get_user_by_id,        # ← Queries user by ID
)

# Utility functions for security
# Defined in: app/utils/auth.py
from app.utils.auth import (
    verify_password,        # ← Compares plain password with bcrypt hash
    create_access_token,    # ← Generates JWT token
    decode_access_token     # ← Validates and decodes JWT token
)
```

### Services
```python
# User model - defined in app/models/user.py
# This is the SQLAlchemy ORM model that maps to the "users" table
from app.models.user import User

# Password hashing utility - defined in app/utils/auth.py
from app.utils.auth import hash_password
```

---

## Function/Method Comments

### Routes
Document the HTTP method, endpoint, and what the route does:

```python
# POST /auth/signup - Register a new user
@router.post("/signup", response_model=TokenResponse)
def signup_route(payload: SignupRequest, db: Session = Depends(get_db)):
    # FastAPI auto-validates payload against SignupRequest schema
    # Depends(get_db) injects a database session into 'db' parameter

    # Delegate to controller layer - controllers handle business logic
    return signup(...)
```

### Controllers
Describe the workflow and note service calls:

```python
# Signup workflow - orchestrates user creation, profile creation, and token generation
def signup(db: Session, email: str, password: str, username: str) -> dict:
    # 1. Check if user already exists - call service layer to query database
    existing = get_user_by_email(db, email)

    # 2. Create user - service will hash password and insert into database
    user = create_user(db, email=email, password=password, username=username)

    # 3. Create user profile - sets up gamification stats (streaks, exam counts)
    create_profile(db, user_id=user.id)

    # 4. Create JWT token - utility function creates signed token with 15min expiration
    token = create_access_token({"user_id": user.id})

    # Return token for immediate authentication
    return {"access_token": token, "user_id": user.id, "username": user.username}
```

### Services
Explain database operations and ORM behavior:

```python
def create_user(db: Session, email: str, password: str, username: str) -> User:
    """Create a new user in database - password is hashed before storing"""
    # Hash password using bcrypt - NEVER store plain text passwords
    hashed = hash_password(password)

    # Create User model instance - SQLAlchemy will map this to database row
    user = User(...)

    db.add(user)  # Add to session (not yet in database)
    db.commit()  # Execute SQL INSERT - saves to database
    db.refresh(user)  # Reload from database to get auto-generated ID
    return user
```

---

## Inline Comments

### Framework Magic
Explain what the framework does automatically:

```python
# FastAPI auto-validates payload against SignupRequest schema

# Depends(get_db) injects a database session into 'db' parameter

# response_model=UserResponse ensures we don't leak password hash

# FastAPI auto-converts SQLAlchemy User model to UserResponse JSON
```

### Layer Transitions
Note when crossing architectural boundaries:

```python
# Delegate to controller layer - controllers handle business logic

# Call service to query database

# Call controller to decode token and fetch user

# Execute SQL INSERT - saves to database
```

### Security/Best Practices
Highlight security considerations:

```python
# Hash password using bcrypt - NEVER store plain text passwords

# Generic error message prevents email enumeration attacks

# ⚠️ SECRET_KEY should be in environment variables in production
```

### Data Flow
Explain transformations and what data contains:

```python
# Copy to avoid mutating original dict

# Add expiration to payload

# Returns dict with user_id and exp
```

---

## Model Field Comments

Use inline comments for field purposes:

```python
class User(Base):
    """User account model - maps to 'users' table in PostgreSQL"""
    __tablename__ = "users"

    # Primary key - auto-incrementing integer, indexed for fast lookups
    id = Column(Integer, primary_key=True, index=True)

    # Authentication fields - unique constraints prevent duplicates
    email = Column(String, unique=True, index=True, nullable=False)  # Used for login
    username = Column(String, unique=True, index=True, nullable=False)  # Display name
    hashed_password = Column(String, nullable=False)  # Bcrypt hash (never plain text!)

    # Account status flags
    is_active = Column(Boolean, default=True)  # Can disable accounts without deleting
    is_verified = Column(Boolean, default=False)  # Email verification (not implemented yet)
```

---

## Docstrings

Use brief, single-line docstrings for functions:

```python
def get_user_by_email(db: Session, email: str) -> User | None:
    """Query database for user by email - used for login and duplicate checking"""
    return db.query(User).filter(User.email == email).first()
```

For classes, add context about the model's purpose:

```python
class SignupRequest(BaseModel):
    """Request body for POST /auth/signup - validated by FastAPI before reaching route"""
    ...
```

---

## What NOT to Comment

Avoid these common over-commenting patterns:

### ❌ Restating Obvious Code
```python
# Set email to email parameter
user.email = email

# Return user
return user
```

### ❌ Commenting Every Line
```python
# Create variable
x = 5
# Add 1 to x
x = x + 1
# Print x
print(x)
```

### ❌ Redundant Comments
```python
def create_user(...):
    """Create a user"""  # Docstring just restates function name
```

---

## Security and Environment Variables

### Environment Variables (.env)

**Critical Rule:** NEVER hardcode secrets, API keys, or credentials in code files.

#### What Belongs in .env
```python
# ❌ NEVER DO THIS - hardcoded secrets in code
JWT_SECRET = "my_secret_key_123"
DATABASE_URL = "postgresql://user:password@localhost/db"

# ✅ ALWAYS DO THIS - load from environment
import os
JWT_SECRET = os.getenv("JWT_SECRET")
DATABASE_URL = os.getenv("DATABASE_URL")
```

#### Environment Variable Loading
Always load `.env` at the start of `main.py`:

```python
# Load environment variables from .env file before anything else
# python-dotenv reads .env and makes variables available via os.getenv()
from dotenv import load_dotenv
load_dotenv()  # Must be called before importing modules that use env vars
```

#### Comment Style for Environment Variables
```python
# JWT Configuration - loaded from environment variables (.env file)
# Environment variables are loaded in app/main.py via load_dotenv()
SECRET_KEY = os.getenv("JWT_SECRET", "fallback_dev_secret_key")  # ← Loaded from .env
ALGORITHM = "HS256"  # HMAC with SHA-256 signing algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRATION_MINUTES", "15"))  # ← Loaded from .env
```

#### Security Comments
Add these types of security-focused comments:

```python
# SECURITY: Never commit .env files to git (already in .gitignore)

# SECURITY: JWT_SECRET must be kept secret - anyone with this can forge tokens

# SECURITY: Hash password before storing - NEVER store plain text passwords!

# SECURITY: Generic error message prevents email enumeration attacks

# SECURITY: Validate required env vars at startup to fail fast
```

#### Environment Variable Validation
Always validate critical environment variables at startup:

```python
# ============================================
# VALIDATE REQUIRED ENVIRONMENT VARIABLES
# ============================================
# SECURITY: Fail fast if critical environment variables are missing
# This prevents the app from running with insecure fallback values
import os
import sys

REQUIRED_ENV_VARS = [
    "DATABASE_URL",    # PostgreSQL connection string
    "JWT_SECRET",      # Secret key for signing JWT tokens
]

missing_vars = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
if missing_vars:
    print(f"ERROR: Missing required environment variables: {missing_vars}", file=sys.stderr)
    sys.exit(1)  # Exit with error code 1 (prevents app from starting)
```

### Security Best Practices for Learning

Since this is a **learning project**, comments should teach security concepts:

#### Password Security
```python
# Hash password before storing (call utility function)
# NEVER store plain text passwords in database!
# Bcrypt is intentionally slow to resist brute-force attacks
hashed = hash_password(password)  # ← Calls app/utils/auth.py
```

#### JWT Token Security
```python
# Create JWT token - utility function creates signed token with 15min expiration
# Token structure:
# - Header: {"alg": "HS256", "typ": "JWT"}
# - Payload: {"user_id": 123, "exp": 1699999999}
# - Signature: HMAC-SHA256(header + payload, SECRET_KEY)
token = create_access_token({"user_id": user.id})
```

#### Database Credentials
```python
# PostgreSQL connection string format:
# postgresql://username:password@host:port/database
#
# Development: Default postgres user is OK for learning
# Production: Create dedicated user with limited permissions
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/billings")
```

#### Docker Compose Security
```yaml
environment:
  # Load credentials from .env file (with fallback defaults for development)
  # Security: Change these in production! See .env.example
  POSTGRES_USER: ${POSTGRES_USER:-postgres}
  POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-postgres}
```

### .env.example Template

Every project should have a `.env.example` file documenting required variables:

```bash
# ==============================================
# ENVIRONMENT CONFIGURATION TEMPLATE
# ==============================================
# Setup Instructions:
# 1. Copy this file: cp .env.example .env
# 2. Generate JWT secret: python -c "import secrets; print(secrets.token_urlsafe(32))"
# 3. Replace placeholder values with your actual configuration
# 4. NEVER commit .env to git (it's already in .gitignore)
# ==============================================

# Database connection string
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/billings

# JWT secret key (generate a unique secret for each environment!)
JWT_SECRET=your-generated-secret-key-here-minimum-32-characters

# JWT expiration time in minutes
JWT_EXPIRATION_MINUTES=15
```

### Security Comment Checklist

When writing code that involves security, include comments explaining:

- ✅ **Why** secrets are loaded from environment variables
- ✅ **What** happens if a secret is compromised
- ✅ **How** to generate secure secrets
- ✅ **Where** environment variables are loaded (.env file)
- ✅ **When** to use different values (development vs production)

---

## Example Prompt for Claude

When asking Claude to add comments to new code in future conversations, use this prompt:

```
Add teaching comments with breadcrumbs to this code following the Billings backend
commenting style (see COMMENTING_STYLE_GUIDE.md). Include:

1. Layer identification header (e.g., "ROUTES LAYER: ...")

2. Import breadcrumbs showing where each import is defined:
   - "Defined in: app/services/auth_service.py"
   - For grouped imports, add inline comments for each function

3. Function/class header comments showing:
   - "Called by: app/controllers/auth_controller.py → signup()"
   - "Used by: app/api/v1/auth_routes.py"

4. Inline comments for:
   - Framework magic (FastAPI, Pydantic, SQLAlchemy auto-behavior)
   - Layer transitions ("Calls: app/services/auth_service.py → create_user()")
   - Security/best practices notes
   - Data transformations
   - Return type breadcrumbs ("← Returns User model from app/models/user.py")

5. Model field inline comments explaining purpose (with sections for related fields)

6. Brief docstrings (single-line preferred)

Keep comments concise and teaching-focused. Show WHERE things come from and WHERE
they're called. This helps developers navigate the codebase using F12 (Go to Definition).
```

---

## Full File Example

Here's a complete example showing the style in action:

**`backend/app/api/v1/auth_routes.py`**

```python
# ROUTES LAYER: HTTP entry point - receives requests, validates data, calls controllers
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
# Import controller functions - routes delegate business logic to controllers
from app.controllers.auth_controller import (
    signup,
    login,
    get_current_user_from_token,
)
# Import Pydantic schemas - these validate request/response data automatically
from app.schemas.auth import SignupRequest, LoginRequest, TokenResponse, UserResponse

# All routes here are prefixed with /auth (e.g., /auth/signup)
router = APIRouter(prefix="/auth", tags=["Auth"])


# DEPENDENCY INJECTION: FastAPI calls this function to provide DB sessions to routes
def get_db():
    db = SessionLocal()  # Create a new database session
    try:
        yield db  # Provide session to the route function
    finally:
        db.close()  # Always close session after request (even if error occurs)


# POST /auth/signup - Register a new user
@router.post("/signup", response_model=TokenResponse)
def signup_route(payload: SignupRequest, db: Session = Depends(get_db)):
    # FastAPI auto-validates payload against SignupRequest schema
    # Depends(get_db) injects a database session into 'db' parameter

    # Delegate to controller layer - controllers handle business logic
    return signup(
        db=db,
        email=payload.email,
        password=payload.password,
        username=payload.username,
    )


# POST /auth/login - Authenticate existing user
@router.post("/login", response_model=TokenResponse)
def login_route(payload: LoginRequest, db: Session = Depends(get_db)):
    # FastAPI validates payload (email format, required fields)

    # Call controller to handle authentication logic
    return login(
        db=db,
        email=payload.email,
        password=payload.password,
    )


# GET /auth/me?token=xxx - Get current user info from JWT token
@router.get("/me", response_model=UserResponse)
def get_me_route(token: str, db: Session = Depends(get_db)):
    # Token comes from query parameter (?token=xxx)
    # response_model=UserResponse ensures we don't leak password hash

    # Call controller to decode token and fetch user
    user = get_current_user_from_token(db, token)

    # FastAPI auto-converts SQLAlchemy User model to UserResponse JSON
    return user
```

---

## Quick Reference

**Layer Headers:**
- Routes: `# ROUTES LAYER: HTTP entry point - receives requests, validates data, calls controllers`
- Controllers: `# CONTROLLER LAYER: Business logic orchestration - coordinates services, handles workflows`
- Services: `# SERVICE LAYER: Data access - handles database CRUD operations`
- Models: `# MODEL LAYER: Database schema definitions - SQLAlchemy ORM models map to PostgreSQL tables`
- Schemas: `# SCHEMAS: Pydantic models for request/response validation - FastAPI uses these automatically`
- Utils: `# UTILITIES: [specific purpose] - called by [who calls it]`
- Main: `# APPLICATION ENTRY POINT: FastAPI app initialization - run with: uvicorn app.main:app --reload`

**Comment Focus Areas:**
1. Framework automation (FastAPI, Pydantic, SQLAlchemy)
2. Layer transitions (route→controller→service→db)
3. Security considerations
4. Data transformations
5. Field/parameter purposes (when not obvious)

**Golden Rule:** If a new backend developer would ask "how does this work?" or "why is this here?", add a comment.
