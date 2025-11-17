# SERVICE LAYER - Database operations for User model
#
# What services DO:
# - Execute SQL queries (SELECT, INSERT, UPDATE, DELETE)
# - Return database models or None
# - Simple, focused functions (one query per function)
#
# What services DON'T DO:
# - Business logic decisions (that's what CONTROLLERS do)
# - HTTP error handling (that's what CONTROLLERS do)
# - Complex workflows (that's what CONTROLLERS do)

# SQLAlchemy Session type - represents database connection
from sqlalchemy.orm import Session

# User model - maps to "users" table in PostgreSQL
# Defined in: app/models/user.py
from app.models.user import User

# Password hashing utility - called before storing passwords
# Defined in: app/utils/auth.py
from app.utils.auth import hash_password

# For timestamps
from datetime import datetime


# CREATE USER SERVICE
# Called by: app/controllers/auth_controller.py → signup()
def create_user(db: Session, email: str, password: str, username: str) -> User:
    """
    DATABASE OPERATION: Insert new user into database

    This service function:
    - Hashes the password
    - Inserts user into "users" table
    - Returns User model with auto-generated ID
    """

    # Hash password before storing (call utility function)
    # NEVER store plain text passwords in database!
    hashed = hash_password(password)  # ← Calls app/utils/auth.py

    # Create User model instance (from app/models/user.py)
    user = User(
        email=email,
        username=username,
        hashed_password=hashed,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    # Execute database INSERT
    db.add(user)       # Add to SQLAlchemy session (staged for insert)
    db.commit()        # ← EXECUTE: SQL INSERT INTO users (...) VALUES (...)
    db.refresh(user)   # Reload from database to get auto-generated id
    return user        # ← Returns User model with id field populated

# GET USER BY EMAIL SERVICE
# Called by: app/controllers/auth_controller.py → signup(), login()
def get_user_by_email(db: Session, email: str) -> User | None:
    """
    DATABASE OPERATION: Query user by email

    SQL executed: SELECT * FROM users WHERE email = 'xxx' LIMIT 1
    Returns: User model if found, None if not found
    """
    # Execute database SELECT query
    return db.query(User).filter(User.email == email).first()  # ← Returns User or None

# UPDATE USER SERVICE
# Called by: (not currently used - placeholder for future features)
def update_user(db: Session, user_id: int, updates: dict) -> User:
    """
    DATABASE OPERATION: Update user fields

    This service function:
    - Queries for user by ID
    - Updates specified fields
    - Saves changes to database
    """

    # Get user from database (call service in this same file)
    user = get_user_by_id(db, user_id)
    if not user:
        return None

    # Dynamically update fields from updates dict
    # Example: updates = {"is_verified": True, "username": "new_name"}
    for key, value in updates.items():
        setattr(user, key, value)  # Set user.key = value

    user.updated_at = datetime.utcnow()  # Update timestamp
    db.commit()                          # ← EXECUTE: SQL UPDATE users SET ... WHERE id = ...
    db.refresh(user)                     # Reload from database
    return user                          # ← Returns updated User model
