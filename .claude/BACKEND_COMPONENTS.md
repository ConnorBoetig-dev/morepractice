# Backend Components

## Overview
The backend follows a clean layered architecture with clear separation of concerns:

```
Routes → Controllers → Services → Models → Database
```

Each layer has specific responsibilities and communicates through well-defined interfaces (Pydantic schemas).

---

## Layer Responsibilities

### 1. Routes (API Layer)
**Location**: `backend/app/api/v1/*.py`

**Responsibility**: HTTP interface
- Receive HTTP requests
- Extract path/query parameters
- Validate request bodies (Pydantic)
- Call controllers
- Return HTTP responses (200, 201, 400, 401, etc.)
- Handle authentication middleware

**Files**:
- `auth_routes.py` - Authentication endpoints
- `question_routes.py` - Question fetching
- `quiz_routes.py` - Quiz submission & history
- `achievement_routes.py` - Achievement endpoints
- `avatar_routes.py` - Avatar endpoints
- `leaderboard_routes.py` - Leaderboard endpoints

**Example**:
```python
# backend/app/api/v1/auth_routes.py
from fastapi import APIRouter, Depends
from app.controllers import auth_controller
from app.schemas.auth import SignupRequest, SignupResponse

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", response_model=SignupResponse)
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    """Create new user account"""
    return auth_controller.signup(db, request)
```

---

### 2. Controllers (Orchestration Layer)
**Location**: `backend/app/controllers/*.py`

**Responsibility**: Business logic orchestration
- Coordinate multiple services
- Handle complex workflows
- Transaction management
- Error handling and formatting

**Files**:
- `auth_controller.py` - Signup, login, JWT management
- `quiz_controller.py` - Quiz submission orchestration (quiz_service + achievement_service)

**Example**:
```python
# backend/app/controllers/quiz_controller.py
from app.services import quiz_service, achievement_service

def submit_quiz(db: Session, user_id: int, submission: QuizSubmission):
    """Submit quiz, award XP, check achievements"""

    # 1. Submit quiz and calculate XP
    quiz_attempt, xp_earned, new_level, level_up = quiz_service.submit_quiz(
        db, user_id, submission
    )

    # 2. Check for newly unlocked achievements
    achievements_unlocked = achievement_service.check_and_award_achievements(
        db, user_id, submission.exam_type
    )

    # 3. Return combined response
    return {
        "quiz_attempt": quiz_attempt,
        "xp_earned": xp_earned,
        "new_level": new_level,
        "level_up": level_up,
        "achievements_unlocked": achievements_unlocked
    }
```

**When to use Controllers**:
- Multi-service coordination (quiz submission = quiz + achievements)
- Complex workflows with multiple steps
- Transaction management across services

**When to skip Controllers**:
- Simple CRUD operations
- Single-service operations
- Routes can call services directly if logic is simple

---

### 3. Services (Business Logic Layer)
**Location**: `backend/app/services/*.py`

**Responsibility**: Core business logic
- Database queries (via ORM)
- Data transformations
- Calculations and algorithms
- Business rules enforcement

**Files**:
- `quiz_service.py` - Quiz submission, XP/level calculation, quiz history
- `achievement_service.py` - Achievement checking, awarding, progress tracking
- `avatar_service.py` - Avatar unlocking, selection, collection stats
- `leaderboard_service.py` - Leaderboard queries with rankings

**Example**:
```python
# backend/app/services/quiz_service.py

def calculate_xp_earned(correct_answers: int, total_questions: int, exam_type: str) -> int:
    """Calculate XP with accuracy bonus"""
    base_xp = correct_answers * 10
    accuracy = (correct_answers / total_questions) * 100

    if accuracy >= 90:
        bonus_multiplier = 1.5
    elif accuracy >= 80:
        bonus_multiplier = 1.25
    elif accuracy >= 70:
        bonus_multiplier = 1.10
    else:
        bonus_multiplier = 1.0

    return int(base_xp * bonus_multiplier)


def calculate_level_from_xp(xp: int) -> int:
    """Calculate level from total XP using sqrt formula"""
    import math
    if xp < 0:
        return 1
    level = int(math.sqrt(xp / 100)) + 1
    return max(1, level)
```

**Service Design Principles**:
- Each service focuses on one domain (quiz, achievement, avatar)
- Services can call other services (e.g., achievement_service calls avatar_service)
- Services are stateless (no instance variables)
- All functions take `db: Session` as first parameter

---

### 4. Models (ORM Layer)
**Location**: `backend/app/models/*.py`

**Responsibility**: Database schema definition
- SQLAlchemy ORM models
- Table structure (columns, types, constraints)
- Relationships (ForeignKey, relationship())
- Indexes for performance
- CHECK constraints for validation

**Files**:
- `user.py` - User, UserProfile
- `question.py` - Question
- `gamification.py` - QuizAttempt, UserAnswer, Achievement, UserAchievement, Avatar, UserAvatar

**Example**:
```python
# backend/app/models/gamification.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey, CheckConstraint, Index
from sqlalchemy.orm import relationship
from app.db.base import Base

class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    exam_type = Column(String, nullable=False, index=True)
    total_questions = Column(Integer, nullable=False)
    correct_answers = Column(Integer, nullable=False)
    score_percentage = Column(Float, nullable=False)
    xp_earned = Column(Integer, nullable=False, default=0)
    completed_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    # Relationships
    answers = relationship("UserAnswer", back_populates="quiz_attempt", cascade="all, delete-orphan")

    # Constraints
    __table_args__ = (
        CheckConstraint("total_questions > 0"),
        CheckConstraint("correct_answers >= 0"),
        CheckConstraint("correct_answers <= total_questions"),
        CheckConstraint("score_percentage >= 0 AND score_percentage <= 100"),
        Index("idx_quiz_exam_score_date", "exam_type", "score_percentage", "completed_at"),
    )
```

---

### 5. Schemas (Validation Layer)
**Location**: `backend/app/schemas/*.py`

**Responsibility**: Data validation and serialization
- Request body validation
- Response serialization
- Type checking
- Field constraints
- Documentation (OpenAPI/Swagger)

**Files**:
- `auth.py` - Signup, login, user profile schemas
- `quiz.py` - Quiz submission, answer, history schemas
- `achievement.py` - Achievement, progress, stats schemas
- `avatar.py` - Avatar, unlock, selection schemas
- `leaderboard.py` - Leaderboard entry schemas

**Example**:
```python
# backend/app/schemas/quiz.py
from pydantic import BaseModel, Field, validator
from typing import List
from datetime import datetime

class AnswerSubmission(BaseModel):
    """Single answer in a quiz submission"""
    question_id: int = Field(..., description="ID of the question")
    user_answer: str = Field(..., description="User's selected answer (A/B/C/D)")
    correct_answer: str = Field(..., description="Correct answer (A/B/C/D)")
    is_correct: bool = Field(..., description="Whether answer was correct")
    time_spent_seconds: int | None = Field(None, description="Time spent on question")

    @validator("user_answer", "correct_answer")
    def validate_answer_choice(cls, v):
        if v not in ["A", "B", "C", "D"]:
            raise ValueError("Answer must be A, B, C, or D")
        return v


class QuizSubmission(BaseModel):
    """Quiz submission request"""
    exam_type: str = Field(..., description="Exam type (security_plus, network_plus, etc.)")
    total_questions: int = Field(..., gt=0, description="Total number of questions")
    time_taken_seconds: int | None = Field(None, ge=0, description="Total time taken")
    answers: List[AnswerSubmission] = Field(..., description="List of answers")

    @validator("answers")
    def validate_answers_count(cls, v, values):
        if "total_questions" in values and len(v) != values["total_questions"]:
            raise ValueError("Number of answers must match total_questions")
        return v


class AchievementUnlocked(BaseModel):
    """Achievement unlocked during quiz submission"""
    achievement_id: int
    name: str
    description: str
    badge_icon_url: str | None
    xp_reward: int


class QuizSubmissionResponse(BaseModel):
    """Response after submitting a quiz"""
    quiz_attempt: dict  # Could be a more specific schema
    xp_earned: int
    new_level: int
    level_up: bool
    achievements_unlocked: List[AchievementUnlocked]
```

**Schema Naming Conventions**:
- `*Request` - Request body schemas
- `*Response` - Response schemas
- `*Public` - Public data (no auth required)
- `*WithStatus` - Enhanced with user-specific data (unlock status, progress)

---

### 6. Utils (Helper Functions)
**Location**: `backend/app/utils/*.py`

**Responsibility**: Shared utilities
- JWT token creation/verification
- Password hashing
- Common validators
- Helper functions

**Files**:
- `auth.py` - JWT utilities, password hashing

**Example**:
```python
# backend/app/utils/auth.py
import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
import os

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    """Create JWT token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 10080))
    )
    to_encode.update({"exp": expire})

    secret_key = os.getenv("JWT_SECRET")
    algorithm = os.getenv("JWT_ALGORITHM", "HS256")

    return jwt.encode(to_encode, secret_key, algorithm=algorithm)
```

---

### 7. Database (DB Layer)
**Location**: `backend/app/db/*.py`

**Responsibility**: Database configuration and seeding
- Database connection setup
- Session management
- Seed data scripts

**Files**:
- `base.py` - SQLAlchemy declarative base
- `session.py` - Database session and engine
- `seed_achievements.py` - Seed 27 achievements
- `seed_avatars.py` - Seed 18 avatars

**Example**:
```python
# backend/app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Get DATABASE_URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

# Create engine
engine = create_engine(DATABASE_URL, echo=False)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency for FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

## Component Interaction Examples

### Example 1: User Signup Flow

```
1. POST /api/v1/auth/signup
   ↓
2. auth_routes.signup()
   - Validates SignupRequest (Pydantic)
   - Calls auth_controller.signup()
   ↓
3. auth_controller.signup()
   - Hashes password (utils.auth.hash_password)
   - Creates User model
   - Creates UserProfile model
   - Unlocks default avatars (avatar_service)
   - Creates JWT token (utils.auth.create_access_token)
   - Returns SignupResponse
   ↓
4. Returns JSON response to client
```

---

### Example 2: Quiz Submission Flow

```
1. POST /api/v1/quiz/submit
   ↓
2. quiz_routes.submit_quiz()
   - Validates QuizSubmission (Pydantic)
   - Extracts user_id from JWT
   - Calls quiz_controller.submit_quiz()
   ↓
3. quiz_controller.submit_quiz()
   - Calls quiz_service.submit_quiz()
     • Creates QuizAttempt model
     • Bulk creates UserAnswer models
     • Calculates XP (quiz_service.calculate_xp_earned)
     • Updates UserProfile (XP, level)
     • Returns (attempt, xp, level, level_up)

   - Calls achievement_service.check_and_award_achievements()
     • Gets user stats (quiz count, accuracy, streak)
     • Checks each achievement criteria
     • Awards new achievements → UserAchievement models
     • Adds achievement XP rewards
     • Unlocks avatars (avatar_service.unlock_avatar_from_achievement)
     • Returns achievements_unlocked[]

   - Combines results into QuizSubmissionResponse
   ↓
4. Returns JSON response to client
```

---

### Example 3: Leaderboard Query Flow

```
1. GET /api/v1/leaderboard/xp
   ↓
2. leaderboard_routes.get_xp_leaderboard()
   - Validates query params (limit)
   - Calls leaderboard_service.get_xp_leaderboard()
   ↓
3. leaderboard_service.get_xp_leaderboard()
   - Executes SQL query with window function (RANK)
   - Joins users + user_profiles
   - Orders by XP descending
   - Returns LeaderboardResponse
   ↓
4. Returns JSON response to client
```

---

## File Organization Best Practices

### ✅ Good Practices (Currently Followed)

1. **Proper Schema Separation**
   - All Pydantic schemas in `app/schemas/*.py`
   - No inline schemas in routes
   - Reusable schemas (e.g., AchievementUnlocked imported across files)

2. **Service Layer Isolation**
   - Services don't depend on FastAPI
   - Services can be tested independently
   - Services can call other services

3. **No Code Duplication**
   - Shared utilities in `app/utils/`
   - Reusable functions (calculate_xp, calculate_level)
   - Shared schemas imported where needed

4. **Clear Naming**
   - Files named by domain (quiz, achievement, avatar)
   - Functions named by action (submit_quiz, unlock_avatar)
   - Schemas named by purpose (*Request, *Response, *Public)

5. **Comprehensive Comments**
   - Docstrings on all functions
   - Inline comments for complex logic
   - Model docstrings explaining purpose

---

## Testing Structure (Future)

```
backend/tests/
├── unit/
│   ├── services/
│   │   ├── test_quiz_service.py
│   │   ├── test_achievement_service.py
│   │   └── test_leaderboard_service.py
│   ├── models/
│   │   └── test_gamification_models.py
│   └── schemas/
│       └── test_quiz_schemas.py
├── integration/
│   ├── api/
│   │   ├── test_auth_routes.py
│   │   ├── test_quiz_routes.py
│   │   └── test_achievement_routes.py
│   └── gamification/
│       ├── test_quiz_to_achievement_flow.py
│       └── test_avatar_unlock_flow.py
├── fixtures/
│   ├── database.py       # Test DB setup/teardown
│   ├── users.py          # Test user factories
│   └── achievements.py   # Test achievement data
└── conftest.py           # pytest configuration
```

---

## Dependencies Between Components

### Service Dependencies

```
quiz_service
  ↓
  (no dependencies)

achievement_service
  ↓
  • quiz_service (for calculate_level_from_xp)
  • avatar_service (for unlock_avatar_from_achievement)

avatar_service
  ↓
  (no dependencies)

leaderboard_service
  ↓
  (no dependencies)
```

**Note**: Services should avoid circular dependencies. If needed, import functions directly instead of modules.

---

## Key Files Reference

| File | Lines | Purpose |
|------|-------|---------|
| `main.py` | 202 | App initialization, CORS, route registration |
| `models/gamification.py` | 273 | 6 gamification models with relationships |
| `models/user.py` | 97 | User and UserProfile models |
| `services/quiz_service.py` | 329 | Quiz submission, XP/level logic, stats |
| `services/achievement_service.py` | 387 | Achievement checking, awarding, progress |
| `services/avatar_service.py` | ~200 | Avatar unlocking, selection, stats |
| `services/leaderboard_service.py` | ~250 | 5 leaderboard queries with rankings |
| `schemas/quiz.py` | ~150 | Quiz submission/response schemas |
| `schemas/achievement.py` | ~100 | Achievement schemas |
| `schemas/avatar.py` | ~120 | Avatar schemas |
| `db/seed_achievements.py` | 388 | 27 achievement definitions |
| `db/seed_avatars.py` | 248 | 18 avatar definitions |

---

## Quick Component Lookup

**Need to add a new API endpoint?**
→ Add route in `app/api/v1/*_routes.py`

**Need to add business logic?**
→ Add function in `app/services/*_service.py`

**Need to add a database table?**
→ Add model in `app/models/*.py`

**Need to add request/response validation?**
→ Add schema in `app/schemas/*.py`

**Need to add a new achievement?**
→ Edit `app/db/seed_achievements.py` and re-run seed

**Need to add a new avatar?**
→ Edit `app/db/seed_avatars.py` and re-run seed

**Need to change XP calculation?**
→ Edit `app/services/quiz_service.py:calculate_xp_earned()`

**Need to change level formula?**
→ Edit `app/services/quiz_service.py:calculate_level_from_xp()`
