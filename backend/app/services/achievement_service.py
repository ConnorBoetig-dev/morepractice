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
from app.models.user import UserProfile, User
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
            - current_level: User's current level
            - exam_counts: Dict of quiz counts per exam type
            - domains_with_10_plus: Number of exam types with 10+ quizzes
            - is_verified: Whether user has verified their email
    """

    # Get user and profile
    user = db.query(User).filter(User.id == user_id).first()
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

    # Count how many exam types have 10+ quizzes (for multi_domain achievement)
    domains_with_10_plus = sum(1 for count in exam_counts.values() if count >= 10)

    return {
        "total_quizzes": total_quizzes,
        "perfect_quizzes": perfect_quizzes,
        "high_score_quizzes": high_score_quizzes,
        "correct_answers": correct_answers,
        "current_level": profile.level if profile else 1,
        "exam_counts": exam_counts,
        "domains_with_10_plus": domains_with_10_plus,
        "is_verified": user.is_verified if user else False
    }


def check_achievement_earned(
    achievement: Achievement,
    stats: Dict[str, Any],
    exam_type: str = None
) -> bool:
    """
    Check if user has met the criteria for a specific achievement

    Supported criteria types:
    - email_verified: User has verified their email
    - quiz_completed: Total quizzes completed
    - perfect_quiz: Quizzes with 100% score
    - high_score_quiz: Quizzes with 90%+ score
    - correct_answers: Total correct answers over lifetime
    - level_reached: User has reached specific level
    - exam_specific: Completed N quizzes in any single exam type
    - multi_domain: Completed 10+ quizzes in at least N different exam types

    Args:
        achievement: Achievement to check
        stats: User statistics from get_user_stats()
        exam_type: Current exam type (optional, for context)

    Returns:
        bool: True if achievement criteria is met
    """

    criteria_type = achievement.criteria_type
    criteria_value = achievement.criteria_value

    # Email verification achievement
    if criteria_type == "email_verified":
        return stats["is_verified"]

    # Quiz completion achievements
    elif criteria_type == "quiz_completed":
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

    # Level achievements
    elif criteria_type == "level_reached":
        return stats["current_level"] >= criteria_value

    # Exam-specific achievements (e.g., "Complete 10 quizzes in one domain")
    # Check if ANY exam type has reached the criteria
    elif criteria_type == "exam_specific":
        # If criteria_exam_type is specified, check that specific exam
        if achievement.criteria_exam_type:
            exam_count = stats["exam_counts"].get(achievement.criteria_exam_type, 0)
            return exam_count >= criteria_value
        else:
            # Otherwise, check if ANY exam type has reached the criteria
            for exam_count in stats["exam_counts"].values():
                if exam_count >= criteria_value:
                    return True
            return False

    # Multi-domain achievements (e.g., "Complete 10+ quizzes in 2 different domains")
    # criteria_value = minimum number of domains required (e.g., 2)
    elif criteria_type == "multi_domain":
        # Check if user has completed 10+ quizzes in at least N domains
        # The criteria_value represents the number of domains, not quiz count
        # We hardcode 10 as the minimum per domain
        return stats["domains_with_10_plus"] >= 2  # At least 2 domains with 10+ quizzes

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

    from app.models.gamification import Avatar, UserAvatar

    # Get user's current stats
    stats = get_user_stats(db, user_id)

    # Get all achievements ordered by ID (natural order, no display_order)
    all_achievements = db.query(Achievement).order_by(Achievement.id).all()

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
                icon=achievement.icon,
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
            # Query for avatars that require this achievement
            avatar_to_unlock = db.query(Avatar).filter(
                Avatar.required_achievement_id == achievement.id
            ).first()

            if avatar_to_unlock:
                # Check if user already has this avatar
                existing_user_avatar = db.query(UserAvatar).filter(
                    UserAvatar.user_id == user_id,
                    UserAvatar.avatar_id == avatar_to_unlock.id
                ).first()

                if not existing_user_avatar:
                    # Unlock the avatar
                    user_avatar = UserAvatar(
                        user_id=user_id,
                        avatar_id=avatar_to_unlock.id,
                        unlocked_at=datetime.utcnow()
                    )
                    db.add(user_avatar)

    # Commit all achievement awards
    if newly_unlocked:
        db.commit()

    return newly_unlocked


def get_all_achievements(db: Session, user_id: int = None) -> List[Dict[str, Any]]:
    """
    Get all achievements, optionally with user progress

    Args:
        db: Database session
        user_id: Optional user ID to include earned status and progress

    Returns:
        List of achievements with earned status and progress if user_id provided
    """

    # Get all achievements ordered by ID (natural order)
    achievements = db.query(Achievement).order_by(Achievement.id).all()

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

            # Calculate progress toward achievement
            progress = calculate_achievement_progress(achievement, stats)

            result.append({
                "id": achievement.id,
                "name": achievement.name,
                "description": achievement.description,
                "icon": achievement.icon,
                "criteria_type": achievement.criteria_type,
                "criteria_value": achievement.criteria_value,
                "xp_reward": achievement.xp_reward,
                "is_earned": is_earned,
                "progress": progress,
                "progress_percentage": min(100.0, (progress / achievement.criteria_value * 100))
                                      if achievement.criteria_value > 0 else 100.0
            })
    else:
        # No user context - return all achievements without progress
        for achievement in achievements:
            result.append({
                "id": achievement.id,
                "name": achievement.name,
                "description": achievement.description,
                "icon": achievement.icon,
                "criteria_type": achievement.criteria_type,
                "criteria_value": achievement.criteria_value,
                "xp_reward": achievement.xp_reward,
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

    if criteria_type == "email_verified":
        return 1 if stats["is_verified"] else 0
    elif criteria_type == "quiz_completed":
        return stats["total_quizzes"]
    elif criteria_type == "perfect_quiz":
        return stats["perfect_quizzes"]
    elif criteria_type == "high_score_quiz":
        return stats["high_score_quizzes"]
    elif criteria_type == "correct_answers":
        return stats["correct_answers"]
    elif criteria_type == "level_reached":
        return stats["current_level"]
    elif criteria_type == "exam_specific":
        # If specific exam type is set, return count for that exam
        if achievement.criteria_exam_type:
            return stats["exam_counts"].get(achievement.criteria_exam_type, 0)
        else:
            # Return the highest count among all exam types
            if stats["exam_counts"]:
                return max(stats["exam_counts"].values())
            return 0
    elif criteria_type == "multi_domain":
        # Return number of domains with 10+ quizzes
        return stats["domains_with_10_plus"]

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
            "icon": achievement.icon,
            "xp_reward": achievement.xp_reward,
            "earned_at": earned_at.isoformat() if earned_at else None
        }
        for achievement, earned_at in user_achievements
    ]
