import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Card, CardContent } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { apiClient } from '@/services/api'
import { useAuthStore } from '@/stores/authStore'
import { Trophy, Target, Percent, Flame, Crown, Award, TrendingUp } from 'lucide-react'

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
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState<LeaderboardType>('xp')
  const { user } = useAuthStore()

  const tabs = [
    { id: 'xp' as const, label: 'XP', icon: Trophy, color: 'text-accent-purple-500' },
    { id: 'quiz-count' as const, label: 'Quizzes', icon: Target, color: 'text-primary-500' },
    { id: 'accuracy' as const, label: 'Accuracy', icon: Percent, color: 'text-success-500' },
    { id: 'streak' as const, label: 'Streak', icon: Flame, color: 'text-accent-orange-500' },
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
  const activeTabConfig = tabs.find(t => t.id === activeTab)

  const formatValue = (score: number | undefined, type: LeaderboardType) => {
    const val = score ?? 0
    if (type === 'accuracy') return `${val.toFixed(1)}%`
    if (type === 'streak') return `${val} days`
    return val.toLocaleString()
  }

  const getRankDisplay = (rank: number) => {
    if (rank === 1) return { icon: <Crown className="h-6 w-6" />, bg: 'bg-gradient-to-br from-yellow-400 to-amber-500', text: 'text-white' }
    if (rank === 2) return { icon: <Award className="h-5 w-5" />, bg: 'bg-gradient-to-br from-gray-300 to-gray-400', text: 'text-white' }
    if (rank === 3) return { icon: <Award className="h-5 w-5" />, bg: 'bg-gradient-to-br from-amber-600 to-amber-700', text: 'text-white' }
    return { icon: <span className="text-sm font-bold">{rank}</span>, bg: 'bg-neutral-100 dark:bg-slate-600', text: 'text-neutral-600 dark:text-slate-300' }
  }

  // Split top 3 from rest
  const topThree = entries.slice(0, 3)
  const restOfLeaderboard = entries.slice(3)

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-100 mb-2">Leaderboard</h1>
        <p className="text-slate-400">Compete with other learners and climb the ranks</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-8 overflow-x-auto pb-2">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center px-5 py-2.5 rounded-xl font-medium whitespace-nowrap transition-all ${
              activeTab === tab.id
                ? 'bg-primary-500 text-white shadow-lg shadow-primary-500/25'
                : 'bg-slate-700 text-slate-200 hover:bg-slate-600 border border-slate-600'
            }`}
          >
            <tab.icon className={`h-4 w-4 mr-2 ${activeTab === tab.id ? 'text-white' : tab.color}`} />
            {tab.label}
          </button>
        ))}
      </div>

      {/* User's Rank Card */}
      {userRank && (
        <Card className="mb-8 bg-gradient-to-r from-primary-500 to-primary-600 border-0 text-white overflow-hidden relative">
          <div className="absolute right-0 top-0 w-32 h-32 bg-white/10 rounded-full -mr-16 -mt-16" />
          <div className="absolute right-8 bottom-0 w-20 h-20 bg-white/10 rounded-full -mb-10" />
          <CardContent className="py-6 relative">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="w-14 h-14 rounded-full bg-white/20 flex items-center justify-center text-2xl font-bold">
                  {user?.username?.charAt(0).toUpperCase()}
                </div>
                <div>
                  <p className="text-white/80 text-sm">Your Position</p>
                  <p className="text-2xl font-bold">#{userRank.rank}</p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-white/80 text-sm">{tabs.find(t => t.id === activeTab)?.label}</p>
                <p className="text-3xl font-bold">{formatValue(userRank.score, activeTab)}</p>
              </div>
            </div>
            <div className="mt-4 flex items-center gap-2 text-white/80 text-sm">
              <TrendingUp className="h-4 w-4" />
              <span>Keep practicing to climb the ranks!</span>
            </div>
          </CardContent>
        </Card>
      )}

      {isLoading ? (
        <div className="space-y-3">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="h-20 bg-slate-700 rounded-xl animate-pulse" />
          ))}
        </div>
      ) : entries.length === 0 ? (
        <Card className="border-dashed border-slate-600">
          <CardContent className="py-16 text-center">
            <Trophy className="h-16 w-16 text-slate-500 mx-auto mb-4" />
            <p className="text-xl font-medium text-slate-100 mb-2">No rankings yet</p>
            <p className="text-slate-400">Be the first to claim the top spot!</p>
          </CardContent>
        </Card>
      ) : (
        <>
          {/* Top 3 Podium */}
          {topThree.length > 0 && (
            <Card className="mb-8 p-6">
              <div className="grid grid-cols-3 gap-4 items-end">
                {/* 2nd Place */}
                <div className="flex flex-col items-center">
                  {topThree[1] && (
                    <>
                      <div className="relative mb-3">
                        <div className="w-16 h-16 rounded-full bg-gradient-to-br from-gray-300 to-gray-400 flex items-center justify-center text-2xl font-bold text-white shadow-lg">
                          {topThree[1].username?.charAt(0).toUpperCase()}
                        </div>
                        <div className="absolute -bottom-1 -right-1 w-7 h-7 rounded-full bg-gray-400 flex items-center justify-center text-white font-bold text-sm shadow border-2 border-slate-700">
                          2
                        </div>
                      </div>
                      <p
                        className="font-semibold text-slate-100 truncate max-w-full text-center cursor-pointer hover:text-primary-400 transition-colors"
                        onClick={() => navigate(`/app/users/${topThree[1].user_id}`)}
                      >{topThree[1].username}</p>
                      <p className={`text-sm font-medium ${activeTabConfig?.color}`}>{formatValue(topThree[1].score, activeTab)}</p>
                      <div className="w-full h-16 bg-gray-400/30 rounded-t-lg mt-3" />
                    </>
                  )}
                </div>

                {/* 1st Place */}
                <div className="flex flex-col items-center">
                  {topThree[0] && (
                    <>
                      <div className="relative mb-3">
                        <Crown className="h-8 w-8 text-yellow-400 mx-auto mb-1 drop-shadow-lg" />
                        <div className="w-20 h-20 rounded-full bg-gradient-to-br from-yellow-400 to-amber-500 flex items-center justify-center text-3xl font-bold text-white shadow-lg ring-4 ring-yellow-400/30">
                          {topThree[0].username?.charAt(0).toUpperCase()}
                        </div>
                        <div className="absolute -bottom-1 -right-1 w-8 h-8 rounded-full bg-yellow-500 flex items-center justify-center text-white font-bold text-sm shadow border-2 border-slate-700">
                          1
                        </div>
                      </div>
                      <p
                        className="font-bold text-slate-100 truncate max-w-full text-center cursor-pointer hover:text-primary-400 transition-colors"
                        onClick={() => navigate(`/app/users/${topThree[0].user_id}`)}
                      >{topThree[0].username}</p>
                      <p className={`text-sm font-bold ${activeTabConfig?.color}`}>{formatValue(topThree[0].score, activeTab)}</p>
                      <div className="w-full h-24 bg-yellow-500/30 rounded-t-lg mt-3" />
                    </>
                  )}
                </div>

                {/* 3rd Place */}
                <div className="flex flex-col items-center">
                  {topThree[2] && (
                    <>
                      <div className="relative mb-3">
                        <div className="w-14 h-14 rounded-full bg-gradient-to-br from-amber-600 to-amber-700 flex items-center justify-center text-xl font-bold text-white shadow-lg">
                          {topThree[2].username?.charAt(0).toUpperCase()}
                        </div>
                        <div className="absolute -bottom-1 -right-1 w-6 h-6 rounded-full bg-amber-600 flex items-center justify-center text-white font-bold text-xs shadow border-2 border-slate-700">
                          3
                        </div>
                      </div>
                      <p
                        className="font-semibold text-slate-100 truncate max-w-full text-center cursor-pointer hover:text-primary-400 transition-colors"
                        onClick={() => navigate(`/app/users/${topThree[2].user_id}`)}
                      >{topThree[2].username}</p>
                      <p className={`text-sm font-medium ${activeTabConfig?.color}`}>{formatValue(topThree[2].score, activeTab)}</p>
                      <div className="w-full h-10 bg-amber-600/30 rounded-t-lg mt-3" />
                    </>
                  )}
                </div>
              </div>
            </Card>
          )}

          {/* Rest of Leaderboard */}
          {restOfLeaderboard.length > 0 && (
            <Card>
              <CardContent className="p-0 divide-y divide-slate-600">
                {restOfLeaderboard.map((entry) => {
                  const isCurrentUser = entry.is_current_user || entry.user_id === user?.id
                  const rankDisplay = getRankDisplay(entry.rank)
                  return (
                    <div
                      key={entry.user_id}
                      className={`flex items-center justify-between p-4 transition-colors ${
                        isCurrentUser ? 'bg-primary-900/30' : 'hover:bg-slate-600'
                      }`}
                    >
                      <div className="flex items-center space-x-4">
                        <div className={`w-10 h-10 rounded-full ${rankDisplay.bg} ${rankDisplay.text} flex items-center justify-center font-semibold`}>
                          {rankDisplay.icon}
                        </div>
                        <div className="w-10 h-10 rounded-full bg-slate-500 flex items-center justify-center font-semibold text-slate-200">
                          {entry.username?.charAt(0).toUpperCase()}
                        </div>
                        <div>
                          <p className="font-medium text-slate-100">
                            <span
                              className="cursor-pointer hover:text-primary-400 transition-colors"
                              onClick={() => navigate(`/app/users/${entry.user_id}`)}
                            >
                              {entry.username}
                            </span>
                            {isCurrentUser && <Badge variant="primary" className="ml-2">You</Badge>}
                          </p>
                          {entry.level && <p className="text-xs text-slate-400">Level {entry.level}</p>}
                        </div>
                      </div>
                      <div className="text-right">
                        <p className={`font-bold ${activeTabConfig?.color}`}>{formatValue(entry.score, activeTab)}</p>
                      </div>
                    </div>
                  )
                })}
              </CardContent>
            </Card>
          )}
        </>
      )}
    </div>
  )
}
