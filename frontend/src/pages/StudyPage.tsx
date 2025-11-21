import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { apiClient } from '@/services/api'
import { BookOpen, CheckCircle, XCircle, ArrowRight, Target, AlertCircle, X, Trophy, RotateCcw, Bookmark } from 'lucide-react'
import { AchievementUnlockModal } from '@/components/achievements/AchievementUnlockModal'
import { useAuthStore } from '@/stores/authStore'

const EXAM_DISPLAY_NAMES: Record<string, string> = {
  'a1101': 'A+ Core 1',
  'a1102': 'A+ Core 2',
  'network': 'Network+',
  'security': 'Security+',
}

const EXAM_SUBTITLES: Record<string, string> = {
  'a1101': '220-1101',
  'a1102': '220-1102',
  'network': 'N10-008',
  'security': 'SY0-701',
}

interface QuestionOption {
  text: string
  explanation: string
}

interface StudyQuestion {
  question_id: number
  question_text: string
  domain?: string
  correct_answer?: string
  options: {
    A: QuestionOption
    B: QuestionOption
    C: QuestionOption
    D: QuestionOption
  }
}

interface StudySession {
  session_id: number
  total_questions: number
  current_question: StudyQuestion
}

interface StudyResults {
  totalQuestions: number
  correctCount: number
  examType: string
}

interface Achievement {
  achievement_id: number
  name: string
  description: string
  icon: string
  xp_reward: number
}

export function StudyPage() {
  const queryClient = useQueryClient()
  const { updateUser } = useAuthStore()
  const [selectedExam, setSelectedExam] = useState<string | null>(null)
  const [questionCount, setQuestionCount] = useState<string>('')
  const [session, setSession] = useState<StudySession | null>(null)
  const [questionNumber, setQuestionNumber] = useState(1)
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null)
  const [feedback, setFeedback] = useState<{correct: boolean; correctAnswer: string; allOptions?: Record<string, {text: string; explanation: string}>} | null>(null)
  const [showActiveSessionPrompt, setShowActiveSessionPrompt] = useState(false)
  const [submittedQuestionId, setSubmittedQuestionId] = useState<number | null>(null)
  const [correctCount, setCorrectCount] = useState(0)
  const [studyResults, setStudyResults] = useState<StudyResults | null>(null)
  const [bookmarked, setBookmarked] = useState<Set<number>>(new Set())
  const [unlockedAchievements, setUnlockedAchievements] = useState<Achievement[]>([])
  const [showAchievementModal, setShowAchievementModal] = useState(false)

  // Check for active session on mount (only when no local session)
  const { data: activeSession } = useQuery({
    queryKey: ['active-study-session'],
    queryFn: async () => {
      try {
        const response = await apiClient.get('/study/active')
        return response.data
      } catch {
        return null
      }
    },
    enabled: !session, // Only fetch when we don't have a local session
    refetchOnWindowFocus: false, // Don't refetch while user is working
  })

  // If there's an active session, auto-resume it
  useEffect(() => {
    if (activeSession && activeSession.session_id && !session) {
      setSession(activeSession)
      setSelectedExam(activeSession.exam_type || null)
      // Set question number based on backend's current_index (0-based)
      setQuestionNumber((activeSession.current_index || 0) + 1)
    }
  }, [activeSession, session])

  // Warn on browser close/navigate away during active session
  useEffect(() => {
    if (!session) return
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      e.preventDefault()
      e.returnValue = ''
    }
    window.addEventListener('beforeunload', handleBeforeUnload)
    return () => window.removeEventListener('beforeunload', handleBeforeUnload)
  }, [session])

  const { data: examsData, isLoading } = useQuery({
    queryKey: ['exams'],
    queryFn: async () => {
      const response = await apiClient.get('/questions/exams')
      return response.data
    },
  })

  const exams: string[] = examsData?.exams || []

  const isValidCount = () => {
    const count = parseInt(questionCount)
    return count >= 1 && count <= 90
  }

  // Abandon session mutation
  const abandonMutation = useMutation({
    mutationFn: async () => {
      const response = await apiClient.delete('/study/abandon')
      return response.data
    },
    onSuccess: () => {
      // Clear cached data first to prevent useEffect from restoring
      queryClient.setQueryData(['active-study-session'], null)
      setSession(null)
      setShowActiveSessionPrompt(false)
      setQuestionNumber(1)
      setSelectedAnswer(null)
      setFeedback(null)
      setSubmittedQuestionId(null)
      queryClient.invalidateQueries({ queryKey: ['active-study-session'] })
    },
    onError: () => {
      // Even if abandon fails (404 = session already gone), clear UI state
      // Clear cached data first to prevent useEffect from restoring
      queryClient.setQueryData(['active-study-session'], null)
      setSession(null)
      setShowActiveSessionPrompt(false)
      setQuestionNumber(1)
      setSelectedAnswer(null)
      setFeedback(null)
      setSubmittedQuestionId(null)
      queryClient.invalidateQueries({ queryKey: ['active-study-session'] })
    },
  })

  // Start session mutation
  const startMutation = useMutation({
    mutationFn: async ({ examType, count }: { examType: string; count: number }) => {
      const response = await apiClient.post('/study/start', { exam_type: examType, count })
      return response.data
    },
    onSuccess: (data) => {
      setSession(data)
      setQuestionNumber(1)
      setFeedback(null)
      setSelectedAnswer(null)
      setCorrectCount(0)
      setStudyResults(null)
      queryClient.invalidateQueries({ queryKey: ['active-study-session'] })
    },
    onError: () => {
      // Show prompt to abandon existing session
      setShowActiveSessionPrompt(true)
    },
  })

  // Submit answer mutation
  const answerMutation = useMutation({
    mutationFn: async ({ answer, questionId, sessionId }: { answer: string; questionId: number; sessionId: number }) => {
      const response = await apiClient.post('/study/answer', {
        session_id: sessionId,
        question_id: questionId,
        user_answer: answer,
      })
      return response.data
    },
    onSuccess: (data) => {
      // Track correct answers
      if (data.is_correct) {
        setCorrectCount((c) => c + 1)
      }
      // Show feedback (even for last question)
      setFeedback({
        correct: data.is_correct,
        correctAnswer: data.correct_answer,
        allOptions: data.all_options,
      })
    },
    onError: (error: any) => {
      console.error('Answer submission failed:', error?.response?.status, error?.response?.data)
      // Reset submission tracking so user can retry if needed
      setSubmittedQuestionId(null)
      if (error?.response?.status === 400 || error?.response?.status === 404) {
        // Clear cached data first to prevent useEffect from restoring
        queryClient.setQueryData(['active-study-session'], null)
        setSession(null)
        setQuestionNumber(1)
        setSelectedAnswer(null)
        setFeedback(null)
        queryClient.invalidateQueries({ queryKey: ['active-study-session'] })
      }
    },
  })

  // Bookmark mutation
  const bookmarkMutation = useMutation({
    mutationFn: async (questionId: number) => {
      if (bookmarked.has(questionId)) {
        await apiClient.delete(`/bookmarks/questions/${questionId}`)
      } else {
        await apiClient.post(`/bookmarks/questions/${questionId}`, { notes: null })
      }
    },
    onSuccess: (_, questionId) => {
      const newBookmarked = new Set(bookmarked)
      if (newBookmarked.has(questionId)) {
        newBookmarked.delete(questionId)
      } else {
        newBookmarked.add(questionId)
      }
      setBookmarked(newBookmarked)
      queryClient.invalidateQueries({ queryKey: ['bookmarks'] })
    },
  })

  const handleToggleBookmark = () => {
    const questionId = session?.current_question?.question_id
    if (questionId) {
      bookmarkMutation.mutate(questionId)
    }
  }

  const handleStartSession = () => {
    const count = parseInt(questionCount) || 10
    if (selectedExam && count >= 1 && count <= 90) {
      startMutation.mutate({ examType: selectedExam, count })
    }
  }

  const handleSubmitAnswer = () => {
    const questionId = session?.current_question?.question_id
    const sessionId = session?.session_id
    // Guard: need answer, session, question_id, not pending, and not already submitted for this question
    if (selectedAnswer && questionId && sessionId && !answerMutation.isPending && submittedQuestionId !== questionId) {
      setSubmittedQuestionId(questionId)
      answerMutation.mutate({ answer: selectedAnswer, questionId, sessionId })
    }
  }

  const handleNextQuestion = () => {
    const data = answerMutation.data

    console.log('=== STUDY SESSION COMPLETION ===')
    console.log('Full response:', data)
    console.log('Session completed?', data?.session_completed)
    console.log('Has next question?', !!data?.next_question)
    console.log('================================')

    // Check both session_completed flag AND next_question to determine if done
    if (data?.session_completed || !data?.next_question) {
      console.log('📚 Study session ending...')

      // Update XP if provided
      if (data?.total_xp !== undefined && data?.current_level !== undefined) {
        console.log('Updating XP:', data.total_xp, 'Level:', data.current_level)
        updateUser({
          xp: data.total_xp,
          level: data.current_level
        })
      }

      // Invalidate queries for live updates
      queryClient.invalidateQueries({ queryKey: ['user-profile'] })
      queryClient.invalidateQueries({ queryKey: ['achievements-earned'] })
      queryClient.invalidateQueries({ queryKey: ['achievements'] })

      // Check for achievements (they're nested in completion object)
      console.log('Checking for achievements...')
      console.log('Full completion data:', data?.completion)
      console.log('Achievements in response:', data?.completion?.achievements_unlocked)

      const achievements = data?.completion?.achievements_unlocked || []
      if (achievements.length > 0) {
        console.log('🎉 STUDY ACHIEVEMENTS DETECTED! Setting modal state...')
        console.log('Achievements to show:', achievements)
        setUnlockedAchievements(achievements)
        setShowAchievementModal(true)
        console.log('Study modal state set to TRUE')
      } else {
        console.log('⚠️ No study achievements unlocked')
      }

      // Session complete - show results
      setStudyResults({
        totalQuestions: session?.total_questions || questionNumber,
        correctCount: correctCount,
        examType: selectedExam || '',
      })
      // Clear cached data to prevent useEffect from restoring
      queryClient.setQueryData(['active-study-session'], null)
      setSession(null)
      queryClient.invalidateQueries({ queryKey: ['active-study-session'] })
    } else {
      // More questions remain
      setSession((prev) => prev ? {
        ...prev,
        current_question: data.next_question,
      } : null)
      setQuestionNumber((n) => n + 1)
    }
    setSelectedAnswer(null)
    setFeedback(null)
    setSubmittedQuestionId(null)
  }

  // Active study session view
  if (session && session.current_question) {
    const q = session.current_question
    const optionKeys = ['A', 'B', 'C', 'D'] as const

    return (
      <>
        <div className="p-6 max-w-3xl mx-auto">
          <div className="flex items-center justify-between mb-6">
            <Badge variant="primary">{EXAM_DISPLAY_NAMES[selectedExam!] || selectedExam?.toUpperCase()}</Badge>
            <div className="flex items-center gap-4">
              <span className="text-neutral-600 dark:text-slate-400">
                Question {questionNumber} of {session.total_questions}
              </span>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => {
                  if (confirm('Are you sure you want to exit? Your progress will be lost.')) {
                    // Try to abandon on backend, but always clear local state
                    abandonMutation.mutate()
                  }
                }}
                disabled={abandonMutation.isPending}
                className="text-neutral-500 hover:text-error-600"
              >
                <X className="h-4 w-4 mr-1" />
                Exit
              </Button>
            </div>
          </div>

          {/* Progress */}
          <div className="w-full bg-neutral-200 dark:bg-slate-600 rounded-full h-2 mb-8">
            <div
              className="bg-primary-500 h-2 rounded-full transition-all"
              style={{ width: `${(questionNumber / session.total_questions) * 100}%` }}
            />
          </div>

          <Card className="mb-6">
            <CardContent className="pt-6">
              <div className="flex items-start justify-between mb-4">
                {q.domain && <Badge variant="neutral">{q.domain}</Badge>}
                <button
                  onClick={handleToggleBookmark}
                  disabled={bookmarkMutation.isPending}
                  className={`p-2 rounded-lg transition-colors ${
                    bookmarked.has(q.question_id)
                      ? 'text-yellow-500 bg-yellow-500/20'
                      : 'text-slate-400 hover:text-yellow-500 hover:bg-yellow-500/20'
                  }`}
                  title={bookmarked.has(q.question_id) ? 'Remove bookmark' : 'Bookmark question'}
                >
                  <Bookmark className={`h-5 w-5 ${bookmarked.has(q.question_id) ? 'fill-current' : ''}`} />
                </button>
              </div>
              <h2 className="text-lg font-medium text-neutral-900 dark:text-slate-100 mb-6">{q.question_text}</h2>

              <div className="space-y-3">
                {optionKeys.map((optKey) => {
                  const option = q.options?.[optKey]
                  if (!option) return null

                  const isSelected = selectedAnswer === optKey
                  const showResult = feedback !== null
                  const isCorrect = showResult && feedback.correctAnswer === optKey
                  const isWrong = showResult && isSelected && !isCorrect

                  const explanation = showResult ? feedback.allOptions?.[optKey]?.explanation : null

                  return (
                    <div key={optKey} className="space-y-2">
                      <button
                        onClick={() => !feedback && setSelectedAnswer(optKey)}
                        disabled={!!feedback}
                        className={`w-full text-left p-4 rounded-lg border-2 transition-all ${
                          isCorrect
                            ? 'border-success-500 bg-success-50 dark:bg-success-500/20'
                            : isWrong
                            ? 'border-error-500 bg-error-50 dark:bg-error-500/20'
                            : isSelected
                            ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/30'
                            : 'border-neutral-200 dark:border-slate-600 hover:border-neutral-300 dark:hover:border-slate-500'
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-start">
                            <span className={`w-8 h-8 rounded-full flex items-center justify-center mr-3 font-medium flex-shrink-0 ${
                              isCorrect ? 'bg-success-500 text-white' :
                              isWrong ? 'bg-error-500 text-white' :
                              isSelected ? 'bg-primary-500 text-white' :
                              'bg-neutral-200 dark:bg-slate-600 text-neutral-700 dark:text-slate-300'
                            }`}>
                              {optKey}
                            </span>
                            <span className="text-neutral-900 dark:text-slate-100 pt-1">{option.text}</span>
                          </div>
                          {isCorrect && <CheckCircle className="h-5 w-5 text-success-500 flex-shrink-0" />}
                          {isWrong && <XCircle className="h-5 w-5 text-error-500 flex-shrink-0" />}
                        </div>
                      </button>
                      {explanation && (
                        <p className={`ml-11 text-sm ${isCorrect ? 'text-success-700 dark:text-success-400' : 'text-neutral-600 dark:text-slate-400'}`}>
                          {explanation}
                        </p>
                      )}
                    </div>
                  )
                })}
              </div>
            </CardContent>
          </Card>

          {/* Actions */}
          <div className="flex justify-end">
            {!feedback ? (
              <Button onClick={handleSubmitAnswer} disabled={!selectedAnswer || answerMutation.isPending} isLoading={answerMutation.isPending}>
                Submit Answer
              </Button>
            ) : (
              <Button onClick={handleNextQuestion}>
                {answerMutation.data?.next_question ? 'Next Question' : 'Finish Exam'}
                <ArrowRight className="h-5 w-5 ml-2" />
              </Button>
            )}
          </div>
        </div>

        {/* Achievement Unlock Modal */}
        <AchievementUnlockModal
          open={showAchievementModal}
          onClose={() => setShowAchievementModal(false)}
          achievements={unlockedAchievements}
        />
      </>
    )
  }

  // Results screen
  if (studyResults) {
    const percentage = Math.round((studyResults.correctCount / studyResults.totalQuestions) * 100)
    const passed = percentage >= 70

    return (
      <>
        <div className="p-6 max-w-2xl mx-auto">
          <Card className="text-center">
            <CardContent className="pt-8 pb-8">
              <div className={`w-20 h-20 mx-auto mb-6 rounded-full flex items-center justify-center ${
                passed ? 'bg-success-100' : 'bg-error-100'
              }`}>
                <Trophy className={`h-10 w-10 ${passed ? 'text-success-500' : 'text-error-500'}`} />
              </div>

              <h1 className="text-3xl font-bold text-neutral-900 dark:text-slate-100 mb-2">
                {passed ? 'Great Job!' : 'Keep Practicing!'}
              </h1>
              <p className="text-neutral-600 dark:text-slate-400 mb-6">
                {EXAM_DISPLAY_NAMES[studyResults.examType] || studyResults.examType.toUpperCase()} Study Session Complete
              </p>

              <div className="text-6xl font-bold mb-2" style={{ color: passed ? '#22c55e' : '#ef4444' }}>
                {percentage}%
              </div>
              <p className="text-neutral-600 dark:text-slate-400 mb-8">
                {studyResults.correctCount} of {studyResults.totalQuestions} correct
              </p>

              <div className="flex gap-4 justify-center">
                <Button
                  onClick={() => {
                    setStudyResults(null)
                    setSelectedExam(null)
                    setQuestionCount('')
                    setQuestionNumber(1)
                    setCorrectCount(0)
                  }}
                  variant="secondary"
                >
                  <RotateCcw className="h-4 w-4 mr-2" />
                  New Session
                </Button>
                <Button
                  onClick={() => {
                    const examType = studyResults.examType
                    const count = studyResults.totalQuestions
                    setStudyResults(null)
                    setQuestionCount(count.toString())
                    setQuestionNumber(1)
                    setCorrectCount(0)
                    startMutation.mutate({ examType, count })
                  }}
                >
                  Try Again
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Achievement Unlock Modal */}
        <AchievementUnlockModal
          open={showAchievementModal}
          onClose={() => setShowAchievementModal(false)}
          achievements={unlockedAchievements}
        />
      </>
    )
  }

  // Exam selection screen - same design as PracticePage
  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-neutral-900 dark:text-slate-100 mb-2">Study Mode</h1>
        <p className="text-neutral-600 dark:text-slate-400">Learn at your own pace with immediate feedback</p>
      </div>

      {/* Step 1: Select Exam */}
      <div className="mb-8">
        <h2 className="text-lg font-semibold text-neutral-800 dark:text-slate-200 mb-4">
          {selectedExam ? '1. Exam Selected' : '1. Select an Exam'}
        </h2>

        {isLoading ? (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-32 bg-neutral-200 dark:bg-slate-700 rounded-xl animate-pulse" />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {exams.map((examType) => (
              <button
                key={examType}
                onClick={() => setSelectedExam(examType)}
                className={`p-6 rounded-xl border-2 transition-all text-center ${
                  selectedExam === examType
                    ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/30'
                    : 'border-neutral-200 dark:border-slate-600 bg-white dark:bg-slate-700 hover:border-neutral-300 dark:hover:border-slate-500 hover:bg-neutral-50 dark:hover:bg-slate-600'
                }`}
              >
                <Target className={`h-8 w-8 mx-auto mb-3 ${
                  selectedExam === examType ? 'text-primary-500' : 'text-neutral-400 dark:text-slate-400'
                }`} />
                <p className={`font-semibold ${
                  selectedExam === examType ? 'text-primary-700 dark:text-primary-400' : 'text-neutral-900 dark:text-slate-100'
                }`}>
                  {EXAM_DISPLAY_NAMES[examType] || examType.toUpperCase()}
                </p>
                <p className={`text-sm ${
                  selectedExam === examType ? 'text-primary-600 dark:text-primary-400' : 'text-neutral-500 dark:text-slate-400'
                }`}>
                  {EXAM_SUBTITLES[examType] || 'CompTIA'}
                </p>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Step 2: Question Count */}
      {selectedExam && (
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>2. Number of Questions</CardTitle>
            <CardDescription>Enter a number between 1 and 90</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-4">
              <input
                type="number"
                min={1}
                max={90}
                value={questionCount}
                onChange={(e) => setQuestionCount(e.target.value)}
                placeholder="10"
                className="w-32 px-4 py-3 border-2 border-neutral-200 dark:border-slate-600 bg-white dark:bg-slate-700 text-neutral-900 dark:text-slate-100 rounded-lg text-center text-lg font-medium focus:border-primary-500 focus:outline-none"
              />
              <span className="text-neutral-600 dark:text-slate-400">No timer - learn at your pace</span>
            </div>

            {/* Quick select buttons */}
            <div className="flex flex-wrap gap-2 mt-4">
              {[10, 20, 30, 50].map((count) => (
                <button
                  key={count}
                  onClick={() => setQuestionCount(count.toString())}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    parseInt(questionCount) === count
                      ? 'bg-primary-500 text-white'
                      : 'bg-neutral-100 dark:bg-slate-600 text-neutral-700 dark:text-slate-200 hover:bg-neutral-200 dark:hover:bg-slate-500'
                  }`}
                >
                  {count}
                </button>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Start Button */}
      {selectedExam && (
        <Button
          onClick={handleStartSession}
          disabled={!isValidCount()}
          isLoading={startMutation.isPending}
          className="w-full"
          size="lg"
        >
          <BookOpen className="h-5 w-5 mr-2" />
          Start Study Session
        </Button>
      )}

      {/* Active Session Warning */}
      {showActiveSessionPrompt && (
        <Card className="mt-4 border-warning-200 bg-warning-50">
          <CardContent className="pt-6">
            <div className="flex items-start gap-3">
              <AlertCircle className="h-5 w-5 text-warning-500 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <p className="text-warning-700 font-medium mb-2">You have an active study session</p>
                <p className="text-warning-600 text-sm mb-4">
                  Would you like to resume it or start a new session? Starting a new session will abandon your current progress.
                </p>
                <div className="flex gap-3">
                  <Button
                    size="sm"
                    variant="secondary"
                    onClick={() => {
                      if (activeSession) {
                        setSession(activeSession)
                        setShowActiveSessionPrompt(false)
                      }
                    }}
                  >
                    Resume Session
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => abandonMutation.mutate()}
                    isLoading={abandonMutation.isPending}
                    className="text-error-600 hover:text-error-700"
                  >
                    Abandon & Start New
                  </Button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Achievement Unlock Modal */}
      <AchievementUnlockModal
        open={showAchievementModal}
        onClose={() => setShowAchievementModal(false)}
        achievements={unlockedAchievements}
      />
    </div>
  )
}
