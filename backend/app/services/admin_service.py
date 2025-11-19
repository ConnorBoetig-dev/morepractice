"""
ADMIN SERVICE
Database operations for admin panel functionality

Handles:
- Question CRUD operations
- User management queries
- Achievement management
- Admin analytics
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import List, Optional, Tuple
from datetime import datetime
import math

from app.models.question import Question
from app.models.user import User, UserProfile, Session, AuditLog
from app.models.gamification import Achievement, QuizAttempt, UserAchievement, UserAnswer
from app.schemas.admin import QuestionCreate, QuestionUpdate


# ================================================================
# QUESTION MANAGEMENT
# ================================================================

def get_questions_paginated(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    exam_type: Optional[str] = None,
    domain: Optional[str] = None,
    search: Optional[str] = None
) -> Tuple[List[Question], int]:
    """
    Get paginated list of questions with optional filters

    Args:
        db: Database session
        page: Page number (1-indexed)
        page_size: Items per page
        exam_type: Optional filter by exam type
        domain: Optional filter by domain
        search: Optional search in question text

    Returns:
        Tuple of (questions list, total count)
    """
    # Build query with filters
    query = db.query(Question)

    if exam_type:
        query = query.filter(Question.exam_type == exam_type)

    if domain:
        query = query.filter(Question.domain == domain)

    if search:
        # Search in question text (case-insensitive)
        query = query.filter(Question.question_text.ilike(f"%{search}%"))

    # Get total count before pagination
    total = query.count()

    # Apply pagination
    offset = (page - 1) * page_size
    questions = query.order_by(Question.created_at.desc())\
        .offset(offset)\
        .limit(page_size)\
        .all()

    return questions, total


def get_question_by_id(db: Session, question_id: int) -> Optional[Question]:
    """
    Get a specific question by database ID

    Args:
        db: Database session
        question_id: Database ID

    Returns:
        Question object or None if not found
    """
    return db.query(Question).filter(Question.id == question_id).first()


def create_question(db: Session, question_data: QuestionCreate) -> Question:
    """
    Create a new question

    Args:
        db: Database session
        question_data: Question creation data

    Returns:
        Created Question object
    """
    # Convert Pydantic models to dict for JSON storage
    options_dict = {
        key: {"text": option.text, "explanation": option.explanation}
        for key, option in question_data.options.items()
    }

    # Create new question
    new_question = Question(
        question_id=question_data.question_id,
        exam_type=question_data.exam_type,
        domain=question_data.domain,
        question_text=question_data.question_text,
        correct_answer=question_data.correct_answer,
        options=options_dict,
        created_at=datetime.utcnow()
    )

    db.add(new_question)
    db.commit()
    db.refresh(new_question)

    return new_question


def update_question(
    db: Session,
    question_id: int,
    question_data: QuestionUpdate
) -> Optional[Question]:
    """
    Update an existing question

    Args:
        db: Database session
        question_id: Database ID of question to update
        question_data: Updated question data (only provided fields will be updated)

    Returns:
        Updated Question object or None if not found
    """
    question = db.query(Question).filter(Question.id == question_id).first()

    if not question:
        return None

    # Update only provided fields
    update_data = question_data.model_dump(exclude_unset=True)

    # Special handling for options (convert Pydantic models to dict)
    if 'options' in update_data and update_data['options'] is not None:
        options_dict = {
            key: {"text": option.text, "explanation": option.explanation}
            for key, option in question_data.options.items()
        }
        update_data['options'] = options_dict

    # Apply updates
    for key, value in update_data.items():
        setattr(question, key, value)

    db.commit()
    db.refresh(question)

    return question


def delete_question(db: Session, question_id: int) -> bool:
    """
    Delete a question

    Args:
        db: Database session
        question_id: Database ID of question to delete

    Returns:
        True if deleted, False if not found
    """
    question = db.query(Question).filter(Question.id == question_id).first()

    if not question:
        return False

    db.delete(question)
    db.commit()

    return True


def bulk_import_questions(db: Session, questions_data: List[QuestionCreate]) -> Tuple[int, List[str]]:
    """
    Bulk import multiple questions

    Args:
        db: Database session
        questions_data: List of question creation data

    Returns:
        Tuple of (success_count, error_messages)
    """
    success_count = 0
    errors = []

    for idx, question_data in enumerate(questions_data):
        try:
            create_question(db, question_data)
            success_count += 1
        except Exception as e:
            errors.append(f"Question {idx + 1} (ID: {question_data.question_id}): {str(e)}")

    return success_count, errors


# ================================================================
# USER MANAGEMENT
# ================================================================

def get_users_paginated(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    search: Optional[str] = None,
    is_admin: Optional[bool] = None,
    is_verified: Optional[bool] = None
) -> Tuple[List[Tuple[User, UserProfile]], int]:
    """
    Get paginated list of users with their profiles

    Args:
        db: Database session
        page: Page number (1-indexed)
        page_size: Items per page
        search: Optional search in username or email
        is_admin: Optional filter by admin status
        is_verified: Optional filter by verification status

    Returns:
        Tuple of (user+profile tuples list, total count)
    """
    # Build query with join
    query = db.query(User, UserProfile).join(UserProfile, User.id == UserProfile.user_id)

    # Apply filters
    if search:
        query = query.filter(
            or_(
                User.username.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%")
            )
        )

    if is_admin is not None:
        query = query.filter(User.is_admin == is_admin)

    if is_verified is not None:
        query = query.filter(User.is_verified == is_verified)

    # Get total count
    total = query.count()

    # Apply pagination
    offset = (page - 1) * page_size
    users = query.order_by(User.created_at.desc())\
        .offset(offset)\
        .limit(page_size)\
        .all()

    return users, total


def get_user_details(db: Session, user_id: int) -> Optional[Tuple[User, UserProfile, dict]]:
    """
    Get detailed user information including stats

    Args:
        db: Database session
        user_id: User ID

    Returns:
        Tuple of (User, UserProfile, stats_dict) or None if not found
    """
    # Get user and profile
    result = db.query(User, UserProfile)\
        .join(UserProfile, User.id == UserProfile.user_id)\
        .filter(User.id == user_id)\
        .first()

    if not result:
        return None

    user, profile = result

    # Calculate stats
    total_quizzes = db.query(func.count(QuizAttempt.id))\
        .filter(QuizAttempt.user_id == user_id)\
        .scalar() or 0

    total_achievements = db.query(func.count(UserAchievement.user_id))\
        .filter(UserAchievement.user_id == user_id)\
        .scalar() or 0

    stats = {
        "total_quizzes_completed": total_quizzes,
        "total_achievements_earned": total_achievements
    }

    return user, profile, stats


def toggle_user_admin(db: Session, user_id: int) -> Optional[User]:
    """
    Toggle user's admin status

    Args:
        db: Database session
        user_id: User ID

    Returns:
        Updated User or None if not found
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        return None

    user.is_admin = not user.is_admin
    db.commit()
    db.refresh(user)

    return user


def toggle_user_active(db: Session, user_id: int) -> Optional[User]:
    """
    Toggle user's active status (ban/unban)

    Args:
        db: Database session
        user_id: User ID

    Returns:
        Updated User or None if not found
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        return None

    user.is_active = not user.is_active
    db.commit()
    db.refresh(user)

    return user


def delete_user(db: Session, user_id: int) -> bool:
    """
    Delete a user and all their data

    Args:
        db: Database session
        user_id: User ID

    Returns:
        True if deleted, False if not found
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        return False

    # Manually delete related records (in case CASCADE isn't set up)
    # Delete user profile
    db.query(UserProfile).filter(UserProfile.user_id == user_id).delete()

    # Delete user achievements
    db.query(UserAchievement).filter(UserAchievement.user_id == user_id).delete()

    # Delete quiz attempts (will cascade to user_answers)
    db.query(QuizAttempt).filter(QuizAttempt.user_id == user_id).delete()

    # Delete sessions
    db.query(Session).filter(Session.user_id == user_id).delete()

    # Delete audit logs
    db.query(AuditLog).filter(AuditLog.user_id == user_id).delete()

    # Delete user avatars
    from app.models.gamification import UserAvatar
    db.query(UserAvatar).filter(UserAvatar.user_id == user_id).delete()

    # Finally delete the user
    db.delete(user)
    db.commit()

    return True


# ================================================================
# ACHIEVEMENT MANAGEMENT
# ================================================================

def get_all_achievements(db: Session) -> List[Achievement]:
    """
    Get all achievements (including hidden)

    Args:
        db: Database session

    Returns:
        List of all achievements
    """
    return db.query(Achievement).order_by(Achievement.created_at.desc()).all()


def get_achievement_by_id(db: Session, achievement_id: int) -> Optional[Achievement]:
    """
    Get achievement by ID

    Args:
        db: Database session
        achievement_id: Achievement ID

    Returns:
        Achievement or None if not found
    """
    return db.query(Achievement).filter(Achievement.id == achievement_id).first()


def create_achievement(db: Session, achievement_data: dict) -> Achievement:
    """
    Create a new achievement

    Args:
        db: Database session
        achievement_data: Achievement data dictionary

    Returns:
        Created Achievement
    """
    new_achievement = Achievement(**achievement_data)
    db.add(new_achievement)
    db.commit()
    db.refresh(new_achievement)

    return new_achievement


def update_achievement(db: Session, achievement_id: int, achievement_data: dict) -> Optional[Achievement]:
    """
    Update an achievement

    Args:
        db: Database session
        achievement_id: Achievement ID
        achievement_data: Updated data (only provided fields)

    Returns:
        Updated Achievement or None if not found
    """
    achievement = db.query(Achievement).filter(Achievement.id == achievement_id).first()

    if not achievement:
        return None

    for key, value in achievement_data.items():
        if value is not None:
            setattr(achievement, key, value)

    db.commit()
    db.refresh(achievement)

    return achievement


def delete_achievement(db: Session, achievement_id: int) -> bool:
    """
    Delete an achievement

    Args:
        db: Database session
        achievement_id: Achievement ID

    Returns:
        True if deleted, False if not found
    """
    achievement = db.query(Achievement).filter(Achievement.id == achievement_id).first()

    if not achievement:
        return False

    db.delete(achievement)
    db.commit()

    return True


# ================================================================
# ACTIVITY & AUDIT TRACKING
# ================================================================

def get_user_activity(
    db: Session,
    user_id: int,
    limit: int = 50
) -> dict:
    """
    Get comprehensive activity data for a specific user

    Args:
        db: Database session
        user_id: User ID
        limit: Max items per activity type

    Returns:
        Dictionary with all activity data
    """
    # Quiz attempts
    quiz_attempts = db.query(QuizAttempt)\
        .filter(QuizAttempt.user_id == user_id)\
        .order_by(QuizAttempt.completed_at.desc())\
        .limit(limit)\
        .all()

    # Achievements earned
    achievements_earned = db.query(UserAchievement, Achievement)\
        .join(Achievement, UserAchievement.achievement_id == Achievement.id)\
        .filter(UserAchievement.user_id == user_id)\
        .order_by(UserAchievement.earned_at.desc())\
        .limit(limit)\
        .all()

    # Active sessions
    active_sessions = db.query(Session)\
        .filter(Session.user_id == user_id, Session.is_active == True)\
        .order_by(Session.last_active.desc())\
        .all()

    # Audit logs (auth events)
    audit_logs = db.query(AuditLog)\
        .filter(AuditLog.user_id == user_id)\
        .order_by(AuditLog.timestamp.desc())\
        .limit(limit)\
        .all()

    return {
        "quiz_attempts": quiz_attempts,
        "achievements_earned": achievements_earned,
        "active_sessions": active_sessions,
        "audit_logs": audit_logs
    }


def get_global_activity_feed(
    db: Session,
    page: int = 1,
    page_size: int = 50,
    activity_type: Optional[str] = None
) -> Tuple[List[dict], int]:
    """
    Get global activity feed across all users

    Args:
        db: Database session
        page: Page number
        page_size: Items per page
        activity_type: Filter by type (quiz, achievement, login, etc.)

    Returns:
        Tuple of (activity list, total count)
    """
    offset = (page - 1) * page_size
    activities = []

    # Collect different activity types
    if not activity_type or activity_type == "quiz":
        quizzes = db.query(QuizAttempt, User)\
            .join(User, QuizAttempt.user_id == User.id)\
            .order_by(QuizAttempt.completed_at.desc())\
            .limit(page_size if activity_type == "quiz" else page_size // 4)\
            .offset(offset if activity_type == "quiz" else 0)\
            .all()

        for attempt, user in quizzes:
            activities.append({
                "type": "quiz",
                "timestamp": attempt.completed_at,
                "user_id": user.id,
                "username": user.username,
                "details": {
                    "exam_type": attempt.exam_type,
                    "score": attempt.score_percentage,
                    "xp_earned": attempt.xp_earned
                }
            })

    if not activity_type or activity_type == "achievement":
        achievements = db.query(UserAchievement, User, Achievement)\
            .join(User, UserAchievement.user_id == User.id)\
            .join(Achievement, UserAchievement.achievement_id == Achievement.id)\
            .order_by(UserAchievement.earned_at.desc())\
            .limit(page_size if activity_type == "achievement" else page_size // 4)\
            .offset(offset if activity_type == "achievement" else 0)\
            .all()

        for user_ach, user, achievement in achievements:
            activities.append({
                "type": "achievement",
                "timestamp": user_ach.earned_at,
                "user_id": user.id,
                "username": user.username,
                "details": {
                    "achievement_name": achievement.name,
                    "achievement_icon": achievement.icon,
                    "xp_reward": achievement.xp_reward
                }
            })

    if not activity_type or activity_type == "auth":
        auth_logs = db.query(AuditLog, User)\
            .join(User, AuditLog.user_id == User.id)\
            .order_by(AuditLog.timestamp.desc())\
            .limit(page_size if activity_type == "auth" else page_size // 4)\
            .offset(offset if activity_type == "auth" else 0)\
            .all()

        for log, user in auth_logs:
            activities.append({
                "type": "auth",
                "timestamp": log.timestamp,
                "user_id": user.id,
                "username": user.username,
                "details": {
                    "action": log.action,
                    "success": log.success,
                    "ip_address": log.ip_address
                }
            })

    # Sort by timestamp
    activities.sort(key=lambda x: x["timestamp"], reverse=True)

    # Get total count
    total = len(activities)
    if not activity_type:
        # Approximate total when showing mixed types
        total = max(
            db.query(func.count(QuizAttempt.id)).scalar() or 0,
            db.query(func.count(UserAchievement.user_id)).scalar() or 0,
            db.query(func.count(AuditLog.id)).scalar() or 0
        )

    # Limit to page_size
    activities = activities[:page_size]

    return activities, total


def get_quiz_attempt_details(db: Session, attempt_id: int) -> Optional[Tuple[QuizAttempt, List[UserAnswer]]]:
    """
    Get detailed quiz attempt with all answers

    Args:
        db: Database session
        attempt_id: Quiz attempt ID

    Returns:
        Tuple of (QuizAttempt, list of UserAnswers) or None
    """
    attempt = db.query(QuizAttempt).filter(QuizAttempt.id == attempt_id).first()

    if not attempt:
        return None

    answers = db.query(UserAnswer)\
        .filter(UserAnswer.quiz_attempt_id == attempt_id)\
        .all()

    return attempt, answers


def get_audit_logs_paginated(
    db: Session,
    page: int = 1,
    page_size: int = 50,
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    success: Optional[bool] = None
) -> Tuple[List[Tuple[AuditLog, User]], int]:
    """
    Get paginated audit logs with filters

    Args:
        db: Database session
        page: Page number
        page_size: Items per page
        user_id: Filter by user
        action: Filter by action type
        success: Filter by success status

    Returns:
        Tuple of (logs with users, total count)
    """
    query = db.query(AuditLog, User).join(User, AuditLog.user_id == User.id)

    if user_id:
        query = query.filter(AuditLog.user_id == user_id)

    if action:
        query = query.filter(AuditLog.action == action)

    if success is not None:
        query = query.filter(AuditLog.success == success)

    total = query.count()

    offset = (page - 1) * page_size
    logs = query.order_by(AuditLog.timestamp.desc())\
        .offset(offset)\
        .limit(page_size)\
        .all()

    return logs, total
