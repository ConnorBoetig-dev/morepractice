"""
Achievement Schemas

Pydantic models for achievement-related API requests and responses.
Used by FastAPI for request validation and response serialization.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ========================================
# ACHIEVEMENT RESPONSE SCHEMAS
# ========================================

class AchievementBase(BaseModel):
    """Base achievement schema with common fields"""
    id: int
    name: str
    description: str
    icon: str
    criteria_type: str
    criteria_value: int
    xp_reward: int

    class Config:
        from_attributes = True


class AchievementPublic(AchievementBase):
    """
    Public achievement schema (no user-specific data)
    Used when user is not authenticated
    """
    pass


class AchievementWithProgress(AchievementBase):
    """
    Achievement with user's progress
    Used when user is authenticated
    """
    is_earned: bool = Field(
        description="Whether the user has earned this achievement"
    )
    progress: int = Field(
        description="User's current progress toward this achievement"
    )
    progress_percentage: float = Field(
        description="Progress as percentage (0-100)",
        ge=0,
        le=100
    )
    required_achievement_id: Optional[int] = Field(
        default=None,
        description="Achievement ID required to unlock (if applicable)"
    )
    required_achievement_name: Optional[str] = Field(
        default=None,
        description="Name of required achievement (if applicable)"
    )

    class Config:
        from_attributes = True


class AchievementEarned(BaseModel):
    """
    Earned achievement with timestamp
    Used for displaying user's earned achievements
    """
    id: int
    name: str
    description: str
    icon: str
    xp_reward: int
    earned_at: str = Field(
        description="ISO timestamp when achievement was unlocked"
    )

    class Config:
        from_attributes = True


class AchievementUnlocked(BaseModel):
    """
    Newly unlocked achievement notification
    Returned after quiz submission when achievements are earned
    """
    achievement_id: int
    name: str
    description: str
    icon: str
    xp_reward: int

    class Config:
        from_attributes = True


# ========================================
# ACHIEVEMENT STATS RESPONSE
# ========================================

class AchievementStats(BaseModel):
    """
    User's achievement statistics
    """
    total_achievements: int = Field(
        description="Total number of achievements in the game"
    )
    earned_achievements: int = Field(
        description="Number of achievements the user has earned"
    )
    completion_percentage: float = Field(
        description="Percentage of achievements earned (0-100)",
        ge=0,
        le=100
    )
    total_achievement_xp: int = Field(
        description="Total XP earned from achievements",
        ge=0
    )

    class Config:
        from_attributes = True
