# app/controllers/question_controller.py
# ================================================================
# QUESTION CONTROLLER - Business Logic Orchestration
# ================================================================
# Purpose: Orchestrate quiz generation logic between routes and services
# Called by: app/api/v1/question_routes.py
# Calls: app/services/question_service.py
# Architecture: Routes → Controllers → Services → Database
# ================================================================

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional

# Import service layer functions
from app.services import question_service

# Import Pydantic schemas for request/response validation
from app.schemas.question import (
    ExamTypesResponse,
    QuizResponse,
    QuestionResponse,
    DomainsResponse,
    DomainResponse
)


# ================================================================
# CONFIGURATION - Quiz Generation Settings
# ================================================================

# Maximum questions per quiz (prevent abuse/performance issues)
MAX_QUIZ_SIZE = 100

# Minimum questions per quiz (enforce reasonable quiz size)
MIN_QUIZ_SIZE = 1


# ================================================================
# GET EXAMS CONTROLLER - Orchestrate Getting Available Exams
# ================================================================
# Business logic: Query database and format response
# Called by: question_routes.get_exams_route()
# ================================================================

def get_exams_controller(db: Session) -> ExamTypesResponse:
    """
    CONTROLLER OPERATION: Get list of available exam types

    Flow:
        1. Call service layer to query database
        2. Format response using Pydantic schema
        3. Return structured response

    Args:
        db: Database session (injected by FastAPI Depends)

    Returns:
        ExamTypesResponse with list of exam types

    Example Response:
        {
            "exams": ["a1101", "a1102", "network", "security"]
        }

    Raises:
        HTTPException 500: If database query fails
    """
    # Step 1: Call service layer to get exam types from database
    # Service handles SQL query: SELECT DISTINCT exam_type FROM questions
    exams = question_service.get_available_exams(db)

    # Step 2: Format response using Pydantic schema (automatic validation)
    # This ensures response matches API contract
    response = ExamTypesResponse(exams=exams)

    # Step 3: Return structured response
    return response


# ================================================================
# GET QUIZ CONTROLLER - Orchestrate Quiz Generation
# ================================================================
# Business logic:
#   1. Validate exam type exists
#   2. Validate and cap quiz size
#   3. Get random questions
#   4. Format response with metadata
# Called by: question_routes.get_quiz_route()
# ================================================================

def get_quiz_controller(
    db: Session,
    exam_type: str,
    count: int,
    domain: Optional[str] = None
) -> QuizResponse:
    """
    CONTROLLER OPERATION: Generate a random quiz for an exam type

    Business Rules:
        - Exam type must exist in database (404 if not found)
        - Quiz size must be between MIN_QUIZ_SIZE and MAX_QUIZ_SIZE
        - If requested count > available questions, return all available
        - Questions are randomized at database level (efficient)
        - Optionally filter by domain

    Flow:
        1. Validate exam type exists
        2. Validate and cap quiz size
        3. Get available question count (with domain filter if provided)
        4. Adjust count if not enough questions
        5. Query random questions from database
        6. Format response with metadata

    Args:
        db: Database session (injected by FastAPI Depends)
        exam_type: Exam to generate quiz for (e.g., 'security')
        count: Number of questions requested
        domain: Optional domain filter (e.g., '1.1', '2.3')

    Returns:
        QuizResponse with exam metadata and questions array

    Example Response:
        {
            "exam_type": "security",
            "requested_count": 30,
            "actual_count": 30,
            "questions": [...]  # Array of 30 QuestionResponse objects
        }

    Raises:
        HTTPException 404: If exam type doesn't exist
        HTTPException 400: If count is invalid (< MIN_QUIZ_SIZE or > MAX_QUIZ_SIZE)
    """
    # ============================================================
    # STEP 1: VALIDATE EXAM TYPE EXISTS
    # ============================================================
    # Business rule: Only generate quizzes for valid exam types
    # Service query: SELECT * FROM questions WHERE exam_type = ? LIMIT 1
    # ============================================================

    exam_exists = question_service.validate_exam_type(db, exam_type)

    if not exam_exists:
        # Return 404 Not Found with helpful error message
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exam type '{exam_type}' not found. Available exams: {question_service.get_available_exams(db)}"
        )

    # ============================================================
    # STEP 2: VALIDATE QUIZ SIZE
    # ============================================================
    # Business rule: Enforce minimum and maximum quiz sizes
    # This prevents abuse and ensures reasonable quiz experience
    # ============================================================

    if count < MIN_QUIZ_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Quiz size must be at least {MIN_QUIZ_SIZE} question(s)"
        )

    if count > MAX_QUIZ_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Quiz size cannot exceed {MAX_QUIZ_SIZE} questions (requested: {count})"
        )

    # ============================================================
    # STEP 3: GET AVAILABLE QUESTION COUNT
    # ============================================================
    # Business rule: Don't request more questions than available
    # Service query: SELECT COUNT(*) FROM questions WHERE exam_type = ?
    # ============================================================

    available_count = question_service.get_exam_question_count(db, exam_type)

    # ============================================================
    # STEP 4: ADJUST COUNT IF NOT ENOUGH QUESTIONS
    # ============================================================
    # Business rule: If user requests 100 questions but only 50 exist,
    # return all 50 available (don't error, just return what we have)
    # ============================================================

    actual_count = min(count, available_count)
    requested_count = count  # Save original request for response metadata

    # ============================================================
    # STEP 5: QUERY RANDOM QUESTIONS
    # ============================================================
    # Service handles randomization at database level
    # Query: SELECT * FROM questions WHERE exam_type = ? [AND domain = ?] ORDER BY RANDOM() LIMIT ?
    # ============================================================

    questions = question_service.get_random_questions_filtered(
        db=db,
        exam_type=exam_type,
        count=actual_count,
        domain=domain
    )

    # ============================================================
    # STEP 6: FORMAT RESPONSE WITH METADATA
    # ============================================================
    # Convert SQLAlchemy models to Pydantic schemas (automatic validation)
    # Add metadata about quiz (exam type, requested vs actual count)
    # ============================================================

    # Convert Question models to QuestionResponse schemas
    # Pydantic automatically validates data structure
    question_responses = [
        QuestionResponse.model_validate(question)
        for question in questions
    ]

    # Build complete quiz response with metadata
    response = QuizResponse(
        exam_type=exam_type,
        requested_count=requested_count,
        actual_count=actual_count,
        questions=question_responses
    )

    return response


# ================================================================
# GET DOMAINS CONTROLLER - Get Domains for an Exam Type
# ================================================================
# Business logic: Query domains with question counts
# Called by: question_routes.get_domains_route()
# ================================================================

def get_domains_controller(db: Session, exam_type: str) -> DomainsResponse:
    """
    CONTROLLER OPERATION: Get list of domains for an exam type

    Flow:
        1. Validate exam type exists
        2. Call service layer to query domains with counts
        3. Format response using Pydantic schema
        4. Return structured response

    Args:
        db: Database session (injected by FastAPI Depends)
        exam_type: Exam type to get domains for (e.g., 'security')

    Returns:
        DomainsResponse with exam type and list of domains

    Example Response:
        {
            "exam_type": "security",
            "domains": [
                {"domain": "1.1", "question_count": 45},
                {"domain": "1.2", "question_count": 32}
            ]
        }

    Raises:
        HTTPException 404: If exam type doesn't exist
    """
    # Step 1: Validate exam type exists
    exam_exists = question_service.validate_exam_type(db, exam_type)

    if not exam_exists:
        # Return 404 Not Found with helpful error message
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exam type '{exam_type}' not found. Available exams: {question_service.get_available_exams(db)}"
        )

    # Step 2: Call service layer to get domains from database
    domains_data = question_service.get_domains_by_exam(db, exam_type)

    # Step 3: Format response using Pydantic schema (automatic validation)
    domain_responses = [
        DomainResponse(**domain_dict)
        for domain_dict in domains_data
    ]

    response = DomainsResponse(
        exam_type=exam_type,
        domains=domain_responses
    )

    # Step 4: Return structured response
    return response
