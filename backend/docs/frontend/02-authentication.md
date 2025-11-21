# Authentication Guide

## Authentication Flow

Billings API uses **JWT (JSON Web Tokens)** for authentication.

```
┌─────────┐                           ┌─────────┐
│ Frontend│                           │   API   │
└────┬────┘                           └────┬────┘
     │                                     │
     │  POST /api/v1/auth/signup          │
     │  { email, username, password }     │
     ├────────────────────────────────────>│
     │                                     │
     │  { access_token, refresh_token }   │
     │<────────────────────────────────────┤
     │                                     │
     │  Store tokens in localStorage      │
     │                                     │
     │  GET /api/v1/bookmarks             │
     │  Authorization: Bearer <token>     │
     ├────────────────────────────────────>│
     │                                     │
     │  Verify token → Get user_id        │
     │                                     │
     │  { bookmarks: [...] }              │
     │<────────────────────────────────────┤
     │                                     │
```

## 1. User Signup

**Endpoint:** `POST /api/v1/auth/signup`

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
    "is_verified": false,
    "created_at": "2025-01-20T10:00:00Z"
  }
}
```

**Error Response (400):**
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

**Password Requirements:**
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character

## 2. User Login

**Endpoint:** `POST /api/v1/auth/login`

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
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "johndoe",
    "is_active": true,
    "is_verified": true
  }
}
```

**Error Response (401):**
```json
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
```

## 3. Using Access Tokens

**Include the token in the `Authorization` header:**

```javascript
const response = await fetch('http://localhost:8000/api/v1/bookmarks', {
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  }
});
```

**Token Structure:**
```
Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJleHAiOjE3MDU3NjE2MDB9.abc123
       └─────────────────────── JWT Token ───────────────────────┘
```

## 4. Token Expiration & Refresh

**Access tokens expire after 24 hours.**

When you get a 401 error with code `TOKEN_EXPIRED`, refresh the token:

**Endpoint:** `POST /api/v1/auth/refresh`

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

**Frontend Implementation:**
```javascript
// Interceptor example (axios)
axios.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config;

    if (error.response.status === 401 &&
        error.response.data.error.code === 'TOKEN_EXPIRED' &&
        !originalRequest._retry) {
      originalRequest._retry = true;

      const refreshToken = localStorage.getItem('refresh_token');
      const { data } = await axios.post('/api/v1/auth/refresh', {
        refresh_token: refreshToken
      });

      localStorage.setItem('access_token', data.access_token);
      originalRequest.headers['Authorization'] = `Bearer ${data.access_token}`;

      return axios(originalRequest);
    }

    return Promise.reject(error);
  }
);
```

## 5. Get Current User

**Endpoint:** `GET /api/v1/auth/me`

**Request:**
```
Authorization: Bearer <access_token>
```

**Success Response (200):**
```json
{
  "success": true,
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "johndoe",
    "is_active": true,
    "is_verified": true,
    "created_at": "2025-01-20T10:00:00Z"
  }
}
```

## 6. Logout

**Endpoint:** `POST /api/v1/auth/logout`

**Request:**
```
Authorization: Bearer <access_token>
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

**Frontend Implementation:**
```javascript
async function logout() {
  const token = localStorage.getItem('access_token');

  await fetch('http://localhost:8000/api/v1/auth/logout', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });

  // Clear local storage
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');

  // Redirect to login
  window.location.href = '/login';
}
```

## 7. Password Reset Flow

### Step 1: Request Reset

**Endpoint:** `POST /api/v1/auth/password-reset/request`

**Request:**
```json
{
  "email": "user@example.com"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Password reset email sent"
}
```

### Step 2: Reset Password

**Endpoint:** `POST /api/v1/auth/password-reset/confirm`

**Request:**
```json
{
  "token": "reset-token-from-email",
  "new_password": "NewSecurePass123!"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Password reset successful"
}
```

## 8. Email Verification

### Request Verification Email

**Endpoint:** `POST /api/v1/auth/email/verify/request`

**Request:**
```json
{
  "email": "user@example.com"
}
```

### Verify Email

**Endpoint:** `POST /api/v1/auth/email/verify/confirm`

**Request:**
```json
{
  "token": "verification-token-from-email"
}
```

## Frontend Token Storage

**Recommended approach:**

```javascript
// After login/signup
localStorage.setItem('access_token', data.access_token);
localStorage.setItem('refresh_token', data.refresh_token);

// For authenticated requests
const getAuthHeaders = () => ({
  'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
  'Content-Type': 'application/json'
});

// Check if user is logged in
const isAuthenticated = () => {
  return !!localStorage.getItem('access_token');
};

// Protect routes
if (!isAuthenticated()) {
  window.location.href = '/login';
}
```

## Common Auth Errors

| Error Code | Status | Meaning | Action |
|-----------|--------|---------|--------|
| `INVALID_CREDENTIALS` | 401 | Wrong email/password | Show error message |
| `TOKEN_EXPIRED` | 401 | Access token expired | Refresh token |
| `TOKEN_INVALID` | 401 | Token is malformed | Clear tokens, redirect to login |
| `UNAUTHORIZED` | 401 | No token provided | Redirect to login |
| `EMAIL_ALREADY_REGISTERED` | 400 | Email taken | Show error, suggest login |
| `USERNAME_ALREADY_TAKEN` | 400 | Username taken | Choose different username |

## Next Steps

- **[Error Handling](./03-error-handling.md)** - Handle auth errors properly
- **[Endpoints Reference](./04-endpoints-reference.md)** - Explore other endpoints
