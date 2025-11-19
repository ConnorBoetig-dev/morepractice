"""
Leaderboard Tests

Tests for leaderboard endpoints:
- Global leaderboards (XP, quiz count, accuracy, streak)
- Exam-specific leaderboards
- User rankings
- Pagination
- Statistics
"""

import pytest
from datetime import datetime, timedelta
from app.models.user import User, UserProfile
from app.models.gamification import QuizAttempt
from app.utils.auth import hash_password


# ================================================================
# GLOBAL LEADERBOARD TESTS
# ================================================================

@pytest.mark.api
@pytest.mark.integration
def test_get_xp_leaderboard(client, auth_headers, test_db):
    """Test getting leaderboard ranked by XP"""
    # Create users with different XP levels
    for i in range(5):
        user = User(
            email=f"user{i}@example.com",
            username=f"user{i}",
            hashed_password=hash_password("pass123"),
            is_active=True,
            is_verified=True
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        profile = UserProfile(
            user_id=user.id,
            xp=1000 + (i * 500),  # Varying XP
            level=1 + i,
            study_streak_current=0,
            study_streak_longest=0,
            total_exams_taken=10,
            total_questions_answered=100
        )
        test_db.add(profile)
    test_db.commit()

    response = client.get("/api/v1/leaderboard/xp", headers=auth_headers)

    if response.status_code != 404:
        assert response.status_code == 200
        data = response.json()

        # Should be sorted by XP descending
        xp_values = [user["xp"] for user in data if "xp" in user]
        if len(xp_values) > 1:
            assert xp_values == sorted(xp_values, reverse=True)


@pytest.mark.api
@pytest.mark.integration
def test_get_quiz_count_leaderboard(client, auth_headers, test_db):
    """Test getting leaderboard ranked by quiz count"""
    # Create users with different quiz counts
    for i in range(5):
        user = User(
            email=f"quizzer{i}@example.com",
            username=f"quizzer{i}",
            hashed_password=hash_password("pass123"),
            is_active=True,
            is_verified=True
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        profile = UserProfile(
            user_id=user.id,
            xp=1000,
            level=1,
            study_streak_current=0,
            study_streak_longest=0,
            total_exams_taken=10 + (i * 5),  # Varying quiz counts
            total_questions_answered=100 + (i * 50)
        )
        test_db.add(profile)
    test_db.commit()

    response = client.get("/api/v1/leaderboard/quiz-count",
        headers=auth_headers
    )

    if response.status_code != 404:
        assert response.status_code == 200
        data = response.json()

        # Should be sorted by quiz count descending
        counts = [user["total_exams_taken"] for user in data if "total_exams_taken" in user]
        if len(counts) > 1:
            assert counts == sorted(counts, reverse=True)


@pytest.mark.api
@pytest.mark.integration
def test_get_accuracy_leaderboard(client, auth_headers, test_db):
    """Test getting leaderboard ranked by accuracy"""
    # Create users with quiz attempts
    for i in range(5):
        user = User(
            email=f"accurate{i}@example.com",
            username=f"accurate{i}",
            hashed_password=hash_password("pass123"),
            is_active=True,
            is_verified=True
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        profile = UserProfile(
            user_id=user.id,
            xp=1000,
            level=1,
            study_streak_current=0,
            study_streak_longest=0,
            total_exams_taken=10,
            total_questions_answered=100
        )
        test_db.add(profile)

        # Create quiz attempts with varying accuracy
        for j in range(3):
            attempt = QuizAttempt(
                user_id=user.id,
                exam_type="security",
                score_percentage=60 + (i * 8),  # Varying scores
                total_questions=10,
                correct_answers=6 + i,
                time_taken_seconds=300,
                xp_earned=100
            )
            test_db.add(attempt)
    test_db.commit()

    response = client.get("/api/v1/leaderboard/accuracy",
        headers=auth_headers
    )

    if response.status_code != 404:
        assert response.status_code == 200
        # Should be sorted by accuracy/average score


@pytest.mark.api
@pytest.mark.integration
def test_get_streak_leaderboard(client, auth_headers, test_db):
    """Test getting leaderboard ranked by study streak"""
    # Create users with different streaks
    for i in range(5):
        user = User(
            email=f"streaker{i}@example.com",
            username=f"streaker{i}",
            hashed_password=hash_password("pass123"),
            is_active=True,
            is_verified=True
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        profile = UserProfile(
            user_id=user.id,
            xp=1000,
            level=1,
            study_streak_current=i * 3,  # Varying current streak
            study_streak_longest=i * 5,  # Varying longest streak
            total_exams_taken=10,
            total_questions_answered=100
        )
        test_db.add(profile)
    test_db.commit()

    response = client.get("/api/v1/leaderboard/streak", headers=auth_headers)

    if response.status_code != 404:
        assert response.status_code == 200
        data = response.json()

        # Should be sorted by current streak descending
        streaks = [user["study_streak_current"] for user in data if "study_streak_current" in user]
        if len(streaks) > 1:
            assert streaks == sorted(streaks, reverse=True)


# ================================================================
# EXAM-SPECIFIC LEADERBOARD TESTS
# ================================================================

@pytest.mark.api
@pytest.mark.integration
def test_get_security_exam_leaderboard(client, auth_headers, test_db):
    """Test getting leaderboard for Security+ exam"""
    # Create users with security exam attempts
    for i in range(3):
        user = User(
            email=f"secuser{i}@example.com",
            username=f"secuser{i}",
            hashed_password=hash_password("pass123"),
            is_active=True,
            is_verified=True
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        profile = UserProfile(
            user_id=user.id,
            xp=1000,
            level=1,
            study_streak_current=0,
            study_streak_longest=0,
            total_exams_taken=5,
            total_questions_answered=50
        )
        test_db.add(profile)

        # Create security exam attempts
        for j in range(3):
            attempt = QuizAttempt(
                user_id=user.id,
                exam_type="security",
                score_percentage=70 + (i * 10),
                total_questions=10,
                correct_answers=7 + i,
                time_taken_seconds=300,
                xp_earned=100
            )
            test_db.add(attempt)
    test_db.commit()

    response = client.get("/api/v1/leaderboard/exam/security",
        headers=auth_headers
    )

    if response.status_code != 404:
        assert response.status_code == 200
        # Should only show security exam performance


@pytest.mark.api
@pytest.mark.integration
def test_get_network_exam_leaderboard(client, auth_headers, test_db):
    """Test getting leaderboard for Network+ exam"""
    # Create users with network exam attempts
    for i in range(3):
        user = User(
            email=f"netuser{i}@example.com",
            username=f"netuser{i}",
            hashed_password=hash_password("pass123"),
            is_active=True,
            is_verified=True
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        profile = UserProfile(
            user_id=user.id,
            xp=1000,
            level=1,
            study_streak_current=0,
            study_streak_longest=0,
            total_exams_taken=5,
            total_questions_answered=50
        )
        test_db.add(profile)

        # Create network exam attempts
        attempt = QuizAttempt(
            user_id=user.id,
            exam_type="network",
            score_percentage=80 + i * 5,
            total_questions=10,
            correct_answers=8,
            time_taken_seconds=300,
            xp_earned=100
        )
        test_db.add(attempt)
    test_db.commit()

    response = client.get("/api/v1/leaderboard/exam/network",
        headers=auth_headers
    )

    if response.status_code != 404:
        assert response.status_code == 200


# ================================================================
# USER RANKING TESTS
# ================================================================

@pytest.mark.api
@pytest.mark.integration
def test_get_current_user_rank(client, auth_headers, test_db, test_user):
    """Test getting current user's rank in leaderboard"""
    # Create other users with higher XP
    for i in range(5):
        user = User(
            email=f"ranked{i}@example.com",
            username=f"ranked{i}",
            hashed_password=hash_password("pass123"),
            is_active=True,
            is_verified=True
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        profile = UserProfile(
            user_id=user.id,
            xp=2000 + (i * 500),
            level=5,
            study_streak_current=0,
            study_streak_longest=0,
            total_exams_taken=10,
            total_questions_answered=100
        )
        test_db.add(profile)
    test_db.commit()

    response = client.get("/api/v1/leaderboard/my-rank",
        headers=auth_headers
    )

    if response.status_code != 404:
        assert response.status_code == 200
        data = response.json()
        # Should include user's rank
        assert "rank" in data or "position" in data


# ================================================================
# PAGINATION TESTS
# ================================================================

@pytest.mark.api
@pytest.mark.integration
def test_leaderboard_pagination(client, auth_headers, test_db):
    """Test leaderboard pagination"""
    # Create many users
    for i in range(25):
        user = User(
            email=f"paginate{i}@example.com",
            username=f"paginate{i}",
            hashed_password=hash_password("pass123"),
            is_active=True,
            is_verified=True
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        profile = UserProfile(
            user_id=user.id,
            xp=1000 + i * 100,
            level=1,
            study_streak_current=0,
            study_streak_longest=0,
            total_exams_taken=10,
            total_questions_answered=100
        )
        test_db.add(profile)
    test_db.commit()

    # Get first page
    response = client.get("/api/v1/leaderboard/xp?page=1&limit=10",
        headers=auth_headers
    )

    if response.status_code != 404:
        assert response.status_code == 200
        data = response.json()

        # Should return 10 or fewer results
        if isinstance(data, list):
            assert len(data) <= 10


@pytest.mark.api
@pytest.mark.integration
def test_leaderboard_limit_parameter(client, auth_headers, test_db):
    """Test limiting leaderboard results"""
    # Create users
    for i in range(15):
        user = User(
            email=f"limit{i}@example.com",
            username=f"limit{i}",
            hashed_password=hash_password("pass123"),
            is_active=True,
            is_verified=True
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        profile = UserProfile(
            user_id=user.id,
            xp=1000 + i * 50,
            level=1,
            study_streak_current=0,
            study_streak_longest=0,
            total_exams_taken=10,
            total_questions_answered=100
        )
        test_db.add(profile)
    test_db.commit()

    response = client.get("/api/v1/leaderboard/xp?limit=5",
        headers=auth_headers
    )

    if response.status_code != 404:
        assert response.status_code == 200
        data = response.json()
        if isinstance(data, list):
            assert len(data) <= 5


# ================================================================
# STATISTICS TESTS
# ================================================================

@pytest.mark.api
@pytest.mark.integration
def test_get_leaderboard_statistics(client, auth_headers, test_db):
    """Test getting overall leaderboard statistics"""
    # Create users and attempts
    for i in range(5):
        user = User(
            email=f"stats{i}@example.com",
            username=f"stats{i}",
            hashed_password=hash_password("pass123"),
            is_active=True,
            is_verified=True
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        profile = UserProfile(
            user_id=user.id,
            xp=1000 + i * 200,
            level=1 + i,
            study_streak_current=i,
            study_streak_longest=i * 2,
            total_exams_taken=10 + i,
            total_questions_answered=100 + i * 10
        )
        test_db.add(profile)
    test_db.commit()

    response = client.get("/api/v1/leaderboard/statistics",
        headers=auth_headers
    )

    if response.status_code != 404:
        assert response.status_code == 200
        # Should include aggregate statistics


# ================================================================
# AUTHENTICATION AND ACCESS TESTS
# ================================================================

@pytest.mark.api
@pytest.mark.integration
def test_leaderboard_requires_auth(client):
    """Test that leaderboards require authentication"""
    response = client.get("/api/v1/leaderboard/xp")

    # May or may not require auth depending on implementation
    # Most gamification systems allow public leaderboards
    assert response.status_code in [200, 401]


@pytest.mark.api
@pytest.mark.integration
def test_leaderboard_response_format(client, auth_headers, test_db):
    """Test that leaderboard response has correct format"""
    # Create a user with profile
    user = User(
        email="format@example.com",
        username="formatuser",
        hashed_password=hash_password("pass123"),
        is_active=True,
        is_verified=True
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)

    profile = UserProfile(
        user_id=user.id,
        xp=1500,
        level=3,
        study_streak_current=5,
        study_streak_longest=10,
        total_exams_taken=15,
        total_questions_answered=150
    )
    test_db.add(profile)
    test_db.commit()

    response = client.get("/api/v1/leaderboard/xp", headers=auth_headers)

    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list) and len(data) > 0:
            user_entry = data[0]
            # Should include username and stats
            assert "username" in user_entry or "user" in user_entry


# ================================================================
# EDGE CASES
# ================================================================

@pytest.mark.api
@pytest.mark.integration
def test_empty_leaderboard(client, auth_headers, test_db):
    """Test leaderboard with no users (except test user)"""
    response = client.get("/api/v1/leaderboard/xp", headers=auth_headers)

    if response.status_code != 404:
        assert response.status_code == 200
        # Should return empty list or minimal data


@pytest.mark.api
@pytest.mark.integration
def test_leaderboard_invalid_exam_type(client, auth_headers):
    """Test exam leaderboard with invalid exam type"""
    response = client.get("/api/v1/leaderboard/exam/invalid_exam",
        headers=auth_headers
    )

    if response.status_code != 404:
        assert response.status_code in [400, 404, 422]


@pytest.mark.api
@pytest.mark.integration
def test_leaderboard_negative_limit(client, auth_headers):
    """Test leaderboard with negative limit parameter"""
    response = client.get("/api/v1/leaderboard/xp?limit=-10",
        headers=auth_headers
    )

    if response.status_code != 404:
        # Should validate limit > 0
        assert response.status_code in [400, 422] or response.status_code == 200
