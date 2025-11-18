# Quick Start Guide

## Prerequisites
- Python 3.12+
- PostgreSQL (via Docker)
- Node.js (for frontend, optional)

---

## First-Time Setup

### 1. Clone Repository
```bash
git clone <repository-url>
cd billings
```

### 2. Set Up Environment Variables
```bash
cd backend
cp .env.example .env
```

Edit `backend/.env`:
```bash
DATABASE_URL=postgresql://billings_user:billings_password@localhost:5432/billings
JWT_SECRET=<generate-a-32+-character-secret>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
```

**Generate Secure JWT Secret**:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. Start PostgreSQL Database
```bash
# If using docker-compose
docker-compose up -d postgres

# Or start manually
docker run --name billings-postgres \
  -e POSTGRES_USER=billings_user \
  -e POSTGRES_PASSWORD=billings_password \
  -e POSTGRES_DB=billings \
  -p 5432:5432 \
  -d postgres:14
```

### 4. Install Python Dependencies
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 5. Run Database Migrations
```bash
cd backend
alembic upgrade head
```

### 6. Seed Gamification Data
```bash
cd backend
python -m app.db.seed_achievements
python -m app.db.seed_avatars
```

### 7. Start Backend Server
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

Backend running at: http://localhost:8000

API Docs: http://localhost:8000/docs

### 8. Start Frontend (Optional)
```bash
cd frontend
python -m http.server 8080
# Or use Live Server in VS Code
```

Frontend running at: http://localhost:8080

---

## Daily Development Workflow

### Start Services
```bash
# Terminal 1: Start PostgreSQL
docker-compose up postgres

# Terminal 2: Start Backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# Terminal 3: Start Frontend (optional)
cd frontend
python -m http.server 8080
```

### Stop Services
```bash
# Stop backend: Ctrl+C in Terminal 2
# Stop frontend: Ctrl+C in Terminal 3
# Stop postgres: docker-compose stop postgres
```

---

## Common Commands

### Database Management

#### View Database
```bash
# Connect to PostgreSQL
docker exec -it billings-postgres psql -U billings_user -d billings

# List tables
\dt

# Describe table
\d users
\d quiz_attempts
\d achievements

# View data
SELECT * FROM users;
SELECT * FROM achievements;
SELECT * FROM quiz_attempts ORDER BY completed_at DESC LIMIT 5;

# Count records
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM achievements;

# Exit
\q
```

#### Reset Database
```bash
# Drop and recreate database
docker exec -it billings-postgres psql -U billings_user -d billings -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

# Re-run migrations
cd backend
alembic upgrade head

# Re-seed data
python -m app.db.seed_achievements
python -m app.db.seed_avatars
```

#### Create Migration
```bash
cd backend
alembic revision --autogenerate -m "Add new column to users table"
alembic upgrade head
```

#### Rollback Migration
```bash
cd backend
alembic downgrade -1
```

---

### Backend Development

#### Install New Package
```bash
cd backend
source venv/bin/activate
pip install <package-name>
pip freeze > requirements.txt
```

#### Run Python Shell with App Context
```bash
cd backend
source venv/bin/activate
python

# In Python shell:
from app.db.session import SessionLocal
from app.models.user import User, UserProfile
from app.models.gamification import Achievement, QuizAttempt

db = SessionLocal()

# Query users
users = db.query(User).all()
print(users)

# Query achievements
achievements = db.query(Achievement).all()
for a in achievements:
    print(f"{a.name}: {a.description}")

db.close()
```

#### Run Tests
```bash
cd backend
source venv/bin/activate

# All tests
pytest

# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# Specific file
pytest tests/unit/services/test_quiz_service.py

# With coverage
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

---

### API Testing

#### Using curl

**Signup**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "TestUser",
    "password": "SecurePassword123"
  }'
```

**Login**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePassword123"
  }'
```

**Get Profile** (with JWT):
```bash
TOKEN="<jwt-token-from-login>"

curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

**Get Achievements**:
```bash
curl -X GET http://localhost:8000/api/v1/achievements
```

**Submit Quiz**:
```bash
TOKEN="<jwt-token>"

curl -X POST http://localhost:8000/api/v1/quiz/submit \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "exam_type": "security_plus",
    "total_questions": 10,
    "time_taken_seconds": 600,
    "answers": [
      {
        "question_id": 1,
        "user_answer": "A",
        "correct_answer": "A",
        "is_correct": true,
        "time_spent_seconds": 60
      }
    ]
  }'
```

#### Using Postman/Insomnia
1. Import collection: `docs/api-collection.json` (if exists)
2. Set environment variable: `base_url = http://localhost:8000/api/v1`
3. Create requests for each endpoint (see API_ENDPOINTS.md)

---

## Seed Data

### Re-seed Achievements
```bash
cd backend
python -m app.db.seed_achievements
```

**Output**:
```
✅ Successfully seeded 27 achievements!

Achievement Categories:
  - Getting Started: 3 achievements
  - Accuracy: 4 achievements
  - Question Milestones: 4 achievements
  - Study Streaks: 4 achievements
  - A+ Core 1: 2 achievements
  - A+ Core 2: 2 achievements
  - Network+: 2 achievements
  - Security+: 2 achievements
  - Levels: 4 achievements

Total: 27 achievements
```

### Re-seed Avatars
```bash
cd backend
python -m app.db.seed_avatars
```

**Output**:
```
✅ Successfully seeded 18 avatars!

Avatar Categories:
  - Default (Common): 3 avatars
  - Achievement-Locked (Rare): 3 avatars
  - High-Tier (Epic): 7 avatars
  - Legendary: 5 avatars

Total: 18 avatars

Rarity Distribution:
  - Common: 3
  - Rare: 3
  - Epic: 7
  - Legendary: 5
```

---

## Troubleshooting

### Database Connection Error
```
Error: could not connect to server: Connection refused
```

**Fix**:
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Start PostgreSQL
docker-compose up -d postgres

# Check logs
docker logs billings-postgres
```

---

### Migration Error: "revision not found"
```
Error: Can't locate revision identified by 'xxxxx'
```

**Fix**:
```bash
# Reset alembic
cd backend
rm -rf alembic/versions/*
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

---

### Port Already in Use
```
Error: Address already in use: 8000
```

**Fix**:
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
uvicorn app.main:app --reload --port 8001
```

---

### JWT Token Expired
```
Error: 401 Unauthorized - Token expired
```

**Fix**: Login again to get a new token. Tokens expire after 7 days by default.

---

### Achievement/Avatar Seed Already Exists
```
⚠️ Achievements already exist (27 found). Skipping seed.
```

**To Re-seed**:
```bash
# Delete existing data
docker exec -it billings-postgres psql -U billings_user -d billings -c "DELETE FROM user_achievements;"
docker exec -it billings-postgres psql -U billings_user -d billings -c "DELETE FROM achievements;"

# Re-seed
python -m app.db.seed_achievements
```

---

## Project Structure Quick Reference

```
billings/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # API routes
│   │   ├── controllers/     # Business logic orchestration
│   │   ├── services/        # Core business logic
│   │   ├── models/          # Database models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── db/              # Database config & seeds
│   │   ├── utils/           # Helper functions
│   │   └── main.py          # FastAPI app
│   ├── alembic/             # Database migrations
│   ├── tests/               # Test suite
│   ├── .env                 # Environment variables
│   ├── requirements.txt     # Python dependencies
│   └── pytest.ini           # pytest config
├── frontend/                # Frontend (temporary)
└── .claude/                 # Claude context docs
    ├── ARCHITECTURE.md
    ├── DATABASE.md
    ├── GAMIFICATION.md
    ├── API_ENDPOINTS.md
    ├── BACKEND_COMPONENTS.md
    ├── TESTING.md
    ├── QUICK_START.md      # This file
    └── FRONTEND_INTEGRATION.md
```

---

## Key Files to Know

| File | Purpose |
|------|---------|
| `backend/app/main.py` | FastAPI app entry point |
| `backend/app/db/session.py` | Database connection |
| `backend/requirements.txt` | Python dependencies |
| `backend/.env` | Environment variables (not in git) |
| `backend/alembic.ini` | Alembic config |
| `backend/pytest.ini` | pytest config |

---

## Useful SQL Queries

### View User Stats
```sql
SELECT u.username, up.xp, up.level, up.study_streak_current, up.total_exams_taken
FROM users u
JOIN user_profiles up ON u.id = up.user_id
ORDER BY up.xp DESC
LIMIT 10;
```

### View Quiz Attempts
```sql
SELECT u.username, qa.exam_type, qa.score_percentage, qa.xp_earned, qa.completed_at
FROM quiz_attempts qa
JOIN users u ON qa.user_id = u.id
ORDER BY qa.completed_at DESC
LIMIT 10;
```

### View User Achievements
```sql
SELECT u.username, a.name, ua.earned_at
FROM user_achievements ua
JOIN users u ON ua.user_id = u.user_id
JOIN achievements a ON ua.achievement_id = a.id
ORDER BY ua.earned_at DESC
LIMIT 10;
```

### View Leaderboard (XP)
```sql
SELECT u.username, up.xp, up.level,
       RANK() OVER (ORDER BY up.xp DESC) as rank
FROM users u
JOIN user_profiles up ON u.id = up.user_id
ORDER BY up.xp DESC
LIMIT 10;
```

---

## Next Steps

After setup:
1. Read `.claude/ARCHITECTURE.md` for system overview
2. Read `.claude/DATABASE.md` for database schema
3. Read `.claude/GAMIFICATION.md` for gamification details
4. Read `.claude/API_ENDPOINTS.md` for API reference
5. Read `.claude/TESTING.md` for testing strategy

Ready to code!
