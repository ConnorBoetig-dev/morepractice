import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Input } from '@/components/ui/Input'
import { apiClient } from '@/services/api'
import { Bookmark, Trash2, Edit2, X, Check, Search } from 'lucide-react'

interface QuestionOption {
  text: string
  explanation: string
}

interface BookmarkedQuestion {
  id: number
  question_id: number
  notes: string | null
  created_at: string
  question: {
    id: number
    question_id: string
    question_text: string
    exam_type: string
    domain: string
    correct_answer: string
    options: {
      A: QuestionOption
      B: QuestionOption
      C: QuestionOption
      D: QuestionOption
    }
  }
}

export function BookmarksPage() {
  const queryClient = useQueryClient()
  const [search, setSearch] = useState('')
  const [editingId, setEditingId] = useState<number | null>(null)
  const [editNote, setEditNote] = useState('')

  const { data, isLoading } = useQuery({
    queryKey: ['bookmarks'],
    queryFn: async () => {
      const response = await apiClient.get('/bookmarks')
      return response.data
    },
  })

  const deleteMutation = useMutation({
    mutationFn: async (questionId: number) => {
      await apiClient.delete(`/bookmarks/questions/${questionId}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bookmarks'] })
    },
  })

  const updateNoteMutation = useMutation({
    mutationFn: async ({ questionId, note }: { questionId: number; note: string }) => {
      await apiClient.patch(`/bookmarks/questions/${questionId}`, { note })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bookmarks'] })
      setEditingId(null)
    },
  })

  const bookmarks: BookmarkedQuestion[] = data?.bookmarks || []

  const filteredBookmarks = bookmarks.filter(
    (b) =>
      b.question.question_text.toLowerCase().includes(search.toLowerCase()) ||
      b.question.domain.toLowerCase().includes(search.toLowerCase()) ||
      b.notes?.toLowerCase().includes(search.toLowerCase())
  )

  const handleStartEdit = (bookmark: BookmarkedQuestion) => {
    setEditingId(bookmark.question_id)
    setEditNote(bookmark.notes || '')
  }

  const handleSaveNote = (questionId: number) => {
    updateNoteMutation.mutate({ questionId, note: editNote })
  }

  return (
    <div className="p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-neutral-900 dark:text-slate-100 mb-2">Bookmarks</h1>
        <p className="text-neutral-600 dark:text-slate-400">Questions you've saved for later review</p>
      </div>

      {/* Search */}
      <div className="relative mb-6">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-neutral-400" />
        <Input
          placeholder="Search bookmarks..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="pl-10"
        />
      </div>

      {/* Stats */}
      <div className="flex gap-4 mb-6">
        <Badge variant="neutral">{bookmarks.length} bookmarks</Badge>
      </div>

      {isLoading ? (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <Card key={i} className="animate-pulse">
              <CardContent className="py-6">
                <div className="h-6 bg-neutral-200 dark:bg-slate-600 rounded w-3/4 mb-2" />
                <div className="h-4 bg-neutral-200 dark:bg-slate-600 rounded w-1/2" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : filteredBookmarks.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <Bookmark className="h-12 w-12 text-neutral-400 dark:text-slate-500 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-neutral-900 dark:text-slate-100 mb-2">
              {search ? 'No matching bookmarks' : 'No Bookmarks Yet'}
            </h3>
            <p className="text-neutral-600 dark:text-slate-400">
              {search
                ? 'Try a different search term'
                : 'Bookmark questions during quizzes to review them later'}
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {filteredBookmarks.map((bookmark) => (
            <Card key={bookmark.id}>
              <CardContent className="py-4">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex gap-2">
                    <Badge variant="primary">{bookmark.question.exam_type.toUpperCase()}</Badge>
                    <Badge variant="neutral">{bookmark.question.domain}</Badge>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleStartEdit(bookmark)}
                      className="p-2 text-neutral-400 hover:text-primary-500 transition-colors"
                    >
                      <Edit2 className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => deleteMutation.mutate(bookmark.question_id)}
                      className="p-2 text-neutral-400 hover:text-error-500 transition-colors"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>

                <p className="text-neutral-900 dark:text-slate-100 mb-4">{bookmark.question.question_text}</p>

                {/* Options with correct answer highlighted */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mb-4 text-sm">
                  {(['A', 'B', 'C', 'D'] as const).map((opt) => {
                    const option = bookmark.question.options?.[opt]
                    const isCorrect = bookmark.question.correct_answer === opt
                    if (!option) return null
                    return (
                      <div
                        key={opt}
                        className={`p-3 rounded-lg ${
                          isCorrect ? 'bg-success-500/20 text-success-400 border border-success-500/30' : 'bg-slate-600 text-slate-300'
                        }`}
                      >
                        <span className="font-bold mr-2">{opt}:</span>
                        <span>{option.text}</span>
                        {isCorrect && option.explanation && (
                          <p className="text-xs mt-1 text-success-400/80">{option.explanation}</p>
                        )}
                      </div>
                    )
                  })}
                </div>

                {/* Note */}
                {editingId === bookmark.question_id ? (
                  <div className="flex gap-2">
                    <Input
                      value={editNote}
                      onChange={(e) => setEditNote(e.target.value)}
                      placeholder="Add a note..."
                      className="flex-1"
                    />
                    <Button
                      size="sm"
                      onClick={() => handleSaveNote(bookmark.question_id)}
                      isLoading={updateNoteMutation.isPending}
                    >
                      <Check className="h-4 w-4" />
                    </Button>
                    <Button size="sm" variant="ghost" onClick={() => setEditingId(null)}>
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                ) : bookmark.notes ? (
                  <div className="bg-slate-600 p-3 rounded-lg">
                    <p className="text-sm text-slate-300">
                      <span className="font-medium">Note:</span> {bookmark.notes}
                    </p>
                  </div>
                ) : null}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
