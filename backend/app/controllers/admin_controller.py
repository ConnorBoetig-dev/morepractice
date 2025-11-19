"""
ADMIN CONTROLLER
Orchestrates admin panel operations between routes and services

Handles:
- Question CRUD logic
- User management logic
- Achievement management logic
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional
import math

from app.services import admin_service
from app.schemas.admin import (
    QuestionCreate,
    QuestionUpdate,
    QuestionResponse,
    QuestionListResponse,
    QuestionDeleteResponse,
    UserSummary,
    UserListResponse,
    UserDetailResponse,
    AchievementCreate,
    AchievementUpdate,
    AchievementResponse,
    AchievementListResponse
)


# ================================================================
# QUESTION MANAGEMENT CONTROLLERS
# ================================================================

def list_questions_controller(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    exam_type: Optional[str] = None,
    domain: Optional[str] = None,
    search: Optional[str] = None
) -> QuestionListResponse:
    """
    Get paginated list of questions with filters

    Args:
        db: Database session
        page: Page number (1-indexed, default 1)
        page_size: Items per page (default 20, max 100)
        exam_type: Optional exam type filter
        domain: Optional domain filter
        search: Optional search term

    Returns:
        QuestionListResponse with paginated questions

    Raises:
        HTTPException 400: Invalid parameters
    """
    # Validate parameters
    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page must be at least 1"
        )

    if page_size < 1 or page_size > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page size must be between 1 and 100"
        )

    # Get questions from service
    questions, total = admin_service.get_questions_paginated(
        db, page, page_size, exam_type, domain, search
    )

    # Calculate total pages
    total_pages = math.ceil(total / page_size) if total > 0 else 0

    # Convert to response schema
    question_responses = [
        QuestionResponse.model_validate(q) for q in questions
    ]

    return QuestionListResponse(
        total=total,
        questions=question_responses,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


def get_question_controller(db: Session, question_id: int) -> QuestionResponse:
    """
    Get a single question by ID

    Args:
        db: Database session
        question_id: Question database ID

    Returns:
        QuestionResponse

    Raises:
        HTTPException 404: Question not found
    """
    question = admin_service.get_question_by_id(db, question_id)

    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question with ID {question_id} not found"
        )

    return QuestionResponse.model_validate(question)


def create_question_controller(
    db: Session,
    question_data: QuestionCreate
) -> QuestionResponse:
    """
    Create a new question

    Args:
        db: Database session
        question_data: Question creation data

    Returns:
        QuestionResponse for created question

    Raises:
        HTTPException 500: Database error
    """
    try:
        question = admin_service.create_question(db, question_data)
        return QuestionResponse.model_validate(question)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create question: {str(e)}"
        )


def update_question_controller(
    db: Session,
    question_id: int,
    question_data: QuestionUpdate
) -> QuestionResponse:
    """
    Update an existing question

    Args:
        db: Database session
        question_id: Question database ID
        question_data: Updated question data

    Returns:
        QuestionResponse for updated question

    Raises:
        HTTPException 404: Question not found
        HTTPException 500: Database error
    """
    try:
        question = admin_service.update_question(db, question_id, question_data)

        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Question with ID {question_id} not found"
            )

        return QuestionResponse.model_validate(question)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update question: {str(e)}"
        )


def delete_question_controller(db: Session, question_id: int) -> QuestionDeleteResponse:
    """
    Delete a question

    Args:
        db: Database session
        question_id: Question database ID

    Returns:
        QuestionDeleteResponse

    Raises:
        HTTPException 404: Question not found
    """
    success = admin_service.delete_question(db, question_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question with ID {question_id} not found"
        )

    return QuestionDeleteResponse(
        success=True,
        message=f"Question {question_id} deleted successfully",
        deleted_id=question_id
    )


# ================================================================
# USER MANAGEMENT CONTROLLERS
# ================================================================

def list_users_controller(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    search: Optional[str] = None,
    is_admin: Optional[bool] = None,
    is_verified: Optional[bool] = None
) -> UserListResponse:
    """
    Get paginated list of users

    Args:
        db: Database session
        page: Page number
        page_size: Items per page
        search: Search term
        is_admin: Filter by admin status
        is_verified: Filter by verification status

    Returns:
        UserListResponse with paginated users
    """
    # Validate parameters
    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page must be at least 1"
        )

    if page_size < 1 or page_size > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page size must be between 1 and 100"
        )

    # Get users from service
    users_with_profiles, total = admin_service.get_users_paginated(
        db, page, page_size, search, is_admin, is_verified
    )

    # Calculate total pages
    total_pages = math.ceil(total / page_size) if total > 0 else 0

    # Convert to response schema
    user_summaries = [
        UserSummary(
            id=user.id,
            username=user.username,
            email=user.email,
            is_active=user.is_active,
            is_verified=user.is_verified,
            is_admin=user.is_admin,
            created_at=user.created_at,
            last_login_at=user.last_login_at,
            xp=profile.xp,
            level=profile.level,
            study_streak_current=profile.study_streak_current
        )
        for user, profile in users_with_profiles
    ]

    return UserListResponse(
        total=total,
        users=user_summaries,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


def get_user_details_controller(db: Session, user_id: int) -> UserDetailResponse:
    """
    Get detailed user information

    Args:
        db: Database session
        user_id: User ID

    Returns:
        UserDetailResponse

    Raises:
        HTTPException 404: User not found
    """
    result = admin_service.get_user_details(db, user_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )

    user, profile, stats = result

    return UserDetailResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        is_active=user.is_active,
        is_verified=user.is_verified,
        is_admin=user.is_admin,
        created_at=user.created_at,
        updated_at=user.updated_at,
        last_login_at=user.last_login_at,
        last_login_ip=user.last_login_ip,
        xp=profile.xp,
        level=profile.level,
        study_streak_current=profile.study_streak_current,
        study_streak_longest=profile.study_streak_longest,
        total_quizzes_completed=stats["total_quizzes_completed"],
        total_achievements_earned=stats["total_achievements_earned"]
    )


def toggle_user_admin_controller(db: Session, user_id: int) -> dict:
    """
    Toggle user's admin status

    Args:
        db: Database session
        user_id: User ID

    Returns:
        Success response with updated user info

    Raises:
        HTTPException 404: User not found
    """
    user = admin_service.toggle_user_admin(db, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )

    return {
        "success": True,
        "message": f"User admin status toggled successfully",
        "user": {
            "id": user.id,
            "username": user.username,
            "is_admin": user.is_admin
        }
    }


def toggle_user_active_controller(db: Session, user_id: int) -> dict:
    """
    Toggle user's active status (ban/unban)

    Args:
        db: Database session
        user_id: User ID

    Returns:
        Success response with updated user info

    Raises:
        HTTPException 404: User not found
    """
    user = admin_service.toggle_user_active(db, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )

    status_text = "active" if user.is_active else "banned"
    return {
        "success": True,
        "message": f"User is now {status_text}",
        "user": {
            "id": user.id,
            "username": user.username,
            "is_active": user.is_active
        }
    }


def delete_user_controller(db: Session, user_id: int, admin_id: int) -> dict:
    """
    Delete a user account

    Args:
        db: Database session
        user_id: User ID to delete
        admin_id: ID of admin performing the action (cannot delete self)

    Returns:
        Success response

    Raises:
        HTTPException 400: Cannot delete own account
        HTTPException 404: User not found
    """
    # Prevent admin from deleting themselves
    if user_id == admin_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )

    success = admin_service.delete_user(db, user_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )

    return {
        "success": True,
        "message": f"User {user_id} deleted successfully",
        "deleted_id": user_id
    }


# ================================================================
# ACTIVITY & AUDIT LOG CONTROLLERS
# ================================================================

def get_user_activity_controller(db: Session, user_id: int, limit: int = 50) -> dict:
    """
    Get comprehensive activity history for a user

    Args:
        db: Database session
        user_id: User ID
        limit: Max items per activity type

    Returns:
        Activity data dictionary
    """
    activity_data = admin_service.get_user_activity(db, user_id, limit)

    # Format the response
    return {
        "user_id": user_id,
        "quiz_attempts": [
            {
                "id": attempt.id,
                "exam_type": attempt.exam_type,
                "score_percentage": attempt.score_percentage,
                "correct_answers": attempt.correct_answers,
                "total_questions": attempt.total_questions,
                "xp_earned": attempt.xp_earned,
                "time_taken_seconds": attempt.time_taken_seconds,
                "completed_at": attempt.completed_at
            }
            for attempt in activity_data["quiz_attempts"]
        ],
        "achievements_earned": [
            {
                "achievement_id": achievement.id,
                "achievement_name": achievement.name,
                "achievement_icon": achievement.icon,
                "xp_reward": achievement.xp_reward,
                "earned_at": user_ach.earned_at
            }
            for user_ach, achievement in activity_data["achievements_earned"]
        ],
        "active_sessions": [
            {
                "id": session.id,
                "ip_address": session.ip_address,
                "user_agent": session.user_agent,
                "created_at": session.created_at,
                "last_active": session.last_active,
                "expires_at": session.expires_at
            }
            for session in activity_data["active_sessions"]
        ],
        "audit_logs": [
            {
                "id": log.id,
                "action": log.action,
                "success": log.success,
                "ip_address": log.ip_address,
                "user_agent": log.user_agent,
                "details": log.details,
                "timestamp": log.timestamp
            }
            for log in activity_data["audit_logs"]
        ]
    }


def get_activity_feed_controller(
    db: Session,
    page: int = 1,
    page_size: int = 50,
    activity_type: Optional[str] = None
) -> dict:
    """
    Get global activity feed

    Args:
        db: Database session
        page: Page number
        page_size: Items per page
        activity_type: Filter by type

    Returns:
        Activity feed data
    """
    activities, total = admin_service.get_global_activity_feed(
        db, page, page_size, activity_type
    )

    total_pages = math.ceil(total / page_size) if total > 0 else 0

    return {
        "activities": activities,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }


def get_audit_logs_controller(
    db: Session,
    page: int = 1,
    page_size: int = 50,
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    success: Optional[bool] = None
) -> dict:
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
        Paginated audit logs
    """
    logs, total = admin_service.get_audit_logs_paginated(
        db, page, page_size, user_id, action, success
    )

    total_pages = math.ceil(total / page_size) if total > 0 else 0

    return {
        "logs": [
            {
                "id": log.id,
                "user_id": user.id,
                "username": user.username,
                "action": log.action,
                "success": log.success,
                "ip_address": log.ip_address,
                "user_agent": log.user_agent,
                "details": log.details,
                "timestamp": log.timestamp
            }
            for log, user in logs
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }


# ================================================================
# ACHIEVEMENT MANAGEMENT CONTROLLERS
# ================================================================

def list_achievements_controller(db: Session) -> AchievementListResponse:
    """
    Get all achievements (including hidden)

    Args:
        db: Database session

    Returns:
        AchievementListResponse
    """
    achievements = admin_service.get_all_achievements(db)

    achievement_responses = [
        AchievementResponse.model_validate(a) for a in achievements
    ]

    return AchievementListResponse(
        total=len(achievements),
        achievements=achievement_responses
    )


def create_achievement_controller(
    db: Session,
    achievement_data: AchievementCreate
) -> AchievementResponse:
    """
    Create a new achievement

    Args:
        db: Database session
        achievement_data: Achievement creation data

    Returns:
        AchievementResponse

    Raises:
        HTTPException 500: Database error
    """
    try:
        achievement = admin_service.create_achievement(
            db,
            achievement_data.model_dump()
        )
        return AchievementResponse.model_validate(achievement)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create achievement: {str(e)}"
        )


def update_achievement_controller(
    db: Session,
    achievement_id: int,
    achievement_data: AchievementUpdate
) -> AchievementResponse:
    """
    Update an achievement

    Args:
        db: Database session
        achievement_id: Achievement ID
        achievement_data: Updated data

    Returns:
        AchievementResponse

    Raises:
        HTTPException 404: Achievement not found
    """
    update_data = achievement_data.model_dump(exclude_unset=True)
    achievement = admin_service.update_achievement(db, achievement_id, update_data)

    if not achievement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Achievement with ID {achievement_id} not found"
        )

    return AchievementResponse.model_validate(achievement)


def delete_achievement_controller(db: Session, achievement_id: int) -> dict:
    """
    Delete an achievement

    Args:
        db: Database session
        achievement_id: Achievement ID

    Returns:
        Success response dict

    Raises:
        HTTPException 404: Achievement not found
    """
    success = admin_service.delete_achievement(db, achievement_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Achievement with ID {achievement_id} not found"
        )

    return {
        "success": True,
        "message": f"Achievement {achievement_id} deleted successfully",
        "deleted_id": achievement_id
    }
