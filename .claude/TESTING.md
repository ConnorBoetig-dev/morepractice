# Testing Strategy

## Overview
Comprehensive testing setup for the CompTIA quiz application using pytest with a PostgreSQL test database.

---

## Test Database Setup

### Configuration
**File**: `backend/pytest.ini`

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --strict-markers
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow tests
```

### Test Database
- **Separate database**: `billings_test` (never use production DB)
- **Setup/Teardown**: Each test gets a clean database
- **Fixtures**: Reusable test data (users, achievements, avatars)

**Environment**:
Create `backend/.env.test`:
```bash
DATABASE_URL=postgresql://billings_user:billings_password@localhost:5432/billings_test
JWT_SECRET=test_secret_key_for_testing_only_32chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
```

### Creating Test Database
```bash
# Connect to PostgreSQL
docker exec -it billings-postgres psql -U billings_user -d billings

# Create test database
CREATE DATABASE billings_test;
\q
```

---

## Test Structure

```
backend/tests/
├── conftest.py                        # pytest fixtures
├── fixtures/
│   ├── database.py                    # DB setup/teardown
│   ├── users.py                       # User factories
│   ├── achievements.py                # Achievement test data
│   └── avatars.py                     # Avatar test data
├── unit/
│   ├── services/
│   │   ├── test_quiz_service.py       # XP calculation, level logic
│   │   ├── test_achievement_service.py # Achievement checking
│   │   ├── test_avatar_service.py     # Avatar unlocking
│   │   └── test_leaderboard_service.py # Leaderboard queries
│   ├── models/
│   │   ├── test_user_models.py        # User model validation
│   │   └── test_gamification_models.py # Gamification model constraints
│   └── schemas/
│       ├── test_quiz_schemas.py       # Quiz schema validation
│       └── test_achievement_schemas.py # Achievement schema validation
└── integration/
    ├── api/
    │   ├── test_auth_routes.py        # Signup, login, me
    │   ├── test_quiz_routes.py        # Quiz submission, history
    │   ├── test_achievement_routes.py # Achievement endpoints
    │   ├── test_avatar_routes.py      # Avatar endpoints
    │   └── test_leaderboard_routes.py # Leaderboard endpoints
    └── gamification/
        ├── test_quiz_to_achievement.py # Quiz → Achievement flow
        ├── test_achievement_to_avatar.py # Achievement → Avatar unlock
        └── test_level_up_flow.py      # XP → Level up → Achievement
```

---

## Test Categories

### Unit Tests
**Marker**: `@pytest.mark.unit`

**Purpose**: Test individual functions in isolation
- No database queries (use mocks)
- Fast execution
- Test business logic only

**Examples**:

```python
# tests/unit/services/test_quiz_service.py
import pytest
from app.services.quiz_service import calculate_xp_earned, calculate_level_from_xp

@pytest.mark.unit
class TestXPCalculation:
    def test_base_xp_no_bonus(self):
        """Test XP calculation with <70% accuracy (no bonus)"""
        xp = calculate_xp_earned(correct_answers=20, total_questions=30, exam_type="security_plus")
        assert xp == 200  # 20 * 10 * 1.0

    def test_xp_with_70_percent_bonus(self):
        """Test XP calculation with 70-79% accuracy (+10% bonus)"""
        xp = calculate_xp_earned(correct_answers=22, total_questions=30, exam_type="security_plus")
        assert xp == 242  # 22 * 10 * 1.1

    def test_xp_with_80_percent_bonus(self):
        """Test XP calculation with 80-89% accuracy (+25% bonus)"""
        xp = calculate_xp_earned(correct_answers=25, total_questions=30, exam_type="security_plus")
        assert xp == 312  # 25 * 10 * 1.25

    def test_xp_with_90_percent_bonus(self):
        """Test XP calculation with 90%+ accuracy (+50% bonus)"""
        xp = calculate_xp_earned(correct_answers=28, total_questions=30, exam_type="security_plus")
        assert xp == 420  # 28 * 10 * 1.5

    def test_perfect_score_bonus(self):
        """Test XP calculation with 100% accuracy"""
        xp = calculate_xp_earned(correct_answers=30, total_questions=30, exam_type="security_plus")
        assert xp == 450  # 30 * 10 * 1.5


@pytest.mark.unit
class TestLevelCalculation:
    def test_level_1_at_zero_xp(self):
        assert calculate_level_from_xp(0) == 1

    def test_level_1_at_99_xp(self):
        assert calculate_level_from_xp(99) == 1

    def test_level_2_at_100_xp(self):
        assert calculate_level_from_xp(100) == 2

    def test_level_5_at_1600_xp(self):
        assert calculate_level_from_xp(1600) == 5

    def test_level_10_at_8100_xp(self):
        assert calculate_level_from_xp(8100) == 10

    def test_negative_xp_returns_level_1(self):
        assert calculate_level_from_xp(-100) == 1
```

---

### Integration Tests
**Marker**: `@pytest.mark.integration`

**Purpose**: Test complete workflows with database
- Real database queries
- Test API endpoints end-to-end
- Test service interactions

**Examples**:

```python
# tests/integration/api/test_quiz_routes.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.mark.integration
class TestQuizSubmission:
    def test_submit_quiz_success(self, test_db, test_user, auth_headers):
        """Test successful quiz submission"""
        payload = {
            "exam_type": "security_plus",
            "total_questions": 10,
            "time_taken_seconds": 600,
            "answers": [
                {
                    "question_id": 1,
                    "user_answer": "A",
                    "correct_answer": "A",
                    "is_correct": True,
                    "time_spent_seconds": 60
                }
                # ... 9 more answers
            ]
        }

        response = client.post("/api/v1/quiz/submit", json=payload, headers=auth_headers)

        assert response.status_code == 201
        data = response.json()
        assert "quiz_attempt" in data
        assert "xp_earned" in data
        assert "new_level" in data
        assert "level_up" in data
        assert "achievements_unlocked" in data

    def test_submit_quiz_unlocks_first_steps_achievement(self, test_db, test_user, auth_headers):
        """Test that first quiz unlocks 'First Steps' achievement"""
        # User has 0 quizzes
        payload = create_quiz_payload(correct=10, total=10)

        response = client.post("/api/v1/quiz/submit", json=payload, headers=auth_headers)

        data = response.json()
        achievements = data["achievements_unlocked"]

        # Should unlock "First Steps" achievement
        assert len(achievements) > 0
        assert any(a["name"] == "First Steps" for a in achievements)

    def test_quiz_history_pagination(self, test_db, test_user_with_quizzes, auth_headers):
        """Test quiz history with pagination"""
        response = client.get("/api/v1/quiz/history?limit=5&offset=0", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data["attempts"]) <= 5
        assert "total" in data
        assert "limit" in data
        assert "offset" in data
```

---

```python
# tests/integration/gamification/test_quiz_to_achievement.py
import pytest
from app.services import quiz_service, achievement_service

@pytest.mark.integration
class TestQuizToAchievementFlow:
    def test_first_quiz_unlocks_achievement(self, test_db, test_user):
        """Test that completing first quiz unlocks 'First Steps' achievement"""
        user_id = test_user.id

        # Submit first quiz
        submission = create_quiz_submission(correct=25, total=30)
        quiz_attempt, xp, level, level_up = quiz_service.submit_quiz(test_db, user_id, submission)

        # Check achievements
        unlocked = achievement_service.check_and_award_achievements(test_db, user_id)

        # Should unlock "First Steps"
        assert len(unlocked) > 0
        assert any(a.name == "First Steps" for a in unlocked)

    def test_10_quizzes_unlocks_quick_learner(self, test_db, test_user):
        """Test that 10 quizzes unlocks 'Quick Learner' achievement"""
        user_id = test_user.id

        # Submit 9 quizzes (no unlock yet)
        for _ in range(9):
            submission = create_quiz_submission(correct=20, total=30)
            quiz_service.submit_quiz(test_db, user_id, submission)
            test_db.commit()

        # Check achievements (should not have Quick Learner yet)
        unlocked = achievement_service.check_and_award_achievements(test_db, user_id)
        assert not any(a.name == "Quick Learner" for a in unlocked)

        # Submit 10th quiz
        submission = create_quiz_submission(correct=20, total=30)
        quiz_service.submit_quiz(test_db, user_id, submission)
        test_db.commit()

        # Check achievements (should unlock Quick Learner)
        unlocked = achievement_service.check_and_award_achievements(test_db, user_id)
        assert any(a.name == "Quick Learner" for a in unlocked)

    def test_perfect_score_unlocks_achievement(self, test_db, test_user):
        """Test that 100% score unlocks 'Perfect Score' achievement"""
        user_id = test_user.id

        # Submit perfect quiz
        submission = create_quiz_submission(correct=30, total=30)
        quiz_service.submit_quiz(test_db, user_id, submission)

        unlocked = achievement_service.check_and_award_achievements(test_db, user_id)

        assert any(a.name == "Perfect Score" for a in unlocked)
```

---

## Test Fixtures

### Database Fixtures

```python
# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.models.user import User, UserProfile
from app.models.gamification import Achievement, Avatar
from app.db.seed_achievements import seed_achievements
from app.db.seed_avatars import seed_avatars
import os

# Test database URL
TEST_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://billings_user:billings_password@localhost:5432/billings_test")

@pytest.fixture(scope="session")
def test_engine():
    """Create test database engine"""
    engine = create_engine(TEST_DATABASE_URL)
    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def test_db(test_engine):
    """Create clean database for each test"""
    # Create all tables
    Base.metadata.create_all(bind=test_engine)

    # Create session
    TestingSessionLocal = sessionmaker(bind=test_engine)
    db = TestingSessionLocal()

    # Seed achievements and avatars
    seed_achievements(db)
    seed_avatars(db)
    db.commit()

    yield db

    # Teardown: rollback and drop all tables
    db.rollback()
    db.close()
    Base.metadata.drop_all(bind=test_engine)
```

---

### User Fixtures

```python
# tests/fixtures/users.py
import pytest
from app.models.user import User, UserProfile
from app.utils.auth import hash_password, create_access_token

@pytest.fixture
def test_user(test_db):
    """Create a test user"""
    user = User(
        email="test@example.com",
        username="TestUser",
        hashed_password=hash_password("password123"),
        is_active=True
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)

    # Create profile
    profile = UserProfile(
        user_id=user.id,
        xp=0,
        level=1
    )
    test_db.add(profile)
    test_db.commit()

    return user


@pytest.fixture
def auth_headers(test_user):
    """Create Authorization headers with JWT token"""
    token = create_access_token({"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_user_with_quizzes(test_db, test_user):
    """Create user with 20 completed quizzes"""
    from app.services.quiz_service import submit_quiz
    from app.schemas.quiz import QuizSubmission, AnswerSubmission

    for i in range(20):
        submission = QuizSubmission(
            exam_type="security_plus",
            total_questions=10,
            time_taken_seconds=600,
            answers=[
                AnswerSubmission(
                    question_id=j,
                    user_answer="A",
                    correct_answer="A",
                    is_correct=True,
                    time_spent_seconds=60
                )
                for j in range(10)
            ]
        )
        submit_quiz(test_db, test_user.id, submission)

    return test_user
```

---

## Running Tests

### Run All Tests
```bash
cd backend
pytest
```

### Run Unit Tests Only
```bash
pytest -m unit
```

### Run Integration Tests Only
```bash
pytest -m integration
```

### Run Specific Test File
```bash
pytest tests/unit/services/test_quiz_service.py
```

### Run Specific Test
```bash
pytest tests/unit/services/test_quiz_service.py::TestXPCalculation::test_perfect_score_bonus
```

### Run with Coverage
```bash
pytest --cov=app --cov-report=html
```

View coverage report:
```bash
open htmlcov/index.html
```

---

## Coverage Goals

### Target Coverage
- **Unit Tests**: 90%+ coverage of services
- **Integration Tests**: 80%+ coverage of API routes
- **Overall**: 85%+ code coverage

### Critical Areas (Must Have 100% Coverage)
1. XP calculation (`quiz_service.calculate_xp_earned`)
2. Level calculation (`quiz_service.calculate_level_from_xp`)
3. Achievement checking (`achievement_service.check_achievement_earned`)
4. Authentication (`utils.auth` functions)

---

## Test-Driven Development (TDD) Workflow

### When Adding New Features

1. **Write Test First**
   ```python
   def test_new_achievement_criteria(test_db, test_user):
       """Test that exam_specific achievements work correctly"""
       # Test implementation
       pass
   ```

2. **Run Test (Should Fail)**
   ```bash
   pytest tests/unit/services/test_achievement_service.py::test_new_achievement_criteria
   ```

3. **Implement Feature**
   - Add code to make test pass

4. **Run Test (Should Pass)**
   ```bash
   pytest tests/unit/services/test_achievement_service.py::test_new_achievement_criteria
   ```

5. **Refactor**
   - Clean up code while keeping tests green

---

## Continuous Integration (Future)

### GitHub Actions Workflow

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_USER: billings_user
          POSTGRES_PASSWORD: billings_password
          POSTGRES_DB: billings_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt

      - name: Run tests
        env:
          DATABASE_URL: postgresql://billings_user:billings_password@localhost:5432/billings_test
          JWT_SECRET: test_secret_key_32_characters_long
        run: |
          cd backend
          pytest --cov=app --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## Testing Best Practices

### ✅ Do's
- Write tests before code (TDD)
- Use descriptive test names
- Test edge cases and error conditions
- Use fixtures for reusable test data
- Mock external dependencies (e.g., time, random)
- Test one thing per test
- Use parametrize for multiple inputs

### ❌ Don'ts
- Don't test implementation details
- Don't use production database
- Don't skip teardown (clean up after tests)
- Don't write tests that depend on each other
- Don't commit failing tests
- Don't test framework code (e.g., SQLAlchemy internals)

---

## Example Test Coverage Report

```
Name                                     Stmts   Miss  Cover
------------------------------------------------------------
app/services/quiz_service.py               150      5    97%
app/services/achievement_service.py        120      8    93%
app/services/avatar_service.py              85      6    93%
app/services/leaderboard_service.py         95     12    87%
app/models/gamification.py                  80      0   100%
app/utils/auth.py                           30      0   100%
------------------------------------------------------------
TOTAL                                      560     31    94%
```
