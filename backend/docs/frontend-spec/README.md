# Frontend Specification

Complete technical specification for the CompTIA Practice Test Platform frontend application built with React 18, TypeScript, and Vite.

## Overview

This specification suite provides comprehensive guidance for building a production-ready React frontend that interfaces with the CompTIA Practice Test Platform API. The frontend is a portfolio piece showcasing clean, modern UI design with gamification elements, designed to demonstrate full-stack development capabilities.

**Project Type**: Single-page application (SPA)
**Tech Stack**: React 18 + TypeScript + Vite + Tailwind CSS
**Target Users**: Computer professionals studying for CompTIA certifications
**Estimated Timeline**: 14 weeks (7 two-week sprints)
**Total Specification Pages**: ~85 pages

---

## Documents

### Core Specifications

#### [00-overview.md](./00-overview.md) - Project Overview
**5 pages** | Start here for project context

- Project goals and success criteria
- Complete feature list (37 features across 10 categories)
- Technology stack with rationale
- 14-week development timeline (Sprint-by-sprint breakdown)
- Performance and accessibility requirements
- Risk assessment and mitigations

**Read this first** to understand the project scope and goals.

---

#### [01-design-system.md](./01-design-system.md) - Design System
**12 pages** | Visual design language

- Color palette (Primary, Success, Error, Warning, Accent colors)
- Typography system (System fonts, sizes, weights)
- Spacing and layout grid (4px base unit)
- Component specifications (Button, Input, Card, Badge, Modal, Toast, Progress)
- Animation guidelines
- Responsive breakpoints (320px - 1920px+)
- Accessibility standards (WCAG 2.1 AA)

**Read this** when implementing UI components to ensure visual consistency.

---

#### [02-information-architecture.md](./02-information-architecture.md) - Information Architecture
**8 pages** | Site structure and navigation

- Complete site map (35 routes)
- Navigation patterns (Sidebar for desktop, Bottom tabs for mobile)
- User flows:
  - New user onboarding (10 steps)
  - Daily study session (12 steps)
  - Achievement hunting (13 steps)
  - Admin content management (13 steps)
- Empty states and error states
- Loading states and skeletons

**Read this** when setting up routing and navigation structure.

---

#### [03-page-specifications.md](./03-page-specifications.md) - Page Specifications
**25 pages** | Detailed layouts for all pages

Comprehensive specifications for all 14 major pages:
- Dashboard (stats, quick actions, activity feed)
- Practice Mode (exam selection, quiz config, quiz taking, results)
- Study Mode (session setup, active session)
- Achievements Gallery (filter, sort, progress tracking)
- Leaderboards (5 types: XP, Streak, Accuracy, Speed, All-time)
- User Profiles (public profile, stats, achievements)
- Bookmarks (list, notes, quick quiz)
- Admin (dashboard, user management, question management)

**Read this** when implementing specific pages to understand layout requirements.

---

#### [04-component-architecture.md](./04-component-architecture.md) - Component Architecture
**15 pages** | Component hierarchy and structure

- Complete component tree (~40 components)
- Component organization (`/ui`, `/layout`, `/features`)
- State management strategy (Zustand + React Query)
- Component interfaces and props
- Custom hooks:
  - `useAuth()` - Authentication state
  - `useQuiz()` - Quiz state management
  - `useTimer()` - Countdown timer
  - `useLeaderboard()` - Leaderboard data with polling
- Reusable patterns

**Read this** when structuring the codebase and creating components.

---

#### [05-feature-implementation-guide.md](./05-feature-implementation-guide.md) - Implementation Guide
**10 pages** | Practical code examples

Detailed implementation patterns with full code examples:
- Authentication flow (API client with token refresh)
- Quiz taking flow (state management, timer, submission)
- Achievement unlock animation (Framer Motion + confetti)
- React Query setup (caching, auto-refresh)
- Error handling (Error boundaries, API error handler)
- LocalStorage persistence (quiz auto-save)
- Accessibility implementation (keyboard nav, focus management)
- Performance optimization (code splitting, memoization)
- Optimistic updates pattern

**Read this** when implementing specific features for working code patterns.

---

#### [06-testing-strategy.md](./06-testing-strategy.md) - Testing Strategy
**13 pages** | Comprehensive testing approach

- Testing philosophy and principles
- Tool setup (Vitest, Testing Library, Playwright)
- Unit testing (utilities, hooks)
- Component testing (with examples)
- Integration testing (multi-step flows)
- E2E testing (critical user journeys)
- Accessibility testing (jest-axe)
- Coverage targets:
  - Overall: 80%+
  - Critical paths: 95%+
- Mock strategies (MSW for API mocking)
- CI/CD integration

**Read this** when setting up tests or adding test coverage.

---

#### [07-project-setup.md](./07-project-setup.md) - Project Setup
**12 pages** | Step-by-step setup instructions

Complete setup guide from scratch:
- Prerequisites and software requirements
- Creating Vite project with React + TypeScript
- Project structure (directory organization)
- Installing all dependencies
- Configuration files:
  - TypeScript (`tsconfig.json`)
  - Vite (`vite.config.ts`)
  - Vitest (`vitest.config.ts`)
  - Tailwind CSS (`tailwind.config.js`)
  - ESLint and Prettier
- Environment variables setup
- Shadcn/ui installation and configuration
- Git hooks with Husky
- Development workflow
- Deployment (Netlify, Vercel, Docker)
- Troubleshooting guide

**Read this first** when starting development to set up the project correctly.

---

## Quick Start

### For Developers Starting Fresh

1. **Read in this order**:
   - [00-overview.md](./00-overview.md) - Understand the project
   - [07-project-setup.md](./07-project-setup.md) - Set up the project
   - [01-design-system.md](./01-design-system.md) - Understand the design language
   - [04-component-architecture.md](./04-component-architecture.md) - Understand the structure

2. **Set up the project**:
   ```bash
   npm create vite@latest frontend -- --template react-ts
   cd frontend
   npm install
   # Follow all steps in 07-project-setup.md
   ```

3. **Start development**:
   - Implement authentication flow first (Sprint 1)
   - Then build out quiz system (Sprint 2-3)
   - Follow the sprint timeline in `00-overview.md`

### For Designers/UX Reviewers

1. Read [01-design-system.md](./01-design-system.md) for the visual design language
2. Review [02-information-architecture.md](./02-information-architecture.md) for user flows
3. Check [03-page-specifications.md](./03-page-specifications.md) for detailed page layouts

### For QA/Testers

1. Read [06-testing-strategy.md](./06-testing-strategy.md) for testing approach
2. Review [02-information-architecture.md](./02-information-architecture.md) for user flows to test
3. Check [03-page-specifications.md](./03-page-specifications.md) for expected page behavior

---

## Quick Reference

### Technology Stack

**Core**:
- React 18.3
- TypeScript 5.5
- Vite 5.3

**State Management**:
- Zustand (global state)
- React Query / TanStack Query (server state)

**Routing**:
- React Router v6

**Styling**:
- Tailwind CSS 3.4
- Shadcn/ui (component library)
- System fonts (no custom fonts)

**Forms & Validation**:
- React Hook Form
- Zod

**API & Data**:
- Axios
- React Query

**Animations**:
- Framer Motion
- React Confetti

**Charts**:
- Recharts

**Testing**:
- Vitest
- React Testing Library
- Playwright
- jest-axe

**Code Quality**:
- ESLint
- Prettier
- Husky + lint-staged

### Color Reference

```css
/* Primary - Learning, Progress */
--primary-500: #3b82f6

/* Success - Correct Answers */
--success-500: #22c55e

/* Error - Incorrect Answers */
--error-500: #ef4444

/* Warning - Time Warnings */
--warning-500: #f59e0b

/* Accent Colors */
--accent-purple-500: #a855f7  /* XP */
--accent-orange-500: #f97316  /* Streaks */
--accent-gold-500: #f59e0b    /* Achievements */
```

### Key Routes

```
Public Routes:
  /                  - Landing page
  /login             - Login
  /signup            - Signup
  /forgot-password   - Password reset

Authenticated Routes:
  /app/dashboard              - Main dashboard
  /app/practice               - Practice mode
  /app/study                  - Study mode
  /app/achievements           - Achievements gallery
  /app/leaderboard            - Leaderboards
  /app/profile                - User profile
  /app/bookmarks              - Bookmarked questions
  /app/admin                  - Admin dashboard
```

### Component Structure

```
src/
├── components/
│   ├── ui/              # Base UI (Button, Input, Card, Badge, etc.)
│   ├── layout/          # AppShell, Sidebar, MobileNav
│   └── features/        # Feature-specific components
│       ├── auth/        # LoginForm, SignupForm, ProfileEditForm
│       ├── quiz/        # QuizHeader, QuestionCard, QuizResults
│       ├── study/       # StudyQuestion, StudyFeedback
│       ├── achievements/# AchievementCard, UnlockModal
│       ├── leaderboard/ # LeaderboardTable, Tabs, Filters
│       ├── profile/     # ProfileCard, ProfileStats, AvatarSelector
│       ├── bookmarks/   # BookmarkCard, BookmarkList
│       └── admin/       # UserTable, QuestionEditor
```

### API Endpoints (Backend)

See `docs/frontend/api-reference.md` for complete API documentation.

**Key endpoints**:
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/signup` - Signup
- `GET /api/v1/users/me` - Get current user
- `POST /api/v1/quiz/start` - Start quiz
- `POST /api/v1/quiz/{id}/submit` - Submit quiz
- `GET /api/v1/achievements` - Get achievements
- `GET /api/v1/leaderboard/{type}` - Get leaderboard

### Coverage Targets

- Overall: **80%+**
- Critical paths (auth, quiz, payment): **95%+**
- Admin tools: **60%+**

### Performance Targets

- Initial load: **< 3 seconds** (3G connection)
- Lighthouse score: **> 90**
- Bundle size: **< 500KB** (gzipped)
- Time to Interactive: **< 5 seconds**

### Accessibility Requirements

- WCAG 2.1 AA compliance
- Keyboard navigation support
- Screen reader tested
- Color contrast 4.5:1 minimum
- Focus indicators visible

---

## Development Timeline

**Total Duration**: 14 weeks (7 two-week sprints)

### Sprint Overview

| Sprint | Focus | Key Deliverables |
|--------|-------|------------------|
| **Sprint 1** (Weeks 1-2) | Project Setup & Auth | Vite project, auth flows, protected routes |
| **Sprint 2** (Weeks 3-4) | Quiz System Core | Quiz configuration, question display, answer selection |
| **Sprint 3** (Weeks 5-6) | Quiz Features | Timer, bookmarks, results, XP calculations |
| **Sprint 4** (Weeks 7-8) | Gamification | Achievements, level system, leaderboards |
| **Sprint 5** (Weeks 9-10) | Study Mode & Bookmarks | Study session flow, bookmark management |
| **Sprint 6** (Weeks 11-12) | Admin & Polish | Admin dashboard, content management |
| **Sprint 7** (Weeks 13-14) | Testing & Launch | E2E tests, performance optimization, deployment |

See [00-overview.md](./00-overview.md) for detailed sprint breakdowns.

---

## Feature List

### Core Features (37 total)

**Authentication & User Management** (6 features):
- Email/password authentication
- JWT token-based sessions
- Password reset flow
- User profile management
- Avatar selection
- Privacy settings

**Quiz System** (8 features):
- Multiple exam types (Security+, Network+, etc.)
- Configurable quiz (question count, domains, timer)
- Question navigation
- Bookmark questions
- Review flagged questions
- Timed/untimed modes
- Results with detailed breakdown
- Quiz history

**Study Mode** (5 features):
- Domain-based study
- Immediate feedback
- Detailed explanations
- Study session tracking
- Resume active sessions

**Gamification** (7 features):
- XP system with levels
- Achievement system (30+ achievements)
- Daily streak tracking
- 5 leaderboard types (XP, Streak, Accuracy, Speed, All-time)
- Progress tracking
- Level-up animations
- Achievement unlock celebrations

**Bookmarks & Review** (3 features):
- Bookmark questions during quiz
- Add personal notes
- Generate quiz from bookmarks

**Analytics & Reporting** (4 features):
- Performance dashboard
- Domain-specific statistics
- Progress over time charts
- Strength/weakness analysis

**Social Features** (2 features):
- Public user profiles
- Leaderboard rankings

**Admin Tools** (2 features):
- User management
- Question management (CRUD)

---

## API Integration

### Backend API

The backend API is fully documented in `docs/frontend/api-reference.md`.

**Base URL**: `http://localhost:8000/api/v1`

**Authentication**: JWT tokens (Bearer scheme)

**Token Refresh**: Automatic refresh on 401 responses

### Example API Client Setup

```typescript
import axios from 'axios'

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL + '/api/v1',
})

// Request interceptor - add token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor - refresh token on 401
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      const refreshToken = localStorage.getItem('refresh_token')
      const { data } = await axios.post('/api/v1/auth/refresh', {
        refresh_token: refreshToken,
      })
      localStorage.setItem('access_token', data.access_token)
      return apiClient(originalRequest)
    }
    return Promise.reject(error)
  }
)
```

---

## Design Principles

### Core Philosophy

1. **Clarity over flair** - Information is easy to find and understand
2. **Professional, not playful** - Suitable for adult learners
3. **Accessibility by default** - WCAG 2.1 AA compliance from day one
4. **Performance matters** - Fast load times, smooth interactions
5. **Mobile-first** - Responsive design from 320px to 1920px+

### Visual Style

**Inspired by**:
- Duolingo (gamification, progress tracking)
- Khan Academy (clean educational interface)
- FreeCodeCamp (achievement system)

**Characteristics**:
- Clean, minimal layouts
- Generous whitespace
- Clear information hierarchy
- Subtle animations for delight
- System fonts for performance

### Accessibility

- Keyboard navigation (Tab, Enter, Arrow keys, 1-4 for quiz answers)
- Screen reader support (ARIA labels, semantic HTML)
- Color contrast minimum 4.5:1
- Focus indicators always visible
- Error messages announced
- No reliance on color alone

---

## Testing Strategy

### Test Types

**Unit Tests** (70% of tests):
- Utility functions
- Custom hooks
- Isolated components

**Integration Tests** (20% of tests):
- Multi-component flows
- Quiz flow (start → answer → submit)
- Auth flow (signup → login → dashboard)

**E2E Tests** (10% of tests):
- Critical user journeys
- Full signup → quiz → achievement flow
- Cross-browser testing

### Running Tests

```bash
# Unit/Integration tests
npm test                  # Watch mode
npm run test:coverage     # With coverage
npm run test:ui           # Vitest UI

# E2E tests
npm run test:e2e          # Headless
npm run test:e2e:ui       # Playwright UI
```

### Coverage Requirements

- Overall: 80%+
- Critical paths: 95%+
- Admin tools: 60%+

---

## Contributing

### Code Style

- Follow TypeScript strict mode
- Use functional components with hooks
- Prefer composition over prop drilling
- Keep components under 200 lines
- Extract logic to custom hooks
- Write tests for all features

### Commit Messages

```
feat: Add quiz timer functionality
fix: Correct XP calculation on quiz submit
docs: Update API integration guide
test: Add tests for achievement unlock
refactor: Extract quiz state to custom hook
```

### Pull Request Process

1. Create feature branch from `main`
2. Write code following specifications
3. Add tests (aim for 80%+ coverage)
4. Run linter and formatter
5. Ensure all tests pass
6. Create PR with clear description
7. Request review

---

## Deployment

### Production Checklist

- [ ] All tests passing (unit, integration, E2E)
- [ ] Coverage meets targets (80%+)
- [ ] Lighthouse score > 90
- [ ] Accessibility audit passed (axe-core)
- [ ] Performance budget met (< 500KB bundle)
- [ ] Environment variables configured
- [ ] API endpoints configured for production
- [ ] Error tracking set up (Sentry)
- [ ] Analytics configured (if applicable)

### Deployment Options

**Recommended**: Netlify or Vercel (easiest)

**Steps for Netlify**:
```bash
npm install -g netlify-cli
netlify login
netlify deploy --prod
```

**Steps for Vercel**:
```bash
npm install -g vercel
vercel login
vercel --prod
```

**Docker** (for self-hosting):
```bash
docker build -t comptia-frontend .
docker run -p 80:80 comptia-frontend
```

See [07-project-setup.md](./07-project-setup.md#deployment) for detailed deployment instructions.

---

## Troubleshooting

### Common Issues

**"Cannot find module '@/components/...'**
- Ensure `tsconfig.json` has correct path mapping
- Restart VS Code/dev server

**Tailwind styles not applying**
- Check `tailwind.config.js` content paths
- Verify `@tailwind` directives in `index.css`
- Restart dev server

**Tests failing with import errors**
- Ensure `vitest.config.ts` has same aliases as `vite.config.ts`
- Check test setup file is loaded

**API calls returning 401**
- Check token is stored in localStorage
- Verify token hasn't expired
- Check token refresh flow

---

## Additional Resources

### Backend Documentation
- `docs/frontend/api-reference.md` - Complete API documentation
- `docs/frontend/data-models.md` - Data models and schemas
- `docs/frontend/authentication.md` - Auth flow details

### External Resources
- [React Docs](https://react.dev)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Vite Guide](https://vitejs.dev/guide/)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [Shadcn/ui Components](https://ui.shadcn.com)
- [React Query Docs](https://tanstack.com/query/latest)
- [Zustand Docs](https://zustand-demo.pmnd.rs)

---

## Contact & Support

For questions or clarifications about this specification:

1. Review the relevant specification document first
2. Check the troubleshooting section
3. Search for similar issues in the codebase
4. Consult the backend API documentation

---

## Document Status

| Document | Status | Last Updated | Pages |
|----------|--------|--------------|-------|
| 00-overview.md | ✅ Complete | 2024-01 | 5 |
| 01-design-system.md | ✅ Complete | 2024-01 | 12 |
| 02-information-architecture.md | ✅ Complete | 2024-01 | 8 |
| 03-page-specifications.md | ✅ Complete | 2024-01 | 25 |
| 04-component-architecture.md | ✅ Complete | 2024-01 | 15 |
| 05-feature-implementation-guide.md | ✅ Complete | 2024-01 | 10 |
| 06-testing-strategy.md | ✅ Complete | 2024-01 | 13 |
| 07-project-setup.md | ✅ Complete | 2024-01 | 12 |
| README.md | ✅ Complete | 2024-01 | 5 |

**Total**: 105 pages of comprehensive frontend specification

---

## Summary

This specification suite provides everything needed to build a production-ready React frontend for the CompTIA Practice Test Platform. The documentation is comprehensive yet practical, with working code examples and clear guidance.

**Key Highlights**:
- 37 features mapped to backend API
- 14-week development timeline
- 80%+ test coverage requirement
- WCAG 2.1 AA accessibility compliance
- Performance targets (Lighthouse 90+, < 500KB bundle)
- Complete setup and deployment guide

**Ready to start?** Begin with [07-project-setup.md](./07-project-setup.md) to set up your development environment, then follow the sprint timeline in [00-overview.md](./00-overview.md).

Good luck building! 🚀
