# app/schemas/question.py
# ================================================================
# PYDANTIC SCHEMAS FOR QUESTION API
# ================================================================
# Purpose: Define request/response data structures for quiz endpoints
# Used by: Routes to validate incoming requests and serialize responses
# ================================================================

from pydantic import BaseModel, Field
from typing import Dict, List


# ================================================================
# OPTION SCHEMA - Single Answer Choice
# ================================================================
# Represents one answer option (A, B, C, or D) with explanation
# Used in: QuestionResponse.options dictionary
# ================================================================

class OptionSchema(BaseModel):
    """
    Single answer option with text and explanation.

    Example:
        {
            "text": "Encryption at rest",
            "explanation": "Correct - This protects data while stored on disk"
        }
    """
    text: str = Field(..., description="The answer choice text")
    explanation: str = Field(..., description="Why this answer is correct or incorrect")


# ================================================================
# QUESTION RESPONSE SCHEMA - Complete Question Structure
# ================================================================
# What the API returns when sending a question to the frontend
# Used by: GET /api/v1/questions/quiz endpoint
# ================================================================

class QuestionResponse(BaseModel):
    """
    Complete question with all details (question text, options, correct answer).

    Database Source: questions table

    Example Response:
        {
            "id": 123,
            "question_id": "0",
            "exam_type": "security",
            "domain": "1.1",
            "question_text": "Which security control type focuses on...",
            "correct_answer": "B",
            "options": {
                "A": {"text": "Deterrent", "explanation": "Incorrect - ..."},
                "B": {"text": "Preventive", "explanation": "Correct - ..."},
                "C": {"text": "Detective", "explanation": "Incorrect - ..."},
                "D": {"text": "Corrective", "explanation": "Incorrect - ..."}
            }
        }
    """
    # Database fields
    id: int = Field(..., description="Database primary key")
    question_id: str = Field(..., description="External question ID from CSV (e.g., '0', '1', 'Q123')")
    exam_type: str = Field(..., description="Exam category: 'security', 'network', 'a1101', 'a1102'")
    domain: str = Field(..., description="CompTIA domain/objective (e.g., '1.1', '2.3')")
    question_text: str = Field(..., description="The actual question being asked")
    correct_answer: str = Field(..., description="Correct answer letter: 'A', 'B', 'C', or 'D'")
    options: Dict[str, OptionSchema] = Field(
        ...,
        description="All four answer choices with explanations (keys: 'A', 'B', 'C', 'D')"
    )

    # ============================================================
    # PYDANTIC CONFIGURATION
    # ============================================================
    # from_attributes=True allows SQLAlchemy models to be converted to Pydantic models
    # This enables: QuestionResponse.from_orm(question_db_object)
    # ============================================================

    class Config:
        from_attributes = True  # Formerly "orm_mode" in Pydantic v1


# ================================================================
# EXAM TYPES RESPONSE SCHEMA - List of Available Exams
# ================================================================
# What the API returns when frontend asks "what exams are available?"
# Used by: GET /api/v1/questions/exams endpoint
# ================================================================

class ExamTypesResponse(BaseModel):
    """
    List of available exam types from the database.

    Example Response:
        {
            "exams": ["a1101", "a1102", "network", "security"]
        }
    """
    exams: List[str] = Field(
        ...,
        description="Available exam types (e.g., ['security', 'network', 'a1101', 'a1102'])"
    )


# ================================================================
# QUIZ RESPONSE SCHEMA - Array of Questions with Metadata
# ================================================================
# Complete quiz response with exam info and questions array
# Used by: GET /api/v1/questions/quiz endpoint
# ================================================================

class QuizResponse(BaseModel):
    """
    Complete quiz response with metadata and questions.

    Example Response:
        {
            "exam_type": "security",
            "requested_count": 30,
            "actual_count": 30,
            "questions": [
                {...},  # QuestionResponse objects
                {...},
                ...
            ]
        }
    """
    exam_type: str = Field(..., description="The exam type for this quiz")
    requested_count: int = Field(..., description="Number of questions user requested")
    actual_count: int = Field(..., description="Actual number of questions returned (may be less if not enough available)")
    questions: List[QuestionResponse] = Field(..., description="Array of random questions")


# ================================================================
# DOMAIN RESPONSE SCHEMA - Single Domain with Question Count
# ================================================================
# Used by: GET /api/v1/questions/domains endpoint
# ================================================================

class DomainResponse(BaseModel):
    """
    Single domain with question count.

    Example Response:
        {
            "domain": "1.1",
            "question_count": 45
        }
    """
    domain: str = Field(..., description="CompTIA domain/objective (e.g., '1.1', '2.3')")
    question_count: int = Field(..., description="Number of questions available in this domain")


# ================================================================
# DOMAINS RESPONSE SCHEMA - List of Domains for an Exam
# ================================================================
# Used by: GET /api/v1/questions/domains endpoint
# ================================================================

class DomainsResponse(BaseModel):
    """
    List of domains for a specific exam type with question counts.

    Example Response:
        {
            "exam_type": "security",
            "domains": [
                {"domain": "1.1", "question_count": 45},
                {"domain": "1.2", "question_count": 32},
                {"domain": "2.1", "question_count": 28}
            ]
        }
    """
    exam_type: str = Field(..., description="The exam type these domains belong to")
    domains: List[DomainResponse] = Field(..., description="List of domains with question counts")


# ================================================================
# BOOKMARK SCHEMAS
# ================================================================

class BookmarkRequest(BaseModel):
    """
    Request to create or update a bookmark.

    Example Request:
        {
            "notes": "Review this question about encryption at rest"
        }
    """
    notes: str | None = Field(None, description="Optional notes for the bookmark", max_length=1000)


class BookmarkResponse(BaseModel):
    """
    Bookmark with associated question details.

    Example Response:
        {
            "question_id": 123,
            "notes": "Review this question",
            "created_at": "2024-01-15T10:30:00",
            "question": {
                "id": 123,
                "question_text": "Which security control...",
                ...
            }
        }
    """
    question_id: int = Field(..., description="ID of the bookmarked question")
    notes: str | None = Field(None, description="User's notes for this bookmark")
    created_at: str = Field(..., description="ISO 8601 timestamp when bookmark was created")
    question: QuestionResponse = Field(..., description="Full question details")

    class Config:
        from_attributes = True


class BookmarksListResponse(BaseModel):
    """
    Paginated list of bookmarks.

    Example Response:
        {
            "total": 15,
            "page": 1,
            "page_size": 10,
            "bookmarks": [...]
        }
    """
    total: int = Field(..., description="Total number of bookmarks")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of bookmarks per page")
    bookmarks: List[BookmarkResponse] = Field(..., description="List of bookmarks")
