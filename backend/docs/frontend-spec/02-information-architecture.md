# Information Architecture

Complete site structure, navigation patterns, and user flows for the CompTIA Practice Platform.

---

## Site Map

```
Public (Unauthenticated)
├── Landing Page (/)
├── Login (/login)
├── Signup (/signup)
├── Forgot Password (/forgot-password)
└── Reset Password (/reset-password?token=xxx)

Authenticated App (/app)
├── Dashboard (/app/dashboard)
│
├── Practice Mode
│   ├── Exam Selection (/app/practice)
│   ├── Quiz Taking (/app/practice/:examType/quiz)
│   ├── Quiz Results (/app/practice/:examType/results/:attemptId)
│   └── Quiz History (/app/practice/history)
│
├── Study Mode
│   ├── Study Session Setup (/app/study)
│   ├── Active Study Session (/app/study/:sessionId)
│   └── Study Complete (/app/study/:sessionId/complete)
│
├── Gamification
│   ├── Achievements Gallery (/app/achievements)
│   ├── Achievement Detail (/app/achievements/:achievementId)
│   ├── Avatar Selection (/app/avatars)
│   └── Level Progress (/app/profile#progress)
│
├── Leaderboards
│   ├── XP Leaderboard (/app/leaderboard/xp)
│   ├── Quiz Count (/app/leaderboard/quizzes)
│   ├── Accuracy (/app/leaderboard/accuracy)
│   ├── Streaks (/app/leaderboard/streaks)
│   └── Exam-Specific (/app/leaderboard/:examType)
│
├── Profile & Settings
│   ├── My Profile (/app/profile)
│   ├── Edit Profile (/app/profile/edit)
│   ├── Public Profile View (/app/users/:userId)
│   ├── Account Settings (/app/settings)
│   ├── Session Management (/app/settings/sessions)
│   └── Audit Logs (/app/settings/audit)
│
├── Bookmarks
│   ├── Bookmarks List (/app/bookmarks)
│   ├── Bookmark Detail (/app/bookmarks/:bookmarkId)
│   └── Quick Quiz from Bookmarks (/app/bookmarks/quiz)
│
└── Admin Panel (/app/admin) [Admin only]
    ├── Dashboard (/app/admin)
    ├── User Management (/app/admin/users)
    ├── User Detail (/app/admin/users/:userId)
    ├── Question Management (/app/admin/questions)
    ├── Question Editor (/app/admin/questions/:questionId/edit)
    ├── Achievement Management (/app/admin/achievements)
    └── Achievement Editor (/app/admin/achievements/:achievementId/edit)
```

**Total Pages:** ~35 unique routes

---

## Navigation Structure

### Primary Navigation (Sidebar - Desktop)

**Always Visible When Authenticated:**

```
┌─────────────────────────────┐
│ [Logo] Billings Practice    │
│                              │
│ ┌─────────────────────────┐ │
│ │ User Profile Card       │ │
│ │ Avatar + Name + Level   │ │
│ │ XP Progress Bar         │ │
│ └─────────────────────────┘ │
│                              │
│ Navigation Items:            │
│ ■ Dashboard                  │
│ ■ Practice Mode              │
│ ■ Study Mode                 │
│ ■ Achievements               │
│ ■ Leaderboards               │
│ ■ Bookmarks                  │
│ ■ My Profile                 │
│                              │
│ Admin Section: [if admin]    │
│ ■ Admin Panel                │
│                              │
│ Bottom:                      │
│ ⚙ Settings                   │
│ ↗ Logout                     │
└─────────────────────────────┘
```

**Behavior:**
- Collapsible on tablet/small laptop (icon-only mode)
- Active route highlighted with primary-600 background
- Hover states show tooltip in collapsed mode
- Sticky position (always visible when scrolling)

### Mobile Navigation (Bottom Tab Bar)

**5 Primary Tabs (< 768px):**

```
┌───────────────────────────────────────┐
│  Dashboard  Practice  Study  More    │
│     🏠        📝        📚      ⋯     │
└───────────────────────────────────────┘
```

**More Menu (Sheet/Drawer):**
- Achievements
- Leaderboards
- Bookmarks
- Profile
- Settings
- Admin Panel (if admin)
- Logout

### Secondary Navigation (In-Page Tabs)

**Leaderboards Page:**
```
[ XP ] [ Quizzes ] [ Accuracy ] [ Streaks ] [ Exam-Specific ▼ ]
```

**Settings Page:**
```
[ Profile ] [ Account ] [ Sessions ] [ Audit Logs ]
```

**Admin Panel:**
```
[ Dashboard ] [ Users ] [ Questions ] [ Achievements ]
```

---

## Page Hierarchy & Access Control

### Public Pages (No Auth Required)
- Landing page
- Login
- Signup
- Forgot password
- Reset password
- Email verification callback

### Authenticated Pages (Requires Valid JWT)
- All `/app/*` routes
- Redirects to `/login` if not authenticated
- Stores intended destination for post-login redirect

### Admin Pages (Requires `is_admin: true`)
- All `/app/admin/*` routes
- Returns 403 Forbidden if not admin
- Hidden from navigation for non-admin users

---

## Critical User Flows

### Flow 1: New User Onboarding

```
1. Land on Homepage
   ↓
2. Click "Get Started" → Signup Page
   ↓
3. Fill form (email, username, password)
   ↓
4. Submit → Account created → Auto-login → Dashboard
   ↓
5. See welcome message + "Take your first quiz" CTA
   ↓
6. Click CTA → Practice Mode → Exam selection
   ↓
7. Select "Security+" → Quiz configuration (domain, count)
   ↓
8. Start quiz → Answer questions
   ↓
9. Submit quiz → Results screen
   ↓
10. 🎉 Achievement unlocked: "First Steps" (modal with confetti)
    ↓
11. View updated XP/level on profile card
    ↓
12. Return to dashboard with updated stats
```

**Duration:** ~5-10 minutes
**Key Touchpoints:** Signup, Dashboard, Quiz, Results, Achievement unlock

---

### Flow 2: Daily Study Session (Returning User)

```
1. Login → Dashboard
   ↓
2. See "Continue Study" card (if active session exists)
   OR "Start Study Mode" card
   ↓
3. Click → Study Session Setup
   ↓
4. Select exam type (Security+) + domain (1.1) + count (20)
   ↓
5. Start session → First question appears
   ↓
6. Read question → Select answer → Submit
   ↓
7. Immediate feedback appears:
   - ✓ Correct! or ✗ Incorrect
   - Explanation for selected answer
   - Explanation for correct answer
   - All option explanations visible
   ↓
8. Click "Next Question" → Repeat steps 6-7
   ↓
9. Answer all 20 questions
   ↓
10. Session complete → Results summary
    - Score: 18/20 (90%)
    - XP earned: +150 XP
    - Check achievements (may unlock new ones)
    ↓
11. Update study streak (if consecutive day)
    - 🔥 Streak notification appears
    ↓
12. Return to dashboard with updated stats
```

**Duration:** ~20-40 minutes
**Key Features:** Session persistence, immediate feedback, streak tracking

---

### Flow 3: Competitive Leaderboard Journey

```
1. Dashboard → See leaderboard preview widget
   ↓
2. Click "View Full Leaderboard" → Leaderboards page
   ↓
3. Default view: XP Leaderboard
   - See top 100 users
   - See own rank highlighted
   - Current rank: #47
   ↓
4. Click on user #1 (top player)
   ↓
5. Navigate to their public profile
   - See username, level, XP
   - See bio (if they set one)
   - See total stats (quizzes, accuracy, streak)
   - See achievement count
   - NO EMAIL or sensitive data visible
   ↓
6. Return to leaderboard
   ↓
7. Switch tab to "Accuracy Leaderboard"
   - See users sorted by average score
   - Current rank: #23 (better!)
   ↓
8. Motivated to improve → Navigate to Practice Mode
   ↓
9. Take quiz → Score 95% → Climb accuracy leaderboard
```

**Duration:** ~5-15 minutes
**Key Features:** Multiple leaderboard types, public profiles, rank tracking

---

### Flow 4: Achievement Hunting

```
1. Navigate to Achievements page
   ↓
2. See achievement grid:
   - Unlocked achievements (colored, earned date)
   - Locked achievements (grayed out, unlock criteria shown)
   ↓
3. Spot "Quiz Marathon" achievement
   - Requires: Complete 50 quizzes
   - Current progress: 32/50
   - Progress bar shown
   ↓
4. Click achievement → Detail modal
   - Shows unlock criteria
   - Shows XP reward (+500 XP)
   - Shows rarity (Rare)
   - Shows unlock percentage (12% of users)
   ↓
5. Close modal → Go to Practice Mode
   ↓
6. Complete quiz → Progress updates (33/50)
   ↓
7. After 17 more quizzes...
   ↓
8. Submit quiz #50 → Results screen
   ↓
9. 🎊 ACHIEVEMENT UNLOCKED animation
   - Full-screen modal
   - Confetti animation
   - "Quiz Marathon" badge grows from center
   - "+500 XP" floats up
   - Achievement sound plays (optional)
   ↓
10. Click "Claim Reward" → Modal closes
    ↓
11. XP updates: Level up from 8 → 9!
    ↓
12. Another celebration modal (level up)
    ↓
13. Return to achievements page → Badge now colored/unlocked
```

**Duration:** Variable (achievement-dependent)
**Key Features:** Progress tracking, unlock animations, XP rewards

---

### Flow 5: Bookmark & Review

```
1. Taking a quiz → Encounter difficult question
   ↓
2. Click "Bookmark" icon → Question saved
   ↓
3. Add note: "Review OSI model layers"
   ↓
4. Continue quiz
   ↓
5. Later: Navigate to Bookmarks page
   ↓
6. See all bookmarked questions (paginated)
   - Question text preview
   - Personal notes
   - Domain/exam type tags
   - Date bookmarked
   ↓
7. Click on bookmarked question → Detail view
   - Full question text
   - All answer options
   - Correct answer revealed
   - Explanation shown
   - Edit notes inline
   ↓
8. Click "Quick Quiz from Bookmarks"
   ↓
9. System generates quiz from all bookmarked questions
   ↓
10. Take quiz → Re-test weak areas
    ↓
11. After mastering: Remove bookmark
```

**Duration:** ~10-20 minutes
**Key Features:** Bookmarking during quiz, notes, quick quiz generation

---

### Flow 6: Admin Content Management

```
1. Admin logs in → Sidebar shows "Admin Panel"
   ↓
2. Navigate to Admin Panel → Dashboard
   - See stats: Total users, total questions, total achievements
   - Recent user activity
   - Question approval queue (if applicable)
   ↓
3. Navigate to "Question Management"
   ↓
4. See all questions (paginated, searchable, filterable)
   - Filter by exam type: Security+
   - Search: "encryption"
   ↓
5. Click "Create New Question"
   ↓
6. Fill form:
   - Question ID: SEC999
   - Exam type: Security+
   - Domain: 1.1
   - Question text: "What is AES?"
   - Option A: Text + Explanation
   - Option B: Text + Explanation (mark as correct)
   - Option C: Text + Explanation
   - Option D: Text + Explanation
   ↓
7. Submit → Question created
   ↓
8. Immediately available in quiz pool for users
   ↓
9. Navigate to "User Management"
   ↓
10. Search for user: "johndoe"
    ↓
11. View user detail:
    - Account info
    - Quiz history
    - Achievements
    - Toggle admin status
    - Activate/deactivate account
    ↓
12. Make user admin → Confirmation modal → Confirmed
    ↓
13. User now has admin access
```

**Duration:** ~10-30 minutes
**Key Features:** CRUD operations, user management, real-time updates

---

## Information Hierarchy (Dashboard Example)

```
Dashboard Page Structure:

┌─────────────────────────────────────────────────────┐
│ Header                                               │
│ ┌─────────────────────────────────────────────────┐ │
│ │ Welcome back, [Username]! 👋                    │ │
│ │ Current streak: 🔥 7 days                        │ │
│ └─────────────────────────────────────────────────┘ │
│                                                      │
│ Stats Cards (Grid)                                   │
│ ┌───────────┬───────────┬───────────┬───────────┐  │
│ │ Level 8   │ 2,450 XP  │ 32 Quizzes│ 87% Avg   │  │
│ │ Progress  │ to Lvl 9  │ Completed │ Accuracy  │  │
│ └───────────┴───────────┴───────────┴───────────┘  │
│                                                      │
│ Quick Actions                                        │
│ ┌──────────────────┬──────────────────┐             │
│ │ [Start Practice] │ [Continue Study] │             │
│ └──────────────────┴──────────────────┘             │
│                                                      │
│ Recent Activity                                      │
│ ┌─────────────────────────────────────────────────┐ │
│ │ Quiz: Network+ | Score: 90% | 2 hours ago       │ │
│ │ 🏆 Achievement: "Perfect Score" unlocked         │ │
│ │ Bookmark added: "TCP vs UDP question"           │ │
│ └─────────────────────────────────────────────────┘ │
│                                                      │
│ Achievements Preview                                 │
│ ┌───────┬───────┬───────┬───────┬───────┐          │
│ │ [🏆]  │ [🎯]  │ [⭐]  │ [🔒]  │ [🔒]  │          │
│ │ First │ Marathon│ Perfect│ [Locked] │ [Locked] │  │
│ └───────┴───────┴───────┴───────┴───────┘          │
│ [View All Achievements →]                            │
│                                                      │
│ Leaderboard Preview                                  │
│ ┌─────────────────────────────────────────────────┐ │
│ │ 1. AliceStudies     5,000 XP  [View]            │ │
│ │ 2. BobCertified     4,850 XP  [View]            │ │
│ │ ...                                             │ │
│ │ 47. You (YourName)  2,450 XP                    │ │
│ └─────────────────────────────────────────────────┘ │
│ [View Full Leaderboard →]                            │
└─────────────────────────────────────────────────────┘
```

**Hierarchy Principles:**
1. **Welcome & Streak** - Top (most important for engagement)
2. **Stats Cards** - Primary metrics (level, XP, performance)
3. **Quick Actions** - High-frequency tasks (start quiz)
4. **Recent Activity** - Context and continuity
5. **Previews** - Achievements and leaderboard teasers
6. **CTAs** - Clear next actions throughout

---

## Navigation Patterns

### Breadcrumbs (Desktop)

Used for deep navigation paths:

```
Dashboard > Practice Mode > Security+ > Quiz #42
[Home]    [Practice]     [Security+]   [Current]
```

**Rules:**
- Max 4 levels deep
- Current page not clickable
- Each level is a link to parent
- Hidden on mobile (limited space)

### Back Button Pattern

**In Quiz/Study Mode:**
- Show confirmation modal: "Are you sure? Progress will be lost."
- Options: "Keep Going" (primary) | "Exit Quiz" (secondary)

**In Profile/Settings:**
- Standard back navigation, no confirmation

### Tab Persistence

**URL reflects active tab:**
```
/app/leaderboard/xp        → XP tab active
/app/leaderboard/accuracy  → Accuracy tab active
/app/settings?tab=sessions → Sessions tab active
```

**Benefits:**
- Shareable URLs
- Browser back/forward works
- Refresh preserves state

---

## Search & Filtering

### Global Search (Optional - Phase 2)

**Accessible from:**
- Sidebar (keyboard shortcut: Cmd+K / Ctrl+K)
- Header search icon

**Searches:**
- Achievements (by name/description)
- Questions (bookmarked only)
- Users (leaderboard)

### Contextual Filters

**Quiz History:**
- Filter by exam type
- Filter by date range
- Filter by score range
- Sort by date/score

**Bookmarks:**
- Filter by exam type
- Filter by domain
- Search notes
- Sort by date added/question ID

**Leaderboard:**
- Filter by time period (All time, This month, This week)
- Filter by exam type (for exam-specific leaderboard)

**Admin Question Management:**
- Filter by exam type
- Filter by domain
- Search by question text/ID
- Sort by created date/question ID

---

## Empty States

### No Data States (First-Time Users)

**Dashboard (No quizzes taken):**
```
┌─────────────────────────────────────┐
│         📚                          │
│   Welcome to Billings Practice!    │
│                                     │
│   Take your first quiz to start    │
│   tracking your progress.           │
│                                     │
│   [Start Your First Quiz]           │
└─────────────────────────────────────┘
```

**Bookmarks (None saved):**
```
┌─────────────────────────────────────┐
│         🔖                          │
│   No bookmarks yet                  │
│                                     │
│   Bookmark questions during quizzes │
│   to review them later.             │
└─────────────────────────────────────┘
```

**Achievements (None unlocked):**
```
┌─────────────────────────────────────┐
│   [🔒] [🔒] [🔒] [🔒] [🔒]         │
│                                     │
│   Complete quizzes to unlock        │
│   achievements and earn XP!         │
│                                     │
│   [Take a Quiz]                     │
└─────────────────────────────────────┘
```

### Error States

**Network Error:**
```
┌─────────────────────────────────────┐
│         ⚠️                          │
│   Connection Lost                   │
│                                     │
│   Check your internet connection    │
│   and try again.                    │
│                                     │
│   [Retry]                           │
└─────────────────────────────────────┘
```

**404 Not Found:**
```
┌─────────────────────────────────────┐
│         404                         │
│   Page Not Found                    │
│                                     │
│   The page you're looking for       │
│   doesn't exist.                    │
│                                     │
│   [Go to Dashboard]                 │
└─────────────────────────────────────┘
```

**403 Forbidden (Non-admin accessing admin):**
```
┌─────────────────────────────────────┐
│         🚫                          │
│   Access Denied                     │
│                                     │
│   You don't have permission to      │
│   view this page.                   │
│                                     │
│   [Go Back]                         │
└─────────────────────────────────────┘
```

---

## Mobile Considerations

### Responsive Breakpoints

**Mobile (< 640px):**
- Single column layout
- Bottom tab navigation
- Collapsible sections
- Full-width cards
- Stacked stats

**Tablet (640px - 1024px):**
- Two column layout
- Collapsible sidebar (icon-only)
- Grid stats (2 columns)
- Larger touch targets

**Desktop (> 1024px):**
- Full sidebar navigation
- Multi-column layout
- Grid stats (4 columns)
- Hover states enabled

### Touch Interactions

**Swipe Gestures:**
- Swipe between quiz questions (left/right)
- Swipe to dismiss modals (down)
- Pull to refresh on lists (down)

**Tap Targets:**
- Minimum 44x44px (WCAG 2.1 Level AAA)
- 8px spacing between interactive elements

---

## URL Structure

### RESTful Conventions

**Collections:**
```
/app/practice          → List of exams
/app/achievements      → Grid of achievements
/app/bookmarks         → List of bookmarks
```

**Details:**
```
/app/practice/security           → Security+ exam detail
/app/achievements/first-steps    → Achievement detail
/app/users/123                   → User profile
```

**Actions:**
```
/app/practice/security/quiz      → Active quiz
/app/study/session-123           → Active study session
/app/profile/edit                → Edit form
```

**Query Parameters:**
```
/app/leaderboard/xp?period=month → Filter by month
/app/bookmarks?page=2            → Pagination
/app/quiz/history?exam=security  → Filter results
```

---

## Accessibility Navigation

### Keyboard Shortcuts (Optional - Phase 2)

```
Global:
- Cmd/Ctrl + K    → Open search
- Cmd/Ctrl + /    → Focus sidebar navigation
- Esc             → Close modal/drawer

Quiz:
- 1, 2, 3, 4      → Select answer A, B, C, D
- Enter           → Submit answer
- Space           → Next question
- Cmd/Ctrl + B    → Bookmark question
```

### Skip Links

```html
<a href="#main-content" class="sr-only focus:not-sr-only">
  Skip to main content
</a>
```

### Focus Management

**On Modal Open:**
- Focus first interactive element (close button or primary CTA)

**On Modal Close:**
- Return focus to trigger element

**On Page Navigation:**
- Focus main heading (h1) for screen reader announcement

---

## State Management Considerations

### Global State (Zustand)
- User profile data
- Auth tokens
- Quiz state (current answers, timer)
- Active study session

### Server State (React Query)
- All API data (cached, auto-refetch)
- Leaderboards (30s polling)
- Achievements (refetch on quiz complete)
- User stats (refetch on profile view)

### Local State (useState)
- Form inputs
- UI toggles (sidebar collapsed, modals open)
- Pagination current page
- Filter selections

---

**Next:** Review page specifications (03-page-specifications.md)
