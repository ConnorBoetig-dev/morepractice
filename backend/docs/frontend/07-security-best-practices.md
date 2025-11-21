# Security Best Practices

Frontend security guide for building secure applications with the Billings API.

**Important:** The backend has comprehensive security measures in place (100+ security tests covering IDOR, privilege escalation, SQL injection, XSS, etc.). This guide shows you how to work with those security features from the frontend.

---

## Table of Contents

- [Authentication Security](#authentication-security)
- [Authorization & Access Control](#authorization--access-control)
- [Input Validation](#input-validation)
- [XSS Prevention](#xss-prevention)
- [Token Management](#token-management)
- [HTTPS & Secure Communication](#https--secure-communication)
- [Rate Limiting](#rate-limiting)
- [Common Attack Prevention](#common-attack-prevention)

---

## Authentication Security

### ✅ DO: Store Tokens Securely

```javascript
// ✅ Good - Use localStorage (acceptable for most SPAs)
localStorage.setItem('access_token', token);

// ✅ Better - Use httpOnly cookies (set by backend)
// Backend should set: Set-Cookie: access_token=...; HttpOnly; Secure; SameSite=Strict

// ❌ Bad - Don't store in regular state (lost on refresh)
const [token, setToken] = useState(accessToken);
```

**Backend Protection:** Tokens are signed with secret key, tampered tokens are rejected.

---

### ✅ DO: Clear Tokens on Logout

```javascript
async function logout() {
  try {
    // Call logout endpoint (invalidates refresh token server-side)
    await apiClient.post('/api/v1/auth/logout');
  } finally {
    // ALWAYS clear local storage (even if API call fails)
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_data');

    // Redirect to login
    window.location.href = '/login';
  }
}
```

**Backend Protection:** Logout endpoint invalidates refresh tokens server-side.

---

### ✅ DO: Implement Token Refresh

```javascript
// ✅ Good - Auto-refresh expired tokens
apiClient.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config;

    if (error.response?.data?.error?.code === 'TOKEN_EXPIRED' && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const { data } = await refreshToken();
        localStorage.setItem('access_token', data.access_token);
        originalRequest.headers['Authorization'] = `Bearer ${data.access_token}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        // Refresh failed - logout user
        localStorage.clear();
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);
```

**Backend Protection:** Refresh tokens expire after 7 days, must be reissued.

---

### ❌ DON'T: Trust Frontend-Only Authentication

```javascript
// ❌ Bad - Client-side only check (can be bypassed)
function ProtectedRoute({ children }) {
  const isAdmin = localStorage.getItem('is_admin') === 'true';

  if (!isAdmin) {
    return <AccessDenied />;
  }

  return children;
}

// ✅ Good - Also verify server-side
function AdminRoute({ children }) {
  const [authorized, setAuthorized] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Server validates admin status
    apiClient.get('/api/v1/admin/users')
      .then(() => setAuthorized(true))
      .catch(() => setAuthorized(false))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <Loading />;
  if (!authorized) return <AccessDenied />;

  return children;
}
```

**Backend Protection:** All admin endpoints verify `is_admin` flag server-side. Frontend checks are for UX only.

---

## Authorization & Access Control

### ✅ DO: Respect 403 Forbidden Responses

```javascript
// Backend returns 403 when user lacks permission
try {
  await apiClient.get('/api/v1/admin/users');
} catch (error) {
  if (error.response?.status === 403) {
    // Show user-friendly message
    toast.error('You do not have permission to access this resource');
    // Redirect to appropriate page
    navigate('/dashboard');
  }
}
```

**Backend Protection:** All protected endpoints verify user permissions. 403 responses cannot be bypassed.

---

### ❌ DON'T: Try to Access Other Users' Data

```javascript
// ❌ Bad - Trying to access another user's data
const otherUserId = 999;
await apiClient.get(`/api/v1/users/${otherUserId}/bookmarks`);
// Backend will return 403 or 404

// ✅ Good - Access own data only
await apiClient.get('/api/v1/bookmarks');
// Backend extracts user_id from JWT token
```

**Backend Protection:** 100% tested against IDOR attacks. Users can ONLY access their own data.

---

### ✅ DO: Use Current User from Token

```javascript
// ✅ Good - Let backend identify user
async function submitQuiz(answers) {
  // No user_id needed - backend gets it from JWT token
  await apiClient.post('/api/v1/quiz/submit', {
    exam_type: 'security',
    answers: answers
  });
}

// ❌ Bad - Don't send user_id (backend ignores it anyway)
async function submitQuiz(userId, answers) {
  await apiClient.post('/api/v1/quiz/submit', {
    user_id: userId,  // ❌ Ignored by backend
    answers: answers
  });
}
```

**Backend Protection:** User ID is ALWAYS extracted from JWT token, never from request body.

---

## Input Validation

### ✅ DO: Validate Before Sending

```javascript
// ✅ Good - Frontend validation (UX)
function SignupForm() {
  const [errors, setErrors] = useState({});

  const validate = (email, password) => {
    const errors = {};

    // Email validation
    if (!email.includes('@')) {
      errors.email = 'Invalid email format';
    }

    // Password strength
    if (password.length < 8) {
      errors.password = 'Password must be at least 8 characters';
    }
    if (!/[A-Z]/.test(password)) {
      errors.password = 'Password must contain uppercase letter';
    }
    if (!/[0-9]/.test(password)) {
      errors.password = 'Password must contain a number';
    }
    if (!/[!@#$%^&*]/.test(password)) {
      errors.password = 'Password must contain special character';
    }

    return errors;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const validationErrors = validate(email, password);
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      return;
    }

    // Validation passed - send to backend
    await authService.signup(email, username, password);
  };
}
```

**Backend Protection:** ALL inputs re-validated on backend with Pydantic. Frontend validation is for UX only.

---

### ✅ DO: Handle Validation Errors from Backend

```javascript
// Backend returns 422 with validation errors
try {
  await authService.signup(email, username, password);
} catch (error) {
  if (error.response?.status === 422) {
    const validationErrors = error.response.data.errors;

    // Map to form fields
    const fieldErrors = {};
    validationErrors.forEach(err => {
      const field = err.field.split('.').pop(); // "body.email" → "email"
      fieldErrors[field] = err.message;
    });

    setFormErrors(fieldErrors);
    // { email: "field required", password: "ensure this value has at least 8 characters" }
  }
}
```

**Backend Protection:** Pydantic validates all inputs. Invalid data is rejected before reaching business logic.

---

### ❌ DON'T: Trust Client-Side Validation Alone

```javascript
// ❌ Bad - Only frontend validation
function updateProfile(bio) {
  if (bio.length > 500) {
    alert('Bio too long');
    return;
  }
  apiClient.put('/api/v1/auth/me', { bio });
}

// ✅ Good - Frontend + Backend validation
function updateProfile(bio) {
  // Frontend check (UX)
  if (bio.length > 500) {
    alert('Bio must be 500 characters or less');
    return;
  }

  // Backend also validates (security)
  try {
    await apiClient.put('/api/v1/auth/me', { bio });
  } catch (error) {
    if (error.response?.status === 422) {
      alert('Invalid input: ' + error.response.data.errors[0].message);
    }
  }
}
```

**Backend Protection:** All fields have max length constraints enforced by database and Pydantic models.

---

## XSS Prevention

### ✅ DO: Escape User-Generated Content

```javascript
// React automatically escapes by default
function DisplayUsername({ username }) {
  // ✅ Good - React escapes HTML automatically
  return <h1>{username}</h1>;
  // Even if username is "<script>alert('XSS')</script>", it renders as text
}

// ❌ Bad - Using dangerouslySetInnerHTML
function DisplayBio({ bio }) {
  return <div dangerouslySetInnerHTML={{ __html: bio }} />;
  // ⚠️ Only use if bio is sanitized server-side
}

// ✅ Good - Sanitize before rendering
import DOMPurify from 'dompurify';

function DisplayBio({ bio }) {
  const sanitized = DOMPurify.sanitize(bio);
  return <div dangerouslySetInnerHTML={{ __html: sanitized }} />;
}
```

**Backend Protection:** Backend stores user input as-is (doesn't execute JavaScript). Frontend must escape when rendering.

---

### ✅ DO: Use Content Security Policy

```html
<!-- Add to index.html -->
<meta http-equiv="Content-Security-Policy"
      content="default-src 'self';
               script-src 'self';
               style-src 'self' 'unsafe-inline';
               img-src 'self' data: https:;">
```

**Backend Protection:** Backend sets security headers (X-Frame-Options, X-Content-Type-Options, etc.).

---

### ❌ DON'T: Trust URLs in User Input

```javascript
// ❌ Bad - Rendering user-provided URLs
function UserLink({ userProvidedUrl }) {
  return <a href={userProvidedUrl}>Click here</a>;
  // If userProvidedUrl is "javascript:alert('XSS')", it executes JavaScript
}

// ✅ Good - Validate URL protocol
function UserLink({ userProvidedUrl }) {
  const isSafeUrl = (url) => {
    try {
      const parsed = new URL(url);
      return ['http:', 'https:'].includes(parsed.protocol);
    } catch {
      return false;
    }
  };

  if (!isSafeUrl(userProvidedUrl)) {
    return <span>Invalid link</span>;
  }

  return <a href={userProvidedUrl} rel="noopener noreferrer">Click here</a>;
}
```

**Backend Protection:** Backend doesn't execute URLs. This is a frontend rendering concern.

---

## Token Management

### ✅ DO: Check Token Expiration

```javascript
// ✅ Good - Decode JWT to check expiration
import jwtDecode from 'jwt-decode';

function isTokenExpired(token) {
  try {
    const decoded = jwtDecode(token);
    const currentTime = Date.now() / 1000;
    return decoded.exp < currentTime;
  } catch {
    return true;
  }
}

// Use before making requests
const token = localStorage.getItem('access_token');
if (isTokenExpired(token)) {
  await refreshAccessToken();
}
```

**Backend Protection:** Backend validates token expiration on every request. This check is for better UX.

---

### ❌ DON'T: Modify or Decode Sensitive Token Data

```javascript
// ❌ Bad - Trusting JWT payload client-side
const token = localStorage.getItem('access_token');
const decoded = jwtDecode(token);

if (decoded.is_admin) {
  // ❌ Don't use this for access control (can be modified)
  showAdminPanel();
}

// ✅ Good - Always verify with backend
async function checkAdminAccess() {
  try {
    await apiClient.get('/api/v1/admin/users');
    return true; // Backend verified admin status
  } catch {
    return false;
  }
}
```

**Backend Protection:** Backend validates JWT signature. Tampered tokens are rejected immediately.

---

### ✅ DO: Implement Token Rotation

```javascript
// ✅ Good - Refresh tokens periodically
setInterval(async () => {
  const token = localStorage.getItem('access_token');

  if (token && isTokenExpired(token)) {
    try {
      await refreshAccessToken();
    } catch {
      // Refresh failed - logout
      logout();
    }
  }
}, 5 * 60 * 1000); // Check every 5 minutes
```

**Backend Protection:** Access tokens expire after 24 hours. Refresh tokens expire after 7 days.

---

## HTTPS & Secure Communication

### ✅ DO: Use HTTPS in Production

```javascript
// ✅ Good - Production config
const API_BASE_URL = process.env.NODE_ENV === 'production'
  ? 'https://api.yourapp.com'  // ✅ HTTPS
  : 'http://localhost:8000';    // Local dev only

// ❌ Bad - HTTP in production
const API_BASE_URL = 'http://api.yourapp.com'; // ❌ Insecure
```

**Backend Protection:** Backend should enforce HTTPS redirects in production.

---

### ✅ DO: Verify SSL Certificates

```javascript
// ✅ Good - Don't disable SSL verification
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  // httpsAgent is properly configured by default
});

// ❌ Bad - Disabling SSL verification
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  httpsAgent: new https.Agent({
    rejectUnauthorized: false  // ❌ NEVER do this
  })
});
```

---

## Rate Limiting

### ✅ DO: Handle Rate Limit Errors

```javascript
// Backend returns 429 when rate limit exceeded
try {
  await apiClient.post('/api/v1/auth/login', { email, password });
} catch (error) {
  if (error.response?.status === 429) {
    const retryAfter = error.response.headers['retry-after'];

    toast.error(`Too many attempts. Please try again in ${retryAfter} seconds.`);

    // Disable submit button
    setIsLocked(true);
    setTimeout(() => setIsLocked(false), retryAfter * 1000);
  }
}
```

**Backend Protection:** Rate limits enforced server-side:
- Public endpoints: 60 requests/minute
- Auth endpoints: 3 requests/hour
- Authenticated: 100 requests/minute

---

### ✅ DO: Implement Client-Side Throttling

```javascript
import { debounce } from 'lodash';

// ✅ Good - Debounce search queries
const searchQuestions = debounce(async (query) => {
  await apiClient.get(`/api/v1/questions/search?q=${query}`);
}, 500); // Wait 500ms after user stops typing

// ❌ Bad - Search on every keystroke
const handleSearchChange = (e) => {
  apiClient.get(`/api/v1/questions/search?q=${e.target.value}`);
  // Sends request for every character typed
};
```

---

## Common Attack Prevention

### CSRF (Cross-Site Request Forgery)

**Backend Protection:** API uses JWT tokens (not cookies), which are immune to CSRF by default.

```javascript
// ✅ Good - JWT in Authorization header (CSRF-safe)
headers: {
  'Authorization': `Bearer ${token}`
}

// ⚠️ Warning - If using cookies, need CSRF tokens
// But this API doesn't use cookie-based auth
```

---

### Clickjacking

**Backend Protection:** Backend sets `X-Frame-Options: DENY` header.

```javascript
// ✅ Good - Check if app is in iframe
if (window.self !== window.top) {
  // App is in iframe - show warning or break out
  window.top.location = window.self.location;
}
```

---

### SQL Injection

**Backend Protection:** SQLAlchemy ORM prevents SQL injection. All queries are parameterized.

```javascript
// ✅ You don't need to worry about SQL injection from frontend
// Backend handles this automatically with ORM
await apiClient.get(`/api/v1/questions/search?q=${userInput}`);
// userInput is safely parameterized by backend
```

---

### Session Hijacking

**Backend Protection:** Tokens have short expiration (24 hours). Refresh tokens expire after 7 days.

```javascript
// ✅ Good - Additional client-side protection
const SESSION_TIMEOUT = 30 * 60 * 1000; // 30 minutes

let lastActivity = Date.now();

// Track user activity
document.addEventListener('click', () => {
  lastActivity = Date.now();
});

// Check for inactivity
setInterval(() => {
  if (Date.now() - lastActivity > SESSION_TIMEOUT) {
    logout(); // Auto-logout after 30 minutes of inactivity
  }
}, 60000); // Check every minute
```

---

## Security Checklist

Before deploying to production, verify:

### Authentication
- [ ] Tokens stored securely (localStorage or httpOnly cookies)
- [ ] Tokens cleared on logout
- [ ] Token refresh implemented
- [ ] Invalid tokens redirect to login

### Authorization
- [ ] Admin routes protected client-side AND server-side
- [ ] User data access uses JWT token (no user_id in requests)
- [ ] 403 errors handled gracefully

### Input Validation
- [ ] All forms have frontend validation (UX)
- [ ] Backend validation errors displayed to user
- [ ] No trust in client-side validation for security

### XSS Prevention
- [ ] User content escaped when rendered
- [ ] No dangerouslySetInnerHTML without sanitization
- [ ] Content Security Policy configured

### Communication
- [ ] HTTPS used in production
- [ ] No sensitive data in URLs (use POST body)
- [ ] API base URL configured per environment

### Rate Limiting
- [ ] 429 errors handled with user feedback
- [ ] Client-side debouncing for search/autocomplete
- [ ] Submit buttons disabled during processing

### Error Handling
- [ ] Errors displayed user-friendly (not raw error messages)
- [ ] Full errors logged to console for debugging
- [ ] Network errors handled gracefully

---

## Security Testing

### Manual Security Tests

```javascript
// 1. Test IDOR Protection
const myToken = localStorage.getItem('access_token');
const otherUserId = 999;

// Should fail with 403
await apiClient.get(`/api/v1/users/${otherUserId}/profile`);

// 2. Test Token Tampering
const tampered = myToken.slice(0, -5) + 'XXXXX';
localStorage.setItem('access_token', tampered);

// Should fail with 401
await apiClient.get('/api/v1/bookmarks');

// 3. Test XSS
const maliciousUsername = '<script>alert("XSS")</script>';
await apiClient.put('/api/v1/auth/me', { username: maliciousUsername });

// Should be rendered as text, not executed

// 4. Test SQL Injection
const maliciousSearch = "'; DROP TABLE users; --";
await apiClient.get(`/api/v1/questions/search?q=${maliciousSearch}`);

// Should return safely (no SQL injection)
```

---

## Backend Security Coverage

The backend has **100+ security tests** covering:

✅ Password hashing security (bcrypt, timing attacks)
✅ JWT token security (tampering, expiration, signature validation)
✅ IDOR attacks (users accessing other users' data)
✅ Privilege escalation (regular users becoming admin)
✅ SQL injection prevention
✅ XSS prevention
✅ Mass assignment protection
✅ Brute force protection (account lockout)
✅ Session security
✅ Input validation

**You can trust the backend to enforce security.** Frontend security is about:
1. Good UX (validation, error messages)
2. Not making it easier for attackers (client-side checks)
3. Proper token handling

---

## Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
- [React Security](https://react.dev/learn/writing-markup-with-jsx#the-rules-of-jsx)
- [Content Security Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)

---

## Questions?

If you discover a security issue:
1. **DO NOT** create a public GitHub issue
2. Contact the backend team directly
3. Provide steps to reproduce
4. Wait for confirmation before disclosing

The backend is production-ready and secure. Build your frontend with confidence!
