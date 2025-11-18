"""
Avatar Schemas

Pydantic models for avatar-related API requests and responses.
Used by FastAPI for request validation and response serialization.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime


# ========================================
# AVATAR REQUEST SCHEMAS
# ========================================

class SelectAvatarRequest(BaseModel):
    """
    Request to select/equip an avatar
    """
    avatar_id: int = Field(
        description="ID of the avatar to select",
        gt=0
    )


# ========================================
# AVATAR RESPONSE SCHEMAS
# ========================================

class AvatarBase(BaseModel):
    """Base avatar schema with common fields"""
    id: int
    name: str
    description: str
    image_url: str
    rarity: str = Field(
        description="Avatar rarity: common, rare, epic, or legendary"
    )

    class Config:
        from_attributes = True


class AvatarPublic(AvatarBase):
    """
    Public avatar schema (no user-specific data)
    Used when user is not authenticated
    """
    is_default: bool = Field(
        description="Whether this avatar is available to all users by default"
    )

    class Config:
        from_attributes = True


class AvatarWithStatus(AvatarBase):
    """
    Avatar with user's unlock and selection status
    Used when user is authenticated
    """
    is_default: bool = Field(
        description="Whether this avatar is available to all users by default"
    )
    is_unlocked: bool = Field(
        description="Whether the user has unlocked this avatar"
    )
    is_selected: bool = Field(
        description="Whether this is the user's currently selected avatar"
    )
    unlocked_at: Optional[str] = Field(
        default=None,
        description="ISO timestamp when avatar was unlocked (null if locked)"
    )
    required_achievement_id: Optional[int] = Field(
        default=None,
        description="Achievement ID required to unlock this avatar (null if default)"
    )
    required_achievement_name: Optional[str] = Field(
        default=None,
        description="Name of required achievement (null if default)"
    )

    class Config:
        from_attributes = True


class AvatarUnlocked(BaseModel):
    """
    Unlocked avatar for user's collection
    Only includes avatars the user has unlocked
    """
    id: int
    name: str
    description: str
    image_url: str
    rarity: str
    is_selected: bool = Field(
        description="Whether this is the user's currently selected avatar"
    )
    unlocked_at: str = Field(
        description="ISO timestamp when avatar was unlocked"
    )

    class Config:
        from_attributes = True


# ========================================
# AVATAR SELECTION RESPONSE
# ========================================

class AvatarInfo(BaseModel):
    """
    Basic avatar information for nested responses
    """
    id: int
    name: str
    description: str
    image_url: str
    rarity: str

    class Config:
        from_attributes = True


class SelectAvatarResponse(BaseModel):
    """
    Response after successfully selecting an avatar
    """
    success: bool = Field(
        description="Whether the avatar selection was successful"
    )
    message: str = Field(
        description="Success message"
    )
    avatar: AvatarInfo = Field(
        description="The selected avatar's information"
    )

    class Config:
        from_attributes = True


# ========================================
# AVATAR STATS RESPONSE
# ========================================

class AvatarRarityStats(BaseModel):
    """
    Count of unlocked avatars by rarity
    """
    common: int = Field(ge=0)
    rare: int = Field(ge=0)
    epic: int = Field(ge=0)
    legendary: int = Field(ge=0)

    class Config:
        from_attributes = True


class AvatarStats(BaseModel):
    """
    User's avatar collection statistics
    """
    total_avatars: int = Field(
        description="Total number of avatars in the game",
        ge=0
    )
    unlocked_avatars: int = Field(
        description="Number of avatars the user has unlocked",
        ge=0
    )
    completion_percentage: float = Field(
        description="Percentage of avatars unlocked (0-100)",
        ge=0,
        le=100
    )
    unlocked_by_rarity: AvatarRarityStats = Field(
        description="Count of unlocked avatars by rarity tier"
    )
    selected_avatar: Optional[AvatarInfo] = Field(
        default=None,
        description="The user's currently selected avatar (null if none selected)"
    )

    class Config:
        from_attributes = True
