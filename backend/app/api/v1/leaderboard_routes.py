"""
Leaderboard API Routes

Endpoints for viewing various leaderboards and user rankings.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from typing import Optional

# Import centralized rate limiter
from app.utils.rate_limit import limiter, RATE_LIMITS

from app.db.session import get_db
from app.utils.auth import get_current_user_id
from app.services import leaderboard_service
from app.schemas.leaderboard import (
    XPLeaderboardResponse,
    QuizCountLeaderboardResponse,
    AccuracyLeaderboardResponse,
    StreakLeaderboardResponse,
    LeaderboardEntry
)

router = APIRouter(
    prefix="/leaderboard",
    tags=["leaderboard"]
)


@router.get("/xp", response_model=XPLeaderboardResponse)
@limiter.limit(RATE_LIMITS["leaderboard"])  # 20/minute rate limit
async def get_xp_leaderboard(
    request: Request,
    limit: int = Query(100, ge=1, le=500, description="Number of top users to return"),
    time_period: str = Query("all_time", regex="^(all_time|monthly|weekly)$", description="Time period filter"),
    db: Session = Depends(get_db),
    current_user_id: Optional[int] = None
):
    """
    Get leaderboard sorted by total XP

    **Rate limit:** 20 requests per minute per IP (protects expensive database queries)

    Query Parameters:
        - limit: Number of top users to return (1-500, default 100)
        - time_period: Time period filter (all_time, monthly, weekly)

    Returns:
        Leaderboard with top users by XP and current user's entry if authenticated
    """

    try:
        # Note: Authentication is optional - if provided, include user's entry
        data = leaderboard_service.get_xp_leaderboard(
            db,
            limit=limit,
            time_period=time_period,
            current_user_id=current_user_id
        )

        return XPLeaderboardResponse(
            leaderboard_type="xp",
            time_period=data["time_period"],
            total_users=data["total_users"],
            entries=[LeaderboardEntry(**entry) for entry in data["entries"]],
            current_user_entry=LeaderboardEntry(**data["current_user_entry"]) if data["current_user_entry"] else None
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch XP leaderboard: {str(e)}"
        )


@router.get("/quiz-count", response_model=QuizCountLeaderboardResponse)
@limiter.limit(RATE_LIMITS["leaderboard"])  # 20/minute rate limit
async def get_quiz_count_leaderboard(
    request: Request,
    limit: int = Query(100, ge=1, le=500, description="Number of top users to return"),
    time_period: str = Query("all_time", regex="^(all_time|monthly|weekly)$", description="Time period filter"),
    db: Session = Depends(get_db),
    current_user_id: Optional[int] = None
):
    """
    Get leaderboard sorted by total quizzes completed

    **Rate limit:** 20 requests per minute per IP (protects expensive database queries)

    Query Parameters:
        - limit: Number of top users to return (1-500, default 100)
        - time_period: Time period filter (all_time, monthly, weekly)

    Returns:
        Leaderboard with top users by quiz count and current user's entry if authenticated
    """

    try:
        data = leaderboard_service.get_quiz_count_leaderboard(
            db,
            limit=limit,
            time_period=time_period,
            current_user_id=current_user_id
        )

        return QuizCountLeaderboardResponse(
            leaderboard_type="quiz_count",
            time_period=data["time_period"],
            total_users=data["total_users"],
            entries=[LeaderboardEntry(**entry) for entry in data["entries"]],
            current_user_entry=LeaderboardEntry(**data["current_user_entry"]) if data["current_user_entry"] else None
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch quiz count leaderboard: {str(e)}"
        )


@router.get("/accuracy", response_model=AccuracyLeaderboardResponse)
@limiter.limit(RATE_LIMITS["leaderboard"])  # 20/minute rate limit
async def get_accuracy_leaderboard(
    request: Request,
    limit: int = Query(100, ge=1, le=500, description="Number of top users to return"),
    minimum_quizzes: int = Query(1, ge=1, le=100, description="Minimum quizzes to qualify"),
    time_period: str = Query("all_time", regex="^(all_time|monthly|weekly)$", description="Time period filter"),
    db: Session = Depends(get_db),
    current_user_id: Optional[int] = None
):
    """
    Get leaderboard sorted by average accuracy

    **Rate limit:** 20 requests per minute per IP (protects expensive database queries)

    Shows users with at least 1 quiz completed (accuracy calculated from first quiz).

    Query Parameters:
        - limit: Number of top users to return (1-500, default 100)
        - minimum_quizzes: Minimum quizzes required to qualify (1-100, default 1)
        - time_period: Time period filter (all_time, monthly, weekly)

    Returns:
        Leaderboard with top users by accuracy and current user's entry if authenticated and qualified
    """

    try:
        data = leaderboard_service.get_accuracy_leaderboard(
            db,
            limit=limit,
            minimum_quizzes=minimum_quizzes,
            time_period=time_period,
            current_user_id=current_user_id
        )

        return AccuracyLeaderboardResponse(
            leaderboard_type="accuracy",
            time_period=data["time_period"],
            total_users=data["total_users"],
            minimum_quizzes=data["minimum_quizzes"],
            entries=[LeaderboardEntry(**entry) for entry in data["entries"]],
            current_user_entry=LeaderboardEntry(**data["current_user_entry"]) if data["current_user_entry"] else None
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch accuracy leaderboard: {str(e)}"
        )


@router.get("/streak", response_model=StreakLeaderboardResponse)
@limiter.limit(RATE_LIMITS["leaderboard"])  # 20/minute rate limit
async def get_streak_leaderboard(
    request: Request,
    limit: int = Query(100, ge=1, le=500, description="Number of top users to return"),
    db: Session = Depends(get_db),
    current_user_id: Optional[int] = None
):
    """
    Get leaderboard sorted by current study streak

    **Rate limit:** 20 requests per minute per IP (protects expensive database queries)

    Only includes users with active streaks (streak > 0).

    Query Parameters:
        - limit: Number of top users to return (1-500, default 100)

    Returns:
        Leaderboard with top users by current streak and current user's entry if authenticated and has active streak
    """

    try:
        data = leaderboard_service.get_streak_leaderboard(
            db,
            limit=limit,
            current_user_id=current_user_id
        )

        return StreakLeaderboardResponse(
            leaderboard_type="streak",
            time_period=data["time_period"],
            total_users=data["total_users"],
            entries=[LeaderboardEntry(**entry) for entry in data["entries"]],
            current_user_entry=LeaderboardEntry(**data["current_user_entry"]) if data["current_user_entry"] else None
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch streak leaderboard: {str(e)}"
        )


