# Component Architecture

Complete component hierarchy and specifications for the CompTIA Practice Platform.

---

## Component Organization

```
/src/components
  /ui                    # Shadcn/ui base components
  /layout               # App structure components
  /features             # Feature-specific components
    /auth
    /quiz
    /study
    /achievements
    /leaderboard
    /profile
    /bookmarks
    /admin
```

---

## Component Hierarchy

```
App
├── Router
│   ├── PublicRoutes
│   │   ├── LandingPage
│   │   ├── LoginPage
│   │   └── SignupPage
│   │
│   └── AuthenticatedRoutes (Protected)
│       ├── AppShell
│       │   ├── Sidebar
│       │   │   ├── UserProfileCard
│       │   │   ├── NavigationMenu
│       │   │   └── LogoutButton
│       │   │
│       │   ├── MobileNav (< 768px)
│       │   │   └── BottomTabBar
│       │   │
│       │   └── MainContent
│       │       ├── DashboardPage
│       │       ├── PracticePage
│       │       ├── StudyPage
│       │       ├── AchievementsPage
│       │       ├── LeaderboardPage
│       │       ├── ProfilePage
│       │       ├── BookmarksPage
│       │       └── AdminPages
│       │
│       └── GlobalModals
│           ├── AchievementUnlockModal
│           ├── LevelUpModal
│           └── ToastContainer
```

---

## Shared UI Components (Shadcn/ui)

### Button

```typescript
interface ButtonProps {
  variant: 'primary' | 'secondary' | 'danger' | 'ghost'
  size: 'sm' | 'md' | 'lg'
  disabled?: boolean
  loading?: boolean
  icon?: React.ReactNode
  children: React.ReactNode
  onClick?: () => void
}
```

**Usage:**
```tsx
<Button variant="primary" size="lg">
  Start Quiz
</Button>

<Button variant="secondary" icon={<BookmarkIcon />}>
  Bookmark
</Button>
```

### Input

```typescript
interface InputProps {
  type?: 'text' | 'email' | 'password' | 'number'
  placeholder?: string
  value: string
  onChange: (value: string) => void
  error?: string
  disabled?: boolean
  icon?: React.ReactNode
}
```

### Card

```typescript
interface CardProps {
  variant?: 'default' | 'outlined' | 'elevated' | 'clickable'
  padding?: 'sm' | 'md' | 'lg'
  className?: string
  onClick?: () => void
  children: React.ReactNode
}
```

### Badge

```typescript
interface BadgeProps {
  variant: 'success' | 'warning' | 'error' | 'info' | 'neutral'
  size?: 'sm' | 'md'
  children: React.ReactNode
}
```

### Modal (Dialog)

```typescript
interface ModalProps {
  open: boolean
  onClose: () => void
  title: string
  description?: string
  children: React.ReactNode
  footer?: React.ReactNode
  size?: 'sm' | 'md' | 'lg' | 'xl'
}
```

### ProgressBar

```typescript
interface ProgressBarProps {
  value: number // 0-100
  max?: number
  variant?: 'primary' | 'success' | 'warning'
  showLabel?: boolean
  label?: string
  size?: 'sm' | 'md' | 'lg'
}
```

---

## Layout Components

### AppShell

**Purpose:** Main application wrapper for authenticated users

```typescript
interface AppShellProps {
  children: React.ReactNode
}

function AppShell({ children }: AppShellProps) {
  return (
    <div className="flex h-screen">
      <Sidebar />
      <main className="flex-1 overflow-y-auto">
        {children}
      </main>
      <MobileNav className="md:hidden" />
    </div>
  )
}
```

**Responsibilities:**
- Render sidebar (desktop)
- Render bottom nav (mobile)
- Manage responsive layout
- Provide logout functionality

### Sidebar

```typescript
interface SidebarProps {
  className?: string
}
```

**Structure:**
```tsx
<aside className="w-64 bg-white border-r">
  <UserProfileCard />
  <nav>
    <NavigationItem icon={<DashboardIcon />} to="/app/dashboard">
      Dashboard
    </NavigationItem>
    <NavigationItem icon={<PracticeIcon />} to="/app/practice">
      Practice
    </NavigationItem>
    {/* More items */}
  </nav>
  <div className="mt-auto">
    <NavigationItem icon={<SettingsIcon />} to="/app/settings">
      Settings
    </NavigationItem>
    <LogoutButton />
  </div>
</aside>
```

**State:**
- `isCollapsed` (boolean) - For icon-only mode on tablets

### UserProfileCard

```typescript
interface UserProfileCardProps {
  user: {
    username: string
    level: number
    xp: number
    xpToNextLevel: number
    avatarUrl?: string
  }
}
```

**Displays:**
- Avatar image
- Username
- Current level
- XP progress bar to next level

### MobileNav (BottomTabBar)

```typescript
interface MobileNavProps {
  className?: string
}
```

**Tabs:**
- Dashboard (Home icon)
- Practice (Quiz icon)
- Study (Book icon)
- More (Menu icon → drawer)

---

## Feature Components

### Dashboard Components

#### StatCard

```typescript
interface StatCardProps {
  icon: React.ReactNode
  label: string
  value: string | number
  subtext?: string
  variant?: 'default' | 'success' | 'primary'
}
```

**Example:**
```tsx
<StatCard
  icon={<TrophyIcon />}
  label="Level"
  value={8}
  subtext="150 XP to Level 9"
  variant="primary"
/>
```

#### QuickActionCard

```typescript
interface QuickActionCardProps {
  title: string
  description: string
  icon: React.ReactNode
  actionLabel: string
  onAction: () => void
  disabled?: boolean
}
```

#### ActivityFeed

```typescript
interface ActivityFeedProps {
  activities: Activity[]
  limit?: number
}

interface Activity {
  type: 'quiz' | 'achievement' | 'bookmark' | 'level_up'
  title: string
  timestamp: Date
  metadata?: any
}
```

#### AchievementPreview

```typescript
interface AchievementPreviewProps {
  achievements: Achievement[]
  limit: number
  onViewAll: () => void
}
```

**Renders:**
- Horizontal scrollable list of achievement badges
- First N unlocked + first N locked
- "View All" button

#### LeaderboardPreview

```typescript
interface LeaderboardPreviewProps {
  entries: LeaderboardEntry[]
  userRank: number
  onViewFull: () => void
}
```

### Quiz Components

#### QuizHeader

```typescript
interface QuizHeaderProps {
  examType: string
  currentQuestion: number
  totalQuestions: number
  timeRemaining?: number // seconds, undefined if untimed
  progress: number // 0-100
}
```

**Features:**
- Progress bar showing % complete
- Timer (if timed mode)
- Question counter "5 of 30"
- Exam type badge

#### QuestionCard

```typescript
interface QuestionCardProps {
  question: {
    id: number
    questionText: string
    options: {
      A: { text: string }
      B: { text: string }
      C: { text: string }
      D: { text: string }
    }
    domain: string
  }
  selectedAnswer?: string
  onAnswerSelect: (answer: string) => void
  onBookmark?: () => void
  isBookmarked?: boolean
  showBookmark?: boolean
}
```

**Interactive Elements:**
- Radio buttons for answer selection
- Bookmark button (optional)
- Domain tag

#### QuestionNavigator

```typescript
interface QuestionNavigatorProps {
  questions: {
    id: number
    answered: boolean
    flagged: boolean
  }[]
  currentQuestionIndex: number
  onQuestionSelect: (index: number) => void
  onSubmit: () => void
}
```

**Visual States:**
- Answered: Checkmark
- Flagged: Flag icon
- Current: Highlighted border
- Unanswered: Empty circle

#### QuizResults

```typescript
interface QuizResultsProps {
  score: number // percentage
  correct: number
  total: number
  timeSpent: number // seconds
  xpEarned: number
  achievementsUnlocked: Achievement[]
  levelUp?: {
    from: number
    to: number
  }
  questionResults: QuestionResult[]
}
```

**Sub-components:**
- `CircularScoreDisplay` - Animated circular progress
- `StatsGrid` - Correct/incorrect/time/XP
- `AchievementUnlockCard` - New achievements
- `LevelUpBanner` - Level progression
- `QuestionReviewList` - List of all questions with results

### Study Mode Components

#### StudyQuestion

```typescript
interface StudyQuestionProps {
  question: {
    questionText: string
    options: Record<string, { text: string }>
  }
  selectedAnswer?: string
  onAnswerSelect: (answer: string) => void
  onSubmit: () => void
  disabled?: boolean
}
```

#### StudyFeedback

```typescript
interface StudyFeedbackProps {
  isCorrect: boolean
  userAnswer: string
  correctAnswer: string
  explanations: {
    userAnswer: string
    correctAnswer: string
    allOptions: Record<string, { text: string, explanation: string }>
  }
  xpEarned: number
  onNext: () => void
}
```

**Visual:**
- Big ✓ Correct or ✗ Incorrect banner
- User's answer highlighted
- Correct answer highlighted (if different)
- Full explanations for all options
- XP earned notification
- "Next Question" button

### Achievement Components

#### AchievementCard

```typescript
interface AchievementCardProps {
  achievement: {
    id: number
    name: string
    description: string
    icon: string
    xpReward: number
    rarity: 'common' | 'rare' | 'epic' | 'legendary'
  }
  status: 'locked' | 'in_progress' | 'unlocked'
  progress?: {
    current: number
    required: number
  }
  unlockedAt?: Date
  onClick?: () => void
}
```

**Visual States:**
- **Locked:** Grayscale, padlock icon
- **In Progress:** Partial color, progress bar
- **Unlocked:** Full color, unlock date

#### AchievementUnlockModal

```typescript
interface AchievementUnlockModalProps {
  achievement: {
    name: string
    description: string
    icon: string
    xpReward: number
  }
  onClose: () => void
}
```

**Animation:**
- Modal scales in from center
- Confetti effect (react-confetti)
- Badge grows and rotates
- XP counter ticks up
- Sound effect (optional)

#### AchievementDetailModal

```typescript
interface AchievementDetailModalProps {
  achievement: Achievement
  userProgress?: {
    current: number
    required: number
  }
  unlockedAt?: Date
  onClose: () => void
}
```

### Leaderboard Components

#### LeaderboardTable

```typescript
interface LeaderboardTableProps {
  entries: LeaderboardEntry[]
  type: 'xp' | 'quizzes' | 'accuracy' | 'streaks'
  currentUserId: number
  onUserClick: (userId: number) => void
  onLoadMore?: () => void
  hasMore?: boolean
}

interface LeaderboardEntry {
  rank: number
  userId: number
  username: string
  avatarUrl?: string
  value: number // XP, quiz count, accuracy %, streak days
  level?: number
}
```

**Features:**
- Auto-scroll to current user's rank
- Medal icons for top 3 (🥇🥈🥉)
- Highlighted row for current user
- Click username → Public profile
- "Load More" pagination

#### LeaderboardTabs

```typescript
interface LeaderboardTabsProps {
  activeTab: LeaderboardType
  onTabChange: (tab: LeaderboardType) => void
}

type LeaderboardType = 'xp' | 'quizzes' | 'accuracy' | 'streaks' | 'exam'
```

#### LeaderboardFilters

```typescript
interface LeaderboardFiltersProps {
  timePeriod: 'all' | 'month' | 'week'
  examType?: string
  onTimePeriodChange: (period: string) => void
  onExamTypeChange?: (exam: string) => void
}
```

### Profile Components

#### ProfileCard

```typescript
interface ProfileCardProps {
  user: {
    id: number
    username: string
    level: number
    xp: number
    avatarUrl?: string
    bio?: string
    createdAt: Date
  }
  isOwnProfile: boolean
}
```

#### ProfileStats

```typescript
interface ProfileStatsProps {
  stats: {
    totalQuizzes: number
    averageScore: number
    xp: number
    level: number
    currentStreak: number
    longestStreak: number
    totalQuestionsAnswered: number
  }
}
```

**Renders:**
- Grid of stat cards
- XP progress bar to next level
- Streak indicators with fire emoji

#### ProfileEditForm

```typescript
interface ProfileEditFormProps {
  user: {
    username: string
    email: string
    bio?: string
  }
  onSubmit: (data: ProfileUpdateData) => Promise<void>
  onCancel: () => void
}
```

#### AvatarSelector

```typescript
interface AvatarSelectorProps {
  avatars: Avatar[]
  selectedAvatarId?: number
  onSelect: (avatarId: number) => void
}

interface Avatar {
  id: number
  name: string
  imageUrl: string
  unlocked: boolean
  unlockCriteria?: string
}
```

**Layout:**
- Grid of avatar images
- Locked avatars grayed out with lock icon
- Selected avatar has checkmark overlay
- Hover shows unlock criteria tooltip

### Bookmark Components

#### BookmarkCard

```typescript
interface BookmarkCardProps {
  bookmark: {
    id: number
    questionId: number
    questionText: string
    notes?: string
    examType: string
    domain: string
    createdAt: Date
  }
  onView: () => void
  onEditNote: (note: string) => void
  onRemove: () => void
}
```

#### BookmarkDetailModal

```typescript
interface BookmarkDetailModalProps {
  question: {
    questionText: string
    options: Record<string, QuestionOption>
    correctAnswer: string
    domain: string
  }
  notes?: string
  onUpdateNotes: (notes: string) => void
  onClose: () => void
}
```

**Shows:**
- Full question text
- All answer options
- Correct answer highlighted
- All explanations visible
- Editable notes textarea

### Admin Components

#### UserTable

```typescript
interface UserTableProps {
  users: User[]
  onViewUser: (userId: number) => void
  onEditUser: (userId: number) => void
  onToggleAdmin: (userId: number) => void
  onToggleActive: (userId: number) => void
}
```

#### QuestionEditor

```typescript
interface QuestionEditorProps {
  question?: Question // undefined for creating new
  onSubmit: (question: QuestionData) => Promise<void>
  onCancel: () => void
}

interface QuestionData {
  questionId: string
  examType: string
  domain: string
  questionText: string
  options: {
    A: { text: string, explanation: string }
    B: { text: string, explanation: string }
    C: { text: string, explanation: string }
    D: { text: string, explanation: string }
  }
  correctAnswer: 'A' | 'B' | 'C' | 'D'
}
```

**Form Fields:**
- Text input: Question ID
- Dropdown: Exam type
- Dropdown: Domain
- Textarea: Question text
- 4x Input + Textarea: Options with explanations
- Radio: Select correct answer
- Submit/Cancel buttons

---

## Utility Components

### LoadingSpinner

```typescript
interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg'
  fullScreen?: boolean
  text?: string
}
```

### EmptyState

```typescript
interface EmptyStateProps {
  icon?: React.ReactNode
  title: string
  description?: string
  action?: {
    label: string
    onClick: () => void
  }
}
```

### ErrorBoundary

```typescript
interface ErrorBoundaryProps {
  children: React.ReactNode
  fallback?: React.ReactNode
}
```

### ConfirmationModal

```typescript
interface ConfirmationModalProps {
  open: boolean
  title: string
  description: string
  confirmLabel?: string
  cancelLabel?: string
  variant?: 'danger' | 'warning' | 'info'
  onConfirm: () => void
  onCancel: () => void
}
```

### Toast Notifications

```typescript
// Using react-hot-toast or sonner
import { toast } from 'sonner'

toast.success('Quiz submitted successfully!')
toast.error('Failed to save bookmark')
toast.info('Study session saved')
```

---

## Animation Components

### ConfettiEffect

```typescript
import Confetti from 'react-confetti'

interface ConfettiEffectProps {
  active: boolean
  duration?: number // ms
}
```

**Usage:**
- Achievement unlock
- Level up
- Perfect score (100%)

### LevelUpAnimation

```typescript
interface LevelUpAnimationProps {
  fromLevel: number
  toLevel: number
  onComplete: () => void
}
```

**Effect:**
- Screen flash (subtle)
- "LEVEL UP!" banner slides from top
- Level number increments with animation
- XP bar fills smoothly

---

## Custom Hooks

### useAuth

```typescript
function useAuth() {
  return {
    user: User | null
    isAuthenticated: boolean
    isAdmin: boolean
    login: (email: string, password: string) => Promise<void>
    logout: () => void
    updateProfile: (data: ProfileUpdate) => Promise<void>
  }
}
```

### useQuiz

```typescript
function useQuiz() {
  return {
    questions: Question[]
    currentQuestionIndex: number
    answers: Record<number, string>
    timeRemaining: number
    selectAnswer: (questionId: number, answer: string) => void
    nextQuestion: () => void
    previousQuestion: () => void
    flagQuestion: (questionId: number) => void
    submitQuiz: () => Promise<QuizResult>
    saveProgress: () => void // Auto-save to localStorage
  }
}
```

### useStudySession

```typescript
function useStudySession() {
  return {
    session: StudySession | null
    currentQuestion: Question | null
    submitAnswer: (answer: string) => Promise<Feedback>
    nextQuestion: () => void
    abandonSession: () => Promise<void>
  }
}
```

### useLeaderboard

```typescript
function useLeaderboard(type: LeaderboardType) {
  return {
    entries: LeaderboardEntry[]
    userRank: number | null
    isLoading: boolean
    error: Error | null
    refetch: () => void
    loadMore: () => void
  }
}
```

---

## State Management

### Zustand Stores

#### authStore

```typescript
interface AuthState {
  user: User | null
  token: string | null
  refreshToken: string | null
  setAuth: (user: User, token: string, refreshToken: string) => void
  logout: () => void
  updateUser: (user: Partial<User>) => void
}
```

#### quizStore

```typescript
interface QuizState {
  questions: Question[]
  answers: Record<number, string>
  currentQuestionIndex: number
  flaggedQuestions: Set<number>
  startTime: Date | null
  timeRemaining: number | null
  setQuestions: (questions: Question[]) => void
  selectAnswer: (questionId: number, answer: string) => void
  flagQuestion: (questionId: number) => void
  reset: () => void
}
```

### React Query Keys

```typescript
export const queryKeys = {
  user: ['user'] as const,
  profile: (userId: number) => ['profile', userId] as const,
  quizHistory: (page: number) => ['quizHistory', page] as const,
  achievements: ['achievements'] as const,
  earnedAchievements: ['earnedAchievements'] as const,
  leaderboard: (type: string, period: string) => ['leaderboard', type, period] as const,
  bookmarks: (page: number) => ['bookmarks', page] as const,
  questions: (params: any) => ['questions', params] as const,
}
```

---

## File Structure

```
/src
  /components
    /ui
      Button.tsx
      Input.tsx
      Card.tsx
      Badge.tsx
      Modal.tsx
      ProgressBar.tsx
      Tabs.tsx
      Avatar.tsx
      Toast.tsx
      Checkbox.tsx
      RadioGroup.tsx
      Select.tsx

    /layout
      AppShell.tsx
      Sidebar.tsx
      MobileNav.tsx
      UserProfileCard.tsx
      PageContainer.tsx
      Header.tsx

    /features
      /auth
        LoginForm.tsx
        SignupForm.tsx
        ProfileEditForm.tsx

      /quiz
        QuizHeader.tsx
        QuestionCard.tsx
        QuestionNavigator.tsx
        QuizResults.tsx
        CircularScoreDisplay.tsx
        QuestionReviewList.tsx

      /study
        StudyQuestion.tsx
        StudyFeedback.tsx
        StudyProgress.tsx

      /achievements
        AchievementCard.tsx
        AchievementGrid.tsx
        AchievementUnlockModal.tsx
        AchievementDetailModal.tsx
        ConfettiEffect.tsx

      /leaderboard
        LeaderboardTable.tsx
        LeaderboardTabs.tsx
        LeaderboardFilters.tsx
        UserRankCard.tsx

      /profile
        ProfileCard.tsx
        ProfileStats.tsx
        AvatarSelector.tsx
        PublicProfileView.tsx

      /bookmarks
        BookmarkCard.tsx
        BookmarkList.tsx
        BookmarkDetailModal.tsx

      /dashboard
        StatCard.tsx
        QuickActionCard.tsx
        ActivityFeed.tsx
        AchievementPreview.tsx
        LeaderboardPreview.tsx

      /admin
        UserTable.tsx
        QuestionTable.tsx
        QuestionEditor.tsx
        AchievementEditor.tsx

    /shared
      LoadingSpinner.tsx
      EmptyState.tsx
      ErrorBoundary.tsx
      ConfirmationModal.tsx

  /hooks
    useAuth.ts
    useQuiz.ts
    useStudySession.ts
    useLeaderboard.ts
    useBookmarks.ts
    useLocalStorage.ts

  /stores
    authStore.ts
    quizStore.ts

  /lib
    /api
      client.ts
      auth.ts
      quiz.ts
      study.ts
      achievements.ts
      leaderboard.ts
      bookmarks.ts
      admin.ts

  /types
    api.ts (from backend docs)
    components.ts
    stores.ts
```

---

## Component Best Practices

### 1. Component Composition

```tsx
// Good: Composable components
<Card>
  <Card.Header>
    <Card.Title>Quiz Results</Card.Title>
  </Card.Header>
  <Card.Content>
    {/* Content */}
  </Card.Content>
</Card>

// Avoid: Monolithic components with too many props
<QuizResultCard
  title="Quiz Results"
  score={85}
  correct={26}
  total={30}
  showChart={true}
  showActions={true}
  // ... 20 more props
/>
```

### 2. Props Destructuring

```tsx
interface ButtonProps {
  variant: 'primary' | 'secondary'
  children: React.ReactNode
}

// Destructure immediately
function Button({ variant, children }: ButtonProps) {
  return <button className={cn(variants[variant])}>{children}</button>
}
```

### 3. TypeScript Interfaces

- Define props interfaces above component
- Export reusable types
- Use discriminated unions for variant props

### 4. Accessibility

```tsx
// Always include ARIA labels
<button
  aria-label="Bookmark question"
  aria-pressed={isBookmarked}
>
  <BookmarkIcon />
</button>

// Use semantic HTML
<nav role="navigation">
  <ul role="list">
    <li role="listitem">...</li>
  </ul>
</nav>
```

### 5. Error Boundaries

Wrap features in error boundaries:
```tsx
<ErrorBoundary fallback={<ErrorFallback />}>
  <QuizTaking />
</ErrorBoundary>
```

---

**Next:** Feature implementation guide (05-feature-implementation-guide.md)
