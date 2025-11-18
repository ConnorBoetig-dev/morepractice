"""
Leaderboard Schemas

Pydantic models for leaderboard API requests and responses.
Used by FastAPI for request validation and response serialization.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ========================================
# LEADERBOARD ENTRY SCHEMAS
# ========================================

class LeaderboardEntry(BaseModel):
    """
    Single entry in a leaderboard
    """
    rank: int = Field(
        description="User's rank position (1 = first place)",
        ge=1
    )
    user_id: int = Field(
        description="User ID"
    )
    username: str = Field(
        description="User's display name"
    )
    avatar_url: Optional[str] = Field(
        default=None,
        description="URL to user's selected avatar image"
    )
    score: int = Field(
        description="User's score for this leaderboard metric",
        ge=0
    )
    level: int = Field(
        description="User's current level",
        ge=1
    )
    is_current_user: bool = Field(
        default=False,
        description="Whether this entry is the current authenticated user"
    )

    class Config:
        from_attributes = True


# ========================================
# LEADERBOARD RESPONSE SCHEMAS
# ========================================

class XPLeaderboardResponse(BaseModel):
    """
    Leaderboard sorted by total XP
    """
    leaderboard_type: str = Field(
        default="xp",
        description="Type of leaderboard"
    )
    time_period: str = Field(
        description="Time period for this leaderboard (all_time, monthly, weekly)"
    )
    total_users: int = Field(
        description="Total number of users in the leaderboard",
        ge=0
    )
    entries: List[LeaderboardEntry] = Field(
        description="List of leaderboard entries (sorted by rank)"
    )
    current_user_entry: Optional[LeaderboardEntry] = Field(
        default=None,
        description="Current user's entry (if authenticated and not in top entries)"
    )

    class Config:
        from_attributes = True


class QuizCountLeaderboardResponse(BaseModel):
    """
    Leaderboard sorted by total quizzes completed
    """
    leaderboard_type: str = Field(
        default="quiz_count",
        description="Type of leaderboard"
    )
    time_period: str = Field(
        description="Time period for this leaderboard (all_time, monthly, weekly)"
    )
    total_users: int = Field(
        description="Total number of users in the leaderboard",
        ge=0
    )
    entries: List[LeaderboardEntry] = Field(
        description="List of leaderboard entries (sorted by rank)"
    )
    current_user_entry: Optional[LeaderboardEntry] = Field(
        default=None,
        description="Current user's entry (if authenticated and not in top entries)"
    )

    class Config:
        from_attributes = True


class AccuracyLeaderboardResponse(BaseModel):
    """
    Leaderboard sorted by average accuracy (min 10 quizzes to qualify)
    """
    leaderboard_type: str = Field(
        default="accuracy",
        description="Type of leaderboard"
    )
    time_period: str = Field(
        description="Time period for this leaderboard (all_time, monthly, weekly)"
    )
    total_users: int = Field(
        description="Total number of users in the leaderboard",
        ge=0
    )
    minimum_quizzes: int = Field(
        default=10,
        description="Minimum number of quizzes required to appear on this leaderboard"
    )
    entries: List[LeaderboardEntry] = Field(
        description="List of leaderboard entries (sorted by rank)"
    )
    current_user_entry: Optional[LeaderboardEntry] = Field(
        default=None,
        description="Current user's entry (if authenticated and not in top entries)"
    )

    class Config:
        from_attributes = True


class StreakLeaderboardResponse(BaseModel):
    """
    Leaderboard sorted by current study streak
    """
    leaderboard_type: str = Field(
        default="streak",
        description="Type of leaderboard"
    )
    time_period: str = Field(
        default="current",
        description="Time period (always 'current' for streaks)"
    )
    total_users: int = Field(
        description="Total number of users in the leaderboard",
        ge=0
    )
    entries: List[LeaderboardEntry] = Field(
        description="List of leaderboard entries (sorted by rank)"
    )
    current_user_entry: Optional[LeaderboardEntry] = Field(
        default=None,
        description="Current user's entry (if authenticated and not in top entries)"
    )

    class Config:
        from_attributes = True


class ExamSpecificLeaderboardResponse(BaseModel):
    """
    Leaderboard for a specific exam type (e.g., Security+, Network+)
    """
    leaderboard_type: str = Field(
        default="exam_specific",
        description="Type of leaderboard"
    )
    exam_type: str = Field(
        description="Exam type this leaderboard is for"
    )
    time_period: str = Field(
        description="Time period for this leaderboard (all_time, monthly, weekly)"
    )
    total_users: int = Field(
        description="Total number of users in the leaderboard",
        ge=0
    )
    entries: List[LeaderboardEntry] = Field(
        description="List of leaderboard entries (sorted by rank)"
    )
    current_user_entry: Optional[LeaderboardEntry] = Field(
        default=None,
        description="Current user's entry (if authenticated and not in top entries)"
    )

    class Config:
        from_attributes = True


# ========================================
# LEADERBOARD STATS
# ========================================

class UserLeaderboardStats(BaseModel):
    """
    User's current standings across all leaderboards
    """
    xp_rank: Optional[int] = Field(
        default=None,
        description="User's rank in XP leaderboard (null if not ranked)"
    )
    quiz_count_rank: Optional[int] = Field(
        default=None,
        description="User's rank in quiz count leaderboard (null if not ranked)"
    )
    accuracy_rank: Optional[int] = Field(
        default=None,
        description="User's rank in accuracy leaderboard (null if not qualified)"
    )
    streak_rank: Optional[int] = Field(
        default=None,
        description="User's rank in streak leaderboard (null if no streak)"
    )
    total_users: int = Field(
        description="Total number of users in the system",
        ge=0
    )

    class Config:
        from_attributes = True
