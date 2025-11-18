# Frontend Integration Reference

## Current State
The frontend is **temporary** - vanilla HTML/CSS/JavaScript for basic functionality only.
The backend is fully developed with all features. The frontend will be **rebuilt from scratch** later.

---

## Current Frontend Files

```
frontend/
├── index.html              # Landing/login page
├── dashboard.html          # User dashboard
├── quiz-select.html        # Quiz type selection
├── quiz.html               # Quiz taking interface
├── results.html            # Quiz results page
├── css/
│   └── styles.css          # Basic styling
└── js/
    ├── config.js           # API base URL config
    ├── quiz-select.js      # Quiz selection logic
    ├── quiz.js             # Quiz taking logic
    └── results.js          # Results display logic
```

**Note**: This structure will change when we rebuild. Don't invest heavily in documenting or improving it.

---

## API Configuration

**File**: `frontend/js/config.js`

```javascript
const API_BASE_URL = 'http://localhost:8000/api/v1';
```

This is the only configuration needed. All API endpoints are relative to this base URL.

---

## Future Integration Points

When rebuilding the frontend, here are the key integrations needed:

### 1. Authentication Pages
- **Login**: `POST /auth/login` → Get JWT token, store in localStorage
- **Signup**: `POST /auth/signup` → Create account + auto-login
- **Profile**: `GET /auth/me` → Display user stats (XP, level, streak)

### 2. Quiz Pages
- **Quiz Selection**: `GET /questions/exams` → List available exam types
- **Quiz Taking**: `GET /questions/quiz?exam_type=X&count=30` → Get questions
- **Quiz Submission**: `POST /quiz/submit` → Submit answers, get XP, achievements
- **Quiz History**: `GET /quiz/history` → Show past attempts
- **Quiz Stats**: `GET /quiz/stats` → Show performance analytics

### 3. Gamification Pages
- **Achievements Page**:
  - `GET /achievements/me` → Show all achievements with progress bars
  - Display earned/unearned, progress percentage, XP rewards
  - Show "First Steps" prominently as the first achievement to earn

- **Avatars Page**:
  - `GET /avatars/me` → Show all avatars with unlock status
  - `POST /avatars/select` → Equip selected avatar
  - `GET /avatars/stats` → Show collection stats (5/18 unlocked, etc.)
  - Display avatar rarity (common, rare, epic, legendary) with colors

- **Leaderboards Page**:
  - `GET /leaderboard/xp` → Top users by XP
  - `GET /leaderboard/quiz-count` → Top users by quiz count
  - `GET /leaderboard/accuracy` → Top users by accuracy
  - `GET /leaderboard/streak` → Top users by streak
  - `GET /leaderboard/exam/{exam_type}` → Exam-specific leaderboard
  - Tabs to switch between leaderboard types

### 4. Dashboard/Profile Page
- Display user stats: XP, level, current streak, total quizzes
- Show XP progress to next level (progress bar)
- Show recent quiz attempts
- Show recently unlocked achievements (last 3)
- Show equipped avatar
- Link to full achievements page, avatars page, leaderboards

---

## Key Features to Implement

### Achievement Unlocked Notification
When `POST /quiz/submit` returns `achievements_unlocked[]`, show a modal/toast:

```javascript
// Example response
{
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

// Show notification for each achievement
achievements_unlocked.forEach(achievement => {
  showAchievementModal(achievement);
});
```

### Level Up Notification
When `level_up: true` in quiz submission response, show celebration:

```javascript
if (response.level_up) {
  showLevelUpModal(response.new_level);
}
```

### XP Progress Bar
Show progress to next level:

```javascript
// XP for levels (from GAMIFICATION.md)
function xpForLevel(level) {
  return (level - 1) ** 2 * 100;
}

function xpToNextLevel(currentXp, currentLevel) {
  const nextLevelXp = xpForLevel(currentLevel + 1);
  const currentLevelXp = xpForLevel(currentLevel);
  return nextLevelXp - currentXp;
}

// Progress percentage
function levelProgress(currentXp, currentLevel) {
  const currentLevelXp = xpForLevel(currentLevel);
  const nextLevelXp = xpForLevel(currentLevel + 1);
  const xpIntoLevel = currentXp - currentLevelXp;
  const xpNeeded = nextLevelXp - currentLevelXp;
  return (xpIntoLevel / xpNeeded) * 100;
}
```

### Achievement Progress
Display progress bars for unearned achievements:

```javascript
// From GET /achievements/me
{
  "name": "Sharp Shooter",
  "progress": 7,
  "progress_percentage": 70.0,
  "criteria_value": 10,
  "is_earned": false
}

// Render:
// Sharp Shooter
// [███████---] 70% (7/10)
```

### Avatar Display
Show avatar image with rarity indicator:

```javascript
// Avatar with rarity
<div class="avatar ${avatar.rarity}">
  <img src="${avatar.image_url}" alt="${avatar.name}">
  <span class="rarity-badge">${avatar.rarity}</span>
</div>

// CSS for rarity
.avatar.common { border-color: #gray; }
.avatar.rare { border-color: #blue; }
.avatar.epic { border-color: #purple; }
.avatar.legendary { border-color: #gold; }
```

---

## Authentication Flow

### Store JWT Token
```javascript
// After login/signup
const token = response.access_token;
localStorage.setItem('jwt_token', token);
```

### Include Token in Requests
```javascript
const token = localStorage.getItem('jwt_token');

fetch(`${API_BASE_URL}/quiz/submit`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify(quizSubmission)
});
```

### Handle 401 Unauthorized
```javascript
if (response.status === 401) {
  // Token expired or invalid
  localStorage.removeItem('jwt_token');
  window.location.href = '/index.html'; // Redirect to login
}
```

---

## Example API Calls

### Get User Profile
```javascript
async function getUserProfile() {
  const token = localStorage.getItem('jwt_token');
  const response = await fetch(`${API_BASE_URL}/auth/me`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });

  const data = await response.json();
  return data;
}
```

### Get Achievements with Progress
```javascript
async function getAchievements() {
  const token = localStorage.getItem('jwt_token');
  const response = await fetch(`${API_BASE_URL}/achievements/me`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });

  const data = await response.json();
  return data.achievements;
}
```

### Submit Quiz
```javascript
async function submitQuiz(quizSubmission) {
  const token = localStorage.getItem('jwt_token');
  const response = await fetch(`${API_BASE_URL}/quiz/submit`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(quizSubmission)
  });

  const data = await response.json();

  // Handle achievements unlocked
  if (data.achievements_unlocked.length > 0) {
    data.achievements_unlocked.forEach(achievement => {
      showAchievementNotification(achievement);
    });
  }

  // Handle level up
  if (data.level_up) {
    showLevelUpNotification(data.new_level);
  }

  return data;
}
```

---

## Recommended Frontend Framework (Future)

When rebuilding:
- **React** or **Vue** or **Svelte** (pick one)
- **TailwindCSS** for styling
- **React Query** or **SWR** for API caching
- **React Router** or **Vue Router** for navigation
- **Zustand** or **Pinia** for state management

---

## Pages to Build (Priority Order)

1. **Login/Signup** - Get users in
2. **Dashboard** - Show stats, recent activity
3. **Quiz Taking** - Core functionality
4. **Quiz Results** - Show score, XP, achievements
5. **Achievements** - Show all achievements with progress
6. **Avatars** - Collection page with unlock status
7. **Leaderboards** - 5 leaderboard types
8. **Profile** - Detailed user stats, settings

---

## Design Considerations

### Gamification UI Elements
- **Progress bars** for XP, achievement progress
- **Badges/icons** for achievements (use badge_icon_url)
- **Avatar frames** with rarity colors
- **Level display** prominently on profile/dashboard
- **Streak counter** with flame icon
- **Leaderboard rankings** with podium for top 3
- **Achievement unlock animations** (modal with confetti)
- **Level up animation** (screen flash, confetti, sound)

### Responsive Design
- Mobile-first approach
- Quiz taking on mobile (one question per screen)
- Leaderboards scroll horizontally on mobile
- Achievement grid layout (2 columns on mobile, 4 on desktop)

---

## API Error Handling

```javascript
async function apiRequest(endpoint, options = {}) {
  const token = localStorage.getItem('jwt_token');

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': token ? `Bearer ${token}` : '',
      ...options.headers
    }
  });

  if (response.status === 401) {
    // Unauthorized - redirect to login
    localStorage.removeItem('jwt_token');
    window.location.href = '/login';
    return;
  }

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'API request failed');
  }

  return response.json();
}

// Usage
try {
  const data = await apiRequest('/quiz/history', { method: 'GET' });
  renderQuizHistory(data);
} catch (error) {
  showErrorNotification(error.message);
}
```

---

## Summary

The current frontend is **temporary** for basic testing. When rebuilding:

1. Use a modern framework (React/Vue/Svelte)
2. All backend features are ready to integrate (23 endpoints)
3. Focus on gamification UX (achievements, avatars, leaderboards)
4. Reference `API_ENDPOINTS.md` for complete API documentation
5. Reference `GAMIFICATION.md` for XP/level formulas and achievement details

The backend is **complete and production-ready**. The frontend can be built whenever ready.
