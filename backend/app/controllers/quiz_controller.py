"""
QUIZ CONTROLLER
Orchestrates quiz submission and history operations

Sits between routes and services:
- Routes handle HTTP concerns (authentication, validation)
- Controller handles business logic orchestration
- Services handle database operations
"""

from sqlalchemy.orm import Session
from typing import List

from app.schemas.quiz import (
    QuizSubmission,
    QuizSubmissionResponse,
    AchievementUnlocked,
    QuizHistoryResponse,
    QuizAttemptSummary
)
from app.services import quiz_service, achievement_service
from app.models.user import UserProfile


def submit_quiz(db: Session, user_id: int, submission: QuizSubmission) -> QuizSubmissionResponse:
    """
    Handle quiz submission

    Process:
    1. Save quiz attempt and answers (via service)
    2. Get updated user profile
    3. Check for newly unlocked achievements (Phase 3)
    4. Build comprehensive response

    Args:
        db: Database session
        user_id: ID of authenticated user
        submission: Quiz submission data

    Returns:
        QuizSubmissionResponse with results, XP, level, and achievements

    Raises:
        Exception: If submission fails
    """
    # Submit quiz and get results
    quiz_attempt, xp_earned, new_level, level_up = quiz_service.submit_quiz(
        db, user_id, submission
    )

    # Get updated user profile for total XP
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

    # Check for newly unlocked achievements
    achievements_unlocked = achievement_service.check_and_award_achievements(
        db, user_id, exam_type=submission.exam_type
    )

    # Build response
    return QuizSubmissionResponse(
        quiz_attempt_id=quiz_attempt.id,
        score=quiz_attempt.correct_answers,
        total_questions=quiz_attempt.total_questions,
        score_percentage=quiz_attempt.score_percentage,
        xp_earned=xp_earned,
        total_xp=profile.xp,
        current_level=new_level,
        previous_level=new_level - 1 if level_up else new_level,
        level_up=level_up,
        achievements_unlocked=achievements_unlocked
    )


def get_quiz_history(
    db: Session,
    user_id: int,
    limit: int = 20,
    offset: int = 0,
    exam_type: str = None
) -> QuizHistoryResponse:
    """
    Get user's quiz history with pagination

    Args:
        db: Database session
        user_id: ID of authenticated user
        limit: Max attempts to return
        offset: Pagination offset
        exam_type: Optional filter by exam type

    Returns:
        QuizHistoryResponse with attempts list and total count
    """
    # Get quiz attempts
    attempts = quiz_service.get_user_quiz_history(db, user_id, limit, offset, exam_type)

    # Convert to response schema
    attempt_summaries = [
        QuizAttemptSummary(
            id=attempt.id,
            exam_type=attempt.exam_type,
            total_questions=attempt.total_questions,
            correct_answers=attempt.correct_answers,
            score_percentage=attempt.score_percentage,
            xp_earned=attempt.xp_earned,
            time_taken_seconds=attempt.time_taken_seconds,
            completed_at=attempt.completed_at
        )
        for attempt in attempts
    ]

    # Get total count (for pagination info)
    from app.models.gamification import QuizAttempt
    total_query = db.query(QuizAttempt).filter(QuizAttempt.user_id == user_id)
    if exam_type:
        total_query = total_query.filter(QuizAttempt.exam_type == exam_type)
    total_attempts = total_query.count()

    return QuizHistoryResponse(
        total_attempts=total_attempts,
        attempts=attempt_summaries
    )


def get_quiz_stats(db: Session, user_id: int) -> dict:
    """
    Get aggregated quiz statistics for user

    Args:
        db: Database session
        user_id: ID of authenticated user

    Returns:
        Dictionary with quiz statistics
    """
    return quiz_service.get_user_quiz_stats(db, user_id)
