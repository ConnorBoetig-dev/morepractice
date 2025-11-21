import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Input } from '@/components/ui/Input'
import { apiClient } from '@/services/api'
import { useAuthStore } from '@/stores/authStore'
import { Navigate } from 'react-router-dom'
import { Users, FileQuestion, Trophy, Search, Shield, ShieldOff, UserCheck, UserX } from 'lucide-react'

type Tab = 'users' | 'questions' | 'achievements'

export function AdminPage() {
  const { user } = useAuthStore()
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState<Tab>('users')
  const [search, setSearch] = useState('')

  // Redirect if not admin
  if (!user?.isAdmin) {
    return <Navigate to="/app/dashboard" replace />
  }

  const tabs = [
    { id: 'users' as const, label: 'Users', icon: Users },
    { id: 'questions' as const, label: 'Questions', icon: FileQuestion },
    { id: 'achievements' as const, label: 'Achievements', icon: Trophy },
  ]

  return (
    <div className="p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-neutral-900 mb-2">Admin Panel</h1>
        <p className="text-neutral-600">Manage users, questions, and achievements</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-6">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center px-4 py-2 rounded-lg font-medium transition-colors ${
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

      {/* Search */}
      <div className="relative mb-6">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-neutral-400" />
        <Input
          placeholder={`Search ${activeTab}...`}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="pl-10"
        />
      </div>

      {activeTab === 'users' && <UsersTab search={search} />}
      {activeTab === 'questions' && <QuestionsTab search={search} />}
      {activeTab === 'achievements' && <AchievementsTab search={search} />}
    </div>
  )
}

function UsersTab({ search }: { search: string }) {
  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['admin-users'],
    queryFn: async () => {
      const response = await apiClient.get('/admin/users')
      return response.data
    },
  })

  const toggleAdminMutation = useMutation({
    mutationFn: async (userId: number) => {
      const response = await apiClient.post(`/admin/users/${userId}/toggle-admin`)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-users'] })
    },
  })

  const toggleActiveMutation = useMutation({
    mutationFn: async (userId: number) => {
      const response = await apiClient.post(`/admin/users/${userId}/toggle-active`)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-users'] })
    },
  })

  const users = (data?.users || []).filter(
    (u: any) =>
      u.username.toLowerCase().includes(search.toLowerCase()) ||
      u.email.toLowerCase().includes(search.toLowerCase())
  )

  if (isLoading) {
    return <div className="text-center py-8">Loading users...</div>
  }

  return (
    <div className="space-y-4">
      {users.map((u: any) => (
        <Card key={u.id}>
          <CardContent className="py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="w-10 h-10 rounded-full bg-neutral-200 flex items-center justify-center font-semibold">
                  {u.username.charAt(0).toUpperCase()}
                </div>
                <div>
                  <div className="flex items-center space-x-2">
                    <p className="font-medium text-neutral-900">{u.username}</p>
                    {u.is_admin && <Badge variant="primary">Admin</Badge>}
                    {!u.is_active && <Badge variant="error">Inactive</Badge>}
                  </div>
                  <p className="text-sm text-neutral-600">{u.email}</p>
                </div>
              </div>
              <div className="flex gap-2">
                <Button
                  size="sm"
                  variant={u.is_admin ? 'danger' : 'secondary'}
                  onClick={() => toggleAdminMutation.mutate(u.id)}
                >
                  {u.is_admin ? <ShieldOff className="h-4 w-4" /> : <Shield className="h-4 w-4" />}
                </Button>
                <Button
                  size="sm"
                  variant={u.is_active ? 'danger' : 'secondary'}
                  onClick={() => toggleActiveMutation.mutate(u.id)}
                >
                  {u.is_active ? <UserX className="h-4 w-4" /> : <UserCheck className="h-4 w-4" />}
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
      {users.length === 0 && (
        <Card>
          <CardContent className="py-8 text-center text-neutral-600">No users found</CardContent>
        </Card>
      )}
    </div>
  )
}

function QuestionsTab({ search }: { search: string }) {
  const { data, isLoading } = useQuery({
    queryKey: ['admin-questions'],
    queryFn: async () => {
      const response = await apiClient.get('/admin/questions')
      return response.data
    },
  })

  const questions = (data?.questions || []).filter(
    (q: any) =>
      q.question_text.toLowerCase().includes(search.toLowerCase()) ||
      q.domain.toLowerCase().includes(search.toLowerCase())
  )

  if (isLoading) {
    return <div className="text-center py-8">Loading questions...</div>
  }

  return (
    <div className="space-y-4">
      {questions.slice(0, 20).map((q: any) => (
        <Card key={q.id}>
          <CardContent className="py-4">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex gap-2 mb-2">
                  <Badge variant="primary">{q.exam_type.toUpperCase()}</Badge>
                  <Badge variant="neutral">{q.domain}</Badge>
                </div>
                <p className="text-neutral-900 line-clamp-2">{q.question_text}</p>
              </div>
              <Badge variant="success">Answer: {q.correct_answer}</Badge>
            </div>
          </CardContent>
        </Card>
      ))}
      {questions.length === 0 && (
        <Card>
          <CardContent className="py-8 text-center text-neutral-600">No questions found</CardContent>
        </Card>
      )}
      {questions.length > 20 && (
        <p className="text-center text-neutral-600">Showing first 20 of {questions.length} questions</p>
      )}
    </div>
  )
}

function AchievementsTab({ search }: { search: string }) {
  const { data, isLoading } = useQuery({
    queryKey: ['admin-achievements'],
    queryFn: async () => {
      const response = await apiClient.get('/achievements')
      return response.data
    },
  })

  const achievements = (data?.achievements || []).filter((a: any) =>
    a.name.toLowerCase().includes(search.toLowerCase())
  )

  if (isLoading) {
    return <div className="text-center py-8">Loading achievements...</div>
  }

  return (
    <div className="grid md:grid-cols-2 gap-4">
      {achievements.map((a: any) => (
        <Card key={a.id}>
          <CardContent className="py-4">
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 bg-accent-gold-100 rounded-lg flex items-center justify-center text-2xl">
                🏆
              </div>
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <p className="font-medium text-neutral-900">{a.name}</p>
                  <Badge variant="primary">+{a.xp_reward} XP</Badge>
                </div>
                <p className="text-sm text-neutral-600">{a.description}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
      {achievements.length === 0 && (
        <Card className="col-span-2">
          <CardContent className="py-8 text-center text-neutral-600">No achievements found</CardContent>
        </Card>
      )}
    </div>
  )
}
