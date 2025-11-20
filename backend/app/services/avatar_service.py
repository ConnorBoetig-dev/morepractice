"""
Avatar Service

Handles avatar management including unlocking, selection, and retrieval.
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Dict, Any
from datetime import datetime

from app.models.gamification import Avatar, UserAvatar, Achievement, UserAchievement
from app.models.user import UserProfile


def unlock_default_avatars(db: Session, user_id: int):
    """
    Unlock all default avatars for a new user

    Default avatars are those with required_achievement_id = NULL.
    This should be called when a user first signs up.

    Args:
        db: Database session
        user_id: User ID to unlock avatars for
    """
    # Get all default avatars (those with no achievement requirement)
    default_avatars = db.query(Avatar).filter(Avatar.required_achievement_id == None).all()

    # Check which ones user already has
    existing_avatar_ids = db.query(UserAvatar.avatar_id).filter(
        UserAvatar.user_id == user_id
    ).all()
    existing_ids = {aid[0] for aid in existing_avatar_ids}

    # Unlock default avatars that aren't already unlocked
    for avatar in default_avatars:
        if avatar.id not in existing_ids:
            user_avatar = UserAvatar(
                user_id=user_id,
                avatar_id=avatar.id,
                unlocked_at=datetime.utcnow()
            )
            db.add(user_avatar)

    db.commit()


def unlock_avatar_from_achievement(db: Session, user_id: int, achievement_id: int):
    """
    Unlock avatar associated with a specific achievement

    This is called automatically when a user earns an achievement that unlocks an avatar.

    Args:
        db: Database session
        user_id: User ID
        achievement_id: Achievement ID that was just earned

    Returns:
        Avatar: The unlocked avatar if one exists, None otherwise
    """
    # Find avatar that requires this achievement
    avatar = db.query(Avatar).filter(
        Avatar.required_achievement_id == achievement_id
    ).first()

    if not avatar:
        return None

    # Check if user already has this avatar
    existing = db.query(UserAvatar).filter(
        and_(
            UserAvatar.user_id == user_id,
            UserAvatar.avatar_id == avatar.id
        )
    ).first()

    if existing:
        return None  # Already unlocked

    # Unlock the avatar
    user_avatar = UserAvatar(
        user_id=user_id,
        avatar_id=avatar.id,
        unlocked_at=datetime.utcnow()
    )
    db.add(user_avatar)
    db.commit()

    return avatar


def get_all_avatars(db: Session, user_id: int = None) -> List[Dict[str, Any]]:
    """
    Get all avatars with unlock status for a specific user

    Args:
        db: Database session
        user_id: Optional user ID to include unlock status

    Returns:
        List of avatars with unlock status and requirements
    """
    avatars = db.query(Avatar).order_by(Avatar.id).all()

    result = []

    if user_id:
        # Get user's unlocked avatar IDs
        unlocked_avatar_ids = db.query(UserAvatar.avatar_id, UserAvatar.unlocked_at).filter(
            UserAvatar.user_id == user_id
        ).all()
        unlocked_map = {aid: unlocked_at for aid, unlocked_at in unlocked_avatar_ids}

        # Get user's current selected avatar
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        selected_avatar_id = profile.selected_avatar_id if profile else None

        for avatar in avatars:
            is_unlocked = avatar.id in unlocked_map
            unlocked_at = unlocked_map.get(avatar.id)

            # Get required achievement name if applicable
            required_achievement_name = None
            if avatar.required_achievement_id:
                achievement = db.query(Achievement).filter(
                    Achievement.id == avatar.required_achievement_id
                ).first()
                if achievement:
                    required_achievement_name = achievement.name

            result.append({
                "id": avatar.id,
                "name": avatar.name,
                "description": avatar.description,
                "image_url": avatar.image_url,
                "is_default": avatar.required_achievement_id is None,
                "is_unlocked": is_unlocked,
                "is_selected": avatar.id == selected_avatar_id,
                "unlocked_at": unlocked_at.isoformat() if unlocked_at else None,
                "required_achievement_id": avatar.required_achievement_id,
                "required_achievement_name": required_achievement_name
            })
    else:
        # No user context - return basic avatar info
        for avatar in avatars:
            result.append({
                "id": avatar.id,
                "name": avatar.name,
                "description": avatar.description,
                "image_url": avatar.image_url,
                "is_default": avatar.required_achievement_id is None
            })

    return result


def get_user_unlocked_avatars(db: Session, user_id: int) -> List[Dict[str, Any]]:
    """
    Get only the avatars the user has unlocked

    Args:
        db: Database session
        user_id: User ID

    Returns:
        List of unlocked avatars with unlock timestamp
    """
    user_avatars = db.query(
        Avatar, UserAvatar.unlocked_at
    ).join(
        UserAvatar,
        Avatar.id == UserAvatar.avatar_id
    ).filter(
        UserAvatar.user_id == user_id
    ).order_by(
        UserAvatar.unlocked_at.desc()
    ).all()

    # Get user's selected avatar
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    selected_avatar_id = profile.selected_avatar_id if profile else None

    return [
        {
            "id": avatar.id,
            "name": avatar.name,
            "description": avatar.description,
            "image_url": avatar.image_url,
            "is_selected": avatar.id == selected_avatar_id,
            "unlocked_at": unlocked_at.isoformat() if unlocked_at else None
        }
        for avatar, unlocked_at in user_avatars
    ]


def select_avatar(db: Session, user_id: int, avatar_id: int) -> Dict[str, Any]:
    """
    Select/equip an avatar for a user

    Args:
        db: Database session
        user_id: User ID
        avatar_id: Avatar ID to select

    Returns:
        dict: Success message and selected avatar info

    Raises:
        ValueError: If avatar is not unlocked or doesn't exist
    """
    # Check if avatar exists
    avatar = db.query(Avatar).filter(Avatar.id == avatar_id).first()
    if not avatar:
        raise ValueError("Avatar not found")

    # Check if user has unlocked this avatar
    user_avatar = db.query(UserAvatar).filter(
        and_(
            UserAvatar.user_id == user_id,
            UserAvatar.avatar_id == avatar_id
        )
    ).first()

    if not user_avatar:
        raise ValueError("Avatar not unlocked. Complete the required achievement to unlock this avatar.")

    # Update user's selected avatar
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        raise ValueError("User profile not found")

    profile.selected_avatar_id = avatar_id
    db.commit()

    return {
        "success": True,
        "message": f"Avatar '{avatar.name}' selected successfully",
        "avatar": {
            "id": avatar.id,
            "name": avatar.name,
            "description": avatar.description,
            "image_url": avatar.image_url
        }
    }


def get_avatar_stats(db: Session, user_id: int) -> Dict[str, Any]:
    """
    Get user's avatar collection statistics

    Args:
        db: Database session
        user_id: User ID

    Returns:
        dict: Avatar statistics including total, unlocked, and completion percentage
    """
    # Total avatars in game
    total_avatars = db.query(Avatar).count()

    # User's unlocked avatars
    unlocked_count = db.query(UserAvatar).filter(
        UserAvatar.user_id == user_id
    ).count()

    # Calculate completion percentage
    completion_percentage = (unlocked_count / total_avatars * 100) if total_avatars > 0 else 0

    # Get user's selected avatar
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    selected_avatar = None
    if profile and profile.selected_avatar_id:
        selected_avatar_obj = db.query(Avatar).filter(
            Avatar.id == profile.selected_avatar_id
        ).first()
        if selected_avatar_obj:
            selected_avatar = {
                "id": selected_avatar_obj.id,
                "name": selected_avatar_obj.name,
                "image_url": selected_avatar_obj.image_url
            }

    return {
        "total_avatars": total_avatars,
        "unlocked_avatars": unlocked_count,
        "completion_percentage": round(completion_percentage, 1),
        "selected_avatar": selected_avatar
    }
