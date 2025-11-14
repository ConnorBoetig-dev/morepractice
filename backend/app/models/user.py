# app/models/user.py

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Date
from datetime import datetime
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class UserProfile(Base):
    __tablename__ = "user_profiles"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    bio = Column(Text, nullable=True)
    avatar_url = Column(String, nullable=True)

    study_streak_current = Column(Integer, default=0)
    study_streak_longest = Column(Integer, default=0)

    total_exams_taken = Column(Integer, default=0)
    total_questions_answered = Column(Integer, default=0)

    last_activity_date = Column(Date, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)