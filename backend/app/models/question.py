# MODEL LAYER: Question model for CompTIA exam practice

# SQLAlchemy column types
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey

# For timestamps
from datetime import datetime

# Declarative base - all models inherit from this
# Defined in: app/db/base.py
from app.db.base import Base


# QUESTION MODEL
# Used by: scripts/import_questions.py (CSV import script)
# Will be used by: Question service (not yet implemented)
# This class maps to the "questions" table in PostgreSQL
class Question(Base):
    """CompTIA exam question model - populated from CSV files"""
    __tablename__ = "questions"  # PostgreSQL table name

    # ============================================
    # PRIMARY KEY
    # ============================================
    id = Column(Integer, primary_key=True, index=True)  # Database auto-increment ID

    # ============================================
    # QUESTION IDENTIFICATION
    # ============================================
    # String type supports various ID formats: "0", "1", "A1", "Q123", etc.
    question_id = Column(String, index=True)  # External ID from CSV file

    # ============================================
    # CATEGORIZATION (all indexed for fast filtering)
    # ============================================
    # Exam type: "security", "network", "a1101", "a1102"
    # Indexed for queries like: SELECT * FROM questions WHERE exam_type = 'security'
    exam_type = Column(String, index=True)

    # CompTIA domain/objective: "1.1", "1.2", "2.3", etc.
    # Indexed for filtering by domain
    domain = Column(String, index=True)

    # ============================================
    # QUESTION CONTENT
    # ============================================
    question_text = Column(Text, nullable=False)  # The actual question

    # ============================================
    # ANSWER DATA
    # ============================================
    correct_answer = Column(String, nullable=False)  # Letter: "A", "B", "C", or "D"

    # JSON column stores all answer choices with explanations
    # Populated by: scripts/import_questions.py
    # Structure:
    # {
    #   "A": {"text": "First option", "explanation": "Why correct/incorrect"},
    #   "B": {"text": "Second option", "explanation": "Why correct/incorrect"},
    #   "C": {"text": "Third option", "explanation": "Why correct/incorrect"},
    #   "D": {"text": "Fourth option", "explanation": "Why correct/incorrect"}
    # }
    options = Column(JSON, nullable=False)  # PostgreSQL's native JSON type

    # ============================================
    # TIMESTAMPS
    # ============================================
    created_at = Column(DateTime, default=datetime.utcnow)  # When question was imported


# QUESTION BOOKMARK MODEL
# Tracks which questions users have bookmarked for later review
class QuestionBookmark(Base):
    """User bookmarks for questions"""
    __tablename__ = "question_bookmarks"

    # Composite primary key (user_id + question_id)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), primary_key=True)

    # Optional notes for the bookmark
    notes = Column(Text, nullable=True)

    # Timestamp when bookmark was created
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
