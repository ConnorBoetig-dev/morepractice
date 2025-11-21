import { useState, useEffect } from 'react'
import { useParams, useSearchParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation } from '@tanstack/react-query'
import { Card, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { apiClient } from '@/services/api'
import { Clock, ChevronLeft, ChevronRight, Flag, CheckCircle, X } from 'lucide-react'

interface QuestionOption {
  text: string
  explanation: string
}

interface Question {
  id: number
  question_id: string
  exam_type: string
  domain: string
  question_text: string
  correct_answer: string
  options: {
    A: QuestionOption
    B: QuestionOption
    C: QuestionOption
    D: QuestionOption
  }
}

interface AnswerSubmission {
  question_id: number
  user_answer: string
  correct_answer: string
  is_correct: boolean
}

export function QuizPage() {
  const { examType } = useParams()
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const questionCount = parseInt(searchParams.get('count') || '10')

  const [currentIndex, setCurrentIndex] = useState(0)
  const [answers, setAnswers] = useState<Record<number, string>>({})
  const [flagged, setFlagged] = useState<Set<number>>(new Set())
  const [timeElapsed, setTimeElapsed] = useState(0)

  // Fetch questions
  const { data: questionsData, isLoading } = useQuery({
    queryKey: ['quiz-questions', examType, questionCount],
    queryFn: async () => {
      const response = await apiClient.get(`/questions/quiz?exam_type=${examType}&count=${questionCount}`)
      return response.data
    },
  })

  const questions: Question[] = questionsData?.questions || []
  const currentQuestion = questions[currentIndex]

  // Timer
  useEffect(() => {
    const timer = setInterval(() => {
      setTimeElapsed((t) => t + 1)
    }, 1000)
    return () => clearInterval(timer)
  }, [])

  // Warn on browser close/navigate away
  useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      e.preventDefault()
      e.returnValue = ''
    }
    window.addEventListener('beforeunload', handleBeforeUnload)
    return () => window.removeEventListener('beforeunload', handleBeforeUnload)
  }, [])

  // Submit quiz mutation
  const submitMutation = useMutation({
    mutationFn: async (data: { exam_type: string; total_questions: number; answers: AnswerSubmission[]; time_taken_seconds: number }) => {
      const response = await apiClient.post('/quiz/submit', data)
      return response.data
    },
    onSuccess: (data) => {
      navigate(`/app/practice/${examType}/results/${data.quiz_attempt_id}`)
    },
  })

  const handleSelectAnswer = (answer: string) => {
    setAnswers({ ...answers, [currentQuestion.id]: answer })
  }

  const handleToggleFlag = () => {
    const newFlagged = new Set(flagged)
    if (newFlagged.has(currentQuestion.id)) {
      newFlagged.delete(currentQuestion.id)
    } else {
      newFlagged.add(currentQuestion.id)
    }
    setFlagged(newFlagged)
  }

  const handleSubmit = () => {
    // Build answers with correct_answer and is_correct from questions
    const answerList: AnswerSubmission[] = Object.entries(answers).map(([qId, userAnswer]) => {
      const question = questions.find(q => q.id === parseInt(qId))
      const correctAnswer = question?.correct_answer || ''
      return {
        question_id: parseInt(qId),
        user_answer: userAnswer,
        correct_answer: correctAnswer,
        is_correct: userAnswer === correctAnswer,
      }
    })
    submitMutation.mutate({
      exam_type: examType!,
      total_questions: questions.length,
      answers: answerList,
      time_taken_seconds: timeElapsed,
    })
  }

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const answeredCount = Object.keys(answers).length

  if (isLoading) {
    return (
      <div className="p-6 flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500" />
      </div>
    )
  }

  if (!currentQuestion) {
    return (
      <div className="p-6 text-center">
        <p className="text-neutral-600">No questions available for this exam type.</p>
        <Button className="mt-4" onClick={() => navigate('/app/practice')}>
          Back to Practice
        </Button>
      </div>
    )
  }

  const optionKeys = ['A', 'B', 'C', 'D'] as const

  return (
    <div className="p-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-4">
          <Badge variant="primary">{examType?.toUpperCase()}</Badge>
          <span className="text-neutral-600">
            Question {currentIndex + 1} of {questions.length}
          </span>
        </div>
        <div className="flex items-center space-x-4">
          <div className="flex items-center text-neutral-600">
            <Clock className="h-5 w-5 mr-2" />
            {formatTime(timeElapsed)}
          </div>
          <Badge variant={answeredCount === questions.length ? 'success' : 'neutral'}>
            {answeredCount}/{questions.length} answered
          </Badge>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => {
              if (confirm('Are you sure you want to exit? All progress will be lost and no XP will be earned.')) {
                navigate('/app/practice')
              }
            }}
            className="text-neutral-500 hover:text-error-600"
          >
            <X className="h-4 w-4 mr-1" />
            Exit
          </Button>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="w-full bg-neutral-200 rounded-full h-2 mb-8">
        <div
          className="bg-primary-500 h-2 rounded-full transition-all"
          style={{ width: `${((currentIndex + 1) / questions.length) * 100}%` }}
        />
      </div>

      {/* Question Card */}
      <Card className="mb-6">
        <CardContent className="pt-6">
          <div className="flex items-start justify-between mb-4">
            <Badge variant="neutral">{currentQuestion.domain}</Badge>
            <button
              onClick={handleToggleFlag}
              className={`p-2 rounded-lg transition-colors ${
                flagged.has(currentQuestion.id)
                  ? 'text-warning-500 bg-warning-50'
                  : 'text-neutral-400 hover:text-warning-500 hover:bg-warning-50'
              }`}
            >
              <Flag className="h-5 w-5" />
            </button>
          </div>

          <h2 className="text-lg font-medium text-neutral-900 mb-6">
            {currentQuestion.question_text}
          </h2>

          <div className="space-y-3">
            {optionKeys.map((optionKey) => {
              const option = currentQuestion.options[optionKey]
              if (!option) return null
              const isSelected = answers[currentQuestion.id] === optionKey

              return (
                <button
                  key={optionKey}
                  onClick={() => handleSelectAnswer(optionKey)}
                  className={`w-full text-left p-4 rounded-lg border-2 transition-all ${
                    isSelected
                      ? 'border-primary-500 bg-primary-50'
                      : 'border-neutral-200 hover:border-neutral-300 hover:bg-neutral-50'
                  }`}
                >
                  <div className="flex items-start">
                    <span
                      className={`w-8 h-8 rounded-full flex items-center justify-center mr-3 font-medium flex-shrink-0 ${
                        isSelected
                          ? 'bg-primary-500 text-white'
                          : 'bg-neutral-200 text-neutral-700'
                      }`}
                    >
                      {optionKey}
                    </span>
                    <span className="text-neutral-900 pt-1">{option.text}</span>
                  </div>
                </button>
              )
            })}
          </div>
        </CardContent>
      </Card>

      {/* Question Navigator */}
      <Card className="mb-6">
        <CardContent className="py-4">
          <div className="flex flex-wrap gap-2">
            {questions.map((q, idx) => (
              <button
                key={q.id}
                onClick={() => setCurrentIndex(idx)}
                className={`w-10 h-10 rounded-lg font-medium transition-colors ${
                  idx === currentIndex
                    ? 'bg-primary-500 text-white'
                    : answers[q.id]
                    ? 'bg-primary-100 text-primary-700'
                    : flagged.has(q.id)
                    ? 'bg-warning-100 text-warning-700'
                    : 'bg-neutral-100 text-neutral-700 hover:bg-neutral-200'
                }`}
              >
                {idx + 1}
              </button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Navigation */}
      <div className="flex items-center justify-between">
        <Button
          variant="secondary"
          onClick={() => setCurrentIndex(Math.max(0, currentIndex - 1))}
          disabled={currentIndex === 0}
        >
          <ChevronLeft className="h-5 w-5 mr-1" />
          Previous
        </Button>

        {currentIndex === questions.length - 1 ? (
          <Button
            onClick={handleSubmit}
            isLoading={submitMutation.isPending}
            disabled={answeredCount === 0}
          >
            <CheckCircle className="h-5 w-5 mr-2" />
            Submit Quiz
          </Button>
        ) : (
          <Button onClick={() => setCurrentIndex(currentIndex + 1)}>
            Next
            <ChevronRight className="h-5 w-5 ml-1" />
          </Button>
        )}
      </div>
    </div>
  )
}
