# Testing Guide

Comprehensive testing documentation for the backend API.

## Table of Contents

- [Test Types](#test-types)
- [Running Tests](#running-tests)
- [Test Coverage](#test-coverage)
- [Writing New Tests](#writing-new-tests)
- [CI/CD Integration](#cicd-integration)

---

## Test Types

### 1. Unit Tests (`tests/unit/`)

**Purpose:** Test individual functions and classes in isolation

**Examples:**
- `test_utils_auth.py` - Authentication utility functions
- `test_auth_service.py` - Authentication service logic

**When to use:** Testing pure functions, utilities, and business logic without HTTP requests or database

---

### 2. Integration Tests (`tests/integration/`)

**Purpose:** Test complete user journeys across multiple components

**Files:**
- `test_critical_security_flows.py` - Complete authentication, quiz, admin, achievement flows (20 tests)
- `test_profile_system_flows.py` - Complete profile customization and public profile flows (14 tests)

**When to use:** Testing real user scenarios end-to-end with security validation

**Examples:**
- Signup → Verify email → Login → Access protected endpoint
- Update profile → View public profile → Verify privacy
- Submit quiz → Check XP → Verify achievements unlocked

---

### 3. API Tests (`tests/test_*.py`)

**Purpose:** Test individual API endpoints with various inputs

**Files:**
- `test_auth.py` (48KB) - Authentication endpoints (signup, login, profile, sessions, audit logs)
- `test_quiz.py` - Quiz submission and history
- `test_bookmarks.py` - Bookmark CRUD operations
- `test_study_mode.py` - Study mode workflows
- `test_achievements.py` - Achievement system
- `test_leaderboard.py` - Leaderboard rankings
- `test_admin.py` - Admin operations
- `test_avatars.py` - Avatar system
- `test_questions.py` - Question retrieval

**When to use:** Testing specific endpoints with edge cases, validation, and error handling

---

### 4. Security Tests (marked with `@pytest.mark.security`)

**Purpose:** Validate security controls and prevent vulnerabilities

**Coverage:**
- SQL injection prevention
- XSS prevention
- CSRF protection
- JWT validation
- Permission checks (admin vs user)
- Rate limiting
- Input validation
- Data privacy (email, admin status not leaked)

**Files:**
- `test_auth_security.py` - Authentication security
- `test_input_validation_security.py` - Input validation
- All integration tests include security checkpoints

---

### 5. Smoke Tests (`tests/test_smoke.py`)

**Purpose:** Verify test infrastructure is working

**Examples:**
- Database connection works
- Fixtures load correctly
- API client functions
- Test isolation (each test has clean database)

**When to use:** First test to run when setting up or debugging test environment

---

## Running Tests

### Full Test Suite

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=app --cov-report=html
```

### Run Specific Test Categories

```bash
# Run only integration tests
pytest tests/integration/ -v

# Run only security tests
pytest -m security -v

# Run only slow tests (integration)
pytest -m slow -v

# Run specific file
pytest tests/test_auth.py -v

# Run specific test
pytest tests/test_auth.py::test_signup_success -v
```

### Run with Test Database

The tests use a separate PostgreSQL database on port 5433 (not the dev database on 5432).

```bash
# Start test database (from tests directory)
cd tests
docker compose up -d

# Run tests
cd ..
pytest

# Stop test database
cd tests
docker compose down
```

---

## Test Coverage

### Current Test Count

**Total Tests:** ~150+

| Category | Tests | Purpose |
|----------|-------|---------|
| Integration Tests | 34 | End-to-end user journeys |
| API Tests | ~100 | Endpoint validation |
| Unit Tests | ~10 | Utility functions |
| Security Tests | ~40 | Security validation |
| Smoke Tests | 12 | Infrastructure checks |

### Feature Coverage

| Feature | Unit | API | Integration | Security |
|---------|------|-----|-------------|----------|
| **Authentication** | ✅ | ✅ | ✅ | ✅ |
| - Signup/Login | ✅ | ✅ | ✅ | ✅ |
| - Email Verification | ❌ | ✅ | ✅ | ✅ |
| - Password Reset | ❌ | ✅ | ✅ | ✅ |
| - Sessions | ❌ | ✅ | ✅ | ✅ |
| - Audit Logs | ❌ | ✅ | ⚠️ | ✅ |
| **Profile System** | ❌ | ✅ | ✅ | ✅ |
| - Profile Updates | ❌ | ✅ | ✅ | ✅ |
| - Bio Customization | ❌ | ✅ | ✅ | ✅ |
| - Public Profiles | ❌ | ✅ | ✅ | ✅ |
| - Privacy Controls | ❌ | ✅ | ✅ | ✅ |
| **Quiz System** | ⚠️ | ✅ | ✅ | ✅ |
| - Quiz Submission | ❌ | ✅ | ✅ | ✅ |
| - Score Calculation | ✅ | ✅ | ✅ | ✅ |
| - XP Rewards | ❌ | ✅ | ✅ | ✅ |
| **Study Mode** | ❌ | ✅ | ⚠️ | ✅ |
| **Achievements** | ❌ | ✅ | ✅ | ✅ |
| **Leaderboard** | ❌ | ✅ | ⚠️ | ✅ |
| **Bookmarks** | ❌ | ✅ | ⚠️ | ✅ |
| **Admin Operations** | ❌ | ✅ | ✅ | ✅ |
| **Rate Limiting** | ❌ | ✅ | ⚠️ | ✅ |

**Legend:**
- ✅ Comprehensive coverage
- ⚠️ Basic coverage (needs more tests)
- ❌ No coverage

---

## Writing New Tests

### Pattern for Integration Tests

Integration tests follow this pattern:

```python
@pytest.mark.security
@pytest.mark.integration
class TestCompleteFeatureFlows:
    """Test complete user journeys for [feature]"""

    def test_complete_flow_step1_to_step5(self, client, test_db):
        """
        REAL USER JOURNEY: [Brief description]
        Flow: Step 1 → Step 2 → Step 3 → Verify outcome
        """
        # Step 1: Setup (create user, data, etc.)
        user = User(...)
        test_db.add(user)
        test_db.commit()

        # Step 2: Perform action
        response = client.post("/api/v1/endpoint", json={...})
        assert response.status_code == 200

        # Step 3: Verify side effects
        test_db.refresh(user)
        assert user.field == expected_value

        # Step 4: Security checkpoint
        assert "sensitive_field" not in response.json()
```

### Pattern for API Tests

```python
def test_endpoint_specific_scenario(client, auth_headers, test_user):
    """Test [endpoint] with [specific input/scenario]"""
    # Arrange
    data = {"field": "value"}

    # Act
    response = client.post("/api/v1/endpoint", json=data, headers=auth_headers)

    # Assert
    assert response.status_code == 200
    assert response.json()["field"] == "expected"
```

### Required Tests for New Features

When adding a new feature, create tests for:

1. **Happy Path** - Feature works as expected
2. **Validation** - Invalid inputs are rejected
3. **Security** - Unauthorized access is blocked
4. **Privacy** - Sensitive data is not leaked
5. **Edge Cases** - Boundary conditions (empty, max length, etc.)
6. **Integration** - Complete user journey end-to-end

### Example: Adding a "Follow User" Feature

```python
# tests/test_follow.py (API tests)
def test_follow_user_success(client, auth_headers):
    """User can follow another user"""
    response = client.post("/api/v1/users/5/follow", headers=auth_headers)
    assert response.status_code == 201

def test_follow_self_rejected(client, auth_headers, test_user):
    """User cannot follow themselves"""
    response = client.post(f"/api/v1/users/{test_user.id}/follow", headers=auth_headers)
    assert response.status_code == 400

def test_follow_nonexistent_user_404(client, auth_headers):
    """Following nonexistent user returns 404"""
    response = client.post("/api/v1/users/99999/follow", headers=auth_headers)
    assert response.status_code == 404

# tests/integration/test_follow_system_flows.py (Integration tests)
def test_complete_follow_flow_follow_to_notification(client, test_db):
    """
    REAL USER JOURNEY: User follows another user
    Flow: User A follows User B → User B gets notification → User B's followers count increases
    """
    # Step 1: Create User A and User B
    # Step 2: User A follows User B
    # Step 3: Verify follower count increased
    # Step 4: Verify notification created
    # Step 5: Verify User A's following list includes User B
```

---

## Test Best Practices

### 1. Test Isolation

Each test should:
- Have a clean database (automatic with `test_db` fixture)
- Not depend on other tests
- Not modify global state

### 2. Descriptive Names

```python
# Good
def test_signup_with_weak_password_rejected():
    pass

# Bad
def test_signup_2():
    pass
```

### 3. Clear Assertions

```python
# Good
assert response.status_code == 422, "Weak password should be rejected with 422"
assert "password" in error_data["errors"][0]["field"]

# Bad
assert response.status_code != 200
```

### 4. Document Security Tests

```python
def test_admin_endpoint_regular_user_forbidden():
    """
    REAL SECURITY FLOW: Regular user cannot access admin endpoints
    Expected: 403 Forbidden (not 404 - that leaks endpoint existence)
    """
```

### 5. Test Security Boundaries

Always test:
- Unauthenticated access (no token)
- Authenticated wrong user (User A accessing User B's data)
- Insufficient permissions (regular user accessing admin endpoint)
- Input validation (SQL injection, XSS, length limits)
- Privacy (sensitive data not in response)

---

## CI/CD Integration

### GitHub Actions (Future)

```yaml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest --cov=app --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

### Pre-commit Hook (Recommended)

```bash
# .git/hooks/pre-commit
#!/bin/bash
pytest tests/test_smoke.py
if [ $? -ne 0 ]; then
    echo "Smoke tests failed. Commit aborted."
    exit 1
fi
```

---

## Debugging Tests

### Run Single Test with Debug Output

```bash
pytest tests/test_auth.py::test_signup_success -v -s
```

### Drop into Debugger on Failure

```bash
pytest --pdb
```

### Print Database Queries

```bash
# Set echo=True in conftest.py
engine = create_engine(TEST_DATABASE_URL, echo=True)
```

### Check Test Database

```bash
# Connect to test database
docker exec -it billings_test_db psql -U postgres -d billings_test

# List tables
\dt

# Query users
SELECT * FROM users;
```

---

## Test Metrics

### Coverage Goals

- **Overall:** 80%+ coverage
- **Critical paths:** 95%+ coverage (auth, payments, admin)
- **Security endpoints:** 100% coverage

### Running Coverage Report

```bash
# Generate HTML coverage report
pytest --cov=app --cov-report=html

# View report
open htmlcov/index.html
```

### Coverage by Module

```bash
pytest --cov=app --cov-report=term-missing
```

---

## Common Test Issues

### Issue: Tests Fail Locally but Pass in CI

**Cause:** Database state or environment variables

**Solution:**
```bash
# Reset test database
cd tests && docker compose down -v && docker compose up -d
```

### Issue: Test Isolation Failure

**Cause:** Test modifying shared state

**Solution:** Use `test_db` fixture, avoid caching

### Issue: Slow Tests

**Cause:** Too many database operations

**Solution:**
- Use `@pytest.mark.slow` for integration tests
- Run fast tests first: `pytest -m "not slow"`
- Optimize database fixtures

---

## Next Steps

### Recommended Test Additions

1. **Performance Tests** - Load testing for high-traffic endpoints
2. **Stress Tests** - Rate limit enforcement under load
3. **Regression Tests** - Tests for previously fixed bugs
4. **End-to-End Browser Tests** - Selenium/Playwright for frontend integration
5. **Contract Tests** - API contract validation for frontend

### Test Coverage Gaps

1. Email service unit tests
2. Leaderboard edge cases (ties, pagination)
3. Study mode session persistence
4. Bookmark search and filtering
5. Avatar unlock conditions

---

## Questions?

For test-related questions:
1. Check existing tests for patterns
2. Review this documentation
3. Look at `tests/conftest.py` for fixtures
4. Run `pytest --help` for options

**Philosophy:** Write tests that would catch bugs when AI modifies code. Every test should prevent a real regression.
