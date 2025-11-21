import { NavLink, useNavigate } from 'react-router-dom'
import { useQueryClient } from '@tanstack/react-query'
import { cn } from '@/lib/utils'
import { useAuthStore } from '@/stores/authStore'
import { useUserProfile } from '@/hooks/useUserProfile'
import { Button } from '@/components/ui/Button'
import {
  Target,
  LayoutDashboard,
  GraduationCap,
  BookOpen,
  Trophy,
  Users,
  Bookmark,
  User,
  Settings,
  LogOut,
  Shield,
  Flame,
  Sparkles,
} from 'lucide-react'

interface SidebarProps {
  className?: string
}

const navItems = [
  { to: '/app/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/app/practice', icon: Target, label: 'Exam Mode' },
  { to: '/app/study', icon: BookOpen, label: 'Study Mode' },
  { to: '/app/achievements', icon: Trophy, label: 'Achievements' },
  { to: '/app/avatars', icon: Sparkles, label: 'Avatars' },
  { to: '/app/leaderboard', icon: Users, label: 'Leaderboard' },
  { to: '/app/bookmarks', icon: Bookmark, label: 'Bookmarks' },
  { to: '/app/profile', icon: User, label: 'Profile' },
  { to: '/app/settings', icon: Settings, label: 'Settings' },
]

export function Sidebar({ className }: SidebarProps) {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { user, logout } = useAuthStore()
  const { xp, streak, level } = useUserProfile()

  const handleLogout = () => {
    // Clear all cached queries (study sessions, user data, etc.)
    queryClient.clear()
    logout()
    navigate('/login')
  }

  return (
    <aside
      className={cn(
        'fixed left-0 top-0 h-screen w-64 bg-white dark:bg-slate-900 border-r border-neutral-200 dark:border-slate-700 flex flex-col',
        className
      )}
    >
      {/* Logo */}
      <div className="p-6 border-b border-neutral-200 dark:border-slate-700">
        <NavLink to="/app/dashboard" className="flex items-center space-x-2">
          <Target className="h-8 w-8 text-primary-500" />
          <span className="text-xl font-bold text-neutral-900 dark:text-slate-100">CompTIA Practice</span>
        </NavLink>
      </div>

      {/* User Card - Clickable to navigate to Profile */}
      {user && (
        <NavLink
          to="/app/profile"
          className="block p-4 border-b border-neutral-200 dark:border-slate-700 hover:bg-neutral-50 dark:hover:bg-slate-800 transition-colors cursor-pointer"
        >
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-full bg-primary-100 dark:bg-primary-900/50 flex items-center justify-center">
              <span className="text-primary-600 dark:text-primary-400 font-semibold">
                {user.username.charAt(0).toUpperCase()}
              </span>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-neutral-900 dark:text-slate-100 truncate">{user.username}</p>
              <p className="text-xs text-neutral-500 dark:text-slate-400">Level {level}</p>
            </div>
          </div>
          <div className="mt-3 flex items-center space-x-4 text-xs">
            <div className="flex items-center space-x-1 text-accent-purple-500">
              <Sparkles className="h-3.5 w-3.5" />
              <span>{xp} XP</span>
            </div>
            <div className="flex items-center space-x-1 text-accent-orange-500">
              <Flame className="h-3.5 w-3.5" />
              <span>{streak} day streak</span>
            </div>
          </div>
        </NavLink>
      )}

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto p-4">
        <ul className="space-y-1">
          {navItems.map((item) => (
            <li key={item.to}>
              <NavLink
                to={item.to}
                className={({ isActive }) =>
                  cn(
                    'flex items-center space-x-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                    isActive
                      ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400'
                      : 'text-neutral-600 dark:text-slate-400 hover:bg-neutral-100 dark:hover:bg-slate-800 hover:text-neutral-900 dark:hover:text-slate-100'
                  )
                }
              >
                <item.icon className="h-5 w-5" />
                <span>{item.label}</span>
              </NavLink>
            </li>
          ))}

          {/* Admin Link (conditional) */}
          {user?.isAdmin && (
            <li className="pt-4 mt-4 border-t border-neutral-200 dark:border-slate-700">
              <NavLink
                to="/app/admin"
                className={({ isActive }) =>
                  cn(
                    'flex items-center space-x-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                    isActive
                      ? 'bg-error-50 dark:bg-error-900/30 text-error-600 dark:text-error-400'
                      : 'text-neutral-600 dark:text-slate-400 hover:bg-neutral-100 dark:hover:bg-slate-800 hover:text-neutral-900 dark:hover:text-slate-100'
                  )
                }
              >
                <Shield className="h-5 w-5" />
                <span>Admin Panel</span>
              </NavLink>
            </li>
          )}
        </ul>
      </nav>

      {/* Logout */}
      <div className="p-4 border-t border-neutral-200 dark:border-slate-700">
        <Button
          variant="ghost"
          className="w-full justify-start text-neutral-600 dark:text-slate-400 hover:text-error-600 dark:hover:text-error-400"
          onClick={handleLogout}
        >
          <LogOut className="h-5 w-5 mr-3" />
          Logout
        </Button>
      </div>
    </aside>
  )
}
