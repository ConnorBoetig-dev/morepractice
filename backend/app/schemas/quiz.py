"""
QUIZ SCHEMAS
Pydantic models for quiz submission and tracking API requests/responses

Used by:
- Quiz submission endpoint (POST /api/v1/quiz/submit)
- Quiz history endpoint (GET /api/v1/quiz/history)
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime

# Import AchievementUnlocked from achievement schemas (avoid duplication)
from app.schemas.achievement import AchievementUnlocked


# ================================================================
# REQUEST SCHEMAS
# ================================================================

class AnswerSubmission(BaseModel):
    """
    Single answer within a quiz submission
    """
    question_id: int = Field(..., description="Database ID of the question")
    user_answer: str = Field(..., description="User's selected answer (A, B, C, or D)")
    correct_answer: str = Field(..., description="The correct answer (A, B, C, or D)")
    is_correct: bool = Field(..., description="Whether the user answered correctly")
    time_spent_seconds: Optional[int] = Field(None, description="Time spent on this question in seconds")

    @field_validator('user_answer', 'correct_answer')
    @classmethod
    def validate_answer_choice(cls, v: str) -> str:
        """Ensure answer is A, B, C, or D"""
        if v not in ['A', 'B', 'C', 'D']:
            raise ValueError('Answer must be A, B, C, or D')
        return v

    @field_validator('time_spent_seconds')
    @classmethod
    def validate_time_spent(cls, v: Optional[int]) -> Optional[int]:
        """Ensure time spent is non-negative"""
        if v is not None and v < 0:
            raise ValueError('Time spent cannot be negative')
        return v


class QuizSubmission(BaseModel):
    """
    Complete quiz submission from frontend

    Sent when user completes a quiz and clicks "Finish Quiz"
    """
    exam_type: str = Field(..., description="Exam type (security, network, a1101, a1102)")
    total_questions: int = Field(..., gt=0, description="Total number of questions in the quiz")
    answers: List[AnswerSubmission] = Field(..., min_length=1, description="List of all answers")
    time_taken_seconds: Optional[int] = Field(None, description="Total time spent on quiz")

    @field_validator('exam_type')
    @classmethod
    def validate_exam_type(cls, v: str) -> str:
        """Ensure exam_type is valid"""
        valid_types = ['security', 'network', 'a1101', 'a1102']
        if v not in valid_types:
            raise ValueError(f'Exam type must be one of: {", ".join(valid_types)}')
        return v

    @field_validator('answers')
    @classmethod
    def validate_answers_count(cls, v: List[AnswerSubmission], info) -> List[AnswerSubmission]:
        """Ensure number of answers matches total_questions"""
        # Access total_questions from values dict if available
        if 'total_questions' in info.data and len(v) != info.data['total_questions']:
            raise ValueError(f'Number of answers ({len(v)}) must match total_questions ({info.data["total_questions"]})')
        return v

    @field_validator('time_taken_seconds')
    @classmethod
    def validate_time_taken(cls, v: Optional[int]) -> Optional[int]:
        """Ensure time taken is non-negative"""
        if v is not None and v < 0:
            raise ValueError('Time taken cannot be negative')
        return v


# ================================================================
# RESPONSE SCHEMAS
# ================================================================

class QuizSubmissionResponse(BaseModel):
    """
    Response after submitting a quiz

    Includes:
    - Quiz results and stats
    - XP earned and level progression
    - Any achievements unlocked
    """
    # Quiz Results
    quiz_attempt_id: int = Field(..., description="Database ID of this quiz attempt")
    score: int = Field(..., description="Number of correct answers")
    total_questions: int = Field(..., description="Total questions in quiz")
    score_percentage: float = Field(..., description="Score as percentage (0-100)")

    # XP & Leveling
    xp_earned: int = Field(..., description="XP earned from this quiz")
    total_xp: int = Field(..., description="User's total XP after this quiz")
    current_level: int = Field(..., description="User's current level")
    previous_level: int = Field(..., description="User's level before this quiz")
    level_up: bool = Field(..., description="Whether user leveled up")

    # Gamification
    achievements_unlocked: List[AchievementUnlocked] = Field(
        default_factory=list,
        description="Achievements unlocked by this quiz"
    )

    class Config:
        from_attributes = True  # Enable ORM mode for SQLAlchemy models


class QuizAttemptSummary(BaseModel):
    """
    Summary of a single quiz attempt for history/leaderboards
    """
    id: int
    exam_type: str
    total_questions: int
    correct_answers: int
    score_percentage: float
    xp_earned: int
    time_taken_seconds: Optional[int]
    completed_at: datetime

    class Config:
        from_attributes = True


class QuizHistoryResponse(BaseModel):
    """
    User's quiz attempt history
    """
    total_attempts: int
    attempts: List[QuizAttemptSummary]

    class Config:
        from_attributes = True
