import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { apiClient } from '@/services/api'

export interface User {
  id: number
  email: string
  username: string
  level: number
  xp: number
  streak: number
  avatar?: string
  isAdmin?: boolean
}

interface AuthState {
  user: User | null
  token: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  setAuth: (user: User, accessToken: string, refreshToken: string) => void
  updateUser: (user: Partial<User>) => void
  logout: () => void
  logoutAsync: () => Promise<void>
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      refreshToken: null,
      isAuthenticated: false,

      setAuth: (user, accessToken, refreshToken) => {
        localStorage.setItem('access_token', accessToken)
        localStorage.setItem('refresh_token', refreshToken)
        set({
          user,
          token: accessToken,
          refreshToken,
          isAuthenticated: true,
        })
      },

      updateUser: (updatedUser) => {
        set((state) => ({
          user: state.user ? { ...state.user, ...updatedUser } : null,
        }))
      },

      logout: () => {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        set({
          user: null,
          token: null,
          refreshToken: null,
          isAuthenticated: false,
        })
      },

      logoutAsync: async () => {
        const refreshToken = localStorage.getItem('refresh_token')

        // Call backend logout endpoint to revoke refresh token
        try {
          if (refreshToken) {
            await apiClient.post('/auth/logout', { refresh_token: refreshToken })
          }
        } catch (error) {
          // Even if API call fails, still logout locally
          console.error('Logout API call failed:', error)
        } finally {
          // Always clear local state
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          set({
            user: null,
            token: null,
            refreshToken: null,
            isAuthenticated: false,
          })
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)
