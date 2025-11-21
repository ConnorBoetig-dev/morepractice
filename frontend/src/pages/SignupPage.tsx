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
import { Target, CheckCircle, XCircle, AlertCircle } from 'lucide-react'

const signupSchema = z.object({
  email: z.string().email('Invalid email address'),
  username: z
    .string()
    .min(3, 'Username must be at least 3 characters')
    .max(50, 'Username cannot exceed 50 characters')
    .regex(
      /^[a-zA-Z0-9_-]+$/,
      'Username can only contain letters, numbers, underscores, and hyphens (no spaces)'
    )
    .refine(
      (val) => !val.startsWith('_') && !val.startsWith('-') && !val.endsWith('_') && !val.endsWith('-'),
      'Username cannot start or end with special characters'
    )
    .refine(
      (val) => !['__', '--', '_-', '-_'].some(p => val.includes(p)),
      'Username cannot contain consecutive special characters'
    )
    .refine(
      (val) => !['admin', 'root', 'system', 'support', 'moderator', 'staff'].includes(val.toLowerCase()),
      'This username is reserved and cannot be used'
    ),
  password: z.string().min(12, 'Password must be at least 12 characters'),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ['confirmPassword'],
})

type SignupFormData = z.infer<typeof signupSchema>

// Validation item component for checklist
interface ValidationItemProps {
  label: string
  isValid: boolean
  isEmpty: boolean
}

function ValidationItem({ label, isValid, isEmpty }: ValidationItemProps) {
  return (
    <div className="flex items-center gap-2 text-xs">
      {isEmpty ? (
        <AlertCircle className="h-3.5 w-3.5 text-neutral-400 dark:text-slate-500 flex-shrink-0" />
      ) : isValid ? (
        <CheckCircle className="h-3.5 w-3.5 text-success-500 flex-shrink-0" />
      ) : (
        <XCircle className="h-3.5 w-3.5 text-error-500 flex-shrink-0" />
      )}
      <span
        className={
          isEmpty
            ? 'text-neutral-600 dark:text-slate-400'
            : isValid
            ? 'text-success-700 dark:text-success-400 font-medium'
            : 'text-error-700 dark:text-error-400'
        }
      >
        {label}
      </span>
    </div>
  )
}

// Username validation helper functions
const usernameValidations = {
  length: (val: string) => val.length >= 3 && val.length <= 50,
  noSpaces: (val: string) => !val.includes(' '),
  validChars: (val: string) => /^[a-zA-Z0-9_-]*$/.test(val),
  noStartEnd: (val: string) => val.length === 0 || (!val.startsWith('_') && !val.startsWith('-') && !val.endsWith('_') && !val.endsWith('-')),
  noConsecutive: (val: string) => !['__', '--', '_-', '-_'].some(p => val.includes(p)),
  notReserved: (val: string) => !['admin', 'root', 'system', 'support', 'moderator', 'staff'].includes(val.toLowerCase()),
}

export function SignupPage() {
  const navigate = useNavigate()
  const setAuth = useAuthStore((state) => state.setAuth)
  const [isLoading, setIsLoading] = useState(false)
  const [apiError, setApiError] = useState<string | null>(null)
  const [usernameValue, setUsernameValue] = useState('')
  const [showUsernameHelp, setShowUsernameHelp] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm<SignupFormData>({
    resolver: zodResolver(signupSchema),
  })

  // Watch username field for real-time validation
  const username = watch('username', '')

  const onSubmit = async (data: SignupFormData) => {
    setIsLoading(true)
    setApiError(null)

    try {
      const { confirmPassword, ...signupData } = data

      // Debug logging
      console.log('=== SIGNUP REQUEST ===')
      console.log('Form data:', data)
      console.log('Sending to backend:', signupData)
      console.log('======================')

      const response = await apiClient.post('/auth/signup', signupData)
      const apiUser = response.data.user

      // Backend only returns basic user info on signup (id, email, username, is_verified)
      // We'll use default values for profile fields until they're loaded from /auth/me
      const user = {
        id: apiUser.id,
        email: apiUser.email,
        username: apiUser.username,
        level: 1,              // Default level for new users
        xp: 0,                 // Default XP for new users
        streak: 0,             // Default streak for new users
        avatar: undefined,     // No avatar yet
        isAdmin: false,        // Default to non-admin
      }

      setAuth(user, response.data.access_token, response.data.refresh_token)
      navigate('/app/dashboard')
    } catch (error: any) {
      console.error('=== SIGNUP ERROR ===')
      console.error('Error:', error)
      console.error('Response:', error.response)
      console.error('Response data:', error.response?.data)
      console.error('Status:', error.response?.status)
      console.error('====================')
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
            <CardTitle>Create an account</CardTitle>
            <CardDescription>Get started with your free account</CardDescription>
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
                <label htmlFor="username" className="block text-sm font-medium text-neutral-700 dark:text-slate-300 mb-1">
                  Username
                </label>
                <Input
                  id="username"
                  type="text"
                  placeholder="johndoe"
                  error={errors.username?.message}
                  {...register('username')}
                  onFocus={() => setShowUsernameHelp(true)}
                />

                {/* Username validation checklist - shows when field is focused or has content */}
                {(showUsernameHelp || username) && (
                  <div className="mt-3 p-3 bg-neutral-50 dark:bg-slate-800 border border-neutral-200 dark:border-slate-700 rounded-lg space-y-2">
                    <p className="text-xs font-medium text-neutral-700 dark:text-slate-300 mb-2">
                      Username requirements:
                    </p>

                    <ValidationItem
                      label="3-50 characters"
                      isValid={usernameValidations.length(username)}
                      isEmpty={!username}
                    />
                    <ValidationItem
                      label="No spaces"
                      isValid={usernameValidations.noSpaces(username)}
                      isEmpty={!username}
                    />
                    <ValidationItem
                      label="Only letters, numbers, underscores, and hyphens"
                      isValid={usernameValidations.validChars(username)}
                      isEmpty={!username}
                    />
                    <ValidationItem
                      label="Cannot start or end with _ or -"
                      isValid={usernameValidations.noStartEnd(username)}
                      isEmpty={!username}
                    />
                    <ValidationItem
                      label="No consecutive special characters (__, --, etc.)"
                      isValid={usernameValidations.noConsecutive(username)}
                      isEmpty={!username}
                    />
                    <ValidationItem
                      label="Not a reserved name (admin, root, etc.)"
                      isValid={usernameValidations.notReserved(username)}
                      isEmpty={!username}
                    />
                  </div>
                )}
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

              <div>
                <label htmlFor="confirmPassword" className="block text-sm font-medium text-neutral-700 dark:text-slate-300 mb-1">
                  Confirm Password
                </label>
                <Input
                  id="confirmPassword"
                  type="password"
                  placeholder="••••••••"
                  error={errors.confirmPassword?.message}
                  {...register('confirmPassword')}
                />
              </div>

              <Button type="submit" className="w-full" isLoading={isLoading}>
                Sign Up
              </Button>

              <div className="text-center text-sm text-neutral-600 dark:text-slate-400">
                Already have an account?{' '}
                <Link to="/login" className="text-primary-500 hover:text-primary-600 font-medium">
                  Log in
                </Link>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
