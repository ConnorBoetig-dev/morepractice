# Data Models

Complete reference for all data structures used in the API.

## User Models

### User
```typescript
interface User {
  id: number;
  email: string;
  username: string;
  is_active: boolean;
  is_verified: boolean;
  is_admin: boolean;
  created_at: string; // ISO 8601 UTC
  updated_at: string; // ISO 8601 UTC
}
```

**Example:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "is_active": true,
  "is_verified": true,
  "is_admin": false,
  "created_at": "2025-01-20T10:00:00Z",
  "updated_at": "2025-01-20T10:00:00Z"
}
```

---

### ProfileResponse
Returned by `GET /api/v1/auth/me` - combines user data with profile/gamification stats.

```typescript
interface ProfileResponse {
  // User fields
  id: number;
  email: string;
  username: string;
  is_active: boolean;
  is_verified: boolean;
  is_admin: boolean;
  created_at: string; // ISO 8601 UTC

  // Profile customization
  bio: string | null;  // User biography (max 500 chars)
  avatar_url: string | null;  // Profile picture URL
  selected_avatar_id: number | null;  // Currently equipped avatar ID

  // Gamification: XP & Level
  xp: number;  // Total experience points
  level: number;  // Current level (calculated from XP)

  // Gamification: Streaks
  study_streak_current: number;  // Current consecutive study days
  study_streak_longest: number;  // Personal record (highest streak)

  // Stats
  total_exams_taken: number;  // Lifetime quiz count
  total_questions_answered: number;  // Lifetime question count
  last_activity_date: string | null;  // ISO 8601 date (YYYY-MM-DD)
}
```

**Example:**
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

---

### UpdateProfileRequest
Used for `PATCH /api/v1/auth/profile` - all fields optional.

```typescript
interface UpdateProfileRequest {
  username?: string;  // New username (3-50 chars, alphanumeric + _ -)
  email?: string;  // New email (requires re-verification)
  bio?: string;  // New bio (max 500 chars)
}
```

**Example:**
```json
{
  "username": "newusername",
  "bio": "Updated bio text"
}
```

---

## Authentication Models

### TokenResponse
```typescript
interface TokenResponse {
  success: boolean;
  access_token: string;
  refresh_token: string;
  token_type: string; // "bearer"
  user: User;
}
```

**Example:**
```json
{
  "success": true,
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "johndoe"
  }
}
```

---

### SignupRequest
```typescript
interface SignupRequest {
  email: string; // Valid email format
  username: string; // 3-50 characters
  password: string; // Min 8 chars, 1 uppercase, 1 lowercase, 1 number, 1 special
}
```

---

### LoginRequest
```typescript
interface LoginRequest {
  email: string;
  password: string;
}
```

---

## Question Models

### Question
```typescript
interface Question {
  id: number;
  question_id: string; // Unique identifier (e.g., "SEC001")
  exam_type: string; // "security", "network", etc.
  domain: string; // "1.1", "2.3", etc.
  question_text: string;
  options: {
    [key: string]: QuestionOption; // "A", "B", "C", "D"
  };
  correct_answer: string; // "A", "B", "C", or "D"
  created_at: string;
  updated_at: string;
}
```

**Example:**
```json
{
  "id": 123,
  "question_id": "SEC001",
  "exam_type": "security",
  "domain": "1.1",
  "question_text": "What is the primary purpose of encryption?",
  "options": {
    "A": {
      "text": "To compress data",
      "explanation": "Incorrect. Compression reduces size, not security."
    },
    "B": {
      "text": "To protect confidentiality",
      "explanation": "Correct. Encryption ensures data cannot be read by unauthorized parties."
    },
    "C": {
      "text": "To delete data",
      "explanation": "Incorrect. Deletion removes data, encryption protects it."
    },
    "D": {
      "text": "To backup data",
      "explanation": "Incorrect. Backups create copies, encryption protects data."
    }
  },
  "correct_answer": "B",
  "created_at": "2025-01-15T10:00:00Z",
  "updated_at": "2025-01-15T10:00:00Z"
}
```

---

### QuestionOption
```typescript
interface QuestionOption {
  text: string; // The option text
  explanation: string; // Why this option is correct/incorrect
}
```

---

### ExamInfo
```typescript
interface ExamInfo {
  exam_type: string;
  display_name: string;
  total_questions: number;
}
```

**Example:**
```json
{
  "exam_type": "security",
  "display_name": "Security+",
  "total_questions": 450
}
```

---

## Bookmark Models

### Bookmark
```typescript
interface Bookmark {
  id: number;
  user_id: number;
  question_id: number;
  notes: string | null;
  created_at: string;
  updated_at: string;
  question?: Question; // Included in some responses
}
```

**Example:**
```json
{
  "id": 1,
  "user_id": 1,
  "question_id": 123,
  "notes": "Review this - tricky encryption question",
  "created_at": "2025-01-20T14:30:00Z",
  "updated_at": "2025-01-20T14:30:00Z",
  "question": {
    "id": 123,
    "question_text": "What is...",
    "exam_type": "security",
    "domain": "1.1"
  }
}
```

---

### BookmarkRequest
```typescript
interface BookmarkRequest {
  notes?: string | null; // Optional notes
}
```

---

### BookmarksListResponse
```typescript
interface BookmarksListResponse {
  success: boolean;
  bookmarks: Bookmark[];
  pagination: PaginationInfo;
}
```

---

## Quiz Models

### QuizSubmissionRequest
```typescript
interface QuizSubmissionRequest {
  exam_type: string;
  answers: UserAnswer[];
  time_spent_seconds: number;
}
```

**Example:**
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

---

### UserAnswer
```typescript
interface UserAnswer {
  question_id: number;
  selected_answer: string; // "A", "B", "C", "D"
}
```

---

### QuizAttempt
```typescript
interface QuizAttempt {
  id: number;
  user_id: number;
  exam_type: string;
  score: number; // Percentage (0-100)
  total_questions: number;
  correct_answers: number;
  time_spent_seconds: number;
  xp_earned: number;
  created_at: string;
}
```

**Example:**
```json
{
  "id": 1,
  "user_id": 1,
  "exam_type": "security",
  "score": 85.5,
  "total_questions": 30,
  "correct_answers": 26,
  "time_spent_seconds": 1800,
  "xp_earned": 100,
  "created_at": "2025-01-20T14:30:00Z"
}
```

---

### QuizResult
```typescript
interface QuizResult {
  question_id: number;
  selected_answer: string;
  correct_answer: string;
  is_correct: boolean;
  explanation?: string; // Explanation from the question option
}
```

---

### QuizStats
```typescript
interface QuizStats {
  total_attempts: number;
  average_score: number;
  total_xp: number;
  by_exam_type: {
    [exam_type: string]: {
      attempts: number;
      average_score: number;
    };
  };
}
```

**Example:**
```json
{
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
```

---

## Achievement Models

### Achievement
```typescript
interface Achievement {
  id: number;
  name: string;
  description: string;
  icon: string;
  xp_reward: number;
  requirement_type: string; // "quiz_count", "score_average", "streak", etc.
  requirement_value: number;
  created_at: string;
}
```

**Example:**
```json
{
  "id": 1,
  "name": "First Steps",
  "description": "Complete your first quiz",
  "icon": "trophy",
  "xp_reward": 50,
  "requirement_type": "quiz_count",
  "requirement_value": 1,
  "created_at": "2025-01-15T10:00:00Z"
}
```

---

### UserAchievement
```typescript
interface UserAchievement {
  user_id: number;
  achievement_id: number;
  earned_at: string;
  achievement?: Achievement; // Included in some responses
}
```

---

## Avatar Models

### Avatar
```typescript
interface Avatar {
  id: number;
  name: string;
  image_url: string;
  unlock_requirement_type: string; // "default", "xp", "achievement", "streak"
  unlock_requirement_value: number;
  is_premium: boolean;
}
```

**Example:**
```json
{
  "id": 1,
  "name": "Rookie",
  "image_url": "/avatars/rookie.png",
  "unlock_requirement_type": "default",
  "unlock_requirement_value": 0,
  "is_premium": false
}
```

---

## Leaderboard Models

### LeaderboardEntry
```typescript
interface LeaderboardEntry {
  rank: number;
  user_id: number;
  username: string;
  total_xp?: number;
  total_quizzes?: number;
  average_score?: number;
  current_streak?: number;
  avatar_url?: string;
}
```

**Example:**
```json
{
  "rank": 1,
  "user_id": 5,
  "username": "johndoe",
  "total_xp": 5000,
  "level": 15,
  "avatar_url": "/avatars/master.png"
}
```

---

## Pagination Models

### PaginationInfo
```typescript
interface PaginationInfo {
  page: number; // Current page (1-indexed)
  page_size: number; // Items per page
  total_items: number; // Total items across all pages
  total_pages: number; // Total number of pages
}
```

**Example:**
```json
{
  "page": 1,
  "page_size": 10,
  "total_items": 45,
  "total_pages": 5
}
```

---

## Error Models

### ErrorResponse
```typescript
interface ErrorResponse {
  success: false;
  error: {
    message: string; // Human-readable error message
    code: string; // Machine-readable error code
  };
  status_code: number;
  timestamp: string;
  path: string;
}
```

**Example:**
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

---

### ValidationErrorResponse
```typescript
interface ValidationErrorResponse {
  success: false;
  errors: ValidationError[];
  status_code: 422;
  timestamp: string;
  path: string;
}

interface ValidationError {
  field: string; // e.g., "body.email", "query.page"
  message: string;
  code: "VALIDATION_ERROR";
}
```

**Example:**
```json
{
  "success": false,
  "errors": [
    {
      "field": "body.email",
      "message": "field required",
      "code": "VALIDATION_ERROR"
    },
    {
      "field": "body.password",
      "message": "ensure this value has at least 8 characters",
      "code": "VALIDATION_ERROR"
    }
  ],
  "status_code": 422,
  "timestamp": "2025-01-20T14:30:00Z",
  "path": "/api/v1/auth/signup"
}
```

---

## Common Response Patterns

### Success Response (Generic)
```typescript
interface SuccessResponse<T> {
  success: true;
  data?: T;
  message?: string;
}
```

### List Response (Paginated)
```typescript
interface ListResponse<T> {
  success: true;
  items: T[]; // Or specific name like "bookmarks", "questions", etc.
  pagination: PaginationInfo;
}
```

### Message Response
```typescript
interface MessageResponse {
  success: true;
  message: string;
}
```

**Example:**
```json
{
  "success": true,
  "message": "Bookmark removed successfully"
}
```

---

## TypeScript Type Definitions

Here's a complete TypeScript definition file you can use:

```typescript
// types/api.ts

// ============================================
// User Types
// ============================================
export interface User {
  id: number;
  email: string;
  username: string;
  is_active: boolean;
  is_verified: boolean;
  is_admin: boolean;
  created_at: string;
  updated_at: string;
}

// ============================================
// Auth Types
// ============================================
export interface TokenResponse {
  success: boolean;
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface SignupRequest {
  email: string;
  username: string;
  password: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

// ============================================
// Question Types
// ============================================
export interface QuestionOption {
  text: string;
  explanation: string;
}

export interface Question {
  id: number;
  question_id: string;
  exam_type: string;
  domain: string;
  question_text: string;
  options: Record<string, QuestionOption>;
  correct_answer: string;
  created_at: string;
  updated_at: string;
}

// ============================================
// Bookmark Types
// ============================================
export interface Bookmark {
  id: number;
  user_id: number;
  question_id: number;
  notes: string | null;
  created_at: string;
  updated_at: string;
  question?: Question;
}

// ============================================
// Quiz Types
// ============================================
export interface QuizSubmissionRequest {
  exam_type: string;
  answers: UserAnswer[];
  time_spent_seconds: number;
}

export interface UserAnswer {
  question_id: number;
  selected_answer: string;
}

export interface QuizAttempt {
  id: number;
  user_id: number;
  exam_type: string;
  score: number;
  total_questions: number;
  correct_answers: number;
  time_spent_seconds: number;
  xp_earned: number;
  created_at: string;
}

// ============================================
// Error Types
// ============================================
export interface ErrorResponse {
  success: false;
  error: {
    message: string;
    code: string;
  };
  status_code: number;
  timestamp: string;
  path: string;
}

export interface ValidationErrorResponse {
  success: false;
  errors: ValidationError[];
  status_code: 422;
  timestamp: string;
  path: string;
}

export interface ValidationError {
  field: string;
  message: string;
  code: "VALIDATION_ERROR";
}

// ============================================
// Pagination Types
// ============================================
export interface PaginationInfo {
  page: number;
  page_size: number;
  total_items: number;
  total_pages: number;
}
```

## Next Steps

- **[Integration Guide](./06-integration-guide.md)** - See these models in action with complete examples
