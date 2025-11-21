import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { apiClient, handleApiError } from '@/services/api'
import { useAuthStore } from '@/stores/authStore'
import { Target } from 'lucide-react'

const loginSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(1, 'Password is required'),
})

type LoginFormData = z.infer<typeof loginSchema>

export function LoginPage() {
  const navigate = useNavigate()
  const setAuth = useAuthStore((state) => state.setAuth)
  const [isLoading, setIsLoading] = useState(false)
  const [apiError, setApiError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  })

  const onSubmit = async (data: LoginFormData) => {
    setIsLoading(true)
    setApiError(null)

    try {
      const response = await apiClient.post('/auth/login', data)
      const apiUser = response.data.user

      // Backend may return basic user info on login (id, email, username)
      // We'll use safe defaults for profile fields until they're loaded from /auth/me
      const user = {
        id: apiUser.id,
        email: apiUser.email,
        username: apiUser.username,
        level: apiUser.level || 1,
        xp: apiUser.xp || 0,
        streak: apiUser.study_streak_current || 0,
        avatar: apiUser.avatar_url || undefined,
        isAdmin: apiUser.is_admin || false,
      }

      setAuth(user, response.data.access_token, response.data.refresh_token)
      navigate('/app/dashboard')
    } catch (error) {
      setApiError(handleApiError(error))
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-neutral-50 dark:bg-slate-800 flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="flex items-center justify-center space-x-2 mb-8">
          <Target className="h-10 w-10 text-primary-500" />
          <h1 className="text-3xl font-bold text-neutral-900 dark:text-slate-100">CompTIA Practice</h1>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Welcome back</CardTitle>
            <CardDescription>Sign in to your account to continue</CardDescription>
          </CardHeader>

          <CardContent>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              {apiError && (
                <div className="bg-error-50 border border-error-200 text-error-800 px-4 py-3 rounded-lg">
                  {apiError}
                </div>
              )}

              <div>
                <label htmlFor="email" className="block text-sm font-medium text-neutral-700 dark:text-slate-300 mb-1">
                  Email
                </label>
                <Input
                  id="email"
                  type="email"
                  placeholder="you@example.com"
                  error={errors.email?.message}
                  {...register('email')}
                />
              </div>

              <div>
                <label htmlFor="password" className="block text-sm font-medium text-neutral-700 dark:text-slate-300 mb-1">
                  Password
                </label>
                <Input
                  id="password"
                  type="password"
                  placeholder="••••••••"
                  error={errors.password?.message}
                  {...register('password')}
                />
              </div>

              <Button type="submit" className="w-full" isLoading={isLoading}>
                Log In
              </Button>

              <div className="text-center text-sm text-neutral-600 dark:text-slate-400">
                Don't have an account?{' '}
                <Link to="/signup" className="text-primary-500 hover:text-primary-600 font-medium">
                  Sign up
                </Link>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
