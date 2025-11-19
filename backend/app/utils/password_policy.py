"""
PASSWORD POLICY ENFORCEMENT
Enterprise-level password security policies

Features:
- Password complexity requirements
- Password history tracking (prevent reuse)
- Common password blacklist
- Password strength scoring
"""

import re
from typing import List, Tuple
from datetime import datetime, timedelta


# ============================================
# PASSWORD POLICY CONFIGURATION
# ============================================

# Minimum requirements
MIN_PASSWORD_LENGTH = 12
REQUIRE_UPPERCASE = True
REQUIRE_LOWERCASE = True
REQUIRE_DIGIT = True
REQUIRE_SPECIAL_CHAR = True

# History settings
PASSWORD_HISTORY_COUNT = 5  # Remember last 5 passwords
PASSWORD_EXPIRY_DAYS = 90  # Password expires after 90 days (0 = no expiry)

# Common passwords blacklist (top weak passwords)
COMMON_PASSWORDS = {
    "password", "password123", "123456", "12345678", "qwerty",
    "abc123", "monkey", "letmein", "trustno1", "dragon",
    "baseball", "iloveyou", "master", "sunshine", "ashley",
    "bailey", "passw0rd", "shadow", "123123", "654321",
    "superman", "qazwsx", "michael", "football", "welcome",
    "jesus", "ninja", "mustang", "password1", "admin",
    "CompTIA", "comptia", "security+", "network+", "a+"
}


# ============================================
# PASSWORD VALIDATION
# ============================================

def validate_password_strength(password: str) -> Tuple[bool, List[str]]:
    """
    Validate password against security policy

    Args:
        password: Plain text password to validate

    Returns:
        Tuple of (is_valid, list_of_errors)
        - is_valid: True if password meets all requirements
        - list_of_errors: List of requirement violations (empty if valid)

    Example:
        is_valid, errors = validate_password_strength("weak")
        if not is_valid:
            raise ValueError(f"Password requirements not met: {', '.join(errors)}")
    """
    errors = []

    # Check minimum length
    if len(password) < MIN_PASSWORD_LENGTH:
        errors.append(f"Password must be at least {MIN_PASSWORD_LENGTH} characters long")

    # Check for uppercase letter
    if REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")

    # Check for lowercase letter
    if REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")

    # Check for digit
    if REQUIRE_DIGIT and not re.search(r'\d', password):
        errors.append("Password must contain at least one number")

    # Check for special character
    if REQUIRE_SPECIAL_CHAR and not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]', password):
        errors.append("Password must contain at least one special character (!@#$%^&* etc.)")

    # Check against common passwords (case-insensitive)
    if password.lower() in COMMON_PASSWORDS:
        errors.append("This password is too common and easily guessed")

    # Check for sequential characters (e.g., "123", "abc")
    if has_sequential_chars(password):
        errors.append("Password should not contain sequential characters (e.g., '123', 'abc')")

    # Check for repeated characters (e.g., "aaa", "111")
    if has_repeated_chars(password, max_repeats=3):
        errors.append("Password should not contain more than 3 repeated characters")

    return (len(errors) == 0, errors)


def has_sequential_chars(password: str, min_length: int = 3) -> bool:
    """
    Check if password contains sequential characters (e.g., "123", "abc")

    Args:
        password: Password to check
        min_length: Minimum length of sequence to detect (default: 3)

    Returns:
        True if sequential characters found, False otherwise
    """
    password_lower = password.lower()

    # Check for sequential numbers (123, 456, etc.)
    for i in range(len(password_lower) - min_length + 1):
        substring = password_lower[i:i + min_length]
        if substring.isdigit():
            chars = [int(c) for c in substring]
            if all(chars[j] + 1 == chars[j + 1] for j in range(len(chars) - 1)):
                return True
            if all(chars[j] - 1 == chars[j + 1] for j in range(len(chars) - 1)):
                return True

    # Check for sequential letters (abc, xyz, etc.)
    for i in range(len(password_lower) - min_length + 1):
        substring = password_lower[i:i + min_length]
        if substring.isalpha():
            chars = [ord(c) for c in substring]
            if all(chars[j] + 1 == chars[j + 1] for j in range(len(chars) - 1)):
                return True
            if all(chars[j] - 1 == chars[j + 1] for j in range(len(chars) - 1)):
                return True

    return False


def has_repeated_chars(password: str, max_repeats: int = 3) -> bool:
    """
    Check if password contains too many repeated characters

    Args:
        password: Password to check
        max_repeats: Maximum allowed consecutive repeats (default: 3)

    Returns:
        True if too many repeated characters found, False otherwise
    """
    for i in range(len(password) - max_repeats):
        if all(password[i] == password[i + j] for j in range(max_repeats + 1)):
            return True
    return False


def calculate_password_strength(password: str) -> Tuple[int, str]:
    """
    Calculate password strength score (0-100) and rating

    Args:
        password: Password to evaluate

    Returns:
        Tuple of (score, rating)
        - score: 0-100 (higher is better)
        - rating: "Very Weak", "Weak", "Fair", "Strong", "Very Strong"

    Scoring criteria:
    - Length: +4 points per character
    - Uppercase letters: +10 points
    - Lowercase letters: +10 points
    - Numbers: +10 points
    - Special characters: +15 points
    - Entropy bonus: +20 points for high variety
    - Penalty for common passwords: -50 points
    - Penalty for sequential/repeated: -20 points each
    """
    score = 0

    # Length score (max 40 points for 10+ characters)
    score += min(len(password) * 4, 40)

    # Character variety
    if re.search(r'[A-Z]', password):
        score += 10
    if re.search(r'[a-z]', password):
        score += 10
    if re.search(r'\d', password):
        score += 10
    if re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]', password):
        score += 15

    # Entropy bonus (high character variety)
    unique_chars = len(set(password))
    if unique_chars >= 8:
        score += 20

    # Penalties
    if password.lower() in COMMON_PASSWORDS:
        score -= 50
    if has_sequential_chars(password):
        score -= 20
    if has_repeated_chars(password):
        score -= 20

    # Cap score at 0-100
    score = max(0, min(100, score))

    # Determine rating
    if score >= 80:
        rating = "Very Strong"
    elif score >= 60:
        rating = "Strong"
    elif score >= 40:
        rating = "Fair"
    elif score >= 20:
        rating = "Weak"
    else:
        rating = "Very Weak"

    return (score, rating)


def is_password_expired(last_changed: datetime, expiry_days: int = PASSWORD_EXPIRY_DAYS) -> bool:
    """
    Check if password has expired

    Args:
        last_changed: Datetime when password was last changed
        expiry_days: Number of days until password expires (0 = no expiry)

    Returns:
        True if password has expired, False otherwise
    """
    if expiry_days == 0:
        return False  # No expiry policy

    expiry_date = last_changed + timedelta(days=expiry_days)
    return datetime.utcnow() > expiry_date


# ============================================
# EXPORT
# ============================================
__all__ = [
    "validate_password_strength",
    "calculate_password_strength",
    "is_password_expired",
    "has_sequential_chars",
    "has_repeated_chars",
    "MIN_PASSWORD_LENGTH",
    "PASSWORD_HISTORY_COUNT",
    "PASSWORD_EXPIRY_DAYS"
]
