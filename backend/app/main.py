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

# Rate limiting - protects API from abuse and DDoS attacks
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.utils.rate_limit import limiter  # Import centralized limiter

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
from app.models.user import User, UserProfile

# Question model - defined in: app/models/question.py
from app.models.question import Question

# Gamification models - defined in: app/models/gamification.py
from app.models.gamification import (
    QuizAttempt, UserAnswer, Achievement, UserAchievement, Avatar, UserAvatar
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
app = FastAPI(title="Billings API")  # Creates the FastAPI app instance

# Add rate limiter to app state (makes it accessible to routes)
app.state.limiter = limiter

# Register rate limit exceeded handler (returns 429 status)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


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
        "http://localhost:8080",    # Frontend via localhost
        "http://127.0.0.1:8080",    # Frontend via 127.0.0.1 (same machine, different origin)
    ],
    allow_credentials=True,  # Allow Authorization headers (for JWT tokens)
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE)
    allow_headers=["*"],  # Allow all headers (Content-Type, Authorization, etc.)
)


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

# Import router from achievement routes file
# Defined in: app/api/v1/achievement_routes.py
from app.api.v1.achievement_routes import router as achievement_router

# Import router from avatar routes file
# Defined in: app/api/v1/avatar_routes.py
from app.api.v1.avatar_routes import router as avatar_router

# Import router from leaderboard routes file
# Defined in: app/api/v1/leaderboard_routes.py
from app.api.v1.leaderboard_routes import router as leaderboard_router

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
# This creates routes:
#   - POST /api/v1/quiz/submit
#   - GET  /api/v1/quiz/history
#   - GET  /api/v1/quiz/stats
app.include_router(quiz_router, prefix="/api/v1")

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


# ============================================
# BACKGROUND TASKS
# ============================================
# Start scheduled background tasks (runs independently of HTTP requests)
from app.tasks import start_background_tasks

# Use startup event to initialize scheduler when app starts
@app.on_event("startup")
async def startup_event():
    """Initialize background tasks on application startup"""
    start_background_tasks()
