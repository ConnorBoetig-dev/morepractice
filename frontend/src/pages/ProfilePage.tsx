import { useState } from 'react'
import { useAuthStore } from '@/stores/authStore'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { apiClient } from '@/services/api'
import { Trophy, Target, Flame, TrendingUp, Sparkles, Calendar, Award, Edit2, Check, X } from 'lucide-react'

export function ProfilePage() {
  const queryClient = useQueryClient()
  const { user, updateUser } = useAuthStore()
  const [isEditingBio, setIsEditingBio] = useState(false)
  const [bioText, setBioText] = useState('')

  // Get user profile data (includes study_streak_longest)
  const { data: profileData } = useQuery({
    queryKey: ['user-profile'],
    queryFn: async () => {
      const response = await apiClient.get('/auth/me')
      return response.data
    },
  })

  const { data: statsData } = useQuery({
    queryKey: ['quiz-stats'],
    queryFn: async () => {
      const response = await apiClient.get('/quiz/stats')
      return response.data
    },
  })

  // Get all achievements
  const { data: allAchievements } = useQuery({
    queryKey: ['achievements'],
    queryFn: async () => {
      const response = await apiClient.get('/achievements')
      return response.data.achievements || response.data || []
    },
  })

  // Get earned achievements
  const { data: earnedData } = useQuery({
    queryKey: ['achievements-earned'],
    queryFn: async () => {
      const response = await apiClient.get('/achievements/earned')
      return response.data.earned_achievements || response.data.achievements || response.data || []
    },
  })

  const stats = statsData || {}

  // Build set of earned achievement IDs (same logic as AchievementsPage)
  const earnedIds = new Set(
    (earnedData || []).map((a: any) => a.achievement_id || a.id)
  )

  // Get earned achievements for display
  const earnedAchievements = (allAchievements || []).filter((a: any) => earnedIds.has(a.id))
  const totalEarnedAchievements = earnedIds.size
  const bestStreak = profileData?.study_streak_longest ?? 0
  const userBio = profileData?.bio || ''

  // Bio update mutation
  const bioMutation = useMutation({
    mutationFn: async (bio: string) => {
      const response = await apiClient.patch('/auth/profile', { bio })
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['user-profile'] })
      setIsEditingBio(false)
    },
  })

  const handleEditBio = () => {
    setBioText(userBio)
    setIsEditingBio(true)
  }

  const handleSaveBio = () => {
    bioMutation.mutate(bioText)
  }

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
            <div className="w-24 h-24 rounded-full bg-primary-100 dark:bg-primary-900/50 flex items-center justify-center text-4xl font-bold text-primary-600 dark:text-primary-400">
              {user.avatar || user.username.charAt(0).toUpperCase()}
            </div>
            <div className="flex-1 text-center md:text-left">
              <h1 className="text-2xl font-bold text-neutral-900 dark:text-slate-100 mb-1">{user.username}</h1>
              <p className="text-neutral-600 dark:text-slate-400 mb-4">{user.email}</p>
              <div className="flex flex-wrap justify-center md:justify-start gap-3">
                <Badge variant="primary" className="text-sm">
                  <TrendingUp className="h-4 w-4 mr-1" />
                  Level {user.level || 1}
                </Badge>
                <Badge className="bg-accent-purple-100 dark:bg-accent-purple-500/20 text-accent-purple-700 dark:text-accent-purple-500 text-sm">
                  <Sparkles className="h-4 w-4 mr-1" />
                  {user.xp || 0} XP
                </Badge>
                <Badge className="bg-accent-orange-100 dark:bg-accent-orange-500/20 text-accent-orange-700 dark:text-accent-orange-500 text-sm">
                  <Flame className="h-4 w-4 mr-1" />
                  {user.streak || 0} day streak
                </Badge>
              </div>
            </div>
          </div>

          {/* XP Progress */}
          <div className="mt-6">
            <div className="flex justify-between text-sm mb-2">
              <span className="text-neutral-600 dark:text-slate-400">Progress to Level {(user.level || 1) + 1}</span>
              <span className="text-neutral-900 dark:text-slate-100 font-medium">{currentXp} / 1000 XP</span>
            </div>
            <div className="w-full bg-neutral-200 dark:bg-slate-600 rounded-full h-3">
              <div
                className="bg-primary-500 h-3 rounded-full transition-all"
                style={{ width: `${xpProgress}%` }}
              />
            </div>
          </div>

          {/* Bio Section */}
          <div className="mt-6 pt-6 border-t border-slate-600">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-slate-300">Bio</span>
              {!isEditingBio && (
                <button
                  onClick={handleEditBio}
                  className="p-1 text-slate-400 hover:text-primary-500 transition-colors"
                >
                  <Edit2 className="h-4 w-4" />
                </button>
              )}
            </div>
            {isEditingBio ? (
              <div className="space-y-3">
                <textarea
                  value={bioText}
                  onChange={(e) => setBioText(e.target.value.slice(0, 100))}
                  placeholder="Tell others about yourself..."
                  className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-primary-500 resize-none"
                  rows={2}
                  maxLength={100}
                />
                <div className="flex items-center justify-between">
                  <span className="text-xs text-slate-400">{bioText.length}/100</span>
                  <div className="flex gap-2">
                    <Button size="sm" variant="ghost" onClick={() => setIsEditingBio(false)}>
                      <X className="h-4 w-4 mr-1" /> Cancel
                    </Button>
                    <Button size="sm" onClick={handleSaveBio} isLoading={bioMutation.isPending}>
                      <Check className="h-4 w-4 mr-1" /> Save
                    </Button>
                  </div>
                </div>
              </div>
            ) : (
              <p className="text-slate-400 text-sm break-words whitespace-pre-wrap">
                {userBio || 'No bio yet. Click the edit button to add one!'}
              </p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <Card>
          <CardContent className="pt-6 text-center">
            <Target className="h-8 w-8 text-primary-500 mx-auto mb-2" />
            <p className="text-2xl font-bold text-neutral-900 dark:text-slate-100">{stats.total_attempts || 0}</p>
            <p className="text-sm text-neutral-600 dark:text-slate-400">Total Quizzes</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6 text-center">
            <Award className="h-8 w-8 text-success-500 mx-auto mb-2" />
            <p className="text-2xl font-bold text-neutral-900 dark:text-slate-100">
              {stats.average_score ? `${Math.round(stats.average_score)}%` : '0%'}
            </p>
            <p className="text-sm text-neutral-600 dark:text-slate-400">Avg. Score</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6 text-center">
            <Trophy className="h-8 w-8 text-accent-gold-500 mx-auto mb-2" />
            <p className="text-2xl font-bold text-neutral-900 dark:text-slate-100">{totalEarnedAchievements}</p>
            <p className="text-sm text-neutral-600 dark:text-slate-400">Achievements</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6 text-center">
            <Calendar className="h-8 w-8 text-accent-purple-500 mx-auto mb-2" />
            <p className="text-2xl font-bold text-neutral-900 dark:text-slate-100">{bestStreak}</p>
            <p className="text-sm text-neutral-600 dark:text-slate-400">Best Streak</p>
          </CardContent>
        </Card>
      </div>

      {/* Recent Achievements */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Achievements</CardTitle>
        </CardHeader>
        <CardContent>
          {earnedAchievements.length === 0 ? (
            <p className="text-neutral-600 dark:text-slate-400 text-center py-6">
              No achievements yet. Start practicing to earn your first one!
            </p>
          ) : (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
              {earnedAchievements.slice(0, 6).map((achievement: any) => (
                <div
                  key={achievement.id}
                  className="flex items-center space-x-3 p-3 bg-accent-gold-50 dark:bg-accent-gold-500/10 rounded-lg"
                >
                  <div className="w-10 h-10 bg-accent-gold-100 dark:bg-accent-gold-500/20 rounded-lg flex items-center justify-center text-xl">
                    🏆
                  </div>
                  <div>
                    <p className="font-medium text-neutral-900 dark:text-slate-100">{achievement.name}</p>
                    <p className="text-xs text-neutral-600 dark:text-slate-400">+{achievement.xp_reward} XP</p>
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
