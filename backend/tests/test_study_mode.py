"""
Study Mode Tests - COMPREHENSIVE & SUBSTANTIVE

Tests the complete study mode vs practice mode functionality.
Every test verifies REAL functionality end-to-end, not just format.

These tests catch REAL bugs:
- Study mode workflow broken
- Practice mode mode field not set
- Session management issues
- XP calculation differences
- Feedback not showing explanations
- Mode filtering in quiz history

NO FLUFF - Every test integrates with actual business logic.
"""

import pytest
from app.models.gamification import QuizAttempt, StudySession
from app.models.question import Question
from app.models.user import UserProfile


# ================================================================
# STUDY MODE - START SESSION
# ================================================================

@pytest.mark.integration
def test_start_study_session_creates_session_and_returns_first_question(client, test_db, test_user_token):
    """
    REAL TEST: Start study session and verify first question is returned
    Tests: Session creation, question retrieval, response format
    """
    # Create test questions
    for i in range(5):
        question = Question(
            question_id=f"STUDY{i}",
            exam_type="security",
            domain="1.1",
            question_text=f"Study question {i}?",
            correct_answer="A",
            options={
                "A": {"text": "Correct answer", "explanation": "This is correct"},
                "B": {"text": "Wrong answer", "explanation": "This is wrong"}
            }
        )
        test_db.add(question)
    test_db.commit()

    # Start study session
    response = client.post(
        "/api/v1/study/start",
        json={"exam_type": "security", "count": 5},
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 201
    data = response.json()

    # Verify session created
    assert "session_id" in data
    assert data["exam_type"] == "security"
    assert data["total_questions"] == 5
    assert data["current_index"] == 0

    # Verify first question returned (without correct answer)
    assert "current_question" in data
    question = data["current_question"]
    assert "question_id" in question
    assert "question_text" in question
    assert "domain" in question
    assert "options" in question

    # Verify options don't include explanations (not shown until answered)
    option_a = question["options"]["A"]
    assert "text" in option_a
    assert "explanation" not in option_a  # Explanations hidden until answer

    # Verify session exists in database
    session = test_db.query(StudySession).filter(StudySession.id == data["session_id"]).first()
    assert session is not None
    assert session.is_completed is False


@pytest.mark.integration
def test_start_study_session_with_existing_active_session_fails(client, test_db, test_user_token, test_user):
    """
    REAL TEST: Cannot start new session if active session exists
    Tests: Session uniqueness constraint, business logic validation
    """
    # Create questions
    question = Question(
        question_id="EXIST1",
        exam_type="security",
        domain="1.1",
        question_text="Test?",
        correct_answer="A",
        options={"A": {"text": "A", "explanation": "A"}, "B": {"text": "B", "explanation": "B"}}
    )
    test_db.add(question)
    test_db.commit()

    # Start first session
    response1 = client.post(
        "/api/v1/study/start",
        json={"exam_type": "security", "count": 1},
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response1.status_code == 201

    # Try to start second session (should fail)
    response2 = client.post(
        "/api/v1/study/start",
        json={"exam_type": "network", "count": 1},
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response2.status_code == 400
    data = response2.json()
    assert data["success"] is False
    assert "active" in data["error"]["message"].lower()


@pytest.mark.integration
def test_start_study_session_with_no_questions_fails(client, test_user_token):
    """
    REAL TEST: Starting session with no questions available should fail
    Tests: Question availability validation

    Uses valid exam_type but empty database (test_db starts clean with no questions)
    """
    response = client.post(
        "/api/v1/study/start",
        json={"exam_type": "security", "count": 10},
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert "no questions found" in data["error"]["message"].lower()


# ================================================================
# STUDY MODE - ANSWER QUESTIONS
# ================================================================

@pytest.mark.integration
def test_answer_study_question_returns_immediate_feedback_with_explanations(client, test_db, test_user_token):
    """
    REAL TEST: Answer question and get immediate feedback with full explanations
    Tests: Immediate feedback, explanation visibility, progress tracking
    """
    # Create 2 test questions
    q1 = Question(
        question_id="FEED1",
        exam_type="security",
        domain="1.1",
        question_text="What is encryption?",
        correct_answer="B",
        options={
            "A": {"text": "Compression", "explanation": "Wrong - compression reduces size"},
            "B": {"text": "Confidentiality", "explanation": "Correct - encryption protects confidentiality"},
            "C": {"text": "Deletion", "explanation": "Wrong - deletion removes data"}
        }
    )
    q2 = Question(
        question_id="FEED2",
        exam_type="security",
        domain="1.2",
        question_text="Second question?",
        correct_answer="A",
        options={
            "A": {"text": "Right", "explanation": "Correct"},
            "B": {"text": "Wrong", "explanation": "Incorrect"}
        }
    )
    test_db.add_all([q1, q2])
    test_db.commit()

    # Start session
    start_response = client.post(
        "/api/v1/study/start",
        json={"exam_type": "security", "count": 2},
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    session_id = start_response.json()["session_id"]

    # Answer first question INCORRECTLY
    answer_response = client.post(
        "/api/v1/study/answer",
        json={
            "session_id": session_id,
            "question_id": q1.id,
            "user_answer": "A"  # Wrong answer
        },
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert answer_response.status_code == 200
    data = answer_response.json()

    # Verify immediate feedback
    assert data["is_correct"] is False
    assert data["user_answer"] == "A"
    assert data["correct_answer"] == "B"

    # Verify explanations are shown
    assert data["user_answer_text"] == "Compression"
    assert data["correct_answer_text"] == "Confidentiality"
    assert "wrong" in data["user_answer_explanation"].lower()
    assert "correct" in data["correct_answer_explanation"].lower()

    # Verify all options with explanations are returned for learning
    assert "all_options" in data
    assert "A" in data["all_options"]
    assert "explanation" in data["all_options"]["A"]

    # Verify progress tracking
    assert data["current_index"] == 1  # Moved to next question
    assert data["total_questions"] == 2
    assert data["questions_remaining"] == 1
    assert data["session_completed"] is False

    # Verify next question is provided
    assert "next_question" in data
    assert data["next_question"] is not None
    assert data["next_question"]["question_id"] == q2.id


@pytest.mark.integration
def test_answer_wrong_question_fails(client, test_db, test_user_token):
    """
    REAL TEST: Answering wrong question in sequence should fail
    Tests: Question order validation
    """
    # Create 2 questions
    q1 = Question(question_id="SEQ1", exam_type="security", domain="1.1", question_text="Q1?", correct_answer="A",
                  options={"A": {"text": "A", "explanation": "A"}, "B": {"text": "B", "explanation": "B"}})
    q2 = Question(question_id="SEQ2", exam_type="security", domain="1.2", question_text="Q2?", correct_answer="A",
                  options={"A": {"text": "A", "explanation": "A"}, "B": {"text": "B", "explanation": "B"}})
    test_db.add_all([q1, q2])
    test_db.commit()

    # Start session
    start_response = client.post(
        "/api/v1/study/start",
        json={"exam_type": "security", "count": 2},
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    session_id = start_response.json()["session_id"]

    # Try to answer second question first (should fail)
    response = client.post(
        "/api/v1/study/answer",
        json={
            "session_id": session_id,
            "question_id": q2.id,  # Wrong question - should be q1
            "user_answer": "A"
        },
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 400
    data = response.json()
    assert "mismatch" in data["error"]["message"].lower()


# ================================================================
# STUDY MODE - COMPLETE SESSION
# ================================================================

@pytest.mark.integration
def test_complete_study_session_creates_quiz_attempt_with_study_mode(client, test_db, test_user_token, test_user):
    """
    REAL TEST: Completing study session creates quiz attempt with mode="study"
    Tests: Session completion, quiz attempt creation, mode field, XP calculation
    """
    # Create 3 questions
    questions = []
    for i in range(3):
        q = Question(
            question_id=f"COMPLETE{i}",
            exam_type="security",
            domain="1.1",
            question_text=f"Question {i}?",
            correct_answer="A",
            options={
                "A": {"text": "Correct", "explanation": "Right"},
                "B": {"text": "Wrong", "explanation": "Wrong"}
            }
        )
        test_db.add(q)
        questions.append(q)
    test_db.commit()

    # Refresh to get IDs
    for q in questions:
        test_db.refresh(q)

    # Start session
    start_response = client.post(
        "/api/v1/study/start",
        json={"exam_type": "security", "count": 3},
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    session_id = start_response.json()["session_id"]

    # Answer all questions (2 correct, 1 wrong)
    answers = ["A", "A", "B"]  # Last one is wrong
    for i, q in enumerate(questions):
        response = client.post(
            "/api/v1/study/answer",
            json={
                "session_id": session_id,
                "question_id": q.id,
                "user_answer": answers[i]
            },
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        assert response.status_code == 200

        # Last answer should complete session
        if i == len(questions) - 1:
            data = response.json()
            assert data["session_completed"] is True
            assert "completion" in data

            # Verify completion data
            completion = data["completion"]
            assert "quiz_attempt_id" in completion
            assert completion["score"] == 2  # 2 correct out of 3
            assert completion["total_questions"] == 3
            assert completion["score_percentage"] == pytest.approx(66.67, 0.1)
            assert completion["xp_earned"] > 0

    # Verify quiz attempt was created with mode="study"
    quiz_attempt = test_db.query(QuizAttempt).filter(
        QuizAttempt.user_id == test_user.id
    ).first()

    assert quiz_attempt is not None
    assert quiz_attempt.mode == "study"  # CRITICAL: mode must be "study"
    assert quiz_attempt.exam_type == "security"
    assert quiz_attempt.total_questions == 3
    assert quiz_attempt.correct_answers == 2
    assert quiz_attempt.score_percentage == pytest.approx(66.67, 0.1)

    # Verify study mode earns 75% of practice mode XP
    # Practice mode: 10 XP per correct answer = 20 XP
    # Study mode: 75% = 15 XP
    assert quiz_attempt.xp_earned == 15  # 2 correct * 10 * 0.75

    # Verify session marked as completed
    session = test_db.query(StudySession).filter(StudySession.id == session_id).first()
    assert session.is_completed is True
    assert session.completed_quiz_attempt_id == quiz_attempt.id


# ================================================================
# PRACTICE MODE - VERIFY MODE FIELD
# ================================================================

@pytest.mark.integration
def test_practice_mode_quiz_submission_sets_mode_practice(client, test_db, test_user_token, test_user):
    """
    REAL TEST: Regular quiz submission sets mode="practice"
    Tests: Practice mode mode field, backward compatibility
    """
    # Create questions
    q1 = Question(question_id="PRAC1", exam_type="security", domain="1.1", question_text="Q1?", correct_answer="A",
                  options={"A": {"text": "A", "explanation": "A"}, "B": {"text": "B", "explanation": "B"}})
    q2 = Question(question_id="PRAC2", exam_type="security", domain="1.2", question_text="Q2?", correct_answer="B",
                  options={"A": {"text": "A", "explanation": "A"}, "B": {"text": "B", "explanation": "B"}})
    test_db.add_all([q1, q2])
    test_db.commit()
    test_db.refresh(q1)
    test_db.refresh(q2)

    # Submit quiz (practice mode)
    response = client.post(
        "/api/v1/quiz/submit",
        json={
            "exam_type": "security",
            "total_questions": 2,
            "answers": [
                {
                    "question_id": q1.id,
                    "user_answer": "A",
                    "correct_answer": "A",
                    "is_correct": True
                },
                {
                    "question_id": q2.id,
                    "user_answer": "B",
                    "correct_answer": "B",
                    "is_correct": True
                }
            ],
            "time_taken_seconds": 300
        },
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 201

    # Verify quiz attempt has mode="practice"
    quiz_attempt = test_db.query(QuizAttempt).filter(
        QuizAttempt.user_id == test_user.id
    ).first()

    assert quiz_attempt is not None
    assert quiz_attempt.mode == "practice"  # CRITICAL: mode must be "practice"
    assert quiz_attempt.exam_type == "security"

    # Verify practice mode earns 100% XP with accuracy bonus
    # 2 correct * 10 = 20 base XP
    # 100% accuracy = 1.5x multiplier (+50% bonus)
    # Total: 20 * 1.5 = 30 XP
    assert quiz_attempt.xp_earned == 30


# ================================================================
# SESSION MANAGEMENT
# ================================================================

@pytest.mark.integration
def test_get_active_study_session_returns_current_session(client, test_db, test_user_token):
    """
    REAL TEST: GET /study/active returns active session for resume
    Tests: Session retrieval, resume functionality
    """
    # Create question
    q = Question(question_id="RESUME1", exam_type="security", domain="1.1", question_text="Q?", correct_answer="A",
                 options={"A": {"text": "A", "explanation": "A"}, "B": {"text": "B", "explanation": "B"}})
    test_db.add(q)
    test_db.commit()

    # Start session
    start_response = client.post(
        "/api/v1/study/start",
        json={"exam_type": "security", "count": 1},
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    session_id = start_response.json()["session_id"]

    # Get active session
    get_response = client.get(
        "/api/v1/study/active",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert get_response.status_code == 200
    data = get_response.json()
    assert data["session_id"] == session_id
    assert "current_question" in data


@pytest.mark.integration
def test_abandon_study_session_deletes_session(client, test_db, test_user_token, test_user):
    """
    REAL TEST: DELETE /study/abandon removes active session
    Tests: Session abandonment, cleanup
    """
    # Create question
    q = Question(question_id="ABANDON1", exam_type="security", domain="1.1", question_text="Q?", correct_answer="A",
                 options={"A": {"text": "A", "explanation": "A"}, "B": {"text": "B", "explanation": "B"}})
    test_db.add(q)
    test_db.commit()

    # Start session
    start_response = client.post(
        "/api/v1/study/start",
        json={"exam_type": "security", "count": 1},
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    session_id = start_response.json()["session_id"]

    # Abandon session
    abandon_response = client.delete(
        "/api/v1/study/abandon",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert abandon_response.status_code == 200
    data = abandon_response.json()
    assert data["success"] is True

    # Verify session deleted from database
    session = test_db.query(StudySession).filter(StudySession.id == session_id).first()
    assert session is None


# ================================================================
# XP CALCULATION DIFFERENCES
# ================================================================

@pytest.mark.integration
def test_study_mode_earns_75_percent_xp_compared_to_practice(client, test_db, test_user_token, test_user):
    """
    REAL TEST: Study mode earns 75% of practice mode XP (since it's easier)
    Tests: XP calculation differences between modes
    """
    # Create 5 questions
    for i in range(5):
        q = Question(
            question_id=f"XP{i}",
            exam_type="security",
            domain="1.1",
            question_text=f"Q{i}?",
            correct_answer="A",
            options={"A": {"text": "A", "explanation": "A"}, "B": {"text": "B", "explanation": "B"}}
        )
        test_db.add(q)
    test_db.commit()

    questions = test_db.query(Question).filter(Question.exam_type == "security").all()[:5]

    # Study mode: Complete session with 4/5 correct
    start_response = client.post(
        "/api/v1/study/start",
        json={"exam_type": "security", "count": 5},
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    session_id = start_response.json()["session_id"]

    answers = ["A", "A", "A", "A", "B"]  # 4 correct, 1 wrong
    for i, q in enumerate(questions):
        client.post(
            "/api/v1/study/answer",
            json={"session_id": session_id, "question_id": q.id, "user_answer": answers[i]},
            headers={"Authorization": f"Bearer {test_user_token}"}
        )

    # Get study mode attempt
    study_attempt = test_db.query(QuizAttempt).filter(
        QuizAttempt.user_id == test_user.id,
        QuizAttempt.mode == "study"
    ).first()

    # Study mode: 4 correct * 10 * 0.75 = 30 XP
    assert study_attempt.xp_earned == 30

    # Practice mode: Submit quiz with 4/5 correct
    practice_response = client.post(
        "/api/v1/quiz/submit",
        json={
            "exam_type": "security",
            "total_questions": 5,
            "answers": [
                {"question_id": q.id, "user_answer": "A" if i < 4 else "B", "correct_answer": "A", "is_correct": i < 4}
                for i, q in enumerate(questions)
            ]
        },
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    # Get practice mode attempt
    practice_attempt = test_db.query(QuizAttempt).filter(
        QuizAttempt.user_id == test_user.id,
        QuizAttempt.mode == "practice"
    ).first()

    # Practice mode: 4 correct * 10 = 40 base XP
    # 80% accuracy = 1.25x multiplier (+25% bonus)
    # Total: 40 * 1.25 = 50 XP
    assert practice_attempt.xp_earned == 50

    # Verify study mode uses simple 75% calculation (no accuracy bonus)
    # Study: 4 * 10 * 0.75 = 30 XP
    # Practice: 4 * 10 * 1.25 = 50 XP (with 80% accuracy bonus)
    # Study mode earns 75% of BASE XP, not final XP with bonuses
    assert study_attempt.xp_earned == 30
    assert practice_attempt.xp_earned == 50


# ================================================================
# EDGE CASES
# ================================================================

@pytest.mark.integration
def test_cannot_answer_after_session_completed(client, test_db, test_user_token):
    """
    REAL TEST: Cannot answer questions after session is complete
    Tests: Session state validation
    """
    # Create 1 question
    q = Question(question_id="DONE1", exam_type="security", domain="1.1", question_text="Q?", correct_answer="A",
                 options={"A": {"text": "A", "explanation": "A"}, "B": {"text": "B", "explanation": "B"}})
    test_db.add(q)
    test_db.commit()
    test_db.refresh(q)

    # Start and complete session
    start_response = client.post(
        "/api/v1/study/start",
        json={"exam_type": "security", "count": 1},
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    session_id = start_response.json()["session_id"]

    # Answer question (completes session)
    client.post(
        "/api/v1/study/answer",
        json={"session_id": session_id, "question_id": q.id, "user_answer": "A"},
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    # Try to answer again (should fail)
    response = client.post(
        "/api/v1/study/answer",
        json={"session_id": session_id, "question_id": q.id, "user_answer": "A"},
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 400
    data = response.json()
    assert "already completed" in data["error"]["message"].lower()


@pytest.mark.integration
def test_invalid_session_id_returns_404(client, test_user_token):
    """
    REAL TEST: Invalid session ID returns 404
    Tests: Session validation
    """
    response = client.post(
        "/api/v1/study/answer",
        json={"session_id": 99999, "question_id": 1, "user_answer": "A"},
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["error"]["message"].lower()
