import { QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { queryClient } from './lib/queryClient'

// Layout
import { AppShell } from './components/layout'
import { ProtectedRoute } from './components/auth/ProtectedRoute'

// Public Pages
import { LoginPage } from './pages/LoginPage'
import { SignupPage } from './pages/SignupPage'
import { LandingPage } from './pages/LandingPage'

// Protected Pages
import { DashboardPage } from './pages/DashboardPage'
import { PracticePage } from './pages/PracticePage'
import { QuizPage } from './pages/QuizPage'
import { QuizResultsPage } from './pages/QuizResultsPage'
import { QuizHistoryPage } from './pages/QuizHistoryPage'
import { StudyPage } from './pages/StudyPage'
import { AchievementsPage } from './pages/AchievementsPage'
import { AvatarsPage } from './pages/AvatarsPage'
import { LeaderboardPage } from './pages/LeaderboardPage'
import { BookmarksPage } from './pages/BookmarksPage'
import { ProfilePage } from './pages/ProfilePage'
import { SettingsPage } from './pages/SettingsPage'
import { AdminPage } from './pages/AdminPage'

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          {/* Public routes */}
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignupPage />} />

          {/* Protected routes with AppShell */}
          <Route
            path="/app"
            element={
              <ProtectedRoute>
                <AppShell />
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/app/dashboard" replace />} />
            <Route path="dashboard" element={<DashboardPage />} />

            {/* Practice Mode */}
            <Route path="practice" element={<PracticePage />} />
            <Route path="practice/:examType/quiz" element={<QuizPage />} />
            <Route path="practice/:examType/results/:attemptId" element={<QuizResultsPage />} />
            <Route path="practice/history" element={<QuizHistoryPage />} />

            {/* Study Mode */}
            <Route path="study" element={<StudyPage />} />

            {/* Gamification */}
            <Route path="achievements" element={<AchievementsPage />} />
            <Route path="avatars" element={<AvatarsPage />} />

            {/* Social */}
            <Route path="leaderboard" element={<LeaderboardPage />} />

            {/* User */}
            <Route path="bookmarks" element={<BookmarksPage />} />
            <Route path="profile" element={<ProfilePage />} />
            <Route path="settings" element={<SettingsPage />} />

            {/* Admin */}
            <Route path="admin/*" element={<AdminPage />} />

            {/* Catch all */}
            <Route path="*" element={<Navigate to="/app/dashboard" replace />} />
          </Route>

          {/* Catch all */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

export default App
