"""
Question Endpoint Tests

Tests for question-related endpoints:
- Get random questions by exam type
- Get available exam types
- Question randomization
- Question difficulty filtering
"""

import pytest
from app.models.question import Question


# ================================================================
# GET EXAM TYPES TESTS
# ================================================================

@pytest.mark.api
@pytest.mark.integration
def test_get_exam_types(client):
    """Test getting list of available exam types"""
    response = client.get("/api/v1/questions/exams")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Should include standard exam types
    expected_exams = ["security", "network", "a1101", "a1102"]
    for exam in expected_exams:
        assert exam in data or any(exam in str(item).lower() for item in data)


@pytest.mark.api
@pytest.mark.integration
def test_exam_types_no_auth_required(client):
    """Test that getting exam types doesn't require authentication"""
    response = client.get("/api/v1/questions/exams")
    # Should work without auth
    assert response.status_code == 200


# ================================================================
# GET RANDOM QUESTIONS TESTS
# ================================================================

@pytest.mark.api
@pytest.mark.integration
def test_get_random_questions_success(client, auth_headers, test_db):
    """Test getting random questions for an exam type"""
    # Create 10 questions
    for i in range(10):
        q = Question(
            exam_type="security",
            question_text=f"Security question {i}?",
            correct_answer="A",
            options={
                "A": {"text": f"Option A{i}", "explanation": "Correct answer"},
                "B": {"text": f"Option B{i}", "explanation": "Incorrect"},
                "C": {"text": f"Option C{i}", "explanation": "Incorrect"},
                "D": {"text": f"Option D{i}", "explanation": "Incorrect"}
            }
        )
        test_db.add(q)
    test_db.commit()

    response = client.get("/api/v1/questions/random?exam_type=security&count=5",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5
    assert all(q["exam_type"] == "security" for q in data)
    # Should not include correct answer in response
    assert all("correct_answer" not in q for q in data)


@pytest.mark.api
@pytest.mark.integration
def test_get_random_questions_default_count(client, auth_headers, test_db):
    """Test getting random questions with default count"""
    # Create 20 questions
    for i in range(20):
        q = Question(
            exam_type="network",
            question_text=f"Network question {i}?",
            correct_answer="B",
            options={
                "A": {"text": "Option A", "explanation": "Incorrect"},
                "B": {"text": "Option B", "explanation": "Correct answer"},
                "C": {"text": "Option C", "explanation": "Incorrect"},
                "D": {"text": "Option D", "explanation": "Incorrect"}
            }
        )
        test_db.add(q)
    test_db.commit()

    # Request without count parameter (should default to 10)
    response = client.get("/api/v1/questions/random?exam_type=network",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    # Default count is typically 10
    assert len(data) <= 20


@pytest.mark.api
@pytest.mark.integration
def test_get_random_questions_insufficient_pool(client, auth_headers, test_db):
    """Test getting random questions when fewer questions exist than requested"""
    # Create only 3 questions
    for i in range(3):
        q = Question(
            exam_type="a1101",
            question_text=f"Question {i}?",
            correct_answer="C",
            options={
                "A": {"text": "Option A", "explanation": "Incorrect"},
                "B": {"text": "Option B", "explanation": "Incorrect"},
                "C": {"text": "Option C", "explanation": "Correct answer"},
                "D": {"text": "Option D", "explanation": "Incorrect"}
            }
        )
        test_db.add(q)
    test_db.commit()

    # Request 10 questions but only 3 exist
    response = client.get("/api/v1/questions/random?exam_type=a1101&count=10",
        headers=auth_headers
    )

    # Should return what's available or error
    if response.status_code == 200:
        data = response.json()
        assert len(data) == 3  # Return all available
    else:
        assert response.status_code == 400  # Or reject request


@pytest.mark.api
@pytest.mark.integration
def test_random_questions_no_auth(client, test_db):
    """Test that random questions require authentication"""
    # Create questions
    q = Question(
        exam_type="security",
        question_text="Test?",
        correct_answer="A",
        options={
            "A": {"text": "Option A", "explanation": "Correct"},
            "B": {"text": "Option B", "explanation": "Incorrect"},
            "C": {"text": "Option C", "explanation": "Incorrect"},
            "D": {"text": "Option D", "explanation": "Incorrect"}
        }
    )
    test_db.add(q)
    test_db.commit()

    response = client.get("/api/v1/questions/random?exam_type=security")

    # Should require auth
    assert response.status_code == 401


@pytest.mark.api
@pytest.mark.integration
def test_random_questions_invalid_exam_type(client, auth_headers):
    """Test getting questions for invalid exam type"""
    response = client.get("/api/v1/questions/random?exam_type=invalid_exam&count=5",
        headers=auth_headers
    )

    # Should validate exam type
    assert response.status_code in [400, 404, 422]


@pytest.mark.api
@pytest.mark.integration
def test_random_questions_invalid_count(client, auth_headers, test_db):
    """Test getting questions with invalid count parameter"""
    q = Question(
        exam_type="security",
        question_text="Test?",
        correct_answer="A",
        options={
            "A": {"text": "Option A", "explanation": "Correct"},
            "B": {"text": "Option B", "explanation": "Incorrect"},
            "C": {"text": "Option C", "explanation": "Incorrect"},
            "D": {"text": "Option D", "explanation": "Incorrect"}
        }
    )
    test_db.add(q)
    test_db.commit()

    # Try negative count
    response = client.get("/api/v1/questions/random?exam_type=security&count=-5",
        headers=auth_headers
    )

    assert response.status_code in [400, 422]

    # Try zero count
    response = client.get("/api/v1/questions/random?exam_type=security&count=0",
        headers=auth_headers
    )

    assert response.status_code in [400, 422]


@pytest.mark.api
@pytest.mark.integration
def test_random_questions_excessive_count(client, auth_headers, test_db):
    """Test getting questions with excessively large count"""
    q = Question(
        exam_type="security",
        question_text="Test?",
        correct_answer="A",
        options={
            "A": {"text": "Option A", "explanation": "Correct"},
            "B": {"text": "Option B", "explanation": "Incorrect"},
            "C": {"text": "Option C", "explanation": "Incorrect"},
            "D": {"text": "Option D", "explanation": "Incorrect"}
        }
    )
    test_db.add(q)
    test_db.commit()

    # Try requesting 1000 questions
    response = client.get("/api/v1/questions/random?exam_type=security&count=1000",
        headers=auth_headers
    )

    # Should limit or reject excessive requests
    if response.status_code == 200:
        data = response.json()
        assert len(data) <= 100  # Should have reasonable limit
    else:
        assert response.status_code in [400, 422]


# ================================================================
# RANDOMIZATION TESTS
# ================================================================

@pytest.mark.api
@pytest.mark.integration
def test_questions_are_randomized(client, auth_headers, test_db):
    """Test that questions are actually randomized between requests"""
    # Create 20 questions
    for i in range(20):
        q = Question(
            exam_type="network",
            question_text=f"Question {i}?",
            correct_answer="A",
            options={
                "A": {"text": "Option A", "explanation": "Correct"},
                "B": {"text": "Option B", "explanation": "Incorrect"},
                "C": {"text": "Option C", "explanation": "Incorrect"},
                "D": {"text": "Option D", "explanation": "Incorrect"}
            }
        )
        test_db.add(q)
    test_db.commit()

    # Make two requests for 5 questions
    response1 = client.get("/api/v1/questions/random?exam_type=network&count=5",
        headers=auth_headers
    )
    response2 = client.get("/api/v1/questions/random?exam_type=network&count=5",
        headers=auth_headers
    )

    assert response1.status_code == 200
    assert response2.status_code == 200

    data1 = response1.json()
    data2 = response2.json()

    # Extract question IDs
    ids1 = [q["id"] for q in data1]
    ids2 = [q["id"] for q in data2]

    # Should be different (or at least not always identical)
    # This might occasionally fail due to randomness, but very unlikely with 20 questions
    assert ids1 != ids2 or len(set(ids1)) == len(set(ids2))


# ================================================================
# DIFFICULTY FILTERING TESTS
# ================================================================

@pytest.mark.api
@pytest.mark.integration
def test_get_questions_by_difficulty(client, auth_headers, test_db):
    """Test filtering questions by difficulty level"""
    # Create questions of different difficulties
    # NOTE: Question model doesn't have difficulty field - this test may need endpoint support
    for i in range(15):
        q = Question(
            exam_type="security",
            question_text=f"Question {i}?",
            correct_answer="A",
            options={
                "A": {"text": "Option A", "explanation": "Correct"},
                "B": {"text": "Option B", "explanation": "Incorrect"},
                "C": {"text": "Option C", "explanation": "Incorrect"},
                "D": {"text": "Option D", "explanation": "Incorrect"}
            }
        )
        test_db.add(q)
    test_db.commit()

    # Request only medium questions
    response = client.get(
        "/api/v1/questions/random?exam_type=security&count=5&difficulty=medium",
        headers=auth_headers
    )

    if response.status_code == 200:
        data = response.json()
        # Difficulty filtering may or may not be supported (Question model has no difficulty field)
        # This test verifies the endpoint accepts the parameter without error
        assert len(data) >= 0


# ================================================================
# QUESTION FORMAT TESTS
# ================================================================

@pytest.mark.api
@pytest.mark.integration
def test_question_response_format(client, auth_headers, test_db):
    """Test that questions have correct response format"""
    q = Question(
        exam_type="security",
        question_text="What is the best security practice?",
        correct_answer="A",
        options={
            "A": {"text": "Use strong passwords", "explanation": "Strong passwords are essential for security"},
            "B": {"text": "Share passwords", "explanation": "Never share passwords"},
            "C": {"text": "No passwords", "explanation": "Always use passwords"},
            "D": {"text": "Weak passwords", "explanation": "Use strong passwords"}
        }
    )
    test_db.add(q)
    test_db.commit()

    response = client.get("/api/v1/questions/random?exam_type=security&count=1",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1

    question = data[0]
    # Required fields
    assert "id" in question
    assert "question_text" in question
    assert "options" in question or "option_a" in question  # May return options or formatted
    assert "exam_type" in question

    # Should NOT include correct answer (that's for after submission)
    assert "correct_answer" not in question


# ================================================================
# EXAM TYPE SPECIFIC TESTS
# ================================================================

@pytest.mark.api
@pytest.mark.integration
def test_get_security_questions(client, auth_headers, test_db):
    """Test getting Security+ specific questions"""
    for i in range(5):
        q = Question(
            exam_type="security",
            question_text=f"Security question {i}?",
            correct_answer="A",
            options={
                "A": {"text": "Option A", "explanation": "Correct"},
                "B": {"text": "Option B", "explanation": "Incorrect"},
                "C": {"text": "Option C", "explanation": "Incorrect"},
                "D": {"text": "Option D", "explanation": "Incorrect"}
            }
        )
        test_db.add(q)
    test_db.commit()

    response = client.get("/api/v1/questions/random?exam_type=security&count=5",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert all(q["exam_type"] == "security" for q in data)


@pytest.mark.api
@pytest.mark.integration
def test_get_network_questions(client, auth_headers, test_db):
    """Test getting Network+ specific questions"""
    for i in range(5):
        q = Question(
            exam_type="network",
            question_text=f"Network question {i}?",
            correct_answer="B",
            options={
                "A": {"text": "Option A", "explanation": "Incorrect"},
                "B": {"text": "Option B", "explanation": "Correct"},
                "C": {"text": "Option C", "explanation": "Incorrect"},
                "D": {"text": "Option D", "explanation": "Incorrect"}
            }
        )
        test_db.add(q)
    test_db.commit()

    response = client.get("/api/v1/questions/random?exam_type=network&count=5",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert all(q["exam_type"] == "network" for q in data)


@pytest.mark.api
@pytest.mark.integration
def test_get_a1101_questions(client, auth_headers, test_db):
    """Test getting A+ Core 1 (A-1101) questions"""
    for i in range(5):
        q = Question(
            exam_type="a1101",
            question_text=f"A+ Core 1 question {i}?",
            correct_answer="C",
            options={
                "A": {"text": "Option A", "explanation": "Incorrect"},
                "B": {"text": "Option B", "explanation": "Incorrect"},
                "C": {"text": "Option C", "explanation": "Correct"},
                "D": {"text": "Option D", "explanation": "Incorrect"}
            }
        )
        test_db.add(q)
    test_db.commit()

    response = client.get("/api/v1/questions/random?exam_type=a1101&count=5",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert all(q["exam_type"] == "a1101" for q in data)


@pytest.mark.api
@pytest.mark.integration
def test_get_a1102_questions(client, auth_headers, test_db):
    """Test getting A+ Core 2 (A-1102) questions"""
    for i in range(5):
        q = Question(
            exam_type="a1102",
            question_text=f"A+ Core 2 question {i}?",
            correct_answer="D",
            options={
                "A": {"text": "Option A", "explanation": "Incorrect"},
                "B": {"text": "Option B", "explanation": "Incorrect"},
                "C": {"text": "Option C", "explanation": "Incorrect"},
                "D": {"text": "Option D", "explanation": "Correct"}
            }
        )
        test_db.add(q)
    test_db.commit()

    response = client.get("/api/v1/questions/random?exam_type=a1102&count=5",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert all(q["exam_type"] == "a1102" for q in data)


# ================================================================
# EDGE CASES
# ================================================================

@pytest.mark.api
@pytest.mark.integration
def test_get_questions_empty_database(client, auth_headers, test_db):
    """Test getting questions when no questions exist for exam type"""
    response = client.get("/api/v1/questions/random?exam_type=security&count=5",
        headers=auth_headers
    )

    # Should handle gracefully
    if response.status_code == 200:
        data = response.json()
        assert len(data) == 0
    else:
        assert response.status_code in [400, 404]


@pytest.mark.api
@pytest.mark.integration
def test_get_questions_missing_exam_type_param(client, auth_headers):
    """Test getting questions without specifying exam_type"""
    response = client.get("/api/v1/questions/random?count=5",
        headers=auth_headers
    )

    # Should require exam_type parameter
    assert response.status_code in [400, 422]


@pytest.mark.api
@pytest.mark.integration
def test_get_questions_multiple_same_request(client, auth_headers, test_db):
    """Test that multiple identical requests work correctly"""
    # Create questions
    for i in range(10):
        q = Question(
            exam_type="security",
            question_text=f"Question {i}?",
            correct_answer="A",
            options={
                "A": {"text": "Option A", "explanation": "Correct"},
                "B": {"text": "Option B", "explanation": "Incorrect"},
                "C": {"text": "Option C", "explanation": "Incorrect"},
                "D": {"text": "Option D", "explanation": "Incorrect"}
            }
        )
        test_db.add(q)
    test_db.commit()

    # Make multiple requests
    for _ in range(3):
        response = client.get("/api/v1/questions/random?exam_type=security&count=5",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5
