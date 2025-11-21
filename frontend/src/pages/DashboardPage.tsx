import { useState } from 'react'
import { useAuthStore } from '@/stores/authStore'
import { useUserProfile } from '@/hooks/useUserProfile'
import { Button } from '@/components/ui/Button'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Target, Trophy, Flame, TrendingUp, BookOpen } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

export function DashboardPage() {
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const { xp, level, streak, quizCount } = useUserProfile()
  const [hoveredStat, setHoveredStat] = useState<string | null>(null)

  if (!user) {
    return null
  }

  return (
    <div className="p-6">
      {/* Welcome Section */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-neutral-900 dark:text-slate-100 mb-2">
          Welcome back, {user.username}!
        </h1>
        <p className="text-neutral-600 dark:text-slate-400">
          Ready to continue your certification journey?
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <Card
          className="cursor-pointer transition-all hover:scale-105 hover:shadow-lg hover:shadow-primary-500/20"
          onMouseEnter={() => setHoveredStat('level')}
          onMouseLeave={() => setHoveredStat(null)}
        >
          <CardContent className="py-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-medium text-slate-400">Level</p>
                <p className="text-2xl font-bold text-slate-100">{level}</p>
              </div>
              <div className="w-10 h-10 bg-primary-900/30 rounded-lg flex items-center justify-center">
                <TrendingUp className="h-5 w-5 text-primary-500" />
              </div>
            </div>
            {hoveredStat === 'level' && (
              <p className="text-xs text-slate-400 mt-2 animate-fadeIn">Your achieved level since sign up</p>
            )}
          </CardContent>
        </Card>

        <Card
          className="cursor-pointer transition-all hover:scale-105 hover:shadow-lg hover:shadow-accent-purple-500/20"
          onMouseEnter={() => setHoveredStat('xp')}
          onMouseLeave={() => setHoveredStat(null)}
        >
          <CardContent className="py-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-medium text-slate-400">Total XP</p>
                <p className="text-2xl font-bold text-accent-purple-500">{xp}</p>
              </div>
              <div className="w-10 h-10 bg-accent-purple-500/20 rounded-lg flex items-center justify-center">
                <Trophy className="h-5 w-5 text-accent-purple-500" />
              </div>
            </div>
            {hoveredStat === 'xp' && (
              <p className="text-xs text-slate-400 mt-2 animate-fadeIn">Total XP earned since sign up</p>
            )}
          </CardContent>
        </Card>

        <Card
          className="cursor-pointer transition-all hover:scale-105 hover:shadow-lg hover:shadow-accent-orange-500/20"
          onMouseEnter={() => setHoveredStat('streak')}
          onMouseLeave={() => setHoveredStat(null)}
        >
          <CardContent className="py-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-medium text-slate-400">Streak</p>
                <p className="text-2xl font-bold text-accent-orange-500">{streak}</p>
              </div>
              <div className="w-10 h-10 bg-accent-orange-500/20 rounded-lg flex items-center justify-center">
                <Flame className="h-5 w-5 text-accent-orange-500" />
              </div>
            </div>
            {hoveredStat === 'streak' && (
              <p className="text-xs text-slate-400 mt-2 animate-fadeIn">Your current daily practice streak</p>
            )}
          </CardContent>
        </Card>

        <Card
          className="cursor-pointer transition-all hover:scale-105 hover:shadow-lg hover:shadow-success-500/20"
          onMouseEnter={() => setHoveredStat('quizzes')}
          onMouseLeave={() => setHoveredStat(null)}
        >
          <CardContent className="py-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-medium text-slate-400">Quizzes</p>
                <p className="text-2xl font-bold text-success-500">{quizCount}</p>
              </div>
              <div className="w-10 h-10 bg-success-500/20 rounded-lg flex items-center justify-center">
                <Target className="h-5 w-5 text-success-500" />
              </div>
            </div>
            {hoveredStat === 'quizzes' && (
              <p className="text-xs text-slate-400 mt-2 animate-fadeIn">Total quizzes completed</p>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <Button className="w-full justify-start" onClick={() => navigate('/app/practice')}>
              <Target className="h-5 w-5 mr-2" />
              Start Exam Mode
            </Button>
            <Button className="w-full justify-start" onClick={() => navigate('/app/study')}>
              <BookOpen className="h-5 w-5 mr-2" />
              Study Mode
            </Button>
            <Button className="w-full justify-start" onClick={() => navigate('/app/achievements')}>
              <Trophy className="h-5 w-5 mr-2" />
              View Achievements
            </Button>
            <Button className="w-full justify-start" onClick={() => navigate('/app/leaderboard')}>
              <TrendingUp className="h-5 w-5 mr-2" />
              Check Leaderboard
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Status Message */}
      <Card variant="outlined">
        <CardContent className="py-8 text-center">
          <h3 className="text-xl font-semibold text-neutral-900 dark:text-slate-100 mb-2">
            Your Dashboard is Ready!
          </h3>
          <p className="text-neutral-600 dark:text-slate-400 mb-4">
            Start practicing to earn XP, level up, and unlock achievements!
          </p>
          <Badge variant="success">Backend Connected</Badge>
        </CardContent>
      </Card>
    </div>
  )
}
