# Feature Implementation Guide

Practical implementation patterns and code examples for key features.

---

## Authentication Flow

### 1. API Client Setup

**File:** `/src/lib/api/client.ts`

```typescript
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor: Add auth token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor: Handle 401, refresh token
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    // If 401 and not already retrying
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const refreshToken = localStorage.getItem('refresh_token')
        const { data } = await axios.post(`${API_BASE_URL}/api/v1/auth/refresh`, {
          refresh_token: refreshToken,
        })

        localStorage.setItem('access_token', data.access_token)
        originalRequest.headers.Authorization = `Bearer ${data.access_token}`

        return apiClient(originalRequest)
      } catch (refreshError) {
        // Refresh failed, logout user
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)
```

### 2. Auth Store (Zustand)

**File:** `/src/stores/authStore.ts`

```typescript
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface User {
  id: number
  email: string
  username: string
  level: number
  xp: number
  // ... other fields from ProfileResponse
}

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  setAuth: (user: User, token: string, refreshToken: string) => void
  updateUser: (updates: Partial<User>) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,

      setAuth: (user, token, refreshToken) => {
        localStorage.setItem('access_token', token)
        localStorage.setItem('refresh_token', refreshToken)
        set({ user, token, isAuthenticated: true })
      },

      updateUser: (updates) =>
        set((state) => ({
          user: state.user ? { ...state.user, ...updates } : null,
        })),

      logout: () => {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        set({ user: null, token: null, isAuthenticated: false })
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ user: state.user }), // Only persist user, not token
    }
  )
)
```

### 3. Login Implementation

**File:** `/src/features/auth/LoginForm.tsx`

```typescript
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useMutation } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { apiClient } from '@/lib/api/client'
import { useAuthStore } from '@/stores/authStore'
import { toast } from 'sonner'

const loginSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(1, 'Password is required'),
})

type LoginFormData = z.infer<typeof loginSchema>

export function LoginForm() {
  const navigate = useNavigate()
  const setAuth = useAuthStore((state) => state.setAuth)

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  })

  const loginMutation = useMutation({
    mutationFn: async (data: LoginFormData) => {
      const response = await apiClient.post('/api/v1/auth/login', data)
      return response.data
    },
    onSuccess: (data) => {
      setAuth(data.user, data.access_token, data.refresh_token)
      toast.success('Logged in successfully!')
      navigate('/app/dashboard')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error?.message || 'Login failed')
    },
  })

  const onSubmit = (data: LoginFormData) => {
    loginMutation.mutate(data)
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <label htmlFor="email">Email</label>
        <input
          id="email"
          type="email"
          {...register('email')}
          className="..."
        />
        {errors.email && (
          <p className="text-error-600 text-sm">{errors.email.message}</p>
        )}
      </div>

      <div>
        <label htmlFor="password">Password</label>
        <input
          id="password"
          type="password"
          {...register('password')}
          className="..."
        />
        {errors.password && (
          <p className="text-error-600 text-sm">{errors.password.message}</p>
        )}
      </div>

      <button
        type="submit"
        disabled={loginMutation.isPending}
        className="..."
      >
        {loginMutation.isPending ? 'Logging in...' : 'Login'}
      </button>
    </form>
  )
}
```

### 4. Protected Route

**File:** `/src/components/ProtectedRoute.tsx`

```typescript
import { Navigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
  const location = useLocation()

  if (!isAuthenticated) {
    // Redirect to login, save intended destination
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  return <>{children}</>
}
```

---

## Quiz Taking Flow

### 1. Quiz Store

**File:** `/src/stores/quizStore.ts`

```typescript
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface QuizState {
  questions: Question[]
  answers: Record<number, string>
  currentQuestionIndex: number
  flaggedQuestions: Set<number>
  startTime: Date | null
  timeRemaining: number | null
  setQuestions: (questions: Question[]) => void
  selectAnswer: (questionId: number, answer: string) => void
  goToQuestion: (index: number) => void
  flagQuestion: (questionId: number) => void
  reset: () => void
}

export const useQuizStore = create<QuizState>()(
  persist(
    (set, get) => ({
      questions: [],
      answers: {},
      currentQuestionIndex: 0,
      flaggedQuestions: new Set(),
      startTime: null,
      timeRemaining: null,

      setQuestions: (questions) =>
        set({
          questions,
          answers: {},
          currentQuestionIndex: 0,
          flaggedQuestions: new Set(),
          startTime: new Date(),
        }),

      selectAnswer: (questionId, answer) =>
        set((state) => ({
          answers: { ...state.answers, [questionId]: answer },
        })),

      goToQuestion: (index) => set({ currentQuestionIndex: index }),

      flagQuestion: (questionId) =>
        set((state) => {
          const newFlagged = new Set(state.flaggedQuestions)
          if (newFlagged.has(questionId)) {
            newFlagged.delete(questionId)
          } else {
            newFlagged.add(questionId)
          }
          return { flaggedQuestions: newFlagged }
        }),

      reset: () =>
        set({
          questions: [],
          answers: {},
          currentQuestionIndex: 0,
          flaggedQuestions: new Set(),
          startTime: null,
        }),
    }),
    {
      name: 'quiz-storage',
    }
  )
)
```

### 2. Quiz Timer Hook

**File:** `/src/hooks/useQuizTimer.ts`

```typescript
import { useEffect, useState } from 'react'

export function useQuizTimer(totalSeconds: number | null) {
  const [timeRemaining, setTimeRemaining] = useState(totalSeconds)

  useEffect(() => {
    if (totalSeconds === null) return // Untimed mode

    const interval = setInterval(() => {
      setTimeRemaining((prev) => {
        if (prev === null || prev <= 0) {
          clearInterval(interval)
          return 0
        }
        return prev - 1
      })
    }, 1000)

    return () => clearInterval(interval)
  }, [totalSeconds])

  const minutes = Math.floor((timeRemaining || 0) / 60)
  const seconds = (timeRemaining || 0) % 60

  return {
    timeRemaining,
    formattedTime: `${minutes}:${seconds.toString().padStart(2, '0')}`,
    isWarning: (timeRemaining || 0) < 300, // < 5 minutes
  }
}
```

### 3. Quiz Submission

**File:** `/src/features/quiz/useQuizSubmission.ts`

```typescript
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api/client'
import { useQuizStore } from '@/stores/quizStore'
import { toast } from 'sonner'

export function useQuizSubmission() {
  const queryClient = useQueryClient()
  const { questions, answers, startTime, reset } = useQuizStore()

  return useMutation({
    mutationFn: async () => {
      const timeSpent = startTime
        ? Math.floor((Date.now() - startTime.getTime()) / 1000)
        : 0

      const submissionData = {
        exam_type: questions[0].exam_type,
        answers: Object.entries(answers).map(([questionId, selectedAnswer]) => ({
          question_id: parseInt(questionId),
          selected_answer: selectedAnswer,
        })),
        time_spent_seconds: timeSpent,
      }

      const response = await apiClient.post('/api/v1/quiz/submit', submissionData)
      return response.data
    },
    onSuccess: (data) => {
      // Invalidate quiz history
      queryClient.invalidateQueries({ queryKey: ['quizHistory'] })

      // Invalidate user profile (XP/level may have changed)
      queryClient.invalidateQueries({ queryKey: ['user'] })

      // Invalidate achievements (new ones may be unlocked)
      queryClient.invalidateQueries({ queryKey: ['earnedAchievements'] })

      // Reset quiz state
      reset()

      toast.success('Quiz submitted successfully!')

      return data
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error?.message || 'Failed to submit quiz')
    },
  })
}
```

---

## Achievement Unlock Animation

### File: `/src/features/achievements/AchievementUnlockModal.tsx`

```typescript
import { motion, AnimatePresence } from 'framer-motion'
import Confetti from 'react-confetti'
import { useWindowSize } from 'react-use'
import { TrophyIcon } from 'lucide-react'

interface AchievementUnlockModalProps {
  achievement: {
    name: string
    description: string
    icon: string
    xpReward: number
  }
  open: boolean
  onClose: () => void
}

export function AchievementUnlockModal({
  achievement,
  open,
  onClose,
}: AchievementUnlockModalProps) {
  const { width, height } = useWindowSize()

  return (
    <AnimatePresence>
      {open && (
        <>
          {/* Confetti */}
          <Confetti
            width={width}
            height={height}
            recycle={false}
            numberOfPieces={500}
            gravity={0.3}
          />

          {/* Overlay */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50"
            onClick={onClose}
          />

          {/* Modal */}
          <div className="fixed inset-0 flex items-center justify-center z-50 pointer-events-none">
            <motion.div
              initial={{ scale: 0, rotate: -180, opacity: 0 }}
              animate={{ scale: 1, rotate: 0, opacity: 1 }}
              exit={{ scale: 0, rotate: 180, opacity: 0 }}
              transition={{
                type: 'spring',
                stiffness: 260,
                damping: 20,
              }}
              className="bg-white rounded-xl shadow-2xl p-8 max-w-md pointer-events-auto"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Icon */}
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: [0, 1.2, 1] }}
                transition={{ delay: 0.2, duration: 0.5 }}
                className="flex justify-center mb-4"
              >
                <div className="w-24 h-24 bg-accent-gold-500 rounded-full flex items-center justify-center text-4xl">
                  {achievement.icon}
                </div>
              </motion.div>

              {/* Title */}
              <motion.h2
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
                className="text-2xl font-bold text-center mb-2"
              >
                Achievement Unlocked!
              </motion.h2>

              {/* Achievement Name */}
              <motion.p
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
                className="text-xl font-semibold text-center mb-2"
              >
                {achievement.name}
              </motion.p>

              {/* Description */}
              <motion.p
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.6 }}
                className="text-neutral-600 text-center mb-4"
              >
                {achievement.description}
              </motion.p>

              {/* XP Reward */}
              <motion.div
                initial={{ opacity: 0, scale: 0 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.7 }}
                className="flex items-center justify-center gap-2 mb-6"
              >
                <TrophyIcon className="w-5 h-5 text-accent-gold-500" />
                <span className="text-lg font-bold text-accent-gold-600">
                  +{achievement.xpReward} XP
                </span>
              </motion.div>

              {/* Close Button */}
              <motion.button
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.8 }}
                onClick={onClose}
                className="w-full px-6 py-3 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-lg transition-colors"
              >
                Awesome!
              </motion.button>
            </motion.div>
          </div>
        </>
      )}
    </AnimatePresence>
  )
}
```

---

## React Query Setup

### File: `/src/lib/queryClient.ts`

```typescript
import { QueryClient } from '@tanstack/react-query'

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      gcTime: 1000 * 60 * 30, // 30 minutes (formerly cacheTime)
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
})
```

### File: `/src/hooks/useUser.ts`

```typescript
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api/client'

export function useUser() {
  return useQuery({
    queryKey: ['user'],
    queryFn: async () => {
      const { data } = await apiClient.get('/api/v1/auth/me')
      return data
    },
    staleTime: 1000 * 60 * 10, // 10 minutes
  })
}
```

### File: `/src/hooks/useLeaderboard.ts`

```typescript
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api/client'

type LeaderboardType = 'xp' | 'quizzes' | 'accuracy' | 'streaks'

export function useLeaderboard(type: LeaderboardType, period: string = 'all') {
  return useQuery({
    queryKey: ['leaderboard', type, period],
    queryFn: async () => {
      const { data } = await apiClient.get(`/api/v1/leaderboard/${type}`, {
        params: { period },
      })
      return data
    },
    staleTime: 1000 * 30, // 30 seconds
    refetchInterval: 1000 * 30, // Auto-refetch every 30s
  })
}
```

---

## Error Handling

### Global Error Handler

**File:** `/src/components/ErrorBoundary.tsx`

```typescript
import { Component, ReactNode } from 'react'

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error?: Error
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: any) {
    console.error('Error caught by boundary:', error, errorInfo)
    // Send to error tracking service (Sentry, etc.)
  }

  render() {
    if (this.state.hasError) {
      return (
        this.props.fallback || (
          <div className="flex flex-col items-center justify-center min-h-screen p-4">
            <h1 className="text-2xl font-bold mb-4">Something went wrong</h1>
            <p className="text-neutral-600 mb-4">
              We're sorry for the inconvenience. Please try refreshing the page.
            </p>
            <button
              onClick={() => window.location.reload()}
              className="px-6 py-3 bg-primary-600 text-white rounded-lg"
            >
              Refresh Page
            </button>
          </div>
        )
      )
    }

    return this.props.children
  }
}
```

### API Error Handler

**File:** `/src/lib/api/errors.ts`

```typescript
export function handleApiError(error: any) {
  if (error.response) {
    // Server responded with error
    const { status, data } = error.response

    switch (status) {
      case 400:
        return data.error?.message || 'Invalid request'
      case 401:
        return 'Unauthorized - please log in'
      case 403:
        return 'Access denied'
      case 404:
        return 'Resource not found'
      case 422:
        // Validation errors
        const errors = data.errors || []
        return errors.map((e: any) => e.message).join(', ')
      case 429:
        return 'Too many requests - please slow down'
      case 500:
        return 'Server error - please try again later'
      default:
        return 'An error occurred'
    }
  } else if (error.request) {
    // Network error
    return 'Network error - check your connection'
  } else {
    // Something else happened
    return error.message || 'Unknown error'
  }
}
```

---

## LocalStorage Persistence

### File: `/src/hooks/useLocalStorage.ts`

```typescript
import { useState, useEffect } from 'react'

export function useLocalStorage<T>(key: string, initialValue: T) {
  // Get initial value from localStorage or use provided initial value
  const [storedValue, setStoredValue] = useState<T>(() => {
    try {
      const item = window.localStorage.getItem(key)
      return item ? JSON.parse(item) : initialValue
    } catch (error) {
      console.error(error)
      return initialValue
    }
  })

  // Update localStorage when value changes
  const setValue = (value: T | ((val: T) => T)) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value
      setStoredValue(valueToStore)
      window.localStorage.setItem(key, JSON.stringify(valueToStore))
    } catch (error) {
      console.error(error)
    }
  }

  return [storedValue, setValue] as const
}
```

### Quiz Auto-Save

```typescript
// In quiz component
import { useEffect } from 'react'
import { useQuizStore } from '@/stores/quizStore'

export function QuizTaking() {
  const quizState = useQuizStore()

  // Auto-save every 10 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      localStorage.setItem('quiz-backup', JSON.stringify(quizState))
    }, 10000)

    return () => clearInterval(interval)
  }, [quizState])

  // ... rest of component
}
```

---

## Accessibility Implementation

### Keyboard Navigation

```typescript
// In QuizQuestionCard component
import { useEffect } from 'react'

export function QuizQuestionCard({ question, onAnswerSelect }: Props) {
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      // Number keys 1-4 select answers A-D
      if (['1', '2', '3', '4'].includes(e.key)) {
        const answers = ['A', 'B', 'C', 'D']
        onAnswerSelect(answers[parseInt(e.key) - 1])
      }

      // Letter keys A-D also work
      if (['a', 'b', 'c', 'd'].includes(e.key.toLowerCase())) {
        onAnswerSelect(e.key.toUpperCase())
      }
    }

    window.addEventListener('keydown', handleKeyPress)
    return () => window.removeEventListener('keydown', handleKeyPress)
  }, [onAnswerSelect])

  return (
    <div role="radiogroup" aria-label="Answer options">
      {/* ... options */}
    </div>
  )
}
```

### Focus Management

```typescript
// In Modal component
import { useEffect, useRef } from 'react'

export function Modal({ open, onClose, children }: ModalProps) {
  const previousFocusRef = useRef<HTMLElement | null>(null)
  const modalRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (open) {
      // Save current focus
      previousFocusRef.current = document.activeElement as HTMLElement

      // Focus modal
      modalRef.current?.focus()

      // Trap focus
      const handleTab = (e: KeyboardEvent) => {
        if (e.key === 'Tab') {
          const focusableElements = modalRef.current?.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
          )
          // ... implement focus trapping
        }

        if (e.key === 'Escape') {
          onClose()
        }
      }

      window.addEventListener('keydown', handleTab)
      return () => window.removeEventListener('keydown', handleTab)
    } else {
      // Restore focus
      previousFocusRef.current?.focus()
    }
  }, [open, onClose])

  if (!open) return null

  return (
    <div
      ref={modalRef}
      tabIndex={-1}
      role="dialog"
      aria-modal="true"
      className="..."
    >
      {children}
    </div>
  )
}
```

---

## Performance Optimization

### Code Splitting

```typescript
// Lazy load route components
import { lazy, Suspense } from 'react'

const DashboardPage = lazy(() => import('./pages/Dashboard'))
const QuizPage = lazy(() => import('./pages/Quiz'))
const AchievementsPage = lazy(() => import('./pages/Achievements'))

function App() {
  return (
    <Suspense fallback={<LoadingSpinner fullScreen />}>
      <Routes>
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/quiz" element={<QuizPage />} />
        <Route path="/achievements" element={<AchievementsPage />} />
      </Routes>
    </Suspense>
  )
}
```

### React.memo for Expensive Components

```typescript
import { memo } from 'react'

export const LeaderboardTable = memo(function LeaderboardTable({ entries }: Props) {
  // Expensive rendering logic
  return <table>{/* ... */}</table>
}, (prevProps, nextProps) => {
  // Custom comparison: only re-render if entries actually changed
  return prevProps.entries === nextProps.entries
})
```

### Virtual Scrolling for Long Lists

```typescript
import { useVirtualizer } from '@tanstack/react-virtual'
import { useRef } from 'react'

export function BookmarkList({ bookmarks }: Props) {
  const parentRef = useRef<HTMLDivElement>(null)

  const virtualizer = useVirtualizer({
    count: bookmarks.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 100, // Estimated row height
  })

  return (
    <div ref={parentRef} style={{ height: '600px', overflow: 'auto' }}>
      <div style={{ height: `${virtualizer.getTotalSize()}px`, position: 'relative' }}>
        {virtualizer.getVirtualItems().map((virtualRow) => (
          <div
            key={virtualRow.key}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: `${virtualRow.size}px`,
              transform: `translateY(${virtualRow.start}px)`,
            }}
          >
            <BookmarkCard bookmark={bookmarks[virtualRow.index]} />
          </div>
        ))}
      </div>
    </div>
  )
}
```

---

## Common Patterns

### Optimistic Updates

```typescript
// When bookmarking a question
const bookmarkMutation = useMutation({
  mutationFn: (questionId: number) =>
    apiClient.post(`/api/v1/bookmarks/questions/${questionId}`),

  // Optimistic update
  onMutate: async (questionId) => {
    // Cancel outgoing refetches
    await queryClient.cancelQueries({ queryKey: ['bookmarks'] })

    // Snapshot previous value
    const previousBookmarks = queryClient.getQueryData(['bookmarks'])

    // Optimistically update
    queryClient.setQueryData(['bookmarks'], (old: any) => ({
      ...old,
      bookmarks: [...(old?.bookmarks || []), { question_id: questionId }],
    }))

    return { previousBookmarks }
  },

  // Rollback on error
  onError: (err, questionId, context) => {
    queryClient.setQueryData(['bookmarks'], context?.previousBookmarks)
    toast.error('Failed to bookmark question')
  },

  // Refetch on success
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['bookmarks'] })
    toast.success('Question bookmarked!')
  },
})
```

---

**Next:** Testing strategy (06-testing-strategy.md)
