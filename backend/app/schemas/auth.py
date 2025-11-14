# app/schemas/auth.py

from pydantic import BaseModel, EmailStr
from datetime import datetime


# ----------------------------------------------------
# SIGNUP REQUEST
# What the client must send when creating an account
# ----------------------------------------------------
class SignupRequest(BaseModel):
    # EmailStr automatically validates email format
    email: EmailStr
    
    # Raw password (we hash it later in the service)
    password: str
    
    # Visible display name for the user
    username: str


# ----------------------------------------------------
# LOGIN REQUEST
# What the client sends to log in
# ----------------------------------------------------
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ----------------------------------------------------
# TOKEN RESPONSE
# What we return after signup/login
# Example:
# {
#   "access_token": "...jwt...",
#   "token_type": "bearer"
# }
# ----------------------------------------------------
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"   # Standard OAuth format


# ----------------------------------------------------
# USER RESPONSE
# Returned from /auth/me
# This exposes safe info (not password!)
# ----------------------------------------------------
class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    is_active: bool
    created_at: datetime

    # Helps FastAPI convert SQLAlchemy model → Pydantic
    class Config:
        orm_mode = True
