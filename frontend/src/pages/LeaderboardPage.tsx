import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Card, CardContent } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { apiClient } from '@/services/api'
import { useAuthStore } from '@/stores/authStore'
import { Trophy, Target, Percent, Flame, Medal } from 'lucide-react'

type LeaderboardType = 'xp' | 'quiz-count' | 'accuracy' | 'streak'

interface LeaderboardEntry {
  rank: number
  user_id: number
  username: string
  score: number
  level: number
  avatar_url?: string
  is_current_user?: boolean
}

export function LeaderboardPage() {
  const [activeTab, setActiveTab] = useState<LeaderboardType>('xp')
  const { user } = useAuthStore()

  const tabs = [
    { id: 'xp' as const, label: 'XP', icon: Trophy },
    { id: 'quiz-count' as const, label: 'Quizzes', icon: Target },
    { id: 'accuracy' as const, label: 'Accuracy', icon: Percent },
    { id: 'streak' as const, label: 'Streak', icon: Flame },
  ]

  const { data, isLoading } = useQuery({
    queryKey: ['leaderboard', activeTab],
    queryFn: async () => {
      const response = await apiClient.get(`/leaderboard/${activeTab}`)
      return response.data
    },
  })

  const entries: LeaderboardEntry[] = data?.entries || []
  const userRank = data?.current_user_entry

  const formatValue = (score: number | undefined, type: LeaderboardType) => {
    const val = score ?? 0
    if (type === 'accuracy') return `${val.toFixed(1)}%`
    if (type === 'streak') return `${val} days`
    return val.toLocaleString()
  }

  const getRankBadge = (rank: number) => {
    if (rank === 1) return <Medal className="h-5 w-5 text-yellow-500" />
    if (rank === 2) return <Medal className="h-5 w-5 text-gray-400" />
    if (rank === 3) return <Medal className="h-5 w-5 text-amber-600" />
    return <span className="text-neutral-500 font-medium">#{rank}</span>
  }

  return (
    <div className="p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-neutral-900 mb-2">Leaderboard</h1>
        <p className="text-neutral-600">See how you rank against other learners</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center px-4 py-2 rounded-lg font-medium whitespace-nowrap transition-colors ${
              activeTab === tab.id
                ? 'bg-primary-500 text-white'
                : 'bg-neutral-100 text-neutral-700 hover:bg-neutral-200'
            }`}
          >
            <tab.icon className="h-4 w-4 mr-2" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* User's Rank Card */}
      {userRank && (
        <Card className="mb-6 bg-primary-50 border-primary-200">
          <CardContent className="py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="w-10 h-10 rounded-full bg-primary-500 flex items-center justify-center text-white font-bold">
                  {user?.username?.charAt(0).toUpperCase()}
                </div>
                <div>
                  <p className="font-semibold text-neutral-900">Your Rank</p>
                  <p className="text-sm text-neutral-600">Keep practicing to climb higher!</p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-2xl font-bold text-primary-600">#{userRank.rank}</p>
                <p className="text-sm text-neutral-600">{formatValue(userRank.score, activeTab)}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Leaderboard */}
      {isLoading ? (
        <div className="space-y-3">
          {[1, 2, 3, 4, 5].map((i) => (
            <Card key={i} className="animate-pulse">
              <CardContent className="py-4">
                <div className="h-6 bg-neutral-200 rounded w-1/2" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : entries.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <Trophy className="h-12 w-12 text-neutral-400 mx-auto mb-4" />
            <p className="text-neutral-600">No data yet. Be the first on the leaderboard!</p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {entries.map((entry) => {
            const isCurrentUser = entry.is_current_user || entry.user_id === user?.id
            return (
              <Card
                key={entry.user_id}
                className={`transition-all ${isCurrentUser ? 'ring-2 ring-primary-500 bg-primary-50' : ''}`}
              >
                <CardContent className="py-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <div className="w-8 flex justify-center">{getRankBadge(entry.rank)}</div>
                      <div className="w-10 h-10 rounded-full bg-neutral-200 flex items-center justify-center font-semibold text-neutral-700">
                        {entry.username?.charAt(0).toUpperCase()}
                      </div>
                      <div>
                        <p className="font-medium text-neutral-900">
                          {entry.username}
                          {isCurrentUser && <Badge variant="primary" className="ml-2">You</Badge>}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-bold text-neutral-900">{formatValue(entry.score, activeTab)}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>
      )}
    </div>
  )
}
