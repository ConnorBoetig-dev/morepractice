from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.services.auth_service import (
    create_user,
    get_user_by_email,
    get_user_by_id,
)
from app.services.profile_service import create_profile
from app.utils.auth import verify_password, create_access_token, decode_access_token


# ----------------------------------------------------
# SIGNUP
# ----------------------------------------------------
def signup(db: Session, email: str, password: str, username: str) -> dict:
    # 1. Check if user already exists
    existing = get_user_by_email(db, email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered.",
        )

    # 2. Create user
    user = create_user(db, email=email, password=password, username=username)

    # 3. Create user profile
    create_profile(db, user_id=user.id)

    # 4. Create JWT token
    token = create_access_token({"user_id": user.id})

    return {"access_token": token, "user_id": user.id, "username": user.username}


# ----------------------------------------------------
# LOGIN
# ----------------------------------------------------
def login(db: Session, email: str, password: str) -> dict:
    # 1. Look up the user
    user = get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    # 2. Verify password
    if not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    # 3. Create JWT token
    token = create_access_token({"user_id": user.id})

    return {"access_token": token, "user_id": user.id, "username": user.username}


# ----------------------------------------------------
# GET CURRENT USER FROM TOKEN
# ----------------------------------------------------
def get_current_user_from_token(db: Session, token: str):
    # 1. Decode token
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
        )

    # 2. Extract user_id
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload.",
        )

    # 3. Load user
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    return user
