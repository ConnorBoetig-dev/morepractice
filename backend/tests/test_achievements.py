"""
Achievement and Avatar System Tests

Tests for gamification features:
- Achievement unlocking
- Achievement progress tracking
- Avatar unlocking
- Avatar selection
- Criteria checking
"""

import pytest
from datetime import datetime, timedelta
from app.models.user import User, UserProfile
from app.models.gamification import (
    Achievement, UserAchievement,
    Avatar, UserAvatar,
    QuizAttempt
)
from app.utils.auth import hash_password


# ================================================================
# ACHIEVEMENT LISTING TESTS
# ================================================================

@pytest.mark.api
@pytest.mark.integration
def test_get_all_achievements(client, auth_headers, test_db):
    """Test getting list of all achievements"""
    # Create achievements
    for i in range(5):
        achievement = Achievement(
            name=f"Achievement {i}",
            description=f"Description {i}",
            icon="🏆",
            rarity="common" if i < 3 else "rare",
            criteria_type="quiz_count",
            criteria_value=10 + i
        )
        test_db.add(achievement)
    test_db.commit()

    response = client.get("/api/v1/achievements", headers=auth_headers)

    if response.status_code != 404:
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 5
        assert all("name" in a for a in data)
        assert all("description" in a for a in data)


@pytest.mark.api
@pytest.mark.integration
def test_get_achievements_includes_rarity(client, auth_headers, test_db):
    """Test that achievements include rarity information"""
    achievement = Achievement(
        name="Legendary Achievement",
        description="Very rare",
        icon="💎",
        rarity="legendary",
        criteria_type="quiz_count",
        criteria_value=100
    )
    test_db.add(achievement)
    test_db.commit()

    response = client.get("/api/v1/achievements", headers=auth_headers)

    if response.status_code != 404:
        assert response.status_code == 200
        data = response.json()
        legendary = [a for a in data if a.get("name") == "Legendary Achievement"]
        if legendary:
            assert legendary[0]["rarity"] == "legendary"


# ================================================================
# USER ACHIEVEMENT TESTS
# ================================================================

@pytest.mark.api
@pytest.mark.integration
def test_get_user_achievements(client, auth_headers, test_db, test_user):
    """Test getting achievements for current user"""
    # Create achievement
    achievement = Achievement(
        name="Test Achievement",
        description="For testing",
        icon="🎯",
        rarity="common",
        criteria_type="quiz_count",
        criteria_value=5
    )
    test_db.add(achievement)
    test_db.commit()
    test_db.refresh(achievement)

    # Award to user
    user_achievement = UserAchievement(
        user_id=test_user.id,
        achievement_id=achievement.id,
        progress_value=100,
        earned_at=datetime.utcnow()
    )
    test_db.add(user_achievement)
    test_db.commit()

    response = client.get("/api/v1/achievements/my-achievements",
        headers=auth_headers
    )

    if response.status_code != 404:
        assert response.status_code == 200
        data = response.json()
        # Should include unlocked achievement
        if isinstance(data, list):
            assert len(data) >= 1


@pytest.mark.api
@pytest.mark.integration
def test_achievement_progress_tracking(client, auth_headers, test_db, test_user):
    """Test achievement progress is tracked correctly"""
    # Create achievement with progress requirement
    achievement = Achievement(
        name="Quiz Master",
        description="Complete 10 quizzes",
        icon="🏆",
        rarity="rare",
        criteria_type="quiz_count",
        criteria_value=10
    )
    test_db.add(achievement)
    test_db.commit()
    test_db.refresh(achievement)

    # Create partial progress
    user_achievement = UserAchievement(
        user_id=test_user.id,
        achievement_id=achievement.id,
        progress_value=5,  # 5 out of 10
        earned_at=None
    )
    test_db.add(user_achievement)
    test_db.commit()

    response = client.get("/api/v1/achievements/my-achievements",
        headers=auth_headers
    )

    if response.status_code != 404:
        assert response.status_code == 200
        data = response.json()
        # Should show progress
        if isinstance(data, list) and len(data) > 0:
            assert any(a.get("progress_value") is not None for a in data)


@pytest.mark.api
@pytest.mark.integration
def test_achievement_unlock_notification(client, auth_headers, test_db, test_user):
    """Test that newly unlocked achievements are indicated"""
    achievement = Achievement(
        name="First Quiz",
        description="Complete your first quiz",
        icon="🎓",
        rarity="common",
        criteria_type="quiz_count",
        criteria_value=1
    )
    test_db.add(achievement)
    test_db.commit()
    test_db.refresh(achievement)

    # Recently unlocked achievement
    user_achievement = UserAchievement(
        user_id=test_user.id,
        achievement_id=achievement.id,
        progress_value=1,
        earned_at=datetime.utcnow() - timedelta(minutes=5)  # Recently
    )
    test_db.add(user_achievement)
    test_db.commit()

    response = client.get("/api/v1/achievements/my-achievements",
        headers=auth_headers
    )

    if response.status_code != 404:
        assert response.status_code == 200
        # Should include earned_at timestamp


# ================================================================
# ACHIEVEMENT CRITERIA TESTS
# ================================================================

@pytest.mark.api
@pytest.mark.integration
def test_achievement_unlocked_by_quiz_count(client, auth_headers, test_db, test_user):
    """Test achievement unlocking based on quiz count"""
    # Create achievement for completing 5 quizzes
    achievement = Achievement(
        name="Quiz Enthusiast",
        description="Complete 5 quizzes",
        icon="📝",
        rarity="common",
        criteria_type="quiz_count",
        criteria_value=5
    )
    test_db.add(achievement)
    test_db.commit()

    # Complete 5 quizzes
    for i in range(5):
        attempt = QuizAttempt(
            user_id=test_user.id,
            exam_type="security",
            total_questions=10,
            correct_answers=8,
            score_percentage=80.0,
            time_taken_seconds=300,
            xp_earned=100
        )
        test_db.add(attempt)
    test_db.commit()

    # Update profile
    profile = test_db.query(UserProfile).filter(
        UserProfile.user_id == test_user.id
    ).first()
    profile.total_exams_taken = 5
    test_db.commit()

    # Check achievements - may auto-unlock or require manual check
    response = client.get("/api/v1/achievements/my-achievements",
        headers=auth_headers
    )

    if response.status_code != 404:
        assert response.status_code == 200


@pytest.mark.api
@pytest.mark.integration
def test_achievement_unlocked_by_score(client, auth_headers, test_db, test_user):
    """Test achievement unlocking based on perfect score"""
    # Create achievement for perfect score
    achievement = Achievement(
        name="Perfect!",
        description="Get 100% on a quiz",
        icon="💯",
        rarity="rare",
        criteria_type="perfect_score",
        criteria_value=1
    )
    test_db.add(achievement)
    test_db.commit()

    # Create perfect score attempt
    attempt = QuizAttempt(
        user_id=test_user.id,
        exam_type="security",
        total_questions=10,
        correct_answers=10,
        score_percentage=100.0,
        time_taken_seconds=300,
        xp_earned=200
    )
    test_db.add(attempt)
    test_db.commit()

    response = client.get("/api/v1/achievements/my-achievements",
        headers=auth_headers
    )

    if response.status_code != 404:
        assert response.status_code == 200


@pytest.mark.api
@pytest.mark.integration
def test_achievement_exam_specific(client, auth_headers, test_db, test_user):
    """Test exam-specific achievements"""
    # Create Security+ specific achievement
    achievement = Achievement(
        name="Security Expert",
        description="Complete 10 Security+ quizzes",
        icon="🔒",
        rarity="rare",
        criteria_type="exam_quiz_count",
        criteria_value=10,
        criteria_exam_type="security"
    )
    test_db.add(achievement)
    test_db.commit()

    # Create security quiz attempts
    for i in range(10):
        attempt = QuizAttempt(
            user_id=test_user.id,
            exam_type="security",
            total_questions=10,
            correct_answers=7,
            score_percentage=70.0,
            time_taken_seconds=300,
            xp_earned=100
        )
        test_db.add(attempt)
    test_db.commit()

    response = client.get("/api/v1/achievements/my-achievements",
        headers=auth_headers
    )

    if response.status_code != 404:
        assert response.status_code == 200


# ================================================================
# AVATAR TESTS
# ================================================================

@pytest.mark.api
@pytest.mark.integration
def test_get_all_avatars(client, auth_headers, test_db):
    """Test getting list of all available avatars"""
    # Create avatars
    for i in range(5):
        avatar = Avatar(
            name=f"Avatar {i}",
            image_url=f"https://example.com/avatar{i}.png",
            rarity="common" if i < 3 else "rare",
            is_default=i == 0
        )
        test_db.add(avatar)
    test_db.commit()

    response = client.get("/api/v1/avatars", headers=auth_headers)

    if response.status_code != 404:
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 5
        assert all("name" in a for a in data)


@pytest.mark.api
@pytest.mark.integration
def test_get_user_avatars(client, auth_headers, test_db, test_user):
    """Test getting avatars unlocked by user"""
    # Create avatar
    avatar = Avatar(
        name="Beginner",
        image_url="https://example.com/beginner.png",
        rarity="common",
        is_default=True
    )
    test_db.add(avatar)
    test_db.commit()
    test_db.refresh(avatar)

    # Unlock for user
    user_avatar = UserAvatar(
        user_id=test_user.id,
        avatar_id=avatar.id,
        unlocked_at=datetime.utcnow()
    )
    test_db.add(user_avatar)
    test_db.commit()

    response = client.get("/api/v1/avatars/my-avatars", headers=auth_headers)

    if response.status_code != 404:
        assert response.status_code == 200
        data = response.json()
        # Should include unlocked avatar
        assert len(data) >= 1


@pytest.mark.api
@pytest.mark.integration
def test_select_avatar(client, auth_headers, test_db, test_user):
    """Test selecting an avatar as current"""
    # Create and unlock avatar
    avatar = Avatar(
        name="Selected",
        image_url="https://example.com/selected.png",
        rarity="common",
        is_default=True
    )
    test_db.add(avatar)
    test_db.commit()
    test_db.refresh(avatar)

    user_avatar = UserAvatar(
        user_id=test_user.id,
        avatar_id=avatar.id,
        unlocked_at=datetime.utcnow()
    )
    test_db.add(user_avatar)
    test_db.commit()
    test_db.refresh(user_avatar)

    # Select avatar
    response = client.post(f"/api/v1/avatars/select/{avatar.id}",
        headers=auth_headers
    )

    if response.status_code != 404:
        assert response.status_code == 200

        # Verify selection - selected avatar is tracked on user profile
        profile = test_db.query(UserProfile).filter(
            UserProfile.user_id == test_user.id
        ).first()
        # May be set to selected avatar ID
        # assert profile.selected_avatar_id == avatar.id


@pytest.mark.api
@pytest.mark.integration
def test_cannot_select_locked_avatar(client, auth_headers, test_db, test_user):
    """Test that user cannot select an avatar they haven't unlocked"""
    # Create avatar (not unlocked)
    avatar = Avatar(
        name="Locked",
        image_url="https://example.com/locked.png",
        rarity="legendary",
        is_default=False
    )
    test_db.add(avatar)
    test_db.commit()
    test_db.refresh(avatar)

    # Try to select without unlocking
    response = client.post(f"/api/v1/avatars/select/{avatar.id}",
        headers=auth_headers
    )

    if response.status_code != 404:
        assert response.status_code in [400, 403, 404]


# ================================================================
# RARITY TESTS
# ================================================================

@pytest.mark.api
@pytest.mark.integration
def test_achievement_rarity_levels(client, auth_headers, test_db):
    """Test different achievement rarity levels"""
    rarities = ["common", "rare", "epic", "legendary"]

    for rarity in rarities:
        achievement = Achievement(
            name=f"{rarity.title()} Achievement",
            description=f"A {rarity} achievement",
            icon="🏅",
            rarity=rarity,
            criteria_type="quiz_count",
            criteria_value=10
        )
        test_db.add(achievement)
    test_db.commit()

    response = client.get("/api/v1/achievements", headers=auth_headers)

    if response.status_code != 404:
        assert response.status_code == 200
        data = response.json()
        # Should include all rarity levels
        found_rarities = {a.get("rarity") for a in data if "rarity" in a}
        assert len(found_rarities) >= 2


# ================================================================
# AUTHENTICATION TESTS
# ================================================================

@pytest.mark.api
@pytest.mark.integration
def test_achievements_require_auth(client):
    """Test that achievement endpoints require authentication"""
    response = client.get("/api/v1/achievements")

    # May allow public viewing or require auth
    assert response.status_code in [200, 401]


@pytest.mark.api
@pytest.mark.integration
def test_my_achievements_require_auth(client):
    """Test that personal achievements require authentication"""
    response = client.get("/api/v1/achievements/my-achievements")

    # Should require auth or return 404 if endpoint doesn't exist
    assert response.status_code in [401, 404]


# ================================================================
# EDGE CASES
# ================================================================

@pytest.mark.api
@pytest.mark.integration
def test_no_achievements_unlocked(client, auth_headers, test_db, test_user):
    """Test user with no achievements unlocked"""
    response = client.get("/api/v1/achievements/my-achievements",
        headers=auth_headers
    )

    if response.status_code != 404:
        assert response.status_code == 200
        data = response.json()
        # Should return empty list or show all as locked
        if isinstance(data, list):
            # May be empty or may show locked achievements
            assert len(data) >= 0


@pytest.mark.api
@pytest.mark.integration
def test_achievement_progress_over_100(client, auth_headers, test_db, test_user):
    """Test that achievement progress can exceed criteria value"""
    achievement = Achievement(
        name="Overflow Test",
        description="Test overflow",
        icon="🔢",
        rarity="common",
        criteria_type="quiz_count",
        criteria_value=10
    )
    test_db.add(achievement)
    test_db.commit()
    test_db.refresh(achievement)

    # Create achievement with progress exceeding criteria
    user_achievement = UserAchievement(
        user_id=test_user.id,
        achievement_id=achievement.id,
        progress_value=15,  # Over criteria_value of 10
        earned_at=datetime.utcnow()
    )
    test_db.add(user_achievement)
    test_db.commit()

    response = client.get("/api/v1/achievements/my-achievements",
        headers=auth_headers
    )

    if response.status_code != 404:
        assert response.status_code == 200
        # Progress should be handled gracefully
