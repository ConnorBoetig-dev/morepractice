# Billings Backend - Comprehensive Developer Guide

## Table of Contents
1. [Project Overview](#project-overview)
2. [Technology Stack](#technology-stack)
3. [Architecture & Design Patterns](#architecture--design-patterns)
4. [Project Structure](#project-structure)
5. [Database Layer](#database-layer)
6. [Authentication System](#authentication-system)
7. [API Endpoints](#api-endpoints)
8. [Data Flow & Request Lifecycle](#data-flow--request-lifecycle)
9. [Services & Controllers](#services--controllers)
10. [Data Validation & Schemas](#data-validation--schemas)
11. [Question Import System](#question-import-system)
12. [Setup & Configuration](#setup--configuration)
13. [Security Considerations](#security-considerations)
14. [Future Development](#future-development)

---

## Project Overview

**Billings** is a CompTIA exam practice platform backend built with Python and FastAPI. The application provides user authentication, profile management, and question management for various CompTIA certification exams (Security+, Network+, A+ Core 1, A+ Core 2).

### Key Features
- User registration and authentication with JWT tokens
- User profile tracking (streaks, exam stats)
- Question database for multiple exam types
- CSV import system for bulk question loading

---

## Technology Stack

### Core Framework
- **FastAPI 0.121.2** - Modern, high-performance web framework for building APIs
  - Built on Starlette and Pydantic
  - Automatic API documentation (Swagger UI)
  - Native async/await support
  - Type hints and automatic validation
- **Uvicorn 0.38.0** - Lightning-fast ASGI server
- **Python 3.x** - Primary programming language

### Database
- **PostgreSQL 15** - Production-grade relational database
  - Running in Docker container
  - Port: 5432
  - Database name: `billings`
- **SQLAlchemy 2.0.44** - SQL toolkit and ORM (Object-Relational Mapping)
  - Declarative models
  - Query building
  - Transaction management
- **psycopg2-binary 2.9.11** - PostgreSQL adapter for Python

### Authentication & Security
- **PyJWT 2.10.1** - JSON Web Token implementation
  - Token generation with expiration
  - Token validation and decoding
- **Passlib 1.7.4** - Password hashing library
- **bcrypt 5.0.0** - Hashing algorithm for secure password storage

### Data Validation
- **Pydantic 2.12.4** - Data validation using Python type annotations
  - Request/response models
  - Automatic validation
  - JSON serialization
- **email-validator 2.3.0** - Email address validation

### Development Tools
- **Docker & Docker Compose** - Containerization for PostgreSQL and pgAdmin
- **pgAdmin 4** - Web-based database management tool (port 5050)

---

## Architecture & Design Patterns

The backend follows a **layered architecture** pattern with clear separation of concerns:

```
┌─────────────────────────────────────────┐
│         HTTP Client (Frontend)          │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│    Routes Layer (api/v1/)               │ ◄── HTTP request/response handling
│    - Endpoint definitions               │     Request validation (Pydantic)
│    - Dependency injection                │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│    Controller Layer (controllers/)      │ ◄── Business logic orchestration
│    - Workflow coordination               │     Error handling
│    - Service composition                 │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│    Service Layer (services/)            │ ◄── Data access operations
│    - Database interactions               │     CRUD operations
│    - Data retrieval/persistence         │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│    Model Layer (models/)                │ ◄── Database schema definitions
│    - SQLAlchemy ORM models              │     Table relationships
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│         PostgreSQL Database             │
└─────────────────────────────────────────┘
```

### Design Patterns Used

1. **Repository Pattern**
   - Services act as repositories for data access
   - Abstracts database operations from business logic
   - Examples: `auth_service.py`, `profile_service.py`

2. **Dependency Injection**
   - FastAPI's `Depends()` for database sessions and authentication
   - Promotes loose coupling and testability
   - Example: `db: Session = Depends(get_db)`

3. **Data Transfer Objects (DTO)**
   - Pydantic schemas for data validation and serialization
   - Separate models for requests and responses
   - Example: `SignupRequest`, `TokenResponse`

4. **ORM Pattern**
   - SQLAlchemy models map Python classes to database tables
   - Relationship management and lazy loading

---

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── v1/                          # API version 1 routes
│   │       ├── auth_routes.py           # ✅ Authentication endpoints
│   │       ├── user_routes.py           # 🔲 User management (planned)
│   │       ├── exam_routes.py           # 🔲 Exam endpoints (planned)
│   │       └── question_routes.py       # 🔲 Question endpoints (planned)
│   │
│   ├── controllers/                     # Business logic layer
│   │   ├── auth_controller.py           # ✅ Auth workflow logic
│   │   ├── badge_controller.py          # 🔲 Empty (planned)
│   │   ├── exam_controller.py           # 🔲 Empty (planned)
│   │   ├── profile_controller.py        # 🔲 Empty (planned)
│   │   └── streak_controller.py         # 🔲 Empty (planned)
│   │
│   ├── db/                              # Database configuration
│   │   ├── base.py                      # ✅ SQLAlchemy Base class
│   │   └── session.py                   # ✅ Database connection setup
│   │
│   ├── models/                          # Database schema definitions
│   │   ├── user.py                      # ✅ User & UserProfile models
│   │   ├── question.py                  # ✅ Question model
│   │   ├── badge.py                     # 🔲 Empty (planned)
│   │   ├── exam.py                      # 🔲 Empty (planned)
│   │   └── session.py                   # 🔲 Empty (planned)
│   │
│   ├── schemas/                         # Pydantic validation schemas
│   │   ├── auth.py                      # ✅ Auth request/response models
│   │   ├── user.py                      # 🔲 Empty (planned)
│   │   └── exam.py                      # 🔲 Empty (planned)
│   │
│   ├── services/                        # Data access layer
│   │   ├── auth_service.py              # ✅ User CRUD operations
│   │   ├── profile_service.py           # ✅ Profile CRUD operations
│   │   ├── answer_service.py            # 🔲 Empty (planned)
│   │   ├── badge_service.py             # 🔲 Empty (planned)
│   │   ├── exam_service.py              # 🔲 Empty (planned)
│   │   ├── question_service.py          # 🔲 Empty (planned)
│   │   └── session_service.py           # 🔲 Empty (planned)
│   │
│   ├── utils/                           # Helper functions
│   │   ├── auth.py                      # ✅ Password hashing & JWT utilities
│   │   ├── dependencies.py              # 🔲 Empty (planned)
│   │   └── validators.py                # 🔲 Empty (planned)
│   │
│   └── main.py                          # ✅ Application entry point
│
├── scripts/                             # Utility scripts
│   ├── import_questions.py              # ✅ CSV import script
│   ├── debug.py                         # ✅ Debug utility
│   └── seed_badges.py                   # 🔲 Empty (planned)
│
├── requirements.txt                     # Python dependencies
├── docker-compose.yml                   # PostgreSQL + pgAdmin setup
└── .env                                 # Environment variables (empty currently)

✅ = Fully implemented
🔲 = Planned but not implemented
```

---

## Database Layer

### Database Configuration

**File:** `backend/app/db/session.py`

```python
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/billings"
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

**Key Components:**
- `engine` - SQLAlchemy engine for database connections
- `SessionLocal` - Session factory for creating database sessions
- `echo=False` - Disables SQL query logging (set to `True` for debugging)

**Connection Details:**
- Host: `localhost`
- Port: `5432`
- Database: `billings`
- Username: `postgres`
- Password: `postgres`

### Database Models

**File:** `backend/app/db/base.py`

```python
from sqlalchemy.orm import declarative_base
Base = declarative_base()
```

All models inherit from this `Base` class, which:
- Provides table metadata
- Enables automatic table creation
- Manages model registry

### User Model

**File:** `backend/app/models/user.py:7-21`

```python
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

**Field Breakdown:**
- `id` - Auto-incrementing primary key, indexed for fast lookups
- `email` - Unique, indexed, required - used for login
- `username` - Unique, indexed, required - display name
- `hashed_password` - Bcrypt-hashed password (never store plain text!)
- `is_active` - Account status (default: True)
- `is_verified` - Email verification status (default: False, not yet implemented)
- `created_at` - Account creation timestamp
- `updated_at` - Last modification timestamp (auto-updates on changes)

**Indexes:**
- Primary key on `id`
- Unique indexes on `email` and `username` for fast duplicate checking

### UserProfile Model

**File:** `backend/app/models/user.py:23-38`

```python
class UserProfile(Base):
    __tablename__ = "user_profiles"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    bio = Column(Text, nullable=True)
    avatar_url = Column(String, nullable=True)
    study_streak_current = Column(Integer, default=0)
    study_streak_longest = Column(Integer, default=0)
    total_exams_taken = Column(Integer, default=0)
    total_questions_answered = Column(Integer, default=0)
    last_activity_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
```

**Relationship:**
- One-to-one relationship with `User` (user_id is both FK and PK)
- Created automatically when a user signs up

**Field Breakdown:**
- `user_id` - Foreign key to `users.id`, primary key for this table
- `bio` - Optional text field for user biography
- `avatar_url` - Optional URL for user profile picture
- `study_streak_current` - Current consecutive days of study (default: 0)
- `study_streak_longest` - Record streak length (default: 0)
- `total_exams_taken` - Lifetime exam count (default: 0)
- `total_questions_answered` - Lifetime question count (default: 0)
- `last_activity_date` - Last day user was active (for streak calculation)
- `created_at` - Profile creation timestamp

### Question Model

**File:** `backend/app/models/question.py:8-37`

```python
class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(String, index=True)          # From CSV (e.g., "0", "A1")
    exam_type = Column(String, index=True)            # "security", "network", etc.
    domain = Column(String, index=True)               # "1.1", "2.3", etc.
    question_text = Column(Text, nullable=False)
    correct_answer = Column(String, nullable=False)   # "A", "B", "C", or "D"
    options = Column(JSON, nullable=False)            # JSON object with all choices
    created_at = Column(DateTime, default=datetime.utcnow)
```

**Field Breakdown:**
- `id` - Database auto-increment ID
- `question_id` - External ID from CSV files (can be numeric or alphanumeric)
- `exam_type` - Exam category: `security`, `network`, `a1101`, `a1102`
- `domain` - CompTIA domain/objective (e.g., "1.1", "2.3")
- `question_text` - The actual question text
- `correct_answer` - Letter of correct answer ("A", "B", "C", or "D")
- `options` - JSON structure with all answer choices and explanations
- `created_at` - Import timestamp

**Options JSON Structure:**
```json
{
  "A": {
    "text": "This is option A",
    "explanation": "Explanation why A is correct/incorrect"
  },
  "B": {
    "text": "This is option B",
    "explanation": "Explanation why B is correct/incorrect"
  },
  "C": { ... },
  "D": { ... }
}
```

**Indexes:**
- `question_id`, `exam_type`, `domain` are indexed for efficient filtering
- Example query: "Get all Security+ questions from domain 1.1"

### Table Creation

**File:** `backend/app/main.py:12`

```python
Base.metadata.create_all(bind=engine)
```

This line:
1. Imports all models (User, UserProfile, Question)
2. Reads their schema definitions
3. Generates SQL CREATE TABLE statements
4. Executes them on the database (if tables don't exist)

**Important:** This is a simple approach suitable for development. Production systems should use **migrations** (e.g., Alembic) to track schema changes over time.

---

## Authentication System

The authentication system uses **JWT (JSON Web Tokens)** for stateless authentication with **bcrypt** password hashing.

### Password Security

**File:** `backend/app/utils/auth.py:1-16`

```python
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Turn a raw password into a hashed password."""
    return pwd_context.hash(password)

def verify_password(raw_password: str, hashed_password: str) -> bool:
    """Check if raw_password matches the stored hashed version."""
    return pwd_context.verify(raw_password, hashed_password)
```

**How it works:**
1. **During signup:** Raw password → `hash_password()` → stored in database
2. **During login:** User enters password → `verify_password()` → compares with stored hash
3. **Security:** bcrypt is a slow, salted hashing algorithm designed to resist brute-force attacks

**Example:**
```
Raw password: "MyPassword123"
Hashed: "$2b$12$KIXvZ9Q2r8Y.../aBcD..."  (60 characters)
```

### JWT Token Management

**File:** `backend/app/utils/auth.py:18-53`

```python
SECRET_KEY = "CHANGE_THIS_TO_A_RANDOM_LONG_STRING"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a signed JWT token with an expiration time."""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    """Decode a JWT token and return the payload if valid."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None  # Token expired
    except jwt.InvalidTokenError:
        return None  # Token invalid
```

**How JWT Works:**

1. **Token Creation (Login/Signup):**
   ```python
   token = create_access_token({"user_id": 123})
   # Returns: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
   ```

   Token contains:
   - `user_id` - Identifies the user
   - `exp` - Expiration timestamp (15 minutes from creation)
   - Signature - Prevents tampering

2. **Token Validation:**
   ```python
   payload = decode_access_token(token)
   # Returns: {"user_id": 123, "exp": 1699999999} or None if invalid
   ```

**Security Notes:**
- ⚠️ `SECRET_KEY` is hardcoded - **MUST be changed in production** and stored in environment variables
- Tokens expire after 15 minutes (no refresh token system yet)
- Algorithm: HS256 (HMAC with SHA-256)

### Authentication Flow Diagrams

**Signup Flow:**
```
Client                Route              Controller           Service            Database
  |                     |                     |                   |                  |
  |--POST /signup----->|                     |                   |                  |
  |  {email, password, |                     |                   |                  |
  |   username}        |                     |                   |                  |
  |                    |--signup()---------->|                   |                  |
  |                    |                     |--get_user_by_email()--------------->|
  |                    |                     |                   |                  |
  |                    |                     |<--None (no existing user)-----------|
  |                    |                     |                   |                  |
  |                    |                     |--create_user()---->|                 |
  |                    |                     |  (hashes password) |--INSERT users-->|
  |                    |                     |                    |<--User object---|
  |                    |                     |<--User object------|                 |
  |                    |                     |                   |                  |
  |                    |                     |--create_profile()-->|                |
  |                    |                     |                    |--INSERT profile>|
  |                    |                     |<--Profile object---|                 |
  |                    |                     |                   |                  |
  |                    |                     |--create_access_token()              |
  |                    |                     |  (generates JWT)  |                  |
  |                    |<--{token, user_id}--|                   |                  |
  |<--{access_token}---|                     |                   |                  |
```

**Login Flow:**
```
Client                Route              Controller           Service            Database
  |                     |                     |                   |                  |
  |--POST /login------>|                     |                   |                  |
  |  {email, password} |                     |                   |                  |
  |                    |--login()----------->|                   |                  |
  |                    |                     |--get_user_by_email()--------------->|
  |                    |                     |<--User object-----------------------|
  |                    |                     |                   |                  |
  |                    |                     |--verify_password()|                  |
  |                    |                     |  (checks hash)    |                  |
  |                    |                     |                   |                  |
  |                    |                     |--create_access_token()              |
  |                    |                     |  (generates JWT)  |                  |
  |                    |<--{token, user_id}--|                   |                  |
  |<--{access_token}---|                     |                   |                  |
```

**Token Validation Flow (/auth/me):**
```
Client                Route              Controller           Service            Database
  |                     |                     |                   |                  |
  |--GET /auth/me?---->|                     |                   |                  |
  |  token=xxxxx       |                     |                   |                  |
  |                    |--get_current_user-->|                   |                  |
  |                    |  _from_token()      |                   |                  |
  |                    |                     |--decode_access_token()              |
  |                    |                     |  (validates JWT)  |                  |
  |                    |                     |                   |                  |
  |                    |                     |--get_user_by_id()------------------>|
  |                    |                     |<--User object-----------------------|
  |                    |<--User object-------|                   |                  |
  |<--{id, email,...}--|                     |                   |                  |
```

---

## API Endpoints

All endpoints are prefixed with `/api/v1`.

### Authentication Endpoints

**File:** `backend/app/api/v1/auth_routes.py`

#### 1. POST /api/v1/auth/signup

**Purpose:** Register a new user account

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123",
  "username": "john_doe"
}
```

**Success Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Error Responses:**
- `400 Bad Request` - Email already registered
- `422 Unprocessable Entity` - Invalid email format or missing fields

**Implementation:** `backend/app/api/v1/auth_routes.py:29-36`

**Logic:**
1. Validates request data (Pydantic `SignupRequest`)
2. Calls `signup()` controller
3. Returns JWT token for immediate authentication

---

#### 2. POST /api/v1/auth/login

**Purpose:** Authenticate existing user

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Success Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid email or password
- `422 Unprocessable Entity` - Invalid email format or missing fields

**Implementation:** `backend/app/api/v1/auth_routes.py:42-48`

**Logic:**
1. Validates request data
2. Calls `login()` controller
3. Returns JWT token

---

#### 3. GET /api/v1/auth/me

**Purpose:** Get current user information from token

**Query Parameters:**
- `token` (required) - JWT access token

**Example Request:**
```
GET /api/v1/auth/me?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Success Response (200 OK):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "john_doe",
  "is_active": true,
  "created_at": "2025-11-15T10:30:00"
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid or expired token
- `404 Not Found` - User not found

**Implementation:** `backend/app/api/v1/auth_routes.py:54-61`

**Logic:**
1. Receives token as query parameter
2. Calls `get_current_user_from_token()` controller
3. Returns user data (excluding password!)

**Note:** Typically, tokens would be sent in the `Authorization` header as `Bearer <token>`, but this implementation uses a query parameter for frontend simplicity.

---

### Dependency Injection

**File:** `backend/app/api/v1/auth_routes.py:18-23`

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Purpose:** Provides a database session to each request

**How it works:**
1. Creates a new database session
2. Yields it to the route handler
3. Automatically closes the session after the request (even if errors occur)

**Usage in routes:**
```python
@router.post("/signup")
def signup_route(payload: SignupRequest, db: Session = Depends(get_db)):
    # 'db' is automatically injected by FastAPI
    return signup(db=db, ...)
```

---

## Data Flow & Request Lifecycle

Let's trace a complete signup request through the system.

### Signup Request Step-by-Step

**1. Client sends POST request:**
```
POST /api/v1/auth/signup
Content-Type: application/json

{
  "email": "alice@example.com",
  "password": "MySecret123",
  "username": "alice_wonder"
}
```

**2. Route layer validates and routes:**

`backend/app/api/v1/auth_routes.py:29-36`

```python
@router.post("/signup", response_model=TokenResponse)
def signup_route(payload: SignupRequest, db: Session = Depends(get_db)):
    return signup(
        db=db,
        email=payload.email,
        password=payload.password,
        username=payload.username,
    )
```

- FastAPI automatically validates JSON against `SignupRequest` schema
- Email format is checked (thanks to `EmailStr`)
- Database session is injected via `Depends(get_db)`

**3. Controller orchestrates business logic:**

`backend/app/controllers/auth_controller.py:16-34`

```python
def signup(db: Session, email: str, password: str, username: str) -> dict:
    # 1. Check if user already exists
    existing = get_user_by_email(db, email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered.",
        )

    # 2. Create user
    user = create_user(db, email=email, password=password, username=username)

    # 3. Create user profile
    create_profile(db, user_id=user.id)

    # 4. Create JWT token
    token = create_access_token({"user_id": user.id})

    return {"access_token": token, "user_id": user.id, "username": user.username}
```

**Step-by-step breakdown:**

**3a. Check for existing user:**
- Calls `get_user_by_email()` service
- If user exists, raises HTTP 400 error
- This prevents duplicate email addresses

**3b. Create user:**
- Calls `create_user()` service
- Password is hashed inside the service (never stored plain!)

**4. Service layer interacts with database:**

`backend/app/services/auth_service.py:6-22`

```python
def create_user(db: Session, email: str, password: str, username: str) -> User:
    """
    Create a new user row in the database.
    Password is hashed BEFORE storing.
    """
    hashed = hash_password(password)  # ← Bcrypt hashing here
    user = User(
        email=email,
        username=username,
        hashed_password=hashed,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(user)
    db.commit()  # ← SQL INSERT executed here
    db.refresh(user)  # ← Loads auto-generated ID
    return user
```

**5. Create profile:**

`backend/app/services/profile_service.py:5-16`

```python
def create_profile(db: Session, user_id: int) -> UserProfile:
    """
    Create a new user profile when a new user signs up.
    """
    profile = UserProfile(
        user_id=user_id,
        created_at=datetime.utcnow()
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile
```

- Creates profile with default values (streaks = 0, exams = 0)
- Linked to user via `user_id` foreign key

**6. Generate JWT token:**

`backend/app/utils/auth.py:26-40`

```python
token = create_access_token({"user_id": user.id})
# Returns: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJleHAiOjE2OTk5OTk5OTl9..."
```

**7. Return response to client:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**8. Client stores token:**
- Frontend saves token (localStorage, cookies, etc.)
- Includes token in future requests for authentication

---

## Services & Controllers

### Auth Service

**File:** `backend/app/services/auth_service.py`

Provides CRUD operations for `User` model.

**Functions:**

#### create_user()
```python
def create_user(db: Session, email: str, password: str, username: str) -> User
```
- Hashes password with bcrypt
- Inserts new row into `users` table
- Returns User object with auto-generated ID

#### get_user_by_email()
```python
def get_user_by_email(db: Session, email: str) -> User | None
```
- Queries database for user with matching email
- Returns User object or None
- Used during login and duplicate checking

#### get_user_by_id()
```python
def get_user_by_id(db: Session, user_id: int) -> User | None
```
- Queries database by primary key
- Returns User object or None
- Used for token validation

#### update_user()
```python
def update_user(db: Session, user_id: int, updates: dict) -> User
```
- Updates user fields dynamically
- Automatically sets `updated_at` timestamp
- Returns updated User object

**Example usage:**
```python
user = update_user(db, user_id=1, updates={"is_verified": True})
```

---

### Profile Service

**File:** `backend/app/services/profile_service.py`

Manages `UserProfile` model operations.

**Functions:**

#### create_profile()
```python
def create_profile(db: Session, user_id: int) -> UserProfile
```
- Called automatically during signup
- Creates profile with default values
- One-to-one relationship with User

#### get_profile()
```python
def get_profile(db: Session, user_id: int) -> UserProfile | None
```
- Retrieves profile for a given user
- Returns None if not found

#### update_profile()
```python
def update_profile(db: Session, user_id: int, updates: dict) -> UserProfile
```
- Updates profile fields (bio, avatar, etc.)
- Dynamic field updates via dictionary

**Example:**
```python
profile = update_profile(db, user_id=1, updates={"bio": "CompTIA enthusiast"})
```

#### increment_exam_count()
```python
def increment_exam_count(db: Session, user_id: int)
```
- Called when user completes an exam
- Increments `total_exams_taken` counter
- Part of gamification system

#### update_last_activity()
```python
def update_last_activity(db: Session, user_id: int, activity_date: date)
```
- Tracks last activity date for streak calculation
- Called when user studies questions

#### update_streak()
```python
def update_streak(db: Session, user_id: int, current: int, longest: int)
```
- Updates both current and longest streak values
- Services only store data; controllers handle streak logic

**Streak System Design:**
- Service layer: Data persistence only
- Controller layer: Business logic (calculating if streak continues or resets)
- Separation of concerns for easier testing

---

### Auth Controller

**File:** `backend/app/controllers/auth_controller.py`

Orchestrates multi-step authentication workflows.

#### signup()

`backend/app/controllers/auth_controller.py:16-34`

**Workflow:**
1. Check if email already exists
2. Create user (with hashed password)
3. Create associated profile
4. Generate JWT token
5. Return token + user info

**Error handling:**
- Raises HTTP 400 if email is already registered
- Validation errors caught by Pydantic at route level

#### login()

`backend/app/controllers/auth_controller.py:40-59`

**Workflow:**
1. Look up user by email
2. Verify password against stored hash
3. Generate JWT token
4. Return token + user info

**Security:**
- Generic error message for invalid email OR password (prevents email enumeration)
- Password never stored or logged

#### get_current_user_from_token()

`backend/app/controllers/auth_controller.py:65-90`

**Workflow:**
1. Decode JWT token
2. Extract user_id from payload
3. Load user from database
4. Return user object

**Error handling:**
- HTTP 401 if token is invalid or expired
- HTTP 401 if token payload is malformed
- HTTP 404 if user_id doesn't exist in database

---

## Data Validation & Schemas

Pydantic schemas enforce data validation and provide type safety.

**File:** `backend/app/schemas/auth.py`

### SignupRequest

```python
class SignupRequest(BaseModel):
    email: EmailStr       # ← Automatic email validation
    password: str         # Raw password (hashed in service)
    username: str         # Display name
```

**Validation:**
- `EmailStr` from `email-validator` checks format
- FastAPI automatically rejects invalid requests with HTTP 422

**Example valid request:**
```json
{
  "email": "test@example.com",
  "password": "SecurePass123",
  "username": "test_user"
}
```

**Example invalid request (rejected):**
```json
{
  "email": "not-an-email",  // ❌ Invalid format
  "password": "123",
  "username": "test"
}
```

### LoginRequest

```python
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
```

### TokenResponse

```python
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"  # OAuth 2.0 standard
```

**Returned by signup and login endpoints.**

### UserResponse

```python
class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True  # ← Enables SQLAlchemy model conversion
```

**Purpose:**
- Safe representation of User (excludes `hashed_password`!)
- `orm_mode = True` allows direct conversion from SQLAlchemy models

**Example conversion:**
```python
user = get_user_by_id(db, 1)  # SQLAlchemy User object
return user  # FastAPI auto-converts to UserResponse JSON
```

---

## Question Import System

The backend includes a CSV import script for bulk loading exam questions.

**File:** `backend/scripts/import_questions.py`

### CSV File Structure

**Expected columns:**
- `question-id` - Unique identifier (e.g., "0", "1", "A1")
- `domain` - CompTIA domain (e.g., "1.1", "2.3")
- `question-text` - The question
- `option-a` - Answer choice A text
- `option-b` - Answer choice B text
- `option-c` - Answer choice C text
- `option-d` - Answer choice D text
- `explanation-a` - Explanation for A
- `explanation-b` - Explanation for B
- `explanation-c` - Explanation for C
- `explanation-d` - Explanation for D
- `correct answer` - Letter of correct answer (note: space in header name!)

### Import Configuration

```python
CSV_DIR = "/home/connor-boetig/Documents/COMPTIA"

EXAMS = {
    "security.csv": "security",
    "network.csv": "network",
    "a1101.csv": "a1101",
    "a1102.csv": "a1102",
}
```

### Import Logic

`backend/scripts/import_questions.py:21-66`

```python
def import_csv_file(db: Session, filename: str, exam_type: str):
    path = os.path.join(CSV_DIR, filename)

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=",")

        for row in reader:
            # Skip empty lines
            if not row or row["question-id"].strip() == "":
                continue

            # Build options JSON structure
            options = {
                "A": {
                    "text": row["option-a"].strip(),
                    "explanation": row["explanation-a"].strip(),
                },
                "B": { ... },
                "C": { ... },
                "D": { ... },
            }

            # Create SQLAlchemy model
            q = Question(
                question_id=row["question-id"].strip(),
                exam_type=exam_type,
                domain=row["domain"].strip(),
                question_text=row["question-text"].strip(),
                correct_answer=row["correct answer"].strip(),
                options=options,
            )

            db.add(q)

    db.commit()
```

**Process:**
1. Open CSV file
2. Read rows as dictionaries
3. Skip empty rows
4. Transform flat CSV structure into nested JSON for `options` field
5. Create Question model instances
6. Bulk insert into database

### Running the Import

```bash
cd backend
python -m scripts.import_questions
```

**Output:**
```
📥 Importing security.csv as exam_type=security ...
✅ Finished importing security.csv.

📥 Importing network.csv as exam_type=network ...
✅ Finished importing network.csv.

...

🎉 All CSV files imported successfully!
```

### Data Transformation Example

**CSV row:**
```csv
question-id,domain,question-text,option-a,option-b,...,correct answer
0,1.1,"What is CIA triad?","Confidentiality...","Central...",...,A
```

**Transformed to JSON in database:**
```json
{
  "id": 1,
  "question_id": "0",
  "exam_type": "security",
  "domain": "1.1",
  "question_text": "What is CIA triad?",
  "correct_answer": "A",
  "options": {
    "A": {
      "text": "Confidentiality, Integrity, Availability",
      "explanation": "Correct! These are the three pillars..."
    },
    "B": {
      "text": "Central Intelligence Agency",
      "explanation": "Incorrect. In security, CIA refers to..."
    },
    ...
  }
}
```

---

## Setup & Configuration

### Prerequisites

- Python 3.x
- Docker & Docker Compose
- PostgreSQL 15 (via Docker)

### Installation Steps

**1. Clone the repository and navigate to backend:**
```bash
cd backend
```

**2. Install Python dependencies:**
```bash
pip install -r requirements.txt
```

**3. Start PostgreSQL database:**
```bash
docker-compose up -d
```

This starts:
- PostgreSQL on port 5432
- pgAdmin on port 5050

**4. Verify database connection:**

Access pgAdmin at `http://localhost:5050`
- Email: (check docker-compose.yml)
- Password: (check docker-compose.yml)

**5. Run the application:**
```bash
uvicorn app.main:app --reload
```

**6. Access API documentation:**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Environment Variables

**File:** `.env` (currently empty - needs to be configured)

**Recommended variables:**
```env
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/billings

# JWT
SECRET_KEY=your-super-secret-key-here-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=15

# CORS (if needed)
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

**Note:** Currently, all configuration is hardcoded. Production systems should use environment variables and a `.env` file.

### Docker Compose Configuration

**File:** `docker-compose.yml`

Defines two services:
1. **PostgreSQL database**
   - Port: 5432
   - Database: billings
   - Credentials: postgres/postgres

2. **pgAdmin** (database GUI)
   - Port: 5050
   - Web interface for database management

---

## Security Considerations

### Current Security Measures

✅ **Password hashing with bcrypt**
- Slow, salted hashing algorithm
- Resistant to rainbow table attacks

✅ **JWT-based authentication**
- Stateless authentication
- Token expiration (15 minutes)

✅ **SQL injection protection**
- SQLAlchemy ORM prevents SQL injection
- Parameterized queries

✅ **Email validation**
- Pydantic EmailStr validator
- Prevents invalid email formats

### Security Vulnerabilities & Improvements Needed

⚠️ **Hardcoded SECRET_KEY**
- **Risk:** Anyone with source code access can forge tokens
- **Fix:** Move to environment variable
- **Location:** `backend/app/utils/auth.py:22`

⚠️ **Database credentials in docker-compose**
- **Risk:** Credentials in version control
- **Fix:** Use environment variables or Docker secrets

⚠️ **No HTTPS enforcement**
- **Risk:** Tokens sent over unencrypted connections
- **Fix:** Use HTTPS in production, add HSTS headers

⚠️ **Short token expiration without refresh tokens**
- **Risk:** Users logged out frequently
- **Fix:** Implement refresh token system

⚠️ **No rate limiting**
- **Risk:** Brute-force attacks on login endpoint
- **Fix:** Add rate limiting middleware (e.g., slowapi)

⚠️ **No CORS configuration**
- **Risk:** Any origin can access API
- **Fix:** Configure CORS middleware with allowed origins

⚠️ **Token in query parameter (/auth/me)**
- **Risk:** Tokens logged in browser history and server logs
- **Fix:** Use Authorization header: `Bearer <token>`

⚠️ **No input sanitization**
- **Risk:** Potential XSS if data displayed without escaping
- **Fix:** Sanitize user inputs (bio, username, etc.)

⚠️ **No email verification**
- **Risk:** Fake accounts with invalid emails
- **Fix:** Implement email verification flow

⚠️ **No account lockout**
- **Risk:** Unlimited login attempts
- **Fix:** Lock account after N failed attempts

### Recommended Security Enhancements

1. **Environment-based configuration**
   ```python
   import os
   SECRET_KEY = os.getenv("SECRET_KEY")
   DATABASE_URL = os.getenv("DATABASE_URL")
   ```

2. **CORS middleware**
   ```python
   from fastapi.middleware.cors import CORSMiddleware

   app.add_middleware(
       CORSMiddleware,
       allow_origins=["http://localhost:3000"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

3. **Rate limiting**
   ```python
   from slowapi import Limiter
   limiter = Limiter(key_func=get_remote_address)

   @limiter.limit("5/minute")
   @router.post("/login")
   def login_route(...):
       ...
   ```

4. **Refresh token system**
   - Short-lived access tokens (15 min)
   - Long-lived refresh tokens (7 days)
   - Stored in database for revocation

---

## Future Development

### Planned Features (Placeholder Files Exist)

**1. Exam Taking System**
- Routes: `exam_routes.py`, `question_routes.py`
- Controllers: `exam_controller.py`
- Services: `exam_service.py`, `question_service.py`
- Models: `exam.py`, `session.py`

**Expected functionality:**
- Start exam session
- Fetch random questions by exam type
- Submit answers
- Calculate scores
- Save exam history

**2. Badge System**
- Files: `badge.py` (model), `badge_service.py`, `badge_controller.py`
- Gamification: Award badges for achievements
- Examples: "First Exam", "7-Day Streak", "100 Questions Answered"

**3. Streak Tracking**
- File: `streak_controller.py`
- Logic for calculating streaks based on `last_activity_date`
- Reset streaks if user misses a day
- Update `study_streak_longest` when current exceeds it

**4. User Management**
- File: `user_routes.py`
- Update profile (bio, avatar)
- View statistics
- Delete account

**5. Answer Tracking**
- File: `answer_service.py`
- Store user's answer history
- Track which questions were answered correctly/incorrectly
- Identify weak areas (domains with low scores)

### Technical Improvements Needed

**1. Database Migrations**
- **Tool:** Alembic
- **Purpose:** Track schema changes over time
- **Current issue:** Using `create_all()` which doesn't handle schema updates

**2. Testing**
- Unit tests for services
- Integration tests for API endpoints
- Test database fixtures

**3. API Documentation**
- Add docstrings to all functions
- Use FastAPI's automatic docs (already available at /docs)
- Write API usage guide for frontend team

**4. Error Handling**
- Global exception handler
- Structured error responses
- Error logging

**5. Logging**
- Request logging
- Error logging
- Performance monitoring

**6. Performance Optimization**
- Database query optimization
- Caching frequently accessed data (Redis)
- Connection pooling

**7. Deployment**
- Production WSGI server (e.g., Gunicorn)
- Environment-specific configurations
- CI/CD pipeline

---

## Summary

This backend is a **well-structured FastAPI application** following modern Python best practices:

**Strengths:**
- Clean layered architecture (routes → controllers → services → models)
- Type safety with Pydantic
- Secure password hashing (bcrypt)
- JWT authentication
- ORM for database interactions (SQLAlchemy)
- CSV import system for questions

**What's Working:**
- User registration and login
- Profile creation and management
- Question database and import
- Token-based authentication

**What Needs Work:**
- Environment variable configuration
- Security hardening (SECRET_KEY, CORS, rate limiting)
- Exam taking functionality (models exist but no logic)
- Badge and streak systems (planned)
- Database migrations (currently using create_all)
- Testing suite
- Production deployment setup

This codebase provides a **solid foundation** for a CompTIA exam practice platform. The architecture is scalable and follows industry standards. With the planned features implemented, it will become a full-featured exam preparation system.

---

## Quick Reference

### Key Files
- **Entry point:** `backend/app/main.py`
- **Database config:** `backend/app/db/session.py`
- **Auth routes:** `backend/app/api/v1/auth_routes.py`
- **Auth logic:** `backend/app/controllers/auth_controller.py`
- **Password/JWT utils:** `backend/app/utils/auth.py`
- **User model:** `backend/app/models/user.py`
- **Question import:** `backend/scripts/import_questions.py`

### Common Commands
```bash
# Start database
docker-compose up -d

# Run server
uvicorn app.main:app --reload

# Import questions
python -m scripts.import_questions

# Access API docs
http://localhost:8000/docs
```

### Database Connection
```
postgresql://postgres:postgres@localhost:5432/billings
```

### Default Token Expiration
15 minutes (configured in `backend/app/utils/auth.py:24`)

---

**For new developers:** Start by reading the [Architecture](#architecture--design-patterns) section, then trace a [Signup Request](#signup-request-step-by-step) through the system to understand the data flow. Experiment with the API using the Swagger UI at `/docs`.
