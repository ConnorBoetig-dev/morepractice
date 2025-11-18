"""
QUIZ SERVICE
Business logic for quiz submission and tracking

Enterprise features:
- Atomic transactions (all-or-nothing operations)
- Bulk inserts for performance
- XP and level calculation
- Achievement unlock integration
"""

from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Tuple
import math

from app.models.gamification import QuizAttempt, UserAnswer
from app.models.user import UserProfile
from app.schemas.quiz import QuizSubmission, AnswerSubmission


# ================================================================
# XP & LEVEL CALCULATION
# ================================================================

def calculate_xp_earned(correct_answers: int, total_questions: int, exam_type: str) -> int:
    """
    Calculate XP earned from a quiz

    Formula:
    - Base XP: 10 XP per correct answer
    - Accuracy bonus: +50% if score >= 90%, +25% if >= 80%, +10% if >= 70%

    Args:
        correct_answers: Number of correct answers
        total_questions: Total number of questions
        exam_type: Type of exam (currently unused, could apply multipliers later)

    Returns:
        Total XP earned (integer)
    """
    # Base XP: 10 per correct answer
    base_xp = correct_answers * 10

    # Calculate accuracy percentage
    accuracy = (correct_answers / total_questions) * 100 if total_questions > 0 else 0

    # Accuracy bonus
    if accuracy >= 90:
        bonus_multiplier = 1.5  # +50%
    elif accuracy >= 80:
        bonus_multiplier = 1.25  # +25%
    elif accuracy >= 70:
        bonus_multiplier = 1.10  # +10%
    else:
        bonus_multiplier = 1.0  # No bonus

    total_xp = int(base_xp * bonus_multiplier)
    return total_xp


def calculate_level_from_xp(xp: int) -> int:
    """
    Calculate level from total XP

    Formula: level = floor(sqrt(xp / 100)) + 1
    - Level 1: 0-99 XP
    - Level 2: 100-399 XP
    - Level 3: 400-899 XP
    - Level 4: 900-1599 XP
    - Level 5: 1600-2499 XP
    - etc.

    This creates a gradually increasing XP requirement per level

    Args:
        xp: Total XP

    Returns:
        Current level (minimum 1)
    """
    if xp < 0:
        return 1

    level = int(math.sqrt(xp / 100)) + 1
    return max(1, level)  # Minimum level is 1


# ================================================================
# QUIZ SUBMISSION
# ================================================================

def submit_quiz(
    db: Session,
    user_id: int,
    submission: QuizSubmission
) -> Tuple[QuizAttempt, int, int, bool]:
    """
    Submit a completed quiz and track all answers

    This is an ATOMIC operation - either all data is saved or none is.

    Process:
    1. Create QuizAttempt record
    2. Bulk insert UserAnswer records (performance optimization)
    3. Calculate XP earned
    4. Update user profile (XP, level, counters)
    5. Check for level up

    Args:
        db: Database session
        user_id: ID of user submitting quiz
        submission: Quiz submission data from frontend

    Returns:
        Tuple of (quiz_attempt, xp_earned, new_level, level_up)

    Raises:
        Exception: If database operation fails (transaction will rollback)
    """
    try:
        # Step 1: Calculate score
        correct_answers = sum(1 for answer in submission.answers if answer.is_correct)
        score_percentage = (correct_answers / submission.total_questions) * 100

        # Step 2: Calculate XP earned
        xp_earned = calculate_xp_earned(correct_answers, submission.total_questions, submission.exam_type)

        # Step 3: Create QuizAttempt record
        quiz_attempt = QuizAttempt(
            user_id=user_id,
            exam_type=submission.exam_type,
            total_questions=submission.total_questions,
            correct_answers=correct_answers,
            score_percentage=score_percentage,
            time_taken_seconds=submission.time_taken_seconds,
            xp_earned=xp_earned,
            completed_at=datetime.utcnow()
        )
        db.add(quiz_attempt)
        db.flush()  # Get quiz_attempt.id without committing

        # Step 4: Bulk create UserAnswer records (performance optimization)
        # Creating list first, then bulk insert is faster than individual inserts
        user_answers = [
            UserAnswer(
                user_id=user_id,
                quiz_attempt_id=quiz_attempt.id,
                question_id=answer.question_id,
                user_answer=answer.user_answer,
                correct_answer=answer.correct_answer,
                is_correct=answer.is_correct,
                time_spent_seconds=answer.time_spent_seconds,
                answered_at=datetime.utcnow()
            )
            for answer in submission.answers
        ]
        db.bulk_save_objects(user_answers)

        # Step 5: Update user profile
        # Get current profile (should always exist from signup)
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

        if not profile:
            # Safety check - create profile if it doesn't exist
            profile = UserProfile(user_id=user_id, xp=0, level=1)
            db.add(profile)
            db.flush()

        # Store previous level for level_up detection
        previous_level = profile.level

        # Update profile stats
        profile.xp += xp_earned
        profile.total_exams_taken = (profile.total_exams_taken or 0) + 1
        profile.total_questions_answered = (profile.total_questions_answered or 0) + submission.total_questions

        # Calculate new level from total XP
        new_level = calculate_level_from_xp(profile.xp)
        profile.level = new_level

        # Check if user leveled up
        level_up = new_level > previous_level

        # Commit all changes atomically
        db.commit()
        db.refresh(quiz_attempt)  # Refresh to get final state

        return quiz_attempt, xp_earned, new_level, level_up

    except Exception as e:
        # Rollback on any error to maintain data consistency
        db.rollback()
        raise e


# ================================================================
# QUIZ HISTORY
# ================================================================

def get_user_quiz_history(
    db: Session,
    user_id: int,
    limit: int = 20,
    offset: int = 0,
    exam_type: str = None
) -> List[QuizAttempt]:
    """
    Get user's quiz attempt history with pagination

    Args:
        db: Database session
        user_id: User ID
        limit: Maximum number of attempts to return
        offset: Number of attempts to skip (for pagination)
        exam_type: Optional filter by exam type

    Returns:
        List of QuizAttempt records (most recent first)
    """
    query = db.query(QuizAttempt).filter(QuizAttempt.user_id == user_id)

    # Optional filter by exam type
    if exam_type:
        query = query.filter(QuizAttempt.exam_type == exam_type)

    # Order by most recent first
    query = query.order_by(QuizAttempt.completed_at.desc())

    # Apply pagination
    query = query.limit(limit).offset(offset)

    return query.all()


def get_quiz_attempt_details(db: Session, quiz_attempt_id: int, user_id: int) -> QuizAttempt:
    """
    Get detailed quiz attempt including all answers

    Args:
        db: Database session
        quiz_attempt_id: ID of quiz attempt
        user_id: User ID (for authorization check)

    Returns:
        QuizAttempt with answers relationship loaded

    Raises:
        ValueError: If quiz attempt not found or doesn't belong to user
    """
    attempt = db.query(QuizAttempt).filter(
        QuizAttempt.id == quiz_attempt_id,
        QuizAttempt.user_id == user_id
    ).first()

    if not attempt:
        raise ValueError("Quiz attempt not found or access denied")

    return attempt


# ================================================================
# STATISTICS
# ================================================================

def get_user_quiz_stats(db: Session, user_id: int) -> dict:
    """
    Get aggregated quiz statistics for a user

    Returns:
        Dictionary with:
        - total_attempts: Total quizzes taken
        - total_questions_answered: Total questions answered
        - average_score: Average score percentage across all quizzes
        - best_score: Highest score percentage
        - total_xp_earned: Total XP from quizzes
        - stats_by_exam: Breakdown by exam type
    """
    from sqlalchemy import func

    attempts = db.query(QuizAttempt).filter(QuizAttempt.user_id == user_id).all()

    if not attempts:
        return {
            "total_attempts": 0,
            "total_questions_answered": 0,
            "average_score": 0.0,
            "best_score": 0.0,
            "total_xp_earned": 0,
            "stats_by_exam": {}
        }

    total_xp = sum(a.xp_earned for a in attempts)
    total_questions = sum(a.total_questions for a in attempts)
    avg_score = sum(a.score_percentage for a in attempts) / len(attempts)
    best_score = max(a.score_percentage for a in attempts)

    # Group by exam type
    stats_by_exam = {}
    for attempt in attempts:
        exam = attempt.exam_type
        if exam not in stats_by_exam:
            stats_by_exam[exam] = {
                "attempts": 0,
                "questions_answered": 0,
                "average_score": 0.0,
                "best_score": 0.0,
                "xp_earned": 0
            }

        stats_by_exam[exam]["attempts"] += 1
        stats_by_exam[exam]["questions_answered"] += attempt.total_questions
        stats_by_exam[exam]["xp_earned"] += attempt.xp_earned

    # Calculate averages for each exam type
    for exam, stats in stats_by_exam.items():
        exam_attempts = [a for a in attempts if a.exam_type == exam]
        stats["average_score"] = sum(a.score_percentage for a in exam_attempts) / len(exam_attempts)
        stats["best_score"] = max(a.score_percentage for a in exam_attempts)

    return {
        "total_attempts": len(attempts),
        "total_questions_answered": total_questions,
        "average_score": round(avg_score, 2),
        "best_score": round(best_score, 2),
        "total_xp_earned": total_xp,
        "stats_by_exam": stats_by_exam
    }
