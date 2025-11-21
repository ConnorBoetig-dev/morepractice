import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/services/api'
import { useAuthStore } from '@/stores/authStore'
import { useEffect } from 'react'

/**
 * Hook to fetch fresh user profile data and sync it with the auth store.
 * Use this in components that display XP, streak, level to ensure consistency.
 */
export function useUserProfile() {
  const { user, updateUser, isAuthenticated } = useAuthStore()

  const query = useQuery({
    queryKey: ['user-profile'],
    queryFn: async () => {
      const response = await apiClient.get('/auth/me')
      return response.data
    },
    enabled: isAuthenticated,
    staleTime: 30000, // Consider fresh for 30 seconds
    refetchOnWindowFocus: true,
  })

  // Sync API data to auth store
  useEffect(() => {
    if (query.data && user) {
      const apiUser = query.data
      // Only update if values changed
      const updates: Partial<typeof user> = {}

      if (apiUser.xp !== user.xp) updates.xp = apiUser.xp
      if (apiUser.level !== user.level) updates.level = apiUser.level
      if (apiUser.study_streak_current !== user.streak) updates.streak = apiUser.study_streak_current
      if (apiUser.avatar_url !== user.avatar) updates.avatar = apiUser.avatar_url

      if (Object.keys(updates).length > 0) {
        updateUser(updates)
      }
    }
  }, [query.data, user, updateUser])

  return {
    ...query,
    // Mapped user data for convenience
    xp: query.data?.xp ?? user?.xp ?? 0,
    level: query.data?.level ?? user?.level ?? 1,
    streak: query.data?.study_streak_current ?? user?.streak ?? 0,
    avatar: query.data?.avatar_url ?? user?.avatar,
  }
}
