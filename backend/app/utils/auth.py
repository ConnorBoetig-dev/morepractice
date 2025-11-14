from passlib.context import CryptContext

# Passlib context tells us which hashing algorithm to use.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Turn a raw password into a hashed password.
    """
    return pwd_context.hash(password)

def verify_password(raw_password: str, hashed_password: str) -> bool:
    """
    Check if raw_password matches the stored hashed version.
    """
    return pwd_context.verify(raw_password, hashed_password)

import jwt
from datetime import datetime, timedelta
from typing import Optional

SECRET_KEY = "CHANGE_THIS_TO_A_RANDOM_LONG_STRING"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create a signed JWT token with an expiration time.
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    """
    Decode a JWT token and return the payload if valid.
    Raises an exception if token is invalid or expired.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None  # Token expired
    except jwt.InvalidTokenError:
        return None  # Token invalid
