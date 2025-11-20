# Development Guide

Complete guide for developers working on the Billings Study Platform.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Running Services](#running-services)
3. [Development Workflow](#development-workflow)
4. [Database Management](#database-management)
5. [Testing](#testing)
6. [Troubleshooting](#troubleshooting)
7. [Deployment](#deployment)

---

## Architecture Overview

### Services

```
┌─────────────┐     ┌──────────────┐     ┌────────────┐
│  Frontend   │────▶│   Backend    │────▶│ PostgreSQL │
│ (Port 8080) │     │  (Port 8000) │     │ (Port 5432)│
└─────────────┘     └──────────────┘     └────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │   pgAdmin    │
                    │ (Port 5050)  │
                    └──────────────┘
```

### Docker Containers

- **billings_backend** - FastAPI application (Python 3.12)
- **billings_db** - PostgreSQL 15 database
- **billings_pgadmin** - Database admin interface

All services are defined in `backend/docker-compose.yml` and networked together.

### Key Directories

```
backend/
├── app/
│   ├── api/v1/          # API endpoints
│   ├── controllers/     # Business logic orchestration
│   ├── services/        # Core business logic
│   ├── models/          # SQLAlchemy models
│   ├── schemas/         # Pydantic schemas
│   ├── db/              # Database config & seeds
│   ├── utils/           # Helper functions
│   └── main.py          # FastAPI app entry point
├── scripts/             # Utility scripts
├── questions/           # CSV question files (gitignored)
├── Dockerfile           # Backend container
└── docker-compose.yml   # Service orchestration
```

---

## Running Services

### Start All Services

```bash
cd backend
docker-compose up -d
```

Services start in dependency order: `db` → `backend` → `pgadmin`

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f db
```

### Stop All Services

```bash
docker-compose down
```

**⚠️ WARNING**: Never use `-v` flag unless you want to **delete all database data**:

```bash
docker-compose down -v  # DESTROYS DATABASE!
```

### Restart a Service

```bash
docker-compose restart backend
docker-compose restart db
```

### Check Service Status

```bash
docker-compose ps
```

---

## Development Workflow

### Making Code Changes

The backend code is **mounted as a volume** in the container, so changes are reflected immediately with auto-reload.

```bash
# 1. Edit code in your editor
vim backend/app/api/v1/quiz.py

# 2. uvicorn inside container auto-reloads
# Check logs:
docker-compose logs -f backend

# 3. Test your changes
curl http://localhost:8000/api/v1/quiz/random
```

### Adding Python Dependencies

```bash
# 1. Add package to requirements.txt
echo "new-package==1.0.0" >> backend/requirements.txt

# 2. Rebuild backend container
docker-compose down
docker-compose build backend
docker-compose up -d
```

### Accessing Python Shell Inside Container

```bash
docker exec -it billings_backend python

# Then in Python:
from app.db.session import SessionLocal
from app.models.user import User
db = SessionLocal()
users = db.query(User).all()
print(users)
```

### Running Scripts Inside Container

```bash
# Import questions
docker exec billings_backend python scripts/import_questions.py

# Create admin
docker exec -it billings_backend python scripts/create_admin.py

# Custom script
docker exec billings_backend python scripts/your_script.py
```

---

## Database Management

### Accessing PostgreSQL

```bash
# Via psql
docker exec -it billings_db psql -U postgres -d billings

# List tables
\dt

# Describe table
\d users

# Query
SELECT * FROM users LIMIT 5;

# Exit
\q
```

### Using pgAdmin

1. Open http://localhost:5050
2. Login: `admin@admin.com` / `admin`
3. Add server:
   - Host: `db`
   - Port: `5432`
   - Username: `postgres`
   - Password: `postgres`
   - Database: `billings`

### Database Migrations

```bash
# Create new migration
docker exec billings_backend alembic revision --autogenerate -m "Add new column"

# Apply migrations
docker exec billings_backend alembic upgrade head

# Rollback one migration
docker exec billings_backend alembic downgrade -1

# View migration history
docker exec billings_backend alembic history
```

### Reset Database (Nuclear Option)

```bash
# Stop and remove containers + volumes
docker-compose down -v

# Restart
docker-compose up -d

# Re-run migrations
docker exec billings_backend alembic upgrade head

# Re-import questions
docker exec billings_backend python scripts/import_questions.py

# Re-seed data
docker exec billings_backend python -m app.db.seed_achievements_v2
docker exec billings_backend python -m app.db.seed_avatars_v2

# Re-create admin
docker exec -it billings_backend python scripts/create_admin.py
```

### Backup & Restore

```bash
# Backup
docker exec billings_db pg_dump -U postgres billings > backup.sql

# Restore
docker exec -i billings_db psql -U postgres billings < backup.sql
```

---

## Testing

### Run Tests

```bash
# All tests
docker exec billings_backend pytest

# Specific file
docker exec billings_backend pytest tests/unit/services/test_quiz_service.py

# With coverage
docker exec billings_backend pytest --cov=app --cov-report=html

# View coverage report (copy from container)
docker cp billings_backend:/app/htmlcov ./htmlcov
open htmlcov/index.html
```

### Test Categories

```bash
# Unit tests only
docker exec billings_backend pytest -m unit

# Integration tests only
docker exec billings_backend pytest -m integration

# Verbose output
docker exec billings_backend pytest -v
```

### Writing Tests

Tests are in `backend/tests/`:

```python
# tests/unit/services/test_example.py
import pytest
from app.services.example import example_function

def test_example():
    result = example_function()
    assert result == expected_value
```

---

## Troubleshooting

### Port Already in Use

**Problem**: Can't start service because port is occupied.

```
Error: Bind for 0.0.0.0:8000 failed: port is already allocated
```

**Solution**:

```bash
# Find process using port
lsof -i :8000

# Kill it
kill -9 <PID>

# Or kill all on port in one command
lsof -ti :8000 | xargs -r kill -9
```

### Database Connection Refused

**Problem**: Backend can't connect to database.

```
sqlalchemy.exc.OperationalError: connection to server at "db" failed
```

**Solution**:

```bash
# Check if db container is running
docker ps | grep billings_db

# Check db logs
docker-compose logs db

# Restart database
docker-compose restart db

# If still failing, restart everything
docker-compose down
docker-compose up -d
```

### Container Won't Start

**Problem**: Container immediately exits.

```bash
# Check what went wrong
docker-compose logs backend

# Common issues:
# - Syntax error in Python code
# - Missing .env file
# - Database not ready yet
```

**Solution**:

```bash
# Check logs first
docker-compose logs backend

# Try rebuilding
docker-compose down
docker-compose build --no-cache backend
docker-compose up -d
```

### Changes Not Reflected

**Problem**: Code changes don't appear when you refresh.

**Solution**:

```bash
# 1. Check if volume mount is working
docker-compose exec backend ls -la /app/app

# 2. Restart backend with reload
docker-compose restart backend

# 3. If still not working, rebuild
docker-compose down
docker-compose up -d
```

### MODULE_NOT_FOUND Error

**Problem**: Python can't find a module.

```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution**:

```bash
# Rebuild container with dependencies
docker-compose down
docker-compose build backend
docker-compose up -d
```

### Environment Variable Not Set

**Problem**: `DATABASE_URL` or other env var missing.

**Solution**:

```bash
# Check if .env exists
ls -la backend/.env

# Check if docker-compose reads it
docker-compose config | grep DATABASE_URL

# Ensure .env is in backend/ directory (same as docker-compose.yml)

# Restart after fixing .env
docker-compose down
docker-compose up -d
```

### Database Has Wrong Hostname

**Problem**: App tries to connect to `localhost` instead of `db`.

**Solution**:

```bash
# Check your .env file
grep DATABASE_URL backend/.env

# Should be:
DATABASE_URL=postgresql://postgres:postgres@db:5432/billings

# NOT:
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/billings

# If wrong, fix it and restart
docker-compose down
docker-compose up -d
```

### Can't Access pgAdmin

**Problem**: http://localhost:5050 doesn't load.

**Solution**:

```bash
# Check if container is running
docker ps | grep pgadmin

# Check logs
docker-compose logs pgadmin

# Restart
docker-compose restart pgadmin
```

---

## Deployment

### Building for Production

```bash
# Build optimized image
docker build -t billings-backend:latest -f backend/Dockerfile backend/

# Run in production mode (without --reload)
docker run -p 8000:8000 --env-file .env billings-backend:latest \
  uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Production Checklist

- [ ] Set strong `JWT_SECRET`
- [ ] Use production database (not Docker)
- [ ] Set `DEBUG=false` in environment
- [ ] Configure CORS for production domain
- [ ] Set up HTTPS/SSL
- [ ] Configure proper email SMTP
- [ ] Set up database backups
- [ ] Configure logging
- [ ] Set up monitoring

### Environment Differences

| Variable | Development | Production |
|----------|-------------|------------|
| `DATABASE_URL` | `db:5432` (Docker) | External PostgreSQL |
| `JWT_SECRET` | Any value | Strong 32+ char secret |
| `DEBUG` | `true` | `false` |
| `FRONTEND_URL` | `localhost:8080` | `https://your-domain.com` |

---

## Useful Commands

### Docker

```bash
# View all containers
docker ps -a

# Remove stopped containers
docker container prune

# View images
docker images

# Remove unused images
docker image prune

# View volumes
docker volume ls

# Remove unused volumes (CAREFUL!)
docker volume prune

# View networks
docker network ls

# Inspect container
docker inspect billings_backend

# Copy file from container
docker cp billings_backend:/app/file.txt ./file.txt

# Execute bash in container
docker exec -it billings_backend bash
```

### Database Queries

```bash
# Count users
docker exec billings_db psql -U postgres -d billings -c "SELECT COUNT(*) FROM users;"

# Count questions
docker exec billings_db psql -U postgres -d billings -c "SELECT COUNT(*) FROM questions;"

# View recent quiz attempts
docker exec billings_db psql -U postgres -d billings -c "SELECT * FROM quiz_attempts ORDER BY completed_at DESC LIMIT 5;"
```

### Kill Processes by Port

```bash
# Port 8000 (backend)
lsof -ti :8000 | xargs -r kill -9

# Port 8080 (frontend)
lsof -ti :8080 | xargs -r kill -9

# Port 5432 (postgres)
lsof -ti :5432 | xargs -r kill -9
```

---

## Additional Resources

- **API Documentation**: http://localhost:8000/docs (when running)
- **Architecture Details**: See `.claude/ARCHITECTURE.md`
- **Database Schema**: See `.claude/DATABASE.md`
- **API Endpoints**: See `.claude/API_ENDPOINTS.md`
- **Testing Guide**: See `.claude/TESTING.md`

---

## Getting Help

If you run into issues:

1. Check logs: `docker-compose logs -f backend`
2. Check this troubleshooting section
3. Search for error message online
4. Ask Claude Code for help!
