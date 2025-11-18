"""
Pytest Configuration and Fixtures

This file contains shared test fixtures for the entire test suite.
Fixtures are automatically discovered by pytest.

Test Database:
- Uses PostgreSQL running in Docker on port 5433
- Database: billings_test
- Start with: cd tests && docker compose up
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.models.user import User, UserProfile
from app.utils.auth import hash_password, create_access_token


# Test database URL (port 5433, different from dev DB on 5432)
TEST_DATABASE_URL = "postgresql://postgres:postgres@localhost:5433/billings_test"


# ================================================================
# DATABASE FIXTURES
# ================================================================

@pytest.fixture(scope="session")
def test_engine():
    """
    Create database engine for test database

    Scope: session (created once per test session, shared across all tests)
    """
    engine = create_engine(TEST_DATABASE_URL, echo=False)
    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def test_db(test_engine):
    """
    Create a clean database for each test

    Process:
    1. Drop all tables (clean slate)
    2. Create all tables (fresh schema)
    3. Create session
    4. Run test
    5. Close session and drop tables

    Scope: function (new database for each test = isolated tests)
    """
    # Create all tables
    Base.metadata.create_all(bind=test_engine)

    # Create session factory
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    # Create session
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()

        # Drop all tables (cleanup)
        # Use raw SQL with CASCADE to handle circular dependencies
        from sqlalchemy import text
        with test_engine.begin() as conn:
            # Drop schema to remove all tables and constraints
            conn.execute(text("DROP SCHEMA public CASCADE"))
            conn.execute(text("CREATE SCHEMA public"))
            conn.execute(text("GRANT ALL ON SCHEMA public TO postgres"))
            conn.execute(text("GRANT ALL ON SCHEMA public TO public"))


@pytest.fixture(scope="function")
def client(test_db):
    """
    FastAPI TestClient with test database dependency override

    This client makes HTTP requests to FastAPI without starting a server.
    All database operations use test_db instead of the real database.
    """
    # Override get_db dependency to use test database
    def override_get_db():
        try:
            yield test_db
        finally:
            pass  # test_db fixture handles cleanup

    app.dependency_overrides[get_db] = override_get_db

    # Create test client
    with TestClient(app) as test_client:
        yield test_client

    # Clean up dependency override
    app.dependency_overrides.clear()


# ================================================================
# USER FIXTURES
# ================================================================

@pytest.fixture(scope="function")
def test_user(test_db):
    """
    Create a test user in the database

    Returns:
        User: User model with hashed password
    """
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=hash_password("testpass123"),
        is_active=True,
        is_verified=False
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)

    # Create user profile (required for quiz submission)
    profile = UserProfile(
        user_id=user.id,
        xp=0,
        level=1,
        study_streak_current=0,
        study_streak_longest=0,
        total_exams_taken=0,
        total_questions_answered=0
    )
    test_db.add(profile)
    test_db.commit()

    return user


@pytest.fixture(scope="function")
def test_user_token(test_user):
    """
    Create a JWT token for test user

    Returns:
        str: Valid JWT token
    """
    return create_access_token(data={"user_id": test_user.id})


@pytest.fixture(scope="function")
def auth_headers(test_user_token):
    """
    Create authorization headers for authenticated requests

    Returns:
        dict: Headers with Bearer token
    """
    return {"Authorization": f"Bearer {test_user_token}"}
