# SERVICE LAYER - Database operations for Question Bookmarks
#
# What services DO:
# - Execute SQL queries (SELECT, INSERT, UPDATE, DELETE)
# - Return database models or None
# - Simple, focused functions (one query per function)
#
# What services DON'T DO:
# - Business logic decisions (that's what CONTROLLERS do)
# - HTTP error handling (that's what CONTROLLERS do)
# - Complex workflows (that's what CONTROLLERS do)

from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.question import QuestionBookmark, Question
from typing import List, Tuple, Optional
from datetime import datetime


def create_bookmark(
    db: Session,
    user_id: int,
    question_id: int,
    notes: Optional[str] = None
) -> QuestionBookmark:
    """
    DATABASE OPERATION: Insert or update bookmark

    SQL executed: INSERT INTO question_bookmarks ... ON CONFLICT UPDATE
    Returns: QuestionBookmark model
    """
    # Check if bookmark already exists
    existing = db.query(QuestionBookmark).filter(
        QuestionBookmark.user_id == user_id,
        QuestionBookmark.question_id == question_id
    ).first()

    if existing:
        # Update existing bookmark
        existing.notes = notes
        db.commit()
        db.refresh(existing)
        return existing
    else:
        # Create new bookmark
        bookmark = QuestionBookmark(
            user_id=user_id,
            question_id=question_id,
            notes=notes,
            created_at=datetime.utcnow()
        )
        db.add(bookmark)
        db.commit()
        db.refresh(bookmark)
        return bookmark


def get_user_bookmarks(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 10
) -> Tuple[List[Tuple[QuestionBookmark, Question]], int]:
    """
    DATABASE OPERATION: Get user's bookmarks with pagination

    SQL executed:
        SELECT * FROM question_bookmarks
        JOIN questions ON question_bookmarks.question_id = questions.id
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ? OFFSET ?

    Returns: Tuple of (list of (bookmark, question) tuples, total_count)
    """
    # Get total count
    total = db.query(func.count(QuestionBookmark.user_id)).filter(
        QuestionBookmark.user_id == user_id
    ).scalar()

    # Get bookmarks with associated questions
    bookmarks = db.query(QuestionBookmark, Question).join(
        Question,
        QuestionBookmark.question_id == Question.id
    ).filter(
        QuestionBookmark.user_id == user_id
    ).order_by(
        QuestionBookmark.created_at.desc()
    ).offset(skip).limit(limit).all()

    return bookmarks, total


def get_bookmark(
    db: Session,
    user_id: int,
    question_id: int
) -> Optional[QuestionBookmark]:
    """
    DATABASE OPERATION: Get specific bookmark

    SQL executed:
        SELECT * FROM question_bookmarks
        WHERE user_id = ? AND question_id = ?

    Returns: QuestionBookmark or None
    """
    return db.query(QuestionBookmark).filter(
        QuestionBookmark.user_id == user_id,
        QuestionBookmark.question_id == question_id
    ).first()


def delete_bookmark(
    db: Session,
    user_id: int,
    question_id: int
) -> bool:
    """
    DATABASE OPERATION: Delete bookmark

    SQL executed:
        DELETE FROM question_bookmarks
        WHERE user_id = ? AND question_id = ?

    Returns: True if deleted, False if not found
    """
    bookmark = db.query(QuestionBookmark).filter(
        QuestionBookmark.user_id == user_id,
        QuestionBookmark.question_id == question_id
    ).first()

    if bookmark:
        db.delete(bookmark)
        db.commit()
        return True
    return False


def update_bookmark_notes(
    db: Session,
    user_id: int,
    question_id: int,
    notes: Optional[str]
) -> Optional[QuestionBookmark]:
    """
    DATABASE OPERATION: Update bookmark notes

    SQL executed:
        UPDATE question_bookmarks
        SET notes = ?
        WHERE user_id = ? AND question_id = ?

    Returns: Updated QuestionBookmark or None if not found
    """
    bookmark = db.query(QuestionBookmark).filter(
        QuestionBookmark.user_id == user_id,
        QuestionBookmark.question_id == question_id
    ).first()

    if bookmark:
        bookmark.notes = notes
        db.commit()
        db.refresh(bookmark)
        return bookmark
    return None


def is_question_bookmarked(
    db: Session,
    user_id: int,
    question_id: int
) -> bool:
    """
    DATABASE OPERATION: Check if question is bookmarked

    SQL executed:
        SELECT 1 FROM question_bookmarks
        WHERE user_id = ? AND question_id = ?
        LIMIT 1

    Returns: True if bookmarked, False otherwise
    """
    return db.query(QuestionBookmark).filter(
        QuestionBookmark.user_id == user_id,
        QuestionBookmark.question_id == question_id
    ).first() is not None
