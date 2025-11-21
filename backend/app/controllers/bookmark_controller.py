# CONTROLLER LAYER - Business logic for Question Bookmarks
#
# What controllers DO:
# - Orchestrate multiple service calls
# - Make business logic decisions
# - Validate data and handle errors
# - Return data to routes
#
# What controllers DON'T DO:
# - Direct database queries (that's what SERVICES do)
# - HTTP request/response handling (that's what ROUTES do)

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.services import bookmark_service
from app.models.question import Question
from typing import Dict, Any, List, Optional
from datetime import datetime


def create_or_update_bookmark(
    db: Session,
    user_id: int,
    question_id: int,
    notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create or update a question bookmark for a user.

    Business Logic:
    - Verify question exists
    - Create or update bookmark
    - Return bookmark with question details
    """
    # Verify question exists
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question with id {question_id} not found"
        )

    # Create or update bookmark
    bookmark = bookmark_service.create_bookmark(db, user_id, question_id, notes)

    # Return bookmark with question details
    return {
        "question_id": bookmark.question_id,
        "notes": bookmark.notes,
        "created_at": bookmark.created_at.isoformat(),
        "question": question
    }


def get_user_bookmarks_paginated(
    db: Session,
    user_id: int,
    page: int = 1,
    page_size: int = 10
) -> Dict[str, Any]:
    """
    Get user's bookmarks with pagination.

    Business Logic:
    - Validate pagination parameters
    - Get bookmarks from database
    - Format response with pagination metadata
    """
    # Validate pagination parameters
    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page must be >= 1"
        )
    if page_size < 1 or page_size > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page size must be between 1 and 100"
        )

    # Calculate offset
    skip = (page - 1) * page_size

    # Get bookmarks
    bookmarks, total = bookmark_service.get_user_bookmarks(db, user_id, skip, page_size)

    # Format response
    bookmark_list = []
    for bookmark, question in bookmarks:
        bookmark_list.append({
            "question_id": bookmark.question_id,
            "notes": bookmark.notes,
            "created_at": bookmark.created_at.isoformat(),
            "question": question
        })

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "bookmarks": bookmark_list
    }


def remove_bookmark(
    db: Session,
    user_id: int,
    question_id: int
) -> Dict[str, str]:
    """
    Remove a bookmark.

    Business Logic:
    - Verify bookmark exists
    - Delete bookmark
    - Return success message
    """
    deleted = bookmark_service.delete_bookmark(db, user_id, question_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bookmark not found for question {question_id}"
        )

    return {"message": "Bookmark removed successfully"}


def update_bookmark_notes_only(
    db: Session,
    user_id: int,
    question_id: int,
    notes: Optional[str]
) -> Dict[str, Any]:
    """
    Update only the notes of an existing bookmark.

    Business Logic:
    - Verify bookmark exists
    - Update notes
    - Return updated bookmark
    """
    bookmark = bookmark_service.update_bookmark_notes(db, user_id, question_id, notes)

    if not bookmark:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bookmark not found for question {question_id}"
        )

    # Get question details
    question = db.query(Question).filter(Question.id == question_id).first()

    return {
        "question_id": bookmark.question_id,
        "notes": bookmark.notes,
        "created_at": bookmark.created_at.isoformat(),
        "question": question
    }


def check_if_bookmarked(
    db: Session,
    user_id: int,
    question_id: int
) -> Dict[str, bool]:
    """
    Check if a question is bookmarked by the user.

    Business Logic:
    - Query bookmark existence
    - Return boolean result
    """
    is_bookmarked = bookmark_service.is_question_bookmarked(db, user_id, question_id)

    return {"is_bookmarked": is_bookmarked}
