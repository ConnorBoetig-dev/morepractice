# Production Deployment Guide

**Quick checklist for deploying the Billings Study Platform to production.**

---

## Critical Security Requirements ⚠️

### 1. HTTPS/SSL Certificate
**Status**: ❌ REQUIRED (not configured by default)

Production MUST use HTTPS. Without it, JWT tokens and passwords are sent in plain text.

**Options:**
- **Let's Encrypt** (Free, auto-renewing)
  ```bash
  sudo apt install certbot python3-certbot-nginx
  sudo certbot --nginx -d yourdomain.com
  ```
- **Cloudflare** (Free SSL proxy + DDoS protection)
- **AWS Certificate Manager** (Free with AWS services)

**Verification:**
```bash
curl -I https://yourdomain.com | grep "HTTP/2 200"
```

---

### 2. Environment Variables
**Status**: ⚠️ MUST UPDATE

Never use development secrets in production.

**Required Changes:**

```bash
# .env file (NEVER commit to git)

# 1. Generate STRONG JWT secret (32+ characters)
JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

# 2. Production database (NOT Docker)
DATABASE_URL=postgresql://user:password@production-db.example.com:5432/billings

# 3. Production domain
FRONTEND_URL=https://yourdomain.com

# 4. Production email (use real SMTP)
SMTP_USERNAME=noreply@yourdomain.com
SMTP_PASSWORD=your_production_email_password
SMTP_SERVER=smtp.gmail.com  # Or your email provider
SMTP_PORT=587

# 5. Enable security features
DEBUG=false
ENABLE_HSTS=true
```

**Security Check:**
```python
# Verify JWT secret strength
python3 -c "import os; secret=os.getenv('JWT_SECRET'); print('✓ Strong' if len(secret) >= 32 else '✗ TOO WEAK')"
```

---

### 3. Database Security
**Status**: ⚠️ MUST CONFIGURE

**Production Database Checklist:**
- [ ] Use managed database (AWS RDS, Google Cloud SQL, DigitalOcean)
- [ ] Enable SSL/TLS connections
- [ ] Set up automated daily backups
- [ ] Enable point-in-time recovery
- [ ] Restrict database access by IP (only allow app server)
- [ ] Use strong passwords (30+ random characters)

**PostgreSQL SSL Connection:**
```python
# Update DATABASE_URL to require SSL
DATABASE_URL=postgresql://user:pass@host:5432/billings?sslmode=require
```

**Database User Permissions** (least privilege):
```sql
-- Create limited user (not postgres superuser)
CREATE USER billings_app WITH PASSWORD 'strong_random_password_here';
GRANT CONNECT ON DATABASE billings TO billings_app;
GRANT USAGE ON SCHEMA public TO billings_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO billings_app;
```

---

### 4. CORS Configuration
**Status**: ✅ Configured (update for production)

Update `backend/app/main.py` with your production domain:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://yourdomain.com",  # Production domain
        "https://www.yourdomain.com",  # www subdomain
        # Remove localhost entries for production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Application Deployment

### Option A: Docker (Recommended)

```bash
# 1. Build production image
cd backend
docker build -t billings-backend:prod .

# 2. Run with production .env
docker run -d \
  --name billings_backend \
  -p 8000:8000 \
  --env-file .env \
  --restart unless-stopped \
  billings-backend:prod

# 3. Verify running
docker logs billings_backend
curl http://localhost:8000/docs
```

**Docker Compose (Production)**:
```yaml
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    restart: unless-stopped
    depends_on:
      - db
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/docs"]
      interval: 30s
      timeout: 10s
      retries: 3

  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: billings
    restart: unless-stopped

volumes:
  postgres_data:
```

---

### Option B: systemd Service (No Docker)

```ini
# /etc/systemd/system/billings.service
[Unit]
Description=Billings Study Platform Backend
After=network.target

[Service]
Type=simple
User=billings
WorkingDirectory=/opt/billings/backend
Environment=PATH=/opt/billings/venv/bin
EnvironmentFile=/opt/billings/.env
ExecStart=/opt/billings/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable billings
sudo systemctl start billings
sudo systemctl status billings
```

---

### Option C: Cloud Platforms

**Heroku**:
```bash
heroku create billings-study-platform
heroku addons:create heroku-postgresql:hobby-dev
heroku config:set JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
git push heroku main
```

**Railway / Render / Fly.io**:
- Connect GitHub repo
- Set environment variables in dashboard
- Deploy with one click

---

## Nginx Reverse Proxy (Recommended)

**Why:** Handle SSL termination, rate limiting, static files

```nginx
# /etc/nginx/sites-available/billings
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Frontend (static files)
    location / {
        root /var/www/billings/frontend;
        try_files $uri $uri/ /index.html;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/billings /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## Database Migrations

**Before deploying code changes:**

```bash
# Run migrations in production
docker exec billings_backend alembic upgrade head

# Or if not using Docker:
cd /opt/billings/backend
source venv/bin/activate
alembic upgrade head
```

**Rollback if needed:**
```bash
alembic downgrade -1  # Go back one migration
```

---

## Monitoring & Logging

### Application Logs

```bash
# Docker logs
docker logs -f billings_backend

# systemd logs
sudo journalctl -u billings -f

# Save to file
docker logs billings_backend > /var/log/billings/app.log 2>&1
```

### Health Check Endpoint

**Endpoint**: `GET /health`

The application includes a production-ready health check endpoint for monitoring.

**Response (Healthy)**:
```json
{
    "status": "healthy",
    "timestamp": "2025-11-20T23:12:00.905742",
    "version": "1.0.0",
    "database": "connected"
}
```

**Response (Unhealthy)**:
```json
{
    "status": "unhealthy",
    "timestamp": "2025-11-20T23:12:00.905742",
    "database": "disconnected",
    "error": "Database connection failed",
    "version": "1.0.0"
}
```

**Status Codes**:
- `200 OK` - Service is healthy
- `503 Service Unavailable` - Database or critical dependency failed

**Usage Examples**:

```bash
# Simple health check
curl https://yourdomain.com/health

# Check with status code
curl -f https://yourdomain.com/health && echo "✅ Healthy" || echo "❌ Unhealthy"

# CI/CD deployment verification
if curl -f https://yourdomain.com/health; then
    echo "✅ Deployment successful"
else
    echo "❌ Deployment failed - rolling back"
    exit 1
fi
```

**Monitoring Services Integration**:

**UptimeRobot** (Free):
```
Monitor Type: HTTP(s)
URL: https://yourdomain.com/health
Keyword: "healthy"
Check Interval: 5 minutes
Alert Contacts: Your email/SMS
```

**Pingdom**:
```
Check Type: HTTP Check
URL: https://yourdomain.com/health
Response Time Threshold: 1000ms
Expected Response: HTTP 200
Alert When: Status code != 200
```

**AWS Application Load Balancer**:
```yaml
HealthCheck:
  Path: /health
  Protocol: HTTP
  Port: 8000
  HealthyThresholdCount: 2
  UnhealthyThresholdCount: 3
  Timeout: 5
  Interval: 30
```

**Nginx Upstream Health Check**:
```nginx
upstream backend {
    server backend1:8000 max_fails=3 fail_timeout=30s;
    server backend2:8000 max_fails=3 fail_timeout=30s;
}

location /health {
    proxy_pass http://backend;
    access_log off;  # Don't log health checks
}
```

**Kubernetes Liveness/Readiness Probes**:
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 2
```

**Docker Compose Health Check**:
```yaml
services:
  backend:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

### Monitoring (Optional but Recommended)

**Sentry** (Error Tracking):
```python
# Add to backend/app/main.py
import sentry_sdk
sentry_sdk.init(
    dsn="your-sentry-dsn",
    traces_sample_rate=0.1,
    environment="production"
)
```

**Uptime Monitoring** (Free):
- UptimeRobot: https://uptimerobot.com
- Pingdom: https://www.pingdom.com
- StatusCake: https://www.statuscake.com

---

## Backup Strategy

### Database Backups

**Automated Daily Backup** (cron job):
```bash
# /etc/cron.daily/backup-billings-db
#!/bin/bash
BACKUP_DIR="/backups/billings"
DATE=$(date +%Y%m%d)
docker exec billings_db pg_dump -U postgres billings | gzip > "$BACKUP_DIR/billings-$DATE.sql.gz"

# Keep last 30 days
find $BACKUP_DIR -name "billings-*.sql.gz" -mtime +30 -delete
```

**Manual Backup:**
```bash
docker exec billings_db pg_dump -U postgres billings > backup-$(date +%Y%m%d).sql
```

**Restore from Backup:**
```bash
docker exec -i billings_db psql -U postgres billings < backup-20250120.sql
```

---

## Security Hardening

### Firewall Rules

```bash
# Only allow HTTP/HTTPS and SSH
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP (redirects to HTTPS)
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable

# Block direct access to backend port
sudo ufw deny 8000/tcp
```

### Rate Limiting (Application Level)
✅ Already configured in your app (5 login attempts per minute)

### Rate Limiting (Nginx Level)
```nginx
# Add to nginx config
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

location /api {
    limit_req zone=api_limit burst=20 nodelay;
    proxy_pass http://localhost:8000;
}
```

### Fail2Ban (Block Brute Force)
```bash
sudo apt install fail2ban

# Create filter for auth failures
sudo nano /etc/fail2ban/filter.d/billings.conf
```

---

## Testing in Production

### Smoke Test Checklist

After deployment, verify these endpoints:

```bash
# 1. Health check
curl https://yourdomain.com/docs
# Expected: 200 OK, Swagger UI loads

# 2. Signup
curl -X POST https://yourdomain.com/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","username":"testuser","password":"Test@Pass9word!"}'
# Expected: 200 OK, returns access_token

# 3. Login
curl -X POST https://yourdomain.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"Test@Pass9word!"}'
# Expected: 200 OK, returns access_token

# 4. Protected endpoint
curl https://yourdomain.com/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
# Expected: 200 OK, returns user info
```

---

## Performance Optimization

### Database Connection Pooling
✅ Already configured (SQLAlchemy default: 5 connections)

Increase for high traffic:
```python
# backend/app/db/session.py
engine = create_engine(
    DATABASE_URL,
    pool_size=20,        # Max connections
    max_overflow=40,     # Additional connections when needed
    pool_pre_ping=True   # Check connection health
)
```

### Gunicorn (Multiple Workers)

Replace `uvicorn` with `gunicorn` for production:

```bash
# Install
pip install gunicorn

# Run with 4 workers (2 x CPU cores)
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile /var/log/billings/access.log \
  --error-logfile /var/log/billings/error.log
```

**Update Dockerfile:**
```dockerfile
CMD ["gunicorn", "app.main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

---

## Troubleshooting

### Database Connection Issues
```bash
# Test connection from app server
psql "postgresql://user:pass@db-host:5432/billings"

# Check if database allows remote connections
# Edit postgresql.conf: listen_addresses = '*'
# Edit pg_hba.conf: host all all 0.0.0.0/0 md5
```

### 502 Bad Gateway (Nginx)
```bash
# Check if backend is running
curl http://localhost:8000/docs

# Check nginx error logs
sudo tail -f /var/log/nginx/error.log
```

### High Memory Usage
```bash
# Check memory
free -h
docker stats billings_backend

# Restart if needed
docker restart billings_backend
```

---

## Final Production Checklist

- [ ] HTTPS enabled (Let's Encrypt or Cloudflare)
- [ ] Strong JWT_SECRET set (32+ chars)
- [ ] Production DATABASE_URL configured
- [ ] Database backups running daily
- [ ] DEBUG=false in .env
- [ ] CORS updated for production domain
- [ ] Firewall rules configured
- [ ] Nginx reverse proxy setup
- [ ] Application logs configured
- [ ] Health monitoring setup (UptimeRobot, etc.)
- [ ] Test signup, login, protected endpoints
- [ ] Verify email sending works
- [ ] Password reset flow tested
- [ ] Rate limiting confirmed working

---

## Quick Deploy Commands

```bash
# 1. Clone repo on server
git clone https://github.com/yourusername/morepractice.git
cd morepractice/backend

# 2. Create production .env
cp .env.example .env
nano .env  # Edit with production values

# 3. Start services
docker-compose -f docker-compose.prod.yml up -d

# 4. Run migrations
docker exec billings_backend alembic upgrade head

# 5. Import questions
docker exec billings_backend python scripts/import_questions.py

# 6. Create admin
docker exec -it billings_backend python scripts/create_admin.py

# 7. Verify
curl https://yourdomain.com/docs
```

---

## Support Resources

- **FastAPI Deployment**: https://fastapi.tiangolo.com/deployment/
- **PostgreSQL Security**: https://www.postgresql.org/docs/current/ssl-tcp.html
- **Let's Encrypt**: https://letsencrypt.org/getting-started/
- **Docker Production**: https://docs.docker.com/config/containers/start-containers-automatically/

---

**Your auth system is production-ready.** Just add HTTPS and update environment variables. 🚀
