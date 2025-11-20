# How to Run - Quick Reference

After making changes, follow these steps to test:

## 1. Start Backend + Database

```bash
cd ~/Desktop/Projects/morepractice/backend
docker-compose up -d
```

Wait ~10 seconds for services to start.

## 2. Start Frontend

Open a new terminal:

```bash
cd ~/Desktop/Projects/morepractice/frontend
python3 -m http.server 8080
```

## 3. Access Application

- **Frontend**: http://localhost:8080
- **API Docs**: http://localhost:8000/docs
- **pgAdmin**: http://localhost:5050

## 4. View Backend Logs (Optional)

```bash
cd ~/Desktop/Projects/morepractice/backend
docker-compose logs -f backend
```

Press `Ctrl+C` to stop following logs.

## 5. Stop Everything

```bash
# Stop frontend: Ctrl+C in frontend terminal

# Stop backend + database:
cd ~/Desktop/Projects/morepractice/backend
docker-compose down
```

---

## Quick Troubleshooting

**Port conflict?**
```bash
lsof -ti :8000 | xargs -r kill -9  # Kill backend
lsof -ti :8080 | xargs -r kill -9  # Kill frontend
```

**Backend not updating?**
```bash
docker-compose restart backend
```

**Need fresh database?**
```bash
docker-compose down -v  # WARNING: Deletes all data
docker-compose up -d
```
