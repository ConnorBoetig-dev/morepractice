"""
STUDY MODE ROUTES
API endpoints for study mode (one question at a time with immediate feedback)

Study mode workflow:
1. POST /study/start → Start session, get first question
2. POST /study/answer → Answer question, get feedback + next question
3. Repeat step 2 until all questions answered
4. GET /study/active → Get current active session (resume)
5. DELETE /study/abandon → Abandon current session

All endpoints require authentication.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.db.session import get_db
from app.utils.auth import get_current_user
from app.models.user import User
from app.schemas.quiz import (
    StudySessionStartRequest,
    StudySessionResponse,
    StudyQuestionAnswerRequest,
    StudyQuestionFeedbackResponse
)
from app.controllers import study_controller

router = APIRouter(prefix="/study", tags=["Study Mode"])

# Store answers history per session (in production, use Redis or similar)
# Key: (user_id, session_id), Value: List[(question_id, user_answer, is_correct)]
_answers_cache: Dict[tuple, list] = {}


@router.post(
    "/start",
    response_model=StudySessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start study mode session"
)
def start_study_session_route(
    request: StudySessionStartRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Start a new study mode session

    Study mode:
    - Answer one question at a time
    - Get immediate feedback after each answer
    - See explanations for all options
    - Learn as you go

    vs Practice mode (quiz):
    - Answer all questions first
    - Get results at the end
    - Simulates real exam

    **Requirements:**
    - Must not have an active study session
    - Questions must be available for the exam type

    **Returns:**
    - Session ID
    - Total question count
    - First question (without correct answer)

    **Example workflow:**
    ```
    1. POST /study/start { exam_type: "security", count: 30 }
    2. POST /study/answer { session_id: 1, question_id: 123, user_answer: "A" }
    3. (Get immediate feedback + next question)
    4. POST /study/answer { session_id: 1, question_id: 124, user_answer: "C" }
    5. ... repeat until all questions answered
    ```
    """
    result = study_controller.start_study_session_controller(
        db=db,
        user_id=current_user.id,
        exam_type=request.exam_type,
        count=request.count,
        domain=request.domain
    )

    # Initialize answers history for this session
    cache_key = (current_user.id, result["session_id"])
    _answers_cache[cache_key] = []

    return result


@router.post(
    "/answer",
    response_model=StudyQuestionFeedbackResponse,
    status_code=status.HTTP_200_OK,
    summary="Answer question and get immediate feedback"
)
def answer_study_question_route(
    request: StudyQuestionAnswerRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submit answer for current question and get immediate feedback

    **Immediate feedback includes:**
    - Whether answer is correct/incorrect
    - Explanation for your answer
    - Explanation for correct answer
    - All option explanations for learning
    - Next question (if not finished)
    - Completion results (if last question)

    **If this is the last question:**
    - Session is automatically completed
    - Quiz attempt is created
    - XP is awarded
    - Achievements are checked
    - Final results are included in response

    **Error cases:**
    - 404: Session not found
    - 400: Session already completed
    - 400: Question mismatch (not current question)
    - 404: Question not found
    """
    # Get answers history from cache
    cache_key = (current_user.id, request.session_id)
    answers_history = _answers_cache.get(cache_key, [])

    result = study_controller.answer_study_question_controller(
        db=db,
        session_id=request.session_id,
        user_id=current_user.id,
        question_id=request.question_id,
        user_answer=request.user_answer,
        answers_history=answers_history
    )

    # Update cache
    _answers_cache[cache_key] = answers_history

    # Clean up cache if session completed
    if result.get("session_completed"):
        _answers_cache.pop(cache_key, None)

    return result


@router.get(
    "/active",
    response_model=StudySessionResponse,
    status_code=status.HTTP_200_OK,
    summary="Get active study session (resume)"
)
def get_active_study_session_route(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get user's currently active study session

    Use this to:
    - Resume a study session after closing the app
    - Check if user has an active session before starting new one
    - Get current question if page was refreshed

    **Returns:**
    - Session info
    - Current question (the one to answer next)

    **Error cases:**
    - 404: No active study session found
    """
    result = study_controller.get_active_session_controller(
        db=db,
        user_id=current_user.id
    )

    return result


@router.delete(
    "/abandon",
    status_code=status.HTTP_200_OK,
    summary="Abandon current study session"
)
def abandon_study_session_route(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Abandon (delete) current study session without completing it

    Use this when:
    - User wants to start a different exam type
    - User wants to restart with different settings
    - Session is no longer needed

    **Warning:** All progress in this session will be lost!

    **Returns:**
    - Success message

    **Error cases:**
    - 404: No active study session found
    """
    result = study_controller.abandon_session_controller(
        db=db,
        user_id=current_user.id
    )

    # Clean up cache
    # Find and remove cache entries for this user
    keys_to_remove = [key for key in _answers_cache.keys() if key[0] == current_user.id]
    for key in keys_to_remove:
        _answers_cache.pop(key, None)

    return result
