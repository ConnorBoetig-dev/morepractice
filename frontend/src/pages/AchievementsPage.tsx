import { useQuery } from '@tanstack/react-query'
import { Card, CardContent } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { apiClient } from '@/services/api'
import { Trophy, Sparkles, CheckCircle, Lock } from 'lucide-react'

interface Achievement {
  id: number
  name: string
  description: string
  xp_reward: number
  icon: string
  tier: string
  criteria_type: string
  criteria_value: number
}

interface EarnedAchievement {
  achievement_id: number
  earned_at: string
}

export function AchievementsPage() {
  // GET /achievements returns array directly
  const { data: allAchievements, isLoading: loadingAll } = useQuery({
    queryKey: ['achievements'],
    queryFn: async () => {
      const response = await apiClient.get('/achievements')
      // API returns { achievements: [...] } or direct array
      return response.data.achievements || response.data || []
    },
  })

  // GET /achievements/earned returns array directly
  const { data: earnedData, isLoading: loadingEarned } = useQuery({
    queryKey: ['achievements-earned'],
    queryFn: async () => {
      const response = await apiClient.get('/achievements/earned')
      // API returns { earned_achievements: [...] } or { achievements: [...] }
      return response.data.earned_achievements || response.data.achievements || response.data || []
    },
  })

  const isLoading = loadingAll || loadingEarned

  // Build set of earned achievement IDs
  const earnedIds = new Set(
    (earnedData || []).map((a: EarnedAchievement) => a.achievement_id || (a as any).id)
  )

  // Combine all achievements with earned status
  const achievements: (Achievement & { earned: boolean })[] = (allAchievements || []).map((a: Achievement) => ({
    ...a,
    earned: earnedIds.has(a.id),
  }))

  // Sort: earned first, then by tier
  const sortedAchievements = [...achievements].sort((a, b) => {
    if (a.earned !== b.earned) return a.earned ? -1 : 1
    return 0
  })

  const earnedCount = achievements.filter((a) => a.earned).length
  const totalXP = achievements.filter((a) => a.earned).reduce((sum, a) => sum + a.xp_reward, 0)

  const tierColors: Record<string, string> = {
    bronze: 'bg-amber-600',
    silver: 'bg-gray-400',
    gold: 'bg-yellow-500',
    platinum: 'bg-purple-500',
  }

  const tierBgColors: Record<string, string> = {
    bronze: 'bg-amber-100',
    silver: 'bg-gray-100',
    gold: 'bg-yellow-100',
    platinum: 'bg-purple-100',
  }

  return (
    <div className="p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-neutral-900 mb-2">Achievements</h1>
        <p className="text-neutral-600">Track your progress and earn rewards</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        <Card>
          <CardContent className="pt-6 text-center">
            <Trophy className="h-8 w-8 text-yellow-500 mx-auto mb-2" />
            <p className="text-2xl font-bold text-neutral-900">{earnedCount}/{achievements.length}</p>
            <p className="text-sm text-neutral-600">Earned</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6 text-center">
            <Sparkles className="h-8 w-8 text-purple-500 mx-auto mb-2" />
            <p className="text-2xl font-bold text-purple-600">{totalXP.toLocaleString()}</p>
            <p className="text-sm text-neutral-600">XP Earned</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6 text-center">
            <CheckCircle className="h-8 w-8 text-green-500 mx-auto mb-2" />
            <p className="text-2xl font-bold text-neutral-900">
              {achievements.length > 0 ? Math.round((earnedCount / achievements.length) * 100) : 0}%
            </p>
            <p className="text-sm text-neutral-600">Complete</p>
          </CardContent>
        </Card>
      </div>

      {/* Achievements Grid */}
      {isLoading ? (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <Card key={i} className="animate-pulse">
              <CardContent className="pt-6">
                <div className="h-14 w-14 bg-neutral-200 rounded-lg mb-4" />
                <div className="h-5 bg-neutral-200 rounded w-2/3 mb-2" />
                <div className="h-4 bg-neutral-200 rounded w-full" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {sortedAchievements.map((achievement) => (
            <Card
              key={achievement.id}
              className={`transition-all ${
                achievement.earned ? '' : 'opacity-50'
              }`}
            >
              <CardContent className="pt-6">
                <div className="flex items-start justify-between mb-4">
                  <div
                    className={`w-14 h-14 rounded-lg flex items-center justify-center text-2xl ${
                      achievement.earned
                        ? tierBgColors[achievement.tier] || 'bg-yellow-100'
                        : 'bg-neutral-200'
                    }`}
                  >
                    {achievement.earned ? (
                      achievement.icon || '🏆'
                    ) : (
                      <Lock className="h-6 w-6 text-neutral-400" />
                    )}
                  </div>
                  <div className="flex flex-col items-end gap-1">
                    <div className={`w-3 h-3 rounded-full ${
                      achievement.earned
                        ? tierColors[achievement.tier] || 'bg-yellow-500'
                        : 'bg-neutral-300'
                    }`} />
                    <Badge variant={achievement.earned ? 'primary' : 'neutral'}>
                      +{achievement.xp_reward} XP
                    </Badge>
                  </div>
                </div>
                <h3 className={`text-lg font-semibold mb-1 ${
                  achievement.earned ? 'text-neutral-900' : 'text-neutral-500'
                }`}>
                  {achievement.name}
                </h3>
                <p className={`text-sm ${
                  achievement.earned ? 'text-neutral-600' : 'text-neutral-400'
                }`}>
                  {achievement.description}
                </p>
                {achievement.earned && (
                  <div className="mt-3 flex items-center text-green-600 text-sm">
                    <CheckCircle className="h-4 w-4 mr-1" />
                    Unlocked
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {!isLoading && achievements.length === 0 && (
        <Card>
          <CardContent className="py-12 text-center">
            <Trophy className="h-12 w-12 text-neutral-400 mx-auto mb-4" />
            <p className="text-neutral-600">No achievements available</p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
