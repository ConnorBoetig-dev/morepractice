import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { apiClient } from '@/services/api'
import { Trophy, Target, Flame, TrendingUp, Sparkles, Calendar, ArrowLeft, HelpCircle } from 'lucide-react'

export function PublicProfilePage() {
  const { userId } = useParams()
  const navigate = useNavigate()

  // Get public user profile - this endpoint returns all public stats
  const { data: profileData, isLoading, error } = useQuery({
    queryKey: ['public-profile', userId],
    queryFn: async () => {
      const response = await apiClient.get(`/auth/users/${userId}`)
      return response.data
    },
    enabled: !!userId,
  })

  if (isLoading) {
    return (
      <div className="p-6 flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500" />
      </div>
    )
  }

  if (error || !profileData) {
    return (
      <div className="p-6">
        <Card>
          <CardContent className="py-12 text-center">
            <p className="text-slate-400 mb-4">User not found</p>
            <Button onClick={() => navigate(-1)}>
              <ArrowLeft className="h-4 w-4 mr-2" /> Go Back
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  const user = profileData

  return (
    <div className="p-6 max-w-3xl mx-auto">
      {/* Back Button */}
      <Button variant="ghost" className="mb-4" onClick={() => navigate(-1)}>
        <ArrowLeft className="h-4 w-4 mr-2" /> Back
      </Button>

      {/* Profile Header */}
      <Card className="mb-8">
        <CardContent className="pt-6">
          <div className="flex flex-col md:flex-row items-center md:items-start gap-6">
            <div className="w-24 h-24 rounded-full bg-primary-900/50 flex items-center justify-center text-4xl font-bold text-primary-400">
              {user.avatar_url ? (
                <img src={user.avatar_url} alt={user.username} className="w-full h-full rounded-full object-cover" />
              ) : (
                user.username?.charAt(0).toUpperCase()
              )}
            </div>
            <div className="flex-1 text-center md:text-left">
              <h1 className="text-2xl font-bold text-slate-100 mb-1">{user.username}</h1>
              <p className="text-slate-400 text-sm mb-4">
                Member since {new Date(user.created_at).toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
              </p>
              <div className="flex flex-wrap justify-center md:justify-start gap-3">
                <Badge variant="primary" className="text-sm">
                  <TrendingUp className="h-4 w-4 mr-1" />
                  Level {user.level || 1}
                </Badge>
                <Badge className="bg-accent-purple-500/20 text-accent-purple-500 text-sm">
                  <Sparkles className="h-4 w-4 mr-1" />
                  {user.xp || 0} XP
                </Badge>
                <Badge className="bg-accent-orange-500/20 text-accent-orange-500 text-sm">
                  <Flame className="h-4 w-4 mr-1" />
                  {user.study_streak_current || 0} day streak
                </Badge>
              </div>
            </div>
          </div>

          {/* Bio */}
          {user.bio && (
            <div className="mt-6 pt-6 border-t border-slate-600">
              <p className="text-slate-300 text-sm italic break-words whitespace-pre-wrap">"{user.bio.slice(0, 100)}"</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <Card className="transition-all hover:scale-105 hover:shadow-lg hover:shadow-primary-500/20">
          <CardContent className="py-4 text-center">
            <Target className="h-6 w-6 text-primary-500 mx-auto mb-1" />
            <p className="text-xl font-bold text-slate-100">{user.total_exams_taken || 0}</p>
            <p className="text-xs text-slate-400">Quizzes</p>
          </CardContent>
        </Card>
        <Card className="transition-all hover:scale-105 hover:shadow-lg hover:shadow-success-500/20">
          <CardContent className="py-4 text-center">
            <HelpCircle className="h-6 w-6 text-success-500 mx-auto mb-1" />
            <p className="text-xl font-bold text-slate-100">{user.total_questions_answered || 0}</p>
            <p className="text-xs text-slate-400">Questions</p>
          </CardContent>
        </Card>
        <Card className="transition-all hover:scale-105 hover:shadow-lg hover:shadow-accent-orange-500/20">
          <CardContent className="py-4 text-center">
            <Flame className="h-6 w-6 text-accent-orange-500 mx-auto mb-1" />
            <p className="text-xl font-bold text-slate-100">{user.study_streak_current || 0}</p>
            <p className="text-xs text-slate-400">Current Streak</p>
          </CardContent>
        </Card>
        <Card className="transition-all hover:scale-105 hover:shadow-lg hover:shadow-accent-purple-500/20">
          <CardContent className="py-4 text-center">
            <Calendar className="h-6 w-6 text-accent-purple-500 mx-auto mb-1" />
            <p className="text-xl font-bold text-slate-100">{user.study_streak_longest || 0}</p>
            <p className="text-xs text-slate-400">Best Streak</p>
          </CardContent>
        </Card>
      </div>

      {/* Activity Summary */}
      <Card>
        <CardHeader>
          <CardTitle>Activity Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 bg-slate-600/50 rounded-lg text-center">
              <Trophy className="h-8 w-8 text-accent-gold-500 mx-auto mb-2" />
              <p className="text-2xl font-bold text-slate-100">{user.xp || 0}</p>
              <p className="text-xs text-slate-400">Total XP Earned</p>
            </div>
            <div className="p-4 bg-slate-600/50 rounded-lg text-center">
              <TrendingUp className="h-8 w-8 text-primary-500 mx-auto mb-2" />
              <p className="text-2xl font-bold text-slate-100">Level {user.level || 1}</p>
              <p className="text-xs text-slate-400">Current Level</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
