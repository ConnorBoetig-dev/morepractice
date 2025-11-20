# Billings Study Platform

CompTIA exam preparation platform with gamification features.

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Git

### Setup (5 minutes)

```bash
# 1. Clone repository
git clone <your-repo-url>
cd morepractice

# 2. Create .env file
cp .env.example .env
# Edit .env - add your email credentials and JWT secret

# 3. Start everything with Docker
cd backend
docker-compose up -d

# 4. Import questions (one-time)
# Place CSV files in backend/questions/
# Then run:
docker exec billings_backend python scripts/import_questions.py

# 5. Create admin user (one-time)
docker exec -it billings_backend python scripts/create_admin.py
```

### Access Points

- **Frontend**: http://localhost:8080 (serve frontend/index.html)
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **pgAdmin**: http://localhost:5050

### Daily Workflow

```bash
# Start all services
cd backend
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop all services
docker-compose down
```

## Project Structure

```
morepractice/
├── backend/
│   ├── app/              # FastAPI application
│   ├── questions/        # CSV question files (gitignored)
│   ├── Dockerfile        # Backend container definition
│   ├── docker-compose.yml # Orchestrates all services
│   └── .env              # Environment variables (gitignored)
├── frontend/             # HTML/CSS/JS static files
└── README.md             # This file
```

## Documentation

- **[DEVELOPMENT.md](./DEVELOPMENT.md)** - Full developer guide, workflows, debugging
- **[COMMANDS.md](./COMMANDS.md)** - Quick reference for common commands
- **[.claude/](./.claude/)** - Detailed architecture docs for Claude Code

## Tech Stack

- **Backend**: Python 3.12, FastAPI, SQLAlchemy, PostgreSQL
- **Frontend**: Vanilla JS, HTML, CSS
- **Infrastructure**: Docker, Docker Compose
- **Testing**: pytest

## Environment Variables

Key variables in `.env`:

```env
# Database (Docker uses 'db' hostname)
DATABASE_URL=postgresql://postgres:postgres@db:5432/billings

# JWT Secret (generate with: python -c "import secrets; print(secrets.token_urlsafe(32))")
JWT_SECRET=your-secret-here

# Email (for verification emails)
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

## Common Issues

### Port already in use
```bash
# Find and kill process
lsof -i :8000
kill -9 <PID>
```

### Database connection failed
```bash
# Restart database
docker-compose restart db
```

### Need fresh start
```bash
# WARNING: Deletes all data
docker-compose down -v
docker-compose up -d
```

## Contributing

1. Create feature branch
2. Make changes
3. Run tests: `docker exec billings_backend pytest`
4. Create pull request

## License

Private - Internal use only
