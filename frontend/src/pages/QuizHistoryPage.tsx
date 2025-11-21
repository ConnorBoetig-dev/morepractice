import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Card, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { apiClient } from '@/services/api'
import { ChevronLeft, Clock, Target, Calendar } from 'lucide-react'

interface QuizAttempt {
  id: number
  exam_type: string
  score: number
  total_questions: number
  correct_answers: number
  time_taken: number
  xp_earned: number
  created_at: string
}

export function QuizHistoryPage() {
  const navigate = useNavigate()

  const { data, isLoading } = useQuery({
    queryKey: ['quiz-history'],
    queryFn: async () => {
      const response = await apiClient.get('/quiz/history')
      return response.data
    },
  })

  const attempts: QuizAttempt[] = data?.attempts || []

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}m ${secs}s`
  }

  return (
    <div className="p-6">
      <div className="flex items-center mb-8">
        <Button variant="ghost" onClick={() => navigate('/app/practice')} className="mr-4">
          <ChevronLeft className="h-5 w-5" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold text-neutral-900">Quiz History</h1>
          <p className="text-neutral-600">View your past quiz attempts</p>
        </div>
      </div>

      {isLoading ? (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <Card key={i} className="animate-pulse">
              <CardContent className="py-6">
                <div className="h-6 bg-neutral-200 rounded w-1/3 mb-2" />
                <div className="h-4 bg-neutral-200 rounded w-1/2" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : attempts.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <Target className="h-12 w-12 text-neutral-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-neutral-900 mb-2">No Quiz History</h3>
            <p className="text-neutral-600 mb-4">You haven't taken any quizzes yet.</p>
            <Button onClick={() => navigate('/app/practice')}>Start Practicing</Button>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {attempts.map((attempt) => {
            const percentage = Math.round((attempt.correct_answers / attempt.total_questions) * 100)
            return (
              <Card
                key={attempt.id}
                className="hover:shadow-md transition-shadow cursor-pointer"
                onClick={() => navigate(`/app/practice/${attempt.exam_type}/results/${attempt.id}`)}
              >
                <CardContent className="py-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <div
                        className={`w-14 h-14 rounded-lg flex items-center justify-center font-bold text-xl ${
                          percentage >= 70
                            ? 'bg-success-100 text-success-600'
                            : percentage >= 50
                            ? 'bg-warning-100 text-warning-600'
                            : 'bg-error-100 text-error-600'
                        }`}
                      >
                        {percentage}%
                      </div>
                      <div>
                        <div className="flex items-center space-x-2 mb-1">
                          <h3 className="font-semibold text-neutral-900">
                            {attempt.exam_type.toUpperCase()}
                          </h3>
                          <Badge variant="neutral">
                            {attempt.correct_answers}/{attempt.total_questions}
                          </Badge>
                        </div>
                        <div className="flex items-center text-sm text-neutral-600 space-x-4">
                          <span className="flex items-center">
                            <Calendar className="h-4 w-4 mr-1" />
                            {formatDate(attempt.created_at)}
                          </span>
                          <span className="flex items-center">
                            <Clock className="h-4 w-4 mr-1" />
                            {formatTime(attempt.time_taken)}
                          </span>
                        </div>
                      </div>
                    </div>
                    <Badge variant="primary">+{attempt.xp_earned} XP</Badge>
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
