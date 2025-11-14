# app/db/session.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Will be replaced with real database URL soon
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/billings"

engine = create_engine(DATABASE_URL, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
