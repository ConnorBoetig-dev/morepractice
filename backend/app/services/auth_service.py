from sqlalchemy.orm import Session
from app.models.user import User
from app.utils.auth import hash_password
from datetime import datetime

def create_user(db: Session, email: str, password: str, username: str) -> User:
    """
    Create a new user row in the database.
    Password is hashed BEFORE storing.
    """
    hashed = hash_password(password)
    user = User(
        email=email,
        username=username,
        hashed_password=hashed,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()

def update_user(db: Session, user_id: int, updates: dict) -> User:
    user = get_user_by_id(db, user_id)
    if not user:
        return None

    for key, value in updates.items():
        setattr(user, key, value)

    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    return user
