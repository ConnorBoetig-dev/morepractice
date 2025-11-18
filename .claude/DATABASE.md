# Database Schema

## Overview
PostgreSQL database with 8 tables organized into 3 main systems:
1. **User Management** (2 tables): users, user_profiles
2. **Question Bank** (1 table): questions
3. **Gamification System** (6 tables): quiz_attempts, user_answers, achievements, user_achievements, avatars, user_avatars

All models use SQLAlchemy ORM with foreign key constraints, CHECK constraints, and strategic indexes.

---

## Table Relationships

```
┌──────────────┐
│    users     │
└──────┬───────┘
       │ 1
       │
       │ 1
┌──────┴───────────┐
│  user_profiles   │◄─────┐
└──────┬───────────┘      │
       │ 1                │ selected_avatar_id
       │                  │
       │ *                │
┌──────┴───────────┐      │
│  quiz_attempts   │      │
└──────┬───────────┘      │
       │ 1                │
       │                  │
       │ *                │
┌──────┴───────────┐      │
│   user_answers   │      │
└──────────────────┘      │
                          │
┌──────────────┐          │
│ achievements │          │
└──────┬───────┘          │
       │ *                │
       │                  │
       │ *                │
┌──────┴────────────┐     │
│ user_achievements │     │
└───────────────────┘     │
                          │
┌──────────────┐          │
│   avatars    │──────────┘
└──────┬───────┘
       │ *
       │
       │ *
┌──────┴────────┐
│  user_avatars │
└───────────────┘

┌──────────────┐
│  questions   │
└──────────────┘
```

---

## Tables

### 1. users
**Purpose**: User accounts and authentication

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO INCREMENT | User ID |
| email | STRING | UNIQUE, NOT NULL, INDEXED | Login email |
| username | STRING | UNIQUE, NOT NULL, INDEXED | Display name |
| hashed_password | STRING | NOT NULL | Bcrypt password hash |
| is_active | BOOLEAN | DEFAULT TRUE | Account enabled/disabled |
| is_verified | BOOLEAN | DEFAULT FALSE | Email verification status |
| created_at | DATETIME | DEFAULT NOW | Account creation timestamp |
| updated_at | DATETIME | DEFAULT NOW, ON UPDATE NOW | Last update timestamp |

**Indexes**:
- `id` (primary key)
- `email` (unique)
- `username` (unique)

**File**: `backend/app/models/user.py`

---

### 2. user_profiles
**Purpose**: User gamification stats and profile customization

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| user_id | INTEGER | PRIMARY KEY, FOREIGN KEY(users.id) | Links to users table |
| bio | TEXT | NULLABLE | User biography |
| avatar_url | STRING | NULLABLE | Profile picture URL |
| selected_avatar_id | INTEGER | FOREIGN KEY(avatars.id), NULLABLE | Currently equipped avatar |
| xp | INTEGER | DEFAULT 0, NOT NULL | Total experience points |
| level | INTEGER | DEFAULT 1, NOT NULL | Current level (calculated from XP) |
| study_streak_current | INTEGER | DEFAULT 0 | Current consecutive study days |
| study_streak_longest | INTEGER | DEFAULT 0 | Personal best streak |
| total_exams_taken | INTEGER | DEFAULT 0 | Lifetime quiz count |
| total_questions_answered | INTEGER | DEFAULT 0 | Lifetime question count |
| last_activity_date | DATE | NULLABLE | Last quiz date (for streak tracking) |
| created_at | DATETIME | DEFAULT NOW | Profile creation timestamp |

**Relationships**:
- One-to-one with `users` (user_id is both PK and FK)
- Many-to-one with `avatars` (selected_avatar_id)

**File**: `backend/app/models/user.py`

---

### 3. questions
**Purpose**: CompTIA exam question bank

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO INCREMENT | Question ID |
| question_id | STRING | INDEXED | External ID from CSV |
| exam_type | STRING | INDEXED | "security", "network", "a1101", "a1102" |
| domain | STRING | INDEXED | CompTIA domain (e.g., "1.1", "2.3") |
| question_text | TEXT | NOT NULL | The question |
| correct_answer | STRING | NOT NULL | Letter: "A", "B", "C", or "D" |
| options | JSON | NOT NULL | Answer choices with explanations |
| created_at | DATETIME | DEFAULT NOW | Import timestamp |

**Options JSON Structure**:
```json
{
  "A": {"text": "First option", "explanation": "Why correct/incorrect"},
  "B": {"text": "Second option", "explanation": "Why correct/incorrect"},
  "C": {"text": "Third option", "explanation": "Why correct/incorrect"},
  "D": {"text": "Fourth option", "explanation": "Why correct/incorrect"}
}
```

**Indexes**:
- `id` (primary key)
- `question_id`
- `exam_type`
- `domain`

**File**: `backend/app/models/question.py`

---

### 4. quiz_attempts
**Purpose**: Tracks each completed quiz session

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO INCREMENT | Attempt ID |
| user_id | INTEGER | FOREIGN KEY(users.id) ON DELETE CASCADE, INDEXED | User who took quiz |
| exam_type | STRING | NOT NULL, INDEXED | Exam type taken |
| total_questions | INTEGER | NOT NULL, CHECK > 0 | Number of questions in quiz |
| correct_answers | INTEGER | NOT NULL, CHECK >= 0 | Number answered correctly |
| score_percentage | FLOAT | NOT NULL, CHECK 0-100 | (correct/total) * 100 |
| time_taken_seconds | INTEGER | NULLABLE, CHECK >= 0 | Total time spent |
| xp_earned | INTEGER | NOT NULL, DEFAULT 0, CHECK >= 0 | XP awarded |
| completed_at | DATETIME | NOT NULL, DEFAULT NOW, INDEXED | Completion timestamp |

**CHECK Constraints**:
- `total_questions > 0`
- `correct_answers >= 0`
- `correct_answers <= total_questions`
- `score_percentage >= 0 AND score_percentage <= 100`
- `time_taken_seconds >= 0`
- `xp_earned >= 0`

**Composite Indexes**:
- `(exam_type, score_percentage, completed_at)` - Leaderboard queries
- `(user_id, completed_at)` - User history

**Relationships**:
- Many-to-one with `users` (CASCADE delete)
- One-to-many with `user_answers`

**File**: `backend/app/models/gamification.py`

---

### 5. user_answers
**Purpose**: Tracks individual question answers for each quiz attempt

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO INCREMENT | Answer ID |
| user_id | INTEGER | FOREIGN KEY(users.id) ON DELETE CASCADE, INDEXED | User who answered |
| quiz_attempt_id | INTEGER | FOREIGN KEY(quiz_attempts.id) ON DELETE CASCADE, INDEXED | Parent quiz attempt |
| question_id | INTEGER | FOREIGN KEY(questions.id) ON DELETE SET NULL, INDEXED | Question answered |
| user_answer | STRING(1) | NOT NULL, CHECK IN ('A','B','C','D') | User's selected answer |
| correct_answer | STRING(1) | NOT NULL, CHECK IN ('A','B','C','D') | Correct answer |
| is_correct | BOOLEAN | NOT NULL, INDEXED | Whether answer was correct |
| time_spent_seconds | INTEGER | NULLABLE, CHECK >= 0 | Time on this question |
| answered_at | DATETIME | DEFAULT NOW | Answer timestamp |

**CHECK Constraints**:
- `user_answer IN ('A', 'B', 'C', 'D')`
- `correct_answer IN ('A', 'B', 'C', 'D')`
- `time_spent_seconds >= 0`

**Composite Indexes**:
- `(user_id, is_correct)` - User performance analytics
- `(quiz_attempt_id, is_correct)` - Quiz review
- `(question_id, is_correct)` - Question difficulty analysis

**Relationships**:
- Many-to-one with `users` (CASCADE delete)
- Many-to-one with `quiz_attempts` (CASCADE delete with orphan removal)
- Many-to-one with `questions` (SET NULL on delete)

**File**: `backend/app/models/gamification.py`

---

### 6. achievements
**Purpose**: Defines available achievements users can unlock

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO INCREMENT | Achievement ID |
| name | STRING | NOT NULL, UNIQUE | Achievement name |
| description | TEXT | NOT NULL | What it's for |
| badge_icon_url | STRING | NULLABLE | Badge image path |
| criteria_type | STRING | NOT NULL, INDEXED | Type of achievement (see below) |
| criteria_value | INTEGER | NOT NULL, CHECK > 0 | Target value to unlock |
| xp_reward | INTEGER | NOT NULL, DEFAULT 0, CHECK >= 0 | XP awarded on unlock |
| unlocks_avatar_id | INTEGER | FOREIGN KEY(avatars.id) ON DELETE SET NULL | Avatar unlocked (if any) |
| display_order | INTEGER | DEFAULT 0 | UI sort order |
| is_hidden | BOOLEAN | DEFAULT FALSE | Secret achievement |
| created_at | DATETIME | DEFAULT NOW | Creation timestamp |

**Criteria Types**:
- `quiz_completed` - Complete N quizzes
- `perfect_quiz` - Get 100% on N quizzes
- `high_score_quiz` - Get 90%+ on N quizzes
- `correct_answers` - Answer N questions correctly
- `study_streak` - Maintain N-day streak
- `level_reached` - Reach level N
- `exam_specific` - Complete N quizzes of specific exam type

**CHECK Constraints**:
- `criteria_value > 0`
- `xp_reward >= 0`

**Indexes**:
- `id` (primary key)
- `name` (unique)
- `criteria_type`

**Relationships**:
- One-to-many with `user_achievements`
- One-to-one with `avatars` (optional unlock)

**File**: `backend/app/models/gamification.py`

**Seed Data**: `backend/app/db/seed_achievements.py` (27 achievements)

---

### 7. user_achievements
**Purpose**: Many-to-many relationship tracking which achievements users have unlocked

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| user_id | INTEGER | PRIMARY KEY, FOREIGN KEY(users.id) ON DELETE CASCADE, INDEXED | User who earned it |
| achievement_id | INTEGER | PRIMARY KEY, FOREIGN KEY(achievements.id) ON DELETE CASCADE, INDEXED | Achievement earned |
| earned_at | DATETIME | NOT NULL, DEFAULT NOW, INDEXED | When it was earned |
| progress_value | INTEGER | NULLABLE | Progress tracking (future use) |

**Composite Primary Key**: `(user_id, achievement_id)` - Prevents duplicate awards

**Composite Indexes**:
- `(user_id, earned_at)` - User's achievement history sorted by date

**Relationships**:
- Many-to-one with `users` (CASCADE delete)
- Many-to-one with `achievements` (CASCADE delete)

**File**: `backend/app/models/gamification.py`

---

### 8. avatars
**Purpose**: Defines available avatars users can unlock and display

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO INCREMENT | Avatar ID |
| name | STRING | NOT NULL, UNIQUE | Avatar name |
| description | TEXT | NULLABLE | How to unlock |
| image_url | STRING | NOT NULL | Avatar image path |
| is_default | BOOLEAN | DEFAULT FALSE | Available to all users |
| required_achievement_id | INTEGER | FOREIGN KEY(achievements.id) ON DELETE SET NULL | Achievement required (if any) |
| rarity | STRING | NULLABLE | "common", "rare", "epic", "legendary" |
| display_order | INTEGER | DEFAULT 0 | UI sort order |
| created_at | DATETIME | DEFAULT NOW | Creation timestamp |

**Rarity Tiers**:
- `common` - Default avatars (3 total)
- `rare` - Basic achievement avatars (3 total)
- `epic` - Mid-tier achievement avatars (7 total)
- `legendary` - Elite achievement avatars (5 total)

**Relationships**:
- One-to-many with `user_avatars`
- Many-to-one with `achievements` (optional requirement)

**File**: `backend/app/models/gamification.py`

**Seed Data**: `backend/app/db/seed_avatars.py` (18 avatars)

---

### 9. user_avatars
**Purpose**: Many-to-many relationship tracking which avatars users have unlocked

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| user_id | INTEGER | PRIMARY KEY, FOREIGN KEY(users.id) ON DELETE CASCADE, INDEXED | User who unlocked it |
| avatar_id | INTEGER | PRIMARY KEY, FOREIGN KEY(avatars.id) ON DELETE CASCADE, INDEXED | Avatar unlocked |
| unlocked_at | DATETIME | NOT NULL, DEFAULT NOW | When it was unlocked |

**Composite Primary Key**: `(user_id, avatar_id)` - Prevents duplicate unlocks

**Composite Indexes**:
- `(user_id, unlocked_at)` - User's avatar collection sorted by unlock date

**Relationships**:
- Many-to-one with `users` (CASCADE delete)
- Many-to-one with `avatars` (CASCADE delete)

**File**: `backend/app/models/gamification.py`

---

## Migrations

### Current Migrations
1. **Initial Migration**: Creates all 8 tables
   - File: `backend/alembic/versions/ee7ad33dca0c_add_gamification_system_quiz_tracking_.py`
   - Adds: quiz_attempts, user_answers, achievements, user_achievements, avatars, user_avatars

### Running Migrations
```bash
cd backend

# Generate new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```

---

## Seed Data

### Seeding Achievements
```bash
cd backend
python -m app.db.seed_achievements
```

Creates 27 achievements across 9 categories:
- Getting Started (3)
- Accuracy (4)
- Question Milestones (4)
- Study Streaks (4)
- A+ Core 1 (2)
- A+ Core 2 (2)
- Network+ (2)
- Security+ (2)
- Levels (4)

### Seeding Avatars
```bash
cd backend
python -m app.db.seed_avatars
```

Creates 18 avatars:
- Common (3) - Default avatars
- Rare (3) - Basic achievement unlocks
- Epic (7) - Mid-tier unlocks
- Legendary (5) - Elite unlocks

---

## Database Management

### Docker Commands
```bash
# Start PostgreSQL
docker-compose up -d postgres

# Stop PostgreSQL
docker-compose stop postgres

# View logs
docker logs billings-postgres

# Connect to PostgreSQL CLI
docker exec -it billings-postgres psql -U billings_user -d billings
```

### PostgreSQL Commands
```sql
-- List all tables
\dt

-- Describe table structure
\d users
\d quiz_attempts

-- View table data
SELECT * FROM users;
SELECT * FROM achievements;

-- Count records
SELECT COUNT(*) FROM quiz_attempts;

-- Check foreign key constraints
SELECT conname, conrelid::regclass, confrelid::regclass
FROM pg_constraint
WHERE contype = 'f';
```

---

## Performance Considerations

### Optimized Queries
1. **Leaderboards**: Use window functions (RANK, DENSE_RANK) with composite indexes
2. **User Stats**: Use aggregations (COUNT, SUM, AVG) with GROUP BY
3. **Achievement Checking**: Single query to get all user stats, then check in Python

### Index Strategy
- Foreign keys are indexed (user_id, achievement_id, etc.)
- Common filter columns are indexed (exam_type, completed_at)
- Composite indexes for multi-column queries (user_id + completed_at)

### Bulk Operations
- Quiz submission uses `bulk_save_objects()` for UserAnswer records
- Significantly faster than individual inserts
