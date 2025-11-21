"""
STUDY MODE CONTROLLER LAYER
Business logic for study mode operations

Controllers orchestrate between routes and services.
They handle:
- Business logic and validation
- Calling service layer functions
- Formatting responses
- Error handling

Study mode workflow:
1. start_study_session_controller → Start session, get first question
2. answer_study_question_controller → Answer question, get feedback + next question
3. (Repeat step 2 for each question)
4. complete_session_controller (optional) → Finalize and get results
"""

from sqlalchemy.orm import Session
from typing import Dict, Any, List
from fastapi import HTTPException, status

from app.services import study_service, achievement_service
from app.models.gamification import StudySession, QuizAttempt
from app.models.question import Question
from app.models.user import UserProfile
from app.utils.logger import get_logger

logger = get_logger(__name__)


def start_study_session_controller(
    db: Session,
    user_id: int,
    exam_type: str,
    count: int = 30,
    domain: str = None
) -> Dict[str, Any]:
    """
    Start a new study mode session

    Args:
        db: Database session
        user_id: User ID
        exam_type: Exam type (security, network, etc.)
        count: Number of questions (default 30)
        domain: Optional domain filter

    Returns:
        Dict with session_id, exam_type, total_questions, current_index, current_question

    Raises:
        HTTPException: If validation fails or session creation fails
    """
    # Start session (service layer handles validation)
    session, first_question = study_service.start_study_session(
        db=db,
        user_id=user_id,
        exam_type=exam_type,
        count=count,
        domain=domain
    )

    # Parse question IDs to get total count
    question_ids = [int(qid) for qid in session.question_ids.split(",")]

    # Format first question (hide correct answer and explanations)
    question_data = {
        "question_id": first_question.id,
        "question_text": first_question.question_text,
        "domain": first_question.domain,
        "options": {
            key: {"text": opt["text"]}
            for key, opt in first_question.options.items()
        }
    }

    return {
        "session_id": session.id,
        "exam_type": session.exam_type,
        "total_questions": len(question_ids),
        "current_index": session.current_index,
        "current_question": question_data
    }


def answer_study_question_controller(
    db: Session,
    session_id: int,
    user_id: int,
    question_id: int,
    user_answer: str,
    answers_history: List[tuple]  # Track answers for final completion
) -> Dict[str, Any]:
    """
    Answer current question in study session and get immediate feedback

    Args:
        db: Database session
        session_id: Study session ID
        user_id: User ID
        question_id: Question being answered
        user_answer: User's selected answer (A, B, C, D)
        answers_history: List of (question_id, user_answer, is_correct) for tracking

    Returns:
        Dict with feedback and next question (or completion status)

    Raises:
        HTTPException: If validation fails
    """
    # Submit answer and get feedback
    is_correct, current_question, next_question, session_completed = study_service.answer_study_question(
        db=db,
        session_id=session_id,
        user_id=user_id,
        question_id=question_id,
        user_answer=user_answer
    )

    # Add to answers history
    answers_history.append((question_id, user_answer, is_correct))

    # Parse session to get total questions
    session = db.query(StudySession).filter(StudySession.id == session_id).first()
    question_ids = [int(qid) for qid in session.question_ids.split(",")]
    total_questions = len(question_ids)
    current_index = session.current_index  # Already incremented by service

    # Build feedback response
    response = {
        "is_correct": is_correct,
        "user_answer": user_answer,
        "correct_answer": current_question.correct_answer,
        "user_answer_text": current_question.options[user_answer]["text"],
        "correct_answer_text": current_question.options[current_question.correct_answer]["text"],
        "user_answer_explanation": current_question.options[user_answer]["explanation"],
        "correct_answer_explanation": current_question.options[current_question.correct_answer]["explanation"],
        "all_options": current_question.options,
        "current_index": current_index,
        "total_questions": total_questions,
        "questions_remaining": total_questions - current_index,
        "session_completed": session_completed
    }

    # If session completed, finalize it
    if session_completed:
        # Complete the session
        quiz_attempt = study_service.complete_study_session(
            db=db,
            session_id=session_id,
            user_id=user_id,
            answers=answers_history
        )

        # Get user profile for leveling info
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

        # Check for achievements
        achievements_unlocked = achievement_service.check_and_award_achievements(
            db=db,
            user_id=user_id
        )

        # Add completion data to response
        response["next_question"] = None
        response["completion"] = {
            "quiz_attempt_id": quiz_attempt.id,
            "score": quiz_attempt.correct_answers,
            "total_questions": quiz_attempt.total_questions,
            "score_percentage": quiz_attempt.score_percentage,
            "xp_earned": quiz_attempt.xp_earned,
            "total_xp": profile.xp if profile else 0,
            "current_level": profile.level if profile else 1,
            "previous_level": (profile.level - 1) if profile and profile.level > 1 else 1,
            "level_up": False,  # TODO: Track level ups properly
            "achievements_unlocked": [
                {
                    "id": ach.achievement_id,
                    "name": ach.name,
                    "description": ach.description,
                    "icon": ach.icon,
                    "xp_reward": ach.xp_reward
                }
                for ach in achievements_unlocked
            ]
        }
    else:
        # Format next question (hide correct answer)
        next_question_data = {
            "question_id": next_question.id,
            "question_text": next_question.question_text,
            "domain": next_question.domain,
            "options": {
                key: {"text": opt["text"]}
                for key, opt in next_question.options.items()
            }
        }
        response["next_question"] = next_question_data

    return response


def get_active_session_controller(db: Session, user_id: int) -> Dict[str, Any]:
    """
    Get user's active study session if exists

    Args:
        db: Database session
        user_id: User ID

    Returns:
        Dict with session info or None

    Raises:
        HTTPException: If session not found
    """
    session = study_service.get_active_study_session(db=db, user_id=user_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "No active study session found",
                "code": "RESOURCE_NOT_FOUND"
            }
        )

    # Parse question IDs
    question_ids = [int(qid) for qid in session.question_ids.split(",")]

    # Get current question
    current_question_id = question_ids[session.current_index]
    current_question = db.query(Question).filter(Question.id == current_question_id).first()

    if not current_question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Current question not found",
                "code": "QUESTION_NOT_FOUND"
            }
        )

    # Format current question
    question_data = {
        "question_id": current_question.id,
        "question_text": current_question.question_text,
        "domain": current_question.domain,
        "options": {
            key: {"text": opt["text"]}
            for key, opt in current_question.options.items()
        }
    }

    return {
        "session_id": session.id,
        "exam_type": session.exam_type,
        "total_questions": len(question_ids),
        "current_index": session.current_index,
        "current_question": question_data
    }


def abandon_session_controller(db: Session, user_id: int) -> Dict[str, str]:
    """
    Abandon (delete) user's active study session

    Args:
        db: Database session
        user_id: User ID

    Returns:
        Success message

    Raises:
        HTTPException: If no active session
    """
    session = study_service.get_active_study_session(db=db, user_id=user_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "No active study session found",
                "code": "RESOURCE_NOT_FOUND"
            }
        )

    db.delete(session)
    db.commit()

    logger.info(f"User {user_id} abandoned study session {session.id}")

    return {
        "success": True,
        "message": "Study session abandoned successfully"
    }
