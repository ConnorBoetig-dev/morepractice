# Quick Command Reference

Copy-paste commands for common tasks.

## Daily Workflow

### Start Everything
```bash
cd backend
docker-compose up -d
```

### Stop Everything
```bash
cd backend
docker-compose down
```

### View Logs
```bash
docker-compose logs -f backend
docker-compose logs -f db
docker-compose logs -f  # all services
```

### Restart Backend
```bash
docker-compose restart backend
```

---

## Kill Processes by Port

### Port 8000 (Backend)
```bash
lsof -ti :8000 | xargs -r kill -9
```

### Port 8080 (Frontend)
```bash
lsof -ti :8080 | xargs -r kill -9
```

### Port 5432 (Database)
```bash
lsof -ti :5432 | xargs -r kill -9
```

### Find Process on Port (without killing)
```bash
lsof -i :8000
```

---

## Docker Container Management

### Stop All Containers
```bash
docker stop $(docker ps -aq)
```

### Remove All Stopped Containers
```bash
docker rm $(docker ps -aq)
```

### Stop and Remove All
```bash
docker-compose down
docker ps -aq | xargs -r docker stop
docker ps -aq | xargs -r docker rm
```

### View Running Containers
```bash
docker ps
```

### View All Containers (including stopped)
```bash
docker ps -a
```

---

## Database Operations

### Access PostgreSQL CLI
```bash
docker exec -it billings_db psql -U postgres -d billings
```

### Run SQL Query
```bash
docker exec billings_db psql -U postgres -d billings -c "SELECT COUNT(*) FROM users;"
```

### Backup Database
```bash
docker exec billings_db pg_dump -U postgres billings > backup_$(date +%Y%m%d).sql
```

### Restore Database
```bash
docker exec -i billings_db psql -U postgres billings < backup.sql
```

### Reset Database (DESTRUCTIVE!)
```bash
docker-compose down -v  # Deletes all data
docker-compose up -d
docker exec billings_backend alembic upgrade head
docker exec billings_backend python scripts/import_questions.py
docker exec -it billings_backend python scripts/create_admin.py
```

---

## Database Migrations

### Create Migration
```bash
docker exec billings_backend alembic revision --autogenerate -m "Description"
```

### Apply Migrations
```bash
docker exec billings_backend alembic upgrade head
```

### Rollback One Migration
```bash
docker exec billings_backend alembic downgrade -1
```

### View Migration History
```bash
docker exec billings_backend alembic history
```

---

## Running Scripts

### Import Questions
```bash
docker exec billings_backend python scripts/import_questions.py
```

### Create Admin User
```bash
docker exec -it billings_backend python scripts/create_admin.py
```

### Seed Achievements
```bash
docker exec billings_backend python -m app.db.seed_achievements_v2
```

### Seed Avatars
```bash
docker exec billings_backend python -m app.db.seed_avatars_v2
```

### Python Shell
```bash
docker exec -it billings_backend python
```

---

## Testing

### Run All Tests
```bash
docker exec billings_backend pytest
```

### Run Specific Test File
```bash
docker exec billings_backend pytest tests/unit/services/test_quiz_service.py
```

### Run with Coverage
```bash
docker exec billings_backend pytest --cov=app --cov-report=html
```

### Copy Coverage Report
```bash
docker cp billings_backend:/app/htmlcov ./htmlcov
open htmlcov/index.html
```

---

## Code Changes

### Rebuild After Dependency Change
```bash
docker-compose down
docker-compose build backend
docker-compose up -d
```

### Force Rebuild (no cache)
```bash
docker-compose build --no-cache backend
```

---

## Debugging

### Check Environment Variables in Container
```bash
docker exec billings_backend env | grep DATABASE
```

### View Container Logs (last 100 lines)
```bash
docker logs billings_backend --tail 100
```

### Follow Logs Live
```bash
docker logs -f billings_backend
```

### Inspect Container
```bash
docker inspect billings_backend
```

### Execute Bash in Container
```bash
docker exec -it billings_backend bash
```

### List Files in Container
```bash
docker exec billings_backend ls -la /app
```

### Copy File from Container
```bash
docker cp billings_backend:/app/file.txt ./file.txt
```

---

## Cleanup

### Remove Stopped Containers
```bash
docker container prune
```

### Remove Unused Images
```bash
docker image prune
```

### Remove Unused Volumes (CAREFUL!)
```bash
docker volume prune
```

### Remove Everything (NUCLEAR!)
```bash
docker system prune -a --volumes
```

---

## Frontend

### Serve Frontend (Python)
```bash
cd frontend
python3 -m http.server 8080
```

### Serve Frontend (Node - if installed)
```bash
cd frontend
npx http-server -p 8080
```

---

## Useful One-Liners

### Check if Services Are Running
```bash
curl -s http://localhost:8000/docs > /dev/null && echo "Backend: ✅" || echo "Backend: ❌"
```

### Count Questions in Database
```bash
docker exec billings_db psql -U postgres -d billings -c "SELECT exam_type, COUNT(*) FROM questions GROUP BY exam_type;"
```

### Count Users
```bash
docker exec billings_db psql -U postgres -d billings -c "SELECT COUNT(*) FROM users;"
```

### View Recent Logs
```bash
docker-compose logs --tail=50 backend
```

### Restart Everything
```bash
docker-compose down && docker-compose up -d && docker-compose logs -f backend
```

---

## Common Workflows

### Fresh Start (Keep Database)
```bash
cd backend
docker-compose down
docker-compose up -d
```

### Fresh Start (Delete Database)
```bash
cd backend
docker-compose down -v
docker-compose up -d
docker exec billings_backend alembic upgrade head
# Then import questions and create admin
```

### View Specific Service Logs
```bash
docker-compose logs -f backend  # Backend only
docker-compose logs -f db       # Database only
docker-compose logs -f pgadmin  # pgAdmin only
```

### Check Docker Compose Config
```bash
docker-compose config  # See what docker-compose will run
```

---

## Emergency Fixes

### Everything Is Broken
```bash
# Nuclear option - start completely fresh
cd backend
docker-compose down -v
docker system prune -f
docker-compose up -d

# Rebuild database
docker exec billings_backend alembic upgrade head
docker exec billings_backend python scripts/import_questions.py
docker exec -it billings_backend python scripts/create_admin.py
```

### Can't Connect to Database
```bash
# Check containers
docker ps

# Restart database
docker-compose restart db

# Check database logs
docker-compose logs db

# Last resort - restart everything
docker-compose down
docker-compose up -d
```

### Port Conflicts
```bash
# Kill all processes on common ports
lsof -ti :8000 | xargs -r kill -9
lsof -ti :8080 | xargs -r kill -9
lsof -ti :5432 | xargs -r kill -9

# Then restart
docker-compose up -d
```

---

## Quick Links

- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- pgAdmin: http://localhost:5050
- Frontend: http://localhost:8080

---

## Tips

- Always run `docker-compose` commands from `backend/` directory
- Use `-d` flag to run in background (detached mode)
- Use `-f` flag with logs to follow (live updates)
- Check logs first when something breaks: `docker-compose logs backend`
- Never use `docker-compose down -v` unless you want to delete all data
