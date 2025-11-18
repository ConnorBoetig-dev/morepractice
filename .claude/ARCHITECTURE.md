# System Architecture

## Overview
**Billings** is a CompTIA exam preparation platform with comprehensive gamification features. Users take practice quizzes for various CompTIA certifications (Security+, Network+, A+ Core 1, A+ Core 2) and earn XP, level up, unlock achievements, collect avatars, and compete on leaderboards.

## Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.12)
- **ORM**: SQLAlchemy 2.0
- **Database**: PostgreSQL
- **Authentication**: JWT (JSON Web Tokens) with bcrypt password hashing
- **Migrations**: Alembic
- **Validation**: Pydantic V2 schemas
- **Testing**: pytest with pytest-cov

### Frontend
- **Current**: Vanilla HTML/CSS/JavaScript
- **Future**: Will be rebuilt (current version is temporary)

### Infrastructure
- **Database**: PostgreSQL running in Docker
- **Environment**: `.env` file for configuration (not committed to git)

## Architecture Layers

The backend follows a clean layered architecture:

```
┌─────────────────────────────────────────────────┐
│                  HTTP Client                     │
│              (Browser, Postman)                  │
└────────────────────┬────────────────────────────┘
                     │
                     │ HTTP Requests (JSON)
                     ▼
┌─────────────────────────────────────────────────┐
│          ROUTES (app/api/v1/*.py)                │
│  - Receive HTTP requests                         │
│  - Extract path/query parameters                 │
│  - Call controllers                              │
│  - Return HTTP responses                         │
└────────────────────┬────────────────────────────┘
                     │
                     │ Pydantic Schemas
                     ▼
┌─────────────────────────────────────────────────┐
│       CONTROLLERS (app/controllers/*.py)         │
│  - Orchestrate business logic                    │
│  - Call services                                 │
│  - Handle errors                                 │
└────────────────────┬────────────────────────────┘
                     │
                     │ Domain Objects
                     ▼
┌─────────────────────────────────────────────────┐
│        SERVICES (app/services/*.py)              │
│  - Business logic                                │
│  - Database queries                              │
│  - Achievement checking                          │
│  - XP/Level calculations                         │
└────────────────────┬────────────────────────────┘
                     │
                     │ ORM Models
                     ▼
┌─────────────────────────────────────────────────┐
│         MODELS (app/models/*.py)                 │
│  - SQLAlchemy ORM classes                        │
│  - Database table definitions                    │
│  - Relationships                                 │
└────────────────────┬────────────────────────────┘
                     │
                     │ SQL Queries
                     ▼
┌─────────────────────────────────────────────────┐
│            PostgreSQL Database                   │
│  - Persistent data storage                       │
│  - Foreign key constraints                       │
│  - Indexes for performance                       │
└─────────────────────────────────────────────────┘
```

## Data Flow

### Quiz Submission Flow
This is the most complex flow in the system, involving multiple services:

```
1. User submits quiz
   ↓
2. POST /api/v1/quiz/submit
   ↓
3. quiz_controller.submit_quiz()
   ↓
4. quiz_service.submit_quiz()
   - Create QuizAttempt record
   - Bulk create UserAnswer records
   - Calculate XP earned
   - Update UserProfile (XP, level, counters)
   - Return (quiz_attempt, xp_earned, new_level, level_up)
   ↓
5. achievement_service.check_and_award_achievements()
   - Get user stats
   - Check each achievement criteria
   - Award new achievements
   - Add XP rewards from achievements
   - Auto-unlock avatars from achievements
   - Return newly_unlocked[]
   ↓
6. Return response to client:
   {
     "quiz_attempt": {...},
     "xp_earned": 150,
     "new_level": 5,
     "level_up": true,
     "achievements_unlocked": [...]
   }
```

### Authentication Flow
```
1. POST /api/v1/auth/signup
   - Validate email/username/password
   - Hash password with bcrypt
   - Create User record
   - Create UserProfile record (XP=0, Level=1)
   - Auto-unlock default avatars
   - Return JWT token

2. POST /api/v1/auth/login
   - Find user by email
   - Verify password hash
   - Generate JWT token
   - Return token + user data

3. Protected routes
   - Extract JWT from Authorization header
   - Verify JWT signature
   - Extract user_id from token
   - Load user from database
   - Pass user to route handler
```

## Directory Structure

```
billings/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── auth_routes.py          # Auth endpoints
│   │   │       ├── question_routes.py      # Question fetching
│   │   │       ├── quiz_routes.py          # Quiz submission & history
│   │   │       ├── achievement_routes.py   # Achievement endpoints
│   │   │       ├── avatar_routes.py        # Avatar endpoints
│   │   │       └── leaderboard_routes.py   # Leaderboard endpoints
│   │   ├── controllers/
│   │   │   ├── auth_controller.py          # Auth business logic
│   │   │   └── quiz_controller.py          # Quiz orchestration
│   │   ├── db/
│   │   │   ├── base.py                     # SQLAlchemy Base
│   │   │   ├── session.py                  # Database connection
│   │   │   ├── seed_achievements.py        # Seed 27 achievements
│   │   │   └── seed_avatars.py             # Seed 18 avatars
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py                     # User, UserProfile
│   │   │   ├── question.py                 # Question
│   │   │   └── gamification.py             # QuizAttempt, UserAnswer,
│   │   │                                   # Achievement, UserAchievement,
│   │   │                                   # Avatar, UserAvatar
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py                     # Auth request/response schemas
│   │   │   ├── quiz.py                     # Quiz submission schemas
│   │   │   ├── achievement.py              # Achievement schemas
│   │   │   ├── avatar.py                   # Avatar schemas
│   │   │   └── leaderboard.py              # Leaderboard schemas
│   │   ├── services/
│   │   │   ├── achievement_service.py      # Achievement logic
│   │   │   ├── avatar_service.py           # Avatar unlock logic
│   │   │   ├── leaderboard_service.py      # Leaderboard queries
│   │   │   └── quiz_service.py             # Quiz submission logic
│   │   ├── utils/
│   │   │   └── auth.py                     # JWT creation/verification
│   │   └── main.py                         # FastAPI app entry point
│   ├── alembic/
│   │   ├── versions/
│   │   │   └── ee7ad33dca0c_*.py           # Gamification migration
│   │   └── alembic.ini                     # Alembic config
│   ├── tests/                              # Test directory
│   │   ├── unit/                           # Unit tests
│   │   └── integration/                    # Integration tests
│   ├── .env                                # Environment variables (not in git)
│   ├── requirements.txt                    # Python dependencies
│   └── pytest.ini                          # pytest configuration
├── frontend/                               # Temporary HTML/JS (will be rebuilt)
├── .claude/                                # Claude context documentation
│   ├── ARCHITECTURE.md                     # This file
│   ├── DATABASE.md                         # Database schema
│   ├── GAMIFICATION.md                     # Gamification system details
│   ├── API_ENDPOINTS.md                    # API reference
│   ├── BACKEND_COMPONENTS.md               # Code organization
│   ├── TESTING.md                          # Testing strategy
│   ├── QUICK_START.md                      # Quick start guide
│   └── FRONTEND_INTEGRATION.md             # Future frontend integration
└── README.md                               # Project README
```

## Environment Variables

Required environment variables (stored in `backend/.env`):

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/billings

# Authentication
JWT_SECRET=<32+ character random string>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080  # 7 days

# CORS
ALLOWED_ORIGINS=http://localhost:8080,http://127.0.0.1:8080
```

## Security Features

1. **Password Security**
   - Passwords hashed with bcrypt (12 rounds)
   - Never stored in plain text
   - Minimum password length validation

2. **JWT Authentication**
   - Tokens signed with HS256
   - 7-day expiration
   - Secret key validation (minimum 32 characters)

3. **CORS Protection**
   - Only allows requests from whitelisted origins
   - Credentials allowed for authenticated requests

4. **Database Security**
   - Foreign key constraints with CASCADE delete
   - CHECK constraints for data validation
   - No SQL injection (using ORM)

5. **Environment Variable Validation**
   - App fails fast if required vars missing
   - Warns if JWT_SECRET is weak

## Performance Optimizations

1. **Database Indexes**
   - Foreign keys indexed
   - Query columns indexed (exam_type, completed_at, user_id)
   - Composite indexes for common query patterns

2. **Bulk Operations**
   - Bulk insert for UserAnswer records (vs individual inserts)
   - Optimized lazy loading for relationships

3. **Query Optimization**
   - Using SQLAlchemy aggregations (COUNT, SUM, AVG)
   - Efficient window functions for leaderboard rankings
   - Minimal N+1 query issues

## Error Handling

1. **Database Errors**
   - Atomic transactions (rollback on error)
   - Graceful error messages

2. **Validation Errors**
   - Pydantic validation at API layer
   - SQLAlchemy CHECK constraints at database layer

3. **Authentication Errors**
   - 401 Unauthorized for invalid tokens
   - 403 Forbidden for insufficient permissions
   - 404 Not Found for missing resources

## Future Considerations

1. **Scalability**
   - Redis for caching leaderboards
   - Database connection pooling
   - CDN for avatar images

2. **Features**
   - Email verification
   - Password reset
   - Social authentication
   - Real-time notifications for achievements

3. **Frontend**
   - Complete rebuild with React/Vue/Svelte
   - Real-time leaderboard updates
   - Animated achievement unlocks
   - Profile customization
