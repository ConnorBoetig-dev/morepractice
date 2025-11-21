import { NavLink } from 'react-router-dom'
import { cn } from '@/lib/utils'
import {
  LayoutDashboard,
  Target,
  Trophy,
  Users,
  User,
} from 'lucide-react'

interface MobileNavProps {
  className?: string
}

const mobileNavItems = [
  { to: '/app/dashboard', icon: LayoutDashboard, label: 'Home' },
  { to: '/app/practice', icon: Target, label: 'Practice' },
  { to: '/app/achievements', icon: Trophy, label: 'Achieve' },
  { to: '/app/leaderboard', icon: Users, label: 'Ranks' },
  { to: '/app/profile', icon: User, label: 'Profile' },
]

export function MobileNav({ className }: MobileNavProps) {
  return (
    <nav
      className={cn(
        'fixed bottom-0 left-0 right-0 bg-white border-t border-neutral-200 z-50',
        className
      )}
    >
      <ul className="flex justify-around items-center h-16">
        {mobileNavItems.map((item) => (
          <li key={item.to}>
            <NavLink
              to={item.to}
              className={({ isActive }) =>
                cn(
                  'flex flex-col items-center justify-center px-3 py-2 min-w-[64px]',
                  isActive ? 'text-primary-500' : 'text-neutral-500'
                )
              }
            >
              <item.icon className="h-5 w-5" />
              <span className="text-xs mt-1">{item.label}</span>
            </NavLink>
          </li>
        ))}
      </ul>
    </nav>
  )
}
