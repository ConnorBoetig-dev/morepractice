"""
BACKGROUND TASKS - Scheduled jobs for periodic maintenance

Uses APScheduler to run background tasks within the FastAPI application.
Runs independently of HTTP requests.

Current tasks:
1. Daily streak reset - Resets study streaks for inactive users
"""

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import date, timedelta
import logging

from app.db.session import get_db
from app.models.user import UserProfile

# Configure logging
logger = logging.getLogger(__name__)


def reset_expired_streaks():
    """
    Reset study streaks for users who haven't been active for 2+ days

    This runs daily at midnight UTC to maintain streak accuracy.

    Logic:
    - If last_activity_date is None: skip (no streak to reset)
    - If last_activity_date is today or yesterday: keep streak (still active)
    - If last_activity_date is 2+ days ago: reset current streak to 0

    Note: We DON'T reset longest_streak - it's a personal record
    """
    logger.info("Starting daily streak reset task")

    try:
        # Get database session
        db = next(get_db())

        # Calculate cutoff date (2 days ago)
        # If today is Wednesday, cutoff is Monday
        # Anyone active on Monday or Tuesday keeps their streak
        # Anyone active on Sunday or earlier loses their streak
        today = date.today()
        cutoff_date = today - timedelta(days=2)

        # Find all users with expired streaks
        # Conditions:
        # 1. last_activity_date is not None (user has been active before)
        # 2. last_activity_date < cutoff_date (more than 1 day gap)
        # 3. study_streak_current > 0 (has an active streak to reset)
        expired_profiles = db.query(UserProfile).filter(
            UserProfile.last_activity_date.isnot(None),
            UserProfile.last_activity_date < cutoff_date,
            UserProfile.study_streak_current > 0
        ).all()

        # Reset streaks to 0
        count = 0
        for profile in expired_profiles:
            old_streak = profile.study_streak_current
            profile.study_streak_current = 0
            count += 1
            logger.debug(
                f"Reset streak for user {profile.user_id}: "
                f"{old_streak} -> 0 (last active: {profile.last_activity_date})"
            )

        # Save all changes
        if count > 0:
            db.commit()
            logger.info(f"Reset {count} expired study streaks")
        else:
            logger.info("No expired streaks to reset")

    except Exception as e:
        logger.error(f"Error in streak reset task: {str(e)}", exc_info=True)
        db.rollback()
    finally:
        db.close()


def start_background_tasks():
    """
    Initialize and start the background task scheduler

    Called from: app/main.py on application startup

    Scheduled tasks:
    - reset_expired_streaks: Daily at midnight UTC
    """
    scheduler = BackgroundScheduler()

    # Schedule daily streak reset at midnight UTC
    scheduler.add_job(
        reset_expired_streaks,
        trigger='cron',
        hour=0,
        minute=0,
        id='daily_streak_reset',
        name='Reset expired study streaks',
        replace_existing=True
    )

    # Start the scheduler
    scheduler.start()
    logger.info("Background task scheduler started")
    logger.info("Scheduled tasks:")
    logger.info("  - reset_expired_streaks: Daily at 00:00 UTC")

    return scheduler
