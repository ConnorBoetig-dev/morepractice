import { useEffect, useState } from 'react'
import { useSearchParams, useNavigate, Link } from 'react-router-dom'
import { apiClient } from '@/services/api'
import { Card, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { CheckCircle, XCircle, Loader2, Target } from 'lucide-react'

type VerificationStatus = 'loading' | 'success' | 'error'

export function VerifyEmailPage() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const [status, setStatus] = useState<VerificationStatus>('loading')
  const [message, setMessage] = useState('')
  const [countdown, setCountdown] = useState(3)

  useEffect(() => {
    const token = searchParams.get('token')

    if (!token) {
      setStatus('error')
      setMessage('Invalid verification link - missing token')
      return
    }

    // Call verify endpoint
    const verifyEmail = async () => {
      try {
        const response = await apiClient.post('/auth/verify-email', { token })
        setStatus('success')
        setMessage(response.data.message || 'Email verified successfully!')

        // Start countdown timer
        const timer = setInterval(() => {
          setCountdown((prev) => {
            if (prev <= 1) {
              clearInterval(timer)
              navigate('/login')
              return 0
            }
            return prev - 1
          })
        }, 1000)

        return () => clearInterval(timer)
      } catch (error: any) {
        setStatus('error')
        const errorMessage =
          error.response?.data?.detail ||
          error.response?.data?.message ||
          'Verification failed. The link may be invalid or expired.'
        setMessage(errorMessage)
      }
    }

    verifyEmail()
  }, [searchParams, navigate])

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-neutral-50 dark:bg-slate-900 p-6">
      {/* Logo */}
      <div className="flex items-center space-x-2 mb-8">
        <Target className="h-10 w-10 text-primary-500" />
        <h1 className="text-3xl font-bold text-neutral-900 dark:text-slate-100">
          CompTIA Practice
        </h1>
      </div>

      <Card className="max-w-md w-full">
        <CardContent className="pt-8 pb-8 text-center">
          {status === 'loading' && (
            <>
              <Loader2 className="h-16 w-16 mx-auto mb-4 text-primary-500 animate-spin" />
              <h2 className="text-2xl font-bold text-neutral-900 dark:text-slate-100 mb-2">
                Verifying Your Email...
              </h2>
              <p className="text-neutral-600 dark:text-slate-400">
                Please wait while we verify your email address
              </p>
            </>
          )}

          {status === 'success' && (
            <>
              <div className="relative inline-block mb-4">
                <CheckCircle className="h-16 w-16 mx-auto text-success-500" />
                <div className="absolute -inset-2 bg-success-500/20 rounded-full blur-xl" />
              </div>
              <h2 className="text-2xl font-bold text-neutral-900 dark:text-slate-100 mb-2">
                Email Verified!
              </h2>
              <p className="text-neutral-600 dark:text-slate-400 mb-6">
                {message}
              </p>
              <p className="text-sm text-neutral-500 dark:text-slate-500 mb-6">
                Redirecting to login in {countdown} second{countdown !== 1 ? 's' : ''}...
              </p>
              <Button onClick={() => navigate('/login')} className="w-full">
                Continue to Login
              </Button>
            </>
          )}

          {status === 'error' && (
            <>
              <div className="relative inline-block mb-4">
                <XCircle className="h-16 w-16 mx-auto text-error-500" />
                <div className="absolute -inset-2 bg-error-500/20 rounded-full blur-xl" />
              </div>
              <h2 className="text-2xl font-bold text-neutral-900 dark:text-slate-100 mb-2">
                Verification Failed
              </h2>
              <p className="text-neutral-600 dark:text-slate-400 mb-6">{message}</p>
              <div className="space-y-3">
                <Button onClick={() => navigate('/login')} className="w-full">
                  Go to Login
                </Button>
                <div className="text-center text-sm text-neutral-600 dark:text-slate-400">
                  Need help?{' '}
                  <Link
                    to="/signup"
                    className="text-primary-500 hover:text-primary-600 font-medium"
                  >
                    Create a new account
                  </Link>
                </div>
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
