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


# ================================================================
# DATABASE DEPENDENCY - FastAPI Dependency Injection
# ================================================================
# This function is used with FastAPI's Depends() to inject a database
# session into route handlers
# ================================================================

def get_db():
    """
    FastAPI Dependency: Provides a database session for each request

    How it works:
        1. FastAPI calls this function before running the route handler
        2. Creates a new database session using SessionLocal()
        3. Yields the session to the route handler (via Depends(get_db))
        4. After the route finishes, closes the session (cleanup)

    Usage in routes:
        @router.get("/some-endpoint")
        def my_route(db: Session = Depends(get_db)):
            # db is automatically injected by FastAPI
            # Use db to query database
            users = db.query(User).all()
            return users
            # Session automatically closed after this function returns

    Why use yield instead of return:
        - yield makes this a generator function
        - Code after yield runs AFTER the route finishes (cleanup)
        - Ensures database connection is always closed, even if route errors

    Database Connection Lifecycle:
        Request → get_db() called → Session created → yield session
        → Route handler executes → Route finishes → Session closed
    """
    # Create new database session for this request
    db = SessionLocal()

    try:
        # Yield session to route handler
        # Everything after yield runs AFTER the route finishes
        yield db
    finally:
        # Always close the session when request is done
        # This happens even if the route raises an exception
        db.close()
