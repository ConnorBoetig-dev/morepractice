# Billings Frontend

A simple, educational HTML/CSS/JavaScript frontend demonstrating full-stack authentication with JWT tokens.

## 🎯 Purpose

This frontend is designed for **learning** how to build a frontend that interacts with a REST API backend. It uses vanilla JavaScript (no frameworks) to keep things simple and easy to understand.

## 📂 Project Structure

```
frontend/
├── index.html           # Landing page
├── signup.html          # User registration page
├── login.html           # User authentication page
├── dashboard.html       # Protected user dashboard
├── css/
│   └── styles.css       # All styling
├── js/
│   ├── config.js        # API endpoint configuration
│   ├── auth.js          # JWT token management utilities
│   ├── api.js           # Generic API request wrapper
│   ├── signup.js        # Signup page logic
│   ├── login.js         # Login page logic
│   └── dashboard.js     # Dashboard page logic
└── README.md            # This file
```

## 🚀 Quick Start

### Prerequisites

1. **Backend must be running** on `http://localhost:8000`
   ```bash
   cd ../backend
   source venv/bin/activate
   uvicorn app.main:app --reload
   ```

2. **Database must be running**
   ```bash
   cd ../backend
   docker compose up -d
   ```

### Running the Frontend

**Option 1: Python HTTP Server (Recommended)**
```bash
cd frontend
python3 -m http.server 8080
```

Then open: http://localhost:8080

**Option 2: VS Code Live Server**
1. Install "Live Server" extension in VS Code
2. Right-click `index.html`
3. Select "Open with Live Server"

**Option 3: Node.js http-server**
```bash
npm install -g http-server
cd frontend
http-server -p 8080
```

## 📖 How It Works

### 1. User Registration (Signup)

**Page:** `signup.html`

**Flow:**
1. User fills in email, username, and password
2. JavaScript validates inputs (client-side)
3. POST request to `/api/v1/auth/signup`
4. Backend creates user and returns JWT token
5. Token saved to localStorage
6. Redirect to dashboard

**Key Files:**
- `signup.html` - Form UI
- `js/signup.js` - Form submission logic
- `js/api.js` - Makes the POST request
- `js/auth.js` - Saves token

### 2. User Authentication (Login)

**Page:** `login.html`

**Flow:**
1. User enters email and password
2. POST request to `/api/v1/auth/login`
3. Backend validates credentials
4. Returns JWT token if valid
5. Token saved to localStorage
6. Redirect to dashboard

**Key Files:**
- `login.html` - Form UI
- `js/login.js` - Form submission logic

### 3. Protected Dashboard

**Page:** `dashboard.html`

**Flow:**
1. JavaScript checks if token exists (route guard)
2. If no token → redirect to login
3. If token exists → GET request to `/api/v1/auth/me`
4. Include token in Authorization header: `Bearer <token>`
5. Backend validates token and returns user data
6. Display user information

**Key Files:**
- `dashboard.html` - Dashboard UI
- `js/dashboard.js` - Fetch and display user data
- `js/auth.js` - Token retrieval and route guard

### 4. Logout

**Flow:**
1. User clicks logout button
2. Token removed from localStorage
3. Redirect to login page

**Note:** This is client-side logout. The token remains valid on the backend until expiration (15 minutes).

## 🔐 Authentication Flow

```
┌──────────┐       ┌─────────────┐       ┌─────────────┐
│  Signup  │──────▶│   Backend   │──────▶│ localStorage│
│  /Login  │       │  (FastAPI)  │       │   (Token)   │
└──────────┘       └─────────────┘       └─────────────┘
                           │
                           │ Validates
                           │ credentials
                           ▼
                   ┌─────────────┐
                   │  PostgreSQL │
                   │  (Database) │
                   └─────────────┘

┌──────────────┐   Authorization: Bearer <token>   ┌─────────────┐
│  Dashboard   │──────────────────────────────────▶│   Backend   │
│  (Protected) │                                    │  (FastAPI)  │
└──────────────┘◀──────────────────────────────────└─────────────┘
                      Returns user data
```

## 📚 What You'll Learn

### JavaScript Concepts

- **ES6 Modules** - `import` and `export` statements
- **Async/Await** - Handling asynchronous operations
- **Promises** - Using `fetch()` API
- **Event Listeners** - Detecting user actions
- **Form Handling** - Getting form data with FormData
- **localStorage** - Client-side storage
- **Error Handling** - try/catch blocks

### Web API Concepts

- **REST APIs** - Making HTTP requests (GET, POST)
- **JSON** - Request/response data format
- **HTTP Status Codes** - 200, 400, 401, 500
- **Request Headers** - Content-Type, Authorization
- **Bearer Tokens** - JWT authentication
- **CORS** - Cross-Origin Resource Sharing

### Authentication Concepts

- **JWT (JSON Web Tokens)** - Token structure and usage
- **Protected Routes** - Route guards
- **Token Storage** - localStorage vs cookies
- **Token Expiration** - Handling 401 errors
- **Client-side vs Server-side** - Security considerations

### Best Practices

- **Separation of Concerns** - Modular code organization
- **DRY Principle** - Reusable API wrapper function
- **Error Handling** - User-friendly error messages
- **Input Validation** - Client and server-side
- **Security** - XSS prevention, HTTPS importance

## 🔧 API Endpoints Used

All endpoints are on `http://localhost:8000/api/v1`

| Method | Endpoint | Auth Required | Purpose |
|--------|----------|---------------|---------|
| POST | `/auth/signup` | No | Create new user account |
| POST | `/auth/login` | No | Authenticate existing user |
| GET | `/auth/me` | Yes | Get current user info |
| POST | `/auth/logout` | Yes | Logout user (client-side) |

## 🛠️ Customization

### Change API URL

Edit `js/config.js`:
```javascript
export const API_BASE_URL = 'http://your-backend-url:8000';
```

### Change Token Expiration

This is set in the backend `.env` file:
```bash
JWT_EXPIRATION_MINUTES=15  # Change this value
```

### Add New API Endpoints

1. Add to `js/config.js`:
   ```javascript
   export const ENDPOINTS = {
       // Existing endpoints...
       NEW_ENDPOINT: `${API_FULL_BASE}/your/endpoint`,
   };
   ```

2. Use in your code:
   ```javascript
   import { ENDPOINTS } from './config.js';

   const data = await apiRequest('GET', ENDPOINTS.NEW_ENDPOINT, null, true);
   ```

## 🐛 Troubleshooting

### Error: "Cannot connect to server"

**Problem:** Backend is not running

**Solution:**
```bash
cd ../backend
source venv/bin/activate
uvicorn app.main:app --reload
```

### Error: "Invalid or expired token"

**Problem:** JWT token has expired (15 minutes)

**Solution:** Log out and log back in to get a new token

### Error: "CORS error"

**Problem:** Frontend URL not in backend's allowed origins

**Solution:** Add your frontend URL to `backend/app/main.py`:
```python
allow_origins=[
    "http://localhost:8080",  # Add your frontend URL
    "http://localhost:5173",
    "http://localhost:3000",
],
```

### Page shows "Loading..." forever

**Problem:** JavaScript console likely has errors

**Solution:**
1. Open browser DevTools (F12)
2. Check Console tab for errors
3. Check Network tab to see API requests/responses

### Forms not submitting

**Problem:** JavaScript not loading properly

**Solution:**
- Check browser console for errors
- Ensure you're using a web server (not opening file:// directly)
- Make sure all JS files exist in `js/` folder

## 📝 Code Tour

### Start Here
1. Read `js/config.js` - API configuration
2. Read `js/auth.js` - Token management
3. Read `js/api.js` - API request wrapper

### Then Explore Pages
1. `signup.html` + `js/signup.js` - User registration
2. `login.html` + `js/login.js` - Authentication
3. `dashboard.html` + `js/dashboard.js` - Protected page

### Finally
1. `css/styles.css` - All styling
2. `index.html` - Landing page

## 🔒 Security Notes

### What This Demo Does Right
✅ HTTPS in production (important!)
✅ Password hashing on backend (never plain text)
✅ JWT token expiration (15 minutes)
✅ Input validation (client and server)
✅ Generic error messages (prevents email enumeration)
✅ XSS prevention (using textContent, not innerHTML)
✅ Rate limiting (IP-based with slowapi)

### What's Missing (For Learning Simplicity)
⚠️ No refresh tokens (must re-login after 15 min)
⚠️ No token blacklist (tokens valid until expiration)
⚠️ localStorage instead of HttpOnly cookies
⚠️ No CSRF protection
⚠️ No 2FA/MFA

**For Production:** Consider these additional security measures!

## 🎓 Learning Resources

### JavaScript
- [MDN Web Docs - JavaScript](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
- [JavaScript.info](https://javascript.info/)

### APIs & HTTP
- [MDN - Fetch API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API)
- [HTTP Status Codes](https://httpstatuses.com/)

### JWT & Auth
- [JWT.io - Introduction](https://jwt.io/introduction)
- [OWASP Auth Cheatsheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)

## 📄 License

This is an educational project. Feel free to use and modify for learning!

## 🙋 Need Help?

1. Check browser console (F12) for errors
2. Check backend logs in terminal
3. Review code comments in JS files
4. Check API responses in Network tab

Happy learning! 🚀
