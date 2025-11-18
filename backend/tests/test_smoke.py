"""
Smoke Tests

Basic tests to verify test infrastructure is working correctly.
These should always pass if the setup is correct.
"""

import pytest
from app.models.user import User, UserProfile


# ================================================================
# DATABASE TESTS
# ================================================================

def test_database_connection(test_db):
    """Test that we can connect to the test database"""
    # If this runs without error, database connection works
    assert test_db is not None


def test_create_user(test_db):
    """Test that we can create a user in the test database"""
    user = User(
        email="smoke@test.com",
        username="smoketest",
        hashed_password="hashed_pass",
        is_active=True
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)

    # Verify user was created
    assert user.id is not None
    assert user.email == "smoke@test.com"


# ================================================================
# FIXTURE TESTS
# ================================================================

def test_user_fixture(test_user):
    """Test that test_user fixture creates a user correctly"""
    assert test_user.id is not None
    assert test_user.email == "test@example.com"
    assert test_user.username == "testuser"


def test_user_has_profile(test_db, test_user):
    """Test that test_user has an associated profile"""
    profile = test_db.query(UserProfile).filter(
        UserProfile.user_id == test_user.id
    ).first()

    assert profile is not None
    assert profile.xp == 0
    assert profile.level == 1


def test_auth_token_fixture(test_user_token):
    """Test that JWT token is generated"""
    assert test_user_token is not None
    assert isinstance(test_user_token, str)
    assert len(test_user_token) > 0


def test_auth_headers_fixture(auth_headers):
    """Test that auth headers are formatted correctly"""
    assert "Authorization" in auth_headers
    assert auth_headers["Authorization"].startswith("Bearer ")


# ================================================================
# API TESTS
# ================================================================

def test_api_client(client):
    """Test that TestClient is working"""
    # Test root endpoint (if it exists) or docs
    response = client.get("/docs")
    # Docs endpoint should be accessible
    assert response.status_code in [200, 404]  # 404 is ok if no docs route


def test_api_health_check(client):
    """Test basic API functionality"""
    # Test that we can make requests
    response = client.get("/api/v1/questions/exams")
    # Should get 200 (returns exam list)
    assert response.status_code == 200


def test_api_authentication(client, auth_headers):
    """Test that authentication works with test fixtures"""
    response = client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"


# ================================================================
# ISOLATION TESTS
# ================================================================

def test_database_isolation_1(test_db):
    """Test 1: Create a user"""
    user = User(email="isolation1@test.com", username="user1", hashed_password="pass")
    test_db.add(user)
    test_db.commit()

    # User should exist
    users = test_db.query(User).filter(User.email == "isolation1@test.com").all()
    assert len(users) == 1


def test_database_isolation_2(test_db):
    """Test 2: Verify user from test 1 doesn't exist (tests are isolated)"""
    # User from previous test should NOT exist
    users = test_db.query(User).filter(User.email == "isolation1@test.com").all()
    assert len(users) == 0  # Database is clean for each test
