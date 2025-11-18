# Troubleshooting & Dev Notes

## 🔥 Common Issues

### Browser Issues - USE FIREFOX FOR LOCAL DEV

**Problem:** Weird errors, CORS issues, or things not working in Brave/Chrome

**Solution:** **USE FIREFOX** for local development

**Why:**
- Brave has aggressive privacy/blocking features that interfere with `localhost` development
- Shields, tracker blocking, and fingerprinting protection can block API calls
- Firefox is more dev-friendly for local `localhost:8080` → `localhost:8000` connections

**You've done this twice now - just use Firefox!**

---

## Other Common Issues

### Port Already in Use
**Error:** `Address already in use` on port 8000 or 8080

**Solution:**
```bash
# Find what's using the port
lsof -i :8000
lsof -i :8080

# Kill the process
kill <PID>
```

### CORS Errors
**Error:** `CORS policy: No 'Access-Control-Allow-Origin' header`

**Check:**
1. Backend is running (`http://localhost:8000`)
2. Frontend is at `http://localhost:8080` or `http://127.0.0.1:8080`
3. Using Firefox (not Brave!)

### Database Connection Failed
**Error:** `Connection refused` to PostgreSQL

**Solution:**
```bash
cd ~/proj/billings/backend
docker compose up
```

### Python Module Errors
**Error:** `ModuleNotFoundError` or bytecode cache issues

**Solution:**
```bash
cd ~/proj/billings/backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Quick Start Commands

**Terminal 1 - Database:**
```bash
cd ~/proj/billings/backend
docker compose up
```

**Terminal 2 - Backend:**
```bash
cd ~/proj/billings/backend
source venv/bin/activate
uvicorn app.main:app --reload
```

**Terminal 3 - Frontend:**
```bash
cd ~/proj/billings/frontend
python3 -m http.server 8080
```

**Then open FIREFOX at:** `http://localhost:8080`

---

## Git Issues

### Accidentally Committed Sensitive Files

1. Add to `.gitignore`
2. Remove from tracking: `git rm --cached <file>`
3. Commit: `git commit -m "Remove sensitive files"`
4. Push: `git push`

To remove from history completely, see the "goodnight" commit for reference.

---

**Remember: Firefox for dev, not Brave!** 🦊
