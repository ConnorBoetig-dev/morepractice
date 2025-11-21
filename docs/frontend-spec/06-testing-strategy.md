# Frontend Testing Strategy

## Table of Contents
- [Testing Philosophy](#testing-philosophy)
- [Testing Tools](#testing-tools)
- [Unit Testing](#unit-testing)
- [Component Testing](#component-testing)
- [Integration Testing](#integration-testing)
- [End-to-End Testing](#end-to-end-testing)
- [Accessibility Testing](#accessibility-testing)
- [Coverage Targets](#coverage-targets)
- [Test File Structure](#test-file-structure)
- [Testing Utilities](#testing-utilities)
- [Mock Strategies](#mock-strategies)
- [CI/CD Integration](#cicd-integration)

---

## Testing Philosophy

### Core Principles
1. **Test user behavior, not implementation details**
   - Query elements the way users interact with them (labels, roles, text)
   - Avoid testing internal state or implementation
   - Focus on what users see and do

2. **Critical path coverage**
   - 95%+ coverage for authentication, quiz taking, payment flows
   - 80%+ coverage for general features
   - Accept lower coverage for admin tools

3. **Fast feedback loops**
   - Unit tests: < 5 seconds total
   - Component tests: < 30 seconds total
   - Integration tests: < 2 minutes total
   - E2E tests: Run on CI only (< 10 minutes)

4. **Maintainable tests**
   - Use data-testid sparingly (only when necessary)
   - Extract common test utilities
   - Keep tests DRY with custom render functions

---

## Testing Tools

### Test Runner & Framework
```bash
npm install -D vitest
npm install -D @vitest/ui
```

**Vitest Configuration** (`vitest.config.ts`):
```typescript
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/tests/setup.ts',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/tests/',
        '**/*.d.ts',
        '**/*.config.*',
        '**/mockData/',
      ],
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})
```

### Component Testing
```bash
npm install -D @testing-library/react
npm install -D @testing-library/jest-dom
npm install -D @testing-library/user-event
```

### E2E Testing
```bash
npm install -D @playwright/test
npx playwright install
```

### Accessibility Testing
```bash
npm install -D @axe-core/react
npm install -D jest-axe
```

---

## Unit Testing

### Utility Functions
Test pure functions that don't depend on React.

**Example: Score calculation** (`src/utils/scoring.test.ts`):
```typescript
import { describe, it, expect } from 'vitest'
import { calculateScore, calculateXPGained, getScoreGrade } from '@/utils/scoring'

describe('calculateScore', () => {
  it('calculates percentage correctly', () => {
    expect(calculateScore(8, 10)).toBe(80)
    expect(calculateScore(0, 10)).toBe(0)
    expect(calculateScore(10, 10)).toBe(100)
  })

  it('handles edge cases', () => {
    expect(calculateScore(0, 0)).toBe(0)
    expect(calculateScore(5, 0)).toBe(0)
  })
})

describe('getScoreGrade', () => {
  it('returns correct grade for score ranges', () => {
    expect(getScoreGrade(95)).toBe('A+')
    expect(getScoreGrade(85)).toBe('A')
    expect(getScoreGrade(75)).toBe('B')
    expect(getScoreGrade(65)).toBe('C')
    expect(getScoreGrade(50)).toBe('F')
  })
})

describe('calculateXPGained', () => {
  it('calculates XP with score multiplier', () => {
    const baseXP = 100
    expect(calculateXPGained(baseXP, 100, false)).toBe(150) // Perfect score: 1.5x
    expect(calculateXPGained(baseXP, 80, false)).toBe(120)  // Good score: 1.2x
    expect(calculateXPGained(baseXP, 60, false)).toBe(100)  // Base XP
  })

  it('applies first-time bonus', () => {
    expect(calculateXPGained(100, 80, true)).toBe(180) // 1.2x + 1.5x first-time
  })
})
```

### Custom Hooks
**Example: useTimer hook** (`src/hooks/useTimer.test.ts`):
```typescript
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useTimer } from '@/hooks/useTimer'

describe('useTimer', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('counts down from initial time', () => {
    const { result } = renderHook(() => useTimer(60))

    expect(result.current.timeRemaining).toBe(60)

    act(() => {
      vi.advanceTimersByTime(1000)
    })

    expect(result.current.timeRemaining).toBe(59)
  })

  it('calls onComplete when timer reaches zero', () => {
    const onComplete = vi.fn()
    const { result } = renderHook(() => useTimer(2, onComplete))

    act(() => {
      vi.advanceTimersByTime(2000)
    })

    expect(result.current.timeRemaining).toBe(0)
    expect(onComplete).toHaveBeenCalledOnce()
  })

  it('can pause and resume timer', () => {
    const { result } = renderHook(() => useTimer(60))

    act(() => {
      result.current.pause()
      vi.advanceTimersByTime(5000)
    })

    expect(result.current.timeRemaining).toBe(60) // Should not have decreased

    act(() => {
      result.current.resume()
      vi.advanceTimersByTime(1000)
    })

    expect(result.current.timeRemaining).toBe(59)
  })
})
```

---

## Component Testing

### Testing Library Best Practices
1. **Query Priority**:
   - `getByRole` (preferred)
   - `getByLabelText`
   - `getByPlaceholderText`
   - `getByText`
   - `getByTestId` (last resort)

2. **User Event over fireEvent**:
```typescript
// ❌ Avoid fireEvent
fireEvent.click(button)

// ✅ Use userEvent (simulates real browser behavior)
await user.click(button)
```

### Custom Render Function
**Create wrapper with providers** (`src/tests/utils/test-utils.tsx`):
```typescript
import { ReactElement } from 'react'
import { render, RenderOptions } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  })

interface CustomRenderOptions extends Omit<RenderOptions, 'wrapper'> {
  initialRoute?: string
}

export function renderWithProviders(
  ui: ReactElement,
  {
    initialRoute = '/',
    ...renderOptions
  }: CustomRenderOptions = {}
) {
  const queryClient = createTestQueryClient()

  window.history.pushState({}, 'Test page', initialRoute)

  function Wrapper({ children }: { children: React.ReactNode }) {
    return (
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          {children}
        </BrowserRouter>
      </QueryClientProvider>
    )
  }

  return {
    ...render(ui, { wrapper: Wrapper, ...renderOptions }),
    queryClient,
  }
}

// Re-export everything
export * from '@testing-library/react'
export { renderWithProviders as render }
```

### Button Component
**Test all variants and states** (`src/components/ui/Button.test.tsx`):
```typescript
import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@/tests/utils/test-utils'
import userEvent from '@testing-library/user-event'
import { Button } from './Button'

describe('Button', () => {
  it('renders with text', () => {
    render(<Button>Click me</Button>)
    expect(screen.getByRole('button', { name: /click me/i })).toBeInTheDocument()
  })

  it('calls onClick when clicked', async () => {
    const user = userEvent.setup()
    const handleClick = vi.fn()

    render(<Button onClick={handleClick}>Click me</Button>)

    await user.click(screen.getByRole('button'))

    expect(handleClick).toHaveBeenCalledOnce()
  })

  it('is disabled when disabled prop is true', async () => {
    const user = userEvent.setup()
    const handleClick = vi.fn()

    render(<Button onClick={handleClick} disabled>Click me</Button>)

    const button = screen.getByRole('button')
    expect(button).toBeDisabled()

    await user.click(button)
    expect(handleClick).not.toHaveBeenCalled()
  })

  it('applies variant classes', () => {
    const { rerender } = render(<Button variant="primary">Primary</Button>)
    expect(screen.getByRole('button')).toHaveClass('bg-primary-500')

    rerender(<Button variant="danger">Danger</Button>)
    expect(screen.getByRole('button')).toHaveClass('bg-error-500')
  })

  it('shows loading state', () => {
    render(<Button isLoading>Submit</Button>)

    const button = screen.getByRole('button')
    expect(button).toBeDisabled()
    expect(screen.getByRole('status')).toBeInTheDocument() // Loading spinner
  })
})
```

### Login Form
**Test form validation and submission** (`src/components/features/auth/LoginForm.test.tsx`):
```typescript
import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor } from '@/tests/utils/test-utils'
import userEvent from '@testing-library/user-event'
import { LoginForm } from './LoginForm'

describe('LoginForm', () => {
  it('renders form fields', () => {
    render(<LoginForm />)

    expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /log in/i })).toBeInTheDocument()
  })

  it('shows validation errors for empty fields', async () => {
    const user = userEvent.setup()
    render(<LoginForm />)

    await user.click(screen.getByRole('button', { name: /log in/i }))

    expect(await screen.findByText(/email is required/i)).toBeInTheDocument()
    expect(await screen.findByText(/password is required/i)).toBeInTheDocument()
  })

  it('shows error for invalid email format', async () => {
    const user = userEvent.setup()
    render(<LoginForm />)

    await user.type(screen.getByLabelText(/email/i), 'invalid-email')
    await user.click(screen.getByRole('button', { name: /log in/i }))

    expect(await screen.findByText(/invalid email/i)).toBeInTheDocument()
  })

  it('submits form with valid data', async () => {
    const user = userEvent.setup()
    const onSubmit = vi.fn()

    render(<LoginForm onSubmit={onSubmit} />)

    await user.type(screen.getByLabelText(/email/i), 'test@example.com')
    await user.type(screen.getByLabelText(/password/i), 'Password123!')
    await user.click(screen.getByRole('button', { name: /log in/i }))

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'Password123!',
      })
    })
  })

  it('disables submit button while loading', async () => {
    const user = userEvent.setup()
    render(<LoginForm isLoading />)

    const submitButton = screen.getByRole('button', { name: /log in/i })
    expect(submitButton).toBeDisabled()
  })

  it('shows API error message', () => {
    const errorMessage = 'Invalid credentials'
    render(<LoginForm error={errorMessage} />)

    expect(screen.getByText(errorMessage)).toBeInTheDocument()
  })
})
```

### Question Card
**Test quiz interactions** (`src/components/features/quiz/QuestionCard.test.tsx`):
```typescript
import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@/tests/utils/test-utils'
import userEvent from '@testing-library/user-event'
import { QuestionCard } from './QuestionCard'

const mockQuestion = {
  id: 1,
  questionText: 'What is the default SSH port?',
  options: {
    A: { text: '21' },
    B: { text: '22' },
    C: { text: '23' },
    D: { text: '25' },
  },
  domain: 'Network Ports',
}

describe('QuestionCard', () => {
  it('renders question and options', () => {
    render(<QuestionCard question={mockQuestion} />)

    expect(screen.getByText(mockQuestion.questionText)).toBeInTheDocument()
    expect(screen.getByRole('radio', { name: /22/i })).toBeInTheDocument()
  })

  it('calls onAnswerSelect when option is clicked', async () => {
    const user = userEvent.setup()
    const handleAnswerSelect = vi.fn()

    render(
      <QuestionCard
        question={mockQuestion}
        onAnswerSelect={handleAnswerSelect}
      />
    )

    await user.click(screen.getByRole('radio', { name: /22/i }))

    expect(handleAnswerSelect).toHaveBeenCalledWith('B')
  })

  it('shows selected answer', () => {
    render(
      <QuestionCard
        question={mockQuestion}
        selectedAnswer="B"
      />
    )

    const optionB = screen.getByRole('radio', { name: /22/i })
    expect(optionB).toBeChecked()
  })

  it('supports keyboard navigation (1-4 keys)', async () => {
    const user = userEvent.setup()
    const handleAnswerSelect = vi.fn()

    render(
      <QuestionCard
        question={mockQuestion}
        onAnswerSelect={handleAnswerSelect}
      />
    )

    await user.keyboard('2')
    expect(handleAnswerSelect).toHaveBeenCalledWith('B')

    await user.keyboard('A')
    expect(handleAnswerSelect).toHaveBeenCalledWith('A')
  })

  it('shows bookmark button when onBookmark is provided', () => {
    render(
      <QuestionCard
        question={mockQuestion}
        onBookmark={vi.fn()}
      />
    )

    expect(screen.getByRole('button', { name: /bookmark/i })).toBeInTheDocument()
  })

  it('calls onBookmark when bookmark button is clicked', async () => {
    const user = userEvent.setup()
    const handleBookmark = vi.fn()

    render(
      <QuestionCard
        question={mockQuestion}
        onBookmark={handleBookmark}
      />
    )

    await user.click(screen.getByRole('button', { name: /bookmark/i }))

    expect(handleBookmark).toHaveBeenCalledOnce()
  })

  it('shows bookmarked state', () => {
    render(
      <QuestionCard
        question={mockQuestion}
        onBookmark={vi.fn()}
        isBookmarked
      />
    )

    const bookmarkButton = screen.getByRole('button', { name: /bookmark/i })
    expect(bookmarkButton).toHaveClass('text-accent-gold-500')
  })
})
```

---

## Integration Testing

### Critical User Flows
Test multi-step flows that involve multiple components and API calls.

**Example: Quiz flow** (`src/tests/integration/quiz-flow.test.tsx`):
```typescript
import { describe, it, expect, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@/tests/utils/test-utils'
import userEvent from '@testing-library/user-event'
import { rest } from 'msw'
import { setupServer } from 'msw/node'
import { QuizPage } from '@/pages/QuizPage'

const mockQuestions = [
  {
    id: 1,
    questionText: 'What is the default SSH port?',
    options: { A: { text: '21' }, B: { text: '22' }, C: { text: '23' }, D: { text: '25' } },
    correctAnswer: 'B',
  },
  {
    id: 2,
    questionText: 'Which protocol is connectionless?',
    options: { A: { text: 'TCP' }, B: { text: 'UDP' }, C: { text: 'ICMP' }, D: { text: 'HTTP' } },
    correctAnswer: 'B',
  },
]

const server = setupServer(
  rest.post('/api/v1/quiz/start', (req, res, ctx) => {
    return res(ctx.json({
      quizId: 123,
      questions: mockQuestions,
    }))
  }),

  rest.post('/api/v1/quiz/:quizId/submit', (req, res, ctx) => {
    return res(ctx.json({
      score: 100,
      correctAnswers: 2,
      totalQuestions: 2,
      xpGained: 150,
      achievements: [
        {
          id: 1,
          name: 'Perfect Score',
          description: 'Score 100% on a quiz',
          xpReward: 50,
        },
      ],
    }))
  })
)

beforeAll(() => server.listen())
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

describe('Quiz Flow Integration', () => {
  it('completes full quiz flow: start → answer → submit → results', async () => {
    const user = userEvent.setup()

    render(<QuizPage />)

    // Step 1: Start quiz
    await user.click(screen.getByRole('button', { name: /start quiz/i }))

    // Step 2: Answer first question
    await waitFor(() => {
      expect(screen.getByText(mockQuestions[0].questionText)).toBeInTheDocument()
    })

    await user.click(screen.getByRole('radio', { name: /22/i }))
    await user.click(screen.getByRole('button', { name: /next/i }))

    // Step 3: Answer second question
    await waitFor(() => {
      expect(screen.getByText(mockQuestions[1].questionText)).toBeInTheDocument()
    })

    await user.click(screen.getByRole('radio', { name: /UDP/i }))
    await user.click(screen.getByRole('button', { name: /submit quiz/i }))

    // Step 4: View results
    await waitFor(() => {
      expect(screen.getByText(/100%/i)).toBeInTheDocument()
      expect(screen.getByText(/Perfect Score/i)).toBeInTheDocument()
      expect(screen.getByText(/150 XP/i)).toBeInTheDocument()
    })
  })

  it('saves quiz progress to localStorage', async () => {
    const user = userEvent.setup()

    render(<QuizPage />)

    await user.click(screen.getByRole('button', { name: /start quiz/i }))

    await waitFor(() => {
      expect(screen.getByText(mockQuestions[0].questionText)).toBeInTheDocument()
    })

    await user.click(screen.getByRole('radio', { name: /22/i }))

    // Check localStorage was updated
    const savedState = localStorage.getItem('quiz-123-state')
    expect(savedState).toBeTruthy()

    const parsed = JSON.parse(savedState!)
    expect(parsed.answers).toEqual({ 0: 'B' })
  })

  it('resumes quiz from saved state', async () => {
    // Pre-populate localStorage
    localStorage.setItem('quiz-123-state', JSON.stringify({
      quizId: 123,
      currentQuestionIndex: 1,
      answers: { 0: 'B' },
      startTime: new Date().toISOString(),
    }))

    render(<QuizPage />)

    await waitFor(() => {
      expect(screen.getByText(/resume quiz/i)).toBeInTheDocument()
    })

    await userEvent.click(screen.getByRole('button', { name: /resume/i }))

    // Should start at question 2
    expect(screen.getByText(mockQuestions[1].questionText)).toBeInTheDocument()
  })
})
```

---

## End-to-End Testing

### Playwright Configuration
**Setup** (`playwright.config.ts`):
```typescript
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:5173',
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 13'] },
    },
  ],
  webServer: {
    command: 'npm run dev',
    port: 5173,
    reuseExistingServer: !process.env.CI,
  },
})
```

### Critical E2E Test: Full User Journey
**Signup → Quiz → Achievement** (`e2e/user-journey.spec.ts`):
```typescript
import { test, expect } from '@playwright/test'

test.describe('New User Journey', () => {
  test('signup → complete quiz → unlock achievement', async ({ page }) => {
    // Step 1: Signup
    await page.goto('/signup')

    await page.getByLabel('Email').fill('newuser@example.com')
    await page.getByLabel('Username').fill('testuser')
    await page.getByLabel('Password').fill('SecurePass123!')
    await page.getByRole('button', { name: /sign up/i }).click()

    // Should redirect to dashboard
    await expect(page).toHaveURL(/\/app\/dashboard/)
    await expect(page.getByText(/welcome, testuser/i)).toBeVisible()

    // Step 2: Start a quiz
    await page.getByRole('link', { name: /practice/i }).click()
    await page.getByText(/security\+/i).click()
    await page.getByRole('button', { name: /start quiz/i }).click()

    // Step 3: Answer questions
    const questions = page.locator('[data-testid="question-card"]')
    const questionCount = await questions.count()

    for (let i = 0; i < questionCount; i++) {
      // Select first option for simplicity
      await page.locator('input[type="radio"]').first().click()

      if (i < questionCount - 1) {
        await page.getByRole('button', { name: /next/i }).click()
      } else {
        await page.getByRole('button', { name: /submit/i }).click()
      }
    }

    // Step 4: View results
    await expect(page.getByText(/quiz complete/i)).toBeVisible()

    const score = page.getByTestId('quiz-score')
    await expect(score).toBeVisible()

    // Step 5: Check for achievement unlock
    const achievementModal = page.getByRole('dialog', { name: /achievement unlocked/i })

    if (await achievementModal.isVisible()) {
      await expect(achievementModal.getByText(/first steps/i)).toBeVisible()
      await expect(achievementModal.getByText(/50 XP/i)).toBeVisible()

      await page.getByRole('button', { name: /continue/i }).click()
    }

    // Step 6: Verify dashboard updated
    await page.goto('/app/dashboard')

    const xpDisplay = page.getByTestId('user-xp')
    await expect(xpDisplay).toContainText(/\d+ XP/)
  })
})

test.describe('Authentication', () => {
  test('redirects unauthenticated users to login', async ({ page }) => {
    await page.goto('/app/dashboard')
    await expect(page).toHaveURL(/\/login/)
  })

  test('persists authentication across page refreshes', async ({ page }) => {
    // Login
    await page.goto('/login')
    await page.getByLabel('Email').fill('test@example.com')
    await page.getByLabel('Password').fill('Password123!')
    await page.getByRole('button', { name: /log in/i }).click()

    await expect(page).toHaveURL(/\/app\/dashboard/)

    // Refresh page
    await page.reload()

    // Should still be authenticated
    await expect(page).toHaveURL(/\/app\/dashboard/)
    await expect(page.getByText(/welcome/i)).toBeVisible()
  })
})

test.describe('Quiz Features', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/login')
    await page.getByLabel('Email').fill('test@example.com')
    await page.getByLabel('Password').fill('Password123!')
    await page.getByRole('button', { name: /log in/i }).click()
    await expect(page).toHaveURL(/\/app\/dashboard/)
  })

  test('bookmark question during quiz', async ({ page }) => {
    await page.goto('/app/practice')
    await page.getByText(/security\+/i).click()
    await page.getByRole('button', { name: /start quiz/i }).click()

    // Bookmark first question
    await page.getByRole('button', { name: /bookmark/i }).first().click()

    await expect(page.getByText(/bookmarked/i)).toBeVisible()

    // Navigate to bookmarks
    await page.getByRole('link', { name: /bookmarks/i }).click()

    await expect(page.getByTestId('bookmark-list')).toHaveCount(1)
  })

  test('timer counts down during timed quiz', async ({ page }) => {
    await page.goto('/app/practice')
    await page.getByText(/security\+/i).click()

    // Enable timer
    await page.getByRole('checkbox', { name: /timed mode/i }).check()
    await page.getByRole('button', { name: /start quiz/i }).click()

    const timer = page.getByTestId('quiz-timer')
    const initialTime = await timer.textContent()

    // Wait 2 seconds
    await page.waitForTimeout(2000)

    const newTime = await timer.textContent()
    expect(newTime).not.toBe(initialTime)
  })
})
```

---

## Accessibility Testing

### Automated Accessibility Testing
**Setup jest-axe** (`src/tests/setup.ts`):
```typescript
import '@testing-library/jest-dom'
import { toHaveNoViolations } from 'jest-axe'

expect.extend(toHaveNoViolations)
```

**Example component test** (`src/components/ui/Button.a11y.test.tsx`):
```typescript
import { describe, it, expect } from 'vitest'
import { render } from '@/tests/utils/test-utils'
import { axe } from 'jest-axe'
import { Button } from './Button'

describe('Button Accessibility', () => {
  it('should not have accessibility violations', async () => {
    const { container } = render(<Button>Click me</Button>)
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })

  it('should not have violations when disabled', async () => {
    const { container } = render(<Button disabled>Click me</Button>)
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
```

### Manual Accessibility Testing Checklist
- [ ] Keyboard navigation works (Tab, Enter, Arrow keys)
- [ ] Focus indicators are visible
- [ ] Screen reader announces all interactive elements
- [ ] Color contrast meets WCAG AA (4.5:1 for normal text)
- [ ] Form labels are properly associated
- [ ] Error messages are announced
- [ ] Modals trap focus
- [ ] Skip links work
- [ ] ARIA attributes are correct

---

## Coverage Targets

### Overall Coverage Goals
- **Statements**: 80%+
- **Branches**: 75%+
- **Functions**: 80%+
- **Lines**: 80%+

### Critical Path Coverage (95%+)
- Authentication flows (login, signup, password reset)
- Quiz taking (start, answer, submit)
- Payment flows (if implemented)
- Achievement unlocks
- Leaderboard updates

### Acceptable Lower Coverage
- Admin pages: 60%+
- Error boundaries: 70%+
- UI-only components (animations, transitions): 60%+

### Running Coverage Reports
```bash
# Generate coverage report
npm run test:coverage

# View HTML report
open coverage/index.html
```

---

## Test File Structure

```
src/
├── components/
│   ├── ui/
│   │   ├── Button.tsx
│   │   └── Button.test.tsx
│   └── features/
│       ├── auth/
│       │   ├── LoginForm.tsx
│       │   └── LoginForm.test.tsx
│       └── quiz/
│           ├── QuestionCard.tsx
│           └── QuestionCard.test.tsx
├── hooks/
│   ├── useTimer.ts
│   └── useTimer.test.ts
├── utils/
│   ├── scoring.ts
│   └── scoring.test.ts
├── tests/
│   ├── setup.ts
│   ├── utils/
│   │   └── test-utils.tsx
│   ├── mocks/
│   │   ├── handlers.ts
│   │   └── server.ts
│   └── integration/
│       ├── quiz-flow.test.tsx
│       └── auth-flow.test.tsx
└── e2e/
    ├── user-journey.spec.ts
    ├── authentication.spec.ts
    └── quiz-features.spec.ts
```

### Naming Conventions
- Unit/Component tests: `ComponentName.test.tsx`
- Accessibility tests: `ComponentName.a11y.test.tsx`
- Integration tests: `feature-name.test.tsx`
- E2E tests: `feature-name.spec.ts`

---

## Testing Utilities

### Mock Server Setup (MSW)
**API mock handlers** (`src/tests/mocks/handlers.ts`):
```typescript
import { rest } from 'msw'

export const handlers = [
  // Auth
  rest.post('/api/v1/auth/login', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        user: { id: 1, email: 'test@example.com', username: 'testuser' },
        access_token: 'mock-access-token',
        refresh_token: 'mock-refresh-token',
      })
    )
  }),

  // User profile
  rest.get('/api/v1/users/me', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        id: 1,
        email: 'test@example.com',
        username: 'testuser',
        level: 5,
        xp: 1250,
        streak: 7,
      })
    )
  }),

  // Leaderboard
  rest.get('/api/v1/leaderboard/xp', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        leaderboard: [
          { rank: 1, username: 'topuser', xp: 5000 },
          { rank: 2, username: 'testuser', xp: 1250 },
        ],
      })
    )
  }),
]
```

**Server setup** (`src/tests/mocks/server.ts`):
```typescript
import { setupServer } from 'msw/node'
import { handlers } from './handlers'

export const server = setupServer(...handlers)
```

### Custom Testing Utilities
**Wait for loading states** (`src/tests/utils/test-utils.tsx`):
```typescript
export async function waitForLoadingToFinish() {
  await waitFor(() => {
    expect(screen.queryByRole('status')).not.toBeInTheDocument()
  })
}

export function expectLoadingState() {
  expect(screen.getByRole('status')).toBeInTheDocument()
}
```

### Mock Data Generators
**Generate test questions** (`src/tests/utils/mockData.ts`):
```typescript
export function generateMockQuestion(overrides = {}) {
  return {
    id: Math.floor(Math.random() * 1000),
    questionText: 'Sample question text?',
    options: {
      A: { text: 'Option A' },
      B: { text: 'Option B' },
      C: { text: 'Option C' },
      D: { text: 'Option D' },
    },
    correctAnswer: 'B',
    domain: 'Sample Domain',
    ...overrides,
  }
}

export function generateMockQuizResults(overrides = {}) {
  return {
    score: 80,
    correctAnswers: 8,
    totalQuestions: 10,
    xpGained: 120,
    achievements: [],
    ...overrides,
  }
}
```

---

## Mock Strategies

### API Mocking
Use MSW (Mock Service Worker) for all API calls in tests:

**Advantages:**
- Works at network level (intercepts fetch/axios)
- Same code for tests and Storybook
- Can test loading/error states easily

**Example: Testing error states**:
```typescript
it('shows error message when login fails', async () => {
  server.use(
    rest.post('/api/v1/auth/login', (req, res, ctx) => {
      return res(
        ctx.status(401),
        ctx.json({ detail: 'Invalid credentials' })
      )
    })
  )

  const user = userEvent.setup()
  render(<LoginForm />)

  await user.type(screen.getByLabelText(/email/i), 'wrong@example.com')
  await user.type(screen.getByLabelText(/password/i), 'wrongpass')
  await user.click(screen.getByRole('button', { name: /log in/i }))

  await waitFor(() => {
    expect(screen.getByText(/invalid credentials/i)).toBeInTheDocument()
  })
})
```

### LocalStorage Mocking
```typescript
beforeEach(() => {
  localStorage.clear()
})

// Mock specific items
beforeEach(() => {
  localStorage.setItem('access_token', 'mock-token')
})
```

### Date/Time Mocking
```typescript
import { vi } from 'vitest'

beforeEach(() => {
  vi.setSystemTime(new Date('2024-01-15T12:00:00Z'))
})

afterEach(() => {
  vi.useRealTimers()
})
```

---

## CI/CD Integration

### GitHub Actions Workflow
**`.github/workflows/test.yml`**:
```yaml
name: Test

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run unit tests
        run: npm run test:coverage

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage/coverage-final.json

      - name: Install Playwright
        run: npx playwright install --with-deps

      - name: Run E2E tests
        run: npm run test:e2e

      - name: Upload Playwright report
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: playwright-report
          path: playwright-report/
```

### Pre-commit Hook
**`.husky/pre-commit`**:
```bash
#!/bin/sh
. "$(dirname "$0")/_/husky.sh"

# Run tests on staged files
npm run test:staged

# Run linter
npm run lint:staged
```

**`package.json` scripts**:
```json
{
  "scripts": {
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest run --coverage",
    "test:staged": "vitest related --run",
    "test:e2e": "playwright test",
    "test:e2e:ui": "playwright test --ui"
  }
}
```

---

## Testing Checklist

### Before Merging PR
- [ ] All unit tests pass
- [ ] Coverage meets targets (80%+)
- [ ] Integration tests pass for modified flows
- [ ] E2E tests pass (if applicable)
- [ ] No accessibility violations (axe-core)
- [ ] Manual keyboard navigation tested
- [ ] Tested on mobile viewport
- [ ] Error states tested
- [ ] Loading states tested

### New Feature Checklist
- [ ] Unit tests for utilities/hooks
- [ ] Component tests for UI components
- [ ] Integration test for complete flow
- [ ] E2E test for critical path (if applicable)
- [ ] Accessibility test
- [ ] Error boundary test
- [ ] Loading skeleton test

---

## Summary

This testing strategy ensures:
1. **High confidence** in code changes with 80%+ coverage
2. **Fast feedback** with unit tests completing in < 5 seconds
3. **Comprehensive coverage** of critical user journeys
4. **Accessibility compliance** with automated and manual testing
5. **Maintainable tests** using Testing Library best practices

**Test Distribution:**
- 70% Unit tests (hooks, utilities, isolated components)
- 20% Integration tests (multi-component flows)
- 10% E2E tests (critical user journeys only)

**Next Steps:**
1. Set up Vitest and Testing Library
2. Configure MSW for API mocking
3. Write tests for critical components first (auth, quiz)
4. Integrate coverage reporting in CI
5. Add E2E tests for signup/login/quiz flow
