import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { apiClient } from '@/services/api'
import { useAuthStore } from '@/stores/authStore'
import { Check, Lock, User } from 'lucide-react'

interface Avatar {
  id: number
  name: string
  description: string
  image_url: string
  is_default?: boolean
  is_unlocked?: boolean
  is_selected?: boolean
  required_achievement_name?: string
}

export function AvatarsPage() {
  const queryClient = useQueryClient()
  const { updateUser } = useAuthStore()

  // GET /avatars/me returns array with unlock status
  const { data: avatars, isLoading } = useQuery({
    queryKey: ['avatars-me'],
    queryFn: async () => {
      const response = await apiClient.get('/avatars/me')
      // Returns array directly
      return response.data || []
    },
  })

  // GET /avatars/stats for collection progress
  const { data: stats } = useQuery({
    queryKey: ['avatars-stats'],
    queryFn: async () => {
      const response = await apiClient.get('/avatars/stats')
      return response.data
    },
  })

  const selectMutation = useMutation({
    mutationFn: async (avatarId: number) => {
      const response = await apiClient.post('/avatars/select', { avatar_id: avatarId })
      return response.data
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['avatars-me'] })
      queryClient.invalidateQueries({ queryKey: ['avatars-stats'] })
      if (data.avatar) {
        updateUser({ avatar: data.avatar.image_url })
      }
    },
  })

  const avatarList: Avatar[] = avatars || []
  const unlockedCount = avatarList.filter((a) => a.is_unlocked || a.is_default).length

  // Sort: selected first, then unlocked, then locked
  const sortedAvatars = [...avatarList].sort((a, b) => {
    if (a.is_selected) return -1
    if (b.is_selected) return 1
    const aUnlocked = a.is_unlocked || a.is_default
    const bUnlocked = b.is_unlocked || b.is_default
    if (aUnlocked !== bUnlocked) return aUnlocked ? -1 : 1
    return 0
  })

  return (
    <div className="p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-neutral-900 mb-2">Avatars</h1>
        <p className="text-neutral-600">
          Customize your profile ({unlockedCount}/{avatarList.length} unlocked)
        </p>
      </div>

      {/* Progress Bar */}
      {stats && (
        <Card className="mb-8">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-neutral-700">Collection Progress</span>
              <span className="text-sm text-neutral-600">{stats.completion_percentage?.toFixed(0)}%</span>
            </div>
            <div className="w-full bg-neutral-200 rounded-full h-2">
              <div
                className="bg-primary-500 h-2 rounded-full transition-all"
                style={{ width: `${stats.completion_percentage || 0}%` }}
              />
            </div>
          </CardContent>
        </Card>
      )}

      {isLoading ? (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
            <Card key={i} className="animate-pulse">
              <CardContent className="pt-6 text-center">
                <div className="w-20 h-20 bg-neutral-200 rounded-full mx-auto mb-4" />
                <div className="h-4 bg-neutral-200 rounded w-2/3 mx-auto mb-2" />
                <div className="h-3 bg-neutral-200 rounded w-full" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {sortedAvatars.map((avatar) => {
            const isUnlocked = avatar.is_unlocked || avatar.is_default

            return (
              <Card
                key={avatar.id}
                className={`transition-all ${
                  avatar.is_selected ? 'ring-2 ring-primary-500' : ''
                } ${!isUnlocked ? 'opacity-60' : ''}`}
              >
                <CardContent className="pt-6 text-center">
                  <div className="relative inline-block mb-4">
                    <div
                      className={`w-20 h-20 rounded-full mx-auto flex items-center justify-center overflow-hidden ${
                        isUnlocked ? 'bg-primary-100' : 'bg-neutral-100'
                      }`}
                    >
                      {isUnlocked ? (
                        avatar.image_url ? (
                          <img
                            src={avatar.image_url}
                            alt={avatar.name}
                            className="w-full h-full object-cover"
                            onError={(e) => {
                              (e.target as HTMLImageElement).style.display = 'none'
                            }}
                          />
                        ) : (
                          <User className="h-10 w-10 text-primary-500" />
                        )
                      ) : (
                        <Lock className="h-8 w-8 text-neutral-400" />
                      )}
                    </div>
                    {avatar.is_selected && (
                      <div className="absolute -bottom-1 -right-1 w-6 h-6 bg-primary-500 rounded-full flex items-center justify-center">
                        <Check className="h-4 w-4 text-white" />
                      </div>
                    )}
                  </div>

                  <h3 className="font-semibold text-neutral-900 mb-1">{avatar.name}</h3>
                  <p className="text-xs text-neutral-600 mb-3 line-clamp-2">{avatar.description}</p>

                  {isUnlocked ? (
                    avatar.is_selected ? (
                      <Badge variant="success">Selected</Badge>
                    ) : (
                      <Button
                        size="sm"
                        variant="secondary"
                        onClick={() => selectMutation.mutate(avatar.id)}
                        isLoading={selectMutation.isPending}
                      >
                        Select
                      </Button>
                    )
                  ) : (
                    <Badge variant="neutral" className="text-xs">
                      {avatar.required_achievement_name || 'Locked'}
                    </Badge>
                  )}
                </CardContent>
              </Card>
            )
          })}
        </div>
      )}

      {!isLoading && avatarList.length === 0 && (
        <Card>
          <CardContent className="py-12 text-center">
            <User className="h-12 w-12 text-neutral-400 mx-auto mb-4" />
            <p className="text-neutral-600">No avatars available</p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
