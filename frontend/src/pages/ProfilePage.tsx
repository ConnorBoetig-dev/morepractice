import { useAuthStore } from '@/stores/authStore'
import { useQuery } from '@tanstack/react-query'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { apiClient } from '@/services/api'
import { Trophy, Target, Flame, TrendingUp, Sparkles, Calendar, Award } from 'lucide-react'

export function ProfilePage() {
  const { user } = useAuthStore()

  const { data: statsData } = useQuery({
    queryKey: ['quiz-stats'],
    queryFn: async () => {
      const response = await apiClient.get('/quiz/stats')
      return response.data
    },
  })

  const { data: achievementsData } = useQuery({
    queryKey: ['achievements-earned'],
    queryFn: async () => {
      const response = await apiClient.get('/achievements/earned')
      return response.data
    },
  })

  const stats = statsData || {}
  const achievements = achievementsData?.achievements || []

  if (!user) return null

  const xpToNextLevel = (user.level || 1) * 1000
  const currentXp = (user.xp || 0) % 1000
  const xpProgress = (currentXp / 1000) * 100

  return (
    <div className="p-6">
      {/* Profile Header */}
      <Card className="mb-8">
        <CardContent className="pt-6">
          <div className="flex flex-col md:flex-row items-center md:items-start gap-6">
            <div className="w-24 h-24 rounded-full bg-primary-100 flex items-center justify-center text-4xl font-bold text-primary-600">
              {user.avatar || user.username.charAt(0).toUpperCase()}
            </div>
            <div className="flex-1 text-center md:text-left">
              <h1 className="text-2xl font-bold text-neutral-900 mb-1">{user.username}</h1>
              <p className="text-neutral-600 mb-4">{user.email}</p>
              <div className="flex flex-wrap justify-center md:justify-start gap-3">
                <Badge variant="primary" className="text-sm">
                  <TrendingUp className="h-4 w-4 mr-1" />
                  Level {user.level || 1}
                </Badge>
                <Badge className="bg-accent-purple-100 text-accent-purple-700 text-sm">
                  <Sparkles className="h-4 w-4 mr-1" />
                  {user.xp || 0} XP
                </Badge>
                <Badge className="bg-accent-orange-100 text-accent-orange-700 text-sm">
                  <Flame className="h-4 w-4 mr-1" />
                  {user.streak || 0} day streak
                </Badge>
              </div>
            </div>
          </div>

          {/* XP Progress */}
          <div className="mt-6">
            <div className="flex justify-between text-sm mb-2">
              <span className="text-neutral-600">Progress to Level {(user.level || 1) + 1}</span>
              <span className="text-neutral-900 font-medium">{currentXp} / 1000 XP</span>
            </div>
            <div className="w-full bg-neutral-200 rounded-full h-3">
              <div
                className="bg-primary-500 h-3 rounded-full transition-all"
                style={{ width: `${xpProgress}%` }}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <Card>
          <CardContent className="pt-6 text-center">
            <Target className="h-8 w-8 text-primary-500 mx-auto mb-2" />
            <p className="text-2xl font-bold text-neutral-900">{stats.total_attempts || 0}</p>
            <p className="text-sm text-neutral-600">Total Quizzes</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6 text-center">
            <Award className="h-8 w-8 text-success-500 mx-auto mb-2" />
            <p className="text-2xl font-bold text-neutral-900">
              {stats.average_score ? `${Math.round(stats.average_score)}%` : '0%'}
            </p>
            <p className="text-sm text-neutral-600">Avg. Score</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6 text-center">
            <Trophy className="h-8 w-8 text-accent-gold-500 mx-auto mb-2" />
            <p className="text-2xl font-bold text-neutral-900">{achievements.length}</p>
            <p className="text-sm text-neutral-600">Achievements</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6 text-center">
            <Calendar className="h-8 w-8 text-accent-purple-500 mx-auto mb-2" />
            <p className="text-2xl font-bold text-neutral-900">{stats.best_streak || 0}</p>
            <p className="text-sm text-neutral-600">Best Streak</p>
          </CardContent>
        </Card>
      </div>

      {/* Recent Achievements */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Achievements</CardTitle>
        </CardHeader>
        <CardContent>
          {achievements.length === 0 ? (
            <p className="text-neutral-600 text-center py-6">
              No achievements yet. Start practicing to earn your first one!
            </p>
          ) : (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
              {achievements.slice(0, 6).map((achievement: any) => (
                <div
                  key={achievement.id}
                  className="flex items-center space-x-3 p-3 bg-accent-gold-50 rounded-lg"
                >
                  <div className="w-10 h-10 bg-accent-gold-100 rounded-lg flex items-center justify-center text-xl">
                    🏆
                  </div>
                  <div>
                    <p className="font-medium text-neutral-900">{achievement.name}</p>
                    <p className="text-xs text-neutral-600">+{achievement.xp_reward} XP</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
