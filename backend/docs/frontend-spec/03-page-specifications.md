# Page Specifications

Detailed specifications for all major pages in the CompTIA Practice Platform.

---

## 1. Dashboard Page

**Route:** `/app/dashboard`
**Auth Required:** Yes
**API Calls:**
- `GET /api/v1/auth/me` - User profile with stats
- `GET /api/v1/quiz/history?limit=5` - Recent quizzes
- `GET /api/v1/achievements/earned?limit=5` - Recent achievements
- `GET /api/v1/leaderboard/xp?limit=5` - Top 5 leaderboard preview

### Layout

```
┌────────────────────────────────────────────────────────┐
│ Header                                                  │
│ ┌────────────────────────────────────────────────────┐ │
│ │ "Welcome back, [Username]! 👋"                     │ │
│ │ Study Streak: 🔥 [7] days | [Continue Streak]     │ │
│ └────────────────────────────────────────────────────┘ │
│                                                         │
│ Stats Grid (4 columns on desktop, 2 on tablet, 1 mobile)│
│ ┌───────────┬───────────┬───────────┬───────────┐     │
│ │ Level 8   │ 2,450 XP  │ 32 Quizzes│ 87% Avg   │     │
│ │ Progress  │ 150 to 9  │ Completed │ Accuracy  │     │
│ │ [─────▓░] │           │           │           │     │
│ └───────────┴───────────┴───────────┴───────────┘     │
│                                                         │
│ Quick Actions (2 columns)                               │
│ ┌──────────────────────┬──────────────────────┐        │
│ │ 📝 Start Practice    │ 📚 Continue Study    │        │
│ │ Take a quiz to earn  │ Resume session #42   │        │
│ │ XP and achievements  │ 12 questions left    │        │
│ │ [Start Quiz →]       │ [Continue →]         │        │
│ └──────────────────────┴──────────────────────┘        │
│                                                         │
│ Recent Activity (List)                                  │
│ ┌──────────────────────────────────────────────────┐   │
│ │ ■ Network+ Quiz | 90% | 2 hours ago            │   │
│ │ ■ 🏆 Achievement "Perfect Score" unlocked       │   │
│ │ ■ Bookmarked: "TCP vs UDP question"            │   │
│ │ ■ Security+ Quiz | 85% | 1 day ago             │   │
│ └──────────────────────────────────────────────────┘   │
│                                                         │
│ Achievements Preview (Horizontal scroll)                │
│ ┌───────┬───────┬───────┬───────┬───────┐             │
│ │ [🏆]  │ [🎯]  │ [⭐]  │ [🔒]  │ [🔒]  │             │
│ │ First │Marathon│Perfect│Locked │Locked │             │
│ └───────┴───────┴───────┴───────┴───────┘             │
│ [View All →]                                            │
│                                                         │
│ Leaderboard Preview                                     │
│ ┌──────────────────────────────────────────────────┐   │
│ │ 🥇 AliceStudies    5,000 XP                      │   │
│ │ 🥈 BobCertified    4,850 XP                      │   │
│ │ 🥉 CharlieCoder    4,200 XP                      │   │
│ │ ...                                              │   │
│ │ 47. You            2,450 XP  ← (highlighted)     │   │
│ └──────────────────────────────────────────────────┘   │
│ [View Full Leaderboard →]                               │
└─────────────────────────────────────────────────────────┘
```

### Components Used
- `ProfileCard` - User avatar, name, level, XP bar
- `StatCard` (x4) - Level, XP, Quizzes, Accuracy
- `QuickActionCard` (x2) - Practice, Study mode CTAs
- `ActivityFeed` - Recent activities list
- `AchievementPreview` - Horizontal scrollable badges
- `LeaderboardPreview` - Top 5 + user rank

### State Requirements
- User profile data (from React Query)
- Recent activities (cached)
- Active study session check (conditional CTA)

### Responsive Behavior
- **Desktop:** 4-column stats grid, 2-column actions
- **Tablet:** 2-column stats grid, 2-column actions
- **Mobile:** 1-column all, horizontal scroll for achievements

### Empty States
- No quizzes: "Take your first quiz!" CTA
- No achievements: "Complete quizzes to unlock achievements"
- No streak: "Start your study streak today!"

---

## 2. Practice Mode - Exam Selection

**Route:** `/app/practice`
**Auth Required:** Yes
**API Calls:**
- `GET /api/v1/questions/exams` - List of available exams

### Layout

```
┌────────────────────────────────────────────────────────┐
│ Header                                                  │
│ ┌────────────────────────────────────────────────────┐ │
│ │ Practice Mode                                      │ │
│ │ Choose an exam to practice                         │ │
│ └────────────────────────────────────────────────────┘ │
│                                                         │
│ Exam Cards Grid (2 columns desktop, 1 mobile)          │
│ ┌──────────────────────────┬──────────────────────────┐│
│ │ Security+ (SY0-701)      │ Network+ (N10-009)       ││
│ │                          │                          ││
│ │ 450 questions            │ 320 questions            ││
│ │ 5 domains                │ 6 domains                ││
│ │                          │                          ││
│ │ Your progress:           │ Your progress:           ││
│ │ [──────▓░░] 65%          │ [───▓░░░░░] 40%          ││
│ │                          │                          ││
│ │ [Start Practice →]       │ [Start Practice →]       ││
│ └──────────────────────────┴──────────────────────────┘│
│ ┌──────────────────────────┬──────────────────────────┐│
│ │ Linux+ (XK0-005)         │ CySA+ (CS0-003)          ││
│ │ [Coming Soon]            │ [Coming Soon]            ││
│ └──────────────────────────┴──────────────────────────┘│
└─────────────────────────────────────────────────────────┘
```

### Components
- `ExamCard` - Clickable card with exam details
- `ProgressBar` - User's completion percentage per exam

### Interactions
- Click card → Navigate to quiz configuration
- Hover shows exam description tooltip
- "Coming Soon" cards are non-clickable, grayed out

---

## 3. Practice Mode - Quiz Configuration

**Route:** `/app/practice/:examType`
**Auth Required:** Yes
**API Calls:** None (just UI configuration)

### Layout

```
┌────────────────────────────────────────────────────────┐
│ Security+ Practice Quiz                                 │
│                                                         │
│ Configure Your Quiz                                     │
│ ┌────────────────────────────────────────────────────┐ │
│ │ Number of Questions                                │ │
│ │ ┌──────────────────────────────────────────────┐   │ │
│ │ │ [10] [20] [30▼] [50] [Custom: ___]          │   │ │
│ │ └──────────────────────────────────────────────┘   │ │
│ │                                                    │ │
│ │ Domain Filter (Optional)                           │ │
│ │ ┌──────────────────────────────────────────────┐   │ │
│ │ │ [ ] All Domains                              │   │ │
│ │ │ [ ] 1.1 - Security Concepts                  │   │ │
│ │ │ [ ] 1.2 - Threat Actors & Vectors            │   │ │
│ │ │ [ ] 2.1 - Security Architecture              │   │ │
│ │ │ [Show More ▼]                                │   │ │
│ │ └──────────────────────────────────────────────┘   │ │
│ │                                                    │ │
│ │ Quiz Mode                                          │ │
│ │ ┌──────────────────────────────────────────────┐   │ │
│ │ │ ● Timed (90 seconds per question)            │   │ │
│ │ │ ○ Untimed (practice at your own pace)        │   │ │
│ │ └──────────────────────────────────────────────┘   │ │
│ │                                                    │ │
│ │ [Cancel]  [Start Quiz →]                          │ │
│ └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### Components
- `QuizConfigForm` - Form with question count, domain, timer
- `DomainCheckboxList` - Multi-select domain filter
- `Button` - Cancel, Start Quiz

### Validation
- Question count: 1-100
- At least one domain selected (or "All")
- If custom count, must be number

---

## 4. Practice Mode - Quiz Taking

**Route:** `/app/practice/:examType/quiz`
**Auth Required:** Yes
**API Calls:**
- `GET /api/v1/questions/quiz?exam_type=X&count=Y&domain=Z` - Fetch questions

### Layout

```
┌────────────────────────────────────────────────────────┐
│ Quiz Header                                             │
│ ┌────────────────────────────────────────────────────┐ │
│ │ Security+ Practice | Question 5 of 30 | ⏱ 1:23:45  │ │
│ │ [──────▓░░░░░░░░░░░░░░░░░░░░░░░░] 17% complete    │ │
│ └────────────────────────────────────────────────────┘ │
│                                                         │
│ Question Card                                           │
│ ┌────────────────────────────────────────────────────┐ │
│ │ Question 5                          🔖 Bookmark    │ │
│ │                                                    │ │
│ │ Which of the following BEST describes the purpose │ │
│ │ of implementing a DMZ in a network architecture?  │ │
│ │                                                    │ │
│ │ ○ A. To provide a buffer zone between internal    │ │
│ │      and external networks                        │ │
│ │                                                    │ │
│ │ ○ B. To encrypt all network traffic               │ │
│ │                                                    │ │
│ │ ○ C. To block all incoming connections            │ │
│ │                                                    │ │
│ │ ○ D. To monitor employee internet usage           │ │
│ │                                                    │ │
│ │ Domain: 2.1 - Security Architecture               │ │
│ │                                                    │ │
│ │ [← Previous]          [Flag for Review]  [Next →] │ │
│ └────────────────────────────────────────────────────┘ │
│                                                         │
│ Question Navigator (Bottom)                             │
│ ┌────────────────────────────────────────────────────┐ │
│ │ [1✓] [2✓] [3✓] [4✓] [5] [6] [7] ... [30]  [Submit]│ │
│ │ ✓=answered, 🚩=flagged, empty=unanswered            │ │
│ └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### Components
- `QuizHeader` - Progress bar, timer, question count
- `QuestionCard` - Question text, options (radio), bookmark button
- `QuestionNavigator` - Grid of question numbers

### State Management
- `quizState` (Zustand):
  ```typescript
  {
    questions: Question[],
    answers: Record<number, string>,  // questionId -> selectedAnswer
    currentQuestionIndex: number,
    flaggedQuestions: Set<number>,
    timeRemaining: number,  // seconds
    startTime: Date
  }
  ```

### Interactions
- Select answer → Update state, auto-save to localStorage
- Click Next → Move to next question
- Click question number → Jump to that question
- Click Bookmark → Call bookmark API
- Click Flag → Mark question for review
- Click Submit → Confirmation modal → Navigate to results

### Timer Behavior
- If timed: Count down from total time (question_count * 90s)
- Show warning at 5 minutes remaining (warning color)
- At 0:00 → Auto-submit quiz
- If untimed: Count up from 0 (show total time spent)

### Keyboard Shortcuts
- `1-4` or `A-D`: Select answer
- `Enter`: Next question
- `Space`: Flag for review
- `Cmd/Ctrl + B`: Bookmark

### Confirmation Modals
- **Exit quiz:** "Are you sure? Progress will be lost."
- **Submit quiz:** "Submit 30 answers? (5 flagged for review)"

---

## 5. Practice Mode - Results

**Route:** `/app/practice/:examType/results/:attemptId`
**Auth Required:** Yes
**API Calls:**
- `GET /api/v1/quiz/history/{attemptId}` - Quiz attempt details with results

### Layout

```
┌────────────────────────────────────────────────────────┐
│ Quiz Results                                            │
│                                                         │
│ Score Circle (Center)                                   │
│ ┌────────────────────────────────────────────────────┐ │
│ │         ┌─────────┐                                │ │
│ │         │  85%    │  (Circular progress)           │ │
│ │         │ 26/30   │                                │ │
│ │         └─────────┘                                │ │
│ │    Great job! You passed!                          │ │
│ └────────────────────────────────────────────────────┘ │
│                                                         │
│ Stats Grid                                              │
│ ┌───────────┬───────────┬───────────┬───────────┐     │
│ │ Correct   │ Incorrect │ Time Spent│ XP Earned │     │
│ │    26     │     4     │  45:23    │   +180    │     │
│ └───────────┴───────────┴───────────┴───────────┘     │
│                                                         │
│ 🎉 NEW ACHIEVEMENTS UNLOCKED!                          │
│ ┌────────────────────────┬────────────────────────┐    │
│ │ 🏆 High Achiever       │ ⭐ Perfect Domain      │    │
│ │ Score 80%+ on a quiz   │ 100% on Domain 2.1     │    │
│ │ +50 XP                 │ +30 XP                 │    │
│ └────────────────────────┴────────────────────────┘    │
│                                                         │
│ 📈 LEVEL UP! You're now Level 9!                       │
│ ┌────────────────────────────────────────────────────┐ │
│ │ [───────────────▓] 2,630 XP / 3,000 XP to Level 10 │ │
│ └────────────────────────────────────────────────────┘ │
│                                                         │
│ Review Answers                                          │
│ ┌────────────────────────────────────────────────────┐ │
│ │ ✓ Question 1 | You: A | Correct: A                │ │
│ │ ✓ Question 2 | You: C | Correct: C                │ │
│ │ ✗ Question 3 | You: B | Correct: D [View]         │ │
│ │ ✓ Question 4 | You: A | Correct: A                │ │
│ │ [Show All 30 ▼]                                    │ │
│ └────────────────────────────────────────────────────┘ │
│                                                         │
│ Actions                                                 │
│ ┌──────────────────────────┬──────────────────────────┐│
│ │ [Review Mistakes]        │ [Take New Quiz]          ││
│ │ (4 incorrect questions)  │                          ││
│ └──────────────────────────┴──────────────────────────┘│
│ [Return to Dashboard]                                   │
└─────────────────────────────────────────────────────────┘
```

### Components
- `CircularScoreDisplay` - Large circular progress with percentage
- `StatsGrid` - Correct, incorrect, time, XP
- `AchievementUnlockCard` - New achievements with animation
- `LevelUpBanner` - Level progression notice
- `QuestionReviewList` - Expandable list of all questions

### Animations
- **On page load:**
  - Score circle animates from 0 to actual score (1s)
  - Confetti bursts if score > 90%

- **Achievement unlock:**
  - Modal appears with scale animation
  - Badge grows from center
  - XP counter ticks up
  - Confetti effect

- **Level up:**
  - Screen flash (subtle)
  - Banner slides in from top
  - Progress bar fills smoothly

### Interactions
- Click "View" on incorrect answer → Modal with full question, all explanations
- Click "Review Mistakes" → New quiz with only the 4 incorrect questions
- Click "Take New Quiz" → Back to exam selection

---

## 6. Study Mode - Session Setup

**Route:** `/app/study`
**Auth Required:** Yes
**API Calls:**
- `GET /api/v1/study/active` - Check for active session

### Layout (Similar to Practice Config)

```
┌────────────────────────────────────────────────────────┐
│ Study Mode                                              │
│                                                         │
│ 📚 Learn with immediate feedback                       │
│ Answer questions one at a time and see explanations    │
│ immediately after each answer.                          │
│                                                         │
│ [Resume Active Session] ← if active session exists     │
│                                                         │
│ Configure Study Session                                 │
│ ┌────────────────────────────────────────────────────┐ │
│ │ Exam Type: [Security+ ▼]                          │ │
│ │ Domain: [All Domains ▼]                            │ │
│ │ Question Count: [●10] [○20] [○30]                 │ │
│ │                                                    │ │
│ │ [Cancel]  [Start Studying →]                      │ │
│ └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### If Active Session Exists
- Show "Resume Session" banner at top
- Display: "Session #42 | 8/20 questions answered | Started 2 hours ago"
- CTA: "Resume Session" → Navigate to `/app/study/:sessionId`
- Secondary CTA: "Abandon Session" → Confirmation modal → Delete session

---

## 7. Study Mode - Active Session

**Route:** `/app/study/:sessionId`
**Auth Required:** Yes
**API Calls:**
- `GET /api/v1/study/active` - Get current question
- `POST /api/v1/study/answer` - Submit answer, get next question

### Layout

```
┌────────────────────────────────────────────────────────┐
│ Study Session | Question 8 of 20 | [Abandon Session]  │
│ [──────────▓░░░░░░░░░] 40% complete                    │
│                                                         │
│ Question                                                │
│ ┌────────────────────────────────────────────────────┐ │
│ │ Which protocol operates at the Transport Layer?   │ │
│ │                                                    │ │
│ │ ○ A. IP                                            │ │
│ │ ○ B. TCP                                           │ │
│ │ ○ C. Ethernet                                      │ │
│ │ ○ D. HTTP                                          │ │
│ │                                                    │ │
│ │ [Submit Answer]                                    │ │
│ └────────────────────────────────────────────────────┘ │
│                                                         │
│ [After submission - Feedback appears below]             │
│                                                         │
│ ✓ Correct!                                             │
│ ┌────────────────────────────────────────────────────┐ │
│ │ Your Answer: B - TCP ✓                            │ │
│ │                                                    │ │
│ │ Explanation: TCP (Transmission Control Protocol)  │ │
│ │ operates at Layer 4 (Transport Layer) and provides│ │
│ │ reliable, ordered delivery of data packets.       │ │
│ │                                                    │ │
│ │ Why Other Options Are Wrong:                       │ │
│ │ A. IP - Network Layer (Layer 3)                   │ │
│ │ C. Ethernet - Data Link Layer (Layer 2)           │ │
│ │ D. HTTP - Application Layer (Layer 7)             │ │
│ │                                                    │ │
│ │ +10 XP earned                                      │ │
│ │                                                    │ │
│ │ [Next Question →]                                  │ │
│ └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### Flow
1. Question displayed with options (radio buttons)
2. User selects answer
3. Click "Submit Answer"
4. **Immediate feedback appears:**
   - ✓ Correct! (green) or ✗ Incorrect (red)
   - User's selected answer highlighted
   - Correct answer highlighted (if different)
   - Detailed explanation for correct answer
   - Explanations for all incorrect options
   - XP earned (+10 for correct, +5 for incorrect - still learning)
5. Click "Next Question" → Repeat

### On Last Question
- After submitting answer 20 of 20:
- Show completion screen:
  ```
  🎉 Study Session Complete!

  Score: 18/20 (90%)
  XP Earned: +187 XP
  Time Spent: 42:15

  [View Results] [Start New Session]
  ```

---

## 8. Achievements Gallery

**Route:** `/app/achievements`
**Auth Required:** Yes
**API Calls:**
- `GET /api/v1/achievements` - All achievements
- `GET /api/v1/achievements/earned` - User's earned achievements

### Layout

```
┌────────────────────────────────────────────────────────┐
│ Achievements                                            │
│                                                         │
│ Filter: [All ▼] [Earned] [Locked] | Sort: [Rarity ▼]  │
│                                                         │
│ Progress: 8 of 25 unlocked (32%)                        │
│ ┌────────────────────────────────────────────────────┐ │
│ │ [───────▓░░░░░░░░░░░░░░░░░░░░░] 32%                │ │
│ └────────────────────────────────────────────────────┘ │
│                                                         │
│ Achievement Grid (3 columns desktop, 2 tablet, 1 mobile)│
│ ┌──────────────┬──────────────┬──────────────┐        │
│ │ 🏆           │ 🎯           │ ⭐           │        │
│ │ First Steps  │ Quiz Marathon│ Perfect Score│        │
│ │ Complete 1   │ Complete 50  │ Score 100%   │        │
│ │ quiz         │ quizzes      │ on any quiz  │        │
│ │ +50 XP       │ +500 XP      │ +100 XP      │        │
│ │ ✓ Unlocked   │ 32/50 (64%)  │ ✓ Unlocked   │        │
│ │ Jan 15, 2025 │ [In Progress]│ Jan 20, 2025 │        │
│ └──────────────┴──────────────┴──────────────┘        │
│ ┌──────────────┬──────────────┬──────────────┐        │
│ │ 🔒           │ 🔒           │ 🔒           │        │
│ │ Streak Master│ Domain Expert│ Early Bird   │        │
│ │ 30-day streak│ Master all   │ Study before │        │
│ │ 7/30 days    │ domains      │ 8 AM         │        │
│ │ +1000 XP     │ +750 XP      │ +25 XP       │        │
│ │ [Locked]     │ [Locked]     │ [Locked]     │        │
│ └──────────────┴──────────────┴──────────────┘        │
└─────────────────────────────────────────────────────────┘
```

### Components
- `AchievementCard` - Badge with unlock status, progress
- `FilterControls` - Dropdown filters for All/Earned/Locked
- `ProgressBar` - Overall achievement completion

### Achievement Card States

**Unlocked:**
- Full color badge
- Title and description
- XP reward
- Unlock date
- Clickable → Detail modal

**Locked (with progress):**
- Grayed out badge with progress bar
- Shows "32/50 quizzes"
- Still clickable → Detail modal shows how to unlock

**Locked (no progress):**
- Grayed out, padlock icon
- Shows unlock criteria
- Clickable → Detail modal

### Achievement Detail Modal

```
┌────────────────────────────────────┐
│ 🏆 Quiz Marathon                   │
│                                    │
│ Complete 50 quizzes in any domain  │
│                                    │
│ Rarity: Rare (12% of users)       │
│ XP Reward: +500 XP                 │
│                                    │
│ Your Progress: 32/50 (64%)         │
│ [─────────▓░░░░░░] 64%             │
│                                    │
│ Keep going! 18 more quizzes to go! │
│                                    │
│ [Close]                            │
└────────────────────────────────────┘
```

---

## 9. Leaderboards

**Route:** `/app/leaderboard/:type` (xp, quizzes, accuracy, streaks)
**Auth Required:** Yes
**API Calls:**
- `GET /api/v1/leaderboard/xp?limit=100` (or quizzes, accuracy, streaks)

### Layout

```
┌────────────────────────────────────────────────────────┐
│ Leaderboards                                            │
│                                                         │
│ Tabs:                                                   │
│ [XP▼] [Quizzes] [Accuracy] [Streaks] [Exam: Security+▼]│
│                                                         │
│ Time Period: [●All Time] [○This Month] [○This Week]   │
│                                                         │
│ Your Rank: #47 of 1,234 users                          │
│                                                         │
│ Leaderboard Table                                       │
│ ┌────────────────────────────────────────────────────┐ │
│ │ Rank | User          | Level | XP    | View      │ │
│ ├────────────────────────────────────────────────────┤ │
│ │ 🥇 1 | AliceStudies  | 15    | 5,000 | [Profile] │ │
│ │ 🥈 2 | BobCertified  | 14    | 4,850 | [Profile] │ │
│ │ 🥉 3 | CharlieCoder  | 13    | 4,200 | [Profile] │ │
│ │  4   | DianaDev      | 13    | 4,100 | [Profile] │ │
│ │  5   | EvanExpert    | 12    | 3,900 | [Profile] │ │
│ │ ...                                                │ │
│ │ 47   | You (YourName)| 8     | 2,450 | [You]     │ │← Highlighted
│ │ ...                                                │ │
│ │ 100  | ZoeZealous    | 5     | 1,200 | [Profile] │ │
│ └────────────────────────────────────────────────────┘ │
│                                                         │
│ [Load More (101-200)]                                   │
└─────────────────────────────────────────────────────────┘
```

### Tab Variations

**XP Leaderboard:**
- Rank by total XP
- Show level and XP columns

**Quiz Count Leaderboard:**
- Rank by total quizzes completed
- Show quiz count and average score

**Accuracy Leaderboard:**
- Rank by average quiz score
- Show average score % and total quizzes (min 10 to qualify)

**Streak Leaderboard:**
- Rank by current study streak
- Show streak days (🔥) and longest streak

**Exam-Specific Leaderboard:**
- Dropdown to select exam type
- Rank by XP earned in that specific exam
- Show exam-specific stats

### Interactions
- Click username → Navigate to public profile `/app/users/:userId`
- Click "Load More" → Fetch next 100 users
- User's row auto-scrolls into view on page load
- Auto-refresh every 30 seconds (React Query polling)

---

## 10. Public User Profile

**Route:** `/app/users/:userId`
**Auth Required:** Yes (but viewing someone else's profile)
**API Calls:**
- `GET /api/v1/auth/users/:userId` - Public profile data

### Layout

```
┌────────────────────────────────────────────────────────┐
│ [← Back to Leaderboard]                                │
│                                                         │
│ Profile Header                                          │
│ ┌────────────────────────────────────────────────────┐ │
│ │ ┌──────┐                                           │ │
│ │ │Avatar│  AliceStudies                             │ │
│ │ │      │  Level 15                                 │ │
│ │ └──────┘  Member since: Jan 2024                   │ │
│ │                                                    │ │
│ │ Bio: "Cybersecurity enthusiast preparing for       │ │
│ │ Security+ certification. Love helping others!"     │ │
│ └────────────────────────────────────────────────────┘ │
│                                                         │
│ Stats Grid                                              │
│ ┌───────────┬───────────┬───────────┬───────────┐     │
│ │ 5,000 XP  │ Level 15  │ 150 Quizzes│ 92% Avg  │     │
│ └───────────┴───────────┴───────────┴───────────┘     │
│                                                         │
│ Streaks                                                 │
│ ┌───────────────────────────────────┐                  │
│ │ 🔥 Current: 25 days               │                  │
│ │ 🏆 Longest: 40 days               │                  │
│ └───────────────────────────────────┘                  │
│                                                         │
│ Achievements (showing earned only)                      │
│ ┌───────┬───────┬───────┬───────┬───────┐             │
│ │ [🏆]  │ [🎯]  │ [⭐]  │ [🔥]  │ [+15] │             │
│ │ First │Marathon│Perfect│ Streak│ More  │             │
│ └───────┴───────┴───────┴───────┴───────┘             │
│                                                         │
│ 🔒 Private Information                                 │
│ Email, account status, and other sensitive data        │
│ are not shown on public profiles.                      │
└─────────────────────────────────────────────────────────┘
```

### Privacy Note
- **Shown:** Username, level, XP, total stats, bio, avatar, streaks, achievements
- **Hidden:** Email, is_admin, is_active, is_verified, quiz history details

---

## 11. Bookmarks Page

**Route:** `/app/bookmarks`
**Auth Required:** Yes
**API Calls:**
- `GET /api/v1/bookmarks?page=1&page_size=20` - User's bookmarks

### Layout

```
┌────────────────────────────────────────────────────────┐
│ Bookmarks                                               │
│                                                         │
│ Filter: [All Exams ▼] [All Domains ▼] | Search: [___] │
│                                                         │
│ 42 bookmarks | [Quick Quiz from All Bookmarks]         │
│                                                         │
│ Bookmark List                                           │
│ ┌────────────────────────────────────────────────────┐ │
│ │ 🔖 Which protocol...                              │ │
│ │ Security+ | Domain 2.1 | Jan 20, 2025              │ │
│ │ Note: "Review TCP vs UDP differences"             │ │
│ │ [View] [Edit Note] [Remove]                       │ │
│ ├────────────────────────────────────────────────────┤ │
│ │ 🔖 What is the purpose of...                      │ │
│ │ Network+ | Domain 1.2 | Jan 19, 2025              │ │
│ │ Note: None                                        │ │
│ │ [View] [Add Note] [Remove]                        │ │
│ └────────────────────────────────────────────────────┘ │
│                                                         │
│ Pagination: [← Prev] Page 1 of 3 [Next →]             │
└─────────────────────────────────────────────────────────┘
```

### Bookmark Card Actions
- **View** → Modal with full question + correct answer + explanations
- **Edit Note** → Inline textarea appears
- **Remove** → Confirmation → DELETE request → Remove from list

### Quick Quiz Feature
- Button: "Quick Quiz from All Bookmarks"
- Generates quiz using all bookmarked question IDs
- Max 30 questions (if more bookmarks, randomly sample)
- Navigate to practice quiz interface

---

## 12. Admin - Dashboard

**Route:** `/app/admin`
**Auth Required:** Yes + Admin role
**API Calls:**
- `GET /api/v1/admin/users?limit=10` - Recent users
- `GET /api/v1/admin/questions?limit=10` - Recent questions

### Layout

```
┌────────────────────────────────────────────────────────┐
│ Admin Dashboard                                         │
│                                                         │
│ Stats Grid                                              │
│ ┌───────────┬───────────┬───────────┬───────────┐     │
│ │ 1,234     │ 2,500     │ 25        │ 15,000    │     │
│ │ Users     │ Questions │Achievements│ Total XP  │     │
│ └───────────┴───────────┴───────────┴───────────┘     │
│                                                         │
│ Navigation                                              │
│ ┌──────────────────────────────────────────────────┐   │
│ │ [Manage Users] [Manage Questions] [Manage Achievements]│
│ └──────────────────────────────────────────────────┘   │
│                                                         │
│ Recent Activity                                         │
│ ┌──────────────────────────────────────────────────┐   │
│ │ ■ User "john@example.com" signed up              │   │
│ │ ■ Question SEC999 created by admin               │   │
│ │ ■ User "alice" reached Level 10                  │   │
│ └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## 13. Admin - User Management

**Route:** `/app/admin/users`
**Auth Required:** Admin
**API Calls:**
- `GET /api/v1/admin/users?page=1&page_size=50`

### Layout

```
┌────────────────────────────────────────────────────────┐
│ User Management                                         │
│                                                         │
│ Search: [___________] | Filter: [All ▼] [Active ▼]     │
│                                                         │
│ User Table                                              │
│ ┌────────────────────────────────────────────────────┐ │
│ │ ID | Email         | Username | Active | Admin    │ │
│ ├────────────────────────────────────────────────────┤ │
│ │ 1  | alice@ex.com  | alice    | ✓      | ✓        │ │
│ │ 2  | bob@ex.com    | bob      | ✓      | ✗        │ │
│ │ 3  | charlie@ex.com| charlie  | ✗      | ✗        │ │
│ │                                        [View] [Edit] │ │
│ └────────────────────────────────────────────────────┘ │
│                                                         │
│ Pagination: [← Prev] Page 1 of 25 [Next →]            │
└─────────────────────────────────────────────────────────┘
```

### User Actions
- **View** → User detail page with full info, quiz history
- **Edit** → Modal to toggle admin, toggle active, change email/username
- **Delete** → Disabled (preserve data integrity)

---

## 14. Admin - Question Management

**Route:** `/app/admin/questions`
**Auth Required:** Admin
**API Calls:**
- `GET /api/v1/admin/questions?page=1&page_size=50`

### Layout

```
┌────────────────────────────────────────────────────────┐
│ Question Management                                     │
│                                                         │
│ [+ Create New Question]                                 │
│                                                         │
│ Search: [___________] | Exam: [All ▼] | Domain: [All ▼]│
│                                                         │
│ Question Table                                          │
│ ┌────────────────────────────────────────────────────┐ │
│ │ ID     | Exam      | Domain | Question Text...   │ │
│ ├────────────────────────────────────────────────────┤ │
│ │ SEC001 | Security+ | 1.1    | What is encryption...│ │
│ │ SEC002 | Security+ | 1.2    | Which protocol...   │ │
│ │ NET001 | Network+  | 2.1    | What is a subnet... │ │
│ │                                   [Edit] [Delete]  │ │
│ └────────────────────────────────────────────────────┘ │
│                                                         │
│ Pagination: [← Prev] Page 1 of 50 [Next →]            │
└─────────────────────────────────────────────────────────┘
```

### Question Editor Modal

```
┌────────────────────────────────────────────────────────┐
│ Edit Question: SEC001                                   │
│                                                         │
│ Exam Type: [Security+ ▼]  Domain: [1.1 ▼]             │
│                                                         │
│ Question Text:                                          │
│ ┌────────────────────────────────────────────────────┐ │
│ │ [Textarea with current question text]              │ │
│ └────────────────────────────────────────────────────┘ │
│                                                         │
│ Options:                                                │
│ ● A: [Input] Explanation: [Textarea]                   │
│ ○ B: [Input] Explanation: [Textarea]                   │
│ ○ C: [Input] Explanation: [Textarea]                   │
│ ○ D: [Input] Explanation: [Textarea]                   │
│ (Radio selects correct answer)                          │
│                                                         │
│ [Cancel]  [Save Changes]                                │
└─────────────────────────────────────────────────────────┘
```

---

## Responsive Design Notes

### Mobile Adaptations (< 640px)

**Dashboard:**
- Stack all cards vertically
- Horizontal scroll for achievement preview
- Bottom tab navigation (Dashboard, Practice, Study, More)

**Quiz Taking:**
- Full-screen question card
- Question navigator collapses to dropdown: "Question 5 of 30 ▼"
- Timer moves to sticky header

**Leaderboard:**
- Table becomes cards (one user per card)
- Tabs become dropdown selector

**Forms:**
- Full-width inputs
- Larger touch targets (48px min)

### Tablet Adaptations (640px - 1024px)

- Sidebar collapses to icon-only
- 2-column grids instead of 4
- Preserved horizontal space for content

---

**Next:** Component architecture (04-component-architecture.md)
