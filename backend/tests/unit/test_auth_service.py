"""
Unit Tests for Auth Service

Tests the auth service layer functions directly (no HTTP requests).
These are pure unit tests that test database operations in isolation.
"""

import pytest
from datetime import datetime
from app.services.auth_service import (
    create_user,
    get_user_by_email,
    get_user_by_username,
    get_user_by_id,
    check_password_in_history,
)
from app.utils.auth import verify_password


@pytest.mark.unit
def test_create_user_hashes_password(test_db):
    """Test that create_user properly hashes the password"""
    email = "newuser@example.com"
    password = "Plain@Text9Pass!"
    username = "newuser"

    user = create_user(test_db, email=email, password=password, username=username)

    # User should be created with ID
    assert user.id is not None
    assert user.email == email
    assert user.username == username

    # Password should be hashed (not plain text)
    assert user.hashed_password != password
    assert user.hashed_password.startswith("$2b$")  # bcrypt hash prefix

    # Hashed password should verify correctly
    assert verify_password(password, user.hashed_password)

    # Wrong password should not verify
    assert not verify_password("Wrong@Pass8!", user.hashed_password)


@pytest.mark.unit
def test_get_user_by_email(test_db, test_user):
    """Test retrieving user by email"""
    # Retrieve existing user
    found = get_user_by_email(test_db, "test@example.com")

    assert found is not None
    assert found.id == test_user.id
    assert found.email == test_user.email
    assert found.username == test_user.username


@pytest.mark.unit
def test_get_user_by_email_not_found(test_db):
    """Test that get_user_by_email returns None for non-existent email"""
    found = get_user_by_email(test_db, "nonexistent@example.com")

    assert found is None


@pytest.mark.unit
def test_get_user_by_username(test_db, test_user):
    """Test retrieving user by username"""
    found = get_user_by_username(test_db, "testuser")

    assert found is not None
    assert found.id == test_user.id
    assert found.username == test_user.username
    assert found.email == test_user.email


@pytest.mark.unit
def test_get_user_by_username_not_found(test_db):
    """Test that get_user_by_username returns None for non-existent username"""
    found = get_user_by_username(test_db, "nonexistent_user")

    assert found is None


@pytest.mark.unit
def test_get_user_by_id(test_db, test_user):
    """Test retrieving user by ID"""
    found = get_user_by_id(test_db, test_user.id)

    assert found is not None
    assert found.id == test_user.id
    assert found.email == test_user.email


@pytest.mark.unit
def test_get_user_by_id_not_found(test_db):
    """Test that get_user_by_id returns None for non-existent ID"""
    found = get_user_by_id(test_db, 99999)

    assert found is None


@pytest.mark.unit
def test_check_password_in_history_not_used(test_db, test_user):
    """Test that new password is allowed (not in history)"""
    new_password = "NewUnique@Pass9!"

    # Check if password was used before (should return False)
    was_used = check_password_in_history(test_db, test_user.id, new_password)

    assert was_used is False


@pytest.mark.unit
def test_check_password_in_history_was_used(test_db, test_user):
    """Test that old password is detected in history"""
    from app.services.auth_service import add_password_to_history
    from app.utils.auth import hash_password

    # Add password to history
    old_password = "OldUsed@Pass8!"
    password_hash = hash_password(old_password)
    add_password_to_history(test_db, test_user.id, password_hash, reason="test")

    # Check if password was used before (should return True)
    was_used = check_password_in_history(test_db, test_user.id, old_password)

    assert was_used is True


@pytest.mark.unit
def test_create_user_sets_timestamps(test_db):
    """Test that create_user sets created_at and updated_at timestamps"""
    before = datetime.utcnow()

    user = create_user(
        test_db,
        email="timestamps@example.com",
        password="Test@Pass9word!",
        username="timestamps"
    )

    after = datetime.utcnow()

    # Timestamps should be set
    assert user.created_at is not None
    assert user.updated_at is not None

    # Timestamps should be reasonable (between before and after)
    assert before <= user.created_at <= after
    assert before <= user.updated_at <= after


@pytest.mark.unit
def test_password_hash_is_different_each_time(test_db):
    """Test that hashing the same password twice produces different hashes (salt)"""
    password = "Same@Pass9word!"

    user1 = create_user(test_db, "user1@example.com", password, "user1")
    user2 = create_user(test_db, "user2@example.com", password, "user2")

    # Different users with same password should have different hashes (bcrypt salt)
    assert user1.hashed_password != user2.hashed_password

    # But both should verify correctly
    assert verify_password(password, user1.hashed_password)
    assert verify_password(password, user2.hashed_password)
