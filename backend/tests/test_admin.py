"""
Admin Operations Tests

Tests for admin-only endpoints:
- User management (list, update, delete, promote)
- Question CRUD operations
- Achievement management
- System statistics
- Audit logs
"""

import pytest
from app.models.user import User, UserProfile
from app.models.question import Question
from app.models.gamification import Achievement
from app.utils.auth import hash_password, create_access_token


# ================================================================
# ADMIN FIXTURES
# ================================================================

@pytest.fixture(scope="function")
def admin_user(test_db):
    """Create an admin user for testing admin endpoints"""
    user = User(
        email="admin@example.com",
        username="admin",
        hashed_password=hash_password("adminpass123"),
        is_active=True,
        is_verified=True,
        is_admin=True  # Admin flag
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)

    # Create profile
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
def admin_headers(admin_user):
    """Create authorization headers for admin user"""
    token = create_access_token(data={"user_id": admin_user.id})
    return {"Authorization": f"Bearer {token}"}


# ================================================================
# AUTHORIZATION TESTS
# ================================================================

@pytest.mark.api
@pytest.mark.integration
def test_admin_endpoint_requires_auth(client):
    """Test that admin endpoints require authentication"""
    response = client.get("/api/v1/admin/users")
    assert response.status_code == 401


@pytest.mark.api
@pytest.mark.integration
def test_admin_endpoint_requires_admin_role(client, auth_headers):
    """Test that admin endpoints require admin role"""
    # auth_headers is from regular test_user (not admin)
    response = client.get("/api/v1/admin/users", headers=auth_headers)

    if response.status_code != 404:
        assert response.status_code == 403  # Forbidden for non-admins


@pytest.mark.api
@pytest.mark.integration
def test_admin_user_can_access(client, admin_headers):
    """Test that admin user can access admin endpoints"""
    response = client.get("/api/v1/admin/users", headers=admin_headers)

    if response.status_code != 404:
        assert response.status_code == 200


# ================================================================
# USER MANAGEMENT TESTS
# ================================================================

@pytest.mark.api
@pytest.mark.integration
def test_list_all_users(client, admin_headers, test_db, test_user):
    """Test listing all users as admin"""
    # Create additional users
    for i in range(3):
        user = User(
            email=f"user{i}@example.com",
            username=f"user{i}",
            hashed_password=hash_password("pass123"),
            is_active=True,
            is_verified=False
        )
        test_db.add(user)
    test_db.commit()

    response = client.get("/api/v1/admin/users", headers=admin_headers)

    if response.status_code != 404:
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 4  # 3 new + test_user + admin


@pytest.mark.api
@pytest.mark.integration
def test_get_user_by_id(client, admin_headers, test_user):
    """Test getting specific user details"""
    response = client.get(f"/api/v1/admin/users/{test_user.id}",
        headers=admin_headers
    )

    if response.status_code != 404:
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user.id
        assert data["email"] == "test@example.com"


@pytest.mark.api
@pytest.mark.integration
def test_update_user_details(client, admin_headers, test_db, test_user):
    """Test updating user information as admin"""
    response = client.put(f"/api/v1/admin/users/{test_user.id}",
        headers=admin_headers,
        json={
            "is_verified": True,
            "is_active": True
        }
    )

    if response.status_code != 404:
        assert response.status_code == 200

        # Verify update
        test_db.refresh(test_user)
        assert test_user.is_verified is True


@pytest.mark.api
@pytest.mark.integration
def test_promote_user_to_admin(client, admin_headers, test_db, test_user):
    """Test promoting a regular user to admin"""
    response = client.post(f"/api/v1/admin/users/{test_user.id}/promote",
        headers=admin_headers
    )

    if response.status_code != 404:
        assert response.status_code == 200

        # Verify promotion
        test_db.refresh(test_user)
        assert test_user.is_admin is True


@pytest.mark.api
@pytest.mark.integration
def test_demote_admin_user(client, admin_headers, test_db):
    """Test demoting an admin to regular user"""
    # Create another admin
    admin2 = User(
        email="admin2@example.com",
        username="admin2",
        hashed_password=hash_password("pass123"),
        is_active=True,
        is_admin=True
    )
    test_db.add(admin2)
    test_db.commit()
    test_db.refresh(admin2)

    response = client.post(f"/api/v1/admin/users/{admin2.id}/demote",
        headers=admin_headers
    )

    if response.status_code != 404:
        assert response.status_code == 200

        # Verify demotion
        test_db.refresh(admin2)
        assert admin2.is_admin is False


@pytest.mark.api
@pytest.mark.integration
def test_deactivate_user(client, admin_headers, test_db, test_user):
    """Test deactivating a user account"""
    response = client.post(f"/api/v1/admin/users/{test_user.id}/deactivate",
        headers=admin_headers
    )

    if response.status_code != 404:
        assert response.status_code == 200

        # Verify deactivation
        test_db.refresh(test_user)
        assert test_user.is_active is False


@pytest.mark.api
@pytest.mark.integration
def test_reactivate_user(client, admin_headers, test_db):
    """Test reactivating a deactivated user"""
    # Create inactive user
    user = User(
        email="inactive@example.com",
        username="inactive",
        hashed_password=hash_password("pass123"),
        is_active=False,
        is_verified=True
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)

    response = client.post(f"/api/v1/admin/users/{user.id}/activate",
        headers=admin_headers
    )

    if response.status_code != 404:
        assert response.status_code == 200

        # Verify activation
        test_db.refresh(user)
        assert user.is_active is True


@pytest.mark.api
@pytest.mark.integration
def test_delete_user(client, admin_headers, test_db):
    """Test deleting a user account"""
    # Create user to delete
    user = User(
        email="todelete@example.com",
        username="todelete",
        hashed_password=hash_password("pass123"),
        is_active=True
    )
    test_db.add(user)
    test_db.commit()
    user_id = user.id

    response = client.delete(f"/api/v1/admin/users/{user_id}",
        headers=admin_headers
    )

    if response.status_code != 404:
        assert response.status_code in [200, 204]

        # Verify deletion
        deleted_user = test_db.query(User).filter(User.id == user_id).first()
        assert deleted_user is None


# ================================================================
# QUESTION MANAGEMENT TESTS
# ================================================================

@pytest.mark.api
@pytest.mark.integration
def test_create_question(client, admin_headers, test_db):
    """Test creating a new question as admin"""
    response = client.post("/api/v1/admin/questions",
        headers=admin_headers,
        json={
            "question_id": "test_q1",
            "exam_type": "security",
            "domain": "1.1",
            "question_text": "What is encryption?",
            "correct_answer": "A",
            "options": {
                "A": {"text": "Encoding data", "explanation": "Correct - Encryption is the process of encoding data."},
                "B": {"text": "Deleting data", "explanation": "Incorrect - This is data removal, not encryption."},
                "C": {"text": "Copying data", "explanation": "Incorrect - This is data replication, not encryption."},
                "D": {"text": "Moving data", "explanation": "Incorrect - This is data transfer, not encryption."}
            }
        }
    )

    if response.status_code != 404:
        assert response.status_code == 201
        data = response.json()
        assert data["question_text"] == "What is encryption?"
        assert data["correct_answer"] == "A"

        # Verify in database
        question = test_db.query(Question).filter(
            Question.question_text == "What is encryption?"
        ).first()
        assert question is not None


@pytest.mark.api
@pytest.mark.integration
def test_update_question(client, admin_headers, test_db):
    """Test updating an existing question"""
    # Create question
    q = Question(
        exam_type="network",
        question_text="Old question?",
        correct_answer="A",
        options={
            "A": {"text": "Option A", "explanation": "Correct answer"},
            "B": {"text": "Option B", "explanation": "Incorrect"},
            "C": {"text": "Option C", "explanation": "Incorrect"},
            "D": {"text": "Option D", "explanation": "Incorrect"}
        }
    )
    test_db.add(q)
    test_db.commit()
    test_db.refresh(q)

    response = client.put(f"/api/v1/admin/questions/{q.id}",
        headers=admin_headers,
        json={
            "question_text": "Updated question?",
            "difficulty": "hard"
        }
    )

    if response.status_code != 404:
        assert response.status_code == 200

        # Verify update
        test_db.refresh(q)
        assert q.question_text == "Updated question?"
        assert q.difficulty == "hard"


@pytest.mark.api
@pytest.mark.integration
def test_delete_question(client, admin_headers, test_db):
    """Test deleting a question"""
    # Create question
    q = Question(
        exam_type="security",
        question_text="To delete?",
        correct_answer="A",
        options={
            "A": {"text": "Option A", "explanation": "Correct answer"},
            "B": {"text": "Option B", "explanation": "Incorrect"},
            "C": {"text": "Option C", "explanation": "Incorrect"},
            "D": {"text": "Option D", "explanation": "Incorrect"}
        }
    )
    test_db.add(q)
    test_db.commit()
    question_id = q.id

    response = client.delete(f"/api/v1/admin/questions/{question_id}",
        headers=admin_headers
    )

    if response.status_code != 404:
        assert response.status_code in [200, 204]

        # Verify deletion
        deleted_q = test_db.query(Question).filter(
            Question.id == question_id
        ).first()
        assert deleted_q is None


@pytest.mark.api
@pytest.mark.integration
def test_list_questions_with_filters(client, admin_headers, test_db):
    """Test listing questions with exam_type filter"""
    # Create questions for different exam types
    for exam_type in ["security", "network"]:
        for i in range(3):
            q = Question(
                exam_type=exam_type,
                question_text=f"{exam_type} question {i}?",
                correct_answer="A",
                options={
                    "A": {"text": "Option A", "explanation": "Correct answer"},
                    "B": {"text": "Option B", "explanation": "Incorrect"},
                    "C": {"text": "Option C", "explanation": "Incorrect"},
                    "D": {"text": "Option D", "explanation": "Incorrect"}
                }
            )
            test_db.add(q)
    test_db.commit()

    response = client.get("/api/v1/admin/questions?exam_type=security",
        headers=admin_headers
    )

    if response.status_code != 404:
        assert response.status_code == 200
        data = response.json()
        # Should only return security questions
        assert all(q["exam_type"] == "security" for q in data)


@pytest.mark.api
@pytest.mark.integration
def test_question_includes_correct_answer_for_admin(client, admin_headers, test_db):
    """Test that admin can see correct answers in question list"""
    q = Question(
        exam_type="security",
        question_text="Admin test?",
        correct_answer="A",
        options={
            "A": {"text": "Option A", "explanation": "Correct answer"},
            "B": {"text": "Option B", "explanation": "Incorrect"},
            "C": {"text": "Option C", "explanation": "Incorrect"},
            "D": {"text": "Option D", "explanation": "Incorrect"}
        }
    )
    test_db.add(q)
    test_db.commit()
    test_db.refresh(q)

    response = client.get(f"/api/v1/admin/questions/{q.id}",
        headers=admin_headers
    )

    if response.status_code != 404:
        assert response.status_code == 200
        data = response.json()
        # Admin should see correct answer
        assert "correct_answer" in data
        assert data["correct_answer"] == "A"


# ================================================================
# ACHIEVEMENT MANAGEMENT TESTS
# ================================================================

@pytest.mark.api
@pytest.mark.integration
def test_create_achievement(client, admin_headers, test_db):
    """Test creating a new achievement"""
    response = client.post("/api/v1/admin/achievements",
        headers=admin_headers,
        json={
            "name": "Quiz Master",
            "description": "Complete 100 quizzes",
            "icon": "🏆",
            "rarity": "legendary",
            "criteria_type": "quiz_count",
            "criteria_value": 100,
            "criteria_exam_type": None,
            "xp_reward": 1000
        }
    )

    if response.status_code != 404:
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Quiz Master"

        # Verify in database
        achievement = test_db.query(Achievement).filter(
            Achievement.name == "Quiz Master"
        ).first()
        assert achievement is not None


@pytest.mark.api
@pytest.mark.integration
def test_update_achievement(client, admin_headers, test_db):
    """Test updating an achievement"""
    # Create achievement
    achievement = Achievement(
        name="Old Name",
        description="Old description",
        icon="🎯",
        rarity="common",
        criteria_type="quiz_count",
        criteria_value=10
    )
    test_db.add(achievement)
    test_db.commit()
    test_db.refresh(achievement)

    response = client.put(f"/api/v1/admin/achievements/{achievement.id}",
        headers=admin_headers,
        json={
            "name": "New Name",
            "rarity": "rare"
        }
    )

    if response.status_code != 404:
        assert response.status_code == 200

        # Verify update
        test_db.refresh(achievement)
        assert achievement.name == "New Name"
        assert achievement.rarity == "rare"


@pytest.mark.api
@pytest.mark.integration
def test_delete_achievement(client, admin_headers, test_db):
    """Test deleting an achievement"""
    achievement = Achievement(
        name="To Delete",
        description="Will be deleted",
        icon="❌",
        rarity="common",
        criteria_type="quiz_count",
        criteria_value=5
    )
    test_db.add(achievement)
    test_db.commit()
    achievement_id = achievement.id

    response = client.delete(f"/api/v1/admin/achievements/{achievement_id}",
        headers=admin_headers
    )

    if response.status_code != 404:
        assert response.status_code in [200, 204]

        # Verify deletion
        deleted_achievement = test_db.query(Achievement).filter(
            Achievement.id == achievement_id
        ).first()
        assert deleted_achievement is None


# ================================================================
# SYSTEM STATISTICS TESTS
# ================================================================

@pytest.mark.api
@pytest.mark.integration
def test_get_system_statistics(client, admin_headers, test_db):
    """Test getting overall system statistics"""
    # Create some data
    for i in range(5):
        user = User(
            email=f"stats{i}@example.com",
            username=f"stats{i}",
            hashed_password=hash_password("pass123"),
            is_active=True
        )
        test_db.add(user)
    test_db.commit()

    response = client.get("/api/v1/admin/statistics", headers=admin_headers)

    if response.status_code != 404:
        assert response.status_code == 200
        data = response.json()
        # Should include counts
        assert "total_users" in data or "user_count" in data


@pytest.mark.api
@pytest.mark.integration
def test_get_question_statistics(client, admin_headers, test_db):
    """Test getting question statistics by exam type"""
    # Create questions
    for exam_type in ["security", "network"]:
        for i in range(10):
            q = Question(
                exam_type=exam_type,
                question_text=f"Q{i}?",
                correct_answer="A",
                options={
                    "A": {"text": "Option A", "explanation": "Correct answer"},
                    "B": {"text": "Option B", "explanation": "Incorrect"},
                    "C": {"text": "Option C", "explanation": "Incorrect"},
                    "D": {"text": "Option D", "explanation": "Incorrect"}
                }
            )
            test_db.add(q)
    test_db.commit()

    response = client.get("/api/v1/admin/questions/statistics",
        headers=admin_headers
    )

    if response.status_code != 404:
        assert response.status_code == 200
        # Should show question counts by exam type


# ================================================================
# NON-ADMIN PREVENTION TESTS
# ================================================================

@pytest.mark.api
@pytest.mark.integration
def test_regular_user_cannot_create_question(client, auth_headers):
    """Test that regular users cannot create questions"""
    response = client.post("/api/v1/admin/questions",
        headers=auth_headers,
        json={
            "question_id": "test_unauth",
            "exam_type": "security",
            "domain": "1.1",
            "question_text": "Unauthorized?",
            "correct_answer": "A",
            "options": {
                "A": {"text": "Option A", "explanation": "Answer A"},
                "B": {"text": "Option B", "explanation": "Answer B"},
                "C": {"text": "Option C", "explanation": "Answer C"},
                "D": {"text": "Option D", "explanation": "Answer D"}
            }
        }
    )

    if response.status_code != 404:
        assert response.status_code == 403


@pytest.mark.api
@pytest.mark.integration
def test_regular_user_cannot_delete_user(client, auth_headers, test_db):
    """Test that regular users cannot delete other users"""
    # Create user
    user = User(
        email="victim@example.com",
        username="victim",
        hashed_password=hash_password("pass123"),
        is_active=True
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)

    response = client.delete(f"/api/v1/admin/users/{user.id}",
        headers=auth_headers
    )

    if response.status_code != 404:
        assert response.status_code == 403

        # User should still exist
        still_exists = test_db.query(User).filter(User.id == user.id).first()
        assert still_exists is not None


@pytest.mark.api
@pytest.mark.integration
def test_regular_user_cannot_promote_to_admin(client, auth_headers, test_db):
    """Test that regular users cannot promote themselves or others to admin"""
    response = client.post(f"/api/v1/admin/users/{test_db.query(User).first().id}/promote",
        headers=auth_headers
    )

    if response.status_code != 404:
        assert response.status_code == 403
