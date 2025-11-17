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

# FastAPI - modern web framework for building APIs
from fastapi import FastAPI

# CORS Middleware - allows React frontend to make requests to this API
# Without CORS, browsers block cross-origin requests (frontend on :5173, backend on :8000)
from fastapi.middleware.cors import CORSMiddleware

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


# ============================================
# CONFIGURE CORS MIDDLEWARE
# ============================================
# Allow React frontend to make API requests from different origin (localhost:5173 or :3000)
# Origins: List of URLs that are allowed to make requests to this API
# Credentials: Allow cookies and Authorization headers to be sent
# Methods/Headers: Allow all HTTP methods and headers
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite default dev server
        "http://localhost:3000",  # Create React App default
    ],
    allow_credentials=True,  # Required for sending JWT tokens in headers
    allow_methods=["*"],  # Allow GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],  # Allow Authorization, Content-Type, etc.
)


# ============================================
# REGISTER ROUTE MODULES
# ============================================
# Import router from auth routes file
# Defined in: app/api/v1/auth_routes.py
from app.api.v1.auth_routes import router as auth_router

# Register the auth router with /api/v1 prefix
# This creates routes:
#   - POST /api/v1/auth/signup
#   - POST /api/v1/auth/login
#   - GET  /api/v1/auth/me
app.include_router(auth_router, prefix="/api/v1")
