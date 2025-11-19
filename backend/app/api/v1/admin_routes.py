"""
ADMIN API ROUTES
Admin-only endpoints for content and user management

All routes require admin authentication via get_admin_user_id dependency

Endpoints:
- Question Management: CRUD operations for questions
- User Management: View and manage users
- Achievement Management: CRUD operations for achievements
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session
from typing import Optional

# Import centralized rate limiter
from app.utils.rate_limit import limiter, RATE_LIMITS

from app.db.session import get_db
from app.utils.auth import get_admin_user_id, get_admin_user
from app.utils.request_helpers import get_client_ip, get_user_agent
from app.config.logging_config import log_admin_action
from app.schemas.admin import (
    QuestionCreate,
    QuestionUpdate,
    QuestionResponse,
    QuestionListResponse,
    QuestionDeleteResponse,
    UserListResponse,
    UserDetailResponse,
    AchievementCreate,
    AchievementUpdate,
    AchievementResponse,
    AchievementListResponse
)
from app.controllers import admin_controller


# Create router
router = APIRouter(prefix="/admin", tags=["admin"])


# ================================================================
# QUESTION MANAGEMENT ENDPOINTS
# ================================================================

@router.get(
    "/questions",
    response_model=QuestionListResponse,
    summary="List all questions with pagination"
)
@limiter.limit(RATE_LIMITS["standard"])
async def list_questions(
    request: Request,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    exam_type: Optional[str] = Query(None, description="Filter by exam type"),
    domain: Optional[str] = Query(None, description="Filter by domain"),
    search: Optional[str] = Query(None, description="Search in question text"),
    db: Session = Depends(get_db),
    admin_id: int = Depends(get_admin_user_id)
):
    """
    Get paginated list of questions with optional filters

    **Admin only**

    Query Parameters:
    - `page`: Page number (default: 1)
    - `page_size`: Items per page (default: 20, max: 100)
    - `exam_type`: Filter by exam type (security, network, a1101, a1102)
    - `domain`: Filter by domain (e.g., "1.1", "2.3")
    - `search`: Search term for question text

    Returns paginated question list with total count and page info
    """
    return admin_controller.list_questions_controller(
        db, page, page_size, exam_type, domain, search
    )


@router.get(
    "/questions/{question_id}",
    response_model=QuestionResponse,
    summary="Get a single question by ID"
)
@limiter.limit(RATE_LIMITS["standard"])
async def get_question(
    request: Request,
    question_id: int,
    db: Session = Depends(get_db),
    admin_id: int = Depends(get_admin_user_id)
):
    """
    Get detailed information for a specific question

    **Admin only**

    Path Parameters:
    - `question_id`: Database ID of the question

    Returns complete question details including all options and explanations
    """
    return admin_controller.get_question_controller(db, question_id)


@router.post(
    "/questions",
    response_model=QuestionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new question"
)
@limiter.limit(RATE_LIMITS["standard"])
async def create_question(
    request: Request,
    question_data: QuestionCreate,
    db: Session = Depends(get_db),
    admin_user = Depends(get_admin_user)
):
    """
    Create a new question

    **Admin only**

    Request Body:
    ```json
    {
        "question_id": "Q123",
        "exam_type": "security",
        "domain": "1.1",
        "question_text": "Which security control...",
        "correct_answer": "B",
        "options": {
            "A": {"text": "Deterrent", "explanation": "Incorrect because..."},
            "B": {"text": "Preventive", "explanation": "Correct because..."},
            "C": {"text": "Detective", "explanation": "Incorrect because..."},
            "D": {"text": "Corrective", "explanation": "Incorrect because..."}
        }
    }
    ```

    Returns the created question with database ID
    """
    result = admin_controller.create_question_controller(db, question_data)

    # Log admin action
    log_admin_action(
        action="create_question",
        admin_id=admin_user.id,
        admin_username=admin_user.username,
        target_type="question",
        target_id=result.id,
        ip_address=get_client_ip(request),
        details=f"Created question: {question_data.question_id} ({question_data.exam_type}/{question_data.domain})"
    )

    return result


@router.put(
    "/questions/{question_id}",
    response_model=QuestionResponse,
    summary="Update an existing question"
)
@limiter.limit(RATE_LIMITS["standard"])
async def update_question(
    request: Request,
    question_id: int,
    question_data: QuestionUpdate,
    db: Session = Depends(get_db),
    admin_user = Depends(get_admin_user)
):
    """
    Update an existing question

    **Admin only**

    Path Parameters:
    - `question_id`: Database ID of the question to update

    Request Body: Provide only the fields you want to update (all fields optional)

    Returns the updated question
    """
    result = admin_controller.update_question_controller(db, question_id, question_data)

    # Log admin action
    log_admin_action(
        action="update_question",
        admin_id=admin_user.id,
        admin_username=admin_user.username,
        target_type="question",
        target_id=question_id,
        ip_address=get_client_ip(request),
        details=f"Updated question #{question_id}"
    )

    return result


@router.delete(
    "/questions/{question_id}",
    response_model=QuestionDeleteResponse,
    summary="Delete a question"
)
@limiter.limit(RATE_LIMITS["standard"])
async def delete_question(
    request: Request,
    question_id: int,
    db: Session = Depends(get_db),
    admin_user = Depends(get_admin_user)
):
    """
    Delete a question permanently

    **Admin only**

    Path Parameters:
    - `question_id`: Database ID of the question to delete

    Warning: This action cannot be undone. The question will be permanently deleted.

    Returns success confirmation
    """
    result = admin_controller.delete_question_controller(db, question_id)

    # Log admin action
    log_admin_action(
        action="delete_question",
        admin_id=admin_user.id,
        admin_username=admin_user.username,
        target_type="question",
        target_id=question_id,
        ip_address=get_client_ip(request),
        details=f"Permanently deleted question #{question_id}"
    )

    return result


# ================================================================
# USER MANAGEMENT ENDPOINTS
# ================================================================

@router.get(
    "/users",
    response_model=UserListResponse,
    summary="List all users with pagination"
)
@limiter.limit(RATE_LIMITS["standard"])
async def list_users(
    request: Request,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search username or email"),
    is_admin: Optional[bool] = Query(None, description="Filter by admin status"),
    is_verified: Optional[bool] = Query(None, description="Filter by verification status"),
    db: Session = Depends(get_db),
    admin_id: int = Depends(get_admin_user_id)
):
    """
    Get paginated list of users with filters

    **Admin only**

    Query Parameters:
    - `page`: Page number
    - `page_size`: Items per page
    - `search`: Search in username or email
    - `is_admin`: Filter by admin status (true/false)
    - `is_verified`: Filter by verification status (true/false)

    Returns paginated user list with basic info and stats
    """
    return admin_controller.list_users_controller(
        db, page, page_size, search, is_admin, is_verified
    )


@router.get(
    "/users/{user_id}",
    response_model=UserDetailResponse,
    summary="Get detailed user information"
)
@limiter.limit(RATE_LIMITS["standard"])
async def get_user_details(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db),
    admin_id: int = Depends(get_admin_user_id)
):
    """
    Get detailed information for a specific user

    **Admin only**

    Path Parameters:
    - `user_id`: Database ID of the user

    Returns complete user details including:
    - Account information
    - Profile stats (XP, level, streaks)
    - Activity metrics (quizzes, achievements)
    """
    return admin_controller.get_user_details_controller(db, user_id)


@router.post(
    "/users/{user_id}/toggle-admin",
    summary="Toggle user admin status"
)
@limiter.limit(RATE_LIMITS["standard"])
async def toggle_user_admin(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db),
    admin_user = Depends(get_admin_user)
):
    """
    Toggle admin status for a user

    **Admin only**

    Path Parameters:
    - `user_id`: Database ID of the user

    Warning: Use with caution. Granting admin access gives full control.

    Returns updated user information
    """
    result = admin_controller.toggle_user_admin_controller(db, user_id)

    # Log admin action
    log_admin_action(
        action="toggle_admin",
        admin_id=admin_user.id,
        admin_username=admin_user.username,
        target_type="user",
        target_id=user_id,
        ip_address=get_client_ip(request),
        details=f"Toggled admin status to: {result['user']['is_admin']}"
    )

    return result


@router.post(
    "/users/{user_id}/toggle-active",
    summary="Toggle user active status (ban/unban)"
)
@limiter.limit(RATE_LIMITS["standard"])
async def toggle_user_active(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db),
    admin_user = Depends(get_admin_user)
):
    """
    Toggle user active status (ban or unban)

    **Admin only**

    Path Parameters:
    - `user_id`: Database ID of the user

    Banned users cannot log in or access the platform.

    Returns updated user information
    """
    result = admin_controller.toggle_user_active_controller(db, user_id)

    # Log admin action
    status_action = "banned" if not result['user']['is_active'] else "unbanned"
    log_admin_action(
        action="toggle_active",
        admin_id=admin_user.id,
        admin_username=admin_user.username,
        target_type="user",
        target_id=user_id,
        ip_address=get_client_ip(request),
        details=f"User {status_action}"
    )

    return result


@router.delete(
    "/users/{user_id}",
    summary="Delete a user account"
)
@limiter.limit(RATE_LIMITS["standard"])
async def delete_user(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db),
    admin_user = Depends(get_admin_user)
):
    """
    Permanently delete a user account

    **Admin only**

    Path Parameters:
    - `user_id`: Database ID of the user

    Warning: This action cannot be undone. All user data will be deleted.

    Returns success confirmation
    """
    result = admin_controller.delete_user_controller(db, user_id, admin_user.id)

    # Log admin action (critical - user deletion)
    log_admin_action(
        action="delete_user",
        admin_id=admin_user.id,
        admin_username=admin_user.username,
        target_type="user",
        target_id=user_id,
        ip_address=get_client_ip(request),
        details="Permanently deleted user account"
    )

    return result


# ================================================================
# ACTIVITY & AUDIT LOG ENDPOINTS
# ================================================================

@router.get(
    "/users/{user_id}/activity",
    summary="Get user activity history"
)
@limiter.limit(RATE_LIMITS["standard"])
async def get_user_activity(
    request: Request,
    user_id: int,
    limit: int = Query(50, ge=1, le=200, description="Max items per type"),
    db: Session = Depends(get_db),
    admin_id: int = Depends(get_admin_user_id)
):
    """
    Get comprehensive activity history for a specific user

    **Admin only**

    Returns:
    - Quiz attempts
    - Achievements earned
    - Active sessions
    - Audit logs (auth events)
    """
    return admin_controller.get_user_activity_controller(db, user_id, limit)


@router.get(
    "/activity/feed",
    summary="Get global activity feed"
)
@limiter.limit(RATE_LIMITS["standard"])
async def get_activity_feed(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    activity_type: Optional[str] = Query(None, description="Filter: quiz, achievement, auth"),
    db: Session = Depends(get_db),
    admin_id: int = Depends(get_admin_user_id)
):
    """
    Get global activity feed across all users

    **Admin only**

    Query Parameters:
    - `activity_type`: Filter by type (quiz, achievement, auth)
    """
    return admin_controller.get_activity_feed_controller(
        db, page, page_size, activity_type
    )


@router.get(
    "/audit-logs",
    summary="Get audit logs with filters"
)
@limiter.limit(RATE_LIMITS["standard"])
async def get_audit_logs(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    user_id: Optional[int] = Query(None),
    action: Optional[str] = Query(None),
    success: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    admin_id: int = Depends(get_admin_user_id)
):
    """
    Get paginated audit logs with filters

    **Admin only**

    Query Parameters:
    - `user_id`: Filter by specific user
    - `action`: Filter by action type (login, logout, etc.)
    - `success`: Filter by success status
    """
    return admin_controller.get_audit_logs_controller(
        db, page, page_size, user_id, action, success
    )


# ================================================================
# ACHIEVEMENT MANAGEMENT ENDPOINTS
# ================================================================

@router.get(
    "/achievements",
    response_model=AchievementListResponse,
    summary="List all achievements"
)
@limiter.limit(RATE_LIMITS["standard"])
async def list_achievements(
    request: Request,
    db: Session = Depends(get_db),
    admin_id: int = Depends(get_admin_user_id)
):
    """
    Get all achievements (including hidden ones)

    **Admin only**

    Returns complete list of all achievements with unlock criteria
    """
    return admin_controller.list_achievements_controller(db)


@router.post(
    "/achievements",
    response_model=AchievementResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new achievement"
)
@limiter.limit(RATE_LIMITS["standard"])
async def create_achievement(
    request: Request,
    achievement_data: AchievementCreate,
    db: Session = Depends(get_db),
    admin_user = Depends(get_admin_user)
):
    """
    Create a new achievement

    **Admin only**

    Request Body:
    ```json
    {
        "name": "First Steps",
        "description": "Complete your first quiz",
        "icon": "🎯",
        "criteria_type": "quiz_count",
        "criteria_value": 1,
        "xp_reward": 50,
        "is_hidden": false,
        "rarity": "common"
    }
    ```

    Criteria Types:
    - `quiz_count`: Total quizzes completed
    - `perfect_quiz`: Perfect score quizzes
    - `high_score`: Specific score percentage threshold
    - `streak`: Study streak days
    - `level`: User level requirement
    - `exam_specific`: Exam-specific achievements (requires criteria_exam_type)

    Returns the created achievement
    """
    result = admin_controller.create_achievement_controller(db, achievement_data)

    # Log admin action
    log_admin_action(
        action="create_achievement",
        admin_id=admin_user.id,
        admin_username=admin_user.username,
        target_type="achievement",
        target_id=result.id,
        ip_address=get_client_ip(request),
        details=f"Created achievement: {achievement_data.name} ({achievement_data.criteria_type})"
    )

    return result


@router.put(
    "/achievements/{achievement_id}",
    response_model=AchievementResponse,
    summary="Update an achievement"
)
@limiter.limit(RATE_LIMITS["standard"])
async def update_achievement(
    request: Request,
    achievement_id: int,
    achievement_data: AchievementUpdate,
    db: Session = Depends(get_db),
    admin_user = Depends(get_admin_user)
):
    """
    Update an existing achievement

    **Admin only**

    Path Parameters:
    - `achievement_id`: Database ID of the achievement

    Request Body: Provide only the fields you want to update

    Returns the updated achievement
    """
    result = admin_controller.update_achievement_controller(
        db, achievement_id, achievement_data
    )

    # Log admin action
    log_admin_action(
        action="update_achievement",
        admin_id=admin_user.id,
        admin_username=admin_user.username,
        target_type="achievement",
        target_id=achievement_id,
        ip_address=get_client_ip(request),
        details=f"Updated achievement #{achievement_id}"
    )

    return result


@router.delete(
    "/achievements/{achievement_id}",
    summary="Delete an achievement"
)
@limiter.limit(RATE_LIMITS["standard"])
async def delete_achievement(
    request: Request,
    achievement_id: int,
    db: Session = Depends(get_db),
    admin_user = Depends(get_admin_user)
):
    """
    Delete an achievement permanently

    **Admin only**

    Path Parameters:
    - `achievement_id`: Database ID of the achievement

    Warning: This will also remove this achievement from all users who earned it.

    Returns success confirmation
    """
    result = admin_controller.delete_achievement_controller(db, achievement_id)

    # Log admin action
    log_admin_action(
        action="delete_achievement",
        admin_id=admin_user.id,
        admin_username=admin_user.username,
        target_type="achievement",
        target_id=achievement_id,
        ip_address=get_client_ip(request),
        details=f"Permanently deleted achievement #{achievement_id}"
    )

    return result
