# Error Handling Guide

## Error Response Format

All errors follow a **consistent, predictable format**.

### Single Error Response

Used for: 400, 401, 403, 404, 409, 500, etc.

```json
{
  "success": false,
  "error": {
    "message": "Human-readable error message",
    "code": "MACHINE_READABLE_ERROR_CODE"
  },
  "status_code": 404,
  "timestamp": "2025-01-20T14:30:00Z",
  "path": "/api/v1/bookmarks/questions/999"
}
```

### Validation Error Response (422)

Used for: Missing required fields, invalid data types, constraint violations

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

## Error Code Reference

### 400 Bad Request

| Code | Description | Example |
|------|-------------|---------|
| `INVALID_INPUT` | Generic bad request | Invalid JSON format |
| `INVALID_CREDENTIALS` | Wrong email/password | Login failed |
| `WEAK_PASSWORD` | Password doesn't meet requirements | Password too short |

**Example:**
```json
{
  "success": false,
  "error": {
    "message": "Email already registered",
    "code": "EMAIL_ALREADY_REGISTERED"
  },
  "status_code": 400,
  "timestamp": "2025-01-20T14:30:00Z",
  "path": "/api/v1/auth/signup"
}
```

### 401 Unauthorized

| Code | Description | Action |
|------|-------------|--------|
| `UNAUTHORIZED` | Generic unauthorized | Redirect to login |
| `TOKEN_EXPIRED` | Access token expired | Refresh token |
| `TOKEN_INVALID` | Token is malformed/invalid | Clear tokens, redirect to login |
| `AUTHENTICATION_REQUIRED` | No token provided | Redirect to login |

**Example:**
```json
{
  "success": false,
  "error": {
    "message": "Invalid or expired token",
    "code": "TOKEN_EXPIRED"
  },
  "status_code": 401,
  "timestamp": "2025-01-20T14:30:00Z",
  "path": "/api/v1/bookmarks"
}
```

### 403 Forbidden

| Code | Description | Meaning |
|------|-------------|---------|
| `FORBIDDEN` | Generic forbidden | User doesn't have permission |
| `INSUFFICIENT_PERMISSIONS` | Lacks required permission | Need higher role |
| `ADMIN_REQUIRED` | Admin access required | Must be admin |
| `ACCOUNT_INACTIVE` | Account is disabled | Contact support |
| `ACCOUNT_LOCKED` | Too many failed attempts | Account locked |

**Example:**
```json
{
  "success": false,
  "error": {
    "message": "Admin access required",
    "code": "ADMIN_REQUIRED"
  },
  "status_code": 403,
  "timestamp": "2025-01-20T14:30:00Z",
  "path": "/api/v1/admin/users"
}
```

### 404 Not Found

| Code | Description |
|------|-------------|
| `RESOURCE_NOT_FOUND` | Generic resource not found |
| `USER_NOT_FOUND` | User doesn't exist |
| `QUESTION_NOT_FOUND` | Question doesn't exist |
| `BOOKMARK_NOT_FOUND` | Bookmark doesn't exist |
| `ENDPOINT_NOT_FOUND` | Endpoint doesn't exist |

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

### 409 Conflict

| Code | Description |
|------|-------------|
| `RESOURCE_ALREADY_EXISTS` | Generic duplicate |
| `EMAIL_ALREADY_REGISTERED` | Email taken |
| `USERNAME_ALREADY_TAKEN` | Username taken |
| `DUPLICATE_ENTRY` | Duplicate entry |

### 422 Validation Error

| Code | Description |
|------|-------------|
| `VALIDATION_ERROR` | Pydantic validation failed |
| `INVALID_FORMAT` | Invalid data format |

**Example:**
```json
{
  "success": false,
  "errors": [
    {
      "field": "body.email",
      "message": "value is not a valid email address",
      "code": "VALIDATION_ERROR"
    }
  ],
  "status_code": 422,
  "timestamp": "2025-01-20T14:30:00Z",
  "path": "/api/v1/auth/signup"
}
```

### 429 Too Many Requests

| Code | Description |
|------|-------------|
| `RATE_LIMIT_EXCEEDED` | Rate limit hit |

**Example:**
```json
{
  "error": "Rate limit exceeded: 3 per 1 hour"
}
```

### 500 Internal Server Error

| Code | Description |
|------|-------------|
| `INTERNAL_SERVER_ERROR` | Unexpected error |
| `DATABASE_ERROR` | Database operation failed |

**Example:**
```json
{
  "success": false,
  "error": {
    "message": "An unexpected error occurred. Please try again later.",
    "code": "INTERNAL_SERVER_ERROR"
  },
  "status_code": 500,
  "timestamp": "2025-01-20T14:30:00Z",
  "path": "/api/v1/quiz/submit"
}
```

## Frontend Error Handling

### React Example

```javascript
async function makeRequest(url, options = {}) {
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        'Content-Type': 'application/json',
        ...options.headers
      }
    });

    const data = await response.json();

    // Handle errors
    if (!response.ok) {
      handleError(data, response.status);
      throw new Error(data.error?.message || 'Request failed');
    }

    return data;
  } catch (error) {
    console.error('Request failed:', error);
    throw error;
  }
}

function handleError(errorData, statusCode) {
  const errorCode = errorData.error?.code;

  switch (errorCode) {
    case 'TOKEN_EXPIRED':
      // Try to refresh token
      refreshAccessToken();
      break;

    case 'TOKEN_INVALID':
    case 'UNAUTHORIZED':
    case 'AUTHENTICATION_REQUIRED':
      // Clear tokens and redirect to login
      localStorage.clear();
      window.location.href = '/login';
      break;

    case 'ADMIN_REQUIRED':
    case 'FORBIDDEN':
      // Show "Access Denied" message
      showErrorToast('You do not have permission to access this resource');
      break;

    case 'RESOURCE_NOT_FOUND':
      // Show 404 message
      showErrorToast('Resource not found');
      break;

    case 'EMAIL_ALREADY_REGISTERED':
      // Suggest login instead
      showErrorToast('Email already registered. Try logging in instead.');
      break;

    case 'RATE_LIMIT_EXCEEDED':
      // Show rate limit message
      showErrorToast('Too many requests. Please try again later.');
      break;

    case 'VALIDATION_ERROR':
      // Display validation errors
      if (errorData.errors) {
        errorData.errors.forEach(err => {
          showFieldError(err.field, err.message);
        });
      }
      break;

    default:
      // Generic error message
      showErrorToast(errorData.error?.message || 'Something went wrong');
  }
}
```

### Validation Error Handling

```javascript
function handleValidationErrors(errors) {
  // errors is array of { field, message, code }

  const fieldErrors = {};
  errors.forEach(error => {
    // Convert "body.email" to "email"
    const fieldName = error.field.split('.').pop();
    fieldErrors[fieldName] = error.message;
  });

  return fieldErrors;
}

// Usage in form:
try {
  await signup(email, password);
} catch (error) {
  if (error.status_code === 422) {
    const fieldErrors = handleValidationErrors(error.errors);
    setFormErrors(fieldErrors);
    // { email: "field required", password: "ensure this value has at least 8 characters" }
  }
}
```

### Toast/Alert Display

```javascript
function showErrorToast(message) {
  // Your toast library
  toast.error(message, {
    position: 'top-right',
    autoClose: 5000
  });
}

function showFieldError(fieldPath, message) {
  // fieldPath: "body.email" → extract "email"
  const field = fieldPath.split('.').pop();

  // Set form error state
  setErrors(prev => ({
    ...prev,
    [field]: message
  }));
}
```

## Common Error Scenarios

### Scenario 1: Failed Login

```javascript
// Request
POST /api/v1/auth/login
{ "email": "user@example.com", "password": "wrong" }

// Response (401)
{
  "success": false,
  "error": {
    "message": "Invalid email or password",
    "code": "INVALID_CREDENTIALS"
  },
  "status_code": 401,
  "timestamp": "2025-01-20T14:30:00Z",
  "path": "/api/v1/auth/login"
}

// Frontend Action
showErrorToast("Invalid email or password");
```

### Scenario 2: Missing Token

```javascript
// Request
GET /api/v1/bookmarks
// (No Authorization header)

// Response (401)
{
  "success": false,
  "error": {
    "message": "Not authenticated",
    "code": "AUTHENTICATION_REQUIRED"
  },
  "status_code": 401,
  "timestamp": "2025-01-20T14:30:00Z",
  "path": "/api/v1/bookmarks"
}

// Frontend Action
window.location.href = '/login';
```

### Scenario 3: Validation Errors

```javascript
// Request
POST /api/v1/auth/signup
{ } // Empty body

// Response (422)
{
  "success": false,
  "errors": [
    { "field": "body.email", "message": "field required", "code": "VALIDATION_ERROR" },
    { "field": "body.username", "message": "field required", "code": "VALIDATION_ERROR" },
    { "field": "body.password", "message": "field required", "code": "VALIDATION_ERROR" }
  ],
  "status_code": 422,
  "timestamp": "2025-01-20T14:30:00Z",
  "path": "/api/v1/auth/signup"
}

// Frontend Action
errors.forEach(err => showFieldError(err.field, err.message));
```

### Scenario 4: Expired Token

```javascript
// Request
GET /api/v1/bookmarks
Authorization: Bearer <expired_token>

// Response (401)
{
  "success": false,
  "error": {
    "message": "Token has expired",
    "code": "TOKEN_EXPIRED"
  },
  "status_code": 401,
  "timestamp": "2025-01-20T14:30:00Z",
  "path": "/api/v1/bookmarks"
}

// Frontend Action
refreshAccessToken(); // Use refresh token to get new access token
```

## Best Practices

1. **Always check `response.ok`** before parsing JSON
2. **Use error codes** for programmatic handling, not status codes
3. **Display `error.message`** to users (human-readable)
4. **Log full error object** for debugging
5. **Handle validation errors** by mapping to form fields
6. **Implement token refresh** for 401 TOKEN_EXPIRED errors
7. **Clear tokens** for 401 TOKEN_INVALID errors
8. **Show generic messages** for 500 errors (don't expose internals)

## Next Steps

- **[Endpoints Reference](./04-endpoints-reference.md)** - See all endpoints and their possible errors
- **[Integration Guide](./06-integration-guide.md)** - Complete integration examples
