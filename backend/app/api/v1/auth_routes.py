from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.controllers.auth_controller import (
    signup,
    login,
    get_current_user_from_token,
)
from app.schemas.auth import SignupRequest, LoginRequest, TokenResponse, UserResponse

router = APIRouter(prefix="/auth", tags=["Auth"])


# ----------------------------------------------------
# Dependency: Create a DB session for each request
# ----------------------------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ----------------------------------------------------
# SIGNUP
# ----------------------------------------------------
@router.post("/signup", response_model=TokenResponse)
def signup_route(payload: SignupRequest, db: Session = Depends(get_db)):
    return signup(
        db=db,
        email=payload.email,
        password=payload.password,
        username=payload.username,
    )


# ----------------------------------------------------
# LOGIN
# ----------------------------------------------------
@router.post("/login", response_model=TokenResponse)
def login_route(payload: LoginRequest, db: Session = Depends(get_db)):
    return login(
        db=db,
        email=payload.email,
        password=payload.password,
    )


# ----------------------------------------------------
# GET CURRENT USER (/auth/me)
# ----------------------------------------------------
@router.get("/me", response_model=UserResponse)
def get_me_route(token: str, db: Session = Depends(get_db)):
    """
    The frontend calls /auth/me?token=xxxxx
    We decode the token and return user data.
    """
    user = get_current_user_from_token(db, token)
    return user
