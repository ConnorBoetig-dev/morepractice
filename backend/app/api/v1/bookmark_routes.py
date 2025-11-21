# ROUTE LAYER: Question Bookmark endpoints
#
# What routes DO:
# - Handle HTTP requests (GET, POST, PUT, DELETE)
# - Extract request data (path params, query params, request body)
# - Call controllers to process the request
# - Return HTTP responses
#
# What routes DON'T DO:
# - Business logic (that's what CONTROLLERS do)
# - Database queries (that's what SERVICES do)

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.utils.auth import get_current_user
from app.models.user import User
from app.schemas.question import (
    BookmarkRequest,
    BookmarkResponse,
    BookmarksListResponse
)
from app.controllers import bookmark_controller
from typing import Dict, Any

router = APIRouter(prefix="/bookmarks", tags=["bookmarks"])


@router.post(
    "/questions/{question_id}",
    response_model=BookmarkResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Bookmark a question"
)
def create_bookmark_route(
    question_id: int,
    request: BookmarkRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Bookmark a question for later review.

    - **question_id**: ID of the question to bookmark
    - **notes**: Optional notes about why you bookmarked this question

    If the question is already bookmarked, this will update the notes.
    """
    result = bookmark_controller.create_or_update_bookmark(
        db=db,
        user_id=current_user.id,
        question_id=question_id,
        notes=request.notes
    )
    return result


@router.get(
    "",
    response_model=BookmarksListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get user's bookmarks"
)
def get_bookmarks_route(
    page: int = Query(1, ge=1, description="Page number (starts at 1)"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page (1-100)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all bookmarks for the current user with pagination.

    - **page**: Page number (default: 1)
    - **page_size**: Number of bookmarks per page (default: 10, max: 100)

    Returns bookmarks ordered by most recently created first.
    """
    result = bookmark_controller.get_user_bookmarks_paginated(
        db=db,
        user_id=current_user.id,
        page=page,
        page_size=page_size
    )
    return result


@router.delete(
    "/questions/{question_id}",
    status_code=status.HTTP_200_OK,
    summary="Remove a bookmark"
)
def delete_bookmark_route(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Remove a bookmark from a question.

    - **question_id**: ID of the question to unbookmark

    Returns 404 if the bookmark doesn't exist.
    """
    result = bookmark_controller.remove_bookmark(
        db=db,
        user_id=current_user.id,
        question_id=question_id
    )
    return result


@router.patch(
    "/questions/{question_id}",
    response_model=BookmarkResponse,
    status_code=status.HTTP_200_OK,
    summary="Update bookmark notes"
)
def update_bookmark_route(
    question_id: int,
    request: BookmarkRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update the notes on an existing bookmark.

    - **question_id**: ID of the bookmarked question
    - **notes**: New notes (or null to remove notes)

    Returns 404 if the bookmark doesn't exist.
    """
    result = bookmark_controller.update_bookmark_notes_only(
        db=db,
        user_id=current_user.id,
        question_id=question_id,
        notes=request.notes
    )
    return result


@router.get(
    "/questions/{question_id}/check",
    status_code=status.HTTP_200_OK,
    summary="Check if question is bookmarked"
)
def check_bookmark_route(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, bool]:
    """
    Check if a question is bookmarked by the current user.

    - **question_id**: ID of the question to check

    Returns: {"is_bookmarked": true/false}
    """
    result = bookmark_controller.check_if_bookmarked(
        db=db,
        user_id=current_user.id,
        question_id=question_id
    )
    return result
