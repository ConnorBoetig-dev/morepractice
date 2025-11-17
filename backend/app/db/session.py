# DATABASE SESSION LAYER - PostgreSQL connection configuration
# Creates database engine and session factory for making queries

# SQLAlchemy - ORM library for database operations
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# For reading environment variables
import os

# Database connection URL - loaded from environment variables (.env file)
# Environment variables are loaded in app/main.py via load_dotenv()
# Format: postgresql://username:password@host:port/database_name
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/billings")

# Create database engine - manages connection pool to PostgreSQL
# echo=False disables SQL query logging (set to True for debugging)
engine = create_engine(DATABASE_URL, echo=False)

# Session factory - call SessionLocal() to create a new database session
# autocommit=False: Must explicitly call commit() to save changes
# autoflush=False: Don't automatically flush changes before queries
# bind=engine: Connect sessions to our PostgreSQL engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
