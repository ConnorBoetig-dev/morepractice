# Rate Limiting Best Practices

## Overview

This project uses **slowapi** for rate limiting. All rate limiting configuration is centralized in `app/utils/rate_limit.py`.

## Quick Start

### 1. Import the limiter in your route file

```python
from app.utils.rate_limit import limiter, RATE_LIMITS
```

### 2. Add the decorator to your route function

```python
@router.get("/endpoint")
@limiter.limit(RATE_LIMITS["standard"])  # Use predefined rate limit
async def my_endpoint(request: Request, ...):
    # Your code here
    pass
```

**Important**: The function MUST have a `request: Request` parameter for the limiter to work.

## Predefined Rate Limits

Located in `app/utils/rate_limit.py`:

- `RATE_LIMITS["auth_signup"]` = `"3/hour"` - For signup endpoints
- `RATE_LIMITS["auth_login"]` = `"5/minute"` - For login endpoints
- `RATE_LIMITS["quiz_submit"]` = `"10/minute"` - For quiz submissions
- `RATE_LIMITS["standard"]` = `"30/minute"` - For standard API endpoints
- `RATE_LIMITS["leaderboard"]` = `"20/minute"` - For leaderboard queries

## Examples

### Example 1: Using predefined rate limit

```python
from fastapi import APIRouter, Request
from app.utils.rate_limit import limiter, RATE_LIMITS

router = APIRouter()

@router.get("/data")
@limiter.limit(RATE_LIMITS["standard"])  # 30/minute
async def get_data(request: Request):
    return {"data": "example"}
```

### Example 2: Using custom rate limit

```python
@router.post("/special")
@limiter.limit("100/hour")  # Custom rate limit
async def special_endpoint(request: Request):
    return {"status": "ok"}
```

### Example 3: Multiple decorators

```python
@router.post("/submit")
@limiter.limit(RATE_LIMITS["quiz_submit"])
async def submit_quiz(
    request: Request,
    payload: QuizPayload,
    db: Session = Depends(get_db)
):
    # Process quiz submission
    return {"success": True}
```

## Common Mistakes

### ❌ WRONG: Manual limiter call (old pattern)

```python
async def my_endpoint(request: Request):
    limiter = request.app.state.limiter
    await limiter.limit("30/minute")(request)  # DON'T DO THIS
    return {"data": "example"}
```

### ✅ CORRECT: Decorator pattern

```python
@limiter.limit("30/minute")
async def my_endpoint(request: Request):
    return {"data": "example"}
```

### ❌ WRONG: Missing Request parameter

```python
@limiter.limit("30/minute")
async def my_endpoint():  # Missing request parameter!
    return {"data": "example"}
```

### ✅ CORRECT: Include Request parameter

```python
@limiter.limit("30/minute")
async def my_endpoint(request: Request):
    return {"data": "example"}
```

## Rate Limit Syntax

- `"10/minute"` - 10 requests per minute
- `"100/hour"` - 100 requests per hour
- `"1000/day"` - 1000 requests per day
- `"5/second"` - 5 requests per second

## Benefits of This Approach

1. **Centralized Configuration**: All rate limits defined in one place
2. **Consistency**: Use predefined limits across similar endpoints
3. **Easy to Update**: Change rate limits globally by updating `RATE_LIMITS`
4. **Clean Code**: Decorator pattern is cleaner than manual calls
5. **Type Safe**: FastAPI validates the Request parameter

## Files Modified

- `app/utils/rate_limit.py` - Centralized rate limiter configuration
- `app/main.py` - Imports and registers the limiter
- `app/api/v1/auth_routes.py` - Example implementation
- All route files now import from `app.utils.rate_limit`

## Testing Rate Limits

To test if rate limiting works:

```bash
# Should succeed
curl http://localhost:8000/api/v1/auth/login -X POST -H "Content-Type: application/json" -d '{"email":"test@test.com","password":"pass"}'

# Hit the endpoint multiple times rapidly
for i in {1..10}; do
  curl http://localhost:8000/api/v1/auth/login -X POST -H "Content-Type: application/json" -d '{"email":"test@test.com","password":"pass"}'
done

# Should return 429 Too Many Requests after exceeding the limit
```

## Further Reading

- [slowapi documentation](https://slowapi.readthedocs.io/)
- [FastAPI Rate Limiting Guide](https://fastapi.tiangolo.com/advanced/middleware/)
