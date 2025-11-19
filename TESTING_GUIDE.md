# Auth System Testing Guide

## Current Status: Backend Ready for Testing

The authentication system with email integration is fully implemented and the backend is running successfully.

---

## What's Been Set Up

### Backend (Running on http://localhost:8000)
- Server is running and ready
- Database migrated with new email token fields
- All endpoints are functional

### New API Endpoints

| Endpoint | Method | Purpose | Status |
|----------|--------|---------|--------|
| `/api/v1/auth/request-reset` | POST | Request password reset email | ✅ Working |
| `/api/v1/auth/reset-password` | POST | Reset password with token | ✅ Working |
| `/api/v1/auth/send-verification` | POST | Send email verification | ✅ Working |
| `/api/v1/auth/verify-email` | POST | Verify email with token | ✅ Working |

### Frontend Pages

| Page | Purpose | Status |
|------|---------|--------|
| `/frontend/request-reset.html` | Request password reset | ✅ Created |
| `/frontend/reset-password.html` | Set new password | ✅ Created |
| `/frontend/verify-email.html` | Email verification | ✅ Created |
| `/frontend/login.html` | Updated with "Forgot password?" link | ✅ Updated |

---

## Configuration Status

### `.env` File Location: `/home/connor-boetig/proj/billings/.env`

**Current Email Settings:**
```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com        # ⚠️ NEEDS TO BE UPDATED
SMTP_PASSWORD=your-app-password-here      # ⚠️ NEEDS TO BE UPDATED
FROM_EMAIL=noreply@billings.com
FRONTEND_URL=http://localhost:8080
```

---

## To Test With Real Emails

### Option 1: Gmail (Recommended for Testing)

1. **Enable 2-Factor Authentication** on your Google Account:
   - Go to https://myaccount.google.com/security
   - Enable 2-Step Verification

2. **Generate App Password**:
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" and your device
   - Copy the 16-character password (format: `xxxx-xxxx-xxxx-xxxx`)

3. **Update `.env` file**:
   ```bash
   SMTP_USERNAME=your-actual-email@gmail.com
   SMTP_PASSWORD=xxxx-xxxx-xxxx-xxxx  # The app password
   FROM_EMAIL=your-actual-email@gmail.com  # Or keep noreply@billings.com
   ```

4. **Restart the backend**:
   ```bash
   # Kill the current server (Ctrl+C or kill the process)
   cd /home/connor-boetig/proj/billings/backend
   source ../venv/bin/activate
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

### Option 2: SendGrid (Recommended for Production)

1. Sign up at https://sendgrid.com (free tier: 100 emails/day)
2. Create an API key
3. Update `.env`:
   ```bash
   SMTP_HOST=smtp.sendgrid.net
   SMTP_PORT=587
   SMTP_USERNAME=apikey
   SMTP_PASSWORD=your-sendgrid-api-key
   FROM_EMAIL=noreply@yourdomain.com
   ```

---

## Testing Without Email (Current State)

Even without SMTP credentials, you can test the API endpoints:

### 1. Test Password Reset Request
```bash
curl http://localhost:8000/api/v1/auth/request-reset \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"email":"testuser2@example.com"}'
```

**Expected Response:**
```json
{
    "message": "If that email exists, a password reset link has been sent",
    "detail": "Check your inbox and spam folder"
}
```

### 2. Check Database for Token
```bash
# Connect to PostgreSQL
psql postgresql://postgres:postgres@localhost:5432/billings

# Check if reset token was generated
SELECT email, reset_token, reset_token_expires FROM users WHERE email = 'testuser2@example.com';
```

You should see a reset token and expiration time.

### 3. Test Password Reset (using the token from database)
```bash
curl http://localhost:8000/api/v1/auth/reset-password \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"token":"PASTE_TOKEN_HERE","new_password":"NewPassword123"}'
```

---

## Complete End-to-End Testing (With Email Configured)

### Password Reset Flow

1. **Start Frontend**:
   ```bash
   cd /home/connor-boetig/proj/billings/frontend
   python3 -m http.server 8080
   ```

2. **Open Browser**: http://localhost:8080/login.html

3. **Click "Forgot password?"**

4. **Enter Email**: testuser2@example.com

5. **Check Email**: Look for reset email

6. **Click Reset Link**: Should open `/reset-password.html?token=...`

7. **Set New Password**: Enter and confirm new password

8. **Login**: Use new password to login

### Email Verification Flow

1. **Create New User**: http://localhost:8080/signup.html

2. **Check Welcome Email**: Should receive immediately

3. **Request Verification Email** (if needed):
   ```bash
   curl http://localhost:8000/api/v1/auth/send-verification \
     -X POST \
     -H "Content-Type: application/json" \
     -d '{"email":"newuser@example.com"}'
   ```

4. **Click Verification Link**: Opens `/verify-email.html?token=...`

5. **Auto-Verification**: Page auto-verifies and redirects

---

## API Testing with Postman/Insomnia

### Import Collection

**Base URL**: `http://localhost:8000/api/v1`

**Endpoints:**

1. **POST** `/auth/signup`
   ```json
   {
     "email": "test@example.com",
     "username": "testuser",
     "password": "Test123456"
   }
   ```

2. **POST** `/auth/login`
   ```json
   {
     "email": "test@example.com",
     "password": "Test123456"
   }
   ```

3. **POST** `/auth/request-reset`
   ```json
   {
     "email": "test@example.com"
   }
   ```

4. **POST** `/auth/reset-password`
   ```json
   {
     "token": "your-token-here",
     "new_password": "NewPass123"
   }
   ```

5. **POST** `/auth/send-verification`
   ```json
   {
     "email": "test@example.com"
   }
   ```

6. **POST** `/auth/verify-email`
   ```json
   {
     "token": "your-token-here"
   }
   ```

---

## Database Migration Applied

**Migration**: `fd40d9dfebff_add_email_verification_and_password_reset_tokens_to_users_table.py`

**New Columns Added to `users` table:**
- `email_verification_token` (String)
- `email_verified_at` (DateTime)
- `reset_token` (String)
- `reset_token_expires` (DateTime)

---

## Security Features Implemented

- Cryptographically secure tokens (`secrets.token_urlsafe(32)`)
- Constant-time token comparison (prevents timing attacks)
- Token expiration (1 hour for reset, 24 hours for verification)
- Tokens cleared after use
- No email enumeration (generic success messages)
- Rate limiting: 5 requests/minute per IP
- Async email sending (non-blocking)

---

## Troubleshooting

### Email not sending?
- Check `.env` has correct SMTP credentials
- Restart backend server after changing `.env`
- Check server logs for email errors
- Test with `curl` first before using frontend

### Database errors?
- Run migrations: `alembic upgrade head`
- Check PostgreSQL is running: `docker ps` or `pg_isready`

### Frontend not connecting?
- Ensure backend is running on port 8000
- Check `frontend/js/config.js` has correct API_BASE_URL
- Use browser dev tools to check network requests

---

## Next Steps

1. **Configure Email** (optional but recommended for full testing):
   - Set up Gmail app password OR SendGrid
   - Update `.env` file
   - Restart backend

2. **Test Frontend Pages**:
   - Start frontend server: `cd frontend && python3 -m http.server 8080`
   - Test complete flows in browser

3. **Test Edge Cases**:
   - Expired tokens
   - Invalid tokens
   - Non-existent emails
   - Rate limiting (try 6 requests in 1 minute)

---

## Summary

### What Works Right Now (Without Email)
- All API endpoints respond correctly
- Tokens generated and stored in database
- Token validation works
- Password reset logic works
- Frontend pages created

### What Needs Email Config
- Actually sending emails
- Receiving reset links in email
- Receiving verification links in email
- Welcome emails on signup

**Backend Status**: ✅ Running on http://localhost:8000
**Frontend Status**: ⏸️ Not started (run `python3 -m http.server 8080` in frontend folder)
**Email Status**: ⚠️ Configured but needs credentials
**Database**: ✅ Migrated and ready

---

*Last Updated: 2025-11-18 19:15 UTC*
