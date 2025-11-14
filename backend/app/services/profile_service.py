from sqlalchemy.orm import Session
from datetime import datetime, date
from app.models.user import UserProfile

def create_profile(db: Session, user_id: int) -> UserProfile:
    """
    Create a new user profile when a new user signs up.
    """
    profile = UserProfile(
        user_id=user_id,
        created_at=datetime.utcnow()
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile

def get_profile(db: Session, user_id: int) -> UserProfile | None:
    return db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

def update_profile(db: Session, user_id: int, updates: dict) -> UserProfile:
    profile = get_profile(db, user_id)
    if not profile:
        return None

    for key, value in updates.items():
        setattr(profile, key, value)

    db.commit()
    db.refresh(profile)
    return profile

def increment_exam_count(db: Session, user_id: int):
    """
    Called whenever a user completes an exam.
    """
    profile = get_profile(db, user_id)
    if profile:
        profile.total_exams_taken += 1
        db.commit()

def update_last_activity(db: Session, user_id: int, activity_date: date):
    """
    Updates the last activity date for streak tracking.
    """
    profile = get_profile(db, user_id)
    if profile:
        profile.last_activity_date = activity_date
        db.commit()

def update_streak(db: Session, user_id: int, current: int, longest: int):
    """
    Update streak numbers directly.
    Controllers decide *when* streak changes.
    Services only store them.
    """
    profile = get_profile(db, user_id)
    if profile:
        profile.study_streak_current = current
        profile.study_streak_longest = longest
        db.commit()
