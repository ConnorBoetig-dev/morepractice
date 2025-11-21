"""
Question Bookmarks Tests

Tests for question bookmarking functionality
"""

import pytest
from app.models.question import Question, QuestionBookmark


@pytest.mark.integration
def test_create_bookmark_success(client, test_db, test_user_token):
    """Test creating a bookmark for a question"""
    # Create a test question
    question = Question(
        question_id="TEST001",
        exam_type="security",
        domain="1.1",
        question_text="Test question about security?",
        correct_answer="A",
        options={
            "A": {"text": "Option A", "explanation": "Correct answer"},
            "B": {"text": "Option B", "explanation": "Wrong answer"}
        }
    )
    test_db.add(question)
    test_db.commit()
    test_db.refresh(question)

    # Create bookmark
    response = client.post(
        f"/api/v1/bookmarks/questions/{question.id}",
        json={"notes": "Important question to review"},
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["question_id"] == question.id
    assert data["notes"] == "Important question to review"
    assert "created_at" in data
    assert data["question"]["question_text"] == "Test question about security?"


@pytest.mark.integration
def test_create_bookmark_without_notes(client, test_db, test_user_token):
    """Test creating a bookmark without notes"""
    question = Question(
        question_id="TEST002",
        exam_type="network",
        domain="2.1",
        question_text="Test networking question?",
        correct_answer="B",
        options={
            "A": {"text": "Option A", "explanation": "Wrong"},
            "B": {"text": "Option B", "explanation": "Correct"}
        }
    )
    test_db.add(question)
    test_db.commit()
    test_db.refresh(question)

    response = client.post(
        f"/api/v1/bookmarks/questions/{question.id}",
        json={},
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["question_id"] == question.id
    assert data["notes"] is None


@pytest.mark.integration
def test_create_bookmark_nonexistent_question(client, test_user_token):
    """Test creating a bookmark for a nonexistent question"""
    response = client.post(
        "/api/v1/bookmarks/questions/99999",
        json={"notes": "This should fail"},
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.integration
def test_create_bookmark_no_auth(client, test_db):
    """Test creating a bookmark without authentication"""
    question = Question(
        question_id="TEST003",
        exam_type="security",
        domain="1.2",
        question_text="Test question?",
        correct_answer="A",
        options={
            "A": {"text": "Option A", "explanation": "Correct"},
            "B": {"text": "Option B", "explanation": "Wrong"}
        }
    )
    test_db.add(question)
    test_db.commit()
    test_db.refresh(question)

    response = client.post(
        f"/api/v1/bookmarks/questions/{question.id}",
        json={"notes": "Should fail"}
    )

    assert response.status_code in [401, 403]  # Both are valid for missing auth


@pytest.mark.integration
def test_update_existing_bookmark(client, test_db, test_user, test_user_token):
    """Test updating an existing bookmark's notes"""
    # Create question
    question = Question(
        question_id="TEST004",
        exam_type="security",
        domain="1.3",
        question_text="Test question?",
        correct_answer="A",
        options={
            "A": {"text": "Option A", "explanation": "Correct"},
            "B": {"text": "Option B", "explanation": "Wrong"}
        }
    )
    test_db.add(question)
    test_db.commit()
    test_db.refresh(question)

    # Create initial bookmark
    response1 = client.post(
        f"/api/v1/bookmarks/questions/{question.id}",
        json={"notes": "Original notes"},
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response1.status_code == 201

    # Update bookmark (POST to same endpoint)
    response2 = client.post(
        f"/api/v1/bookmarks/questions/{question.id}",
        json={"notes": "Updated notes"},
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response2.status_code == 201
    assert response2.json()["notes"] == "Updated notes"


@pytest.mark.integration
def test_get_user_bookmarks(client, test_db, test_user, test_user_token):
    """Test getting user's bookmarks with pagination"""
    # Create multiple questions
    for i in range(5):
        question = Question(
            question_id=f"TEST{100+i}",
            exam_type="security",
            domain="1.1",
            question_text=f"Test question {i}?",
            correct_answer="A",
            options={
                "A": {"text": "Option A", "explanation": "Correct"},
                "B": {"text": "Option B", "explanation": "Wrong"}
            }
        )
        test_db.add(question)
    test_db.commit()

    # Bookmark all questions
    questions = test_db.query(Question).all()
    for question in questions:
        bookmark = QuestionBookmark(
            user_id=test_user.id,
            question_id=question.id,
            notes=f"Notes for question {question.id}"
        )
        test_db.add(bookmark)
    test_db.commit()

    # Get bookmarks
    response = client.get(
        "/api/v1/bookmarks?page=1&page_size=3",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert data["page"] == 1
    assert data["page_size"] == 3
    assert len(data["bookmarks"]) == 3
    assert "question" in data["bookmarks"][0]


@pytest.mark.integration
def test_get_bookmarks_pagination(client, test_db, test_user, test_user_token):
    """Test bookmark pagination works correctly"""
    # Create 15 questions and bookmark them
    for i in range(15):
        question = Question(
            question_id=f"TESTPAGE{i}",
            exam_type="security",
            domain="1.1",
            question_text=f"Pagination test {i}?",
            correct_answer="A",
            options={
                "A": {"text": "Option A", "explanation": "Correct"},
                "B": {"text": "Option B", "explanation": "Wrong"}
            }
        )
        test_db.add(question)
    test_db.commit()

    questions = test_db.query(Question).filter(
        Question.question_id.like("TESTPAGE%")
    ).all()
    for question in questions:
        bookmark = QuestionBookmark(
            user_id=test_user.id,
            question_id=question.id
        )
        test_db.add(bookmark)
    test_db.commit()

    # Get page 1
    response1 = client.get(
        "/api/v1/bookmarks?page=1&page_size=10",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response1.status_code == 200
    assert len(response1.json()["bookmarks"]) == 10

    # Get page 2
    response2 = client.get(
        "/api/v1/bookmarks?page=2&page_size=10",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response2.status_code == 200
    assert len(response2.json()["bookmarks"]) == 5


@pytest.mark.integration
def test_delete_bookmark(client, test_db, test_user, test_user_token):
    """Test removing a bookmark"""
    # Create and bookmark a question
    question = Question(
        question_id="TESTDEL",
        exam_type="security",
        domain="1.1",
        question_text="Test delete?",
        correct_answer="A",
        options={
            "A": {"text": "Option A", "explanation": "Correct"},
            "B": {"text": "Option B", "explanation": "Wrong"}
        }
    )
    test_db.add(question)
    test_db.commit()
    test_db.refresh(question)

    bookmark = QuestionBookmark(
        user_id=test_user.id,
        question_id=question.id,
        notes="To be deleted"
    )
    test_db.add(bookmark)
    test_db.commit()

    # Delete bookmark
    response = client.delete(
        f"/api/v1/bookmarks/questions/{question.id}",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 200
    assert "removed successfully" in response.json()["message"]

    # Verify it's gone
    deleted = test_db.query(QuestionBookmark).filter(
        QuestionBookmark.user_id == test_user.id,
        QuestionBookmark.question_id == question.id
    ).first()
    assert deleted is None


@pytest.mark.integration
def test_delete_nonexistent_bookmark(client, test_db, test_user_token):
    """Test deleting a bookmark that doesn't exist"""
    # Create a question but don't bookmark it
    question = Question(
        question_id="TESTDEL2",
        exam_type="security",
        domain="1.1",
        question_text="Test delete fail?",
        correct_answer="A",
        options={
            "A": {"text": "Option A", "explanation": "Correct"},
            "B": {"text": "Option B", "explanation": "Wrong"}
        }
    )
    test_db.add(question)
    test_db.commit()
    test_db.refresh(question)

    # Try to delete non-existent bookmark
    response = client.delete(
        f"/api/v1/bookmarks/questions/{question.id}",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 404


@pytest.mark.integration
def test_update_bookmark_notes(client, test_db, test_user, test_user_token):
    """Test updating bookmark notes with PATCH"""
    # Create and bookmark a question
    question = Question(
        question_id="TESTPATCH",
        exam_type="security",
        domain="1.1",
        question_text="Test patch?",
        correct_answer="A",
        options={
            "A": {"text": "Option A", "explanation": "Correct"},
            "B": {"text": "Option B", "explanation": "Wrong"}
        }
    )
    test_db.add(question)
    test_db.commit()
    test_db.refresh(question)

    bookmark = QuestionBookmark(
        user_id=test_user.id,
        question_id=question.id,
        notes="Original notes"
    )
    test_db.add(bookmark)
    test_db.commit()

    # Update notes
    response = client.patch(
        f"/api/v1/bookmarks/questions/{question.id}",
        json={"notes": "Patched notes"},
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 200
    assert response.json()["notes"] == "Patched notes"


@pytest.mark.integration
def test_check_if_bookmarked(client, test_db, test_user, test_user_token):
    """Test checking if a question is bookmarked"""
    # Create two questions
    question1 = Question(
        question_id="TESTCHECK1",
        exam_type="security",
        domain="1.1",
        question_text="Test check bookmarked?",
        correct_answer="A",
        options={
            "A": {"text": "Option A", "explanation": "Correct"},
            "B": {"text": "Option B", "explanation": "Wrong"}
        }
    )
    question2 = Question(
        question_id="TESTCHECK2",
        exam_type="security",
        domain="1.1",
        question_text="Test check not bookmarked?",
        correct_answer="A",
        options={
            "A": {"text": "Option A", "explanation": "Correct"},
            "B": {"text": "Option B", "explanation": "Wrong"}
        }
    )
    test_db.add(question1)
    test_db.add(question2)
    test_db.commit()
    test_db.refresh(question1)
    test_db.refresh(question2)

    # Bookmark only question1
    bookmark = QuestionBookmark(
        user_id=test_user.id,
        question_id=question1.id
    )
    test_db.add(bookmark)
    test_db.commit()

    # Check question1 (should be bookmarked)
    response1 = client.get(
        f"/api/v1/bookmarks/questions/{question1.id}/check",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response1.status_code == 200
    assert response1.json()["is_bookmarked"] is True

    # Check question2 (should not be bookmarked)
    response2 = client.get(
        f"/api/v1/bookmarks/questions/{question2.id}/check",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response2.status_code == 200
    assert response2.json()["is_bookmarked"] is False


@pytest.mark.integration
def test_bookmarks_isolated_per_user(client, test_db, test_user):
    """Test that bookmarks are isolated between users"""
    from app.models.user import User
    from app.utils.auth import hash_password, create_access_token

    # Create second user
    user2 = User(
        email="user2@example.com",
        username="user2",
        hashed_password=hash_password("Test@Pass9word!"),
        is_active=True,
        is_verified=True
    )
    test_db.add(user2)
    test_db.commit()
    test_db.refresh(user2)

    # Create question
    question = Question(
        question_id="TESTISOLATE",
        exam_type="security",
        domain="1.1",
        question_text="Test isolation?",
        correct_answer="A",
        options={
            "A": {"text": "Option A", "explanation": "Correct"},
            "B": {"text": "Option B", "explanation": "Wrong"}
        }
    )
    test_db.add(question)
    test_db.commit()
    test_db.refresh(question)

    # User 1 bookmarks the question
    bookmark1 = QuestionBookmark(
        user_id=test_user.id,
        question_id=question.id,
        notes="User 1 notes"
    )
    test_db.add(bookmark1)
    test_db.commit()

    # User 2 token
    user2_token = create_access_token(data={"user_id": user2.id})

    # User 2 checks if bookmarked (should be false)
    response = client.get(
        f"/api/v1/bookmarks/questions/{question.id}/check",
        headers={"Authorization": f"Bearer {user2_token}"}
    )
    assert response.status_code == 200
    assert response.json()["is_bookmarked"] is False

    # User 2 gets their bookmarks (should be empty)
    response2 = client.get(
        "/api/v1/bookmarks",
        headers={"Authorization": f"Bearer {user2_token}"}
    )
    assert response2.status_code == 200
    assert response2.json()["total"] == 0


# ================================================================
# EDGE CASE & VALIDATION TESTS
# ================================================================

@pytest.mark.integration
def test_bookmark_notes_max_length(client, test_db, test_user_token):
    """Test that notes exceeding 1000 characters are rejected"""
    question = Question(
        question_id="TESTMAXLEN",
        exam_type="security",
        domain="1.1",
        question_text="Test max length?",
        correct_answer="A",
        options={
            "A": {"text": "Option A", "explanation": "Correct"},
            "B": {"text": "Option B", "explanation": "Wrong"}
        }
    )
    test_db.add(question)
    test_db.commit()
    test_db.refresh(question)

    # Create notes that exceed 1000 characters
    long_notes = "x" * 1001

    response = client.post(
        f"/api/v1/bookmarks/questions/{question.id}",
        json={"notes": long_notes},
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    # Should fail validation
    assert response.status_code == 422  # Unprocessable Entity (validation error)


@pytest.mark.integration
def test_bookmark_notes_exactly_max_length(client, test_db, test_user_token):
    """Test that notes at exactly 1000 characters are accepted"""
    question = Question(
        question_id="TESTEXACTLEN",
        exam_type="security",
        domain="1.1",
        question_text="Test exact length?",
        correct_answer="A",
        options={
            "A": {"text": "Option A", "explanation": "Correct"},
            "B": {"text": "Option B", "explanation": "Wrong"}
        }
    )
    test_db.add(question)
    test_db.commit()
    test_db.refresh(question)

    # Create notes exactly 1000 characters
    exact_notes = "x" * 1000

    response = client.post(
        f"/api/v1/bookmarks/questions/{question.id}",
        json={"notes": exact_notes},
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    # Should succeed
    assert response.status_code == 201
    assert len(response.json()["notes"]) == 1000


@pytest.mark.integration
def test_pagination_invalid_page_zero(client, test_user_token):
    """Test that page=0 is rejected"""
    response = client.get(
        "/api/v1/bookmarks?page=0&page_size=10",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    # FastAPI query validation returns 422
    assert response.status_code == 422


@pytest.mark.integration
def test_pagination_invalid_page_negative(client, test_user_token):
    """Test that negative page is rejected"""
    response = client.get(
        "/api/v1/bookmarks?page=-1&page_size=10",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    # Query param validation happens at FastAPI level
    assert response.status_code in [400, 422]


@pytest.mark.integration
def test_pagination_invalid_page_size_zero(client, test_user_token):
    """Test that page_size=0 is rejected"""
    response = client.get(
        "/api/v1/bookmarks?page=1&page_size=0",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    # Should fail FastAPI query param validation (ge=1)
    assert response.status_code in [400, 422]


@pytest.mark.integration
def test_pagination_invalid_page_size_too_large(client, test_user_token):
    """Test that page_size > 100 is rejected"""
    response = client.get(
        "/api/v1/bookmarks?page=1&page_size=101",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    # Should fail FastAPI query param validation (le=100)
    assert response.status_code in [400, 422]


@pytest.mark.integration
def test_cascade_delete_question(client, test_db, test_user, test_user_token):
    """Test that deleting a question cascades to delete bookmarks"""
    # Create question
    question = Question(
        question_id="TESTCASCADE1",
        exam_type="security",
        domain="1.1",
        question_text="Test cascade delete?",
        correct_answer="A",
        options={
            "A": {"text": "Option A", "explanation": "Correct"},
            "B": {"text": "Option B", "explanation": "Wrong"}
        }
    )
    test_db.add(question)
    test_db.commit()
    test_db.refresh(question)

    # Create bookmark
    bookmark = QuestionBookmark(
        user_id=test_user.id,
        question_id=question.id,
        notes="This bookmark should be deleted"
    )
    test_db.add(bookmark)
    test_db.commit()

    # Verify bookmark exists
    existing = test_db.query(QuestionBookmark).filter(
        QuestionBookmark.user_id == test_user.id,
        QuestionBookmark.question_id == question.id
    ).first()
    assert existing is not None

    # Delete the question
    test_db.delete(question)
    test_db.commit()

    # Verify bookmark was cascade deleted
    deleted_bookmark = test_db.query(QuestionBookmark).filter(
        QuestionBookmark.user_id == test_user.id,
        QuestionBookmark.question_id == question.id
    ).first()
    assert deleted_bookmark is None


@pytest.mark.integration
def test_cascade_delete_user(client, test_db):
    """Test that deleting a user cascades to delete their bookmarks"""
    from app.models.user import User
    from app.utils.auth import hash_password

    # Create user
    user = User(
        email="deleteme@example.com",
        username="deleteme",
        hashed_password=hash_password("Test@Pass9word!"),
        is_active=True,
        is_verified=True
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)

    # Create question
    question = Question(
        question_id="TESTCASCADE2",
        exam_type="security",
        domain="1.1",
        question_text="Test user cascade delete?",
        correct_answer="A",
        options={
            "A": {"text": "Option A", "explanation": "Correct"},
            "B": {"text": "Option B", "explanation": "Wrong"}
        }
    )
    test_db.add(question)
    test_db.commit()
    test_db.refresh(question)

    # Create bookmark
    bookmark = QuestionBookmark(
        user_id=user.id,
        question_id=question.id,
        notes="This bookmark should be deleted when user is deleted"
    )
    test_db.add(bookmark)
    test_db.commit()

    # Verify bookmark exists
    existing = test_db.query(QuestionBookmark).filter(
        QuestionBookmark.user_id == user.id,
        QuestionBookmark.question_id == question.id
    ).first()
    assert existing is not None

    # Delete the user
    test_db.delete(user)
    test_db.commit()

    # Verify bookmark was cascade deleted
    deleted_bookmark = test_db.query(QuestionBookmark).filter(
        QuestionBookmark.user_id == user.id
    ).first()
    assert deleted_bookmark is None


@pytest.mark.integration
def test_empty_bookmarks_list(client, test_user_token):
    """Test getting bookmarks when user has no bookmarks"""
    response = client.get(
        "/api/v1/bookmarks?page=1&page_size=10",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["page"] == 1
    assert data["page_size"] == 10
    assert data["bookmarks"] == []


@pytest.mark.integration
def test_invalid_question_id_negative(client, test_user_token):
    """Test bookmarking with negative question ID"""
    response = client.post(
        "/api/v1/bookmarks/questions/-1",
        json={"notes": "Invalid ID"},
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 404  # Question not found


@pytest.mark.integration
def test_invalid_question_id_zero(client, test_user_token):
    """Test bookmarking with zero question ID"""
    response = client.post(
        "/api/v1/bookmarks/questions/0",
        json={"notes": "Invalid ID"},
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 404  # Question not found
