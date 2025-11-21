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


# ================================================================
# QUIZ REVIEW SCHEMAS
# ================================================================

class QuestionReviewDetail(BaseModel):
    """
    Detailed question information for review
    Includes user's answer, correct answer, and explanations
    """
    question_id: int = Field(..., description="Database ID of the question")
    question_text: str = Field(..., description="The question text")
    domain: str = Field(..., description="CompTIA domain/objective")
    user_answer: str = Field(..., description="User's selected answer")
    correct_answer: str = Field(..., description="The correct answer")
    is_correct: bool = Field(..., description="Whether user answered correctly")
    time_spent_seconds: Optional[int] = Field(None, description="Time spent on this question")

    # All options with text and explanations
    options: dict = Field(..., description="All answer options with explanations")

    # Helpful computed fields
    user_answer_text: str = Field(..., description="Text of user's selected answer")
    correct_answer_text: str = Field(..., description="Text of correct answer")
    user_answer_explanation: str = Field(..., description="Explanation for user's answer")
    correct_answer_explanation: str = Field(..., description="Explanation for correct answer")


class DomainPerformance(BaseModel):
    """
    Performance breakdown by domain
    """
    domain: str = Field(..., description="Domain identifier (e.g., '1.1', '2.3')")
    total_questions: int = Field(..., description="Total questions in this domain")
    correct_answers: int = Field(..., description="Number of correct answers")
    accuracy_percentage: float = Field(..., description="Accuracy percentage for this domain")


class QuizReviewResponse(BaseModel):
    """
    Complete quiz review with all questions, answers, and explanations
    Returned when user wants to review their answers after completing a quiz
    """
    # Quiz Metadata
    quiz_attempt_id: int = Field(..., description="Database ID of this quiz attempt")
    exam_type: str = Field(..., description="Exam type (security, network, etc.)")
    completed_at: datetime = Field(..., description="When the quiz was completed")

    # Overall Performance
    total_questions: int = Field(..., description="Total number of questions")
    correct_answers: int = Field(..., description="Number of correct answers")
    score_percentage: float = Field(..., description="Overall score percentage")
    time_taken_seconds: Optional[int] = Field(None, description="Total time spent on quiz")
    xp_earned: int = Field(..., description="XP earned from this quiz")

    # Detailed Review
    questions: List[QuestionReviewDetail] = Field(..., description="Detailed review of each question")

    # Performance Analytics
    domain_performance: List[DomainPerformance] = Field(
        default_factory=list,
        description="Performance breakdown by domain"
    )


# ================================================================
# STUDY MODE SCHEMAS
# ================================================================

class StudySessionStartRequest(BaseModel):
    """
    Request to start a new study mode session

    Study mode: answer questions one at a time with immediate feedback
    """
    exam_type: str = Field(..., description="Exam type (security, network, a1101, a1102)")
    count: int = Field(default=30, ge=1, le=100, description="Number of questions (1-100)")
    domain: Optional[str] = Field(None, description="Filter by domain (e.g., '1.1', '2.3')")

    @field_validator('exam_type')
    @classmethod
    def validate_exam_type(cls, v: str) -> str:
        """Ensure exam_type is valid"""
        valid_types = ['security', 'network', 'a1101', 'a1102']
        if v not in valid_types:
            raise ValueError(f'Exam type must be one of: {", ".join(valid_types)}')
        return v


class StudyQuestionDetail(BaseModel):
    """
    Question details for study mode (without correct answer revealed)
    """
    question_id: int = Field(..., description="Database ID of the question")
    question_text: str = Field(..., description="The question text")
    domain: str = Field(..., description="CompTIA domain/objective")
    options: dict = Field(..., description="Answer options (A, B, C, D) with text only")


class StudySessionResponse(BaseModel):
    """
    Response when starting a study session
    Includes first question and session metadata
    """
    session_id: int = Field(..., description="Study session ID")
    exam_type: str = Field(..., description="Exam type")
    total_questions: int = Field(..., description="Total questions in session")
    current_index: int = Field(..., description="Current question index (0-based)")
    current_question: StudyQuestionDetail = Field(..., description="The first question")

    class Config:
        from_attributes = True


class StudyQuestionAnswerRequest(BaseModel):
    """
    Submit answer for current question in study mode
    """
    session_id: int = Field(..., description="Study session ID")
    question_id: int = Field(..., description="Question being answered")
    user_answer: str = Field(..., description="User's selected answer (A, B, C, or D)")

    @field_validator('user_answer')
    @classmethod
    def validate_answer_choice(cls, v: str) -> str:
        """Ensure answer is A, B, C, or D"""
        if v not in ['A', 'B', 'C', 'D']:
            raise ValueError('Answer must be A, B, C, or D')
        return v


class StudyQuestionFeedbackResponse(BaseModel):
    """
    Immediate feedback after answering a question in study mode
    Shows whether correct/incorrect and all explanations
    """
    is_correct: bool = Field(..., description="Whether the answer was correct")
    user_answer: str = Field(..., description="User's selected answer")
    correct_answer: str = Field(..., description="The correct answer")

    # Full explanations for learning
    user_answer_text: str = Field(..., description="Text of user's selected answer")
    correct_answer_text: str = Field(..., description="Text of correct answer")
    user_answer_explanation: str = Field(..., description="Explanation for user's answer")
    correct_answer_explanation: str = Field(..., description="Explanation for correct answer")
    all_options: dict = Field(..., description="All options with explanations for review")

    # Progress tracking
    current_index: int = Field(..., description="Current question index")
    total_questions: int = Field(..., description="Total questions in session")
    questions_remaining: int = Field(..., description="Questions left to answer")

    # Next question (if not finished)
    next_question: Optional[StudyQuestionDetail] = Field(None, description="Next question (null if session complete)")
    session_completed: bool = Field(..., description="Whether this was the last question")

    # Completion data (only present when session_completed is True)
    completion: Optional[dict] = Field(None, description="Quiz results when session is completed")


class StudySessionCompleteResponse(BaseModel):
    """
    Final results when completing a study session
    Similar to quiz submission response
    """
    # Session Results
    session_id: int = Field(..., description="Study session ID")
    quiz_attempt_id: int = Field(..., description="Created quiz attempt ID")

    # Performance
    score: int = Field(..., description="Number of correct answers")
    total_questions: int = Field(..., description="Total questions answered")
    score_percentage: float = Field(..., description="Score as percentage (0-100)")

    # XP & Leveling
    xp_earned: int = Field(..., description="XP earned from this study session")
    total_xp: int = Field(..., description="User's total XP after this session")
    current_level: int = Field(..., description="User's current level")
    previous_level: int = Field(..., description="User's level before this session")
    level_up: bool = Field(..., description="Whether user leveled up")

    # Gamification
    achievements_unlocked: List[AchievementUnlocked] = Field(
        default_factory=list,
        description="Achievements unlocked by this study session"
    )

    class Config:
        from_attributes = True
