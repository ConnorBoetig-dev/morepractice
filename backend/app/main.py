# ============================================
# APPLICATION ENTRY POINT
# ============================================
# This file sets up the FastAPI application and connects all the layers
#
# Layer structure:
# 1. ROUTES (auth_routes.py) - receive HTTP requests
# 2. CONTROLLERS (auth_controller.py) - orchestrate business logic
# 3. SERVICES (auth_service.py, profile_service.py) - query database
# 4. MODELS (user.py, question.py) - define database tables
#
# Run with: uvicorn app.main:app --reload

# Load environment variables from .env file before anything else
# python-dotenv reads backend/.env and makes variables available via os.getenv()
from dotenv import load_dotenv
load_dotenv()  # Must be called before importing modules that use env vars

# ============================================
# VALIDATE REQUIRED ENVIRONMENT VARIABLES
# ============================================
# SECURITY: Fail fast if critical environment variables are missing
# This prevents the app from running with insecure fallback values
import os
import sys

# List of critical environment variables that MUST be set
REQUIRED_ENV_VARS = [
    "DATABASE_URL",    # PostgreSQL connection string
    "JWT_SECRET",      # Secret key for signing JWT tokens
]

# Check for missing environment variables
missing_vars = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]

if missing_vars:
    # Print error message to stderr and exit
    print("=" * 60, file=sys.stderr)
    print("ERROR: Missing required environment variables!", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print(f"Missing variables: {', '.join(missing_vars)}", file=sys.stderr)
    print("", file=sys.stderr)
    print("Fix this by:", file=sys.stderr)
    print("1. Create a .env file in the project root", file=sys.stderr)
    print("2. Copy .env.example to .env: cp .env.example .env", file=sys.stderr)
    print("3. Fill in the required values (see .env.example for guidance)", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    sys.exit(1)  # Exit with error code 1 (prevents app from starting)

# Validate JWT_SECRET strength (warn if using weak secret)
jwt_secret = os.getenv("JWT_SECRET", "")
if len(jwt_secret) < 32:
    print("=" * 60, file=sys.stderr)
    print("WARNING: JWT_SECRET is too short (< 32 characters)", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print("For security, JWT secrets should be at least 32 characters.", file=sys.stderr)
    print("Generate a secure secret:", file=sys.stderr)
    print('  python -c "import secrets; print(secrets.token_urlsafe(32))"', file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    # Don't exit, just warn (allows development to continue)

# FastAPI - modern web framework for building APIs
from fastapi import FastAPI, Request

# CORS Middleware - allows React frontend to make requests to this API
# Without CORS, browsers block cross-origin requests (frontend on :5173, backend on :8000)
from fastapi.middleware.cors import CORSMiddleware

# Security Headers Middleware - adds security headers to all responses
from app.middleware.security_headers import SecurityHeadersMiddleware

# Request ID Middleware - adds unique ID to each request for tracing
from app.middleware.request_id import RequestIDMiddleware

# Rate limiting - protects API from abuse and DDoS attacks
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.utils.rate_limit import limiter, user_limiter, user_only_limiter  # Import rate limiters

# SQLAlchemy components for database setup
# Defined in: app/db/base.py
from app.db.base import Base  # ← Declarative base (all models inherit from this)

# Defined in: app/db/session.py
from app.db.session import engine  # ← Database engine (connection to PostgreSQL)


# ============================================
# IMPORT ALL DATABASE MODELS
# ============================================
# IMPORTANT: Import ALL models BEFORE calling Base.metadata.create_all()
# SQLAlchemy needs to see these imports to know what tables to create

# User models - defined in: app/models/user.py
from app.models.user import User, UserProfile, Session, AuditLog, PasswordHistory

# Question models - defined in: app/models/question.py
from app.models.question import Question, QuestionBookmark

# Gamification models - defined in: app/models/gamification.py
from app.models.gamification import (
    QuizAttempt, StudySession, UserAnswer, Achievement, UserAchievement, Avatar, UserAvatar
)


# ============================================
# CREATE DATABASE TABLES
# ============================================
# Auto-create all tables if they don't exist
# SQLAlchemy looks at all imported models and generates CREATE TABLE statements
# NOTE: This is OK for development, but production should use migrations (Alembic)
Base.metadata.create_all(bind=engine)


# ============================================
# INITIALIZE FASTAPI APPLICATION
# ============================================
app = FastAPI(
    title="Billings API",
    version="1.0.0",
    description="""
## Professional Exam Preparation Platform

A comprehensive API for managing exam questions, quizzes, achievements, and user progress tracking.

### Features

* **Authentication & Authorization**: Secure JWT-based auth with email verification, password reset, and session management
* **Question Management**: Browse questions by exam type and domain with advanced filtering
* **Quiz System**: Take quizzes, track attempts, and view detailed performance analytics
* **Bookmarks**: Save questions for later review with personal notes
* **Gamification**: Earn achievements, unlock avatars, and compete on leaderboards
* **Admin Panel**: Full CRUD operations for questions, users, and achievements

### API Standards

* All endpoints return consistent JSON responses
* Error responses include machine-readable error codes
* Authentication uses Bearer token in Authorization header
* Pagination uses `page` and `page_size` query parameters
* All timestamps are in ISO 8601 format (UTC)

### Rate Limits

* Public endpoints: 60 requests/minute per IP
* Auth endpoints: 3 signup/login per hour per IP
* Authenticated endpoints: 100 requests/minute per user

### Error Handling

All errors follow a consistent format:
- Single errors: `{"success": false, "error": {...}, "status_code": 404, ...}`
- Validation errors: `{"success": false, "errors": [...], "status_code": 422, ...}`

See the error schemas below for full details.
    """.strip(),
    contact={
        "name": "Billings API Support",
        "email": "support@billingsapi.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=[
        {
            "name": "Auth",
            "description": "Authentication and authorization endpoints (signup, login, password reset, email verification, session management)"
        },
        {
            "name": "Questions",
            "description": "Browse and retrieve exam questions by type and domain"
        },
        {
            "name": "bookmarks",
            "description": "Bookmark questions for later review with personal notes"
        },
        {
            "name": "Quiz",
            "description": "Submit quiz attempts and view quiz history and statistics"
        },
        {
            "name": "Achievements",
            "description": "View achievements, track earned achievements, and see achievement statistics"
        },
        {
            "name": "Avatars",
            "description": "View, unlock, and select user avatars"
        },
        {
            "name": "Leaderboard",
            "description": "View leaderboards by XP, quiz count, accuracy, streak, and exam type"
        },
        {
            "name": "Admin",
            "description": "Admin-only endpoints for managing questions, users, and achievements (requires admin role)"
        },
        {
            "name": "Health",
            "description": "Health check endpoints for monitoring application status"
        },
    ]
)  # Creates the FastAPI app instance

# Add rate limiters to app state (makes them accessible to routes)
# Multiple limiters allow different strategies:
# - limiter: IP-based (for public endpoints)
# - user_limiter: User ID or IP-based (for authenticated endpoints)
# - user_only_limiter: User ID only (strict authenticated endpoints)
app.state.limiter = limiter
app.state.user_limiter = user_limiter
app.state.user_only_limiter = user_only_limiter

# Register rate limit exceeded handler (returns 429 status)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ============================================
# REGISTER GLOBAL EXCEPTION HANDLERS
# ============================================
# Transform all exceptions into consistent error responses
# Makes API easier to consume from frontend
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.middleware.error_handlers import (
    http_exception_handler,
    validation_exception_handler,
    generic_exception_handler
)

# Order matters! More specific handlers first, generic last
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)


# ============================================
# CONFIGURE CORS MIDDLEWARE
# ============================================
# CORS (Cross-Origin Resource Sharing) allows browser-based frontends to make API requests
# Without CORS, browsers block requests from frontend (localhost:8080) to backend (localhost:8000)
#
# Security: Only allow requests from our frontend origin
# Note: Database (PostgreSQL) doesn't need CORS - it uses SQL connections, not HTTP
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",    # Vite dev server
        "http://127.0.0.1:5173",    # Vite dev server (127.0.0.1)
        "http://localhost:8080",    # Legacy frontend port
        "http://127.0.0.1:8080",    # Legacy frontend port (127.0.0.1)
        "http://0.0.0.0:8080",      # Frontend via 0.0.0.0 (all interfaces)
    ],
    allow_credentials=True,  # Allow Authorization headers (for JWT tokens)
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE)
    allow_headers=["*"],  # Allow all headers (Content-Type, Authorization, etc.)
)


# ============================================
# CONFIGURE REQUEST ID MIDDLEWARE
# ============================================
# Add unique request ID to each request for tracing
# Makes it easy to correlate logs for a single request
# Request ID is returned in X-Request-ID response header
app.add_middleware(RequestIDMiddleware)


# ============================================
# CONFIGURE SECURITY HEADERS MIDDLEWARE
# ============================================
# Add security headers to all responses (OWASP best practices)
# Protects against: XSS, clickjacking, MIME sniffing, etc.
#
# Headers added:
# - X-Content-Type-Options: nosniff
# - X-Frame-Options: DENY
# - X-XSS-Protection: 1; mode=block
# - Content-Security-Policy: (prevents XSS and injection)
# - Referrer-Policy: strict-origin-when-cross-origin
# - Permissions-Policy: (disables sensitive browser features)
#
# NOTE: HSTS (Strict-Transport-Security) is disabled by default for local dev
# Enable in production by setting environment variable: ENABLE_HSTS=true
app.add_middleware(SecurityHeadersMiddleware)


# ============================================
# REGISTER ROUTE MODULES
# ============================================
# Import router from auth routes file
# Defined in: app/api/v1/auth_routes.py
from app.api.v1.auth_routes import router as auth_router

# Import router from question routes file
# Defined in: app/api/v1/question_routes.py
from app.api.v1.question_routes import router as question_router

# Import router from quiz routes file
# Defined in: app/api/v1/quiz_routes.py
from app.api.v1.quiz_routes import router as quiz_router

# Import router from study mode routes file
# Defined in: app/api/v1/study_routes.py
from app.api.v1.study_routes import router as study_router

# Import router from achievement routes file
# Defined in: app/api/v1/achievement_routes.py
from app.api.v1.achievement_routes import router as achievement_router

# Import router from avatar routes file
# Defined in: app/api/v1/avatar_routes.py
from app.api.v1.avatar_routes import router as avatar_router

# Import router from leaderboard routes file
# Defined in: app/api/v1/leaderboard_routes.py
from app.api.v1.leaderboard_routes import router as leaderboard_router

# Import router from admin routes file
# Defined in: app/api/v1/admin_routes.py
from app.api.v1.admin_routes import router as admin_router

# Import router from bookmark routes file
# Defined in: app/api/v1/bookmark_routes.py
from app.api.v1.bookmark_routes import router as bookmark_router

# Import router from health routes file (not versioned - for monitoring)
# Defined in: app/api/health_routes.py
from app.api.health_routes import router as health_router

# Register the auth router with /api/v1 prefix
# This creates routes:
#   - POST /api/v1/auth/signup
#   - POST /api/v1/auth/login
#   - GET  /api/v1/auth/me
app.include_router(auth_router, prefix="/api/v1")

# Register the question router with /api/v1 prefix
# This creates routes:
#   - GET /api/v1/questions/exams
#   - GET /api/v1/questions/quiz?exam_type=security&count=30
app.include_router(question_router, prefix="/api/v1")

# Register the quiz router with /api/v1 prefix
# This creates routes (PRACTICE MODE):
#   - POST /api/v1/quiz/submit
#   - GET  /api/v1/quiz/history
#   - GET  /api/v1/quiz/stats
app.include_router(quiz_router, prefix="/api/v1")

# Register the study mode router with /api/v1 prefix
# This creates routes (STUDY MODE):
#   - POST /api/v1/study/start
#   - POST /api/v1/study/answer
#   - GET  /api/v1/study/active
#   - DELETE /api/v1/study/abandon
app.include_router(study_router, prefix="/api/v1")

# Register the achievement router with /api/v1 prefix
# This creates routes:
#   - GET /api/v1/achievements
#   - GET /api/v1/achievements/me
#   - GET /api/v1/achievements/earned
#   - GET /api/v1/achievements/stats
app.include_router(achievement_router, prefix="/api/v1")

# Register the avatar router with /api/v1 prefix
# This creates routes:
#   - GET /api/v1/avatars
#   - GET /api/v1/avatars/me
#   - GET /api/v1/avatars/unlocked
#   - POST /api/v1/avatars/select
#   - GET /api/v1/avatars/stats
app.include_router(avatar_router, prefix="/api/v1")

# Register the leaderboard router with /api/v1 prefix
# This creates routes:
#   - GET /api/v1/leaderboard/xp
#   - GET /api/v1/leaderboard/quiz-count
#   - GET /api/v1/leaderboard/accuracy
#   - GET /api/v1/leaderboard/streak
#   - GET /api/v1/leaderboard/exam/{exam_type}
app.include_router(leaderboard_router, prefix="/api/v1")

# Register the admin router with /api/v1 prefix
# This creates routes (admin-only):
#   - GET    /api/v1/admin/questions - List questions with pagination
#   - POST   /api/v1/admin/questions - Create new question
#   - GET    /api/v1/admin/questions/{id} - Get question details
#   - PUT    /api/v1/admin/questions/{id} - Update question
#   - DELETE /api/v1/admin/questions/{id} - Delete question
#   - GET    /api/v1/admin/users - List users with pagination
#   - GET    /api/v1/admin/users/{id} - Get user details
#   - GET    /api/v1/admin/achievements - List all achievements
#   - POST   /api/v1/admin/achievements - Create achievement
#   - PUT    /api/v1/admin/achievements/{id} - Update achievement
#   - DELETE /api/v1/admin/achievements/{id} - Delete achievement
app.include_router(admin_router, prefix="/api/v1")

# Register the bookmark router with /api/v1 prefix
# This creates routes:
#   - POST   /api/v1/bookmarks/questions/{question_id} - Bookmark a question
#   - GET    /api/v1/bookmarks - Get user's bookmarks (paginated)
#   - DELETE /api/v1/bookmarks/questions/{question_id} - Remove bookmark
#   - PATCH  /api/v1/bookmarks/questions/{question_id} - Update bookmark notes
#   - GET    /api/v1/bookmarks/questions/{question_id}/check - Check if bookmarked
app.include_router(bookmark_router, prefix="/api/v1")

# Register the health router (no prefix - not versioned)
# This creates routes:
#   - GET /health - Application health check for monitoring
# Note: Health checks are intentionally NOT versioned (/api/v1)
# Monitoring tools expect a stable endpoint that never changes
app.include_router(health_router)


# ============================================
# BACKGROUND TASKS
# ============================================
# Start scheduled background tasks (runs independently of HTTP requests)
from app.tasks import start_background_tasks

# Use startup event to initialize scheduler when app starts
@app.on_event("startup")
async def startup_event():
    """Initialize background tasks on application startup"""
    # Skip background tasks in test environment
    if not os.getenv("TESTING", "false").lower() == "true":
        start_background_tasks()
    else:
        print("[TEST MODE] Skipping background task initialization")
