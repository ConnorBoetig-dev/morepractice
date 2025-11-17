# Billings - Startup Guide

Simple guide to start the full-stack application.

## Prerequisites

- Docker installed (for PostgreSQL)
- Python 3.12 with venv created
- All dependencies installed

---

## 🚀 Quick Start (3 Terminals)

### Terminal 1️⃣: Database (PostgreSQL)

```bash
cd ~/proj/billings/backend
docker compose up
```

**What you should see:**
```
billings_db  | database system is ready to accept connections
billings_pgadmin  | Listening at: http://[::]:80
```

**Leave this running!** Don't close this terminal.

---

### Terminal 2️⃣: Backend (FastAPI)

```bash
cd ~/proj/billings/backend
source venv/bin/activate
uvicorn app.main:app --reload
```

**What you should see:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using StatReload
INFO:     Application startup complete.
```

**Leave this running!** Don't close this terminal.

---

### Terminal 3️⃣: Frontend (HTML/JS)

```bash
cd ~/proj/billings/frontend
python3 -m http.server 8080
```

**What you should see:**
```
Serving HTTP on 0.0.0.0 port 8080 (http://0.0.0.0:8080/) ...
```

**Leave this running!** Don't close this terminal.

---

## 🌐 Access the Application

Open your browser and visit:
- **Frontend**: http://localhost:8080 or http://127.0.0.1:8080
- **Backend API Docs**: http://localhost:8000/docs
- **pgAdmin (Database UI)**: http://localhost:5050

---

## 📋 Full Setup (First Time Only)

If you're setting up for the first time or after a fresh clone:

### 1. Create Virtual Environment

```bash
cd ~/proj/billings/backend
python3 -m venv venv
```

### 2. Activate Virtual Environment

```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Verify .env File Exists

```bash
ls -la .env
```

Should show the `.env` file. If not, copy from `.env.example`:

```bash
cp .env.example .env
```

### 5. Start Docker Database

```bash
docker compose up -d
```

The `-d` flag runs it in the background (detached mode).

### 6. Start Backend

```bash
uvicorn app.main:app --reload
```

### 7. Start Frontend (New Terminal)

```bash
cd ~/proj/billings/frontend
python3 -m http.server 8080
```

---

## 🛑 Shutdown

### Stop All Services

1. **Frontend**: Press `Ctrl+C` in Terminal 3
2. **Backend**: Press `Ctrl+C` in Terminal 2
3. **Database**: Press `Ctrl+C` in Terminal 1 (or `docker compose down`)

### Stop Database Only (Background)

```bash
cd ~/proj/billings/backend
docker compose down
```

---

## ✅ Health Checks

### Check if Backend is Running

```bash
curl http://localhost:8000/docs
```

Should return HTML (the API docs page).

### Check if Database is Running

```bash
docker ps
```

Should show:
- `billings_db` (PostgreSQL)
- `billings_pgadmin` (pgAdmin)

### Check if Frontend is Serving

```bash
curl http://localhost:8080
```

Should return HTML from index.html.

---

## 🐛 Troubleshooting

### "Address already in use" (Port 8000)

**Problem:** Another process is using port 8000

**Solution:**
```bash
# Find what's using port 8000
lsof -i :8000

# Kill the process (replace PID with actual process ID)
kill <PID>
```

### "Cannot connect to server" (Frontend → Backend)

**Problem:** Backend not running or CORS issue

**Solutions:**
1. Make sure backend is running (`uvicorn app.main:app --reload`)
2. Check browser console for CORS errors
3. Access frontend via `http://localhost:8080` or `http://127.0.0.1:8080` (both are allowed)

### "Connection refused" (Backend → Database)

**Problem:** PostgreSQL not running

**Solution:**
```bash
cd ~/proj/billings/backend
docker compose up -d
```

### Database Tables Not Created

**Problem:** SQLAlchemy hasn't created tables yet

**Solution:** Restart backend - tables are created on startup:
```bash
# Press Ctrl+C
uvicorn app.main:app --reload
```

---

## 📁 Project Structure Reminder

```
billings/
├── backend/
│   ├── app/                    # FastAPI application code
│   ├── venv/                   # Virtual environment (activate this!)
│   ├── requirements.txt        # Python dependencies
│   ├── .env                    # Environment variables (JWT secret, DB URL)
│   └── docker-compose.yml      # PostgreSQL + pgAdmin containers
├── frontend/
│   ├── index.html              # Landing page
│   ├── signup.html             # Registration page
│   ├── login.html              # Login page
│   ├── dashboard.html          # Protected dashboard
│   ├── css/                    # Styles
│   └── js/                     # JavaScript modules
└── STARTUP.md                  # This file!
```

---

## 🎯 Common Workflow

### Starting Work
```bash
# Terminal 1: Database
cd ~/proj/billings/backend && docker compose up

# Terminal 2: Backend
cd ~/proj/billings/backend && source venv/bin/activate && uvicorn app.main:app --reload

# Terminal 3: Frontend
cd ~/proj/billings/frontend && python3 -m http.server 8080
```

### Making Backend Changes
- Edit Python files in `backend/app/`
- Uvicorn auto-reloads (with `--reload` flag)
- Check terminal for errors

### Making Frontend Changes
- Edit HTML/CSS/JS files in `frontend/`
- Refresh browser to see changes
- Check browser console (F12) for errors

### Stopping Work
- Press `Ctrl+C` in all 3 terminals
- Or use `docker compose down` for database

---

## 🎓 What Each Service Does

| Service | Port | Purpose |
|---------|------|---------|
| **PostgreSQL** | 5432 | Database - stores users and data |
| **pgAdmin** | 5050 | Web UI to view/manage database |
| **FastAPI** | 8000 | Backend API - handles business logic |
| **Frontend** | 8080 | Serves HTML/CSS/JS to browser |

**Request Flow:**
```
Browser (port 8080)
    ↓ HTTP requests
FastAPI (port 8000)
    ↓ SQL queries
PostgreSQL (port 5432)
```

---

## 💾 Database Access

### Via pgAdmin (Web UI)
1. Visit http://localhost:5050
2. Login: `admin@admin.com` / `admin`
3. Add server:
   - Host: `db` (Docker network name)
   - Port: `5432`
   - Database: `billings`
   - Username: `postgres`
   - Password: `postgres`

### Via Command Line
```bash
docker exec -it billings_db psql -U postgres -d billings
```

Then run SQL:
```sql
\dt                          -- List tables
SELECT * FROM users;         -- View all users
SELECT * FROM user_profiles; -- View user profiles
\q                           -- Quit
```

---

## 🔄 Restart Everything Fresh

If you want to completely restart:

```bash
# Stop everything
docker compose down
# Press Ctrl+C in backend terminal
# Press Ctrl+C in frontend terminal

# Start again
docker compose up -d
uvicorn app.main:app --reload
python3 -m http.server 8080
```

---

**You're all set! Open http://localhost:8080 and start coding!** 🚀
