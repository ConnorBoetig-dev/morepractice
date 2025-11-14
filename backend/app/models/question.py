# app/models/question.py

from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from datetime import datetime

from app.db.base import Base

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)

    # ID from your CSV (string so it can support "0", "1", "A1", etc.)
    question_id = Column(String, index=True)

    # Security+, Network+, A+ Core 1, A+ Core 2
    exam_type = Column(String, index=True)

    # Domain like 1.1, 2.3
    domain = Column(String, index=True)

    # Main question text
    question_text = Column(Text, nullable=False)

    # "A", "B", "C", "D"
    correct_answer = Column(String, nullable=False)

    # JSON object storing all choices + explanations
    # Example:
    # {
    #   "A": {"text": "option text", "explanation": "why it’s right/wrong"},
    #   "B": {...},
    #   ...
    # }
    options = Column(JSON, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
