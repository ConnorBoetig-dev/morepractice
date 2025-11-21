"""
STUDY MODE SERVICE LAYER
Database operations for study mode (one question at a time with immediate feedback)

Study mode workflow:
1. Start session → get first question
2. Answer question → get immediate feedback + next question
3. Repeat until all questions answered
4. Complete session → convert to quiz attempt

Functions:
- start_study_session: Create study session and get first question
- answer_study_question: Submit answer, get feedback, get next question
- complete_study_session: Finalize session and create quiz attempt
- get_active_study_session: Get user's active session
- cleanup_abandoned_sessions: Clean up old incomplete sessions
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timedelta
from typing import Optional, List, Tuple
from fastapi import HTTPException, status

from app.models.gamification import StudySession, UserAnswer, QuizAttempt
from app.models.question import Question
from app.models.user import UserProfile
from app.utils.logger import get_logger

logger = get_logger(__name__)


def start_study_session(
    db: Session,
    user_id: int,
    exam_type: str,
    count: int,
    domain: Optional[str] = None
) -> Tuple[StudySession, Question]:
    """
    Start a new study mode session

    Args:
        db: Database session
        user_id: User ID
        exam_type: Exam type (security, network, etc.)
        count: Number of questions
        domain: Optional domain filter

    Returns:
        Tuple of (StudySession, first_question)

    Raises:
        HTTPException: If user has active session or no questions available
    """
    # Check for existing active session
    existing_session = db.query(StudySession).filter(
        and_(
            StudySession.user_id == user_id,
            StudySession.is_completed == False
        )
    ).first()

    if existing_session:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "You have an active study session. Complete or abandon it first.",
                "code": "ACTIVE_SESSION_EXISTS"
            }
        )

    # Get random questions
    query = db.query(Question).filter(Question.exam_type == exam_type)
    if domain:
        query = query.filter(Question.domain == domain)

    questions = query.order_by(Question.id).limit(count).all()

    if not questions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": f"No questions found for exam type '{exam_type}'" + (f" and domain '{domain}'" if domain else ""),
                "code": "QUESTION_NOT_FOUND"
            }
        )

    if len(questions) < count:
        logger.warning(
            f"Requested {count} questions but only {len(questions)} available for {exam_type}" +
            (f" domain {domain}" if domain else "")
        )

    # Create study session
    question_ids = ",".join(str(q.id) for q in questions)
    session = StudySession(
        user_id=user_id,
        exam_type=exam_type,
        question_ids=question_ids,
        current_index=0,
        is_completed=False
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    logger.info(f"Started study session {session.id} for user {user_id}: {len(questions)} questions")

    return session, questions[0]


def answer_study_question(
    db: Session,
    session_id: int,
    user_id: int,
    question_id: int,
    user_answer: str
) -> Tuple[bool, Question, Optional[Question], bool]:
    """
    Submit answer for current question in study session

    Args:
        db: Database session
        session_id: Study session ID
        user_id: User ID
        question_id: Question being answered
        user_answer: User's selected answer (A, B, C, D)

    Returns:
        Tuple of (is_correct, current_question, next_question, session_completed)

    Raises:
        HTTPException: If session not found, not active, or question mismatch
    """
    # Get study session
    session = db.query(StudySession).filter(
        and_(
            StudySession.id == session_id,
            StudySession.user_id == user_id
        )
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Study session not found",
                "code": "RESOURCE_NOT_FOUND"
            }
        )

    if session.is_completed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Study session already completed",
                "code": "INVALID_INPUT"
            }
        )

    # Parse question IDs
    question_ids = [int(qid) for qid in session.question_ids.split(",")]

    # Verify question is the current one
    if session.current_index >= len(question_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "All questions already answered",
                "code": "INVALID_INPUT"
            }
        )

    current_question_id = question_ids[session.current_index]
    if current_question_id != question_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Question mismatch. Expected question {current_question_id}, got {question_id}",
                "code": "INVALID_INPUT"
            }
        )

    # Get current question
    current_question = db.query(Question).filter(Question.id == question_id).first()
    if not current_question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Question not found",
                "code": "QUESTION_NOT_FOUND"
            }
        )

    # Check if correct
    is_correct = user_answer == current_question.correct_answer

    # Create temporary user answer (will be attached to quiz attempt later)
    # For now, we'll store it when completing the session

    # Move to next question
    session.current_index += 1
    db.commit()

    # Check if session completed
    session_completed = session.current_index >= len(question_ids)

    # Get next question if not completed
    next_question = None
    if not session_completed:
        next_question_id = question_ids[session.current_index]
        next_question = db.query(Question).filter(Question.id == next_question_id).first()

    logger.info(
        f"Study session {session_id}: Question {session.current_index}/{len(question_ids)} answered " +
        f"({'correct' if is_correct else 'incorrect'})"
    )

    return is_correct, current_question, next_question, session_completed


def complete_study_session(
    db: Session,
    session_id: int,
    user_id: int,
    answers: List[Tuple[int, str, bool]]  # [(question_id, user_answer, is_correct), ...]
) -> QuizAttempt:
    """
    Complete study session and convert to quiz attempt

    Args:
        db: Database session
        session_id: Study session ID
        user_id: User ID
        answers: List of (question_id, user_answer, is_correct) tuples

    Returns:
        Created QuizAttempt

    Raises:
        HTTPException: If session not found or already completed
    """
    # Get study session
    session = db.query(StudySession).filter(
        and_(
            StudySession.id == session_id,
            StudySession.user_id == user_id
        )
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Study session not found",
                "code": "RESOURCE_NOT_FOUND"
            }
        )

    if session.is_completed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Study session already completed",
                "code": "INVALID_INPUT"
            }
        )

    # Calculate score
    total_questions = len(answers)
    correct_answers = sum(1 for _, _, is_correct in answers if is_correct)
    score_percentage = (correct_answers / total_questions * 100) if total_questions > 0 else 0

    # Calculate XP (study mode earns 75% of practice mode XP since it's easier)
    base_xp = 10
    xp_earned = int(correct_answers * base_xp * 0.75)

    # Create quiz attempt
    quiz_attempt = QuizAttempt(
        user_id=user_id,
        exam_type=session.exam_type,
        mode="study",
        total_questions=total_questions,
        correct_answers=correct_answers,
        score_percentage=score_percentage,
        time_taken_seconds=None,  # Not tracked in study mode
        xp_earned=xp_earned
    )

    db.add(quiz_attempt)
    db.flush()  # Get quiz_attempt.id

    # Create user answers
    for question_id, user_answer, is_correct in answers:
        question = db.query(Question).filter(Question.id == question_id).first()
        user_answer_record = UserAnswer(
            user_id=user_id,
            quiz_attempt_id=quiz_attempt.id,
            question_id=question_id,
            user_answer=user_answer,
            correct_answer=question.correct_answer if question else None,
            is_correct=is_correct
        )
        db.add(user_answer_record)

    # Update user profile XP
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if profile:
        old_level = profile.level
        profile.xp += xp_earned
        profile.total_exams_taken += 1

        # Simple level calculation: level = floor(xp / 100)
        new_level = profile.xp // 100
        profile.level = new_level

    # Mark session as completed
    session.is_completed = True
    session.completed_at = datetime.utcnow()
    session.completed_quiz_attempt_id = quiz_attempt.id

    db.commit()
    db.refresh(quiz_attempt)

    logger.info(
        f"Completed study session {session_id}: {correct_answers}/{total_questions} correct, " +
        f"{xp_earned} XP earned"
    )

    return quiz_attempt


def get_active_study_session(db: Session, user_id: int) -> Optional[StudySession]:
    """
    Get user's active study session if exists

    Args:
        db: Database session
        user_id: User ID

    Returns:
        Active StudySession or None
    """
    return db.query(StudySession).filter(
        and_(
            StudySession.user_id == user_id,
            StudySession.is_completed == False
        )
    ).first()


def cleanup_abandoned_sessions(db: Session, hours: int = 24):
    """
    Clean up abandoned study sessions older than specified hours

    Args:
        db: Database session
        hours: Hours threshold for abandonment (default 24)
    """
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)

    abandoned_sessions = db.query(StudySession).filter(
        and_(
            StudySession.is_completed == False,
            StudySession.started_at < cutoff_time
        )
    ).all()

    count = len(abandoned_sessions)
    if count > 0:
        for session in abandoned_sessions:
            db.delete(session)
        db.commit()
        logger.info(f"Cleaned up {count} abandoned study sessions")

    return count
