"""
ADMIN SCHEMAS
Pydantic models for admin API requests/responses

Used by:
- Admin question management endpoints
- Admin user management endpoints
- Admin achievement management endpoints
"""

from pydantic import BaseModel, Field, field_validator
from typing import Dict, List, Optional
from datetime import datetime


# ================================================================
# QUESTION MANAGEMENT SCHEMAS
# ================================================================

class QuestionOptionSchema(BaseModel):
    """Schema for a single answer option"""
    text: str = Field(..., description="Answer choice text", min_length=1)
    explanation: str = Field(..., description="Explanation for this choice", min_length=1)


class QuestionCreate(BaseModel):
    """Schema for creating a new question"""
    question_id: str = Field(..., description="External question ID (e.g., '0', '1', 'Q123')")
    exam_type: str = Field(..., description="Exam type: security, network, a1101, a1102")
    domain: str = Field(..., description="CompTIA domain/objective (e.g., '1.1', '2.3')")
    question_text: str = Field(..., description="The question text", min_length=10)
    correct_answer: str = Field(..., description="Correct answer: A, B, C, or D")
    options: Dict[str, QuestionOptionSchema] = Field(
        ...,
        description="All four answer options with explanations (keys: A, B, C, D)"
    )

    @field_validator('exam_type')
    @classmethod
    def validate_exam_type(cls, v: str) -> str:
        """Ensure exam_type is valid"""
        valid_types = ['security', 'network', 'a1101', 'a1102']
        if v not in valid_types:
            raise ValueError(f'Exam type must be one of: {", ".join(valid_types)}')
        return v

    @field_validator('correct_answer')
    @classmethod
    def validate_correct_answer(cls, v: str) -> str:
        """Ensure correct_answer is A, B, C, or D"""
        if v not in ['A', 'B', 'C', 'D']:
            raise ValueError('Correct answer must be A, B, C, or D')
        return v

    @field_validator('options')
    @classmethod
    def validate_options(cls, v: Dict[str, QuestionOptionSchema]) -> Dict[str, QuestionOptionSchema]:
        """Ensure all four options (A, B, C, D) are present"""
        required_keys = {'A', 'B', 'C', 'D'}
        if set(v.keys()) != required_keys:
            raise ValueError('Must provide exactly 4 options: A, B, C, D')
        return v


class QuestionUpdate(BaseModel):
    """Schema for updating an existing question (all fields optional)"""
    question_id: Optional[str] = Field(None, description="External question ID")
    exam_type: Optional[str] = Field(None, description="Exam type")
    domain: Optional[str] = Field(None, description="CompTIA domain/objective")
    question_text: Optional[str] = Field(None, description="The question text", min_length=10)
    correct_answer: Optional[str] = Field(None, description="Correct answer: A, B, C, or D")
    options: Optional[Dict[str, QuestionOptionSchema]] = Field(None, description="Answer options")

    @field_validator('exam_type')
    @classmethod
    def validate_exam_type(cls, v: Optional[str]) -> Optional[str]:
        """Ensure exam_type is valid if provided"""
        if v is not None:
            valid_types = ['security', 'network', 'a1101', 'a1102']
            if v not in valid_types:
                raise ValueError(f'Exam type must be one of: {", ".join(valid_types)}')
        return v

    @field_validator('correct_answer')
    @classmethod
    def validate_correct_answer(cls, v: Optional[str]) -> Optional[str]:
        """Ensure correct_answer is A, B, C, or D if provided"""
        if v is not None and v not in ['A', 'B', 'C', 'D']:
            raise ValueError('Correct answer must be A, B, C, or D')
        return v

    @field_validator('options')
    @classmethod
    def validate_options(cls, v: Optional[Dict[str, QuestionOptionSchema]]) -> Optional[Dict[str, QuestionOptionSchema]]:
        """Ensure all four options are present if provided"""
        if v is not None:
            required_keys = {'A', 'B', 'C', 'D'}
            if set(v.keys()) != required_keys:
                raise ValueError('Must provide exactly 4 options: A, B, C, D')
        return v


class QuestionResponse(BaseModel):
    """Schema for question response (includes database ID)"""
    id: int
    question_id: str
    exam_type: str
    domain: str
    question_text: str
    correct_answer: str
    options: Dict[str, QuestionOptionSchema]
    created_at: datetime

    class Config:
        from_attributes = True


class QuestionListResponse(BaseModel):
    """Schema for paginated question list"""
    total: int = Field(..., description="Total number of questions matching filters")
    questions: List[QuestionResponse] = Field(..., description="List of questions")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")


class QuestionDeleteResponse(BaseModel):
    """Schema for question deletion response"""
    success: bool
    message: str
    deleted_id: int


# ================================================================
# USER MANAGEMENT SCHEMAS
# ================================================================

class UserSummary(BaseModel):
    """Summary of user account for admin viewing"""
    id: int
    username: str
    email: str
    is_active: bool
    is_verified: bool
    is_admin: bool
    created_at: datetime
    last_login_at: Optional[datetime]

    # Profile stats
    xp: int
    level: int
    study_streak_current: int

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """Schema for paginated user list"""
    total: int
    users: List[UserSummary]
    page: int
    page_size: int
    total_pages: int


class UserDetailResponse(BaseModel):
    """Detailed user information for admin"""
    # Account info
    id: int
    username: str
    email: str
    is_active: bool
    is_verified: bool
    is_admin: bool
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime]
    last_login_ip: Optional[str]

    # Profile info
    xp: int
    level: int
    study_streak_current: int
    study_streak_longest: int
    total_quizzes_completed: int
    total_achievements_earned: int

    class Config:
        from_attributes = True


# ================================================================
# ACHIEVEMENT MANAGEMENT SCHEMAS
# ================================================================

class AchievementCreate(BaseModel):
    """Schema for creating a new achievement"""
    name: str = Field(..., description="Achievement name", min_length=1, max_length=100)
    description: str = Field(..., description="Achievement description", min_length=1)
    icon: str = Field(..., description="Icon identifier/emoji", max_length=50)
    criteria_type: str = Field(
        ...,
        description="Type of criteria: email_verified, quiz_completed, perfect_quiz, high_score_quiz, correct_answers, level_reached, exam_specific, multi_domain"
    )
    criteria_value: int = Field(..., description="Required value to unlock", ge=1)
    criteria_exam_type: Optional[str] = Field(None, description="Specific exam type (for exam_specific achievements)")
    xp_reward: int = Field(default=0, description="Bonus XP for unlocking", ge=0)

    @field_validator('criteria_type')
    @classmethod
    def validate_criteria_type(cls, v: str) -> str:
        """Ensure criteria_type is valid"""
        valid_types = ['email_verified', 'quiz_completed', 'perfect_quiz', 'high_score_quiz', 'correct_answers', 'level_reached', 'exam_specific', 'multi_domain']
        if v not in valid_types:
            raise ValueError(f'Criteria type must be one of: {", ".join(valid_types)}')
        return v


class AchievementUpdate(BaseModel):
    """Schema for updating an achievement (all fields optional)"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, min_length=1)
    icon: Optional[str] = Field(None, max_length=50)
    criteria_type: Optional[str] = None
    criteria_value: Optional[int] = Field(None, ge=1)
    criteria_exam_type: Optional[str] = None
    xp_reward: Optional[int] = Field(None, ge=0)

    @field_validator('criteria_type')
    @classmethod
    def validate_criteria_type(cls, v: Optional[str]) -> Optional[str]:
        """Ensure criteria_type is valid if provided"""
        if v is not None:
            valid_types = ['email_verified', 'quiz_completed', 'perfect_quiz', 'high_score_quiz', 'correct_answers', 'level_reached', 'exam_specific', 'multi_domain']
            if v not in valid_types:
                raise ValueError(f'Criteria type must be one of: {", ".join(valid_types)}')
        return v


class AchievementResponse(BaseModel):
    """Schema for achievement response"""
    id: int
    name: str
    description: str
    icon: str
    criteria_type: str
    criteria_value: int
    criteria_exam_type: Optional[str]
    xp_reward: int
    created_at: datetime

    class Config:
        from_attributes = True


class AchievementListResponse(BaseModel):
    """Schema for achievement list"""
    total: int
    achievements: List[AchievementResponse]
