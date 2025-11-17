# Backend Learning Guide - Complete Overview

This document provides a comprehensive overview of the Billings backend authentication system. It explains the project structure, how files reference each other, how dependencies work, and the complete flow of data through the system.

---

## Table of Contents

1. [Project Structure Overview](#project-structure-overview)
2. [Layer Architecture Explained](#layer-architecture-explained)
3. [FastAPI Dependencies Deep Dive](#fastapi-dependencies-deep-dive)
4. [File-by-File Breakdown](#file-by-file-breakdown)
5. [Code Flow Examples](#code-flow-examples)
6. [JWT Authentication Explained](#jwt-authentication-explained)
7. [Import Reference Map](#import-reference-map)

---

## Project Structure Overview

```
backend/
├── .env                          # Environment variables (secrets, config)
├── app/
│   ├── main.py                   # FastAPI app entry point (starts server)
│   ├── api/
│   │   └── v1/
│   │       └── auth_routes.py    # HTTP endpoints (receives requests)
│   ├── controllers/
│   │   └── auth_controller.py    # Business logic (orchestrates services)
│   ├── services/
│   │   ├── auth_service.py       # Database operations (CRUD for users)
│   │   └── profile_service.py    # Database operations (CRUD for profiles)
│   ├── models/
│   │   ├── user.py               # Database schema (User & UserProfile tables)
│   │   └── question.py           # Database schema (Question table)
│   ├── schemas/
│   │   └── auth.py               # Pydantic models (request/response validation)
│   ├── utils/
│   │   └── auth.py               # Helper functions (JWT, password hashing)
│   └── db/
│       ├── base.py               # SQLAlchemy base class
│       └── session.py            # Database connection setup
└── venv/                         # Python virtual environment
```

### What Each Folder Does

| Folder | Purpose | Can Import From | Cannot Import From |
|--------|---------|-----------------|-------------------|
| **api/** | HTTP layer - receives requests | controllers, schemas, utils, db | services, models |
| **controllers/** | Business logic layer | services, utils | routes, db |
| **services/** | Database layer | models, utils | routes, controllers |
| **models/** | Database schema | Nothing (just SQLAlchemy) | Everything |
| **schemas/** | Data validation | Nothing (just Pydantic) | Everything |
| **utils/** | Helpers | Nothing initially | routes, controllers, services |
| **db/** | Database setup | models | routes, controllers, services |

---

## Layer Architecture Explained

The backend follows a **3-layer architecture** to keep code organized:

```
┌─────────────────────────────────────────────────────────┐
│                    HTTP REQUEST                         │
│          POST /api/v1/auth/login                        │
│          Body: {"email": "...", "password": "..."}      │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  LAYER 1: ROUTES (auth_routes.py)                      │
│  ─────────────────────────────────────────────────      │
│  • Receives HTTP request                                │
│  • Validates JSON against Pydantic schema               │
│  • Injects database session via get_db()                │
│  • Calls CONTROLLER function                            │
│  • Returns JSON response                                │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  LAYER 2: CONTROLLERS (auth_controller.py)             │
│  ─────────────────────────────────────────────────      │
│  • Orchestrates business logic                          │
│  • Calls SERVICES to query database                     │
│  • Calls UTILITIES for JWT/password operations          │
│  • Makes decisions (if user exists, throw error)        │
│  • Returns data dict to route                           │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  LAYER 3: SERVICES (auth_service.py)                   │
│  ─────────────────────────────────────────────────      │
│  • Executes database queries (SELECT, INSERT, etc.)     │
│  • Uses SQLAlchemy ORM to interact with PostgreSQL      │
│  • Returns model objects (User, UserProfile)            │
│  • NO business logic (just data access)                 │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│              POSTGRESQL DATABASE                        │
│  Tables: users, user_profiles, questions                │
└─────────────────────────────────────────────────────────┘
```

### Why This Architecture?

1. **Separation of Concerns** - Each layer has ONE job
2. **Testability** - Can test each layer independently
3. **Reusability** - Controllers can call the same service functions
4. **Maintainability** - Changes in one layer don't affect others

---

## FastAPI Dependencies Deep Dive

### What Are Dependencies?

**Dependencies** are functions that FastAPI runs BEFORE your route handler. They:
- Provide resources (database sessions, authenticated users)
- Validate preconditions (check if user is logged in)
- Extract data (get user from JWT token)

### Dependency Syntax

```python
from fastapi import Depends

def get_db():
    """This is a DEPENDENCY - FastAPI will call this automatically"""
    db = SessionLocal()
    try:
        yield db  # Give database session to route
    finally:
        db.close()  # Clean up after route finishes

@router.post("/login")
def login_route(db: Session = Depends(get_db)):
    """
    FastAPI automatically calls get_db() and injects the result into 'db'
    """
    # db is now a live database session!
    user = db.query(User).filter(User.email == "test@example.com").first()
```

### How Dependencies Work (Step by Step)

When a request comes to `POST /api/v1/auth/login`:

```
1. Request arrives: POST /api/v1/auth/login
                    Body: {"email": "test@example.com", "password": "pass123"}

2. FastAPI sees: db: Session = Depends(get_db)
   ↓
   Runs get_db() function → creates database session

3. FastAPI sees: payload: LoginRequest
   ↓
   Validates JSON against LoginRequest schema

4. FastAPI calls: login_route(payload=LoginRequest(...), db=Session(...))
   ↓
   Your route function executes

5. Route finishes
   ↓
   FastAPI runs the "finally" block in get_db() → closes database connection
```

### Our Two Dependencies

#### Dependency 1: `get_db()` (in auth_routes.py)

**Location**: `backend/app/api/v1/auth_routes.py:31-44`

**Purpose**: Provides a database session to routes

**Code**:
```python
def get_db():
    db = SessionLocal()  # Open connection to PostgreSQL
    try:
        yield db  # Give connection to route
    finally:
        db.close()  # Always close (even if route crashes)
```

**Used By**:
- `signup_route()` - needs DB to create user
- `login_route()` - needs DB to find user
- `get_me_route()` - needs DB to validate user still exists
- `logout_route()` - needs DB to validate user is authenticated

**Why It's a Dependency**:
- Every route needs database access
- Avoids repeating `db = SessionLocal()` in every route
- Guarantees connection is closed (no connection leaks)

#### Dependency 2: `get_current_user()` (in utils/auth.py)

**Location**: `backend/app/utils/auth.py:139-198`

**Purpose**: Extracts and validates authenticated user from JWT token

**Code Flow**:
```python
def get_current_user(
    db: Session,  # ← Injected from Depends(get_db)
    credentials: HTTPAuthorizationCredentials = Depends(security),  # ← Extracts "Bearer <token>"
):
    # Step 1: Extract token from header
    token = credentials.credentials

    # Step 2: Decode JWT and validate
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(401, "Invalid token")

    # Step 3: Get user_id from token
    user_id = payload.get("user_id")

    # Step 4: Query database for user
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(401, "User not found")

    # Return authenticated user
    return user
```

**Used By**:
- `get_me_route()` - needs to know WHO is requesting their info
- `logout_route()` - needs to validate user is logged in

**Why It's a Dependency**:
- Protected routes need to verify authentication
- Avoids repeating JWT validation code in every protected route
- Centralizes authentication logic in one place

### Dependency Injection Order

When a protected route is called:

```python
@router.get("/me")
def get_me_route(
    current_user = Depends(get_current_user),  # ← Runs SECOND
    db: Session = Depends(get_db)              # ← Runs FIRST
):
    return current_user
```

**Execution Order**:
1. `get_db()` runs → creates database session
2. `get_current_user(db=<session>)` runs → uses that session to query for user
3. `get_me_route(current_user=<User>, db=<session>)` runs → your route logic
4. `get_db()` finally block runs → closes database connection

**Important**: `get_current_user` depends on `db`, so `db` must be created first!

---

## File-by-File Breakdown

### 1. `.env` - Environment Variables

**Path**: `backend/.env`

**Purpose**: Store secrets and configuration (never commit to Git!)

**Contents**:
```bash
JWT_SECRET=your_super_secret_jwt_key_change_this_in_production_please_make_it_long_and_random
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/billings
JWT_EXPIRATION_MINUTES=15
```

**Used By**:
- `main.py` - loads env vars via `load_dotenv()`
- `utils/auth.py` - reads JWT_SECRET and JWT_EXPIRATION_MINUTES
- `db/session.py` - reads DATABASE_URL

**Why Environment Variables?**
- Keeps secrets out of code
- Different configs for dev/staging/production
- Can change settings without code changes

---

### 2. `main.py` - Application Entry Point

**Path**: `backend/app/main.py`

**Purpose**: Initialize FastAPI app, configure CORS, register routes

**Imports**:
```python
from dotenv import load_dotenv           # Load .env file
from fastapi import FastAPI              # FastAPI framework
from fastapi.middleware.cors import CORSMiddleware  # CORS config
from app.db.base import Base             # SQLAlchemy base
from app.db.session import engine        # Database engine
from app.models.user import User, UserProfile  # Import models
from app.models.question import Question       # Import models
from app.api.v1.auth_routes import router as auth_router  # Routes
```

**Key Code**:
```python
# 1. Load environment variables FIRST
load_dotenv()

# 2. Create database tables (if they don't exist)
Base.metadata.create_all(bind=engine)

# 3. Initialize FastAPI app
app = FastAPI(title="Billings API")

# 4. Configure CORS (allow React frontend to make requests)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,  # Allow cookies/auth headers
    allow_methods=["*"],     # Allow all HTTP methods
    allow_headers=["*"],     # Allow all headers
)

# 5. Register routes
app.include_router(auth_router, prefix="/api/v1")
```

**What This Creates**:
- POST /api/v1/auth/signup
- POST /api/v1/auth/login
- GET /api/v1/auth/me
- POST /api/v1/auth/logout

**Called By**: `uvicorn app.main:app` (when you start the server)

---

### 3. `auth_routes.py` - HTTP Endpoints (Routes Layer)

**Path**: `backend/app/api/v1/auth_routes.py`

**Purpose**: Define HTTP endpoints that receive requests

**Imports**:
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import SessionLocal           # For get_db()
from app.controllers.auth_controller import (
    signup,  # ← Controller function
    login,   # ← Controller function
)
from app.schemas.auth import SignupRequest, LoginRequest, TokenResponse, UserResponse
from app.utils.auth import get_current_user       # ← Dependency
```

**Key Functions**:

#### `get_db()` - Dependency
```python
def get_db():
    """Creates database session for each request"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

#### `signup_route()` - POST /auth/signup
```python
@router.post("/signup", response_model=TokenResponse)
def signup_route(payload: SignupRequest, db: Session = Depends(get_db)):
    # 1. FastAPI validates 'payload' against SignupRequest schema
    # 2. FastAPI runs get_db() and injects session into 'db'
    # 3. Call controller (controller does the work)
    return signup(
        db=db,
        email=payload.email,
        password=payload.password,
        username=payload.username,
    )
```

**What Happens**:
1. Request: `POST /api/v1/auth/signup` with JSON body
2. FastAPI validates JSON matches `SignupRequest` schema
3. FastAPI calls `get_db()` → creates database session
4. FastAPI calls `signup_route(payload=..., db=...)`
5. Route calls `signup()` controller function
6. Controller returns `{"access_token": "...", "token_type": "bearer", ...}`
7. FastAPI validates response matches `TokenResponse` schema
8. FastAPI converts to JSON and sends to client

#### `login_route()` - POST /auth/login
```python
@router.post("/login", response_model=TokenResponse)
def login_route(payload: LoginRequest, db: Session = Depends(get_db)):
    return login(
        db=db,
        email=payload.email,
        password=payload.password,
    )
```

**What Happens**:
1. Request: `POST /api/v1/auth/login` with JSON body
2. Validates JSON → Creates DB session → Calls login() controller
3. Controller verifies password and returns token
4. Returns JWT token to client

#### `get_me_route()` - GET /auth/me (Protected)
```python
@router.get("/me", response_model=UserResponse)
def get_me_route(
    current_user = Depends(get_current_user),  # ← Requires authentication!
    db: Session = Depends(get_db)
):
    return current_user
```

**What Happens**:
1. Request: `GET /api/v1/auth/me` with `Authorization: Bearer <token>` header
2. FastAPI calls `get_db()` → creates session
3. FastAPI calls `get_current_user(db=session)`:
   - Extracts token from Authorization header
   - Validates JWT signature and expiration
   - Queries database for user by ID from token
   - Raises 401 error if invalid
   - Returns User model if valid
4. Route returns User model
5. FastAPI converts User to UserResponse JSON (excludes password hash)

#### `logout_route()` - POST /auth/logout (Protected)
```python
@router.post("/logout")
def logout_route(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    # Just validates user is authenticated
    # Client must delete token from localStorage
    return {"message": "Logout successful", "detail": "Please remove the access token from client storage"}
```

**What Happens**:
1. Validates user is authenticated (via `get_current_user`)
2. Returns success message
3. Client deletes token from localStorage/cookies

**Calls To**:
- `signup()` in `auth_controller.py`
- `login()` in `auth_controller.py`
- `get_current_user()` in `utils/auth.py`
- `get_db()` (local function)

---

### 4. `auth_controller.py` - Business Logic (Controller Layer)

**Path**: `backend/app/controllers/auth_controller.py`

**Purpose**: Orchestrate services and make business decisions

**Imports**:
```python
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.services.auth_service import (
    create_user,        # ← Service function
    get_user_by_email,  # ← Service function
)
from app.services.profile_service import create_profile  # ← Service function
from app.utils.auth import (
    verify_password,      # ← Utility function
    create_access_token,  # ← Utility function
)
```

**Key Functions**:

#### `signup()` - Signup Workflow
```python
def signup(db: Session, email: str, password: str, username: str) -> dict:
    # Step 1: Check if email already exists
    existing = get_user_by_email(db, email)  # ← Call SERVICE
    if existing:
        raise HTTPException(400, "Email already registered.")

    # Step 2: Create user
    user = create_user(db, email=email, password=password, username=username)  # ← Call SERVICE

    # Step 3: Create profile
    create_profile(db, user_id=user.id)  # ← Call SERVICE

    # Step 4: Generate JWT token
    token = create_access_token({"user_id": user.id})  # ← Call UTILITY

    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.username,
    }
```

**What This Does**:
1. Checks if email is taken (business logic decision)
2. Creates user in database (calls service)
3. Creates profile in database (calls service)
4. Generates JWT token (calls utility)
5. Returns token dict to route

#### `login()` - Login Workflow
```python
def login(db: Session, email: str, password: str) -> dict:
    # Step 1: Find user
    user = get_user_by_email(db, email)  # ← Call SERVICE
    if not user:
        raise HTTPException(401, "Invalid email or password.")  # Generic error (security)

    # Step 2: Verify password
    if not verify_password(password, user.hashed_password):  # ← Call UTILITY
        raise HTTPException(401, "Invalid email or password.")

    # Step 3: Generate token
    token = create_access_token({"user_id": user.id})  # ← Call UTILITY

    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.username,
    }
```

**What This Does**:
1. Looks up user by email (calls service)
2. Verifies password matches hash (calls utility)
3. Generates JWT token (calls utility)
4. Returns token dict to route

**Called By**:
- `signup_route()` in `auth_routes.py`
- `login_route()` in `auth_routes.py`

**Calls To**:
- `create_user()` in `auth_service.py`
- `get_user_by_email()` in `auth_service.py`
- `create_profile()` in `profile_service.py`
- `verify_password()` in `utils/auth.py`
- `create_access_token()` in `utils/auth.py`

---

### 5. `auth_service.py` - Database Operations (Service Layer)

**Path**: `backend/app/services/auth_service.py`

**Purpose**: Execute database queries (CRUD operations)

**Imports**:
```python
from sqlalchemy.orm import Session
from app.models.user import User  # ← Database model
from app.utils.auth import hash_password  # ← Utility for password hashing
```

**Key Functions**:

#### `create_user()` - Insert User into Database
```python
def create_user(db: Session, email: str, password: str, username: str) -> User:
    # Hash password BEFORE storing (NEVER store plain text!)
    hashed = hash_password(password)  # ← Call UTILITY

    # Create User model instance
    user = User(
        email=email,
        hashed_password=hashed,
        username=username,
    )

    db.add(user)      # Add to session (not yet in DB)
    db.commit()       # Execute SQL INSERT → saves to database
    db.refresh(user)  # Reload from DB to get auto-generated ID

    return user  # ← Returns User model
```

**SQL Equivalent**:
```sql
INSERT INTO users (email, hashed_password, username, is_active, is_verified, created_at, updated_at)
VALUES ('test@example.com', '$2b$12$...', 'john_doe', true, false, NOW(), NOW())
RETURNING *;
```

#### `get_user_by_email()` - Query User by Email
```python
def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()
```

**SQL Equivalent**:
```sql
SELECT * FROM users WHERE email = 'test@example.com' LIMIT 1;
```

**Returns**:
- `User` model if found
- `None` if not found

**Called By**:
- `signup()` in `auth_controller.py` (checks if email exists)
- `login()` in `auth_controller.py` (finds user for login)

**Calls To**:
- `hash_password()` in `utils/auth.py`

---

### 6. `profile_service.py` - Profile Database Operations

**Path**: `backend/app/services/profile_service.py`

**Purpose**: Create and manage user profiles

**Imports**:
```python
from sqlalchemy.orm import Session
from app.models.user import UserProfile  # ← Database model
```

**Key Functions**:

#### `create_profile()` - Create User Profile
```python
def create_profile(db: Session, user_id: int) -> UserProfile:
    profile = UserProfile(
        user_id=user_id,
        study_streak_current=0,
        study_streak_longest=0,
        total_exams_taken=0,
        total_questions_answered=0,
    )

    db.add(profile)
    db.commit()
    db.refresh(profile)

    return profile
```

**SQL Equivalent**:
```sql
INSERT INTO user_profiles (user_id, study_streak_current, study_streak_longest, total_exams_taken, total_questions_answered)
VALUES (1, 0, 0, 0, 0)
RETURNING *;
```

**Called By**:
- `signup()` in `auth_controller.py` (creates profile after creating user)

---

### 7. `auth.py` (Utils) - Helper Functions

**Path**: `backend/app/utils/auth.py`

**Purpose**: Password hashing, JWT creation/validation, authentication dependency

**Imports**:
```python
from passlib.context import CryptContext  # For bcrypt password hashing
import jwt  # For JWT token creation/validation
from datetime import datetime, timedelta
import os  # For reading environment variables
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
```

**Configuration**:
```python
# Bcrypt password hasher
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings from .env
SECRET_KEY = os.getenv("JWT_SECRET", "fallback_dev_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRATION_MINUTES", "15"))

# HTTPBearer security scheme (extracts "Authorization: Bearer <token>")
security = HTTPBearer()
```

**Key Functions**:

#### `hash_password()` - Hash Password with Bcrypt
```python
def hash_password(password: str) -> str:
    return pwd_context.hash(password)
```

**Example**:
```python
hash_password("mypassword123")
# Returns: "$2b$12$KIXvZ9Q2r8Y.../aBcD..." (60 characters)
```

**Called By**:
- `create_user()` in `auth_service.py`

#### `verify_password()` - Verify Password Against Hash
```python
def verify_password(raw_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(raw_password, hashed_password)
```

**Example**:
```python
verify_password("mypassword123", "$2b$12$KIXvZ9Q2r8Y.../aBcD...")
# Returns: True (password matches)

verify_password("wrongpassword", "$2b$12$KIXvZ9Q2r8Y.../aBcD...")
# Returns: False (password doesn't match)
```

**Called By**:
- `login()` in `auth_controller.py`

#### `create_access_token()` - Generate JWT Token
```python
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()

    # Set expiration (default 15 minutes from now)
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    # Sign with SECRET_KEY
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
```

**Example**:
```python
token = create_access_token({"user_id": 123})
# Returns: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjMsImV4cCI6MTY5OTk5OTk5OX0.signature..."

# Token payload (decoded):
# {
#   "user_id": 123,
#   "exp": 1699999999  (expiration timestamp)
# }
```

**Called By**:
- `signup()` in `auth_controller.py`
- `login()` in `auth_controller.py`

#### `decode_access_token()` - Validate and Decode JWT
```python
def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload  # {"user_id": 123, "exp": 1699999999}
    except jwt.ExpiredSignatureError:
        return None  # Token expired
    except jwt.InvalidTokenError:
        return None  # Invalid signature or format
```

**Example**:
```python
payload = decode_access_token("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
# Returns: {"user_id": 123, "exp": 1699999999}

payload = decode_access_token("invalid_token")
# Returns: None
```

**Called By**:
- `get_current_user()` in `utils/auth.py`

#### `get_current_user()` - Dependency for Protected Routes
```python
def get_current_user(
    db: Session,  # ← From Depends(get_db)
    credentials: HTTPAuthorizationCredentials = Depends(security),  # ← From Authorization header
):
    # Step 1: Extract token
    token = credentials.credentials  # "Bearer eyJhbGci..." → "eyJhbGci..."

    # Step 2: Decode and validate
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(401, "Invalid or expired token")

    # Step 3: Get user_id from payload
    user_id = payload.get("user_id")
    if user_id is None:
        raise HTTPException(401, "Invalid token payload")

    # Step 4: Query database
    from app.models.user import User
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(401, "User not found")

    return user  # ← Returns User model
```

**Example Flow**:
```
Request: GET /api/v1/auth/me
Headers: Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

↓ FastAPI extracts "Bearer ..." via HTTPBearer

↓ get_current_user() is called

↓ Decodes JWT → {"user_id": 123, "exp": 1699999999}

↓ Queries database: SELECT * FROM users WHERE id = 123

↓ Returns User model

↓ Route receives User model in 'current_user' parameter
```

**Called By**:
- `get_me_route()` in `auth_routes.py`
- `logout_route()` in `auth_routes.py`

**Calls To**:
- `decode_access_token()` (local function)

---

### 8. `auth.py` (Schemas) - Request/Response Validation

**Path**: `backend/app/schemas/auth.py`

**Purpose**: Define Pydantic models for FastAPI validation

**Imports**:
```python
from pydantic import BaseModel, EmailStr
from datetime import datetime
```

**Key Classes**:

#### `SignupRequest` - Validates POST /auth/signup Body
```python
class SignupRequest(BaseModel):
    email: EmailStr  # Must be valid email format
    password: str
    username: str
```

**Example Valid Request**:
```json
{
  "email": "test@example.com",
  "password": "SecurePass123",
  "username": "john_doe"
}
```

**Example Invalid Request** (FastAPI auto-rejects):
```json
{
  "email": "not-an-email",  // ❌ Invalid email format
  "password": "pass123"
  // ❌ Missing username field
}
```

#### `LoginRequest` - Validates POST /auth/login Body
```python
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
```

#### `TokenResponse` - Validates Auth Response
```python
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: str
```

**Example Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": 1,
  "username": "john_doe"
}
```

#### `UserResponse` - Validates GET /auth/me Response
```python
class UserResponse(BaseModel):
    id: int
    email: EmailStr
    username: str
    is_active: bool
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True  # Allows converting User model to UserResponse
```

**Example Response**:
```json
{
  "id": 1,
  "email": "test@example.com",
  "username": "john_doe",
  "is_active": true,
  "is_verified": false,
  "created_at": "2024-01-15T10:30:00"
}
```

**Note**: `hashed_password` is NOT included (security!)

**Used By**:
- `signup_route()` - uses SignupRequest, TokenResponse
- `login_route()` - uses LoginRequest, TokenResponse
- `get_me_route()` - uses UserResponse

---

### 9. `user.py` (Models) - Database Schema

**Path**: `backend/app/models/user.py`

**Purpose**: Define SQLAlchemy models (database tables)

**Imports**:
```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime
```

**Key Classes**:

#### `User` - Users Table
```python
class User(Base):
    __tablename__ = "users"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Authentication
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    profile = relationship("UserProfile", back_populates="user", uselist=False)
```

**PostgreSQL Table**:
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    username VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
```

#### `UserProfile` - User Profiles Table
```python
class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Gamification stats
    study_streak_current = Column(Integer, default=0)
    study_streak_longest = Column(Integer, default=0)
    total_exams_taken = Column(Integer, default=0)
    total_questions_answered = Column(Integer, default=0)

    # Profile info
    bio = Column(Text, nullable=True)
    avatar_url = Column(String, nullable=True)

    # Relationship
    user = relationship("User", back_populates="profile")
```

**PostgreSQL Table**:
```sql
CREATE TABLE user_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    study_streak_current INTEGER DEFAULT 0,
    study_streak_longest INTEGER DEFAULT 0,
    total_exams_taken INTEGER DEFAULT 0,
    total_questions_answered INTEGER DEFAULT 0,
    bio TEXT,
    avatar_url VARCHAR
);
```

**Used By**:
- `auth_service.py` - queries/creates User models
- `profile_service.py` - creates UserProfile models
- `get_current_user()` - queries User by ID

---

### 10. `session.py` (DB) - Database Connection

**Path**: `backend/app/db/session.py`

**Purpose**: Configure PostgreSQL connection

**Imports**:
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
```

**Configuration**:
```python
# Get database URL from .env
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/billings")

# Create engine (connection pool to PostgreSQL)
engine = create_engine(DATABASE_URL, echo=False)

# Session factory (call SessionLocal() to create a session)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

**Used By**:
- `main.py` - uses `engine` to create tables
- `auth_routes.py` - uses `SessionLocal` in `get_db()`

---

### 11. `base.py` (DB) - SQLAlchemy Base

**Path**: `backend/app/db/base.py`

**Purpose**: Declarative base for all models

**Code**:
```python
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
```

**What This Does**:
- All models inherit from `Base` (User, UserProfile, Question)
- `Base.metadata.create_all(bind=engine)` creates all tables

**Used By**:
- `main.py` - calls `Base.metadata.create_all()`
- `user.py` - `class User(Base)`
- `question.py` - `class Question(Base)`

---

## Code Flow Examples

### Example 1: User Signup Flow

**Request**:
```http
POST /api/v1/auth/signup HTTP/1.1
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "SecurePass123",
  "username": "john_doe"
}
```

**Step-by-Step Execution**:

```
1. Request arrives at FastAPI app
   ↓

2. FastAPI routes to: signup_route() in auth_routes.py
   ↓

3. FastAPI validates JSON against SignupRequest schema
   email: EmailStr ✓
   password: str ✓
   username: str ✓
   ↓

4. FastAPI runs get_db() dependency
   Creates PostgreSQL session
   ↓

5. FastAPI calls signup_route(payload=SignupRequest(...), db=Session(...))
   ↓

6. signup_route() calls signup() controller
   Passes: email="john@example.com", password="SecurePass123", username="john_doe"
   ↓

7. signup() controller executes:

   Step 1: Check if email exists
   existing = get_user_by_email(db, "john@example.com")  # Calls SERVICE
   SQL: SELECT * FROM users WHERE email = 'john@example.com'
   Result: None (user doesn't exist)

   Step 2: Create user
   user = create_user(db, email, password, username)  # Calls SERVICE
   Inside create_user():
     - hashed = hash_password("SecurePass123")  # Calls UTILITY
       Returns: "$2b$12$..." (bcrypt hash)
     - user = User(email=..., hashed_password=hashed, username=...)
     - db.add(user)
     - db.commit()  # SQL: INSERT INTO users (...) VALUES (...)
     - db.refresh(user)  # Reload from DB, user.id = 1
   Returns: User(id=1, email=..., username=...)

   Step 3: Create profile
   create_profile(db, user_id=1)  # Calls SERVICE
   SQL: INSERT INTO user_profiles (user_id, ...) VALUES (1, 0, 0, 0, 0)

   Step 4: Generate JWT
   token = create_access_token({"user_id": 1})  # Calls UTILITY
   Returns: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

   Returns: {
     "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
     "token_type": "bearer",
     "user_id": 1,
     "username": "john_doe"
   }
   ↓

8. signup_route() returns dict to FastAPI
   ↓

9. FastAPI validates response against TokenResponse schema
   ✓ All fields present
   ↓

10. FastAPI converts dict to JSON
   ↓

11. FastAPI runs get_db() finally block
    db.close()  # Closes PostgreSQL connection
    ↓

12. Response sent to client:
```

**Response**:
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJleHAiOjE2OTk5OTk5OTl9.signature",
  "token_type": "bearer",
  "user_id": 1,
  "username": "john_doe"
}
```

---

### Example 2: User Login Flow

**Request**:
```http
POST /api/v1/auth/login HTTP/1.1
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "SecurePass123"
}
```

**Step-by-Step Execution**:

```
1. Request arrives at FastAPI
   ↓

2. Routes to login_route() in auth_routes.py
   ↓

3. FastAPI validates JSON against LoginRequest schema
   ↓

4. FastAPI runs get_db() → creates database session
   ↓

5. login_route() calls login() controller
   ↓

6. login() controller executes:

   Step 1: Find user
   user = get_user_by_email(db, "john@example.com")  # Calls SERVICE
   SQL: SELECT * FROM users WHERE email = 'john@example.com'
   Returns: User(id=1, email=..., hashed_password="$2b$12$...", ...)

   Step 2: Verify password
   is_valid = verify_password("SecurePass123", "$2b$12$...")  # Calls UTILITY
   Bcrypt re-hashes "SecurePass123" and compares with stored hash
   Returns: True ✓

   Step 3: Generate JWT
   token = create_access_token({"user_id": 1})  # Calls UTILITY
   Returns: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

   Returns: {
     "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
     "token_type": "bearer",
     "user_id": 1,
     "username": "john_doe"
   }
   ↓

7. FastAPI converts to JSON and sends response
```

**Response**:
```http
HTTP/1.1 200 OK

{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": 1,
  "username": "john_doe"
}
```

---

### Example 3: Get Current User Flow (Protected Route)

**Request**:
```http
GET /api/v1/auth/me HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJleHAiOjE2OTk5OTk5OTl9.signature
```

**Step-by-Step Execution**:

```
1. Request arrives at FastAPI
   ↓

2. Routes to get_me_route() in auth_routes.py
   ↓

3. FastAPI sees dependencies:
   - db: Session = Depends(get_db)
   - current_user = Depends(get_current_user)
   ↓

4. FastAPI runs get_db() FIRST
   Creates database session
   ↓

5. FastAPI runs get_current_user(db=session) SECOND

   Step 1: HTTPBearer extracts Authorization header
   credentials = HTTPAuthorizationCredentials(
     scheme="Bearer",
     credentials="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
   )

   Step 2: Extract token string
   token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

   Step 3: Decode and validate JWT
   payload = decode_access_token(token)  # Calls UTILITY
   jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
   Validates:
     - Signature is valid ✓
     - Token hasn't expired ✓
   Returns: {"user_id": 1, "exp": 1699999999}

   Step 4: Extract user_id
   user_id = 1

   Step 5: Query database
   user = db.query(User).filter(User.id == 1).first()
   SQL: SELECT * FROM users WHERE id = 1
   Returns: User(id=1, email="john@example.com", username="john_doe", ...)

   Returns: User model
   ↓

6. FastAPI calls get_me_route(current_user=User(...), db=Session(...))
   ↓

7. get_me_route() simply returns current_user
   ↓

8. FastAPI validates response against UserResponse schema
   Converts User model to UserResponse (excludes hashed_password)
   ↓

9. FastAPI sends JSON response
```

**Response**:
```http
HTTP/1.1 200 OK

{
  "id": 1,
  "email": "john@example.com",
  "username": "john_doe",
  "is_active": true,
  "is_verified": false,
  "created_at": "2024-01-15T10:30:00"
}
```

---

## JWT Authentication Explained

### What is JWT?

**JWT (JSON Web Token)** is a signed token that proves a user is authenticated.

**Structure**: `header.payload.signature`

**Example JWT**:
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJleHAiOjE2OTk5OTk5OTl9.signature_hash
│                                      │                                      │
└── Header (base64)                    └── Payload (base64)                   └── Signature (HMAC-SHA256)
```

**Decoded**:
```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "user_id": 1,
    "exp": 1699999999
  },
  "signature": "HMAC-SHA256(header + payload, SECRET_KEY)"
}
```

### How JWT Works in Our System

#### 1. **Login** - Server Creates JWT
```
User logs in with email + password
↓
Server verifies credentials
↓
Server creates JWT:
  payload = {"user_id": 1, "exp": <15 minutes from now>}
  signature = HMAC-SHA256(payload, SECRET_KEY)
  token = base64(header) + "." + base64(payload) + "." + signature
↓
Server sends token to client:
  {"access_token": "eyJhbGci...", "token_type": "bearer"}
↓
Client stores token in localStorage
```

#### 2. **Protected Request** - Client Sends JWT
```
Client wants to access GET /api/v1/auth/me
↓
Client reads token from localStorage
↓
Client sends request with header:
  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
↓
Server receives request
```

#### 3. **Validation** - Server Verifies JWT
```
Server extracts token from Authorization header
↓
Server decodes JWT:
  1. Verify signature (proves token wasn't tampered with)
  2. Check expiration (ensures token is still valid)
  3. Extract user_id from payload
↓
Server queries database: SELECT * FROM users WHERE id = <user_id>
↓
If valid: Returns user data
If invalid: Returns 401 Unauthorized
```

### Why Use JWT?

**Stateless Authentication**:
- Server doesn't need to store active sessions in database
- No "sessions" table needed
- Scales easily (any server can validate token)

**Self-Contained**:
- Token contains user_id (no database lookup needed to know WHO)
- Still need database lookup to check if user still exists/is active

**Secure**:
- Signature prevents tampering (if hacker changes user_id, signature becomes invalid)
- Expiration prevents old tokens from being used forever
- SECRET_KEY must be kept secret (if leaked, hacker can forge tokens)

### JWT Security Notes

**✓ What JWT Does**:
- Proves token wasn't tampered with (signature validation)
- Proves token is from your server (only you have SECRET_KEY)
- Prevents expired tokens from working

**✗ What JWT Doesn't Do**:
- Can't revoke tokens before expiration (stateless = no server-side tracking)
- Can't change user permissions mid-session (info is baked into token)
- Can't logout on server-side (client must delete token)

**For True Logout**:
- Need token blacklist (Redis or database table)
- Store revoked tokens until they expire
- Check blacklist on every protected request
- More complex but provides immediate revocation

---

## Import Reference Map

This map shows **exactly** what each file imports and from where:

### `main.py`
```
Imports:
  ├── from dotenv import load_dotenv              (package: python-dotenv)
  ├── from fastapi import FastAPI                 (package: fastapi)
  ├── from fastapi.middleware.cors import CORSMiddleware  (package: fastapi)
  ├── from app.db.base import Base                → app/db/base.py
  ├── from app.db.session import engine           → app/db/session.py
  ├── from app.models.user import User, UserProfile  → app/models/user.py
  ├── from app.models.question import Question    → app/models/question.py
  └── from app.api.v1.auth_routes import router   → app/api/v1/auth_routes.py

Calls:
  ├── load_dotenv()                               → Loads .env file
  ├── Base.metadata.create_all(bind=engine)       → Creates database tables
  ├── app.add_middleware(CORSMiddleware, ...)     → Enables CORS
  └── app.include_router(auth_router, ...)        → Registers routes
```

### `auth_routes.py`
```
Imports:
  ├── from fastapi import APIRouter, Depends, HTTPException, status  (package: fastapi)
  ├── from sqlalchemy.orm import Session          (package: sqlalchemy)
  ├── from app.db.session import SessionLocal     → app/db/session.py
  ├── from app.controllers.auth_controller import signup, login  → app/controllers/auth_controller.py
  ├── from app.schemas.auth import SignupRequest, LoginRequest, TokenResponse, UserResponse  → app/schemas/auth.py
  └── from app.utils.auth import get_current_user  → app/utils/auth.py

Defines:
  ├── get_db()                                    → Dependency: creates database session
  ├── signup_route()                              → POST /auth/signup
  ├── login_route()                               → POST /auth/login
  ├── get_me_route()                              → GET /auth/me (protected)
  └── logout_route()                              → POST /auth/logout (protected)

Calls:
  ├── signup()                                    → app/controllers/auth_controller.py
  ├── login()                                     → app/controllers/auth_controller.py
  └── get_current_user()                          → app/utils/auth.py (dependency)
```

### `auth_controller.py`
```
Imports:
  ├── from fastapi import HTTPException, status   (package: fastapi)
  ├── from sqlalchemy.orm import Session          (package: sqlalchemy)
  ├── from app.services.auth_service import create_user, get_user_by_email  → app/services/auth_service.py
  ├── from app.services.profile_service import create_profile  → app/services/profile_service.py
  └── from app.utils.auth import verify_password, create_access_token  → app/utils/auth.py

Defines:
  ├── signup()                                    → Signup workflow
  └── login()                                     → Login workflow

Calls:
  ├── get_user_by_email()                         → app/services/auth_service.py
  ├── create_user()                               → app/services/auth_service.py
  ├── create_profile()                            → app/services/profile_service.py
  ├── verify_password()                           → app/utils/auth.py
  └── create_access_token()                       → app/utils/auth.py
```

### `auth_service.py`
```
Imports:
  ├── from sqlalchemy.orm import Session          (package: sqlalchemy)
  ├── from app.models.user import User            → app/models/user.py
  └── from app.utils.auth import hash_password    → app/utils/auth.py

Defines:
  ├── create_user()                               → INSERT user into database
  └── get_user_by_email()                         → SELECT user by email

Calls:
  ├── hash_password()                             → app/utils/auth.py
  ├── db.add()                                    → SQLAlchemy ORM
  ├── db.commit()                                 → SQLAlchemy ORM
  ├── db.query()                                  → SQLAlchemy ORM
  └── db.refresh()                                → SQLAlchemy ORM
```

### `profile_service.py`
```
Imports:
  ├── from sqlalchemy.orm import Session          (package: sqlalchemy)
  └── from app.models.user import UserProfile     → app/models/user.py

Defines:
  └── create_profile()                            → INSERT profile into database

Calls:
  ├── db.add()                                    → SQLAlchemy ORM
  ├── db.commit()                                 → SQLAlchemy ORM
  └── db.refresh()                                → SQLAlchemy ORM
```

### `utils/auth.py`
```
Imports:
  ├── from passlib.context import CryptContext    (package: passlib)
  ├── import jwt                                  (package: PyJWT)
  ├── from datetime import datetime, timedelta    (Python standard library)
  ├── from typing import Optional                 (Python standard library)
  ├── import os                                   (Python standard library)
  ├── from fastapi import Depends, HTTPException, status  (package: fastapi)
  ├── from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials  (package: fastapi)
  └── from sqlalchemy.orm import Session          (package: sqlalchemy)

Defines:
  ├── pwd_context                                 → Bcrypt password hasher
  ├── SECRET_KEY                                  → From .env (JWT secret)
  ├── ALGORITHM                                   → "HS256"
  ├── ACCESS_TOKEN_EXPIRE_MINUTES                 → From .env (default 15)
  ├── security                                    → HTTPBearer (extracts token from header)
  ├── hash_password()                             → Bcrypt hash
  ├── verify_password()                           → Bcrypt verify
  ├── create_access_token()                       → Create JWT
  ├── decode_access_token()                       → Validate JWT
  └── get_current_user()                          → Dependency: get user from JWT

Calls:
  ├── pwd_context.hash()                          → passlib (bcrypt)
  ├── pwd_context.verify()                        → passlib (bcrypt)
  ├── jwt.encode()                                → PyJWT
  ├── jwt.decode()                                → PyJWT
  ├── os.getenv()                                 → Read environment variables
  └── db.query(User).filter(...).first()          → SQLAlchemy ORM
```

### `schemas/auth.py`
```
Imports:
  ├── from pydantic import BaseModel, EmailStr    (package: pydantic)
  └── from datetime import datetime               (Python standard library)

Defines:
  ├── SignupRequest                               → Validates signup JSON
  ├── LoginRequest                                → Validates login JSON
  ├── TokenResponse                               → Validates token JSON
  └── UserResponse                                → Validates user JSON

Calls:
  └── None (schemas are just data classes)
```

### `models/user.py`
```
Imports:
  ├── from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text  (package: sqlalchemy)
  ├── from sqlalchemy.orm import relationship     (package: sqlalchemy)
  ├── from app.db.base import Base                → app/db/base.py
  └── from datetime import datetime               (Python standard library)

Defines:
  ├── User                                        → SQLAlchemy model (users table)
  └── UserProfile                                 → SQLAlchemy model (user_profiles table)

Calls:
  └── None (models are just class definitions)
```

### `db/session.py`
```
Imports:
  ├── from sqlalchemy import create_engine        (package: sqlalchemy)
  ├── from sqlalchemy.orm import sessionmaker     (package: sqlalchemy)
  └── import os                                   (Python standard library)

Defines:
  ├── DATABASE_URL                                → From .env
  ├── engine                                      → SQLAlchemy engine
  └── SessionLocal                                → Session factory

Calls:
  ├── os.getenv()                                 → Read environment variables
  ├── create_engine()                             → SQLAlchemy
  └── sessionmaker()                              → SQLAlchemy
```

### `db/base.py`
```
Imports:
  └── from sqlalchemy.ext.declarative import declarative_base  (package: sqlalchemy)

Defines:
  └── Base                                        → Declarative base for all models

Calls:
  └── declarative_base()                          → SQLAlchemy
```

---

## Summary: How Everything Connects

### Request Flow (Top to Bottom)
```
1. Client
      ↓ (HTTP request)
2. FastAPI (main.py)
      ↓ (routes request)
3. Routes (auth_routes.py)
      ↓ (calls controller)
4. Controller (auth_controller.py)
      ↓ (calls services & utilities)
5. Services (auth_service.py, profile_service.py)
      ↓ (queries database)
6. Database (PostgreSQL)
```

### Layer Responsibilities

| Layer | Files | Purpose | Can Call |
|-------|-------|---------|----------|
| **Entry** | main.py | Start app, config | Everything (setup only) |
| **Routes** | auth_routes.py | HTTP handling | Controllers, Schemas, Utils |
| **Controllers** | auth_controller.py | Business logic | Services, Utils |
| **Services** | auth_service.py, profile_service.py | Database access | Models, Utils |
| **Utils** | utils/auth.py | Helpers | Nothing initially (pure functions) |
| **Schemas** | schemas/auth.py | Validation | Nothing (data only) |
| **Models** | models/user.py | Database schema | Nothing (data only) |
| **Database** | db/session.py, db/base.py | DB setup | Nothing (config only) |

### Dependency Flow
```
Routes Dependencies:
  ├── get_db() → Creates database session for each request
  └── get_current_user() → Validates JWT and gets authenticated user

get_current_user() Dependencies:
  ├── db: Session → From get_db()
  └── credentials: HTTPAuthorizationCredentials → From HTTPBearer (extracts "Authorization: Bearer <token>")
```

---

## Quick Reference

### Starting the Server
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

### API Endpoints
```
POST   /api/v1/auth/signup   - Register new user
POST   /api/v1/auth/login    - Login user
GET    /api/v1/auth/me       - Get current user (requires token)
POST   /api/v1/auth/logout   - Logout (requires token)
```

### Testing with curl
```bash
# Signup
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"pass123","username":"testuser"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"pass123"}'

# Get current user (use token from login response)
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <your_token_here>"
```

### Interactive API Docs
Visit: http://localhost:8000/docs (Swagger UI)

---

## Next Steps for Learning

1. **Try Each Endpoint** - Use the interactive docs at `/docs`
2. **Read Code in Order** - Start from routes → controllers → services
3. **Trace a Request** - Pick one endpoint and follow the entire flow
4. **Modify Code** - Add a new field to User model, see what breaks
5. **Add Logging** - Add `print()` statements to see execution order
6. **Break Things** - Remove a dependency, see what error you get
7. **Build Features** - Add password reset, email verification, etc.

---

This guide covers the complete backend authentication system. Use it as a reference while reading code, and re-read sections as you work through the codebase!
