# API Endpoints Reference

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication
Most endpoints require JWT authentication via the `Authorization` header:
```
Authorization: Bearer <jwt_token>
```

---

## Endpoint Summary

### Authentication (3 endpoints)
- `POST /auth/signup` - Create new account
- `POST /auth/login` - Login and get JWT token
- `GET /auth/me` - Get current user profile

### Questions (2 endpoints)
- `GET /questions/exams` - Get available exam types
- `GET /questions/quiz` - Get random quiz questions

### Quiz (4 endpoints)
- `POST /quiz/submit` - Submit completed quiz
- `GET /quiz/history` - Get quiz attempt history
- `GET /quiz/stats` - Get aggregated quiz statistics
- `GET /quiz/attempt/{attempt_id}` - Get detailed quiz attempt

### Achievements (4 endpoints)
- `GET /achievements` - Get all public achievements
- `GET /achievements/me` - Get achievements with user progress
- `GET /achievements/earned` - Get user's earned achievements
- `GET /achievements/stats` - Get user achievement statistics

### Avatars (5 endpoints)
- `GET /avatars` - Get all public avatars
- `GET /avatars/me` - Get avatars with unlock status
- `GET /avatars/unlocked` - Get user's unlocked avatars
- `POST /avatars/select` - Equip an avatar
- `GET /avatars/stats` - Get avatar collection stats

### Leaderboards (5 endpoints)
- `GET /leaderboard/xp` - XP leaderboard
- `GET /leaderboard/quiz-count` - Quiz count leaderboard
- `GET /leaderboard/accuracy` - Accuracy leaderboard
- `GET /leaderboard/streak` - Study streak leaderboard
- `GET /leaderboard/exam/{exam_type}` - Exam-specific leaderboard

**Total**: 23 endpoints

---

## Authentication Endpoints

### POST /auth/signup
Create a new user account.

**Authentication**: None

**Request Body**:
```json
{
  "email": "user@example.com",
  "username": "QuizMaster",
  "password": "SecurePassword123"
}
```

**Response** (201 Created):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "QuizMaster",
    "is_active": true,
    "is_verified": false,
    "created_at": "2025-01-15T14:32:10Z"
  },
  "profile": {
    "user_id": 1,
    "xp": 0,
    "level": 1,
    "study_streak_current": 0,
    "study_streak_longest": 0,
    "total_exams_taken": 0,
    "total_questions_answered": 0,
    "selected_avatar_id": null
  }
}
```

**Errors**:
- `400 Bad Request` - Email or username already exists
- `422 Unprocessable Entity` - Invalid email format or password too short

**File**: `backend/app/api/v1/auth_routes.py`

---

### POST /auth/login
Login with email and password.

**Authentication**: None

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123"
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "QuizMaster",
    "is_active": true
  },
  "profile": {
    "xp": 1520,
    "level": 5,
    "study_streak_current": 3,
    "selected_avatar_id": 7
  }
}
```

**Errors**:
- `401 Unauthorized` - Invalid email or password
- `403 Forbidden` - Account disabled (is_active=False)

**File**: `backend/app/api/v1/auth_routes.py`

---

### GET /auth/me
Get current authenticated user's profile.

**Authentication**: Required (JWT)

**Response** (200 OK):
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "QuizMaster",
    "is_active": true,
    "created_at": "2025-01-15T14:32:10Z"
  },
  "profile": {
    "xp": 1520,
    "level": 5,
    "study_streak_current": 3,
    "study_streak_longest": 7,
    "total_exams_taken": 12,
    "total_questions_answered": 360,
    "selected_avatar_id": 7,
    "bio": "Studying for Security+",
    "avatar_url": null
  }
}
```

**Errors**:
- `401 Unauthorized` - Invalid or missing JWT token

**File**: `backend/app/api/v1/auth_routes.py`

---

## Question Endpoints

### GET /questions/exams
Get list of available exam types.

**Authentication**: None

**Response** (200 OK):
```json
{
  "exams": [
    {
      "exam_type": "security_plus",
      "display_name": "Security+",
      "question_count": 1250
    },
    {
      "exam_type": "network_plus",
      "display_name": "Network+",
      "question_count": 980
    },
    {
      "exam_type": "a_plus_core_1",
      "display_name": "A+ Core 1 (220-1101)",
      "question_count": 850
    },
    {
      "exam_type": "a_plus_core_2",
      "display_name": "A+ Core 2 (220-1102)",
      "question_count": 820
    }
  ]
}
```

**File**: `backend/app/api/v1/question_routes.py`

---

### GET /questions/quiz
Get random quiz questions for practice.

**Authentication**: None (but typically used with auth for tracking)

**Query Parameters**:
- `exam_type` (required): "security_plus", "network_plus", "a_plus_core_1", "a_plus_core_2"
- `count` (optional, default=30): Number of questions (1-100)
- `domain` (optional): Filter by specific domain (e.g., "1.1", "2.3")

**Example**:
```
GET /questions/quiz?exam_type=security_plus&count=30
```

**Response** (200 OK):
```json
{
  "questions": [
    {
      "id": 123,
      "question_id": "SEC-001",
      "exam_type": "security_plus",
      "domain": "1.1",
      "question_text": "Which of the following is a symmetric encryption algorithm?",
      "options": {
        "A": {
          "text": "AES",
          "explanation": "AES is a symmetric encryption algorithm"
        },
        "B": {
          "text": "RSA",
          "explanation": "RSA is asymmetric, not symmetric"
        },
        "C": {
          "text": "ECC",
          "explanation": "ECC is asymmetric, not symmetric"
        },
        "D": {
          "text": "Diffie-Hellman",
          "explanation": "Diffie-Hellman is a key exchange protocol"
        }
      },
      "correct_answer": "A"
    }
  ],
  "metadata": {
    "exam_type": "security_plus",
    "count": 30,
    "domain": null
  }
}
```

**Errors**:
- `400 Bad Request` - Invalid exam_type or count
- `404 Not Found` - No questions found for criteria

**File**: `backend/app/api/v1/question_routes.py`

---

## Quiz Endpoints

### POST /quiz/submit
Submit a completed quiz for grading and XP.

**Authentication**: Required (JWT)

**Request Body**:
```json
{
  "exam_type": "security_plus",
  "total_questions": 30,
  "time_taken_seconds": 1800,
  "answers": [
    {
      "question_id": 123,
      "user_answer": "A",
      "correct_answer": "A",
      "is_correct": true,
      "time_spent_seconds": 45
    },
    {
      "question_id": 124,
      "user_answer": "B",
      "correct_answer": "C",
      "is_correct": false,
      "time_spent_seconds": 60
    }
  ]
}
```

**Response** (201 Created):
```json
{
  "quiz_attempt": {
    "id": 456,
    "user_id": 1,
    "exam_type": "security_plus",
    "total_questions": 30,
    "correct_answers": 28,
    "score_percentage": 93.33,
    "xp_earned": 420,
    "time_taken_seconds": 1800,
    "completed_at": "2025-01-15T14:32:10Z"
  },
  "xp_earned": 420,
  "new_level": 8,
  "level_up": true,
  "achievements_unlocked": [
    {
      "achievement_id": 7,
      "name": "Sharp Shooter",
      "description": "Score 90% or higher on 10 quizzes",
      "badge_icon_url": "/badges/sharp_shooter.svg",
      "xp_reward": 750
    }
  ]
}
```

**Errors**:
- `401 Unauthorized` - Not logged in
- `422 Unprocessable Entity` - Invalid request data

**File**: `backend/app/api/v1/quiz_routes.py`

---

### GET /quiz/history
Get user's quiz attempt history.

**Authentication**: Required (JWT)

**Query Parameters**:
- `limit` (optional, default=20): Number of attempts to return
- `offset` (optional, default=0): Pagination offset
- `exam_type` (optional): Filter by exam type

**Example**:
```
GET /quiz/history?limit=10&exam_type=security_plus
```

**Response** (200 OK):
```json
{
  "attempts": [
    {
      "id": 456,
      "exam_type": "security_plus",
      "total_questions": 30,
      "correct_answers": 28,
      "score_percentage": 93.33,
      "xp_earned": 420,
      "time_taken_seconds": 1800,
      "completed_at": "2025-01-15T14:32:10Z"
    },
    {
      "id": 455,
      "exam_type": "security_plus",
      "total_questions": 30,
      "correct_answers": 25,
      "score_percentage": 83.33,
      "xp_earned": 312,
      "time_taken_seconds": 1650,
      "completed_at": "2025-01-14T10:15:42Z"
    }
  ],
  "total": 87,
  "limit": 10,
  "offset": 0
}
```

**File**: `backend/app/api/v1/quiz_routes.py`

---

### GET /quiz/stats
Get aggregated quiz statistics.

**Authentication**: Required (JWT)

**Response** (200 OK):
```json
{
  "total_attempts": 87,
  "total_questions_answered": 2610,
  "average_score": 87.5,
  "best_score": 100.0,
  "total_xp_earned": 28450,
  "stats_by_exam": {
    "security_plus": {
      "attempts": 45,
      "questions_answered": 1350,
      "average_score": 89.2,
      "best_score": 100.0,
      "xp_earned": 15200
    },
    "network_plus": {
      "attempts": 30,
      "questions_answered": 900,
      "average_score": 85.1,
      "best_score": 96.67,
      "xp_earned": 10100
    },
    "a_plus_core_1": {
      "attempts": 12,
      "questions_answered": 360,
      "average_score": 86.3,
      "best_score": 93.33,
      "xp_earned": 3150
    }
  }
}
```

**File**: `backend/app/api/v1/quiz_routes.py`

---

### GET /quiz/attempt/{attempt_id}
Get detailed quiz attempt including all answers.

**Authentication**: Required (JWT, must own the attempt)

**Response** (200 OK):
```json
{
  "id": 456,
  "exam_type": "security_plus",
  "total_questions": 30,
  "correct_answers": 28,
  "score_percentage": 93.33,
  "xp_earned": 420,
  "time_taken_seconds": 1800,
  "completed_at": "2025-01-15T14:32:10Z",
  "answers": [
    {
      "id": 1001,
      "question_id": 123,
      "user_answer": "A",
      "correct_answer": "A",
      "is_correct": true,
      "time_spent_seconds": 45
    }
  ]
}
```

**Errors**:
- `404 Not Found` - Attempt not found or doesn't belong to user

**File**: `backend/app/api/v1/quiz_routes.py`

---

## Achievement Endpoints

### GET /achievements
Get all public (non-hidden) achievements.

**Authentication**: None

**Response** (200 OK):
```json
{
  "achievements": [
    {
      "id": 1,
      "name": "First Steps",
      "description": "Complete your first quiz",
      "badge_icon_url": "/badges/first_steps.svg",
      "criteria_type": "quiz_completed",
      "criteria_value": 1,
      "xp_reward": 50,
      "is_hidden": false
    }
  ]
}
```

**File**: `backend/app/api/v1/achievement_routes.py`

---

### GET /achievements/me
Get all achievements with user's progress.

**Authentication**: Required (JWT)

**Response** (200 OK):
```json
{
  "achievements": [
    {
      "id": 1,
      "name": "First Steps",
      "description": "Complete your first quiz",
      "badge_icon_url": "/badges/first_steps.svg",
      "criteria_type": "quiz_completed",
      "criteria_value": 1,
      "xp_reward": 50,
      "is_earned": true,
      "is_hidden": false,
      "progress": 1,
      "progress_percentage": 100.0
    },
    {
      "id": 7,
      "name": "Sharp Shooter",
      "description": "Score 90% or higher on 10 quizzes",
      "badge_icon_url": "/badges/sharp_shooter.svg",
      "criteria_type": "high_score_quiz",
      "criteria_value": 10,
      "xp_reward": 750,
      "is_earned": false,
      "is_hidden": false,
      "progress": 7,
      "progress_percentage": 70.0
    }
  ]
}
```

**Note**: Hidden achievements only shown if earned

**File**: `backend/app/api/v1/achievement_routes.py`

---

### GET /achievements/earned
Get only user's earned achievements.

**Authentication**: Required (JWT)

**Response** (200 OK):
```json
{
  "achievements": [
    {
      "id": 1,
      "name": "First Steps",
      "description": "Complete your first quiz",
      "badge_icon_url": "/badges/first_steps.svg",
      "xp_reward": 50,
      "earned_at": "2025-01-10T08:15:22Z"
    },
    {
      "id": 4,
      "name": "Perfect Score",
      "description": "Get 100% on any quiz",
      "badge_icon_url": "/badges/perfect_score.svg",
      "xp_reward": 150,
      "earned_at": "2025-01-12T14:42:33Z"
    }
  ],
  "total_earned": 12,
  "total_available": 27
}
```

**File**: `backend/app/api/v1/achievement_routes.py`

---

### GET /achievements/stats
Get user's achievement statistics.

**Authentication**: Required (JWT)

**Response** (200 OK):
```json
{
  "total_achievements": 27,
  "earned_achievements": 12,
  "completion_percentage": 44.44,
  "total_xp_from_achievements": 3550,
  "hidden_achievements_earned": 1,
  "categories": {
    "Getting Started": { "earned": 3, "total": 3 },
    "Accuracy": { "earned": 2, "total": 4 },
    "Question Milestones": { "earned": 2, "total": 4 },
    "Study Streaks": { "earned": 2, "total": 4 },
    "Exam-Specific": { "earned": 2, "total": 8 },
    "Level": { "earned": 1, "total": 4 }
  }
}
```

**File**: `backend/app/api/v1/achievement_routes.py`

---

## Avatar Endpoints

### GET /avatars
Get all public avatars.

**Authentication**: None

**Response** (200 OK):
```json
{
  "avatars": [
    {
      "id": 1,
      "name": "Default Student",
      "description": "The starting avatar for all new students",
      "image_url": "/avatars/default_student.png",
      "is_default": true,
      "rarity": "common",
      "required_achievement_id": null
    }
  ]
}
```

**File**: `backend/app/api/v1/avatar_routes.py`

---

### GET /avatars/me
Get all avatars with user's unlock status.

**Authentication**: Required (JWT)

**Response** (200 OK):
```json
{
  "avatars": [
    {
      "id": 1,
      "name": "Default Student",
      "description": "The starting avatar for all new students",
      "image_url": "/avatars/default_student.png",
      "is_default": true,
      "rarity": "common",
      "required_achievement_id": null,
      "is_unlocked": true,
      "unlocked_at": "2025-01-10T08:00:15Z",
      "is_equipped": false
    },
    {
      "id": 7,
      "name": "Accuracy Expert",
      "description": "Awarded for consistently high scores",
      "image_url": "/avatars/accuracy_expert.png",
      "is_default": false,
      "rarity": "epic",
      "required_achievement_id": 7,
      "is_unlocked": false,
      "unlocked_at": null,
      "is_equipped": false
    }
  ]
}
```

**File**: `backend/app/api/v1/avatar_routes.py`

---

### GET /avatars/unlocked
Get only user's unlocked avatars.

**Authentication**: Required (JWT)

**Response** (200 OK):
```json
{
  "avatars": [
    {
      "id": 1,
      "name": "Default Student",
      "image_url": "/avatars/default_student.png",
      "rarity": "common",
      "unlocked_at": "2025-01-10T08:00:15Z",
      "is_equipped": false
    },
    {
      "id": 4,
      "name": "Quiz Champion",
      "image_url": "/avatars/quiz_champion.png",
      "rarity": "rare",
      "unlocked_at": "2025-01-10T09:23:45Z",
      "is_equipped": true
    }
  ],
  "total_unlocked": 5,
  "total_available": 18
}
```

**File**: `backend/app/api/v1/avatar_routes.py`

---

### POST /avatars/select
Equip an avatar (set as selected_avatar_id).

**Authentication**: Required (JWT)

**Request Body**:
```json
{
  "avatar_id": 4
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Avatar equipped successfully",
  "selected_avatar": {
    "id": 4,
    "name": "Quiz Champion",
    "image_url": "/avatars/quiz_champion.png",
    "rarity": "rare"
  }
}
```

**Errors**:
- `400 Bad Request` - Avatar not unlocked
- `404 Not Found` - Avatar doesn't exist

**File**: `backend/app/api/v1/avatar_routes.py`

---

### GET /avatars/stats
Get user's avatar collection statistics.

**Authentication**: Required (JWT)

**Response** (200 OK):
```json
{
  "total_avatars": 18,
  "unlocked_avatars": 5,
  "collection_percentage": 27.78,
  "by_rarity": {
    "common": { "unlocked": 3, "total": 3 },
    "rare": { "unlocked": 2, "total": 3 },
    "epic": { "unlocked": 0, "total": 7 },
    "legendary": { "unlocked": 0, "total": 5 }
  },
  "selected_avatar_id": 4
}
```

**File**: `backend/app/api/v1/avatar_routes.py`

---

## Leaderboard Endpoints

### GET /leaderboard/xp
Get top users by total XP.

**Authentication**: None

**Query Parameters**:
- `limit` (optional, default=100): Number of entries (1-100)

**Response** (200 OK):
```json
{
  "leaderboard": [
    {
      "rank": 1,
      "user_id": 42,
      "username": "QuizMaster99",
      "xp": 28450,
      "level": 18,
      "selected_avatar_id": 14
    },
    {
      "rank": 2,
      "user_id": 17,
      "username": "StudyPro",
      "xp": 22100,
      "level": 16,
      "selected_avatar_id": 7
    }
  ],
  "total_entries": 100
}
```

**File**: `backend/app/api/v1/leaderboard_routes.py`

---

### GET /leaderboard/quiz-count
Get top users by total quiz count.

**Authentication**: None

**Query Parameters**:
- `limit` (optional, default=100)

**Response** (200 OK):
```json
{
  "leaderboard": [
    {
      "rank": 1,
      "user_id": 42,
      "username": "QuizMaster99",
      "quiz_count": 187,
      "xp": 28450,
      "level": 18,
      "selected_avatar_id": 14
    }
  ]
}
```

**File**: `backend/app/api/v1/leaderboard_routes.py`

---

### GET /leaderboard/accuracy
Get top users by average quiz accuracy (minimum 10 quizzes).

**Authentication**: None

**Query Parameters**:
- `limit` (optional, default=100)

**Response** (200 OK):
```json
{
  "leaderboard": [
    {
      "rank": 1,
      "user_id": 42,
      "username": "QuizMaster99",
      "average_accuracy": 94.5,
      "quiz_count": 187,
      "xp": 28450,
      "level": 18,
      "selected_avatar_id": 14
    }
  ],
  "minimum_quizzes": 10
}
```

**File**: `backend/app/api/v1/leaderboard_routes.py`

---

### GET /leaderboard/streak
Get top users by current study streak.

**Authentication**: None

**Query Parameters**:
- `limit` (optional, default=100)

**Response** (200 OK):
```json
{
  "leaderboard": [
    {
      "rank": 1,
      "user_id": 42,
      "username": "QuizMaster99",
      "study_streak_current": 45,
      "study_streak_longest": 52,
      "xp": 28450,
      "level": 18,
      "selected_avatar_id": 14
    }
  ]
}
```

**File**: `backend/app/api/v1/leaderboard_routes.py`

---

### GET /leaderboard/exam/{exam_type}
Get top users for a specific exam by average score (minimum 5 quizzes).

**Authentication**: None

**Path Parameters**:
- `exam_type`: "a_plus_core_1", "a_plus_core_2", "network_plus", "security_plus"

**Query Parameters**:
- `limit` (optional, default=100)

**Example**:
```
GET /leaderboard/exam/security_plus?limit=50
```

**Response** (200 OK):
```json
{
  "exam_type": "security_plus",
  "leaderboard": [
    {
      "rank": 1,
      "user_id": 42,
      "username": "QuizMaster99",
      "quiz_count": 87,
      "average_score": 92.3,
      "xp": 28450,
      "level": 18,
      "selected_avatar_id": 14
    }
  ],
  "minimum_quizzes": 5
}
```

**Errors**:
- `400 Bad Request` - Invalid exam_type

**File**: `backend/app/api/v1/leaderboard_routes.py`

---

## Common Error Responses

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 403 Forbidden
```json
{
  "detail": "Account disabled"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 422 Unprocessable Entity
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```
