"""
Avatar API Routes

Endpoints for viewing and managing user avatars.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.utils.auth import get_current_user_id
from app.services import avatar_service
from app.schemas.avatar import (
    SelectAvatarRequest,
    AvatarPublic,
    AvatarWithStatus,
    AvatarUnlocked,
    SelectAvatarResponse,
    AvatarStats,
    AvatarInfo,
    AvatarRarityStats
)

router = APIRouter(
    prefix="/avatars",
    tags=["avatars"]
)


@router.get("", response_model=List[AvatarPublic])
def get_avatars(db: Session = Depends(get_db)):
    """
    Get all avatars (public endpoint)

    No authentication required.

    Returns:
        List of avatars with:
        - id, name, description, image_url, rarity
        - is_default: Whether avatar is available to all users
    """
    try:
        # Get avatars without user context (public view)
        avatars_data = avatar_service.get_all_avatars(db, user_id=None)

        # Convert to Pydantic models
        avatars = [AvatarPublic(**avatar) for avatar in avatars_data]
        return avatars
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch avatars: {str(e)}"
        )


@router.get("/me", response_model=List[AvatarWithStatus])
def get_my_avatars(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    Get all avatars with user's unlock status

    Requires authentication.

    Returns:
        List of all avatars with:
        - id, name, description, image_url, rarity
        - is_default: Whether avatar is available to all users
        - is_unlocked: Whether user has unlocked this avatar
        - is_selected: Whether this is the user's current avatar
        - unlocked_at: When the avatar was unlocked (ISO timestamp, null if locked)
        - required_achievement_id: Achievement needed to unlock (null if default)
        - required_achievement_name: Name of required achievement (null if default)
    """
    try:
        # Get avatars with user status
        avatars_data = avatar_service.get_all_avatars(db, current_user_id)

        # Convert to Pydantic models
        avatars = [AvatarWithStatus(**avatar) for avatar in avatars_data]
        return avatars
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch avatars: {str(e)}"
        )


@router.get("/unlocked", response_model=List[AvatarUnlocked])
def get_unlocked_avatars(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    Get only the avatars the user has unlocked

    Requires authentication.

    Returns:
        List of unlocked avatars with:
        - id, name, description, image_url, rarity
        - is_selected: Whether this is the user's current avatar
        - unlocked_at: ISO timestamp when avatar was unlocked

    Sorted by most recently unlocked first.
    """
    try:
        # Get user's unlocked avatars
        unlocked_data = avatar_service.get_user_unlocked_avatars(db, current_user_id)

        # Convert to Pydantic models
        unlocked_avatars = [AvatarUnlocked(**avatar) for avatar in unlocked_data]
        return unlocked_avatars
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch unlocked avatars: {str(e)}"
        )


@router.post("/select", response_model=SelectAvatarResponse)
def select_avatar(
    request: SelectAvatarRequest,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    Select/equip an avatar

    Requires authentication.

    Request Body:
        {
            "avatar_id": 5
        }

    Returns:
        {
            "success": true,
            "message": "Avatar 'Quiz Champion' selected successfully",
            "avatar": {
                "id": 5,
                "name": "Quiz Champion",
                "description": "...",
                "image_url": "/avatars/quiz_champion.png",
                "rarity": "rare"
            }
        }

    Errors:
        - 400: Avatar not unlocked or doesn't exist
        - 500: Server error
    """
    try:
        # Select the avatar (service will validate unlock status)
        result_data = avatar_service.select_avatar(db, current_user_id, request.avatar_id)

        # Convert to Pydantic model
        result = SelectAvatarResponse(
            success=result_data["success"],
            message=result_data["message"],
            avatar=AvatarInfo(**result_data["avatar"])
        )

        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to select avatar: {str(e)}"
        )


@router.get("/stats", response_model=AvatarStats)
def get_avatar_stats(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    Get user's avatar collection statistics

    Requires authentication.

    Returns:
        {
            "total_avatars": 18,
            "unlocked_avatars": 5,
            "completion_percentage": 27.8,
            "unlocked_by_rarity": {
                "common": 3,
                "rare": 1,
                "epic": 1,
                "legendary": 0
            },
            "selected_avatar": {
                "id": 1,
                "name": "Default Student",
                "description": "...",
                "image_url": "/avatars/default_student.png",
                "rarity": "common"
            }
        }
    """
    try:
        # Get avatar stats from service
        stats_data = avatar_service.get_avatar_stats(db, current_user_id)

        # Convert to Pydantic model
        stats = AvatarStats(
            total_avatars=stats_data["total_avatars"],
            unlocked_avatars=stats_data["unlocked_avatars"],
            completion_percentage=stats_data["completion_percentage"],
            unlocked_by_rarity=AvatarRarityStats(**stats_data["unlocked_by_rarity"]),
            selected_avatar=AvatarInfo(**stats_data["selected_avatar"]) if stats_data["selected_avatar"] else None
        )

        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch avatar stats: {str(e)}"
        )
