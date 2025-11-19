"""
GAMIFICATION MODELS
Database models for quiz tracking, achievements, avatars, and leaderboards

Enterprise Features:
- Foreign key constraints with proper cascading
- Indexes on foreign keys and query columns
- SQLAlchemy relationships with optimized lazy loading
- CHECK constraints for data validation
- Composite indexes for common query patterns
"""

from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Float, Text,
    ForeignKey, Index, CheckConstraint, UniqueConstraint
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


# ================================================================
# QUIZ TRACKING MODELS
# ================================================================

class QuizAttempt(Base):
    """
    Tracks each completed quiz session

    Used for:
    - User performance history
    - Leaderboard rankings
    - XP/level progression
    - Analytics and progress tracking
    """
    __tablename__ = "quiz_attempts"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Quiz Details
    exam_type = Column(String, nullable=False, index=True)  # security, network, a1101, a1102
    total_questions = Column(Integer, nullable=False)
    correct_answers = Column(Integer, nullable=False)
    score_percentage = Column(Float, nullable=False)  # Calculated: (correct/total) * 100

    # Performance Metrics
    time_taken_seconds = Column(Integer, nullable=True)  # Total time spent on quiz
    xp_earned = Column(Integer, nullable=False, default=0)  # XP awarded for this attempt

    # Timestamps
    completed_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    # Relationships
    # lazy="select": Load answers only when accessed (prevents N+1 queries when loading attempts)
    # cascade="all, delete-orphan": Delete answers when attempt is deleted
    answers = relationship("UserAnswer", back_populates="quiz_attempt", lazy="select", cascade="all, delete-orphan")

    # Indexes for common queries
    __table_args__ = (
        # Composite index for leaderboard queries (filter by exam, order by score/date)
        Index("idx_quiz_exam_score_date", "exam_type", "score_percentage", "completed_at"),
        # Composite index for user history (filter by user, order by date)
        Index("idx_quiz_user_date", "user_id", "completed_at"),
        # CHECK constraints for data validation
        CheckConstraint("total_questions > 0", name="check_total_questions_positive"),
        CheckConstraint("correct_answers >= 0", name="check_correct_answers_non_negative"),
        CheckConstraint("correct_answers <= total_questions", name="check_correct_not_exceeds_total"),
        CheckConstraint("score_percentage >= 0 AND score_percentage <= 100", name="check_score_percentage_range"),
        CheckConstraint("time_taken_seconds >= 0", name="check_time_taken_non_negative"),
        CheckConstraint("xp_earned >= 0", name="check_xp_earned_non_negative"),
    )

    def __repr__(self):
        return f"<QuizAttempt(id={self.id}, user_id={self.user_id}, exam={self.exam_type}, score={self.score_percentage}%)>"


class UserAnswer(Base):
    """
    Tracks individual question answers for each quiz attempt

    Used for:
    - Answer review after quiz
    - Domain-specific performance analytics
    - Identifying weak areas
    - Question difficulty analysis
    """
    __tablename__ = "user_answers"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    quiz_attempt_id = Column(Integer, ForeignKey("quiz_attempts.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="SET NULL"), nullable=True, index=True)

    # Answer Details
    user_answer = Column(String(1), nullable=False)  # A, B, C, or D
    correct_answer = Column(String(1), nullable=False)  # A, B, C, or D
    is_correct = Column(Boolean, nullable=False, index=True)

    # Performance Metrics
    time_spent_seconds = Column(Integer, nullable=True)  # Time spent on this question

    # Timestamp
    answered_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    quiz_attempt = relationship("QuizAttempt", back_populates="answers")

    # Indexes for analytics queries
    __table_args__ = (
        # Composite index for user performance queries
        Index("idx_user_answer_user_correct", "user_id", "is_correct"),
        # Composite index for quiz attempt answers
        Index("idx_user_answer_attempt", "quiz_attempt_id", "is_correct"),
        # Composite index for question analytics
        Index("idx_user_answer_question_correct", "question_id", "is_correct"),
        # CHECK constraints
        CheckConstraint("user_answer IN ('A', 'B', 'C', 'D')", name="check_user_answer_valid"),
        CheckConstraint("correct_answer IN ('A', 'B', 'C', 'D')", name="check_correct_answer_valid"),
        CheckConstraint("time_spent_seconds >= 0", name="check_time_spent_non_negative"),
    )

    def __repr__(self):
        return f"<UserAnswer(id={self.id}, question_id={self.question_id}, correct={self.is_correct})>"


# ================================================================
# ACHIEVEMENT SYSTEM MODELS
# ================================================================

class Achievement(Base):
    """
    Defines available achievements users can unlock

    Examples:
    - "First Steps" - Answer 10 questions correctly
    - "Accuracy Master" - Achieve 90% accuracy on a quiz
    - "Week Warrior" - Maintain a 7-day streak
    """
    __tablename__ = "achievements"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Achievement Details
    name = Column(String, nullable=False, unique=True)
    description = Column(Text, nullable=False)
    icon = Column(String, nullable=False, default="🏆")  # Icon/emoji for achievement
    badge_icon_url = Column(String, nullable=True)  # URL to badge image (deprecated, use icon)

    # Unlock Criteria (stored as metadata, logic in achievement_service)
    criteria_type = Column(String, nullable=False, index=True)  # e.g., "quiz_count", "perfect_quiz", "high_score", "streak", "level", "exam_specific"
    criteria_value = Column(Integer, nullable=False)  # e.g., 100 questions, 7 days, 90%
    criteria_exam_type = Column(String, nullable=True)  # For exam-specific achievements (security, network, a1101, a1102)

    # Rewards
    xp_reward = Column(Integer, nullable=False, default=0)
    unlocks_avatar_id = Column(Integer, ForeignKey("avatars.id", ondelete="SET NULL"), nullable=True)

    # Metadata
    rarity = Column(String, nullable=False, default="common")  # common, rare, epic, legendary
    display_order = Column(Integer, nullable=False, default=0)  # For sorting in UI
    is_hidden = Column(Boolean, nullable=False, default=False)  # Secret achievements
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    # lazy="select": Load users only when accessed
    user_achievements = relationship("UserAchievement", back_populates="achievement", lazy="select")

    # Constraints
    __table_args__ = (
        CheckConstraint("criteria_value > 0", name="check_criteria_value_positive"),
        CheckConstraint("xp_reward >= 0", name="check_xp_reward_non_negative"),
        Index("idx_achievement_criteria_type", "criteria_type"),
    )

    def __repr__(self):
        return f"<Achievement(id={self.id}, name={self.name}, criteria={self.criteria_type}:{self.criteria_value})>"


class UserAchievement(Base):
    """
    Many-to-many relationship: Tracks which achievements each user has unlocked

    Includes timestamp for "Earned on" display and progress tracking
    """
    __tablename__ = "user_achievements"

    # Composite Primary Key (user_id + achievement_id)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, index=True)
    achievement_id = Column(Integer, ForeignKey("achievements.id", ondelete="CASCADE"), primary_key=True, index=True)

    # Metadata
    earned_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    progress_value = Column(Integer, nullable=True)  # Current progress toward achievement (if partially unlocked)

    # Relationships
    achievement = relationship("Achievement", back_populates="user_achievements")

    # Indexes
    __table_args__ = (
        # Index for user's achievement list (sorted by earned date)
        Index("idx_user_achievement_user_earned", "user_id", "earned_at"),
        # Unique constraint enforced by composite primary key
    )

    def __repr__(self):
        return f"<UserAchievement(user_id={self.user_id}, achievement_id={self.achievement_id}, earned={self.earned_at})>"


# ================================================================
# AVATAR SYSTEM MODELS
# ================================================================

class Avatar(Base):
    """
    Defines available avatars users can unlock and display

    Avatars are cosmetic profile customizations earned through achievements
    """
    __tablename__ = "avatars"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Avatar Details
    name = Column(String, nullable=False, unique=True)
    description = Column(Text, nullable=True)
    image_url = Column(String, nullable=False)  # URL to avatar image

    # Unlock Requirements
    is_default = Column(Boolean, nullable=False, default=False)  # Available to all users
    required_achievement_id = Column(Integer, ForeignKey("achievements.id", ondelete="SET NULL"), nullable=True)

    # Metadata
    rarity = Column(String, nullable=True)  # e.g., "common", "rare", "legendary"
    display_order = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    user_avatars = relationship("UserAvatar", back_populates="avatar", lazy="select")

    def __repr__(self):
        return f"<Avatar(id={self.id}, name={self.name}, default={self.is_default})>"


class UserAvatar(Base):
    """
    Many-to-many relationship: Tracks which avatars each user has unlocked
    """
    __tablename__ = "user_avatars"

    # Composite Primary Key
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, index=True)
    avatar_id = Column(Integer, ForeignKey("avatars.id", ondelete="CASCADE"), primary_key=True, index=True)

    # Metadata
    unlocked_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    avatar = relationship("Avatar", back_populates="user_avatars")

    # Indexes
    __table_args__ = (
        Index("idx_user_avatar_user", "user_id", "unlocked_at"),
    )

    def __repr__(self):
        return f"<UserAvatar(user_id={self.user_id}, avatar_id={self.avatar_id})>"
