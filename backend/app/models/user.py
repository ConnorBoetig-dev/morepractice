# MODEL LAYER: User and UserProfile database schema definitions

# SQLAlchemy column types for defining table structure
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Date

# For default timestamps
from datetime import datetime

# Declarative base - all models inherit from this
# Defined in: app/db/base.py
from app.db.base import Base

# USER MODEL
# Used by: app/services/auth_service.py
# This class maps to the "users" table in PostgreSQL
class User(Base):
    """User account model - authentication and account info"""
    __tablename__ = "users"  # PostgreSQL table name

    # ============================================
    # PRIMARY KEY
    # ============================================
    id = Column(Integer, primary_key=True, index=True)  # Auto-increments: 1, 2, 3...

    # ============================================
    # AUTHENTICATION FIELDS
    # ============================================
    # unique=True prevents duplicate emails/usernames
    # index=True makes lookups fast (used in WHERE clauses)
    email = Column(String, unique=True, index=True, nullable=False)  # ← Used for login
    username = Column(String, unique=True, index=True, nullable=False)  # ← Display name
    hashed_password = Column(String, nullable=False)  # ← Bcrypt hash (NEVER plain text!)

    # ============================================
    # ACCOUNT STATUS FLAGS
    # ============================================
    is_active = Column(Boolean, default=True)  # False = account disabled (without deleting)
    is_verified = Column(Boolean, default=False)  # Email verification (not implemented yet)

    # ============================================
    # TIMESTAMPS
    # ============================================
    created_at = Column(DateTime, default=datetime.utcnow)  # When account was created
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Auto-updates on changes


# USER PROFILE MODEL
# Used by: app/services/profile_service.py
# This class maps to the "user_profiles" table in PostgreSQL
# One-to-one relationship with User (each user has exactly one profile)
class UserProfile(Base):
    """User profile with gamification stats and customization"""
    __tablename__ = "user_profiles"  # PostgreSQL table name

    # ============================================
    # PRIMARY KEY & RELATIONSHIP
    # ============================================
    # ForeignKey links to users.id - this is BOTH primary key AND foreign key
    # This creates a one-to-one relationship (one user = one profile)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)

    # ============================================
    # PROFILE CUSTOMIZATION
    # ============================================
    bio = Column(Text, nullable=True)  # User biography/description (optional)
    avatar_url = Column(String, nullable=True)  # Profile picture URL (optional)
    selected_avatar_id = Column(Integer, ForeignKey("avatars.id"), nullable=True)  # Currently equipped avatar

    # ============================================
    # GAMIFICATION: XP & LEVEL SYSTEM
    # ============================================
    xp = Column(Integer, default=0, nullable=False)  # Total experience points
    level = Column(Integer, default=1, nullable=False)  # Current level (calculated from XP)

    # ============================================
    # GAMIFICATION: STREAKS
    # ============================================
    study_streak_current = Column(Integer, default=0)  # Current consecutive study days
    study_streak_longest = Column(Integer, default=0)  # Personal record (highest streak)

    # ============================================
    # GAMIFICATION: ACTIVITY COUNTERS
    # ============================================
    total_exams_taken = Column(Integer, default=0)  # Lifetime exam count
    total_questions_answered = Column(Integer, default=0)  # Lifetime question count

    # ============================================
    # STREAK TRACKING DATA
    # ============================================
    # Used to calculate if streak continues or resets
    # Date (not DateTime) - we only care about the day, not the time
    last_activity_date = Column(Date, nullable=True)

    # ============================================
    # TIMESTAMPS
    # ============================================
    created_at = Column(DateTime, default=datetime.utcnow)  # When profile was created