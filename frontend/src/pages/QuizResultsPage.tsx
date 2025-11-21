import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { apiClient } from '@/services/api'
import { Trophy, Target, Clock, CheckCircle, XCircle, RotateCcw, Home, Sparkles } from 'lucide-react'

export function QuizResultsPage() {
  const { examType, attemptId } = useParams()
  const navigate = useNavigate()

  const { data, isLoading } = useQuery({
    queryKey: ['quiz-result', attemptId],
    queryFn: async () => {
      if (!attemptId) return null
      const response = await apiClient.get(`/quiz/history`)
      const attempts = response.data.attempts || []
      return attempts.find((a: any) => a.id === parseInt(attemptId)) || null
    },
    enabled: !!attemptId,
  })

  if (isLoading) {
    return (
      <div className="p-6 flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500" />
      </div>
    )
  }

  const result = data || {
    score: 0,
    total_questions: 0,
    correct_answers: 0,
    time_taken_seconds: 0,
    xp_earned: 0,
  }

  const percentage = result.total_questions > 0
    ? Math.round((result.correct_answers / result.total_questions) * 100)
    : 0

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}m ${secs}s`
  }

  return (
    <div className="p-6 max-w-2xl mx-auto">
      {/* Score Circle */}
      <Card className="mb-8 text-center">
        <CardContent className="py-12">
          <div className="relative w-40 h-40 mx-auto mb-6">
            <svg className="w-full h-full transform -rotate-90">
              <circle
                cx="80"
                cy="80"
                r="70"
                stroke="#e5e7eb"
                strokeWidth="12"
                fill="none"
              />
              <circle
                cx="80"
                cy="80"
                r="70"
                stroke={percentage >= 70 ? '#22c55e' : percentage >= 50 ? '#f59e0b' : '#ef4444'}
                strokeWidth="12"
                fill="none"
                strokeDasharray={`${(percentage / 100) * 440} 440`}
                strokeLinecap="round"
                className="transition-all duration-1000"
              />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className="text-4xl font-bold text-neutral-900">{percentage}%</span>
              <span className="text-sm text-neutral-600">Score</span>
            </div>
          </div>

          <h1 className="text-2xl font-bold text-neutral-900 mb-2">
            {percentage >= 70 ? 'Great Job!' : percentage >= 50 ? 'Good Effort!' : 'Keep Practicing!'}
          </h1>
          <p className="text-neutral-600">
            You answered {result.correct_answers} out of {result.total_questions} questions correctly
          </p>
        </CardContent>
      </Card>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 gap-4 mb-8">
        <Card>
          <CardContent className="pt-6 text-center">
            <CheckCircle className="h-8 w-8 text-success-500 mx-auto mb-2" />
            <p className="text-2xl font-bold text-neutral-900">{result.correct_answers}</p>
            <p className="text-sm text-neutral-600">Correct</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6 text-center">
            <XCircle className="h-8 w-8 text-error-500 mx-auto mb-2" />
            <p className="text-2xl font-bold text-neutral-900">
              {result.total_questions - result.correct_answers}
            </p>
            <p className="text-sm text-neutral-600">Incorrect</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6 text-center">
            <Clock className="h-8 w-8 text-primary-500 mx-auto mb-2" />
            <p className="text-2xl font-bold text-neutral-900">{formatTime(result.time_taken_seconds || 0)}</p>
            <p className="text-sm text-neutral-600">Time Taken</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6 text-center">
            <Sparkles className="h-8 w-8 text-accent-purple-500 mx-auto mb-2" />
            <p className="text-2xl font-bold text-accent-purple-500">+{result.xp_earned || 0}</p>
            <p className="text-sm text-neutral-600">XP Earned</p>
          </CardContent>
        </Card>
      </div>

      {/* Actions */}
      <div className="flex flex-col sm:flex-row gap-4">
        <Button
          variant="secondary"
          className="flex-1"
          onClick={() => navigate('/app/dashboard')}
        >
          <Home className="h-5 w-5 mr-2" />
          Back to Dashboard
        </Button>
        <Button
          className="flex-1"
          onClick={() => navigate('/app/practice')}
        >
          <RotateCcw className="h-5 w-5 mr-2" />
          Practice Again
        </Button>
      </div>
    </div>
  )
}
