# SERVICE LAYER - Database operations for UserProfile model
#
# What services DO:
# - Execute SQL queries (SELECT, INSERT, UPDATE, DELETE)
# - Return database models or None
# - Simple, focused functions (one query per function)
#
# What services DON'T DO:
# - Business logic decisions (that's what CONTROLLERS do)
# - HTTP error handling (that's what CONTROLLERS do)

# SQLAlchemy Session type - represents database connection
from sqlalchemy.orm import Session

# For timestamps and dates
from datetime import datetime, date

# UserProfile model - maps to "user_profiles" table in PostgreSQL
# Defined in: app/models/user.py
from app.models.user import UserProfile


# CREATE PROFILE SERVICE
# Called by: app/controllers/auth_controller.py → signup()
def create_profile(db: Session, user_id: int) -> UserProfile:
    """
    DATABASE OPERATION: Insert new profile into database

    This service function:
    - Creates profile with default gamification stats (all zeros)
    - Inserts into "user_profiles" table
    - Returns UserProfile model
    """

    # Initialize profile with defaults (all counters = 0)
    # UserProfile model defined in: app/models/user.py
    profile = UserProfile(
        user_id=user_id,  # Foreign key links to users table
        created_at=datetime.utcnow()
    )

    # Execute database INSERT
    db.add(profile)      # Add to SQLAlchemy session (staged for insert)
    db.commit()          # ← EXECUTE: SQL INSERT INTO user_profiles (...) VALUES (...)
    db.refresh(profile)  # Reload from database
    return profile       # ← Returns UserProfile model

# GET PROFILE SERVICE
# Called by: Other service functions in this same file
def get_profile(db: Session, user_id: int) -> UserProfile | None:
    """
    DATABASE OPERATION: Query profile by user_id

    SQL executed: SELECT * FROM user_profiles WHERE user_id = 123
    Returns: UserProfile model if found, None if not found
    """
    # Execute database SELECT query
    return db.query(UserProfile).filter(UserProfile.user_id == user_id).first()


# UPDATE PROFILE
# Called by: (not currently used - placeholder for future user profile editing)
def update_profile(db: Session, user_id: int, updates: dict) -> UserProfile:
    """Update profile fields (bio, avatar, etc) - accepts dict of changes"""

    # Get profile from database
    # Calls: get_profile() in this same file
    profile = get_profile(db, user_id)
    if not profile:
        return None

    # Dynamically set fields from updates dict
    # Example: updates = {"bio": "I love CompTIA!", "avatar_url": "https://..."}
    for key, value in updates.items():
        setattr(profile, key, value)  # Set profile.key = value

    db.commit()        # Execute SQL UPDATE user_profiles SET ...
    db.refresh(profile)  # Reload from database
    return profile     # ← Returns updated UserProfile model

# INCREMENT EXAM COUNT
# Called by: (will be called by exam controller when exam feature is implemented)
def increment_exam_count(db: Session, user_id: int):
    """Increment total_exams_taken counter - called when user completes an exam"""

    # Get profile from database
    # Calls: get_profile() in this same file
    profile = get_profile(db, user_id)
    if profile:
        profile.total_exams_taken += 1  # Increase counter by 1
        db.commit()  # Execute SQL UPDATE user_profiles SET total_exams_taken = ...


# UPDATE LAST ACTIVITY
# Called by: (will be called when tracking user activity for streaks)
def update_last_activity(db: Session, user_id: int, activity_date: date):
    """Update last_activity_date - used for streak calculation"""

    # Calls: get_profile() in this same file
    profile = get_profile(db, user_id)
    if profile:
        profile.last_activity_date = activity_date  # Store date (not datetime)
        db.commit()  # Execute SQL UPDATE


# UPDATE STREAK
# Called by: (will be called by streak controller to persist calculated streaks)
def update_streak(db: Session, user_id: int, current: int, longest: int):
    """Update streak counters - service only stores data, controller calculates logic"""

    # NOTE: Separation of concerns
    # - Services (this file) only persist data to database
    # - Controllers calculate business logic (when to increment/reset streaks)

    # Calls: get_profile() in this same file
    profile = get_profile(db, user_id)
    if profile:
        profile.study_streak_current = current  # Current consecutive days
        profile.study_streak_longest = longest  # Personal record
        db.commit()  # Execute SQL UPDATE user_profiles SET ...
