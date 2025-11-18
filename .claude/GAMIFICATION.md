# Gamification System

## Overview
Comprehensive gamification system for the CompTIA quiz app with 4 main systems:
1. **XP & Leveling** - Earn experience points and level up
2. **Achievements** - 27 unlockable achievements across 9 categories
3. **Avatars** - 18 collectible avatars (3 default, 15 achievement-locked)
4. **Leaderboards** - 5 different leaderboard types

---

## 1. XP & Leveling System

### XP Calculation
**Formula**: Base XP + Accuracy Bonus

```python
def calculate_xp_earned(correct_answers: int, total_questions: int) -> int:
    # Base XP: 10 XP per correct answer
    base_xp = correct_answers * 10

    # Calculate accuracy percentage
    accuracy = (correct_answers / total_questions) * 100

    # Accuracy bonus multipliers
    if accuracy >= 90:
        bonus_multiplier = 1.5   # +50% bonus
    elif accuracy >= 80:
        bonus_multiplier = 1.25  # +25% bonus
    elif accuracy >= 70:
        bonus_multiplier = 1.10  # +10% bonus
    else:
        bonus_multiplier = 1.0   # No bonus

    total_xp = int(base_xp * bonus_multiplier)
    return total_xp
```

**Examples**:
- 20/30 correct (66.7%) → 200 XP (no bonus)
- 25/30 correct (83.3%) → 250 * 1.25 = 312 XP (+25% bonus)
- 30/30 correct (100%) → 300 * 1.5 = 450 XP (+50% bonus)

### Level Progression
**Formula**: `level = floor(sqrt(xp / 100)) + 1`

This creates gradually increasing XP requirements:

| Level | XP Required | Total XP | XP to Next Level |
|-------|-------------|----------|------------------|
| 1 | 0-99 | 0 | 100 |
| 2 | 100-399 | 100 | 300 |
| 3 | 400-899 | 400 | 500 |
| 4 | 900-1599 | 900 | 700 |
| 5 | 1600-2499 | 1600 | 900 |
| 10 | 8100-10099 | 8100 | 2000 |
| 20 | 36100-40099 | 36100 | 4000 |
| 50 | 240100-250099 | 240100 | 10000 |

**Service**: `backend/app/services/quiz_service.py:calculate_level_from_xp()`

### XP Sources
1. **Quiz Completion** - Base XP from correct answers
2. **Achievement Unlocks** - Bonus XP rewards (50-5000 XP per achievement)

---

## 2. Achievement System

### Achievement Categories

#### Getting Started Achievements
| Name | Criteria | XP Reward | Hidden |
|------|----------|-----------|--------|
| First Steps | Complete 1 quiz | 50 | No |
| Beginner | Complete 5 quizzes | 100 | No |
| Quick Learner | Complete 10 quizzes | 200 | No |

#### Accuracy Achievements
| Name | Criteria | XP Reward | Hidden |
|------|----------|-----------|--------|
| Perfect Score | Get 100% on 1 quiz | 150 | No |
| Perfectionist | Get 100% on 5 quizzes | 500 | No |
| Flawless | Get 100% on 10 quizzes | 1000 | Yes |
| Sharp Shooter | Get 90%+ on 10 quizzes | 750 | No |

#### Question Milestone Achievements
| Name | Criteria | XP Reward | Hidden |
|------|----------|-----------|--------|
| Question Rookie | Answer 100 questions correctly | 200 | No |
| Question Master | Answer 500 questions correctly | 750 | No |
| Quiz Veteran | Answer 1000 questions correctly | 1500 | No |
| Quiz Legend | Answer 2500 questions correctly | 3000 | Yes |

#### Study Streak Achievements
| Name | Criteria | XP Reward | Hidden |
|------|----------|-----------|--------|
| Getting Started | Maintain 3-day streak | 150 | No |
| Week Warrior | Maintain 7-day streak | 400 | No |
| Dedicated Student | Maintain 14-day streak | 800 | No |
| Month Master | Maintain 30-day streak | 2000 | Yes |

#### Exam-Specific Achievements (A+ Core 1)
| Name | Criteria | XP Reward | Hidden |
|------|----------|-----------|--------|
| A+ Core 1 Beginner | Complete 10 A+ Core 1 quizzes | 300 | No |
| A+ Core 1 Expert | Complete 50 A+ Core 1 quizzes | 1000 | No |

#### Exam-Specific Achievements (A+ Core 2)
| Name | Criteria | XP Reward | Hidden |
|------|----------|-----------|--------|
| A+ Core 2 Beginner | Complete 10 A+ Core 2 quizzes | 300 | No |
| A+ Core 2 Expert | Complete 50 A+ Core 2 quizzes | 1000 | No |

#### Exam-Specific Achievements (Network+)
| Name | Criteria | XP Reward | Hidden |
|------|----------|-----------|--------|
| Network+ Beginner | Complete 10 Network+ quizzes | 300 | No |
| Network+ Pro | Complete 50 Network+ quizzes | 1000 | No |

#### Exam-Specific Achievements (Security+)
| Name | Criteria | XP Reward | Hidden |
|------|----------|-----------|--------|
| Security+ Beginner | Complete 10 Security+ quizzes | 300 | No |
| Security+ Specialist | Complete 50 Security+ quizzes | 1000 | No |

#### Level Achievements
| Name | Criteria | XP Reward | Hidden |
|------|----------|-----------|--------|
| Level 5 | Reach Level 5 | 250 | No |
| Level 10 | Reach Level 10 | 500 | No |
| Level 20 | Reach Level 20 | 1000 | Yes |
| Level 50 | Reach Level 50 | 5000 | Yes |

**Total**: 27 achievements

### Achievement Criteria Types

```python
CRITERIA_TYPES = {
    "quiz_completed": "Complete N quizzes",
    "perfect_quiz": "Get 100% on N quizzes",
    "high_score_quiz": "Get 90%+ on N quizzes",
    "correct_answers": "Answer N questions correctly",
    "study_streak": "Maintain N-day streak",
    "level_reached": "Reach level N",
    "exam_specific": "Complete N quizzes of specific exam type"
}
```

### Achievement Checking Logic

**When**: After every quiz submission

**Process**:
1. `quiz_controller.submit_quiz()` calls `achievement_service.check_and_award_achievements()`
2. Get user's current stats (total quizzes, perfect quizzes, correct answers, streak, level, exam counts)
3. Get all achievements (ordered by display_order)
4. Get already-earned achievement IDs
5. For each unearned achievement:
   - Check if criteria is met
   - If yes: Award achievement, add XP, recalculate level, auto-unlock avatar (if linked)
6. Commit all changes atomically
7. Return list of newly unlocked achievements

**Service**: `backend/app/services/achievement_service.py:check_and_award_achievements()`

### Hidden Achievements
Hidden achievements are not visible until earned:
- Flawless (10 perfect quizzes)
- Quiz Legend (2500 correct answers)
- Month Master (30-day streak)
- Level 20
- Level 50

**API Behavior**:
- `GET /api/v1/achievements` - Excludes hidden achievements (public view)
- `GET /api/v1/achievements/me` - Shows hidden achievements ONLY if earned

---

## 3. Avatar System

### Avatar Tiers

#### Common (3 avatars) - Default
Available to all users immediately upon signup:
1. **Default Student** - "The starting avatar for all new students"
2. **Tech Enthusiast** - "A tech-savvy learner ready to conquer CompTIA exams"
3. **Study Buddy** - "Your friendly study companion"

#### Rare (3 avatars)
Unlocked through basic achievements:
4. **Quiz Champion** - Unlock: "First Steps" achievement
5. **Perfect Scholar** - Unlock: "Perfect Score" achievement
6. **Dedicated Learner** - Unlock: "Week Warrior" achievement

#### Epic (7 avatars)
Unlocked through mid-tier achievements:
7. **Accuracy Expert** - Unlock: "Sharp Shooter" achievement
8. **Knowledge Seeker** - Unlock: "Question Master" achievement
9. **Streak Master** - Unlock: "Dedicated Student" achievement
10. **A+ Core 1 Master** - Unlock: "A+ Core 1 Expert" achievement
11. **A+ Core 2 Master** - Unlock: "A+ Core 2 Expert" achievement
12. **Network Ninja** - Unlock: "Network+ Pro" achievement
13. **Security Sentinel** - Unlock: "Security+ Specialist" achievement

#### Legendary (5 avatars)
Unlocked through elite achievements:
14. **CompTIA Prodigy** - Unlock: "Level 20" achievement
15. **Perfectionist Elite** - Unlock: "Flawless" achievement
16. **Quiz Legend** - Unlock: "Quiz Legend" achievement
17. **Month Champion** - Unlock: "Month Master" achievement
18. **CompTIA Grandmaster** - Unlock: "Level 50" achievement (ultimate)

**Total**: 18 avatars

### Avatar Unlock Logic

**Default Avatars** (is_default=True):
- Auto-unlocked when user signs up
- Inserted into `user_avatars` table during signup flow

**Achievement Avatars** (required_achievement_id set):
- Auto-unlocked when achievement is earned
- `achievement_service.check_and_award_achievements()` calls `avatar_service.unlock_avatar_from_achievement()`
- Inserted into `user_avatars` table

**Service**: `backend/app/services/avatar_service.py`

### Avatar Selection
Users can equip one avatar at a time:
- `POST /api/v1/avatars/select` - Equip avatar
- Updates `user_profiles.selected_avatar_id`
- Only allows equipping unlocked avatars (validation check)

---

## 4. Leaderboard System

### Leaderboard Types

#### 1. XP Leaderboard
**Endpoint**: `GET /api/v1/leaderboard/xp?limit=100`

**Query**:
```sql
SELECT
    u.id,
    u.username,
    up.xp,
    up.level,
    up.selected_avatar_id,
    RANK() OVER (ORDER BY up.xp DESC) as rank
FROM users u
JOIN user_profiles up ON u.id = up.user_id
ORDER BY up.xp DESC
LIMIT 100;
```

**Returns**: Top users by total XP

---

#### 2. Quiz Count Leaderboard
**Endpoint**: `GET /api/v1/leaderboard/quiz-count?limit=100`

**Query**:
```sql
SELECT
    u.id,
    u.username,
    up.xp,
    up.level,
    up.selected_avatar_id,
    COUNT(qa.id) as quiz_count,
    RANK() OVER (ORDER BY COUNT(qa.id) DESC) as rank
FROM users u
JOIN user_profiles up ON u.id = up.user_id
LEFT JOIN quiz_attempts qa ON u.id = qa.user_id
GROUP BY u.id, u.username, up.xp, up.level, up.selected_avatar_id
ORDER BY quiz_count DESC
LIMIT 100;
```

**Returns**: Top users by total quizzes completed

---

#### 3. Accuracy Leaderboard
**Endpoint**: `GET /api/v1/leaderboard/accuracy?limit=100`

**Query**:
```sql
SELECT
    u.id,
    u.username,
    up.xp,
    up.level,
    up.selected_avatar_id,
    AVG(qa.score_percentage) as average_accuracy,
    COUNT(qa.id) as quiz_count,
    RANK() OVER (ORDER BY AVG(qa.score_percentage) DESC) as rank
FROM users u
JOIN user_profiles up ON u.id = up.user_id
JOIN quiz_attempts qa ON u.id = qa.user_id
GROUP BY u.id, u.username, up.xp, up.level, up.selected_avatar_id
HAVING COUNT(qa.id) >= 10  -- Minimum 10 quizzes for fairness
ORDER BY average_accuracy DESC
LIMIT 100;
```

**Returns**: Top users by average quiz accuracy (min 10 quizzes)

---

#### 4. Streak Leaderboard
**Endpoint**: `GET /api/v1/leaderboard/streak?limit=100`

**Query**:
```sql
SELECT
    u.id,
    u.username,
    up.xp,
    up.level,
    up.selected_avatar_id,
    up.study_streak_current,
    up.study_streak_longest,
    RANK() OVER (ORDER BY up.study_streak_current DESC) as rank
FROM users u
JOIN user_profiles up ON u.id = up.user_id
WHERE up.study_streak_current > 0
ORDER BY up.study_streak_current DESC
LIMIT 100;
```

**Returns**: Top users by current study streak

---

#### 5. Exam-Specific Leaderboard
**Endpoint**: `GET /api/v1/leaderboard/exam/{exam_type}?limit=100`

**Example**: `GET /api/v1/leaderboard/exam/security_plus?limit=100`

**Query**:
```sql
SELECT
    u.id,
    u.username,
    up.xp,
    up.level,
    up.selected_avatar_id,
    COUNT(qa.id) as quiz_count,
    AVG(qa.score_percentage) as average_score,
    RANK() OVER (ORDER BY AVG(qa.score_percentage) DESC) as rank
FROM users u
JOIN user_profiles up ON u.id = up.user_id
JOIN quiz_attempts qa ON u.id = qa.user_id
WHERE qa.exam_type = 'security_plus'
GROUP BY u.id, u.username, up.xp, up.level, up.selected_avatar_id
HAVING COUNT(qa.id) >= 5  -- Minimum 5 quizzes for that exam
ORDER BY average_score DESC
LIMIT 100;
```

**Supported Exam Types**:
- `a_plus_core_1`
- `a_plus_core_2`
- `network_plus`
- `security_plus`

**Returns**: Top users for specific exam by average score (min 5 quizzes)

---

**Service**: `backend/app/services/leaderboard_service.py`

---

## Gamification Flow Diagram

### Quiz Submission → Gamification Pipeline

```
┌─────────────────────────┐
│ User submits quiz       │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────┐
│ quiz_service.submit_quiz()                          │
│ 1. Create QuizAttempt record                        │
│ 2. Bulk create UserAnswer records                   │
│ 3. Calculate XP earned (base + accuracy bonus)      │
│ 4. Update UserProfile (XP, level, counters)         │
│ 5. Return (quiz_attempt, xp_earned, level, level_up)│
└───────────┬─────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────┐
│ achievement_service.check_and_award_achievements()  │
│ 1. Get user stats (quizzes, accuracy, streak, etc.) │
│ 2. For each unearned achievement:                   │
│    - Check if criteria met                          │
│    - If yes:                                        │
│      • Award achievement                            │
│      • Add XP reward                                │
│      • Recalculate level                            │
│      • Auto-unlock avatar (if linked)               │
│ 3. Return newly_unlocked[]                          │
└───────────┬─────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────┐
│ Return to client:       │
│ {                       │
│   quiz_attempt: {...},  │
│   xp_earned: 450,       │
│   new_level: 5,         │
│   level_up: true,       │
│   achievements: [...]   │
│ }                       │
└─────────────────────────┘
```

---

## Database Triggers & Auto-Actions

### Signup Flow
1. User creates account → `users` table
2. Auto-create `user_profiles` (XP=0, Level=1)
3. Auto-unlock default avatars (3 common avatars)

### Quiz Submission Flow
1. Create `quiz_attempts` record
2. Bulk create `user_answers` records
3. Update `user_profiles` (XP, level, counters)
4. Check achievements → Award if criteria met → Add to `user_achievements`
5. If achievement unlocks avatar → Add to `user_avatars`

### Achievement Unlock Flow
1. Achievement earned → Insert into `user_achievements`
2. Add XP reward → Update `user_profiles.xp`
3. Recalculate level → Update `user_profiles.level`
4. If achievement has `unlocks_avatar_id` → Insert into `user_avatars`

---

## API Response Examples

### Quiz Submission Response
```json
{
  "quiz_attempt": {
    "id": 123,
    "exam_type": "security_plus",
    "total_questions": 30,
    "correct_answers": 28,
    "score_percentage": 93.33,
    "xp_earned": 420,
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

### Achievement Progress Response
```json
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
```

### Leaderboard Entry
```json
{
  "rank": 1,
  "user_id": 42,
  "username": "QuizMaster99",
  "xp": 15420,
  "level": 15,
  "selected_avatar_id": 14,
  "quiz_count": 87,
  "average_accuracy": 91.5
}
```

---

## Future Enhancements

### Potential Additions
1. **Daily Challenges** - Special achievements for daily goals
2. **Limited-Time Events** - Seasonal achievements
3. **Title System** - Unlockable titles based on achievements
4. **Badge Display** - Show multiple badges on profile (not just avatar)
5. **Weekly Leaderboards** - Reset every Monday
6. **Clan/Guild System** - Team-based challenges
7. **Achievement Points** - Separate from XP, for weighted achievement difficulty
8. **Prestige System** - Reset level for special rewards after level 50
