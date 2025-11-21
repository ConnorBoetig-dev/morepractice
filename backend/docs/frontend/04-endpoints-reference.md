# Endpoints Reference

Complete reference for all API endpoints.

## Table of Contents

- [Authentication](#authentication)
- [Questions](#questions)
- [Bookmarks](#bookmarks)
- [Quizzes](#quizzes)
- [Study Mode](#study-mode)
- [Achievements](#achievements)
- [Avatars](#avatars)
- [Leaderboard](#leaderboard)
- [Admin](#admin)
- [Health](#health)

---

## Authentication

### POST /api/v1/auth/signup
Create a new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "SecurePass123!"
}
```

**Success Response (201):**
```json
{
  "success": true,
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "johndoe",
    "is_active": true,
    "is_verified": false
  }
}
```

**Errors:**
- `400 EMAIL_ALREADY_REGISTERED` - Email already exists
- `400 USERNAME_ALREADY_TAKEN` - Username taken
- `422 VALIDATION_ERROR` - Missing/invalid fields

---

### POST /api/v1/auth/login
Login with email and password.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": { ... }
}
```

**Errors:**
- `401 INVALID_CREDENTIALS` - Wrong email/password
- `403 ACCOUNT_LOCKED` - Too many failed attempts

---

### GET /api/v1/auth/me
Get current user profile with gamification stats.

**Headers:** `Authorization: Bearer <token>`

**Rate Limit:** 300 requests/minute

**Success Response (200):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "is_active": true,
  "is_verified": true,
  "is_admin": false,
  "created_at": "2025-01-20T10:00:00Z",

  "bio": "I love learning cybersecurity!",
  "avatar_url": "https://example.com/avatars/dragon.png",
  "selected_avatar_id": 5,

  "xp": 1250,
  "level": 5,
  "study_streak_current": 7,
  "study_streak_longest": 15,
  "total_exams_taken": 25,
  "total_questions_answered": 500,
  "last_activity_date": "2025-01-20"
}
```

**Fields:**
- User fields: `id`, `email`, `username`, `is_active`, `is_verified`, `is_admin`, `created_at`
- Profile fields: `bio`, `avatar_url`, `selected_avatar_id`
- Gamification: `xp`, `level`, `study_streak_current`, `study_streak_longest`
- Stats: `total_exams_taken`, `total_questions_answered`, `last_activity_date`

**Errors:**
- `401 UNAUTHORIZED` - Invalid/missing token
- `404 NOT_FOUND` - User profile not found (shouldn't happen)

---

### POST /api/v1/auth/logout
Logout and invalidate session.

**Headers:** `Authorization: Bearer <token>`

**Success Response (200):**
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

---

### POST /api/v1/auth/refresh
Refresh access token using refresh token.

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Success Response (200):**
```json
{
  "success": true,
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

### PATCH /api/v1/auth/profile
Update user profile (username, email, or bio).

**Headers:** `Authorization: Bearer <token>`

**Rate Limit:** 5 requests/minute

**Request Body:**
```json
{
  "username": "new_username",  // Optional: New username (3-50 chars, alphanumeric + _ -)
  "email": "newemail@example.com",  // Optional: New email (requires re-verification)
  "bio": "I love coding and cybersecurity!"  // Optional: Bio (max 500 chars)
}
```

**Notes:**
- All fields are optional - send only what you want to update
- Changing email will set `is_verified` to `false` and send verification email
- Bio can be up to 500 characters
- Username must be unique and follow format rules

**Success Response (200):**
```json
{
  "message": "Profile updated successfully",
  "detail": "Verification email sent to new address"  // Only if email changed
}
```

**Errors:**
- `400 BAD_REQUEST` - Username/email already taken
- `401 UNAUTHORIZED` - Invalid/missing token
- `422 VALIDATION_ERROR` - Invalid username format or bio too long

**Examples:**

Update only bio:
```javascript
await fetch('/api/v1/auth/profile', {
  method: 'PATCH',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ bio: "Updated bio text" })
});
```

Update multiple fields:
```javascript
await fetch('/api/v1/auth/profile', {
  method: 'PATCH',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    username: "newusername",
    bio: "New bio text"
  })
});
```

---

### GET /api/v1/auth/users/{user_id}
Get public profile for any user by ID (e.g., from leaderboard).

**No Authentication Required** - Public endpoint

**Rate Limit:** 300 requests/minute

**Path Parameters:**
- `user_id` (integer): The user's ID

**Success Response (200):**
```json
{
  "id": 5,
  "username": "johndoe",
  "created_at": "2025-01-15T10:00:00Z",

  "bio": "Cybersecurity enthusiast learning for Security+",
  "avatar_url": "https://example.com/avatars/dragon.png",
  "selected_avatar_id": 5,

  "xp": 5000,
  "level": 15,
  "study_streak_current": 12,
  "study_streak_longest": 25,
  "total_exams_taken": 150,
  "total_questions_answered": 3000
}
```

**Fields:**
- Public user data: `id`, `username`, `created_at`
- Profile customization: `bio`, `avatar_url`, `selected_avatar_id`
- Gamification: `xp`, `level`, `study_streak_current`, `study_streak_longest`
- Stats: `total_exams_taken`, `total_questions_answered`

**Privacy Note:**
Does NOT include sensitive data like `email`, `is_admin`, `is_active`, or `is_verified`.

**Errors:**
- `404 NOT_FOUND` - User does not exist

**Use Cases:**
- View user profile from leaderboard rankings
- Check another user's stats and achievements
- Compare progress with friends

**Example:**
```javascript
// Get public profile for user ID 5 (e.g., from leaderboard click)
const response = await fetch('/api/v1/auth/users/5');
const profile = await response.json();

console.log(`${profile.username} - Level ${profile.level} (${profile.xp} XP)`);
console.log(`Current streak: ${profile.study_streak_current} days`);
```

---

## Questions

### GET /api/v1/questions/exams
Get list of available exam types.

**Headers:** `Authorization: Bearer <token>`

**Success Response (200):**
```json
{
  "success": true,
  "exams": [
    {
      "exam_type": "security",
      "display_name": "Security+",
      "total_questions": 450
    },
    {
      "exam_type": "network",
      "display_name": "Network+",
      "total_questions": 320
    }
  ]
}
```

---

### GET /api/v1/questions/quiz
Get random questions for a quiz.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `exam_type` (required): Exam type (e.g., "security", "network")
- `count` (optional): Number of questions (default: 30, max: 100)
- `domain` (optional): Filter by domain (e.g., "1.1", "2.3")

**Example:**
```
GET /api/v1/questions/quiz?exam_type=security&count=30&domain=1.1
```

**Success Response (200):**
```json
{
  "success": true,
  "questions": [
    {
      "id": 1,
      "question_id": "SEC001",
      "exam_type": "security",
      "domain": "1.1",
      "question_text": "What is the primary purpose of...",
      "options": {
        "A": {
          "text": "Option A text",
          "explanation": "Why this is correct/wrong"
        },
        "B": { ... }
      },
      "correct_answer": "A",
      "created_at": "2025-01-20T10:00:00Z"
    }
  ],
  "total_count": 30
}
```

**Errors:**
- `400 INVALID_INPUT` - Invalid exam_type or parameters
- `401 UNAUTHORIZED` - Not authenticated

---

## Bookmarks

### POST /api/v1/bookmarks/questions/{question_id}
Bookmark a question.

**Headers:** `Authorization: Bearer <token>`

**Path Parameters:**
- `question_id` (integer): ID of question to bookmark

**Request:**
```json
{
  "notes": "Review this - tricky question about encryption"
}
```

**Success Response (201):**
```json
{
  "success": true,
  "bookmark": {
    "id": 1,
    "user_id": 1,
    "question_id": 123,
    "notes": "Review this - tricky question about encryption",
    "created_at": "2025-01-20T14:30:00Z",
    "updated_at": "2025-01-20T14:30:00Z"
  }
}
```

**Errors:**
- `404 QUESTION_NOT_FOUND` - Question doesn't exist
- `401 UNAUTHORIZED` - Not authenticated

---

### GET /api/v1/bookmarks
Get all bookmarks for current user (paginated).

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Items per page (default: 10, max: 100)

**Example:**
```
GET /api/v1/bookmarks?page=1&page_size=20
```

**Success Response (200):**
```json
{
  "success": true,
  "bookmarks": [
    {
      "id": 1,
      "question_id": 123,
      "notes": "Review this",
      "created_at": "2025-01-20T14:30:00Z",
      "question": {
        "id": 123,
        "question_text": "What is...",
        "exam_type": "security",
        "domain": "1.1"
      }
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_items": 45,
    "total_pages": 3
  }
}
```

**Errors:**
- `422 VALIDATION_ERROR` - Invalid page/page_size
- `401 UNAUTHORIZED` - Not authenticated

---

### DELETE /api/v1/bookmarks/questions/{question_id}
Remove a bookmark.

**Headers:** `Authorization: Bearer <token>`

**Success Response (200):**
```json
{
  "success": true,
  "message": "Bookmark removed successfully"
}
```

**Errors:**
- `404 BOOKMARK_NOT_FOUND` - Bookmark doesn't exist

---

### PATCH /api/v1/bookmarks/questions/{question_id}
Update bookmark notes.

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "notes": "Updated notes here"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "bookmark": {
    "id": 1,
    "notes": "Updated notes here",
    "updated_at": "2025-01-20T15:00:00Z"
  }
}
```

---

### GET /api/v1/bookmarks/questions/{question_id}/check
Check if a question is bookmarked.

**Headers:** `Authorization: Bearer <token>`

**Success Response (200):**
```json
{
  "is_bookmarked": true
}
```

---

## Quizzes

### POST /api/v1/quiz/submit
Submit a completed quiz.

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "exam_type": "security",
  "answers": [
    {
      "question_id": 123,
      "selected_answer": "A"
    },
    {
      "question_id": 124,
      "selected_answer": "C"
    }
  ],
  "time_spent_seconds": 1800
}
```

**Success Response (201):**
```json
{
  "success": true,
  "attempt": {
    "id": 1,
    "user_id": 1,
    "exam_type": "security",
    "score": 85.5,
    "total_questions": 30,
    "correct_answers": 26,
    "time_spent_seconds": 1800,
    "xp_earned": 100,
    "created_at": "2025-01-20T14:30:00Z"
  },
  "results": [
    {
      "question_id": 123,
      "selected_answer": "A",
      "correct_answer": "A",
      "is_correct": true
    }
  ]
}
```

---

### GET /api/v1/quiz/history
Get quiz attempt history.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `page`, `page_size`: Pagination
- `exam_type` (optional): Filter by exam type

**Success Response (200):**
```json
{
  "success": true,
  "attempts": [
    {
      "id": 1,
      "exam_type": "security",
      "score": 85.5,
      "total_questions": 30,
      "correct_answers": 26,
      "created_at": "2025-01-20T14:30:00Z"
    }
  ],
  "pagination": { ... }
}
```

---

### GET /api/v1/quiz/stats
Get quiz statistics.

**Headers:** `Authorization: Bearer <token>`

**Success Response (200):**
```json
{
  "success": true,
  "stats": {
    "total_attempts": 15,
    "average_score": 82.3,
    "total_xp": 1500,
    "by_exam_type": {
      "security": {
        "attempts": 10,
        "average_score": 85.0
      },
      "network": {
        "attempts": 5,
        "average_score": 76.0
      }
    }
  }
}
```

---

## Study Mode

Study mode allows users to answer questions one at a time with immediate feedback, explanations, and learning insights. Different from practice mode where you answer all questions first and get results at the end.

### POST /api/v1/study/start
Start a new study mode session.

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "exam_type": "security",
  "count": 30,
  "domain": "1.1"  // optional: filter by specific domain
}
```

**Success Response (201):**
```json
{
  "session_id": 1,
  "exam_type": "security",
  "total_questions": 30,
  "current_index": 0,
  "current_question": {
    "question_id": 123,
    "question_text": "What is the primary purpose of encryption?",
    "domain": "1.1",
    "options": {
      "A": {"text": "To compress data"},
      "B": {"text": "To protect data confidentiality"},
      "C": {"text": "To speed up transmission"},
      "D": {"text": "To authenticate users"}
    }
  }
}
```

**Errors:**
- `400 ACTIVE_SESSION_EXISTS` - User already has an active study session
- `404 NO_QUESTIONS_FOUND` - No questions available for the exam type

**Note:** Only one active study session allowed per user. Abandon or complete current session before starting a new one.

---

### POST /api/v1/study/answer
Answer current question and get immediate feedback.

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "session_id": 1,
  "question_id": 123,
  "user_answer": "B"
}
```

**Success Response (200) - Not Last Question:**
```json
{
  "is_correct": true,
  "user_answer": "B",
  "correct_answer": "B",
  "user_answer_text": "To protect data confidentiality",
  "correct_answer_text": "To protect data confidentiality",
  "user_answer_explanation": "Correct! Encryption transforms data into unreadable format...",
  "correct_answer_explanation": "Encryption transforms data into unreadable format...",
  "all_options": {
    "A": {
      "text": "To compress data",
      "explanation": "Compression reduces file size, not encryption's purpose"
    },
    "B": {
      "text": "To protect data confidentiality",
      "explanation": "Correct! Encryption transforms data into unreadable format..."
    },
    "C": {
      "text": "To speed up transmission",
      "explanation": "Encryption may actually slow transmission due to processing overhead"
    },
    "D": {
      "text": "To authenticate users",
      "explanation": "Authentication verifies identity, separate from encryption"
    }
  },
  "current_index": 1,
  "total_questions": 30,
  "questions_remaining": 29,
  "next_question": {
    "question_id": 124,
    "question_text": "Which protocol provides end-to-end encryption?",
    "domain": "1.2",
    "options": {
      "A": {"text": "HTTP"},
      "B": {"text": "HTTPS"},
      "C": {"text": "FTP"},
      "D": {"text": "Telnet"}
    }
  },
  "session_completed": false
}
```

**Success Response (200) - Last Question (Session Complete):**
```json
{
  "is_correct": false,
  "user_answer": "A",
  "correct_answer": "B",
  "user_answer_text": "HTTP",
  "correct_answer_text": "HTTPS",
  "user_answer_explanation": "HTTP doesn't provide encryption...",
  "correct_answer_explanation": "HTTPS uses TLS/SSL for encryption...",
  "all_options": { ... },
  "current_index": 30,
  "total_questions": 30,
  "questions_remaining": 0,
  "next_question": null,
  "session_completed": true,
  "completion": {
    "quiz_attempt_id": 1,
    "score": 25,
    "total_questions": 30,
    "score_percentage": 83.33,
    "xp_earned": 187,
    "total_xp": 1687,
    "current_level": 4,
    "previous_level": 3,
    "level_up": true,
    "achievements_unlocked": [
      {
        "id": 5,
        "name": "Study Marathon",
        "description": "Complete 30 questions in study mode",
        "icon": "book-open",
        "xp_reward": 50
      }
    ]
  }
}
```

**Errors:**
- `404 SESSION_NOT_FOUND` - Session doesn't exist
- `400 SESSION_COMPLETED` - Session already completed
- `400 QUESTION_MISMATCH` - Not the current question
- `404 QUESTION_NOT_FOUND` - Question doesn't exist

**Key Features:**
- Immediate feedback after each answer
- Explanations for all options (learn why wrong answers are wrong)
- Auto-completion on last question
- XP awarded: 75% of practice mode (easier learning path)

---

### GET /api/v1/study/active
Get user's active study session (for resuming).

**Headers:** `Authorization: Bearer <token>`

**Success Response (200):**
```json
{
  "session_id": 1,
  "exam_type": "security",
  "total_questions": 30,
  "current_index": 15,
  "current_question": {
    "question_id": 138,
    "question_text": "What is a firewall?",
    "domain": "2.3",
    "options": { ... }
  }
}
```

**Errors:**
- `404 NO_ACTIVE_SESSION` - User has no active study session

**Use Cases:**
- Resume session after closing app
- Check if session exists before starting new one
- Get current question after page refresh

---

### DELETE /api/v1/study/abandon
Abandon (delete) current study session without completing it.

**Headers:** `Authorization: Bearer <token>`

**Success Response (200):**
```json
{
  "success": true,
  "message": "Study session abandoned successfully"
}
```

**Errors:**
- `404 NO_ACTIVE_SESSION` - User has no active study session

**Warning:** All progress in the session will be lost!

**Use Cases:**
- Start a different exam type
- Restart with different settings
- Clear abandoned sessions

---

## Study Mode vs Practice Mode

| Feature | Study Mode | Practice Mode |
|---------|-----------|---------------|
| Workflow | Answer one at a time | Answer all first, results at end |
| Feedback | Immediate after each question | All at end |
| Explanations | After every answer | None during quiz |
| XP Earned | 75% (easier, has hints) | 100% (harder, simulates exam) |
| Resumable | Yes (GET /study/active) | No |
| Use Case | Learning & understanding | Exam simulation & testing |

**Recommendation:**
- **Study Mode**: First time learning material, reviewing weak areas
- **Practice Mode**: Final preparation, simulating real exam conditions

---

## Achievements

### GET /api/v1/achievements
Get all available achievements.

**Headers:** `Authorization: Bearer <token>`

**Success Response (200):**
```json
{
  "success": true,
  "achievements": [
    {
      "id": 1,
      "name": "First Quiz",
      "description": "Complete your first quiz",
      "icon": "trophy",
      "xp_reward": 50,
      "requirement_type": "quiz_count",
      "requirement_value": 1
    }
  ]
}
```

---

### GET /api/v1/achievements/earned
Get user's earned achievements.

**Headers:** `Authorization: Bearer <token>`

**Success Response (200):**
```json
{
  "success": true,
  "earned_achievements": [
    {
      "achievement_id": 1,
      "earned_at": "2025-01-20T14:30:00Z",
      "achievement": {
        "name": "First Quiz",
        "description": "Complete your first quiz",
        "xp_reward": 50
      }
    }
  ]
}
```

---

## Leaderboard

### GET /api/v1/leaderboard/xp
Get XP leaderboard.

**Query Parameters:**
- `limit` (optional): Number of top users (default: 10, max: 100)

**Success Response (200):**
```json
{
  "success": true,
  "leaderboard": [
    {
      "rank": 1,
      "user_id": 5,
      "username": "johndoe",
      "total_xp": 5000,
      "level": 15
    }
  ]
}
```

---

## Admin

All admin endpoints require admin role.

### GET /api/v1/admin/users
List all users (admin only).

**Headers:** `Authorization: Bearer <admin_token>`

**Query Parameters:**
- `page`, `page_size`: Pagination

**Success Response (200):**
```json
{
  "success": true,
  "users": [
    {
      "id": 1,
      "email": "user@example.com",
      "username": "johndoe",
      "is_active": true,
      "created_at": "2025-01-20T10:00:00Z"
    }
  ],
  "pagination": { ... }
}
```

**Errors:**
- `403 ADMIN_REQUIRED` - Not an admin

---

### POST /api/v1/admin/questions
Create a new question (admin only).

**Headers:** `Authorization: Bearer <admin_token>`

**Request:**
```json
{
  "question_id": "SEC999",
  "exam_type": "security",
  "domain": "1.1",
  "question_text": "What is...",
  "options": {
    "A": {
      "text": "Option A",
      "explanation": "Why this is correct"
    },
    "B": { ... }
  },
  "correct_answer": "A"
}
```

---

## Health

### GET /health
Health check endpoint (no auth required).

**Success Response (200):**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-20T14:30:00Z",
  "database": "connected",
  "version": "1.0.0"
}
```

---

## Common Patterns

### Pagination

All paginated endpoints accept:
- `page` (integer, >= 1, default: 1)
- `page_size` (integer, 1-100, default: 10)

Response includes:
```json
{
  "pagination": {
    "page": 1,
    "page_size": 10,
    "total_items": 45,
    "total_pages": 5
  }
}
```

### Authentication

All protected endpoints require:
```
Authorization: Bearer <access_token>
```

### Timestamps

All timestamps are ISO 8601 UTC:
```
2025-01-20T14:30:00Z
```

## Next Steps

- **[Data Models](./05-data-models.md)** - Detailed schema documentation
- **[Integration Guide](./06-integration-guide.md)** - Complete integration examples
