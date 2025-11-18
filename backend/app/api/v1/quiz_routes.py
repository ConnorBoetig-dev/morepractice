"""
QUIZ API ROUTES
Endpoints for quiz submission and history

Endpoints:
- POST /api/v1/quiz/submit - Submit completed quiz
- GET /api/v1/quiz/history - Get quiz attempt history
- GET /api/v1/quiz/stats - Get quiz statistics
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

# Import centralized rate limiter
from app.utils.rate_limit import limiter, RATE_LIMITS

from app.db.session import get_db
from app.utils.auth import get_current_user_id
from app.schemas.quiz import QuizSubmission, QuizSubmissionResponse, QuizHistoryResponse
from app.controllers import quiz_controller


# Create router
router = APIRouter(prefix="/quiz", tags=["quiz"])


@router.post(
    "/submit",
    response_model=QuizSubmissionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit completed quiz"
)
@limiter.limit(RATE_LIMITS["quiz_submit"])  # 10/minute rate limit
async def submit_quiz(
    request: Request,
    submission: QuizSubmission,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    Submit a completed quiz

    **Rate limit:** 10 requests per minute per IP (prevents spam submissions)

    **Process:**
    1. Validate quiz submission data
    2. Save quiz attempt and all answers to database
    3. Calculate XP earned and check for level up
    4. Update study streak automatically
    5. Check for newly unlocked achievements
    6. Return comprehensive results

    **Request Body:**
    ```json
    {
        "exam_type": "security",
        "total_questions": 30,
        "answers": [
            {
                "question_id": 123,
                "user_answer": "A",
                "correct_answer": "B",
                "is_correct": false,
                "time_spent_seconds": 45
            }
        ],
        "time_taken_seconds": 1800
    }
    ```

    **Response:**
    ```json
    {
        "quiz_attempt_id": 456,
        "score": 24,
        "total_questions": 30,
        "score_percentage": 80.0,
        "xp_earned": 240,
        "total_xp": 1240,
        "current_level": 5,
        "previous_level": 4,
        "level_up": true,
        "achievements_unlocked": []
    }
    ```

    **XP Calculation:**
    - Base: 10 XP per correct answer
    - Bonus: +50% for 90%+, +25% for 80%+, +10% for 70%+

    **Authentication:** Requires valid JWT token
    """
    # Apply rate limit: 10 quiz submissions per minute per IP
    try:
        return quiz_controller.submit_quiz(db, current_user_id, submission)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit quiz: {str(e)}"
        )


@router.get(
    "/history",
    response_model=QuizHistoryResponse,
    summary="Get quiz attempt history"
)
@limiter.limit(RATE_LIMITS["standard"])  # 30/minute rate limit
async def get_quiz_history(
    request: Request,
    limit: int = 20,
    offset: int = 0,
    exam_type: str = None,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    Get user's quiz attempt history with pagination

    **Rate limit:** 30 requests per minute per IP

    **Query Parameters:**
    - `limit`: Maximum number of attempts to return (default: 20, max: 100)
    - `offset`: Number of attempts to skip for pagination (default: 0)
    - `exam_type`: Optional filter by exam type (security, network, a1101, a1102)

    **Response:**
    ```json
    {
        "total_attempts": 150,
        "attempts": [
            {
                "id": 456,
                "exam_type": "security",
                "total_questions": 30,
                "correct_answers": 24,
                "score_percentage": 80.0,
                "xp_earned": 240,
                "time_taken_seconds": 1800,
                "completed_at": "2025-11-17T10:30:00"
            }
        ]
    }
    ```

    **Pagination Example:**
    - First page: `?limit=20&offset=0`
    - Second page: `?limit=20&offset=20`
    - Third page: `?limit=20&offset=40`

    **Authentication:** Requires valid JWT token
    """
    # Apply rate limit: 30 requests per minute per IP
    # Validate limit
    if limit > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Limit cannot exceed 100"
        )

    if limit < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Limit must be at least 1"
        )

    # Validate offset
    if offset < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Offset cannot be negative"
        )

    # Validate exam_type if provided
    if exam_type and exam_type not in ['security', 'network', 'a1101', 'a1102']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid exam type. Must be: security, network, a1101, or a1102"
        )

    try:
        return quiz_controller.get_quiz_history(
            db, current_user_id, limit, offset, exam_type
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get quiz history: {str(e)}"
        )


@router.get(
    "/stats",
    summary="Get quiz statistics"
)
@limiter.limit(RATE_LIMITS["standard"])  # 30/minute rate limit
async def get_quiz_stats(
    request: Request,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    Get aggregated quiz statistics for current user

    **Rate limit:** 30 requests per minute per IP

    **Response:**
    ```json
    {
        "total_attempts": 150,
        "total_questions_answered": 4500,
        "average_score": 78.5,
        "best_score": 96.7,
        "total_xp_earned": 45000,
        "stats_by_exam": {
            "security": {
                "attempts": 50,
                "questions_answered": 1500,
                "average_score": 80.2,
                "best_score": 96.7,
                "xp_earned": 15000
            }
        }
    }
    ```

    **Authentication:** Requires valid JWT token
    """
    # Apply rate limit: 30 requests per minute per IP
    try:
        return quiz_controller.get_quiz_stats(db, current_user_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get quiz stats: {str(e)}"
        )
