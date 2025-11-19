"""
Leaderboard Service

Handles leaderboard queries with optimized SQL using window functions.
All queries are designed for performance with proper indexing.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, cast, Float
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from app.models.user import User, UserProfile
from app.models.gamification import QuizAttempt, Avatar


def get_xp_leaderboard(
    db: Session,
    limit: int = 100,
    time_period: str = "all_time",
    current_user_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Get leaderboard sorted by total XP

    Args:
        db: Database session
        limit: Number of top entries to return
        time_period: "all_time", "monthly", or "weekly"
        current_user_id: Optional user ID to include their entry

    Returns:
        dict: Leaderboard data with entries and current user entry
    """

    # Calculate date filter for time-based XP
    date_filter = None
    if time_period == "weekly":
        date_filter = datetime.utcnow() - timedelta(days=7)
    elif time_period == "monthly":
        date_filter = datetime.utcnow() - timedelta(days=30)

    # For all_time, use UserProfile.xp (total accumulated XP)
    if time_period == "all_time":
        # Build the query using total XP from UserProfile
        query = db.query(
            UserProfile.user_id,
            UserProfile.xp,
            UserProfile.level,
            UserProfile.selected_avatar_id,
            User.username
        ).join(
            User, UserProfile.user_id == User.id
        ).order_by(desc(UserProfile.xp))

        # Get top N entries
        top_entries = query.limit(limit).all()

        # Build entries
        entries = []
        for rank, (user_id, xp, level, avatar_id, username) in enumerate(top_entries, start=1):
            avatar_url = None
            if avatar_id:
                avatar = db.query(Avatar).filter(Avatar.id == avatar_id).first()
                if avatar:
                    avatar_url = avatar.image_url

            entries.append({
                "rank": rank,
                "user_id": user_id,
                "username": username,
                "avatar_url": avatar_url,
                "score": xp,
                "level": level,
                "is_current_user": user_id == current_user_id
            })

        # Get current user's entry if not in top N
        current_user_entry = None
        if current_user_id:
            user_in_top = any(entry["user_id"] == current_user_id for entry in entries)

            if not user_in_top:
                # Calculate user's rank
                user_rank = db.query(func.count()).filter(
                    UserProfile.xp > (
                        db.query(UserProfile.xp).filter(
                            UserProfile.user_id == current_user_id
                        ).scalar_subquery()
                    )
                ).scalar() + 1

                # Get user data
                user_data = db.query(
                    UserProfile.user_id,
                    UserProfile.xp,
                    UserProfile.level,
                    UserProfile.selected_avatar_id,
                    User.username
                ).join(
                    User, UserProfile.user_id == User.id
                ).filter(
                    UserProfile.user_id == current_user_id
                ).first()

                if user_data:
                    user_id, xp, level, avatar_id, username = user_data
                    avatar_url = None
                    if avatar_id:
                        avatar = db.query(Avatar).filter(Avatar.id == avatar_id).first()
                        if avatar:
                            avatar_url = avatar.image_url

                    current_user_entry = {
                        "rank": user_rank,
                        "user_id": user_id,
                        "username": username,
                        "avatar_url": avatar_url,
                        "score": xp,
                        "level": level,
                        "is_current_user": True
                    }

        total_users = db.query(UserProfile).count()

    else:
        # For weekly/monthly, sum XP earned from quiz_attempts within time period
        query = db.query(
            QuizAttempt.user_id,
            func.sum(QuizAttempt.xp_earned).label('period_xp'),
            User.username,
            UserProfile.level,
            UserProfile.selected_avatar_id
        ).join(
            User, QuizAttempt.user_id == User.id
        ).join(
            UserProfile, QuizAttempt.user_id == UserProfile.user_id
        ).filter(
            QuizAttempt.completed_at >= date_filter
        ).group_by(
            QuizAttempt.user_id,
            User.username,
            UserProfile.level,
            UserProfile.selected_avatar_id
        ).order_by(desc('period_xp'))

        # Get top N entries
        top_entries = query.limit(limit).all()

        # Build entries
        entries = []
        for rank, (user_id, period_xp, username, level, avatar_id) in enumerate(top_entries, start=1):
            avatar_url = None
            if avatar_id:
                avatar = db.query(Avatar).filter(Avatar.id == avatar_id).first()
                if avatar:
                    avatar_url = avatar.image_url

            entries.append({
                "rank": rank,
                "user_id": user_id,
                "username": username,
                "avatar_url": avatar_url,
                "score": period_xp or 0,
                "level": level,
                "is_current_user": user_id == current_user_id
            })

        # Get current user's entry if not in top N
        current_user_entry = None
        if current_user_id:
            user_in_top = any(entry["user_id"] == current_user_id for entry in entries)

            if not user_in_top:
                # Get user's XP for this period
                user_xp_query = db.query(
                    func.sum(QuizAttempt.xp_earned).label('period_xp')
                ).filter(
                    and_(
                        QuizAttempt.user_id == current_user_id,
                        QuizAttempt.completed_at >= date_filter
                    )
                ).scalar() or 0

                if user_xp_query > 0:
                    # Calculate rank
                    rank_subquery = db.query(QuizAttempt.user_id).filter(
                        QuizAttempt.completed_at >= date_filter
                    ).group_by(QuizAttempt.user_id).having(
                        func.sum(QuizAttempt.xp_earned) > user_xp_query
                    )

                    user_rank = db.query(func.count(func.distinct(QuizAttempt.user_id))).filter(
                        QuizAttempt.user_id.in_(rank_subquery.subquery())
                    ).scalar() + 1

                    # Get user data
                    user_data = db.query(
                        User.username,
                        UserProfile.level,
                        UserProfile.selected_avatar_id
                    ).join(
                        UserProfile, User.id == UserProfile.user_id
                    ).filter(
                        User.id == current_user_id
                    ).first()

                    if user_data:
                        username, level, avatar_id = user_data
                        avatar_url = None
                        if avatar_id:
                            avatar = db.query(Avatar).filter(Avatar.id == avatar_id).first()
                            if avatar:
                                avatar_url = avatar.image_url

                        current_user_entry = {
                            "rank": user_rank,
                            "user_id": current_user_id,
                            "username": username,
                            "avatar_url": avatar_url,
                            "score": user_xp_query,
                            "level": level,
                            "is_current_user": True
                        }

        # Get total users with XP in this period
        total_users = db.query(func.count(func.distinct(QuizAttempt.user_id))).filter(
            QuizAttempt.completed_at >= date_filter
        ).scalar() or 0

    return {
        "entries": entries,
        "current_user_entry": current_user_entry,
        "total_users": total_users,
        "time_period": time_period
    }


def get_quiz_count_leaderboard(
    db: Session,
    limit: int = 100,
    time_period: str = "all_time",
    current_user_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Get leaderboard sorted by total quizzes completed

    Args:
        db: Database session
        limit: Number of top entries to return
        time_period: "all_time", "monthly", or "weekly"
        current_user_id: Optional user ID to include their entry

    Returns:
        dict: Leaderboard data with entries and current user entry
    """

    # Calculate date filter based on time period
    date_filter = None
    if time_period == "weekly":
        date_filter = datetime.utcnow() - timedelta(days=7)
    elif time_period == "monthly":
        date_filter = datetime.utcnow() - timedelta(days=30)

    # Build query with quiz count aggregation
    query = db.query(
        QuizAttempt.user_id,
        func.count(QuizAttempt.id).label('quiz_count'),
        User.username,
        UserProfile.level,
        UserProfile.selected_avatar_id
    ).join(
        User, QuizAttempt.user_id == User.id
    ).join(
        UserProfile, QuizAttempt.user_id == UserProfile.user_id
    )

    # Apply time filter
    if date_filter:
        query = query.filter(QuizAttempt.completed_at >= date_filter)

    # Group and order
    query = query.group_by(
        QuizAttempt.user_id,
        User.username,
        UserProfile.level,
        UserProfile.selected_avatar_id
    ).order_by(desc('quiz_count'))

    # Get top N entries
    top_entries = query.limit(limit).all()

    # Build entries with avatars
    entries = []
    for rank, (user_id, quiz_count, username, level, avatar_id) in enumerate(top_entries, start=1):
        avatar_url = None
        if avatar_id:
            avatar = db.query(Avatar).filter(Avatar.id == avatar_id).first()
            if avatar:
                avatar_url = avatar.image_url

        entries.append({
            "rank": rank,
            "user_id": user_id,
            "username": username,
            "avatar_url": avatar_url,
            "score": quiz_count,  # Quiz count is the score
            "level": level,
            "is_current_user": user_id == current_user_id
        })

    # Get current user's entry if not in top N
    current_user_entry = None
    if current_user_id:
        user_in_top = any(entry["user_id"] == current_user_id for entry in entries)

        if not user_in_top:
            # Get user's quiz count
            user_query = db.query(
                func.count(QuizAttempt.id).label('quiz_count')
            ).filter(QuizAttempt.user_id == current_user_id)

            if date_filter:
                user_query = user_query.filter(QuizAttempt.completed_at >= date_filter)

            user_quiz_count = user_query.scalar() or 0

            # Calculate rank
            rank_query = db.query(func.count(func.distinct(QuizAttempt.user_id))).filter(
                QuizAttempt.user_id.in_(
                    db.query(QuizAttempt.user_id).group_by(QuizAttempt.user_id).having(
                        func.count(QuizAttempt.id) > user_quiz_count
                    )
                )
            )

            if date_filter:
                rank_query = rank_query.filter(QuizAttempt.completed_at >= date_filter)

            user_rank = rank_query.scalar() + 1

            # Get user data
            user_data = db.query(
                User.username,
                UserProfile.level,
                UserProfile.selected_avatar_id
            ).join(
                UserProfile, User.id == UserProfile.user_id
            ).filter(
                User.id == current_user_id
            ).first()

            if user_data:
                username, level, avatar_id = user_data
                avatar_url = None
                if avatar_id:
                    avatar = db.query(Avatar).filter(Avatar.id == avatar_id).first()
                    if avatar:
                        avatar_url = avatar.image_url

                current_user_entry = {
                    "rank": user_rank,
                    "user_id": current_user_id,
                    "username": username,
                    "avatar_url": avatar_url,
                    "score": user_quiz_count,
                    "level": level,
                    "is_current_user": True
                }

    # Get total user count (users with at least one quiz)
    total_query = db.query(func.count(func.distinct(QuizAttempt.user_id)))
    if date_filter:
        total_query = total_query.filter(QuizAttempt.completed_at >= date_filter)
    total_users = total_query.scalar() or 0

    return {
        "entries": entries,
        "current_user_entry": current_user_entry,
        "total_users": total_users,
        "time_period": time_period
    }


def get_accuracy_leaderboard(
    db: Session,
    limit: int = 100,
    minimum_quizzes: int = 1,
    time_period: str = "all_time",
    current_user_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Get leaderboard sorted by average accuracy
    Shows users with at least 1 quiz (accuracy calculated from first quiz)

    Args:
        db: Database session
        limit: Number of top entries to return
        minimum_quizzes: Minimum quizzes required to qualify (default: 1)
        time_period: "all_time", "monthly", or "weekly"
        current_user_id: Optional user ID to include their entry

    Returns:
        dict: Leaderboard data with entries and current user entry
    """

    # Calculate date filter
    date_filter = None
    if time_period == "weekly":
        date_filter = datetime.utcnow() - timedelta(days=7)
    elif time_period == "monthly":
        date_filter = datetime.utcnow() - timedelta(days=30)

    # Build query
    query = db.query(
        QuizAttempt.user_id,
        func.avg(QuizAttempt.score_percentage).label('avg_accuracy'),
        func.count(QuizAttempt.id).label('quiz_count'),
        User.username,
        UserProfile.level,
        UserProfile.selected_avatar_id
    ).join(
        User, QuizAttempt.user_id == User.id
    ).join(
        UserProfile, QuizAttempt.user_id == UserProfile.user_id
    )

    # Apply time filter
    if date_filter:
        query = query.filter(QuizAttempt.completed_at >= date_filter)

    # Group by user
    query = query.group_by(
        QuizAttempt.user_id,
        User.username,
        UserProfile.level,
        UserProfile.selected_avatar_id
    )

    # Filter users with minimum quizzes
    query = query.having(func.count(QuizAttempt.id) >= minimum_quizzes)

    # Order by average accuracy
    query = query.order_by(desc('avg_accuracy'))

    # Get top N entries
    top_entries = query.limit(limit).all()

    # Build entries
    entries = []
    for rank, (user_id, avg_accuracy, quiz_count, username, level, avatar_id) in enumerate(top_entries, start=1):
        avatar_url = None
        if avatar_id:
            avatar = db.query(Avatar).filter(Avatar.id == avatar_id).first()
            if avatar:
                avatar_url = avatar.image_url

        entries.append({
            "rank": rank,
            "user_id": user_id,
            "username": username,
            "avatar_url": avatar_url,
            "score": int(round(avg_accuracy)),  # Round accuracy to int
            "level": level,
            "is_current_user": user_id == current_user_id
        })

    # Get current user's entry if not in top N
    current_user_entry = None
    if current_user_id:
        user_in_top = any(entry["user_id"] == current_user_id for entry in entries)

        if not user_in_top:
            # Get user's average accuracy and quiz count
            user_query = db.query(
                func.avg(QuizAttempt.score_percentage).label('avg_accuracy'),
                func.count(QuizAttempt.id).label('quiz_count')
            ).filter(QuizAttempt.user_id == current_user_id)

            if date_filter:
                user_query = user_query.filter(QuizAttempt.completed_at >= date_filter)

            user_stats = user_query.first()

            if user_stats and user_stats.quiz_count >= minimum_quizzes:
                # Get user data
                user_data = db.query(
                    User.username,
                    UserProfile.level,
                    UserProfile.selected_avatar_id
                ).join(
                    UserProfile, User.id == UserProfile.user_id
                ).filter(
                    User.id == current_user_id
                ).first()

                if user_data:
                    username, level, avatar_id = user_data
                    avatar_url = None
                    if avatar_id:
                        avatar = db.query(Avatar).filter(Avatar.id == avatar_id).first()
                        if avatar:
                            avatar_url = avatar.image_url

                    # Calculate rank (number of users with better accuracy + 1)
                    rank_subquery = db.query(QuizAttempt.user_id).group_by(
                        QuizAttempt.user_id
                    ).having(
                        and_(
                            func.avg(QuizAttempt.score_percentage) > user_stats.avg_accuracy,
                            func.count(QuizAttempt.id) >= minimum_quizzes
                        )
                    )

                    # Apply time filter to rank query if needed
                    if date_filter:
                        rank_subquery = rank_subquery.filter(QuizAttempt.completed_at >= date_filter)

                    # Count users with better accuracy
                    user_rank = db.query(func.count(func.distinct(QuizAttempt.user_id))).filter(
                        QuizAttempt.user_id.in_(rank_subquery.subquery())
                    ).scalar() + 1

                    current_user_entry = {
                        "rank": user_rank,
                        "user_id": current_user_id,
                        "username": username,
                        "avatar_url": avatar_url,
                        "score": int(round(user_stats.avg_accuracy)),
                        "level": level,
                        "is_current_user": True
                    }

    # Get total qualified users (with time filter if applicable)
    total_query = db.query(QuizAttempt.user_id).group_by(QuizAttempt.user_id).having(
        func.count(QuizAttempt.id) >= minimum_quizzes
    )

    # Apply time filter
    if date_filter:
        total_query = total_query.filter(QuizAttempt.completed_at >= date_filter)

    # Count the groups
    total_users = total_query.count()

    return {
        "entries": entries,
        "current_user_entry": current_user_entry,
        "total_users": total_users,
        "time_period": time_period,
        "minimum_quizzes": minimum_quizzes
    }


def get_streak_leaderboard(
    db: Session,
    limit: int = 100,
    current_user_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Get leaderboard sorted by current study streak

    Args:
        db: Database session
        limit: Number of top entries to return
        current_user_id: Optional user ID to include their entry

    Returns:
        dict: Leaderboard data with entries and current user entry
    """

    # Query users with active streaks
    query = db.query(
        UserProfile.user_id,
        UserProfile.study_streak_current,
        UserProfile.level,
        UserProfile.selected_avatar_id,
        User.username
    ).join(
        User, UserProfile.user_id == User.id
    ).filter(
        UserProfile.study_streak_current > 0
    ).order_by(
        desc(UserProfile.study_streak_current)
    )

    # Get top N entries
    top_entries = query.limit(limit).all()

    # Build entries
    entries = []
    for rank, (user_id, streak, level, avatar_id, username) in enumerate(top_entries, start=1):
        avatar_url = None
        if avatar_id:
            avatar = db.query(Avatar).filter(Avatar.id == avatar_id).first()
            if avatar:
                avatar_url = avatar.image_url

        entries.append({
            "rank": rank,
            "user_id": user_id,
            "username": username,
            "avatar_url": avatar_url,
            "score": streak,  # Streak count is the score
            "level": level,
            "is_current_user": user_id == current_user_id
        })

    # Get current user's entry if not in top N
    current_user_entry = None
    if current_user_id:
        user_in_top = any(entry["user_id"] == current_user_id for entry in entries)

        if not user_in_top:
            # Get user data
            user_data = db.query(
                UserProfile.study_streak_current,
                UserProfile.level,
                UserProfile.selected_avatar_id,
                User.username
            ).join(
                User, UserProfile.user_id == User.id
            ).filter(
                UserProfile.user_id == current_user_id
            ).first()

            if user_data and user_data.study_streak_current > 0:
                streak, level, avatar_id, username = user_data

                # Calculate rank
                user_rank = db.query(func.count()).filter(
                    UserProfile.study_streak_current > streak
                ).scalar() + 1

                avatar_url = None
                if avatar_id:
                    avatar = db.query(Avatar).filter(Avatar.id == avatar_id).first()
                    if avatar:
                        avatar_url = avatar.image_url

                current_user_entry = {
                    "rank": user_rank,
                    "user_id": current_user_id,
                    "username": username,
                    "avatar_url": avatar_url,
                    "score": streak,
                    "level": level,
                    "is_current_user": True
                }

    # Get total users with streaks
    total_users = db.query(UserProfile).filter(
        UserProfile.study_streak_current > 0
    ).count()

    return {
        "entries": entries,
        "current_user_entry": current_user_entry,
        "total_users": total_users,
        "time_period": "current"
    }


