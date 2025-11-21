# API Overview

## What is Billings API?

A comprehensive exam preparation platform API that provides:
- User authentication and authorization
- Question bank management by exam type
- Quiz taking and performance tracking
- Gamification (achievements, avatars, leaderboards)
- Bookmark system for saving questions
- Admin panel for content management

## Architecture

```
┌─────────────┐
│   Frontend  │
│  (React)    │
└─────┬───────┘
      │ HTTP/JSON
      │
┌─────▼───────────────────────────────┐
│         Billings API                │
│                                     │
│  ┌──────────┐  ┌──────────────┐   │
│  │  Routes  │  │ Middleware   │   │
│  │  Layer   │  │ - CORS       │   │
│  └────┬─────┘  │ - Rate Limit │   │
│       │        │ - Auth       │   │
│  ┌────▼─────┐  │ - Logging    │   │
│  │Controller│  └──────────────┘   │
│  │  Layer   │                      │
│  └────┬─────┘                      │
│       │                            │
│  ┌────▼─────┐                      │
│  │ Service  │                      │
│  │  Layer   │                      │
│  └────┬─────┘                      │
│       │                            │
│  ┌────▼─────┐                      │
│  │PostgreSQL│                      │
│  │ Database │                      │
│  └──────────┘                      │
└─────────────────────────────────────┘
```

## Core Concepts

### 1. RESTful Design

The API follows REST principles:
- **Resources**: Questions, Users, Bookmarks, Quizzes, etc.
- **HTTP Methods**: GET (read), POST (create), PUT/PATCH (update), DELETE (remove)
- **Status Codes**: 200 (success), 201 (created), 400 (bad request), 401 (unauthorized), 404 (not found), etc.

### 2. Versioning

All endpoints are versioned under `/api/v1/`:
```
/api/v1/auth/login
/api/v1/questions/quiz
/api/v1/bookmarks
```

### 3. Authentication

Uses **JWT (JSON Web Tokens)**:
1. User signs up or logs in → receives `access_token`
2. Frontend includes token in `Authorization: Bearer <token>` header
3. Backend validates token and identifies user

### 4. Response Format

**Success Response:**
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation successful"
}
```

**Error Response:**
```json
{
  "success": false,
  "error": {
    "message": "Bookmark not found",
    "code": "RESOURCE_NOT_FOUND"
  },
  "status_code": 404,
  "timestamp": "2025-01-20T14:30:00Z",
  "path": "/api/v1/bookmarks/questions/999"
}
```

## Feature Modules

### Authentication (`/auth`)
- Signup, login, logout
- Email verification
- Password reset
- Session management

### Questions (`/questions`)
- Browse questions by exam type
- Get random quiz questions
- Filter by domain

### Bookmarks (`/bookmarks`)
- Bookmark questions with notes
- View all bookmarks (paginated)
- Remove bookmarks

### Quizzes (`/quiz`)
- Submit quiz attempts
- View quiz history
- Get performance statistics

### Gamification
- **Achievements** (`/achievements`): View and track achievements
- **Avatars** (`/avatars`): Unlock and select avatars
- **Leaderboard** (`/leaderboard`): Compete with other users

### Admin (`/admin`)
- Manage questions (CRUD)
- View users
- Manage achievements

## Rate Limits

| Endpoint Type | Limit | Window |
|--------------|-------|--------|
| Public endpoints | 60 requests | 1 minute |
| Auth (signup/login) | 3 requests | 1 hour |
| Authenticated endpoints | 100 requests | 1 minute |

**Rate limit exceeded response:**
```json
{
  "error": "Rate limit exceeded: 3 per 1 hour"
}
```

## CORS Configuration

The API allows requests from:
- `http://localhost:8080`
- `http://127.0.0.1:8080`
- `http://0.0.0.0:8080`

**Allowed methods:** GET, POST, PUT, PATCH, DELETE
**Allowed headers:** All (including `Authorization`, `Content-Type`)
**Credentials:** Supported

## Security Features

- **JWT Authentication**: Secure token-based auth
- **Password Hashing**: bcrypt with salt rounds
- **Rate Limiting**: Prevents abuse
- **CORS**: Configured for known origins only
- **Security Headers**: XSS protection, frame options, CSP
- **Input Validation**: All requests validated with Pydantic
- **SQL Injection Protection**: SQLAlchemy ORM prevents SQL injection

## Next Steps

Continue to:
- **[Authentication Guide](./02-authentication.md)** to learn about auth flows
- **[Error Handling](./03-error-handling.md)** to handle errors properly
- **[Endpoints Reference](./04-endpoints-reference.md)** for complete endpoint docs
