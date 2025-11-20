# Achievement & XP System Migration Guide

This guide walks you through migrating from the old complex achievement system (27 achievements with rarity tiers) to the new simplified system (15 achievements with clean progression).

---

## Overview of Changes

### System Simplification

**From:** 27 achievements with rarity tiers, hidden achievements, complex display ordering
**To:** 15 achievements organized into 4 clear progression tiers

### Database Changes

#### Achievement Model
**Removed fields:**
- `rarity` - No more common/rare/epic/legendary tiers
- `is_hidden` - All achievements are now visible
- `display_order` - Achievements ordered by ID naturally
- `badge_icon_url` - Replaced with simple `icon` emoji field
- `unlocks_avatar_id` - Avatar unlocking now works in reverse (avatars point to achievements)

**Kept fields:**
- `id`, `name`, `description`, `icon`
- `criteria_type`, `criteria_value`, `criteria_exam_type`
- `xp_reward`, `created_at`

#### Avatar Model
**Removed fields:**
- `rarity` - No more rarity tiers for avatars
- `is_default` - Default status now determined by `required_achievement_id == NULL`
- `display_order` - Avatars ordered by ID naturally

**Kept fields:**
- `id`, `name`, `description`, `image_url`
- `required_achievement_id`, `created_at`

---

## Migration Steps

### Step 1: Backup Your Database

**CRITICAL:** Before making any changes, backup your database!

```bash
# PostgreSQL backup
pg_dump -U your_user -d your_database > backup_before_migration.sql

# Or use your preferred backup method
```

### Step 2: Run the Database Migration

```bash
cd backend
alembic upgrade head
```

This will:
- Remove deprecated fields from `achievements` table
- Remove deprecated fields from `avatars` table
- Keep all user achievement/avatar unlock data intact

### Step 3: Clear Old Achievement & Avatar Data

Since the achievement structure has fundamentally changed, you'll need to clear the old data:

```sql
-- Clear old data (OPTIONAL - only if you want a fresh start)
TRUNCATE user_achievements CASCADE;
TRUNCATE user_avatars CASCADE;
TRUNCATE achievements CASCADE;
TRUNCATE avatars CASCADE;
```

**Note:** If you skip this step, old achievements will remain but may not work correctly with the new system.

### Step 4: Seed New Achievements

```bash
cd backend
python -m app.db.seed_achievements_v2
```

Expected output:
```
✅ Successfully seeded 15 achievements!

📊 Achievement Breakdown by Tier:
  - Tier 1 (Getting Started):  4 achievements
  - Tier 2 (Competence):       5 achievements
  - Tier 3 (Mastery):          4 achievements
  - Tier 4 (Elite):            2 achievements

🎯 Total: 15 achievements
```

### Step 5: Seed New Avatars

```bash
cd backend
python -m app.db.seed_avatars_v2
```

Expected output:
```
✅ Successfully seeded 15 avatars!

📊 Avatar Breakdown:
  - Default (unlocked on signup):    3 avatars
  - Achievement-locked:              12 avatars

🎯 Total: 15 avatars
```

---

## New Achievement Structure

### Tier 1: Getting Started (4 achievements)
Early wins to engage new users

| Achievement | Criteria | XP |
|------------|----------|-----|
| Welcome Aboard | Verify email | 50 |
| First Steps | Complete 1 quiz | 100 |
| Building Momentum | Complete 3 quizzes | 200 |
| Quiz Regular | Complete 5 quizzes | 300 |

### Tier 2: Competence (5 achievements)
Showing skill and consistency

| Achievement | Criteria | XP |
|------------|----------|-----|
| Perfect Score | Get 100% on 1 quiz | 500 |
| Domain Focus | Complete 10 quizzes in one exam type | 600 |
| Quiz Veteran | Complete 25 total quizzes | 800 |
| Accuracy Pro | Get 90%+ on 5 quizzes | 700 |
| Correct Streak | Answer 100 questions correctly | 400 |

### Tier 3: Mastery (4 achievements)
Deep commitment and expertise

| Achievement | Criteria | XP |
|------------|----------|-----|
| Quiz Master | Complete 50 total quizzes | 1500 |
| Perfectionist | Get 100% on 5 quizzes | 1200 |
| Knowledge Bank | Answer 500 questions correctly | 1000 |
| Multi-Domain Expert | Complete 10+ quizzes in 2+ exam types | 1500 |

### Tier 4: Elite (2 achievements)
Ultimate endgame goals

| Achievement | Criteria | XP |
|------------|----------|-----|
| Century Club | Complete 100 total quizzes | 3000 |
| Quiz Legend | Reach Level 50 | 5000 |

---

## New Avatar System

### Default Avatars (3)
Unlocked automatically on signup:
- Default Student
- Tech Enthusiast
- Study Buddy

### Achievement-Locked Avatars (12)
One for each major achievement:
- Verified Scholar (Welcome Aboard)
- Quiz Starter (First Steps)
- Perfect Student (Perfect Score)
- Domain Specialist (Domain Focus)
- Veteran Learner (Quiz Veteran)
- Accuracy Expert (Accuracy Pro)
- Quiz Master (Quiz Master achievement)
- Flawless Performer (Perfectionist)
- Knowledge Sage (Knowledge Bank)
- Renaissance Scholar (Multi-Domain Expert)
- Century Champion (Century Club)
- Legendary Master (Quiz Legend)

---

## Criteria Types Reference

### Supported Criteria Types

1. **email_verified** - User has verified their email
2. **quiz_completed** - Total quizzes completed across all exam types
3. **perfect_quiz** - Quizzes with 100% score
4. **high_score_quiz** - Quizzes with 90%+ score
5. **correct_answers** - Total correct answers over lifetime
6. **level_reached** - User has reached specific level
7. **exam_specific** - Completed N quizzes in any single exam type
8. **multi_domain** - Completed 10+ quizzes in at least 2 different exam types

### Removed Criteria Types

- **study_streak** - Removed (streaks not being auto-updated)

---

## XP System (Unchanged)

The XP and leveling formulas remain the same:

### XP Calculation
```python
base_xp = 10 * correct_answers

# Apply accuracy bonus
if score_percentage == 100:
    bonus = 1.5x
elif score_percentage >= 90:
    bonus = 1.25x
elif score_percentage >= 75:
    bonus = 1.10x
else:
    bonus = 1.0x

total_xp = int(base_xp * bonus)
```

### Level Calculation
```python
level = floor(sqrt(total_xp / 100)) + 1
```

This makes reaching Level 50 achievable and realistic.

---

## API Changes

### Achievement Endpoints

**Before:**
```json
{
  "id": 1,
  "name": "First Steps",
  "badge_icon_url": "/badges/first_steps.svg",
  "rarity": "common",
  "is_hidden": false,
  "display_order": 1
}
```

**After:**
```json
{
  "id": 1,
  "name": "First Steps",
  "icon": "🎯",
  "criteria_type": "quiz_completed",
  "criteria_value": 1
}
```

### Avatar Endpoints

**Before:**
```json
{
  "id": 1,
  "name": "Default Student",
  "rarity": "common",
  "is_default": true,
  "display_order": 0
}
```

**After:**
```json
{
  "id": 1,
  "name": "Default Student",
  "is_default": true,  // Computed from required_achievement_id == NULL
  "required_achievement_id": null
}
```

---

## Testing the Migration

### 1. Test User Signup
```bash
# Create new user
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "TestPass123!"
  }'

# Verify 3 default avatars were unlocked
curl -X GET http://localhost:8000/api/v1/avatars \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 2. Test Email Verification
```bash
# Verify email
curl -X POST http://localhost:8000/api/v1/auth/verify-email \
  -H "Content-Type: application/json" \
  -d '{"token": "VERIFICATION_TOKEN"}'

# Check for "Welcome Aboard" achievement
curl -X GET http://localhost:8000/api/v1/achievements/user \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. Test Quiz Submission
```bash
# Submit a quiz
curl -X POST http://localhost:8000/api/v1/quiz/submit \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "exam_type": "security_plus",
    "total_questions": 10,
    "answers": [...]
  }'

# Check for "First Steps" achievement
```

---

## Rollback Procedure

If you need to rollback the migration:

```bash
# Rollback the database migration
alembic downgrade -1

# Restore from backup
psql -U your_user -d your_database < backup_before_migration.sql
```

**Note:** This will restore the old schema but not your code changes. You'll need to revert code changes separately.

---

## FAQ

### Q: What happens to existing user achievements?
**A:** User achievement unlocks (`user_achievements` table) are preserved during migration. However, if the old achievements are removed, users will keep their unlock records but won't see those achievements in the UI.

### Q: Will users lose their XP and levels?
**A:** No! User profiles (`user_profiles` table) are not modified. All XP, levels, and statistics are preserved.

### Q: Can I customize the achievement list?
**A:** Yes! Edit `backend/app/db/seed_achievements_v2.py` before running the seed script. You can modify names, descriptions, criteria, and XP rewards.

### Q: How do I add new exam types?
**A:** The system automatically handles any exam type. Just ensure your quiz submission includes the exam type (e.g., `"cloud_plus"`, `"linux_plus"`).

---

## Support

If you encounter issues during migration:

1. **Check logs:** Review backend application logs for errors
2. **Verify database:** Ensure all migrations ran successfully with `alembic history`
3. **Test endpoints:** Use the testing steps above to verify functionality
4. **Restore backup:** If needed, rollback and restore from backup

---

## Summary

The new achievement system is:
- ✅ **Simpler**: 15 achievements vs. 27
- ✅ **Cleaner**: No rarity tiers, hidden achievements, or complex ordering
- ✅ **Clearer**: 4 distinct progression tiers
- ✅ **More maintainable**: Less complexity in code and database
- ✅ **Achievable**: Realistic progression curve from beginner to elite

The migration preserves user progress while simplifying the system for better UX and easier maintenance.
