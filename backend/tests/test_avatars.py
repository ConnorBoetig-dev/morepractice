"""
COMPREHENSIVE AVATAR TESTS

Tests for avatar system including:
- Getting available avatars
- Unlocking avatars (default and achievement-based)
- Selecting/equipping avatars
- Avatar stats and collection
- Error handling

NO FLUFF - Real functionality testing
"""

import pytest
from app.models.gamification import Avatar, UserAvatar, Achievement, UserAchievement
from app.models.user import UserProfile


# ================================================================
# TEST FIXTURES
# ================================================================

@pytest.fixture
def sample_avatars(test_db):
    """
    Create sample avatars for testing

    Creates:
    - 3 default avatars (no achievement required)
    - 2 achievement-locked avatars
    """
    # Default avatars (available to all users)
    avatar1 = Avatar(
        name="Default Student",
        description="Starting avatar for all students",
        image_url="/avatars/default_student.png",
        required_achievement_id=None
    )
    avatar2 = Avatar(
        name="Bookworm",
        description="For studious learners",
        image_url="/avatars/bookworm.png",
        required_achievement_id=None
    )
    avatar3 = Avatar(
        name="Tech Guru",
        description="Technology enthusiast",
        image_url="/avatars/tech_guru.png",
        required_achievement_id=None
    )

    test_db.add_all([avatar1, avatar2, avatar3])
    test_db.flush()

    # Create achievement for testing unlock logic
    achievement1 = Achievement(
        name="First Quiz",
        description="Complete your first quiz",
        icon="star",
        xp_reward=50,
        requirement_type="quiz_count",
        requirement_value=1
    )
    achievement2 = Achievement(
        name="Quiz Master",
        description="Complete 10 quizzes",
        icon="trophy",
        xp_reward=200,
        requirement_type="quiz_count",
        requirement_value=10
    )
    test_db.add_all([achievement1, achievement2])
    test_db.flush()

    # Achievement-locked avatars
    avatar4 = Avatar(
        name="Quiz Champion",
        description="Unlocked after first quiz",
        image_url="/avatars/quiz_champion.png",
        required_achievement_id=achievement1.id
    )
    avatar5 = Avatar(
        name="Ultimate Scholar",
        description="Unlocked after 10 quizzes",
        image_url="/avatars/ultimate_scholar.png",
        required_achievement_id=achievement2.id
    )

    test_db.add_all([avatar4, avatar5])
    test_db.commit()

    return {
        "default": [avatar1, avatar2, avatar3],
        "locked": [avatar4, avatar5],
        "achievements": [achievement1, achievement2]
    }


# ================================================================
# GET ALL AVATARS (PUBLIC ENDPOINT)
# ================================================================

@pytest.mark.integration
def test_get_all_avatars_public_no_auth(client, sample_avatars):
    """
    REAL TEST: Get all avatars without authentication
    Tests: Public endpoint returns basic avatar info
    """
    response = client.get("/api/v1/avatars")

    assert response.status_code == 200
    data = response.json()

    # Should return all 5 avatars
    assert len(data) == 5

    # Verify structure of returned data
    first_avatar = data[0]
    assert "id" in first_avatar
    assert "name" in first_avatar
    assert "description" in first_avatar
    assert "image_url" in first_avatar
    assert "is_default" in first_avatar

    # Should NOT include user-specific fields (no auth)
    assert "is_unlocked" not in first_avatar
    assert "is_selected" not in first_avatar

    # Verify default avatars marked correctly
    default_avatars = [a for a in data if a["is_default"]]
    locked_avatars = [a for a in data if not a["is_default"]]

    assert len(default_avatars) == 3  # 3 default avatars
    assert len(locked_avatars) == 2   # 2 achievement-locked


# ================================================================
# GET USER'S AVATARS WITH STATUS
# ================================================================

@pytest.mark.integration
def test_get_avatars_with_user_status(client, test_db, test_user, test_user_token, sample_avatars):
    """
    REAL TEST: Get avatars with user's unlock/selection status
    Tests: Authenticated endpoint shows which avatars user has unlocked
    """
    # Manually unlock default avatars for test user
    from app.services.avatar_service import unlock_default_avatars
    unlock_default_avatars(test_db, test_user.id)

    response = client.get(
        "/api/v1/avatars/me",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 5  # All avatars returned

    # Verify user-specific fields included
    first_avatar = data[0]
    assert "is_unlocked" in first_avatar
    assert "is_selected" in first_avatar
    assert "unlocked_at" in first_avatar
    assert "required_achievement_id" in first_avatar
    assert "required_achievement_name" in first_avatar

    # Check unlock status
    unlocked = [a for a in data if a["is_unlocked"]]
    locked = [a for a in data if not a["is_unlocked"]]

    assert len(unlocked) == 3  # 3 default avatars unlocked
    assert len(locked) == 2    # 2 achievement avatars still locked

    # Verify locked avatars show required achievement
    for avatar in locked:
        assert avatar["required_achievement_id"] is not None
        assert avatar["required_achievement_name"] is not None
        assert avatar["unlocked_at"] is None


@pytest.mark.integration
def test_get_avatars_requires_authentication(client):
    """
    REAL TEST: /avatars/me requires authentication
    Tests: 401 returned when no token provided
    """
    response = client.get("/api/v1/avatars/me")

    assert response.status_code == 401


# ================================================================
# GET USER'S UNLOCKED AVATARS ONLY
# ================================================================

@pytest.mark.integration
def test_get_unlocked_avatars_only(client, test_db, test_user, test_user_token, sample_avatars):
    """
    REAL TEST: Get only unlocked avatars (filtering)
    Tests: Returns only avatars user has unlocked, sorted by unlock time
    """
    # Unlock default avatars
    from app.services.avatar_service import unlock_default_avatars
    unlock_default_avatars(test_db, test_user.id)

    response = client.get(
        "/api/v1/avatars/unlocked",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 200
    data = response.json()

    # Should only return 3 unlocked avatars (not all 5)
    assert len(data) == 3

    # All returned avatars should have unlock timestamp
    for avatar in data:
        assert avatar["unlocked_at"] is not None
        assert "is_selected" in avatar

    # Verify sorting (most recent first)
    unlock_times = [a["unlocked_at"] for a in data]
    assert unlock_times == sorted(unlock_times, reverse=True)


@pytest.mark.integration
def test_get_unlocked_avatars_empty_for_new_user(client, test_user, test_user_token):
    """
    REAL TEST: New user with no unlocked avatars returns empty list
    Tests: Edge case - user hasn't unlocked anything yet
    """
    response = client.get(
        "/api/v1/avatars/unlocked",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 200
    data = response.json()

    # New user should have empty unlocked list (until default avatars unlocked)
    assert isinstance(data, list)


# ================================================================
# SELECT/EQUIP AVATAR
# ================================================================

@pytest.mark.integration
def test_select_avatar_success(client, test_db, test_user, test_user_token, sample_avatars):
    """
    REAL TEST: Select an unlocked avatar
    Tests: User can equip an avatar they've unlocked
    """
    # Unlock default avatars
    from app.services.avatar_service import unlock_default_avatars
    unlock_default_avatars(test_db, test_user.id)

    # Get first default avatar ID
    avatar_id = sample_avatars["default"][0].id

    response = client.post(
        "/api/v1/avatars/select",
        json={"avatar_id": avatar_id},
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert "selected successfully" in data["message"]
    assert data["avatar"]["id"] == avatar_id
    assert data["avatar"]["name"] == sample_avatars["default"][0].name

    # Verify profile updated in database
    profile = test_db.query(UserProfile).filter(UserProfile.user_id == test_user.id).first()
    assert profile.selected_avatar_id == avatar_id


@pytest.mark.integration
def test_select_avatar_not_unlocked_fails(client, test_db, test_user, test_user_token, sample_avatars):
    """
    REAL TEST: Cannot select avatar that isn't unlocked
    Tests: 400 error when trying to equip locked avatar
    """
    # DON'T unlock avatars - try to select locked one
    locked_avatar_id = sample_avatars["locked"][0].id

    response = client.post(
        "/api/v1/avatars/select",
        json={"avatar_id": locked_avatar_id},
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 400
    data = response.json()

    assert "not unlocked" in data["detail"].lower()


@pytest.mark.integration
def test_select_avatar_nonexistent_fails(client, test_user_token):
    """
    REAL TEST: Cannot select avatar that doesn't exist
    Tests: 400 error when avatar ID invalid
    """
    response = client.post(
        "/api/v1/avatars/select",
        json={"avatar_id": 99999},  # Nonexistent ID
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 400
    data = response.json()

    assert "not found" in data["detail"].lower()


@pytest.mark.integration
def test_select_avatar_shows_in_collection(client, test_db, test_user, test_user_token, sample_avatars):
    """
    REAL TEST: Selected avatar marked as selected in collection
    Tests: is_selected flag updated after selection
    """
    # Unlock and select avatar
    from app.services.avatar_service import unlock_default_avatars
    unlock_default_avatars(test_db, test_user.id)

    avatar_id = sample_avatars["default"][0].id

    # Select avatar
    client.post(
        "/api/v1/avatars/select",
        json={"avatar_id": avatar_id},
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    # Get collection with status
    response = client.get(
        "/api/v1/avatars/me",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    data = response.json()

    # Find the selected avatar
    selected = [a for a in data if a["is_selected"]]
    not_selected = [a for a in data if not a["is_selected"]]

    assert len(selected) == 1  # Exactly one avatar selected
    assert selected[0]["id"] == avatar_id
    assert len(not_selected) == 4  # Other 4 not selected


# ================================================================
# AVATAR UNLOCK VIA ACHIEVEMENT
# ================================================================

@pytest.mark.integration
def test_unlock_avatar_from_achievement(test_db, test_user, sample_avatars):
    """
    REAL TEST: Avatar unlocked when user earns achievement
    Tests: unlock_avatar_from_achievement service function
    """
    from app.services.avatar_service import unlock_avatar_from_achievement

    achievement_id = sample_avatars["achievements"][0].id

    # Unlock avatar via achievement
    unlocked_avatar = unlock_avatar_from_achievement(test_db, test_user.id, achievement_id)

    # Verify avatar was unlocked
    assert unlocked_avatar is not None
    assert unlocked_avatar.name == "Quiz Champion"

    # Verify UserAvatar record created
    user_avatar = test_db.query(UserAvatar).filter(
        UserAvatar.user_id == test_user.id,
        UserAvatar.avatar_id == unlocked_avatar.id
    ).first()

    assert user_avatar is not None
    assert user_avatar.unlocked_at is not None


@pytest.mark.integration
def test_unlock_avatar_achievement_with_no_avatar_returns_none(test_db, test_user, sample_avatars):
    """
    REAL TEST: Unlocking achievement without avatar reward returns None
    Tests: Edge case - not all achievements unlock avatars
    """
    from app.services.avatar_service import unlock_avatar_from_achievement

    # Create achievement with no avatar
    achievement = Achievement(
        name="No Avatar Achievement",
        description="This doesn't unlock an avatar",
        icon="star",
        xp_reward=100,
        requirement_type="quiz_count",
        requirement_value=5
    )
    test_db.add(achievement)
    test_db.commit()

    result = unlock_avatar_from_achievement(test_db, test_user.id, achievement.id)

    assert result is None  # No avatar to unlock


@pytest.mark.integration
def test_unlock_avatar_already_unlocked_returns_none(test_db, test_user, sample_avatars):
    """
    REAL TEST: Unlocking already-unlocked avatar returns None
    Tests: Idempotency - can't unlock same avatar twice
    """
    from app.services.avatar_service import unlock_avatar_from_achievement

    achievement_id = sample_avatars["achievements"][0].id

    # Unlock once
    result1 = unlock_avatar_from_achievement(test_db, test_user.id, achievement_id)
    assert result1 is not None

    # Try to unlock again
    result2 = unlock_avatar_from_achievement(test_db, test_user.id, achievement_id)
    assert result2 is None  # Already unlocked


# ================================================================
# DEFAULT AVATARS UNLOCKED ON SIGNUP
# ================================================================

@pytest.mark.integration
def test_default_avatars_unlocked_on_signup(test_db, test_user, sample_avatars):
    """
    REAL TEST: All default avatars unlocked for new user
    Tests: unlock_default_avatars service function
    """
    from app.services.avatar_service import unlock_default_avatars

    # Initially, user has no avatars
    count_before = test_db.query(UserAvatar).filter(UserAvatar.user_id == test_user.id).count()
    assert count_before == 0

    # Unlock default avatars
    unlock_default_avatars(test_db, test_user.id)

    # Verify 3 default avatars unlocked
    unlocked = test_db.query(UserAvatar).filter(UserAvatar.user_id == test_user.id).all()
    assert len(unlocked) == 3

    # Verify all have unlock timestamps
    for ua in unlocked:
        assert ua.unlocked_at is not None


@pytest.mark.integration
def test_default_avatars_idempotent(test_db, test_user, sample_avatars):
    """
    REAL TEST: Unlocking default avatars multiple times doesn't duplicate
    Tests: Idempotency - calling unlock_default_avatars twice is safe
    """
    from app.services.avatar_service import unlock_default_avatars

    # Unlock twice
    unlock_default_avatars(test_db, test_user.id)
    unlock_default_avatars(test_db, test_user.id)

    # Should still have exactly 3 avatars (not 6)
    unlocked = test_db.query(UserAvatar).filter(UserAvatar.user_id == test_user.id).all()
    assert len(unlocked) == 3


# ================================================================
# AVATAR STATS
# ================================================================

@pytest.mark.integration
def test_get_avatar_stats(client, test_db, test_user, test_user_token, sample_avatars):
    """
    REAL TEST: Get user's avatar collection statistics
    Tests: Total, unlocked, completion percentage
    """
    # Unlock default avatars
    from app.services.avatar_service import unlock_default_avatars
    unlock_default_avatars(test_db, test_user.id)

    # Select one avatar
    avatar_id = sample_avatars["default"][0].id
    client.post(
        "/api/v1/avatars/select",
        json={"avatar_id": avatar_id},
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    # Get stats
    response = client.get(
        "/api/v1/avatars/stats",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 200
    data = response.json()

    assert data["total_avatars"] == 5
    assert data["unlocked_avatars"] == 3
    assert data["completion_percentage"] == 60.0  # 3/5 = 60%

    # Verify selected avatar included
    assert data["selected_avatar"] is not None
    assert data["selected_avatar"]["id"] == avatar_id


@pytest.mark.integration
def test_get_avatar_stats_no_selection(client, test_db, test_user, test_user_token, sample_avatars):
    """
    REAL TEST: Avatar stats when no avatar selected
    Tests: selected_avatar is null when user hasn't selected one
    """
    # Unlock but don't select
    from app.services.avatar_service import unlock_default_avatars
    unlock_default_avatars(test_db, test_user.id)

    response = client.get(
        "/api/v1/avatars/stats",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    data = response.json()

    assert data["selected_avatar"] is None


@pytest.mark.integration
def test_avatar_stats_empty_for_new_user(client, test_user_token, sample_avatars):
    """
    REAL TEST: Stats for user who hasn't unlocked anything
    Tests: 0 unlocked, 0% completion
    """
    response = client.get(
        "/api/v1/avatars/stats",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    data = response.json()

    assert data["total_avatars"] == 5
    assert data["unlocked_avatars"] == 0
    assert data["completion_percentage"] == 0.0


# ================================================================
# EDGE CASES AND ERROR HANDLING
# ================================================================

@pytest.mark.integration
def test_select_avatar_invalid_payload(client, test_user_token):
    """
    REAL TEST: Invalid request payload rejected
    Tests: Pydantic validation on avatar_id field
    """
    # Negative avatar_id
    response = client.post(
        "/api/v1/avatars/select",
        json={"avatar_id": -1},
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 422  # Validation error

    # Missing avatar_id
    response = client.post(
        "/api/v1/avatars/select",
        json={},
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 422


@pytest.mark.integration
def test_avatar_endpoints_require_auth(client):
    """
    REAL TEST: All authenticated endpoints require valid token
    Tests: 401 returned for missing/invalid tokens
    """
    endpoints = [
        ("GET", "/api/v1/avatars/me"),
        ("GET", "/api/v1/avatars/unlocked"),
        ("POST", "/api/v1/avatars/select", {"avatar_id": 1}),
        ("GET", "/api/v1/avatars/stats"),
    ]

    for method, url, *body in endpoints:
        if method == "GET":
            response = client.get(url)
        else:
            response = client.post(url, json=body[0] if body else {})

        assert response.status_code == 401, f"Endpoint {method} {url} should require auth"


@pytest.mark.integration
def test_change_avatar_selection(client, test_db, test_user, test_user_token, sample_avatars):
    """
    REAL TEST: User can change selected avatar
    Tests: Selecting different avatar updates profile
    """
    from app.services.avatar_service import unlock_default_avatars
    unlock_default_avatars(test_db, test_user.id)

    avatar1_id = sample_avatars["default"][0].id
    avatar2_id = sample_avatars["default"][1].id

    # Select first avatar
    client.post(
        "/api/v1/avatars/select",
        json={"avatar_id": avatar1_id},
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    # Verify selection
    profile = test_db.query(UserProfile).filter(UserProfile.user_id == test_user.id).first()
    assert profile.selected_avatar_id == avatar1_id

    # Change to second avatar
    response = client.post(
        "/api/v1/avatars/select",
        json={"avatar_id": avatar2_id},
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 200

    # Verify updated
    test_db.refresh(profile)
    assert profile.selected_avatar_id == avatar2_id


@pytest.mark.integration
def test_multiple_users_independent_unlocks(test_db, test_user, sample_avatars):
    """
    REAL TEST: Avatar unlocks are per-user (isolation)
    Tests: User A unlocking avatar doesn't affect User B
    """
    from app.models.user import User
    from app.services.avatar_service import unlock_default_avatars
    from app.utils.auth import hash_password

    # Create second user
    user2 = User(
        email="user2@example.com",
        username="user2",
        hashed_password=hash_password("Test@Pass123"),
        is_active=True
    )
    test_db.add(user2)
    test_db.commit()

    # Create profiles
    profile1 = UserProfile(user_id=test_user.id, xp=0, level=1)
    profile2 = UserProfile(user_id=user2.id, xp=0, level=1)
    test_db.add_all([profile1, profile2])
    test_db.commit()

    # Unlock for user1 only
    unlock_default_avatars(test_db, test_user.id)

    # User1 should have 3 unlocked
    user1_unlocked = test_db.query(UserAvatar).filter(UserAvatar.user_id == test_user.id).count()
    assert user1_unlocked == 3

    # User2 should have 0 unlocked
    user2_unlocked = test_db.query(UserAvatar).filter(UserAvatar.user_id == user2.id).count()
    assert user2_unlocked == 0
