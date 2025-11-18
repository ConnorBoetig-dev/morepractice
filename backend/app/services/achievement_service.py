"""
Achievement Service

Handles achievement checking and unlocking logic.
Called after quiz submission to check for newly earned achievements.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any
from datetime import datetime, timedelta

from app.models.gamification import (
    Achievement,
    UserAchievement,
    QuizAttempt,
    UserAnswer
)
from app.models.user import UserProfile
from app.schemas.quiz import AchievementUnlocked


def get_user_stats(db: Session, user_id: int) -> Dict[str, Any]:
    """
    Get user's current stats for achievement checking

    Returns:
        dict: User statistics including:
            - total_quizzes: Total quizzes completed
            - perfect_quizzes: Quizzes with 100% score
            - high_score_quizzes: Quizzes with 90%+ score
            - correct_answers: Total correct answers
            - current_streak: Current study streak
            - current_level: User's current level
            - exam_counts: Dict of quiz counts per exam type
    """

    # Get user profile
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

    # Total quizzes completed
    total_quizzes = db.query(QuizAttempt).filter(
        QuizAttempt.user_id == user_id
    ).count()

    # Perfect quizzes (100% score)
    perfect_quizzes = db.query(QuizAttempt).filter(
        QuizAttempt.user_id == user_id,
        QuizAttempt.score_percentage == 100.0
    ).count()

    # High score quizzes (90%+ score)
    high_score_quizzes = db.query(QuizAttempt).filter(
        QuizAttempt.user_id == user_id,
        QuizAttempt.score_percentage >= 90.0
    ).count()

    # Total correct answers
    correct_answers = db.query(func.sum(QuizAttempt.correct_answers)).filter(
        QuizAttempt.user_id == user_id
    ).scalar() or 0

    # Quiz counts per exam type
    exam_counts_query = db.query(
        QuizAttempt.exam_type,
        func.count(QuizAttempt.id).label('count')
    ).filter(
        QuizAttempt.user_id == user_id
    ).group_by(QuizAttempt.exam_type).all()

    exam_counts = {exam_type: count for exam_type, count in exam_counts_query}

    return {
        "total_quizzes": total_quizzes,
        "perfect_quizzes": perfect_quizzes,
        "high_score_quizzes": high_score_quizzes,
        "correct_answers": correct_answers,
        "current_streak": profile.study_streak_current if profile else 0,
        "current_level": profile.level if profile else 1,
        "exam_counts": exam_counts
    }


def check_achievement_earned(
    achievement: Achievement,
    stats: Dict[str, Any],
    exam_type: str = None
) -> bool:
    """
    Check if user has met the criteria for a specific achievement

    Args:
        achievement: Achievement to check
        stats: User statistics from get_user_stats()
        exam_type: Current exam type (for exam_specific achievements)

    Returns:
        bool: True if achievement criteria is met
    """

    criteria_type = achievement.criteria_type
    criteria_value = achievement.criteria_value

    # Quiz completion achievements
    if criteria_type == "quiz_completed":
        return stats["total_quizzes"] >= criteria_value

    # Perfect quiz achievements (100% score)
    elif criteria_type == "perfect_quiz":
        return stats["perfect_quizzes"] >= criteria_value

    # High score achievements (90%+ score)
    elif criteria_type == "high_score_quiz":
        return stats["high_score_quizzes"] >= criteria_value

    # Correct answers achievements
    elif criteria_type == "correct_answers":
        return stats["correct_answers"] >= criteria_value

    # Study streak achievements
    elif criteria_type == "study_streak":
        return stats["current_streak"] >= criteria_value

    # Level achievements
    elif criteria_type == "level_reached":
        return stats["current_level"] >= criteria_value

    # Exam-specific achievements (e.g., "Complete 50 A+ Core 1 quizzes")
    elif criteria_type == "exam_specific":
        # For exam-specific achievements, check the count for that specific exam
        # The exam type is encoded in the achievement name
        # We'll check if any exam type has reached the criteria

        # Map achievement names to exam types
        exam_mapping = {
            "A+ Core 1": "a_plus_core_1",
            "A+ Core 2": "a_plus_core_2",
            "Network+": "network_plus",
            "Security+": "security_plus"
        }

        # Find which exam this achievement is for
        for exam_name, exam_key in exam_mapping.items():
            if exam_name in achievement.name:
                exam_count = stats["exam_counts"].get(exam_key, 0)
                return exam_count >= criteria_value

        return False

    # Unknown criteria type
    return False


def check_and_award_achievements(
    db: Session,
    user_id: int,
    exam_type: str = None
) -> List[AchievementUnlocked]:
    """
    Check for newly unlocked achievements and award them

    This is called after quiz submission to check if the user has unlocked
    any new achievements based on their updated stats.

    Args:
        db: Database session
        user_id: User ID to check achievements for
        exam_type: Exam type of the quiz just completed (optional)

    Returns:
        List[AchievementUnlocked]: List of newly unlocked achievements
    """

    # Get user's current stats
    stats = get_user_stats(db, user_id)

    # Get all achievements
    all_achievements = db.query(Achievement).order_by(Achievement.display_order).all()

    # Get already earned achievement IDs
    earned_achievement_ids = db.query(UserAchievement.achievement_id).filter(
        UserAchievement.user_id == user_id
    ).all()
    earned_ids = {aid[0] for aid in earned_achievement_ids}

    # Check each achievement
    newly_unlocked: List[AchievementUnlocked] = []

    for achievement in all_achievements:
        # Skip if already earned
        if achievement.id in earned_ids:
            continue

        # Check if criteria is met
        if check_achievement_earned(achievement, stats, exam_type):
            # Award the achievement
            user_achievement = UserAchievement(
                user_id=user_id,
                achievement_id=achievement.id,
                earned_at=datetime.utcnow(),
                progress_value=None  # Could track progress for partial achievements
            )
            db.add(user_achievement)

            # Add to newly unlocked list
            newly_unlocked.append(AchievementUnlocked(
                achievement_id=achievement.id,
                name=achievement.name,
                description=achievement.description,
                badge_icon_url=achievement.badge_icon_url,
                xp_reward=achievement.xp_reward
            ))

            # Award XP for the achievement
            profile = db.query(UserProfile).filter(
                UserProfile.user_id == user_id
            ).first()

            if profile:
                profile.xp += achievement.xp_reward
                # Recalculate level (in case XP from achievement causes level up)
                from app.services.quiz_service import calculate_level_from_xp
                profile.level = calculate_level_from_xp(profile.xp)

            # Check if this achievement unlocks an avatar
            if achievement.unlocks_avatar_id:
                from app.services.avatar_service import unlock_avatar_from_achievement
                unlock_avatar_from_achievement(db, user_id, achievement.id)

    # Commit all achievement awards
    if newly_unlocked:
        db.commit()

    return newly_unlocked


def get_all_achievements(db: Session, user_id: int = None) -> List[Dict[str, Any]]:
    """
    Get all achievements, optionally filtered for a specific user

    Args:
        db: Database session
        user_id: Optional user ID to include earned status

    Returns:
        List of achievements with earned status if user_id provided
    """

    # Get all achievements (including hidden ones if earned)
    achievements = db.query(Achievement).order_by(Achievement.display_order).all()

    result = []

    if user_id:
        # Get user's earned achievements
        earned_achievement_ids = db.query(UserAchievement.achievement_id).filter(
            UserAchievement.user_id == user_id
        ).all()
        earned_ids = {aid[0] for aid in earned_achievement_ids}

        # Get user's stats for progress tracking
        stats = get_user_stats(db, user_id)

        for achievement in achievements:
            is_earned = achievement.id in earned_ids

            # Skip hidden achievements that haven't been earned
            if achievement.is_hidden and not is_earned:
                continue

            # Calculate progress toward achievement
            progress = calculate_achievement_progress(achievement, stats)

            result.append({
                "id": achievement.id,
                "name": achievement.name,
                "description": achievement.description,
                "badge_icon_url": achievement.badge_icon_url,
                "criteria_type": achievement.criteria_type,
                "criteria_value": achievement.criteria_value,
                "xp_reward": achievement.xp_reward,
                "is_earned": is_earned,
                "is_hidden": achievement.is_hidden,
                "progress": progress,
                "progress_percentage": min(100.0, (progress / achievement.criteria_value * 100))
                                      if achievement.criteria_value > 0 else 100.0
            })
    else:
        # No user context - return all non-hidden achievements
        for achievement in achievements:
            if not achievement.is_hidden:
                result.append({
                    "id": achievement.id,
                    "name": achievement.name,
                    "description": achievement.description,
                    "badge_icon_url": achievement.badge_icon_url,
                    "criteria_type": achievement.criteria_type,
                    "criteria_value": achievement.criteria_value,
                    "xp_reward": achievement.xp_reward,
                    "is_hidden": False
                })

    return result


def calculate_achievement_progress(
    achievement: Achievement,
    stats: Dict[str, Any]
) -> int:
    """
    Calculate user's progress toward an achievement

    Args:
        achievement: Achievement to check progress for
        stats: User statistics

    Returns:
        int: Current progress value
    """

    criteria_type = achievement.criteria_type

    if criteria_type == "quiz_completed":
        return stats["total_quizzes"]
    elif criteria_type == "perfect_quiz":
        return stats["perfect_quizzes"]
    elif criteria_type == "high_score_quiz":
        return stats["high_score_quizzes"]
    elif criteria_type == "correct_answers":
        return stats["correct_answers"]
    elif criteria_type == "study_streak":
        return stats["current_streak"]
    elif criteria_type == "level_reached":
        return stats["current_level"]
    elif criteria_type == "exam_specific":
        # Find the relevant exam type
        exam_mapping = {
            "A+ Core 1": "a_plus_core_1",
            "A+ Core 2": "a_plus_core_2",
            "Network+": "network_plus",
            "Security+": "security_plus"
        }

        for exam_name, exam_key in exam_mapping.items():
            if exam_name in achievement.name:
                return stats["exam_counts"].get(exam_key, 0)

        return 0

    return 0


def get_user_achievements(db: Session, user_id: int) -> List[Dict[str, Any]]:
    """
    Get all achievements earned by a specific user

    Args:
        db: Database session
        user_id: User ID

    Returns:
        List of earned achievements with earned_at timestamp
    """

    user_achievements = db.query(
        Achievement, UserAchievement.earned_at
    ).join(
        UserAchievement,
        Achievement.id == UserAchievement.achievement_id
    ).filter(
        UserAchievement.user_id == user_id
    ).order_by(
        UserAchievement.earned_at.desc()
    ).all()

    return [
        {
            "id": achievement.id,
            "name": achievement.name,
            "description": achievement.description,
            "badge_icon_url": achievement.badge_icon_url,
            "xp_reward": achievement.xp_reward,
            "earned_at": earned_at.isoformat() if earned_at else None
        }
        for achievement, earned_at in user_achievements
    ]
