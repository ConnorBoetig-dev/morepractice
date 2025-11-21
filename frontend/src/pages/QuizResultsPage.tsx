import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { apiClient } from '@/services/api'
import { Clock, CheckCircle, XCircle, RotateCcw, Home, Sparkles, X } from 'lucide-react'

interface QuestionReview {
  question_id: number
  question_text: string
  domain: string
  user_answer: string
  correct_answer: string
  is_correct: boolean
  options: Record<string, { text: string; explanation: string }>
}

interface QuizReviewData {
  quiz_attempt_id: number
  exam_type: string
  total_questions: number
  correct_answers: number
  score_percentage: number
  time_taken_seconds: number
  xp_earned: number
  questions: QuestionReview[]
}

export function QuizResultsPage() {
  const { examType, attemptId } = useParams()
  const navigate = useNavigate()

  const { data, isLoading } = useQuery({
    queryKey: ['quiz-review', attemptId],
    queryFn: async () => {
      if (!attemptId) return null
      const response = await apiClient.get(`/quiz/review/${attemptId}`)
      return response.data as QuizReviewData
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
    total_questions: 0,
    correct_answers: 0,
    time_taken_seconds: 0,
    xp_earned: 0,
    questions: [],
  }

  const percentage = result.total_questions > 0
    ? Math.round((result.correct_answers / result.total_questions) * 100)
    : 0

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}m ${secs}s`
  }

  const optionKeys = ['A', 'B', 'C', 'D'] as const

  return (
    <div className="p-6 max-w-3xl mx-auto">
      {/* Score Circle */}
      <Card className="mb-8 text-center relative">
        {/* Close Button */}
        <button
          onClick={() => navigate('/app/dashboard')}
          className="absolute top-4 right-4 p-2 rounded-lg text-neutral-400 hover:text-neutral-600 dark:hover:text-slate-300 hover:bg-neutral-100 dark:hover:bg-slate-700 transition-colors"
          title="Back to Dashboard"
        >
          <X className="h-5 w-5" />
        </button>

        <CardContent className="py-12">
          <div className="relative w-40 h-40 mx-auto mb-6">
            <svg className="w-full h-full transform -rotate-90">
              <circle
                cx="80"
                cy="80"
                r="70"
                className="stroke-neutral-200 dark:stroke-slate-600"
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
              <span className="text-4xl font-bold text-neutral-900 dark:text-slate-100">{percentage}%</span>
              <span className="text-sm text-neutral-600 dark:text-slate-400">Score</span>
            </div>
          </div>

          <h1 className="text-2xl font-bold text-neutral-900 dark:text-slate-100 mb-2">
            {percentage >= 70 ? 'Great Job!' : percentage >= 50 ? 'Good Effort!' : 'Keep Practicing!'}
          </h1>
          <p className="text-neutral-600 dark:text-slate-400">
            You answered {result.correct_answers} out of {result.total_questions} questions correctly
          </p>
        </CardContent>
      </Card>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 gap-4 mb-8">
        <Card>
          <CardContent className="pt-6 text-center">
            <CheckCircle className="h-8 w-8 text-success-500 mx-auto mb-2" />
            <p className="text-2xl font-bold text-neutral-900 dark:text-slate-100">{result.correct_answers}</p>
            <p className="text-sm text-neutral-600 dark:text-slate-400">Correct</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6 text-center">
            <XCircle className="h-8 w-8 text-error-500 mx-auto mb-2" />
            <p className="text-2xl font-bold text-neutral-900 dark:text-slate-100">
              {result.total_questions - result.correct_answers}
            </p>
            <p className="text-sm text-neutral-600 dark:text-slate-400">Incorrect</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6 text-center">
            <Clock className="h-8 w-8 text-primary-500 mx-auto mb-2" />
            <p className="text-2xl font-bold text-neutral-900 dark:text-slate-100">{formatTime(result.time_taken_seconds || 0)}</p>
            <p className="text-sm text-neutral-600 dark:text-slate-400">Time Taken</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6 text-center">
            <Sparkles className="h-8 w-8 text-accent-purple-500 mx-auto mb-2" />
            <p className="text-2xl font-bold text-accent-purple-500">+{result.xp_earned || 0}</p>
            <p className="text-sm text-neutral-600 dark:text-slate-400">XP Earned</p>
          </CardContent>
        </Card>
      </div>

      {/* Actions */}
      <div className="flex flex-col sm:flex-row gap-4 mb-8">
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

      {/* Question Review */}
      {result.questions && result.questions.length > 0 && (
        <div>
          <h2 className="text-xl font-bold text-neutral-900 dark:text-slate-100 mb-4">Question Review</h2>
          <div className="space-y-6">
            {result.questions.map((q, idx) => (
              <Card key={q.question_id} className={q.is_correct ? 'border-success-200' : 'border-error-200'}>
                <CardContent className="pt-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-2">
                      <Badge variant="neutral">Q{idx + 1}</Badge>
                      {q.domain && <Badge variant="neutral">{q.domain}</Badge>}
                    </div>
                    {q.is_correct ? (
                      <Badge variant="success">Correct</Badge>
                    ) : (
                      <Badge variant="error">Incorrect</Badge>
                    )}
                  </div>

                  <p className="text-neutral-900 dark:text-slate-100 font-medium mb-4">{q.question_text}</p>

                  <div className="space-y-2">
                    {optionKeys.map((key) => {
                      const option = q.options?.[key]
                      if (!option) return null

                      const isUserAnswer = q.user_answer === key
                      const isCorrectAnswer = q.correct_answer === key
                      const isWrong = isUserAnswer && !isCorrectAnswer

                      return (
                        <div
                          key={key}
                          className={`p-3 rounded-lg border-2 ${
                            isCorrectAnswer
                              ? 'border-success-500 bg-success-50 dark:bg-success-500/20'
                              : isWrong
                              ? 'border-error-500 bg-error-50 dark:bg-error-500/20'
                              : 'border-neutral-200 dark:border-slate-600'
                          }`}
                        >
                          <div className="flex items-start justify-between">
                            <div className="flex items-start">
                              <span className={`w-7 h-7 rounded-full flex items-center justify-center mr-3 text-sm font-medium flex-shrink-0 ${
                                isCorrectAnswer ? 'bg-success-500 text-white' :
                                isWrong ? 'bg-error-500 text-white' :
                                'bg-neutral-200 dark:bg-slate-600 text-neutral-700 dark:text-slate-300'
                              }`}>
                                {key}
                              </span>
                              <span className="text-neutral-900 dark:text-slate-100 text-sm">{option.text}</span>
                            </div>
                            {isCorrectAnswer && <CheckCircle className="h-5 w-5 text-success-500 flex-shrink-0" />}
                            {isWrong && <XCircle className="h-5 w-5 text-error-500 flex-shrink-0" />}
                          </div>
                          {(isCorrectAnswer || isWrong) && option.explanation && (
                            <p className={`mt-2 ml-10 text-sm ${isCorrectAnswer ? 'text-success-700 dark:text-success-400' : 'text-error-700 dark:text-error-400'}`}>
                              {option.explanation}
                            </p>
                          )}
                        </div>
                      )
                    })}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
