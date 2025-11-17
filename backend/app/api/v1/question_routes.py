# app/api/v1/question_routes.py
# ================================================================
# QUESTION ROUTES - REST API Endpoints
# ================================================================
# Purpose: Define HTTP endpoints for quiz functionality
# Architecture: Routes → Controllers → Services → Database
# Registered in: app/main.py
# ================================================================

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

# Import database session dependency
# Defined in: app/db/session.py
# This provides a database connection for each request
from app.db.session import get_db

# Import controller functions (business logic orchestration)
from app.controllers import question_controller

# Import Pydantic schemas for response validation
from app.schemas.question import (
    ExamTypesResponse,
    QuizResponse
)


# ================================================================
# ROUTER CONFIGURATION
# ================================================================
# Create FastAPI router with prefix and tags for API organization
# Prefix: /questions (will be /api/v1/questions when registered in main.py)
# Tags: Used for API documentation (groups endpoints in /docs)
# ================================================================

router = APIRouter(
    prefix="/questions",  # All routes will start with /questions
    tags=["questions"],   # OpenAPI/Swagger documentation tag
)


# ================================================================
# GET AVAILABLE EXAMS ENDPOINT
# ================================================================
# HTTP: GET /api/v1/questions/exams
# Purpose: Return list of available exam types
# Authentication: Not required (public endpoint)
# ================================================================

@router.get(
    "/exams",
    response_model=ExamTypesResponse,
    summary="Get Available Exam Types",
    description="Returns a list of all exam types that have questions in the database"
)
def get_exams_route(
    db: Session = Depends(get_db)  # Database session injected by FastAPI
):
    """
    API ENDPOINT: Get list of available exam types

    HTTP Method: GET
    URL: /api/v1/questions/exams
    Authentication: Not required

    Request:
        No parameters required

    Response:
        200 OK - Returns ExamTypesResponse
        {
            "exams": ["a1101", "a1102", "network", "security"]
        }

    Response Codes:
        200: Success - Returns list of exam types
        500: Server error - Database connection failed

    Example Usage:
        curl http://localhost:8000/api/v1/questions/exams

        JavaScript:
        const response = await fetch('http://localhost:8000/api/v1/questions/exams');
        const data = await response.json();
        console.log(data.exams);  // ["a1101", "a1102", "network", "security"]

    Implementation Flow:
        1. FastAPI injects database session via Depends(get_db)
        2. Call controller to orchestrate business logic
        3. Controller calls service to query database
        4. Service executes: SELECT DISTINCT exam_type FROM questions
        5. Response automatically validated by Pydantic schema
        6. FastAPI returns JSON response
    """
    # Call controller to handle business logic
    # Controller orchestrates: Service → Database → Response formatting
    return question_controller.get_exams_controller(db)


# ================================================================
# GET RANDOM QUIZ QUESTIONS ENDPOINT
# ================================================================
# HTTP: GET /api/v1/questions/quiz?exam_type=security&count=30
# Purpose: Generate a random quiz for a specific exam type
# Authentication: Not required (public endpoint)
# ================================================================

@router.get(
    "/quiz",
    response_model=QuizResponse,
    summary="Get Random Quiz Questions",
    description="Returns N random questions for a specific exam type"
)
def get_quiz_route(
    exam_type: str = Query(
        ...,  # Required parameter (no default)
        description="Exam type to generate quiz for",
        example="security"
    ),
    count: int = Query(
        10,  # Default to 10 questions
        ge=1,  # Greater than or equal to 1 (minimum)
        le=100,  # Less than or equal to 100 (maximum)
        description="Number of questions to include in quiz",
        example=30
    ),
    db: Session = Depends(get_db)  # Database session injected by FastAPI
):
    """
    API ENDPOINT: Get random quiz questions for an exam type

    HTTP Method: GET
    URL: /api/v1/questions/quiz?exam_type=security&count=30
    Authentication: Not required

    Query Parameters:
        exam_type (string, required):
            - Exam type to generate quiz for
            - Valid values: "security", "network", "a1101", "a1102"
            - Example: "security"

        count (integer, optional):
            - Number of questions to include
            - Default: 10
            - Minimum: 1
            - Maximum: 100
            - Example: 30

    Response:
        200 OK - Returns QuizResponse
        {
            "exam_type": "security",
            "requested_count": 30,
            "actual_count": 30,
            "questions": [
                {
                    "id": 123,
                    "question_id": "0",
                    "exam_type": "security",
                    "domain": "1.1",
                    "question_text": "Which security control...",
                    "correct_answer": "B",
                    "options": {
                        "A": {"text": "...", "explanation": "..."},
                        "B": {"text": "...", "explanation": "..."},
                        "C": {"text": "...", "explanation": "..."},
                        "D": {"text": "...", "explanation": "..."}
                    }
                },
                // ... 29 more questions
            ]
        }

    Response Codes:
        200: Success - Returns quiz with random questions
        400: Bad Request - Invalid count (< 1 or > 100)
        404: Not Found - Exam type doesn't exist
        500: Server error - Database connection failed

    Example Usage:
        # Get 30 random Security+ questions
        curl "http://localhost:8000/api/v1/questions/quiz?exam_type=security&count=30"

        # Get 10 random Network+ questions (default count)
        curl "http://localhost:8000/api/v1/questions/quiz?exam_type=network"

        JavaScript:
        const response = await fetch(
            'http://localhost:8000/api/v1/questions/quiz?exam_type=security&count=30'
        );
        const quiz = await response.json();
        console.log(`Got ${quiz.actual_count} questions for ${quiz.exam_type}`);

    Implementation Flow:
        1. FastAPI validates query parameters (exam_type, count)
        2. FastAPI injects database session via Depends(get_db)
        3. Call controller to orchestrate quiz generation
        4. Controller validates exam type exists (404 if not)
        5. Controller validates count is within limits (400 if not)
        6. Controller calls service to get random questions
        7. Service executes: SELECT * FROM questions WHERE exam_type = ? ORDER BY RANDOM() LIMIT ?
        8. Controller formats response with metadata
        9. Response automatically validated by Pydantic schema
        10. FastAPI returns JSON response

    Edge Cases Handled:
        - Exam type doesn't exist → 404 with helpful error
        - Count > available questions → Returns all available questions
        - Count < 1 → 400 Bad Request
        - Count > 100 → 400 Bad Request (enforced by Query validator)
    """
    # Call controller to handle quiz generation logic
    # Controller orchestrates:
    #   1. Validation (exam exists, count valid)
    #   2. Service layer (database queries)
    #   3. Response formatting (Pydantic schemas)
    return question_controller.get_quiz_controller(
        db=db,
        exam_type=exam_type,
        count=count
    )
