import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { apiClient } from '@/services/api'
import { Target, Clock, ChevronRight, History } from 'lucide-react'

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

export function PracticePage() {
  const navigate = useNavigate()
  const [selectedExam, setSelectedExam] = useState<string | null>(null)
  const [questionCount, setQuestionCount] = useState<string>('')

  const { data: examsData, isLoading } = useQuery({
    queryKey: ['exams'],
    queryFn: async () => {
      const response = await apiClient.get('/questions/exams')
      return response.data
    },
  })

  const exams: string[] = examsData?.exams || []

  const handleStartQuiz = () => {
    const count = parseInt(questionCount) || 10
    if (selectedExam && count >= 1 && count <= 90) {
      navigate(`/app/practice/${selectedExam}/quiz?count=${count}`)
    }
  }

  const isValidCount = () => {
    const count = parseInt(questionCount)
    return count >= 1 && count <= 90
  }

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-neutral-900 dark:text-slate-100 mb-2">Practice Quiz</h1>
          <p className="text-neutral-600 dark:text-slate-400">Test your knowledge with timed practice</p>
        </div>
        <Button variant="secondary" onClick={() => navigate('/app/practice/history')}>
          <History className="h-4 w-4 mr-2" />
          History
        </Button>
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

      {/* Step 2: Question Count - Only show after exam is selected */}
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
              <div className="flex items-center text-neutral-600 dark:text-slate-400">
                <Clock className="h-5 w-5 mr-2" />
                <span>~{Math.ceil((parseInt(questionCount) || 10) * 1.5)} minutes</span>
              </div>
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
          onClick={handleStartQuiz}
          disabled={!isValidCount()}
          className="w-full"
          size="lg"
        >
          Start Quiz
          <ChevronRight className="h-5 w-5 ml-2" />
        </Button>
      )}
    </div>
  )
}
