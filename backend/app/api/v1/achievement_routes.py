"""
Achievement API Routes

Endpoints for viewing achievements and user progress.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

# Import centralized rate limiter
from app.utils.rate_limit import limiter, RATE_LIMITS
from typing import List

from app.db.session import get_db
from app.utils.auth import get_current_user_id
from app.services import achievement_service
from app.schemas.achievement import (
    AchievementPublic,
    AchievementWithProgress,
    AchievementEarned,
    AchievementStats
)

router = APIRouter(
    prefix="/achievements",
    tags=["achievements"]
)


@router.get("", response_model=List[AchievementPublic])
@limiter.limit(RATE_LIMITS["standard"])  # 30/minute rate limit
async def get_achievements(request: Request, db: Session = Depends(get_db)):
    """
    Get all non-hidden achievements (public endpoint)

    **Rate limit:** 30 requests per minute per IP

    No authentication required.

    Returns:
        List of achievements with:
        - id, name, description, badge_icon_url
        - criteria_type, criteria_value, xp_reward
        - is_hidden (only non-hidden achievements returned)
    """
    # Apply rate limit: 30 requests per minute per IP
    try:
        # Get achievements without user context (public view)
        achievements_data = achievement_service.get_all_achievements(db, user_id=None)

        # Convert to Pydantic models
        achievements = [AchievementPublic(**ach) for ach in achievements_data]
        return achievements
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch achievements: {str(e)}"
        )


@router.get("/me", response_model=List[AchievementWithProgress])
@limiter.limit(RATE_LIMITS["standard"])  # 30/minute rate limit
async def get_my_achievements(
    request: Request,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    Get all achievements with user's progress

    **Rate limit:** 30 requests per minute per IP

    Requires authentication.

    Returns:
        List of achievements with:
        - All achievement details
        - is_earned: Whether user has earned this achievement
        - progress: Current progress toward achievement
        - progress_percentage: Progress as percentage (0-100)
        - Hidden achievements are only shown if earned
    """
    # Apply rate limit: 30 requests per minute per IP
    try:
        # Get achievements with user progress
        achievements_data = achievement_service.get_all_achievements(db, current_user_id)

        # Convert to Pydantic models
        achievements = [AchievementWithProgress(**ach) for ach in achievements_data]
        return achievements
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch achievements: {str(e)}"
        )


@router.get("/earned", response_model=List[AchievementEarned])
@limiter.limit(RATE_LIMITS["standard"])  # 30/minute rate limit
async def get_earned_achievements(
    request: Request,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    Get only the achievements the user has earned

    **Rate limit:** 30 requests per minute per IP

    Requires authentication.

    Returns:
        List of earned achievements with:
        - id, name, description, badge_icon_url
        - xp_reward
        - earned_at: ISO timestamp when achievement was unlocked

    Sorted by most recently earned first.
    """
    # Apply rate limit: 30 requests per minute per IP
    try:
        # Get user's earned achievements
        earned_data = achievement_service.get_user_achievements(db, current_user_id)

        # Convert to Pydantic models
        earned_achievements = [AchievementEarned(**ach) for ach in earned_data]
        return earned_achievements
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch earned achievements: {str(e)}"
        )


@router.get("/stats", response_model=AchievementStats)
@limiter.limit(RATE_LIMITS["standard"])  # 30/minute rate limit
async def get_achievement_stats(
    request: Request,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    Get user's achievement statistics

    **Rate limit:** 30 requests per minute per IP

    Requires authentication.

    Returns:
        {
            "total_achievements": Total number of achievements in game,
            "earned_achievements": Number of achievements user has earned,
            "completion_percentage": Percentage of achievements earned (0-100),
            "total_achievement_xp": Total XP earned from achievements
        }
    """
    # Apply rate limit: 30 requests per minute per IP
    try:
        # Get all achievements
        from app.models.gamification import Achievement, UserAchievement

        total_achievements = db.query(Achievement).count()

        # Get user's earned achievements
        user_achievements = db.query(UserAchievement).filter(
            UserAchievement.user_id == current_user_id
        ).all()

        earned_count = len(user_achievements)

        # Calculate total XP from achievements
        total_achievement_xp = 0
        for ua in user_achievements:
            achievement = db.query(Achievement).filter(
                Achievement.id == ua.achievement_id
            ).first()
            if achievement:
                total_achievement_xp += achievement.xp_reward

        completion_percentage = (earned_count / total_achievements * 100) if total_achievements > 0 else 0

        stats = AchievementStats(
            total_achievements=total_achievements,
            earned_achievements=earned_count,
            completion_percentage=round(completion_percentage, 1),
            total_achievement_xp=total_achievement_xp
        )

        return stats

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch achievement stats: {str(e)}"
        )
