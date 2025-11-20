# Linux VM Setup Guide

Complete guide to clone and run this project on a Linux VM.

---

## Table of Contents

1. [Understanding Data Persistence](#understanding-data-persistence)
   - [How Data Works](#how-data-works)
   - [What You'll Lose When Cloning](#what-youll-lose-when-cloning)
2. [Migration Options](#migration-options)
   - [Option 1: Start Fresh (Recommended)](#option-1-start-fresh-recommended)
   - [Option 2: Backup & Restore](#option-2-backup--restore)
3. [What to Backup](#what-to-backup)
4. [Prerequisites on Linux VM](#prerequisites-on-linux-vm)
5. [Setup Steps (Fresh Start)](#setup-steps-fresh-start)
6. [Email Configuration](#email-configuration)
7. [Importing Question Data](#importing-question-data)
8. [Creating Admin User](#creating-admin-user)
9. [Seeding Initial Data](#seeding-initial-data)
10. [Running the Application](#running-the-application)
11. [Testing](#testing)
12. [Daily Startup Routine](#daily-startup-routine)
13. [Stopping Services](#stopping-services)
14. [Troubleshooting](#troubleshooting)
15. [Quick Reference](#quick-reference)

---

## Understanding Data Persistence

### How Data Works

This is important to understand before migrating:

**CSV Files → Database (One-Time Import)**
```
CSV files (backend/data/COMPTIA/*.csv)
    ↓
    ↓ python scripts/import_questions.py (run ONCE)
    ↓
PostgreSQL Database (lives in Docker volume)
```

**Key Points:**
- CSV files are only for **importing** questions into the database
- Once imported, questions live in **PostgreSQL**, not CSV files
- Users, quiz attempts, achievements, etc. are **only** in PostgreSQL
- PostgreSQL data is stored in a **Docker volume**: `billings_db_data`

**Docker Volume Persistence:**
```bash
docker-compose down        # ✅ Data survives (volume persists)
docker-compose down -v     # ❌ DESTROYS all data (removes volume)
```

### What You'll Lose When Cloning

When you clone the repo fresh on your VM:

| What | In Git? | After Clone |
|------|---------|-------------|
| Code (Python, HTML, JS) | ✅ Yes | ✅ You have it |
| Database migrations | ✅ Yes | ✅ You have it |
| Seed scripts | ✅ Yes | ✅ You have it |
| `.env` file | ❌ No | ❌ Must recreate |
| CSV question files | ❌ No | ❌ Must download from Google Sheets |
| Database data | ❌ No | ❌ Database is empty |
| - Questions | ❌ No | ❌ Re-import from CSV |
| - Users | ❌ No | ❌ Create new users |
| - Quiz attempts | ❌ No | ❌ Gone (start fresh) |
| - Achievements earned | ❌ No | ❌ Gone (start fresh) |
| Virtual environment | ❌ No | ❌ Recreate with pip |

---

## Migration Options

### Option 1: Start Fresh (Recommended)

**Pros:**
- Simple and clean
- No database compatibility issues
- Good for learning/development

**Cons:**
- Lose all existing users and quiz data
- Need to re-import questions from CSV
- Need to recreate admin users

**Steps:**
1. Clone repo
2. Setup `.env` with email credentials
3. Run migrations to create empty database
4. Import questions from CSV files
5. Create admin user
6. Seed achievements/avatars

**This guide assumes Option 1.**

### Option 2: Backup & Restore

**Pros:**
- Keeps all users, quiz data, progress
- No need to re-import questions

**Cons:**
- More complex
- Need to transfer large SQL file
- Potential version conflicts

**Steps (if you want this):**
```bash
# BEFORE leaving current machine:
cd ~/proj/billings/backend
docker exec billings_db pg_dump -U postgres billings > billings_backup.sql

# Transfer billings_backup.sql to VM

# ON VM after migrations:
docker exec -i billings_db psql -U postgres billings < billings_backup.sql
```

---

## What to Backup

### CRITICAL: Must Backup

**1. Email Credentials (from `.env`)**
```env
SMTP_USERNAME=boetigsolutions@gmail.com
SMTP_PASSWORD=fcim skhy dqxi xspk    # ← Google App Password
FROM_EMAIL=boetigsolutions@billings.com
FROM_NAME=BoetigStudySite
```

**This is the MOST ANNOYING thing to lose!** Save these somewhere safe.

### Optional: Recommended Backups

**2. Full `.env` File**
- Contains JWT secret (can regenerate)
- Contains all config (easier to copy than recreate)

**3. CSV Files (if not in Google Sheets)**
- You said you have them in Google Sheets, so you're good
- Otherwise backup `backend/data/COMPTIA/*.csv`

**4. Database Backup (if using Option 2)**
- Only if you want to preserve users/data
- See Option 2 above

### Don't Backup (Recreated Automatically)

- ❌ `venv/` - Huge, recreated with `pip install`
- ❌ `__pycache__/` - Generated Python cache
- ❌ `node_modules/` - If you had any
- ❌ `logs/` - Log files
- ❌ `htmlcov/` - Test coverage reports

---

## Prerequisites on Linux VM

### 1. Update System
```bash
sudo apt update
sudo apt upgrade -y
```

### 2. Install Python 3.12+
```bash
sudo apt install python3 python3-pip python3-venv -y
python3 --version  # Should show 3.12+
```

### 3. Install Git
```bash
sudo apt install git -y
git --version
```

### 4. Install Docker & Docker Compose
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add your user to docker group (so you don't need sudo)
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt install docker-compose -y

# IMPORTANT: Log out and back in for group changes to take effect
# Or run this to activate immediately:
newgrp docker

# Verify
docker --version
docker-compose --version
```

---

## Setup Steps (Fresh Start)

### 1. Clone Repository
```bash
cd ~
git clone https://github.com/YOUR-USERNAME/billings.git
cd billings
```

**Replace `YOUR-USERNAME` with your actual GitHub username!**

### 2. Create .env File
```bash
cp .env.example .env
```

### 3. Generate JWT Secret
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the output (something like: `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6`)

### 4. Edit .env File
```bash
nano .env  # or vim/vi if you prefer
```

Update these values:

```env
# Database (defaults are fine for development)
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/billings

# JWT Secret - PASTE THE VALUE YOU GENERATED
JWT_SECRET=PASTE_YOUR_GENERATED_SECRET_HERE

# JWT Expiration (default is fine)
JWT_EXPIRATION_MINUTES=15

# Docker Postgres (defaults are fine)
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=billings

# pgAdmin (defaults are fine)
PGADMIN_DEFAULT_EMAIL=admin@admin.com
PGADMIN_DEFAULT_PASSWORD=admin

# Email - USE YOUR SAVED VALUES!
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=boetigsolutions@gmail.com
SMTP_PASSWORD=fcim skhy dqxi xspk
FROM_EMAIL=boetigsolutions@billings.com
FROM_NAME=BoetigStudySite
FRONTEND_URL=http://localhost:8080
```

**Save and exit** (Ctrl+O, Enter, Ctrl+X in nano)

### 5. Start Database with Docker
```bash
cd backend
docker-compose up -d
```

**Verify containers are running:**
```bash
docker ps
```

You should see:
- `billings_db` (PostgreSQL on port 5432)
- `billings_pgadmin` (pgAdmin on port 5050)

### 6. Setup Python Virtual Environment
```bash
# Still in backend/ directory
python3 -m venv venv
source venv/bin/activate
```

Your prompt should show `(venv)`.

### 7. Install Python Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This installs FastAPI, SQLAlchemy, Alembic, pytest, and ~30 other dependencies.

### 8. Run Database Migrations
```bash
alembic upgrade head
```

This creates all database tables (users, questions, quizzes, achievements, etc.).

You should see output like:
```
INFO  [alembic.runtime.migration] Running upgrade -> xxx, initial
INFO  [alembic.runtime.migration] Running upgrade xxx -> yyy, add users
...
```

**Your database now has tables but is EMPTY (no data).**

---

## Email Configuration

### Understanding Email Settings

Your app sends emails for:
- User email verification
- Password reset requests
- Admin notifications (potentially)

### Google App Password Setup

You're using **Gmail SMTP** with an **App Password**.

**Your saved credentials:**
```env
SMTP_USERNAME=boetigsolutions@gmail.com
SMTP_PASSWORD=fcim skhy dqxi xspk    # This is a Google App Password
```

### If You Need to Regenerate App Password

If you lose the password or need a new one:

1. Go to your Google Account: https://myaccount.google.com/
2. Enable **2-Factor Authentication** (required for App Passwords)
3. Go to **App Passwords**: https://myaccount.google.com/apppasswords
4. Generate new password for "Mail" / "Other (Custom name)"
5. Copy the 16-character password (format: `xxxx xxxx xxxx xxxx`)
6. Update `SMTP_PASSWORD` in `.env`

### Testing Email

To test if email is working:
1. Start the app (see [Running the Application](#running-the-application))
2. Sign up for a new account
3. Check if you receive verification email
4. Check backend logs for errors

---

## Importing Question Data

Your database is empty. Let's load questions from CSV files.

### 1. Get CSV Files from Google Sheets

Download these 4 files from your Google Sheets:
- `a1101.csv`
- `a1102.csv`
- `network.csv`
- `security.csv`

### 2. Create Data Directory
```bash
# In backend/ directory
mkdir -p data/COMPTIA
```

### 3. Copy CSV Files
```bash
# Copy downloaded files to data directory
# Adjust path based on where you downloaded them
cp ~/Downloads/a1101.csv data/COMPTIA/
cp ~/Downloads/a1102.csv data/COMPTIA/
cp ~/Downloads/network.csv data/COMPTIA/
cp ~/Downloads/security.csv data/COMPTIA/
```

### 4. Verify Files
```bash
ls -lh data/COMPTIA/
```

Should show 4 CSV files (hundreds of KB each).

### 5. Import Questions into Database
```bash
# Make sure venv is activated
source venv/bin/activate

# Run import script
python scripts/import_questions.py
```

You should see:
```
📥 Importing security.csv as exam_type=security ...
✅ Finished importing security.csv.

📥 Importing network.csv as exam_type=network ...
✅ Finished importing network.csv.

📥 Importing a1101.csv as exam_type=a1101 ...
✅ Finished importing a1101.csv.

📥 Importing a1102.csv as exam_type=a1102 ...
✅ Finished importing a1102.csv.

🎉 All CSV files imported successfully!
```

**CSV files are now in PostgreSQL!** You can delete the CSVs if you want (keep them backed up in Google Sheets).

---

## Creating Admin User

You need an admin user to access admin features.

### Run Admin Creation Script
```bash
# In backend/ with venv activated
python scripts/create_admin.py
```

**Follow the prompts:**
```
Choose an option:
  1. Make an existing user admin
  2. Create a new admin user

Enter choice (1 or 2): 2

📝 Create New Admin User
Username: admin
Email: admin@example.com
Password: YourSecurePassword123

✅ Admin user created successfully!
```

**Save these credentials!** You'll use them to log in.

---

## Seeding Initial Data

Seed achievements and avatars (gamification features).

### 1. Seed Achievements
```bash
# In backend/ with venv activated
python -c "from app.db.seed_achievements_v2 import seed_achievements; from app.db.session import SessionLocal; db = SessionLocal(); seed_achievements(db); db.close(); print('✅ Achievements seeded!')"
```

### 2. Seed Avatars
```bash
python -c "from app.db.seed_avatars_v2 import seed_avatars; from app.db.session import SessionLocal; db = SessionLocal(); seed_avatars(db); db.close(); print('✅ Avatars seeded!')"
```

**Your database is now fully populated!**

---

## Running the Application

### Terminal 1: Backend API
```bash
cd ~/billings/backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Application startup complete.
```

### Terminal 2: Frontend
```bash
cd ~/billings/frontend
python3 -m http.server 8080
```

You should see:
```
Serving HTTP on 0.0.0.0 port 8080 (http://0.0.0.0:8080/) ...
```

### Access Points
- **Frontend:** http://localhost:8080
- **Backend API:** http://localhost:8000
- **API Docs (Swagger):** http://localhost:8000/docs
- **pgAdmin:** http://localhost:5050

### Test It Out
1. Open http://localhost:8080
2. Sign up for a new account
3. Check email for verification link
4. Log in with admin credentials you created
5. Try taking a quiz!

---

## Testing

### Run Tests
```bash
cd ~/billings/backend
source venv/bin/activate
pytest
```

### With Coverage
```bash
pytest --cov=app --cov-report=html
```

View coverage report:
```bash
firefox htmlcov/index.html  # or your browser
```

---

## Daily Startup Routine

Once everything is set up, this is your daily workflow:

```bash
# Terminal 1: Start database (if not running)
cd ~/billings/backend
docker-compose up -d

# Start backend
source venv/bin/activate
uvicorn app.main:app --reload

# Terminal 2: Start frontend
cd ~/billings/frontend
python3 -m http.server 8080
```

**That's it!** Everything else persists in the Docker volume.

---

## Stopping Services

### Stop Backend/Frontend
Press **Ctrl+C** in their respective terminals.

### Stop Database
```bash
cd ~/billings/backend
docker-compose down
```

**WARNING:** Don't use `-v` flag unless you want to **destroy all data**:
```bash
docker-compose down -v   # ⚠️ DESTROYS DATABASE!
```

---

## Troubleshooting

### Docker Permission Denied
```
Got permission denied while trying to connect to the Docker daemon socket
```

**Solution:**
```bash
sudo usermod -aG docker $USER
newgrp docker  # or log out and back in
```

### Port Already in Use
```
Error: Port 5432 is already allocated
```

**Solution:**
```bash
# Find process using port
sudo lsof -i :5432
# Kill it
sudo kill -9 <PID>
```

### Database Connection Failed
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solution:**
```bash
# Check containers are running
docker ps

# Check logs
cd ~/billings/backend
docker-compose logs db

# Restart
docker-compose down
docker-compose up -d
```

### Module Not Found
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution:**
```bash
# Make sure venv is activated (you should see (venv) in prompt)
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Missing .env File
```
ERROR: Missing required environment variables!
Missing variables: DATABASE_URL, JWT_SECRET
```

**Solution:**
```bash
# Copy example and edit it
cp .env.example .env
nano .env  # Add your values
```

### Email Not Sending
Check backend logs for errors. Common issues:
- Wrong SMTP password (App Password, not regular password)
- 2FA not enabled on Google account
- App Passwords not enabled

### CSV Import Fails
```
FileNotFoundError: data/COMPTIA/a1101.csv
```

**Solution:**
- Download CSVs from Google Sheets
- Place in `backend/data/COMPTIA/`
- Verify with: `ls -la data/COMPTIA/`

---

## Quick Reference

### Setup Checklist
- [ ] Clone repo from GitHub
- [ ] Create `.env` from `.env.example`
- [ ] Add email credentials to `.env`
- [ ] Generate and add JWT_SECRET
- [ ] Start Docker containers
- [ ] Create Python venv
- [ ] Install dependencies
- [ ] Run migrations
- [ ] Download CSV files from Google Sheets
- [ ] Import questions from CSV
- [ ] Create admin user
- [ ] Seed achievements and avatars
- [ ] Start backend and frontend
- [ ] Test by signing up/logging in

### Important Commands
```bash
# Activate virtual environment
source venv/bin/activate

# Start database
docker-compose up -d

# Run migrations
alembic upgrade head

# Import questions
python scripts/import_questions.py

# Create admin
python scripts/create_admin.py

# Start backend
uvicorn app.main:app --reload

# Start frontend (different terminal)
python3 -m http.server 8080

# Run tests
pytest

# View Docker logs
docker-compose logs -f
```

### File Locations
```
billings/
├── .env                           # Environment config (create from .env.example)
├── backend/
│   ├── venv/                      # Python virtual environment (create it)
│   ├── data/COMPTIA/*.csv         # Question CSVs (download from Google Sheets)
│   ├── requirements.txt           # Python dependencies
│   ├── alembic/                   # Database migrations
│   ├── app/                       # Application code
│   ├── scripts/                   # Utility scripts
│   └── docker-compose.yml         # Database containers
└── frontend/                      # HTML/CSS/JS files
```

---

## Summary

**What you need to save before switching:**
- ✅ Email credentials from `.env` (Google App Password)
- ✅ CSV files are in Google Sheets (you're good!)

**On VM setup:**
1. Install prerequisites (Python, Docker, Git)
2. Clone repo
3. Create `.env` with saved email credentials
4. Start database, create venv, install deps
5. Run migrations
6. Download CSVs from Google Sheets and import
7. Create admin user
8. Seed achievements/avatars
9. Start app and test!

**You're starting fresh, so:**
- No old users (create new ones)
- No old quiz data (start fresh)
- Questions re-imported from CSV
- Clean slate for development!

---

Good luck with your setup! 🚀
