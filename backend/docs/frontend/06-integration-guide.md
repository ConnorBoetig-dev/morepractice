# Integration Guide

Complete step-by-step guide for integrating with the Billings API.

## Prerequisites

- Node.js installed
- React (or any frontend framework)
- Basic understanding of REST APIs and JWT authentication

## Installation

```bash
npm install axios
# or
npm install fetch
```

## Step 1: Setup API Client

Create a centralized API client with authentication:

```javascript
// src/api/client.js
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - Add auth token to all requests
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - Handle token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If token expired, try to refresh
    if (
      error.response?.status === 401 &&
      error.response?.data?.error?.code === 'TOKEN_EXPIRED' &&
      !originalRequest._retry
    ) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const { data } = await axios.post(`${API_BASE_URL}/api/v1/auth/refresh`, {
          refresh_token: refreshToken,
        });

        // Save new token
        localStorage.setItem('access_token', data.access_token);

        // Retry original request with new token
        originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        // Refresh failed - logout user
        localStorage.clear();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default apiClient;
```

## Step 2: Authentication Service

```javascript
// src/api/auth.js
import apiClient from './client';

export const authService = {
  // Sign up new user
  async signup(email, username, password) {
    const { data } = await apiClient.post('/api/v1/auth/signup', {
      email,
      username,
      password,
    });

    // Save tokens
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);

    return data;
  },

  // Login
  async login(email, password) {
    const { data } = await apiClient.post('/api/v1/auth/login', {
      email,
      password,
    });

    // Save tokens
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);

    return data;
  },

  // Logout
  async logout() {
    try {
      await apiClient.post('/api/v1/auth/logout');
    } finally {
      // Clear tokens even if request fails
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
  },

  // Get current user
  async getCurrentUser() {
    const { data } = await apiClient.get('/api/v1/auth/me');
    return data.user;
  },

  // Check if user is authenticated
  isAuthenticated() {
    return !!localStorage.getItem('access_token');
  },
};
```

## Step 3: Question Service

```javascript
// src/api/questions.js
import apiClient from './client';

export const questionService = {
  // Get available exam types
  async getExamTypes() {
    const { data } = await apiClient.get('/api/v1/questions/exams');
    return data.exams;
  },

  // Get quiz questions
  async getQuizQuestions(examType, count = 30, domain = null) {
    const params = new URLSearchParams({
      exam_type: examType,
      count: count.toString(),
    });

    if (domain) {
      params.append('domain', domain);
    }

    const { data } = await apiClient.get(`/api/v1/questions/quiz?${params}`);
    return data.questions;
  },
};
```

## Step 4: Bookmark Service

```javascript
// src/api/bookmarks.js
import apiClient from './client';

export const bookmarkService = {
  // Get all bookmarks
  async getBookmarks(page = 1, pageSize = 10) {
    const { data } = await apiClient.get('/api/v1/bookmarks', {
      params: { page, page_size: pageSize },
    });
    return data;
  },

  // Create bookmark
  async createBookmark(questionId, notes = null) {
    const { data } = await apiClient.post(
      `/api/v1/bookmarks/questions/${questionId}`,
      { notes }
    );
    return data.bookmark;
  },

  // Remove bookmark
  async removeBookmark(questionId) {
    const { data } = await apiClient.delete(
      `/api/v1/bookmarks/questions/${questionId}`
    );
    return data;
  },

  // Update bookmark notes
  async updateBookmark(questionId, notes) {
    const { data } = await apiClient.patch(
      `/api/v1/bookmarks/questions/${questionId}`,
      { notes }
    );
    return data.bookmark;
  },

  // Check if bookmarked
  async isBookmarked(questionId) {
    const { data } = await apiClient.get(
      `/api/v1/bookmarks/questions/${questionId}/check`
    );
    return data.is_bookmarked;
  },
};
```

## Step 5: Quiz Service

```javascript
// src/api/quiz.js
import apiClient from './client';

export const quizService = {
  // Submit quiz
  async submitQuiz(examType, answers, timeSpentSeconds) {
    const { data } = await apiClient.post('/api/v1/quiz/submit', {
      exam_type: examType,
      answers,
      time_spent_seconds: timeSpentSeconds,
    });
    return data;
  },

  // Get quiz history
  async getHistory(page = 1, pageSize = 10, examType = null) {
    const params = { page, page_size: pageSize };
    if (examType) params.exam_type = examType;

    const { data } = await apiClient.get('/api/v1/quiz/history', { params });
    return data;
  },

  // Get quiz stats
  async getStats() {
    const { data } = await apiClient.get('/api/v1/quiz/stats');
    return data.stats;
  },
};
```

## Step 6: React Components

### Login Component

```jsx
// src/components/Login.jsx
import React, { useState } from 'react';
import { authService } from '../api/auth';

export function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const data = await authService.login(email, password);
      console.log('Logged in:', data.user);
      window.location.href = '/dashboard';
    } catch (err) {
      const errorData = err.response?.data;

      if (errorData?.error?.code === 'INVALID_CREDENTIALS') {
        setError('Invalid email or password');
      } else if (errorData?.error?.code === 'ACCOUNT_LOCKED') {
        setError('Account locked due to too many failed attempts');
      } else {
        setError('Login failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>Login</h2>

      {error && <div className="error">{error}</div>}

      <input
        type="email"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        required
      />

      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
      />

      <button type="submit" disabled={loading}>
        {loading ? 'Logging in...' : 'Login'}
      </button>
    </form>
  );
}
```

### Quiz Component

```jsx
// src/components/Quiz.jsx
import React, { useState, useEffect } from 'react';
import { questionService } from '../api/questions';
import { quizService } from '../api/quiz';

export function Quiz({ examType = 'security' }) {
  const [questions, setQuestions] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [loading, setLoading] = useState(true);
  const [startTime] = useState(Date.now());

  // Load questions
  useEffect(() => {
    loadQuestions();
  }, [examType]);

  const loadQuestions = async () => {
    try {
      const data = await questionService.getQuizQuestions(examType, 30);
      setQuestions(data);
    } catch (error) {
      console.error('Failed to load questions:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAnswer = (questionId, answer) => {
    setAnswers({
      ...answers,
      [questionId]: answer,
    });
  };

  const handleSubmit = async () => {
    const timeSpent = Math.floor((Date.now() - startTime) / 1000);

    const formattedAnswers = Object.entries(answers).map(([questionId, answer]) => ({
      question_id: parseInt(questionId),
      selected_answer: answer,
    }));

    try {
      const result = await quizService.submitQuiz(examType, formattedAnswers, timeSpent);
      console.log('Quiz submitted:', result);
      // Navigate to results page
      window.location.href = `/results/${result.attempt.id}`;
    } catch (error) {
      console.error('Failed to submit quiz:', error);
    }
  };

  if (loading) return <div>Loading quiz...</div>;

  const currentQuestion = questions[currentIndex];

  return (
    <div className="quiz">
      <div className="progress">
        Question {currentIndex + 1} of {questions.length}
      </div>

      <h3>{currentQuestion.question_text}</h3>

      <div className="options">
        {Object.entries(currentQuestion.options).map(([key, option]) => (
          <label key={key}>
            <input
              type="radio"
              name={`question-${currentQuestion.id}`}
              value={key}
              checked={answers[currentQuestion.id] === key}
              onChange={() => handleAnswer(currentQuestion.id, key)}
            />
            {key}. {option.text}
          </label>
        ))}
      </div>

      <div className="navigation">
        <button
          onClick={() => setCurrentIndex(currentIndex - 1)}
          disabled={currentIndex === 0}
        >
          Previous
        </button>

        {currentIndex < questions.length - 1 ? (
          <button onClick={() => setCurrentIndex(currentIndex + 1)}>
            Next
          </button>
        ) : (
          <button onClick={handleSubmit}>Submit Quiz</button>
        )}
      </div>
    </div>
  );
}
```

### Bookmarks Component

```jsx
// src/components/Bookmarks.jsx
import React, { useState, useEffect } from 'react';
import { bookmarkService } from '../api/bookmarks';

export function Bookmarks() {
  const [bookmarks, setBookmarks] = useState([]);
  const [pagination, setPagination] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadBookmarks();
  }, []);

  const loadBookmarks = async (page = 1) => {
    try {
      const data = await bookmarkService.getBookmarks(page, 10);
      setBookmarks(data.bookmarks);
      setPagination(data.pagination);
    } catch (error) {
      console.error('Failed to load bookmarks:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRemove = async (questionId) => {
    try {
      await bookmarkService.removeBookmark(questionId);
      // Reload bookmarks
      loadBookmarks(pagination?.page || 1);
    } catch (error) {
      console.error('Failed to remove bookmark:', error);
    }
  };

  if (loading) return <div>Loading bookmarks...</div>;

  return (
    <div className="bookmarks">
      <h2>My Bookmarks</h2>

      {bookmarks.length === 0 ? (
        <p>No bookmarks yet. Start bookmarking questions!</p>
      ) : (
        <div className="bookmark-list">
          {bookmarks.map((bookmark) => (
            <div key={bookmark.id} className="bookmark-item">
              <h4>{bookmark.question.question_text}</h4>
              {bookmark.notes && <p className="notes">{bookmark.notes}</p>}
              <div className="meta">
                <span>{bookmark.question.exam_type}</span>
                <span>Domain {bookmark.question.domain}</span>
              </div>
              <button onClick={() => handleRemove(bookmark.question_id)}>
                Remove
              </button>
            </div>
          ))}
        </div>
      )}

      {pagination && pagination.total_pages > 1 && (
        <div className="pagination">
          <button
            onClick={() => loadBookmarks(pagination.page - 1)}
            disabled={pagination.page === 1}
          >
            Previous
          </button>
          <span>
            Page {pagination.page} of {pagination.total_pages}
          </span>
          <button
            onClick={() => loadBookmarks(pagination.page + 1)}
            disabled={pagination.page === pagination.total_pages}
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}
```

## Step 7: Protected Routes

```jsx
// src/components/ProtectedRoute.jsx
import React from 'react';
import { Navigate } from 'react-router-dom';
import { authService } from '../api/auth';

export function ProtectedRoute({ children }) {
  if (!authService.isAuthenticated()) {
    return <Navigate to="/login" />;
  }

  return children;
}

// Usage in App.jsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ProtectedRoute } from './components/ProtectedRoute';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />

        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />

        <Route
          path="/quiz"
          element={
            <ProtectedRoute>
              <Quiz />
            </ProtectedRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}
```

## Step 8: Error Handling Hook

```javascript
// src/hooks/useErrorHandler.js
import { useCallback } from 'react';
import { toast } from 'react-toastify'; // or your toast library

export function useErrorHandler() {
  const handleError = useCallback((error) => {
    const errorData = error.response?.data;

    if (!errorData) {
      toast.error('Network error. Please check your connection.');
      return;
    }

    const errorCode = errorData.error?.code;
    const errorMessage = errorData.error?.message;

    switch (errorCode) {
      case 'TOKEN_EXPIRED':
      case 'TOKEN_INVALID':
      case 'UNAUTHORIZED':
        // Handled by interceptor
        break;

      case 'ADMIN_REQUIRED':
      case 'FORBIDDEN':
        toast.error('You do not have permission to access this resource');
        break;

      case 'RESOURCE_NOT_FOUND':
        toast.error('Resource not found');
        break;

      case 'VALIDATION_ERROR':
        if (errorData.errors) {
          errorData.errors.forEach((err) => {
            toast.error(`${err.field}: ${err.message}`);
          });
        }
        break;

      default:
        toast.error(errorMessage || 'An error occurred');
    }
  }, []);

  return { handleError };
}

// Usage
import { useErrorHandler } from '../hooks/useErrorHandler';

function MyComponent() {
  const { handleError } = useErrorHandler();

  const doSomething = async () => {
    try {
      await someApiCall();
    } catch (error) {
      handleError(error);
    }
  };
}
```

## Common Workflows

### Complete Quiz Flow

```javascript
// 1. Load quiz questions
const questions = await questionService.getQuizQuestions('security', 30);

// 2. User answers questions (store in state)
const answers = [
  { question_id: 1, selected_answer: 'A' },
  { question_id: 2, selected_answer: 'C' },
  // ...
];

// 3. Submit quiz
const result = await quizService.submitQuiz('security', answers, 1800);

// 4. Display results
console.log(`Score: ${result.attempt.score}%`);
console.log(`XP Earned: ${result.attempt.xp_earned}`);
```

### Bookmark Flow

```javascript
// 1. Check if already bookmarked
const isBookmarked = await bookmarkService.isBookmarked(questionId);

// 2. If not, bookmark it
if (!isBookmarked) {
  await bookmarkService.createBookmark(questionId, 'Review later');
}

// 3. View all bookmarks
const { bookmarks, pagination } = await bookmarkService.getBookmarks(1, 10);
```

## Testing Your Integration

### Manual Testing Steps

1. **Sign up a new user**
   - POST `/api/v1/auth/signup`
   - Verify you receive tokens
   - Verify tokens are stored in localStorage

2. **Login**
   - POST `/api/v1/auth/login`
   - Verify authentication works

3. **Make authenticated request**
   - GET `/api/v1/bookmarks`
   - Verify token is included in header
   - Verify you receive data

4. **Test token refresh**
   - Wait for token to expire (or manually expire it)
   - Make another request
   - Verify token is refreshed automatically

5. **Test error handling**
   - Try login with wrong credentials
   - Try accessing admin endpoint as regular user
   - Try submitting invalid data

### Integration Testing

```javascript
// test/integration/quiz.test.js
import { authService, quizService, questionService } from '../src/api';

describe('Quiz Flow', () => {
  let user;

  beforeAll(async () => {
    // Sign up test user
    user = await authService.signup(
      'test@example.com',
      'testuser',
      'Test123!'
    );
  });

  it('should complete quiz flow', async () => {
    // Get questions
    const questions = await questionService.getQuizQuestions('security', 5);
    expect(questions).toHaveLength(5);

    // Submit quiz
    const answers = questions.map((q) => ({
      question_id: q.id,
      selected_answer: 'A',
    }));

    const result = await quizService.submitQuiz('security', answers, 300);
    expect(result.attempt).toBeDefined();
    expect(result.attempt.score).toBeGreaterThanOrEqual(0);
  });
});
```

## Best Practices

1. **Always use the API client** - Don't make raw fetch/axios calls
2. **Handle errors consistently** - Use the error handler hook
3. **Store tokens securely** - localStorage is OK for now, consider httpOnly cookies for production
4. **Implement token refresh** - Use the interceptor pattern
5. **Show loading states** - Always show loading indicators
6. **Validate input** - Validate on frontend before sending to API
7. **Log errors** - Log full error objects for debugging
8. **Test error scenarios** - Test what happens when API is down, token expires, etc.

## Troubleshooting

### CORS Errors
```
Access to XMLHttpRequest blocked by CORS policy
```
**Solution:** Make sure your frontend is running on `localhost:8080`

### 401 Unauthorized
```
{ "error": { "code": "UNAUTHORIZED" } }
```
**Solution:** Check that access token is being sent in Authorization header

### Token Refresh Loop
```
Infinite loop of token refresh requests
```
**Solution:** Check `_retry` flag in interceptor to prevent infinite loops

## Next Steps

You now have everything needed to build a complete frontend! Start with:

1. Authentication flow (signup/login)
2. Quiz taking feature
3. Bookmark management
4. Leaderboard display

Happy coding!
