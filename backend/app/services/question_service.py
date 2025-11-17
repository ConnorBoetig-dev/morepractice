# app/services/question_service.py
# ================================================================
# QUESTION SERVICE - Database Query Layer
# ================================================================
# Purpose: Handle all database operations for questions (no HTTP knowledge)
# Called by: app/controllers/question_controller.py
# Architecture: Routes → Controllers → Services → Database
# ================================================================

from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from typing import List, Optional

# Import Question model - defined in app/models/question.py
from app.models.question import Question


# ================================================================
# GET AVAILABLE EXAMS - Query Distinct Exam Types
# ================================================================
# Returns list of unique exam types from the questions table
# Called by: question_controller.get_exams_controller()
# ================================================================

def get_available_exams(db: Session) -> List[str]:
    """
    DATABASE OPERATION: Query all unique exam types from questions table

    SQL executed:
        SELECT DISTINCT exam_type
        FROM questions
        ORDER BY exam_type ASC

    Returns:
        List of exam type strings (e.g., ['a1101', 'a1102', 'network', 'security'])

    Example:
        exams = get_available_exams(db)
        # Returns: ['a1101', 'a1102', 'network', 'security']
    """
    # Query database for distinct exam types (indexed column - fast lookup)
    # .distinct() removes duplicates
    # .order_by() sorts alphabetically for consistent ordering
    exam_types = db.query(distinct(Question.exam_type))\
        .order_by(Question.exam_type)\
        .all()

    # Convert from list of tuples [(exam1,), (exam2,)] to flat list [exam1, exam2]
    return [exam_type[0] for exam_type in exam_types]


# ================================================================
# VALIDATE EXAM TYPE - Check if Exam Exists in Database
# ================================================================
# Verifies that the requested exam type has questions in the database
# Called by: question_controller.get_quiz_controller()
# ================================================================

def validate_exam_type(db: Session, exam_type: str) -> bool:
    """
    DATABASE OPERATION: Check if exam type exists in questions table

    SQL executed:
        SELECT COUNT(*)
        FROM questions
        WHERE exam_type = 'security'
        LIMIT 1

    Args:
        db: Database session
        exam_type: Exam type to validate (e.g., 'security')

    Returns:
        True if exam type exists, False otherwise

    Example:
        is_valid = validate_exam_type(db, 'security')  # Returns: True
        is_valid = validate_exam_type(db, 'invalid')   # Returns: False
    """
    # Query database for at least one question with this exam_type
    # .filter() creates WHERE clause (indexed column - fast lookup)
    # .first() returns first match or None (efficient - stops after 1 row)
    exists = db.query(Question)\
        .filter(Question.exam_type == exam_type)\
        .first()

    # Convert to boolean (None = False, Question object = True)
    return exists is not None


# ================================================================
# GET EXAM QUESTION COUNT - Count Available Questions
# ================================================================
# Returns total number of questions available for an exam type
# Called by: question_controller.get_quiz_controller()
# ================================================================

def get_exam_question_count(db: Session, exam_type: str) -> int:
    """
    DATABASE OPERATION: Count questions for a specific exam type

    SQL executed:
        SELECT COUNT(*)
        FROM questions
        WHERE exam_type = 'security'

    Args:
        db: Database session
        exam_type: Exam type to count (e.g., 'security')

    Returns:
        Number of questions available (e.g., 987)

    Example:
        count = get_exam_question_count(db, 'security')  # Returns: 987
    """
    # Query database to count questions for this exam_type
    # .filter() creates WHERE clause (indexed column - fast lookup)
    # .count() executes COUNT(*) query
    return db.query(Question)\
        .filter(Question.exam_type == exam_type)\
        .count()


# ================================================================
# GET RANDOM QUESTIONS - Retrieve N Random Questions for Exam
# ================================================================
# Returns random questions for quiz generation
# Called by: question_controller.get_quiz_controller()
# ================================================================

def get_random_questions(
    db: Session,
    exam_type: str,
    count: int
) -> List[Question]:
    """
    DATABASE OPERATION: Get N random questions for a specific exam type

    SQL executed:
        SELECT *
        FROM questions
        WHERE exam_type = 'security'
        ORDER BY RANDOM()
        LIMIT 30

    Args:
        db: Database session
        exam_type: Exam type to filter by (e.g., 'security', 'network')
        count: Number of random questions to return

    Returns:
        List of Question model objects (randomized)

    Implementation Details:
        - Uses database-level randomization (ORDER BY RANDOM()) for efficiency
        - Filters by exam_type using indexed column (fast lookup)
        - Returns fewer questions if not enough available
        - Questions are truly random each time (no caching)

    Example:
        questions = get_random_questions(db, 'security', 30)
        # Returns: [Question(...), Question(...), ...] (30 random questions)
    """
    # Build query with filter and randomization
    # Step 1: db.query(Question) - Start query on questions table
    # Step 2: .filter() - Add WHERE clause for exam_type (indexed - fast)
    # Step 3: .order_by(func.random()) - Randomize results at database level
    # Step 4: .limit(count) - Only return requested number of questions
    # Step 5: .all() - Execute query and return all results as list

    questions = db.query(Question)\
        .filter(Question.exam_type == exam_type)\
        .order_by(func.random())\
        .limit(count)\
        .all()

    return questions


# ================================================================
# GET QUESTION BY ID - Retrieve Single Question
# ================================================================
# Returns a specific question by database ID
# Currently unused but useful for future features (review mode, specific questions)
# ================================================================

def get_question_by_id(db: Session, question_id: int) -> Optional[Question]:
    """
    DATABASE OPERATION: Get a specific question by database ID

    SQL executed:
        SELECT *
        FROM questions
        WHERE id = 123
        LIMIT 1

    Args:
        db: Database session
        question_id: Database primary key ID

    Returns:
        Question model object if found, None otherwise

    Example:
        question = get_question_by_id(db, 123)
        # Returns: Question(...) or None
    """
    # Query database for question by primary key
    # .filter() creates WHERE clause (primary key - instant lookup)
    # .first() returns first match or None
    return db.query(Question)\
        .filter(Question.id == question_id)\
        .first()
